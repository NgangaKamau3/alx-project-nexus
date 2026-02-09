# Outfits API

Complete reference for outfit creation, management, and recommendations.

## Overview

The Outfits module enables users to:
- Create outfit combinations from products
- Save and manage personal outfits
- Share outfits with the community
- Get personalized recommendations (future: AI-powered)

## Endpoints Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/outfits/` | GET | Optional | List outfits |
| `/api/outfits/` | POST | Yes | Create outfit |
| `/api/outfits/{id}/` | GET | Optional | Outfit details |
| `/api/outfits/{id}/` | PUT/PATCH | Yes | Update outfit |
| `/api/outfits/{id}/` | DELETE | Yes | Delete outfit |
| `/api/outfits/public/` | GET | No | Public outfits |
| `/api/outfits/my-outfits/` | GET | Yes | User's outfits |

---

## List Outfits

### GET /api/outfits/

List all accessible outfits with filtering.

**Authentication:** Optional (shows public + user's private if authenticated)

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| is_public | boolean | Filter by public status |
| user_id | integer | Filter by creator (admin only) |
| search | string | Search in name/description |
| page | integer | Page number |
| page_size | integer | Items per page (max: 50) |

**Example Request:**
```bash
curl "https://modestwear.onrender.com/api/outfits/?is_public=true&page=1" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "count": 45,
  "next": "https://modestwear.onrender.com/api/outfits/?page=2",
  "previous": null,
  "results": [
    {
      "id": 12,
      "name": "Elegant Evening Look",
      "description": "Perfect for formal occasions and events",
      "is_public": true,
      "created_by": {
        "id": 15,
        "username": "sarah",
        "profile_picture_url": "https://res.cloudinary.com/.../sarah.jpg"
      },
      "items_count": 3,
      "total_price": "4599.97",
      "preview_images": [
        "https://res.cloudinary.com/.../dress_thumb.jpg",
        "https://res.cloudinary.com/.../hijab_thumb.jpg",
        "https://res.cloudinary.com/.../shoes_thumb.jpg"
      ],
      "created_at": "2024-01-18T14:20:00Z",
      "updated_at": "2024-01-18T14:20:00Z"
    }
  ]
}
```

**Business Logic:**
1. **If authenticated:** Shows user's private outfits + all public outfits
2. **If guest:** Shows only public outfits
3. Includes preview images (first 3 products)
4. Calculates total price from all items
5. Orders by most recent first

---

## Create Outfit

### POST /api/outfits/

Create a new outfit combination.

**Authentication:** Required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Outfit name (max 255 chars) |
| description | string | No | Outfit description |
| is_public | boolean | No | Share with community (default: false) |
| products | array | Yes | List of product IDs (min: 2, max: 10) |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/outfits/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Elegant Evening Look",
    "description": "Perfect for formal occasions and events",
    "is_public": true,
    "products": [5, 12, 23]
  }'
