import hashlib
import hmac
import uuid
from starlette.testclient import TestClient
from app.main import app
from app.routers import account
from app.initial_data import FEATURED_DISHES

def run_tests():
    with TestClient(app) as client:
        # 1. Test Menu
        r = client.get('/api/v1/menu')
        assert r.status_code == 200
        menu = r.json()
        print(f"✓ Menu retrieved: {len(menu)} items")
        assert len(menu) >= 12
        category_counts = {kind: sum(dish['dietary_type'] == kind for dish in menu) for kind in ('veg', 'non-veg', 'egg', 'vegan')}
        assert all(count >= 50 for count in category_counts.values()), category_counts
        assert len(menu) >= 200
        assert all(dish['image_url'].startswith('https://images.pexels.com/photos/') for dish in menu)
        assert len({dish['image_url'] for dish in menu}) == len(menu)
        assert len({dish['image_url'].split('?')[0] for dish in menu}) == len(menu)
        print(f"✓ Dietary menu sections: {category_counts}")

        premium_menu = client.get('/api/dishes/premium')
        assert premium_menu.status_code == 200 and len(premium_menu.json()) >= 3
        assert all(dish['is_premium'] for dish in premium_menu.json())
        assert len({dish['image_url'] for dish in premium_menu.json()}) == len(premium_menu.json())
        assert all(dish['image_url'].startswith('https://images.pexels.com/photos/') for dish in premium_menu.json())
        gourmet_photo_ids = {dish['id']: dish['image_url'].split('/')[4] for dish in premium_menu.json()}
        assert gourmet_photo_ids['featured-chirashi'] == '29989984'
        assert gourmet_photo_ids['dish-bowl-03'] == '19998456'
        assert gourmet_photo_ids['featured-unagi'] == '16569754'
        assert gourmet_photo_ids['dish-pizza-02'] == '30849268'

        # 2. Test Safe Search
        r = client.post('/api/v1/menu/safe-search', json={'allergens': ['peanuts', 'gluten']})
        assert r.status_code == 200
        safe_data = r.json()
        print(f"✓ Safe-search filter: {safe_data['safe_count']} safe, {safe_data['unsafe_count']} unsafe")
        assert safe_data['safe_count'] > 0
        assert safe_data['unsafe_count'] > 0

        # 3. Test Cart Under Free Delivery Threshold
        cart_payload = {
            'items': [{'dish_id': 'dish-bowl-01', 'quantity': 1, 'selections': []}],
            'active_allergens': ['peanuts'],
            'distance_km': 4.0
        }
        r = client.post('/api/v1/cart', json=cart_payload)
        assert r.status_code == 200
        cart_res = r.json()
        assert not cart_res['is_free_delivery']
        assert cart_res['delivery_fee'] > 0
        print(f"✓ Cart under threshold: Subtotal ₹{cart_res['subtotal']}, Fee ₹{cart_res['delivery_fee']}, ETA {cart_res['eta_minutes']}m")

        # 4. Test Cart Over the INR Free Delivery Threshold
        cart_payload_over = {
            'items': [
                {'dish_id': 'dish-bowl-01', 'quantity': 1, 'selections': []},
                {'dish_id': 'dish-pizza-01', 'quantity': 1, 'selections': []}
            ],
            'active_allergens': [],
            'distance_km': 5.0
        }
        r = client.post('/api/v1/cart', json=cart_payload_over)
        assert r.status_code == 200
        cart_over = r.json()
        assert cart_over['is_free_delivery']
        assert cart_over['delivery_fee'] == 0.0
        print(f"✓ Cart free delivery unlocked: Subtotal ₹{cart_over['subtotal']}, Fee ₹{cart_over['delivery_fee']}, ETA {cart_over['eta_minutes']}m")

        # 5. Order Placement
        order_payload = {
            'customer_name': 'Test Pilot Nova',
            'delivery_address': 'Sector 4 Orbital Bay',
            'items': [{'dish_id': 'dish-bowl-01', 'quantity': 2, 'selections': []}],
            'active_allergens': ['peanuts'],
            'distance_km': 3.0
        }
        r = client.post('/api/v1/orders', json=order_payload)
        assert r.status_code == 200
        order_res = r.json()
        order_id = order_res['order_id']
        print(f"✓ Order created: {order_id}, ETA {order_res['eta_minutes']}m, Total ₹{order_res['total_amount']}")

        # 6. INR COD and express pricing
        checkout = client.post('/api/v1/cart', json={
            'items': [{'dish_id': 'dish-bowl-01', 'quantity': 1, 'selections': []}],
            'payment_method': 'cod',
            'delivery_mode': 'express',
            'distance_km': 4.0,
        })
        assert checkout.status_code == 200
        checkout_data = checkout.json()
        assert checkout_data['currency'] == 'INR'
        assert checkout_data['cod_fee'] == 10.0
        assert checkout_data['express_fee'] > 0
        assert checkout_data['total'] == round(checkout_data['subtotal'] + checkout_data['delivery_fee'] + 10 + checkout_data['express_fee'], 2)
        print(f"✓ INR checkout: COD ₹{checkout_data['cod_fee']}, express ₹{checkout_data['express_fee']}")

        featured_order = client.post('/api/v1/orders', json={
            'items': [{'dish_id': 'featured-salmon-poke', 'quantity': 1, 'selections': []}],
            'payment_method': 'cod',
            'delivery_mode': 'standard',
            'distance_km': 3.5,
        })
        assert featured_order.status_code == 200
        assert featured_order.json()['subtotal'] == 1535.5
        assert all(not dish['id'].startswith('featured-') for dish in client.get('/api/v1/menu').json())
        print("✓ Featured slide order price matches the visible INR price")
        for dish in FEATURED_DISHES[-5:]:
            slide_order = client.post('/api/v1/orders', json={
                'items': [{'dish_id': dish['id'], 'quantity': 1, 'selections': []}],
                'payment_method': 'cod',
            })
            assert slide_order.status_code == 200
            assert slide_order.json()['subtotal'] == round(dish['base_price'] * 83, 2)

        # 7. Account, address, membership, and order-linked support
        signup = client.post('/api/v1/account/signup', json={
            'email': f"test-{uuid.uuid4().hex[:10]}@example.test",
            'display_name': 'Test Eater',
            'password': 'safe-test-password',
            'phone': '+919876543210',
        })
        assert signup.status_code == 200
        auth_headers = {'Authorization': f"Bearer {signup.json()['access_token']}"}
        assert signup.json()['user']['wallet_tokens'] == 500.0
        address = client.post('/api/v1/account/addresses', headers=auth_headers, json={
            'label': 'Home', 'address': '42 Test Street, Bengaluru', 'postal_code': '560001',
        })
        assert address.status_code == 200 and address.json()['is_default']
        premium = client.post('/api/v1/account/premium', headers=auth_headers)
        assert premium.status_code == 200 and premium.json()['premium']

        user_order = client.post('/api/v1/orders', headers=auth_headers, json={
            'customer_name': 'Test Eater',
            'delivery_address': address.json()['address'],
            'items': [{'dish_id': 'featured-salmon-poke', 'quantity': 1, 'selections': []}],
            'distance_km': 3.0,
            'payment_method': 'cod',
            'delivery_mode': 'express',
        })
        assert user_order.status_code == 200
        user_order_data = user_order.json()
        assert user_order_data['cod_fee'] == 10.0
        assert user_order_data['priority'] is True
        order_details = client.get(f"/api/v1/orders/{user_order_data['order_id']}", headers=auth_headers)
        assert order_details.status_code == 200
        assert order_details.json()['items'][0]['base_price'] == 1535.5
        assert client.get(f"/api/v1/orders/{user_order_data['order_id']}").status_code == 403
        ticket = client.post(f"/api/v1/orders/{user_order_data['order_id']}/support", headers=auth_headers, json={
            'message': 'Please confirm my delivery address.'
        })
        assert ticket.status_code == 200
        profile = client.get('/api/v1/account/me', headers=auth_headers)
        assert profile.status_code == 200
        assert profile.json()['phone'] == '+919876543210'
        assert len(profile.json()['addresses']) == 1
        assert any(order['order_id'] == user_order_data['order_id'] for order in profile.json()['orders'])
        print(f"✓ Account, premium checkout, address, history, and support: {ticket.json()['ticket_id']}")

        restaurants = client.get('/api/v1/restaurants')
        assert restaurants.status_code == 200 and len(restaurants.json()) == 7
        assert all(restaurant['logo_url'] and restaurant['tags'] for restaurant in restaurants.json())
        restaurant_menu = client.get(f"/api/restaurants/{restaurants.json()[0]['id']}/dishes")
        assert restaurant_menu.status_code == 200 and restaurant_menu.json()
        builder_options = client.get('/api/custom-builder/options')
        assert builder_options.status_code == 200
        assert {option['category'] for option in builder_options.json()['options']} == {'base', 'protein', 'topping', 'dressing'}
        custom_meal = client.post('/api/cart/add-custom', json={
            'option_ids': ['base-rice', 'protein-chicken', 'mix-avocado', 'sauce-yuzu'],
            'quantity': 2,
        })
        assert custom_meal.status_code == 200
        assert custom_meal.json()['line_total'] == round(custom_meal.json()['unit_price'] * 2, 2)
        rejected_custom_meal = client.post('/api/cart/add-custom', json={'option_ids': ['base-rice', 'mix-avocado', 'sauce-yuzu']})
        assert rejected_custom_meal.status_code == 400

        modern_order = client.post('/api/orders', json={
            'items': [{'dish_id': 'dish-bowl-01', 'quantity': 1, 'selections': []}],
            'payment_method': 'cod',
        })
        assert modern_order.status_code == 200 and modern_order.json()['status'] == 'placed'
        tracking = client.get(f"/api/orders/{modern_order.json()['order_id']}/track")
        assert tracking.status_code == 200
        assert tracking.json()['status'] in {'placed', 'preparing', 'out_for_delivery', 'delivered'}
        assert tracking.json()['driver']['name'] and tracking.json()['location']['latitude']
        menu_builder = client.get('/api/v1/menu').json()
        builder = next(dish for dish in menu_builder if dish['id'] == 'dish-build-meal')
        assert builder['dietary_type'] == 'veg' and len(builder['customization_schema']) == 4
        missing_base = client.post('/api/v1/cart', json={
            'items': [{'dish_id': 'dish-build-meal', 'quantity': 1, 'selections': []}],
        })
        assert missing_base.status_code == 400

        top_up = client.post('/api/v1/account/tokens/top-up', headers=auth_headers, json={
            'amount': 100,
            'payment_method': 'upi',
        })
        assert top_up.status_code == 200 and top_up.json()['status'] == 'pending'
        account.PAYMENT_WEBHOOK_SECRET = 'test-webhook-secret'
        webhook_payload = {
            'transaction_id': top_up.json()['transaction_id'],
            'order_id': None,
            'status': 'paid',
            'provider_reference': 'provider-test-001',
        }
        webhook_body = __import__('json').dumps(webhook_payload, separators=(',', ':')).encode()
        webhook_signature = hmac.new(b'test-webhook-secret', webhook_body, hashlib.sha256).hexdigest()
        settled = client.post('/api/v1/account/payments/webhook', json=webhook_payload, headers={'X-Payment-Signature': webhook_signature})
        assert settled.status_code == 200 and settled.json()['status'] == 'settled'
        repeated = client.post('/api/v1/account/payments/webhook', json=webhook_payload, headers={'X-Payment-Signature': webhook_signature})
        assert repeated.status_code == 200 and repeated.json()['idempotent']
        updated_profile = client.get('/api/v1/account/me', headers=auth_headers).json()
        assert updated_profile['wallet_tokens'] == 101.0

        token_order = client.post('/api/v1/orders', headers=auth_headers, json={
            'items': [{
                'dish_id': 'dish-build-meal', 'quantity': 1,
                'selections': [{
                    'step_id': 'base', 'option_id': 'base-rice', 'name': 'Steamed rice',
                    'price': 0, 'calories': 210, 'allergens': [],
                }],
            }],
            'payment_method': 'tokens',
            'delivery_mode': 'standard',
        })
        assert token_order.status_code == 200
        assert token_order.json()['payment_status'] == 'paid'
        assert token_order.json()['token_discount'] > 0
        assert token_order.json()['status'] == 'received'

        online_order = client.post('/api/v1/orders', json={
            'items': [{'dish_id': 'featured-salmon-poke', 'quantity': 1, 'selections': []}],
            'payment_method': 'upi',
        })
        assert online_order.status_code == 200
        assert online_order.json()['status'] == 'payment_pending'
        online_payment = {
            'transaction_id': None,
            'order_id': online_order.json()['order_id'],
            'status': 'paid',
            'provider_reference': 'provider-order-001',
        }
        online_signature = hmac.new(
            b'test-webhook-secret',
            __import__('json').dumps(online_payment, separators=(',', ':')).encode(),
            hashlib.sha256,
        ).hexdigest()
        settled_order = client.post('/api/v1/account/payments/webhook', json=online_payment, headers={'X-Payment-Signature': online_signature})
        assert settled_order.status_code == 200 and settled_order.json()['order_status'] == 'received'
        print(f"✓ Marketplace and meal builder: {len(restaurants.json())} restaurants, database-priced custom meals")

        with client.websocket_connect(f"/ws/order-tracking/{order_id}") as ws:
            for _ in range(3):
                data = ws.receive_json()
                print(f"✓ WS Telemetry: stage={data['stage_label']}, progress={data['progress_percent']}%, status={data['status']}")

        # 8. Feature 2 Tests: Discount Coupon Engine & Validation
        available_coupons = client.get('/api/v1/coupons/available')
        assert available_coupons.status_code == 200
        assert len(available_coupons.json()) >= 4
        assert any(c['code'] == 'BOURNET20' for c in available_coupons.json())

        # Test valid percentage coupon with cap
        valid_coupon_res = client.post('/api/v1/coupons/validate', json={'code': 'BOURNET20', 'subtotal': 1500.0})
        assert valid_coupon_res.status_code == 200
        v_data = valid_coupon_res.json()
        assert v_data['is_valid'] is True
        assert v_data['discount_amount'] == 300.0  # 20% of 1500
        assert v_data['final_total'] == 1200.0

        # Test coupon cap
        capped_coupon_res = client.post('/api/v1/coupons/validate', json={'code': 'BOURNET20', 'subtotal': 4000.0})
        assert capped_coupon_res.status_code == 200
        assert capped_coupon_res.json()['discount_amount'] == 500.0  # max cap 500

        # Test minimum order value rejection
        min_order_res = client.post('/api/v1/coupons/validate', json={'code': 'BOURNET20', 'subtotal': 500.0})
        assert min_order_res.status_code == 200
        assert min_order_res.json()['is_valid'] is False
        assert "min order" in min_order_res.json()['message'].lower()

        # Test non-existent coupon
        invalid_coupon_res = client.post('/api/v1/coupons/validate', json={'code': 'INVALID999', 'subtotal': 1500.0})
        assert invalid_coupon_res.status_code == 200
        assert invalid_coupon_res.json()['is_valid'] is False

        # Test Cart with Coupon Applied
        cart_coupon_res = client.post('/api/v1/cart', json={
            'items': [{'dish_id': 'dish-bowl-01', 'quantity': 2, 'selections': []}],
            'coupon_code': 'BOURNET20',
            'distance_km': 3.0,
        })
        assert cart_coupon_res.status_code == 200
        cart_coupon_data = cart_coupon_res.json()
        assert cart_coupon_data['coupon_code'] == 'BOURNET20'
        assert cart_coupon_data['coupon_discount'] > 0
        print(f"✓ Coupon applied in cart: code={cart_coupon_data['coupon_code']}, discount=₹{cart_coupon_data['coupon_discount']}")

        # Test Order with Coupon Applied
        order_coupon_res = client.post('/api/v1/orders', json={
            'customer_name': 'Promo Eater',
            'delivery_address': 'Sector 9 Astral Heights',
            'items': [{'dish_id': 'dish-bowl-01', 'quantity': 2, 'selections': []}],
            'coupon_code': 'BOURNET20',
            'distance_km': 2.5,
            'payment_method': 'cod',
        })
        assert order_coupon_res.status_code == 200
        order_coupon_data = order_coupon_res.json()
        assert order_coupon_data['coupon_code'] == 'BOURNET20'
        assert order_coupon_data['coupon_discount'] > 0
        print(f"✓ Order placed with coupon: order_id={order_coupon_data['order_id']}, discount=₹{order_coupon_data['coupon_discount']}")

        # 9. Feature 1 Tests: Premium Table Reservation System & Conflict Prevention
        tables_res = client.get('/api/v1/reservations/tables')
        assert tables_res.status_code == 200
        tables = tables_res.json()
        assert len(tables) >= 7
        assert any(t['is_premium'] for t in tables)
        assert any(not t['is_premium'] for t in tables)
        vip_table = next(t for t in tables if t['is_premium'])
        std_table = next(t for t in tables if not t['is_premium'])
        _uid = uuid.uuid4().hex
        _yr = 2027 + (int(_uid[:4], 16) % 15)
        _mo = (int(_uid[4:8], 16) % 12) + 1
        _dy = (int(_uid[8:12], 16) % 28) + 1
        test_date = f"{_yr}-{_mo:02d}-{_dy:02d}"

        # Book standard table (free, deposit waived)
        book_std = client.post('/api/v1/reservations/book', json={
            'table_id': std_table['id'],
            'customer_name': 'Eater One',
            'customer_email': 'eater1@example.com',
            'customer_phone': '+91 99999 11111',
            'reservation_date': test_date,
            'time_slot': '19:30',
            'party_size': 2,
            'special_requests': 'Quiet garden view please',
            'payment_method': 'at_venue',
        })
        assert book_std.status_code == 200
        std_res_data = book_std.json()
        assert std_res_data['status'] == 'confirmed'
        assert std_res_data['deposit_amount'] == 0.0
        assert std_res_data['deposit_status'] == 'waived'

        # Book VIP table with deposit checkout
        book_vip = client.post('/api/v1/reservations/book', json={
            'table_id': vip_table['id'],
            'customer_name': 'VIP Gourmet Guest',
            'customer_email': 'vip@example.com',
            'customer_phone': '+91 99999 22222',
            'reservation_date': test_date,
            'time_slot': '20:00',
            'party_size': 2,
            'special_requests': 'Anniversary table by panoramic window',
            'payment_method': 'upi',
            'payment_reference': 'UPI-REF-992819',
        })
        assert book_vip.status_code == 200
        vip_res_data = book_vip.json()
        assert vip_res_data['status'] == 'confirmed'
        assert vip_res_data['is_premium'] is True
        assert vip_res_data['deposit_amount'] > 0
        assert vip_res_data['deposit_status'] == 'paid'

        # Conflict Test: Try booking the exact same VIP table on same date and time slot
        double_book_res = client.post('/api/v1/reservations/book', json={
            'table_id': vip_table['id'],
            'customer_name': 'Conflict Guest',
            'customer_email': 'conflict@example.com',
            'customer_phone': '+91 99999 33333',
            'reservation_date': test_date,
            'time_slot': '20:00',
            'party_size': 2,
        })
        assert double_book_res.status_code == 409
        assert "already reserved" in double_book_res.json()['detail'].lower()
        print("✓ Table reservation conflict prevention verified (409 Conflict returned)")

        # Party size exceeds table capacity check (e.g. party of 6 on a 2-person table)
        over_capacity_res = client.post('/api/v1/reservations/book', json={
            'table_id': std_table['id'],
            'customer_name': 'Large Party',
            'customer_email': 'large@example.com',
            'customer_phone': '+91 99999 44444',
            'reservation_date': '2026-10-16',
            'time_slot': '19:00',
            'party_size': 10,
        })
        assert over_capacity_res.status_code in (400, 422)
        if over_capacity_res.status_code == 400:
            assert "exceeds" in over_capacity_res.json()['detail'].lower()

        # Retrieve reservation details
        res_lookup = client.get(f"/api/v1/reservations/{vip_res_data['reservation_id']}")
        assert res_lookup.status_code == 200
        assert res_lookup.json()['reservation_id'] == vip_res_data['reservation_id']

        # Cancel reservation and verify slot becomes available again
        cancel_res = client.post(f"/api/v1/reservations/{vip_res_data['reservation_id']}/cancel")
        assert cancel_res.status_code == 200
        rebook_res = client.post('/api/v1/reservations/book', json={
            'table_id': vip_table['id'],
            'customer_name': 'Rebooked Guest',
            'customer_email': 'rebooked@example.com',
            'customer_phone': '+91 99999 55555',
            'reservation_date': test_date,
            'time_slot': '20:00',
            'party_size': 2,
            'payment_method': 'upi',
        })
        assert rebook_res.status_code == 200
        print(f"✓ Table reservation lifecycle verified: booked, conflict-checked, cancelled, and rebooked")

        # 10. Feature 3 Tests: Bournet Gourmet Section
        bournet_menu = client.get('/api/v1/menu/bournet')
        assert bournet_menu.status_code == 200
        bournet_dishes = bournet_menu.json()
        assert len(bournet_dishes) == 6
        for dish in bournet_dishes:
            assert 'id' in dish and dish['id'].startswith('bournet-')
            assert 'name' in dish and len(dish['name']) > 5
            assert 'description' in dish and len(dish['description']) > 20
            assert 'price' in dish and dish['price'] > 1000
            assert 'dietaryTags' in dish and isinstance(dish['dietaryTags'], list) and len(dish['dietaryTags']) >= 2
            assert 'imageUrl' in dish and dish['imageUrl'].startswith('https://')
        print(f"✓ Bournet gourmet section: {len(bournet_dishes)} haute cuisine dishes verified")

        # 11. Feature 4 Tests: Continental Food Menu Section
        continental_res = client.get('/api/v1/menu/continental')
        assert continental_res.status_code == 200
        continental_dishes = continental_res.json()
        assert len(continental_dishes) >= 8
        assert all(d['id'].startswith('cont-') for d in continental_dishes)
        assert all(d['image_url'].startswith('https://images.pexels.com/photos/') for d in continental_dishes)
        assert len({d['image_url'] for d in continental_dishes}) == len(continental_dishes)
        assert all(d['origin'] for d in continental_dishes)
        assert all(d['base_price'] > 0 for d in continental_dishes)
        print(f"✓ Continental menu: {len(continental_dishes)} dishes with unique high-quality image URLs verified")

        # 12. Feature 5, 6, 7 Tests: Distance-Free Ordering & Cash on Delivery Cancellation Charge Logic
        # Test 12A: Place COD Order without distance parameter
        cod_order_res = client.post('/api/v1/orders', json={
            'customer_name': 'COD Eater',
            'delivery_address': '45 Heritage Square, New Delhi',
            'items': [{'dish_id': 'cont-pasta-01', 'quantity': 1, 'selections': []}],
            'payment_method': 'cod',
        })
        assert cod_order_res.status_code == 200
        cod_order = cod_order_res.json()
        cod_order_id = cod_order['order_id']
        assert cod_order['payment_method'] == 'cod'
        assert cod_order['cod_fee'] == 10.0
        assert cod_order['delivery_fee'] == 49.0  # Decoupled flat delivery fee

        # Cancel the COD order: ₹50 extra cancellation charge must be strictly enforced!
        cancel_cod = client.post(f"/api/v1/orders/{cod_order_id}/cancel")
        assert cancel_cod.status_code == 200
        cancel_cod_data = cancel_cod.json()
        assert cancel_cod_data['status'] == 'cancelled'
        assert cancel_cod_data['extra_cancellation_charge_applied'] is True
        assert cancel_cod_data['cancellation_fee'] == 50.0
        assert "extra charges apply" in cancel_cod_data['policy_notice'].lower()
        print(f"✓ COD Cancellation Policy strictly enforced: extra charge of ₹{cancel_cod_data['cancellation_fee']} applied")

        # Test 12B: Place Prepaid (UPI) Order without distance parameter
        prepaid_order_res = client.post('/api/v1/orders', json={
            'customer_name': 'Prepaid Eater',
            'delivery_address': '88 Cyber Gateway, Gurugram',
            'items': [{'dish_id': 'cont-pasta-01', 'quantity': 1, 'selections': []}],
            'payment_method': 'upi',
        })
        assert prepaid_order_res.status_code == 200
        prepaid_order = prepaid_order_res.json()
        prepaid_order_id = prepaid_order['order_id']
        assert prepaid_order['payment_method'] == 'upi'
        assert prepaid_order['cod_fee'] == 0.0

        # Cancel the Prepaid order: zero extra cancellation charge!
        cancel_prepaid = client.post(f"/api/v1/orders/{prepaid_order_id}/cancel")
        assert cancel_prepaid.status_code == 200
        cancel_prepaid_data = cancel_prepaid.json()
        assert cancel_prepaid_data['status'] == 'cancelled'
        assert cancel_prepaid_data['extra_cancellation_charge_applied'] is False
        assert cancel_prepaid_data['cancellation_fee'] == 0.0
        print(f"✓ Prepaid Cancellation Policy verified: ₹{cancel_prepaid_data['cancellation_fee']} fee (no penalty)")

        return order_id

if __name__ == "__main__":
    run_tests()
    print("★ ALL SYSTEM TESTS PASSED SUCCESSFULLY! ★")

