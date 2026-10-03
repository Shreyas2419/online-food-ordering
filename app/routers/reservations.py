"""
Premium Table Reservation Router.
Handles visual table inventory, double-booking conflict resolution,
party size validation, VIP deposit checkout, and reservation lifecycle.
"""
import json
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models import RestaurantTableModel, TableReservationModel, UserModel
from app.pricing import money
from app.schemas import (
    RestaurantTableResponse,
    TableReservationRequest,
    TableReservationResponse,
)
from app.security import get_optional_user

router = APIRouter(prefix="/api/v1/reservations", tags=["Table Reservations"])


@router.get("/tables", response_model=List[RestaurantTableResponse])
async def get_tables(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format to check availability"),
    time_slot: Optional[str] = Query(None, description="Time slot e.g. 19:00"),
    party_size: Optional[int] = Query(None, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    List all tables in inventory with VIP status, location, perks, and live availability.
    """
    stmt = select(RestaurantTableModel).where(RestaurantTableModel.is_active.is_(True)).order_by(
        RestaurantTableModel.is_premium.desc(),
        RestaurantTableModel.capacity.asc(),
    )
    result = await db.execute(stmt)
    tables = result.scalars().all()

    # If date and time_slot are provided, find reserved tables
    reserved_table_ids = set()
    if date and time_slot:
        res_stmt = select(TableReservationModel.table_id).where(
            and_(
                TableReservationModel.reservation_date == date,
                TableReservationModel.time_slot == time_slot,
                TableReservationModel.status.in_(["confirmed", "deposit_pending"]),
            )
        )
        res_result = await db.execute(res_stmt)
        reserved_table_ids = set(res_result.scalars().all())

    response = []
    for tbl in tables:
        features = json.loads(tbl.features_json or "[]")
        is_available = tbl.id not in reserved_table_ids
        if party_size and tbl.capacity < party_size:
            is_available = False

        response.append(
            RestaurantTableResponse(
                id=tbl.id,
                name=tbl.name,
                table_type=tbl.table_type,
                capacity=tbl.capacity,
                is_premium=tbl.is_premium,
                reservation_fee=tbl.reservation_fee,
                location_tag=tbl.location_tag,
                description=tbl.description,
                features=features,
                is_active=tbl.is_active,
                is_available=is_available,
            )
        )
    return response


@router.get("/availability")
async def check_availability(
    date: str = Query(..., description="YYYY-MM-DD"),
    time_slot: str = Query(..., description="e.g. 19:00"),
    party_size: int = Query(2, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Check availability of all tables for a given date, time, and party size.
    """
    tables = await get_tables(date=date, time_slot=time_slot, party_size=party_size, db=db)
    available = [t for t in tables if t.is_available]
    vip_available = [t for t in available if t.is_premium]

    return {
        "date": date,
        "time_slot": time_slot,
        "party_size": party_size,
        "total_tables": len(tables),
        "available_count": len(available),
        "vip_available_count": len(vip_available),
        "tables": tables,
    }


@router.post("/book", response_model=TableReservationResponse)
async def book_table(
    payload: TableReservationRequest,
    db: AsyncSession = Depends(get_db),
    user: Optional[UserModel] = Depends(get_optional_user),
):
    """
    Book a table with conflict prevention and VIP reservation deposit processing.
    """
    # 1. Fetch table
    tbl_stmt = select(RestaurantTableModel).where(
        RestaurantTableModel.id == payload.table_id,
        RestaurantTableModel.is_active.is_(True),
    )
    tbl_result = await db.execute(tbl_stmt)
    table = tbl_result.scalars().first()

    if not table:
        raise HTTPException(status_code=404, detail="Selected table was not found in our layout.")

    # 2. Check capacity
    if payload.party_size > table.capacity:
        raise HTTPException(
            status_code=400,
            detail=f"Party size of {payload.party_size} exceeds {table.name}'s maximum capacity of {table.capacity} guests.",
        )

    # 3. Check for booking conflicts (date + time_slot + table_id)
    conflict_stmt = select(TableReservationModel).where(
        and_(
            TableReservationModel.table_id == payload.table_id,
            TableReservationModel.reservation_date == payload.reservation_date,
            TableReservationModel.time_slot == payload.time_slot,
            TableReservationModel.status.in_(["confirmed", "deposit_pending"]),
        )
    )
    conflict_result = await db.execute(conflict_stmt)
    conflict = conflict_result.scalars().first()

    if conflict:
        raise HTTPException(
            status_code=409,
            detail=f"Conflict: Table '{table.name}' is already reserved for {payload.time_slot} on {payload.reservation_date}. Please choose another time slot or table.",
        )

    # 4. Deposit & VIP fee handling
    deposit_amount = money(table.reservation_fee) if table.is_premium else 0.0
    payment_method = payload.payment_method or "at_venue"
    
    if table.is_premium and deposit_amount > 0:
        # If user pays online or with tokens, confirm immediately; else pending
        if payment_method in ["upi", "card", "tokens"]:
            deposit_status = "paid"
            reservation_status = "confirmed"
            payment_ref = payload.payment_reference or f"PAY-{uuid.uuid4().hex[:10].upper()}"
        else:
            deposit_status = "pending"
            reservation_status = "deposit_pending"
            payment_ref = None
    else:
        deposit_status = "waived"
        reservation_status = "confirmed"
        payment_ref = None

    reservation_id = f"RES-{datetime.utcnow().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    confirmation_code = f"ZG-{uuid.uuid4().hex[:8].upper()}"

    new_reservation = TableReservationModel(
        id=reservation_id,
        table_id=table.id,
        user_id=user.id if user else None,
        customer_name=payload.customer_name.strip(),
        customer_email=payload.customer_email.strip().lower(),
        customer_phone=payload.customer_phone.strip(),
        reservation_date=payload.reservation_date,
        time_slot=payload.time_slot,
        party_size=payload.party_size,
        special_requests=payload.special_requests or "",
        status=reservation_status,
        deposit_amount=deposit_amount,
        deposit_status=deposit_status,
        payment_method=payment_method,
        payment_reference=payment_ref,
        created_at=datetime.utcnow(),
    )

    db.add(new_reservation)
    await db.commit()
    await db.refresh(new_reservation)

    notes = (
        f"VIP Reservation confirmed with ₹{deposit_amount:.2f} deposit. Table held for 20 mins."
        if table.is_premium and deposit_status == "paid"
        else f"Standard table reserved. Please arrive 5-10 minutes prior to {payload.time_slot}."
    )

    return TableReservationResponse(
        reservation_id=new_reservation.id,
        table_id=table.id,
        table_name=table.name,
        table_type=table.table_type,
        is_premium=table.is_premium,
        customer_name=new_reservation.customer_name,
        customer_email=new_reservation.customer_email,
        customer_phone=new_reservation.customer_phone,
        reservation_date=new_reservation.reservation_date,
        time_slot=new_reservation.time_slot,
        party_size=new_reservation.party_size,
        special_requests=new_reservation.special_requests,
        status=new_reservation.status,
        deposit_amount=new_reservation.deposit_amount,
        deposit_status=new_reservation.deposit_status,
        payment_method=new_reservation.payment_method,
        created_at=new_reservation.created_at.isoformat(),
        confirmation_code=confirmation_code,
        notes=notes,
    )


@router.get("/{reservation_id}", response_model=TableReservationResponse)
async def get_reservation_details(
    reservation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve reservation by ID.
    """
    stmt = select(TableReservationModel).where(TableReservationModel.id == reservation_id)
    res_result = await db.execute(stmt)
    reservation = res_result.scalars().first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found.")

    tbl_stmt = select(RestaurantTableModel).where(RestaurantTableModel.id == reservation.table_id)
    tbl_result = await db.execute(tbl_stmt)
    table = tbl_result.scalars().first()
    table_name = table.name if table else "Dining Table"
    table_type = table.table_type if table else "standard"
    is_premium = table.is_premium if table else False

    return TableReservationResponse(
        reservation_id=reservation.id,
        table_id=reservation.table_id,
        table_name=table_name,
        table_type=table_type,
        is_premium=is_premium,
        customer_name=reservation.customer_name,
        customer_email=reservation.customer_email,
        customer_phone=reservation.customer_phone,
        reservation_date=reservation.reservation_date,
        time_slot=reservation.time_slot,
        party_size=reservation.party_size,
        special_requests=reservation.special_requests,
        status=reservation.status,
        deposit_amount=reservation.deposit_amount,
        deposit_status=reservation.deposit_status,
        payment_method=reservation.payment_method,
        created_at=reservation.created_at.isoformat(),
        confirmation_code=f"ZG-{reservation.id[-6:]}",
        notes="Please present your confirmation code upon arrival at the bistro host stand.",
    )


@router.post("/{reservation_id}/cancel")
async def cancel_reservation(
    reservation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel an existing reservation to release the table back into inventory.
    """
    stmt = select(TableReservationModel).where(TableReservationModel.id == reservation_id)
    res_result = await db.execute(stmt)
    reservation = res_result.scalars().first()

    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found.")

    reservation.status = "cancelled"
    await db.commit()
    return {"message": "Reservation successfully cancelled.", "reservation_id": reservation_id}