```

**Success Response (201 Created):**
```json
{
  "id": 12,
  "name": "Elegant Evening Look",
  "description": "Perfect for formal occasions and events",
  "is_public": true,
  "created_by": {
    "id": 15,
    "username": "sarah",
    "profile_picture_url": "https://res.cloudinary.com/.../sarah.jpg"
  },
  "items": [
    {
      "id": 45,
      "product": {
        "id": 5,
        "name": "Elegant Maxi Dress",
        "slug": "elegant-maxi-dress",
        "base_price": "1299.99",
        "category": "Dresses",
        "coverage_level": "Full Coverage",
        "images": [
          {
            "image": "https://res.cloudinary.com/.../dress.jpg",
            "thumbnail": "https://res.cloudinary.com/.../dress_thumb.jpg",
            "is_feature": true
          }
        ]
      },
      "position": 0
    },
    {
      "id": 46,
      "product": {
        "id": 12,
        "name": "Classic Hijab",
        "base_price": "299.99",
        "category": "Accessories"
      },
      "position": 1
    },
    {
      "id": 47,
      "product": {
        "id": 23,
        "name": "Modest Heels",
        "base_price": "899.99",
        "category": "Footwear"
      },
      "position": 2
    }
  ],
  "items_count": 3,
  "total_price": "2499.97",
  "created_at": "2024-01-20T16:30:00Z",
  "updated_at": "2024-01-20T16:30:00Z"
}
```

**Business Logic:**
1. Validates all product IDs exist
2. Checks minimum 2 products (outfit requires combination)
3. Checks maximum 10 products (prevent spam)
4. Creates outfit record
5. Creates outfit items with position (order in array)
6. Associates with authenticated user
7. Returns complete outfit with product details

**Validation Rules:**
- Name: Required, max 255 characters
- Products: Min 2, max 10 items
- Products: Must be unique (no duplicates)
- Products: Must exist and be active

**Error Responses:**

**Invalid Products (400):**
```json
{
  "success": false,
  "error": "Invalid product IDs: [99, 100]"
}
```

**Too Few Products (400):**
```json
{
  "success": false,
  "error": "Outfit must contain at least 2 products"
}
```

**Too Many Products (400):**
```json
{
  "success": false,
  "error": "Outfit cannot contain more than 10 products"
}
```

**Duplicate Products (400):**
```json
{
  "success": false,
  "error": "Outfit contains duplicate products"
}
```

---

## Get Outfit Details

### GET /api/outfits/{id}/

Retrieve detailed outfit information.

**Authentication:** Optional (required for private outfits)

**URL Parameters:**
- `id` (integer) - Outfit ID

**Example Request:**
```bash
curl https://modestwear.onrender.com/api/outfits/12/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "id": 12,
  "name": "Elegant Evening Look",
  "description": "Perfect for formal occasions and events. This outfit combines elegance with modesty.",
  "is_public": true,
  "created_by": {
    "id": 15,
    "username": "sarah",
    "first_name": "Sarah",
    "last_name": "Ahmed",
    "profile_picture_url": "https://res.cloudinary.com/.../sarah.jpg"
  },
  "items": [
    {
      "id": 45,
      "product": {
        "id": 5,
        "name": "Elegant Maxi Dress",
        "slug": "elegant-maxi-dress",
        "description": "Beautiful flowing maxi dress...",
        "base_price": "1299.99",
        "category": {
          "id": 2,
          "name": "Dresses",
          "slug": "dresses"
        },
        "coverage_level": {
          "id": 1,
          "name": "Full Coverage",
          "description": "Maximum modesty"
        },
        "images": [
          {
            "image": "https://res.cloudinary.com/.../dress.jpg",
            "thumbnail": "https://res.cloudinary.com/.../dress_thumb.jpg",
            "is_feature": true
          }
        ],
        "variants": [
          {
            "id": 12,
            "size": "M",
            "color": "Black",
            "stock_available": 15
          }
        ]
      },
      "position": 0
    }
  ],
  "items_count": 3,
  "total_price": "2499.97",
  "created_at": "2024-01-20T16:30:00Z",
  "updated_at": "2024-01-20T16:30:00Z",
  "views_count": 45,
  "likes_count": 12
}
```

**Business Logic:**
1. Fetches outfit with all related data
2. **If private:** Validates user is owner
3. Includes complete product details
4. Shows available variants for each product
5. Calculates total price
6. Increments view count (if public)

**Authorization:**
- Public outfits: Anyone can view
- Private outfits: Only owner can view

---

## Update Outfit

### PUT/PATCH /api/outfits/{id}/

Update outfit details or products.

**Authentication:** Required (must be owner)

**URL Parameters:**
- `id` (integer) - Outfit ID

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| name | string | Outfit name |
| description | string | Outfit description |
| is_public | boolean | Public visibility |
| products | array | Updated product IDs |

**Example Request:**
```bash
curl -X PATCH https://modestwear.onrender.com/api/outfits/12/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Elegant Evening Ensemble",
    "description": "Updated description with more details",
    "is_public": false
  }'
```

**Success Response (200 OK):**
```json
{
  "id": 12,
  "name": "Elegant Evening Ensemble",
  "description": "Updated description with more details",
  "is_public": false,
  "items_count": 3,
  "updated_at": "2024-01-20T17:00:00Z"
}
```

**Business Logic:**
1. Validates user is outfit owner
2. Updates provided fields only (PATCH)
3. If products updated: Deletes old items, creates new ones
4. Updates `updated_at` timestamp
5. Returns updated outfit

**Authorization:**
- Only outfit owner can update
- Admin cannot update user's outfits

---

## Delete Outfit

### DELETE /api/outfits/{id}/

Delete an outfit.

**Authentication:** Required (must be owner)

**URL Parameters:**
- `id` (integer) - Outfit ID

**Example Request:**
```bash
curl -X DELETE https://modestwear.onrender.com/api/outfits/12/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (204 No Content)**

