# Orders API

Complete reference for shopping cart, wishlist, and order management.

## Overview

The Orders module handles the complete e-commerce flow:
- **Shopping Cart**: Guest and authenticated user support
- **Wishlist**: Save items for later
- **Order Creation**: Convert cart to order
- **Order Tracking**: Monitor order status
- **Order History**: View past purchases

## Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/orders/cart/` | GET | Optional | View cart contents |
| `/api/orders/cart/add/` | POST | Optional | Add item to cart |
| `/api/orders/cart/update/{id}/` | PATCH | Optional | Update cart item quantity |
| `/api/orders/cart/remove/{id}/` | DELETE | Optional | Remove item from cart |
| `/api/orders/cart/clear/` | POST | Optional | Empty cart |
| `/api/orders/wishlist/` | GET | Yes | View wishlist |
| `/api/orders/wishlist/add/` | POST | Yes | Add to wishlist |
| `/api/orders/wishlist/remove/{id}/` | DELETE | Yes | Remove from wishlist |
| `/api/orders/create/` | POST | Yes | Create order from cart |
| `/api/orders/` | GET | Yes | List user's orders |
| `/api/orders/{id}/` | GET | Yes | Order details |
| `/api/orders/{id}/cancel/` | POST | Yes | Cancel order |

---

## Shopping Cart

### GET /api/orders/cart/

View current cart contents with calculated totals.

**Authentication:** Optional (session-based for guests)

**Example Request:**
```bash
# Authenticated user
curl https://modestwear.onrender.com/api/orders/cart/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."

# Guest user (uses session cookie)
curl https://modestwear.onrender.com/api/orders/cart/ \
  -H "Cookie: sessionid=abc123..."
```

**Success Response (200 OK):**
```json
{
  "items": [
    {
      "id": 45,
      "variant": {
        "id": 12,
        "sku": "DRESS-001-M-BLK",
        "size": "M",
        "color": "Black",
        "stock_available": 15,
        "product": {
          "id": 5,
          "name": "Elegant Maxi Dress",
          "slug": "elegant-maxi-dress",
          "base_price": "1299.99",
          "images": [
            {
              "thumbnail": "https://res.cloudinary.com/.../dress_thumb.jpg",
              "is_feature": true
            }
          ]
        }
      },
      "quantity": 2,
      "subtotal": "2599.98",
      "created_at": "2024-01-20T15:30:00Z"
    },
    {
      "id": 46,
      "variant": {
        "id": 23,
        "sku": "ABAYA-005-L-NVY",
        "size": "L",
        "color": "Navy",
        "stock_available": 8,
        "product": {
          "id": 12,
          "name": "Classic Abaya",
          "slug": "classic-abaya",
          "base_price": "899.99"
        }
      },
      "quantity": 1,
      "subtotal": "899.99"
    }
  ],
  "summary": {
    "total_items": 3,
    "total_price": "3499.97",
    "currency": "ZAR"
  }
}
```

**Business Logic:**
1. **For authenticated users:** Fetches cart by user_id
2. **For guest users:** Fetches cart by session_key
3. Calculates subtotals (quantity × price)
4. Calculates total price
5. Includes product details and images
6. Shows current stock availability

**Empty Cart Response:**
```json
{
  "items": [],
  "summary": {
    "total_items": 0,
    "total_price": "0.00",
    "currency": "ZAR"
  }
}
```

---

### POST /api/orders/cart/add/

Add product variant to cart.

