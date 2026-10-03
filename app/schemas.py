"""
Pydantic v2 schemas for validating requests and responses.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class CustomizationOption(BaseModel):
    id: str
    name: str
    price: float = 0.0
    calories: int = 0
    allergens: List[str] = Field(default_factory=list)
    is_safe_swap: bool = False
    swap_for: Optional[str] = None

class CustomizationStep(BaseModel):
    step_id: str
    title: str
    description: Optional[str] = None
    min_select: int = 1
    max_select: int = 1
    options: List[CustomizationOption]

class DishResponse(BaseModel):
    id: str
    name: str
    slug: str
    category: str
    dietary_type: str = "veg"
    restaurant_id: Optional[str] = None
    hidden_from_catalog: bool = False
    description: str
    base_price: float
    calories: int
    protein_g: int = 20
    prep_time_mins: int = 12
    image_url: str
    allergens: List[str] = Field(default_factory=list)
    ingredients: List[str] = Field(default_factory=list)
    customizable: bool = False
    customization_schema: Optional[List[CustomizationStep]] = None
    is_popular: bool = False
    is_premium: bool = False
    rating: float = 4.9
    review_count: int = 128

class DishSafeAssessment(DishResponse):
    safe: bool = True
    detected_allergens: List[str] = Field(default_factory=list)
    suggested_swaps: List[Dict[str, Any]] = Field(default_factory=list)
    risk_level: str = "safe"  # safe | warning | high_risk

class SafeSearchRequest(BaseModel):
    allergens: List[str] = Field(default_factory=list) # e.g. ["peanuts", "gluten", "dairy", "soy", "shellfish"]
    category: Optional[str] = None
    query: Optional[str] = None

class SafeSearchResponse(BaseModel):
    total: int
    safe_count: int
    unsafe_count: int
    active_filters: List[str]
    safe_items: List[DishSafeAssessment]
    unsafe_items: List[DishSafeAssessment]

class SelectedCustomization(BaseModel):
    step_id: str
    option_id: str
    name: str
    price: float = 0.0
    calories: int = 0
    allergens: List[str] = Field(default_factory=list)

class CartItemInput(BaseModel):
    dish_id: str
    quantity: int = Field(ge=1, le=50)
    selections: List[SelectedCustomization] = Field(default_factory=list)
    special_notes: Optional[str] = None

class CartItemDetail(BaseModel):
    dish_id: str
    name: str
    base_price: float
    unit_price: float
    quantity: int
    total_price: float
    total_calories: int
    image_url: str
    allergens: List[str] = Field(default_factory=list)
    selections_summary: List[str] = Field(default_factory=list)
    allergen_warnings: List[str] = Field(default_factory=list)

class CartValidateRequest(BaseModel):
    items: List[CartItemInput] = Field(default_factory=list)
    active_allergens: List[str] = Field(default_factory=list)
    distance_km: Optional[float] = Field(default=None)
    payment_method: Literal["tokens", "cod", "upi", "card", "netbanking"] = "upi"
    delivery_mode: Literal["standard", "express"] = "standard"
    coupon_code: Optional[str] = None

class CartValidateResponse(BaseModel):
    items: List[CartItemDetail]
    item_count: int
    subtotal: float
    delivery_fee: float
    free_delivery_threshold: float = 2075.00
    amount_needed_for_free_delivery: float
    is_free_delivery: bool
    total: float
    cod_fee: float = 0.0
    express_fee: float = 0.0
    token_discount: float = 0.0
    coupon_code: Optional[str] = None
    coupon_discount: float = 0.0
    payment_method: str = "upi"
    delivery_mode: str = "standard"
    currency: str = "INR"
    active_kitchen_queue: int
    prep_time_mins: int
    transit_time_mins: int = 10
    eta_minutes: int = 25
    sla_formula: str = "Standard Gourmet Kitchen Dispatch (25-30 mins)"
    cancellation_notice: str = "Extra charges apply for the cancellation of an order after it has been placed (Applicable strictly for Cash on Delivery)."
    cod_cancellation_fee: float = 50.0

class OrderCreateRequest(BaseModel):
    customer_name: str = "Faura Guest"
    delivery_address: str = "Civil Lines, Heritage District"
    items: List[CartItemInput]
    active_allergens: List[str] = Field(default_factory=list)
    distance_km: Optional[float] = Field(default=None)
    payment_method: Literal["tokens", "cod", "upi", "card", "netbanking"] = "cod"
    delivery_mode: Literal["standard", "express"] = "standard"
    coupon_code: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str
    customer_name: str
    delivery_address: str
    status: str
    subtotal: float
    delivery_fee: float
    total_amount: float
    cod_fee: float = 0.0
    express_fee: float = 0.0
    token_discount: float = 0.0
    coupon_code: Optional[str] = None
    coupon_discount: float = 0.0
    payment_method: str = "cod"
    payment_status: str = "due"
    delivery_mode: str = "standard"
    priority: bool = False
    currency: str = "INR"
    item_count: int
    distance_km: Optional[float] = 0.0
    active_kitchen_queue: int
    prep_time_mins: int
    transit_time_mins: int = 10
    eta_minutes: int = 25
    cancellation_fee: float = 0.0
    cancellation_notice: str = "Extra charges apply for the cancellation of an order after it has been placed (Applicable strictly for Cash on Delivery)."
    created_at: str
    items: List[CartItemDetail]

class OrderCancelResponse(BaseModel):
    order_id: str
    status: str
    payment_method: str
    extra_cancellation_charge_applied: bool
    cancellation_fee: float
    message: str
    policy_notice: str

class ContinentalDishItem(BaseModel):
    id: str
    name: str
    category: str = "continental"
    dietary_type: str = "veg"
    description: str
    base_price: float
    calories: int
    protein_g: int
    prep_time_mins: int
    dietaryTags: List[str] = Field(default_factory=list)
    imageUrl: str
    image_url: Optional[str] = None
    origin: str = "European Classic"
    ingredients: List[str] = Field(default_factory=list)
    is_popular: bool = False
    rating: float = 4.9
    review_count: int = 120

    def model_post_init(self, __context):
        if not self.image_url:
            self.image_url = self.imageUrl

class KitchenStatusResponse(BaseModel):
    active_queue: int
    avg_prep_time_mins: int
    transit_rate_mins_per_km: float = 0.0
    current_status: str
    sla_formula: str = "Standard Gourmet Kitchen Dispatch (25-30 mins)"


class SignupRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    display_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=30)


class LoginRequest(BaseModel):
    email: str
    password: str


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    dietary_preferences: Optional[List[str]] = Field(default=None, max_length=12)
    phone: Optional[str] = Field(default=None, max_length=30)


class AddressCreateRequest(BaseModel):
    label: str = Field(default="Home", max_length=40)
    address: str = Field(min_length=5, max_length=300)
    postal_code: str = Field(default="", max_length=12)
    is_default: bool = False


class TokenTopUpRequest(BaseModel):
    amount: float = Field(gt=0, le=50000)
    payment_method: Literal["upi", "card", "netbanking"]


class PaymentWebhookRequest(BaseModel):
    transaction_id: Optional[str] = Field(default=None, min_length=8, max_length=50)
    order_id: Optional[str] = Field(default=None, min_length=8, max_length=50)
    status: Literal["paid", "failed"]
    provider_reference: str = Field(default="", max_length=100)


class SupportTicketRequest(BaseModel):
    message: str = Field(min_length=5, max_length=2000)


# =========================================================================
# FEATURE 1: PREMIUM TABLE RESERVATION SCHEMAS
# =========================================================================

class RestaurantTableResponse(BaseModel):
    id: str
    name: str
    table_type: str
    capacity: int
    is_premium: bool
    reservation_fee: float
    location_tag: str
    description: str
    features: List[str] = Field(default_factory=list)
    is_active: bool = True
    is_available: bool = True


class TableReservationRequest(BaseModel):
    table_id: str
    customer_name: str = Field(min_length=2, max_length=100)
    customer_email: str = Field(min_length=5, max_length=254)
    customer_phone: str = Field(min_length=8, max_length=30)
    reservation_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time_slot: str = Field(min_length=4, max_length=10)
    party_size: int = Field(ge=1, le=20)
    special_requests: Optional[str] = Field(default="", max_length=1000)
    payment_method: Optional[Literal["upi", "card", "tokens", "at_venue"]] = "at_venue"
    payment_reference: Optional[str] = None


class TableReservationResponse(BaseModel):
    reservation_id: str
    table_id: str
    table_name: str
    table_type: str
    is_premium: bool
    customer_name: str
    customer_email: str
    customer_phone: str
    reservation_date: str
    time_slot: str
    party_size: int
    special_requests: str
    status: str
    deposit_amount: float
    deposit_status: str
    payment_method: Optional[str] = None
    created_at: str
    confirmation_code: str
    notes: str


# =========================================================================
# FEATURE 2: DISCOUNT COUPON SCHEMAS
# =========================================================================

class CouponValidateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=30)
    subtotal: float = Field(ge=0)


class CouponValidateResponse(BaseModel):
    is_valid: bool
    code: str
    title: str = ""
    description: str = ""
    discount_type: str = "percentage"
    discount_value: float = 0.0
    discount_amount: float = 0.0
    min_order_value: float = 0.0
    subtotal: float = 0.0
    final_total: float = 0.0
    message: str


class AvailableCouponResponse(BaseModel):
    code: str
    title: str
    description: str
    discount_type: str
    discount_value: float
    min_order_value: float
    max_discount_amount: Optional[float] = None


# =========================================================================
# FEATURE 3: BOURNET (GOURMET) DISH SCHEMAS
# =========================================================================

class BournetDishItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    dietaryTags: List[str]
    imageUrl: str

