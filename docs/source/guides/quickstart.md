# Quickstart Guide

Get started with the ModestWear API in 5 minutes.

## Base URL

```
Production: https://modestwear.onrender.com
Development: http://localhost:8000
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <your_access_token>
```

## Quick Example

### 1. Register a New User

```bash
curl -X POST https://modestwear.onrender.com/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah@example.com",
    "password": "SecurePass123!",
    "full_name": "Sarah Ahmed"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "sarah@example.com",
      "username": "sarah",
      "first_name": "Sarah",
      "last_name": "Ahmed"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "token_type": "Bearer",
      "expires_in": 900
    }
  }
}
```

### 2. Browse Products

```bash
curl https://modestwear.onrender.com/api/catalog/products/
```

### 3. Filter by Coverage Level

```bash
curl "https://modestwear.onrender.com/api/catalog/products/?coverage_level=full&category=dresses"
```

### 4. Add to Cart

```bash
curl -X POST https://modestwear.onrender.com/api/orders/cart/add/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": 5,
    "quantity": 2
  }'
```

## Interactive Documentation

Try all endpoints interactively at:
- **Swagger UI**: [https://modestwear.onrender.com/docs/](https://modestwear.onrender.com/docs/)
- **ReDoc**: [https://modestwear.onrender.com/redoc/](https://modestwear.onrender.com/redoc/)

## Next Steps

- Read the [Authentication Guide](authentication.md)
- Explore [API Endpoints](../api/catalog.md)
- Learn about [Database Architecture](../architecture/database.md)