**Authentication:** Optional

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| variant_id | integer | Yes | Product variant ID |
| quantity | integer | No | Quantity (default: 1) |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/orders/cart/add/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": 12,
    "quantity": 2
  }'
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Item added to cart",
  "data": {
    "cart_item_id": 45,
    "variant_id": 12,
    "quantity": 2,
    "subtotal": "2599.98"
  }
}
```

**Business Logic:**
1. Validates variant exists and is active
2. Checks stock availability
3. **If item already in cart:** Updates quantity (adds to existing)
4. **If new item:** Creates new cart item
5. Associates with user_id (authenticated) or session_key (guest)
6. Returns cart item details

**Stock Validation:**
- Requested quantity must be ≤ stock_available
- If insufficient stock, returns error with available quantity

**Error Responses:**

**Insufficient Stock (400):**
```json
{
  "success": false,
  "error": "Insufficient stock. Only 5 items available.",
  "available_stock": 5
}
```

**Invalid Variant (404):**
```json
{
  "success": false,
  "error": "Product variant not found or inactive"
}
```

**Invalid Quantity (400):**
```json
{
  "success": false,
  "error": "Quantity must be at least 1"
}
```

---

### PATCH /api/orders/cart/update/{id}/

Update cart item quantity.

**Authentication:** Optional

**URL Parameters:**
- `id` (integer) - Cart item ID

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| quantity | integer | Yes | New quantity (min: 1) |

**Example Request:**
```bash
curl -X PATCH https://modestwear.onrender.com/api/orders/cart/update/45/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Cart item updated",
  "data": {
    "cart_item_id": 45,
    "quantity": 3,
    "subtotal": "3899.97"
  }
}
```

**Business Logic:**
1. Validates cart item belongs to user/session
2. Checks new quantity against stock
3. Updates quantity
4. Recalculates subtotal
5. Returns updated item

---

### DELETE /api/orders/cart/remove/{id}/

Remove item from cart.

**Authentication:** Optional

**URL Parameters:**
- `id` (integer) - Cart item ID

**Example Request:**
```bash
curl -X DELETE https://modestwear.onrender.com/api/orders/cart/remove/45/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Item removed from cart"
}
```

**Business Logic:**
1. Validates cart item belongs to user/session
2. Deletes cart item
3. Returns success message

---

### POST /api/orders/cart/clear/

Empty entire cart.

**Authentication:** Optional

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/orders/cart/clear/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Cart cleared",
  "items_removed": 3
}
```

**Business Logic:**
1. Fetches all cart items for user/session
2. Deletes all items
3. Returns count of removed items

---

## Wishlist

### GET /api/orders/wishlist/

View user's saved items.

**Authentication:** Required

**Example Request:**
```bash
curl https://modestwear.onrender.com/api/orders/wishlist/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "items": [
    {
      "id": 12,
      "variant": {
        "id": 34,
        "sku": "TUNIC-008-M-BEG",
        "size": "M",
        "color": "Beige",
        "stock_available": 12,
        "is_active": true,
        "product": {
          "id": 18,
          "name": "Modest Tunic",
          "slug": "modest-tunic",
          "base_price": "699.99",
          "is_featured": false,
          "images": [
            {
              "image": "https://res.cloudinary.com/.../tunic.jpg",
              "thumbnail": "https://res.cloudinary.com/.../tunic_thumb.jpg"
            }
          ]
        }
      },
      "added_at": "2024-01-18T10:20:00Z"
    }
  ],
  "total_items": 1
}
```

**Business Logic:**
1. Fetches all wishlist items for authenticated user
2. Includes full product and variant details
3. Shows current stock status
4. Orders by most recently added

---

### POST /api/orders/wishlist/add/

Add product variant to wishlist.

**Authentication:** Required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| variant_id | integer | Yes | Product variant ID |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/orders/wishlist/add/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": 34
  }'
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Item added to wishlist",
  "data": {
    "wishlist_item_id": 12,
    "variant_id": 34
  }
}
```

**Business Logic:**
1. Validates variant exists
2. Checks for duplicate (user_id + variant_id unique)
3. Creates wishlist item
4. Returns wishlist item ID

**Error Responses:**

**Already in Wishlist (400):**
```json
{
  "success": false,
  "error": "Item already in wishlist"
}
```

**Invalid Variant (404):**
```json
{
  "success": false,
  "error": "Product variant not found"
}
```

---

### DELETE /api/orders/wishlist/remove/{id}/

Remove item from wishlist.

**Authentication:** Required

**URL Parameters:**
- `id` (integer) - Wishlist item ID

**Example Request:**
```bash
curl -X DELETE https://modestwear.onrender.com/api/orders/wishlist/remove/12/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Item removed from wishlist"
}
```

---

## Order Management

### POST /api/orders/create/

Create order from cart contents.

**Authentication:** Required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| address | string | Yes | Delivery address |
| payment_method | string | Yes | `stripe` or `paystack` |
| notes | string | No | Order notes |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/orders/create/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main Street, Cape Town, Western Cape, 8001, South Africa",
    "payment_method": "stripe",
    "notes": "Please call before delivery"
  }'
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "message": "Order created successfully",
  "data": {
    "order_id": 89,
    "order_number": "MW-2024-00089",
    "status": "pending",
    "total_price": "3499.97",
    "items_count": 3,
    "created_at": "2024-01-20T16:45:00Z",
    "payment_url": "https://checkout.stripe.com/pay/cs_test_..."
  }
}
```