**Business Logic:**
1. Validates user is outfit owner
2. Deletes outfit items (CASCADE)
3. Deletes outfit record
4. Returns 204 No Content

---

## Public Outfits

### GET /api/outfits/public/

List all public outfits (community feed).

**Authentication:** Not required

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search in name/description |
| ordering | string | Sort: `created_at`, `-created_at`, `views`, `-views` |
| page | integer | Page number |

**Example Request:**
```bash
curl "https://modestwear.onrender.com/api/outfits/public/?ordering=-views"
```

**Success Response (200 OK):**
```json
{
  "count": 120,
  "next": "https://modestwear.onrender.com/api/outfits/public/?page=2",
  "previous": null,
  "results": [
    {
      "id": 34,
      "name": "Summer Modest Style",
      "description": "Light and breezy for hot days",
      "created_by": {
        "username": "fatima",
        "profile_picture_url": "https://res.cloudinary.com/.../fatima.jpg"
      },
      "items_count": 4,
      "total_price": "3299.96",
      "preview_images": [...],
      "views_count": 234,
      "likes_count": 45,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

**Business Logic:**
1. Filters `is_public=true` only
2. Orders by views (popular) or date (recent)
3. Includes engagement metrics
4. Paginates results

---

## My Outfits

### GET /api/outfits/my-outfits/

List authenticated user's outfits (private + public).

**Authentication:** Required

**Example Request:**
```bash
curl https://modestwear.onrender.com/api/outfits/my-outfits/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

**Success Response (200 OK):**
```json
{
  "count": 8,
  "results": [
    {
      "id": 12,
      "name": "Elegant Evening Look",
      "is_public": true,
      "items_count": 3,
      "total_price": "2499.97",
      "views_count": 45,
      "created_at": "2024-01-20T16:30:00Z"
    },
    {
      "id": 9,
      "name": "Casual Friday",
      "is_public": false,
      "items_count": 2,
      "total_price": "1599.98",
      "views_count": 0,
      "created_at": "2024-01-18T12:00:00Z"
    }
  ]
}
```

**Business Logic:**
1. Filters by authenticated user ID
2. Shows both public and private outfits
3. Orders by most recent first
4. Includes engagement metrics

---

## Use Cases

### 1. Personal Styling
Users create private outfits to:
- Plan outfits for events
- Organize wardrobe combinations
- Save favorite looks

### 2. Community Inspiration
Users share public outfits to:
- Inspire others
- Get feedback
- Build following

### 3. Cross-Selling
Outfits drive sales by:
- Showing product combinations
- Encouraging multi-item purchases
- Increasing average order value

### 4. Personalized Recommendations (Future)
AI-powered features:
- Suggest outfits based on purchase history
- Recommend similar outfits
- Auto-generate outfits from new products

---

## Future Enhancements

### AI-Powered Recommendations
```python
# Using pgvector for similarity search
GET /api/outfits/recommendations/
```

**Features:**
- Analyze user's purchase history
- Find similar outfits
- Suggest complementary products
- Personalized outfit generation

### Social Features
```python
# Like/unlike outfits
POST /api/outfits/{id}/like/
DELETE /api/outfits/{id}/unlike/

# Comment on outfits
POST /api/outfits/{id}/comments/
GET /api/outfits/{id}/comments/

# Follow users
POST /api/users/{id}/follow/
```

### Outfit Collections
```python
# Group outfits into collections
POST /api/outfit-collections/
GET /api/outfit-collections/
```

---

## Best Practices

1. **Validate products** - Ensure all products exist before creating outfit
2. **Limit items** - Keep outfits manageable (2-10 items)
3. **Use position** - Maintain display order for consistency
4. **Cache public outfits** - Reduce database load
5. **Track engagement** - Monitor views and likes for popular outfits
6. **Moderate public content** - Review public outfits for quality
7. **Encourage sharing** - Incentivize users to create public outfits

## Next Steps

- Review [Error Handling](errors.md)
- Learn about [Security](../architecture/security.md)
- Explore [Deployment](../architecture/deployment.md)