**Business Logic:**
1. Validates user has items in cart
2. Validates all items still in stock
3. Creates order record with status='pending'
4. Creates order items (copies cart items)
5. **Captures price at purchase** (price_at_purchase field)
6. Calculates total price
7. Clears user's cart
8. Generates payment URL (Stripe/Paystack)
9. Sends order confirmation email
10. Returns order details and payment link

**Price History:**
- Each order item stores `price_at_purchase`
- Ensures accurate financial records even if product price changes later
- Order total is sum of order items, not recalculated from current prices

**Stock Management:**
- Stock is reserved but not decremented until payment confirmed
- If payment fails, stock reservation is released
- Prevents overselling

**Error Responses:**

**Empty Cart (400):**
```json
{
  "success": false,
  "error": "Cart is empty"
}
```

**Insufficient Stock (400):**
```json
{
  "success": false,
  "error": "Insufficient stock for: Elegant Maxi Dress (M, Black). Only 1 available.",
  "out_of_stock_items": [
    {
      "product": "Elegant Maxi Dress",
      "variant": "M, Black",
      "requested": 2,
      "available": 1
    }
  ]
}
```

**Invalid Address (400):**
```json
{
  "success": false,
  "error": "Delivery address is required"
}
```

---

### GET /api/orders/

List user's orders with pagination.

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status: `pending`, `paid`, `shipped`, `delivered`, `cancelled` |
| page | integer | Page number (default: 1) |
| page_size | integer | Items per page (default: 20) |
| ordering | string | Sort by: `created_at`, `-created_at` |

**Example Request:**
```bash
curl "https://modestwear.onrender.com/api/orders/?status=paid&ordering=-created_at" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "count": 15,
  "next": "https://modestwear.onrender.com/api/orders/?page=2",
  "previous": null,
  "results": [
    {
      "id": 89,
      "order_number": "MW-2024-00089",
      "status": "paid",
      "total_price": "3499.97",
      "address": "123 Main Street, Cape Town...",
      "created_at": "2024-01-20T16:45:00Z",
      "updated_at": "2024-01-20T16:50:00Z",
      "items_count": 3,
      "items_preview": [
        {
          "product_name": "Elegant Maxi Dress",
          "quantity": 2,
          "thumbnail": "https://res.cloudinary.com/.../dress_thumb.jpg"
        }
      ]
    },
    {
      "id": 76,
      "order_number": "MW-2024-00076",
      "status": "delivered",
      "total_price": "1899.98",
      "created_at": "2024-01-15T10:20:00Z",
      "items_count": 2
    }
  ]
}
```

**Business Logic:**
1. Fetches orders for authenticated user only
2. Filters by status if provided
3. Orders by creation date (newest first by default)
4. Paginates results
5. Includes item preview for quick reference

---

### GET /api/orders/{id}/

Get detailed order information.

**Authentication:** Required

**URL Parameters:**
- `id` (integer) - Order ID

**Example Request:**
```bash
curl https://modestwear.onrender.com/api/orders/89/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "id": 89,
  "order_number": "MW-2024-00089",
  "status": "paid",
  "total_price": "3499.97",
  "address": "123 Main Street, Cape Town, Western Cape, 8001, South Africa",
  "notes": "Please call before delivery",
  "created_at": "2024-01-20T16:45:00Z",
  "updated_at": "2024-01-20T16:50:00Z",
  "items": [
    {
      "id": 234,
      "variant": {
        "id": 12,
        "sku": "DRESS-001-M-BLK",
        "size": "M",
        "color": "Black",
        "product": {
          "id": 5,
          "name": "Elegant Maxi Dress",
          "slug": "elegant-maxi-dress",
          "images": [
            {
              "thumbnail": "https://res.cloudinary.com/.../dress_thumb.jpg"
            }
          ]
        }
      },
      "quantity": 2,
      "price_at_purchase": "1299.99",
      "subtotal": "2599.98"
    },
    {
      "id": 235,
      "variant": {
        "id": 23,
        "sku": "ABAYA-005-L-NVY",
        "size": "L",
        "color": "Navy",
        "product": {
          "id": 12,
          "name": "Classic Abaya",
          "slug": "classic-abaya"
        }
      },
      "quantity": 1,
      "price_at_purchase": "899.99",
      "subtotal": "899.99"
    }
  ],
  "status_history": [
    {
      "status": "pending",
      "timestamp": "2024-01-20T16:45:00Z"
    },
    {
      "status": "paid",
      "timestamp": "2024-01-20T16:50:00Z"
    }
  ]
}
```

**Business Logic:**
1. Validates order belongs to authenticated user
2. Fetches complete order details
3. Includes all order items with product info
4. Shows price at purchase (historical pricing)
5. Includes status history for tracking

**Authorization:**
- Users can only view their own orders
- Admin users can view all orders

---

### POST /api/orders/{id}/cancel/

Cancel a pending order.

**Authentication:** Required

**URL Parameters:**
- `id` (integer) - Order ID

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| reason | string | No | Cancellation reason |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/orders/89/cancel/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Changed my mind"
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Order cancelled successfully",
  "data": {
    "order_id": 89,
    "status": "cancelled",
    "refund_status": "pending"
  }
}
```

**Business Logic:**
1. Validates order belongs to user
2. Checks order status is 'pending' or 'paid'
3. Updates status to 'cancelled'
4. Releases stock reservation
5. Initiates refund if payment was made
6. Sends cancellation confirmation email
7. Logs cancellation reason

**Cancellation Rules:**
- **Pending orders:** Can be cancelled anytime
- **Paid orders:** Can be cancelled within 24 hours
- **Shipped orders:** Cannot be cancelled (must return)
- **Delivered orders:** Cannot be cancelled (must return)

**Error Responses:**

**Cannot Cancel (400):**
```json
{
  "success": false,
  "error": "Order cannot be cancelled. Status: shipped"
}
```

**Not Found (404):**
```json
{
  "success": false,
  "error": "Order not found"
}
```

---

## Order Status Lifecycle

```
pending → paid → shipped → delivered
   ↓
cancelled
```

**Status Descriptions:**

| Status | Description | User Actions | Admin Actions |
|--------|-------------|--------------|---------------|
| **pending** | Order created, awaiting payment | Cancel, Pay | Cancel, Mark as paid |
| **paid** | Payment confirmed | Cancel (24h), View | Mark as shipped |
| **shipped** | Order dispatched | Track, Contact support | Update tracking, Mark as delivered |
| **delivered** | Order received | Review, Return (7 days) | - |
| **cancelled** | Order cancelled | View refund status | Process refund |

---

## Guest Cart Migration

When a guest user logs in or registers, their cart is automatically migrated:

**Migration Process:**
1. User logs in/registers
2. System fetches guest cart by session_key
3. Merges with user's existing cart
4. Updates cart items: `session_key=null`, `user_id=<user_id>`
5. Removes duplicate items (keeps higher quantity)
6. Clears session cart

**Example:**
```
Guest Cart:        User Cart:         Merged Cart:
- Item A (qty 2)   - Item B (qty 1)   - Item A (qty 2)
- Item C (qty 1)   - Item C (qty 3)   - Item B (qty 1)
                                       - Item C (qty 3)  ← kept higher qty
```

---

## Stock Management

### Stock Reservation
- Stock reserved when order created (status='pending')
- Reservation expires after 30 minutes if unpaid
- Stock decremented when payment confirmed (status='paid')

### Stock Release
- Released when order cancelled
- Released when reservation expires
- Released when payment fails

### Low Stock Alerts
- Admin notified when stock < 5 units
- Celery task checks hourly
- Email sent to admin

---

## Payment Integration

### Stripe
```python
# Payment flow
1. Order created → status='pending'
2. Stripe checkout session created
3. User redirected to Stripe
4. Webhook receives payment confirmation
5. Order status updated to 'paid'
6. Stock decremented
7. Confirmation email sent
```

### Paystack
```python
# Payment flow (similar to Stripe)
1. Order created → status='pending'
2. Paystack transaction initialized
3. User redirected to Paystack
4. Webhook receives payment confirmation
5. Order status updated to 'paid'
```

---

## Best Practices

1. **Check stock before checkout** - Validate availability
2. **Handle cart migration** - Merge guest cart on login
3. **Show order status** - Keep users informed
4. **Enable cancellation** - Allow users to cancel pending orders
5. **Store price history** - Use price_at_purchase for accuracy
6. **Implement retry logic** - Handle payment webhook failures
7. **Send notifications** - Email on order status changes

## Next Steps

- Explore [Outfits API](outfits.md)
- Learn about [Error Handling](errors.md)
- Read [Security Best Practices](../architecture/security.md)
