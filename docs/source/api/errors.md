# Error Handling

Comprehensive guide to error responses and handling in ModestWear API.

## Overview

ModestWear API uses standard HTTP status codes and consistent error response formats to communicate issues clearly to clients.

## Response Format

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "code": "ERROR_CODE",
  "details": {
    // Additional error context (optional)
  }
}
```

---

## HTTP Status Codes

### 2xx Success

| Code | Name | Usage |
|------|------|-------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE (no response body) |

### 4xx Client Errors

| Code | Name | Usage |
|------|------|-------|
| 400 | Bad Request | Invalid input, validation errors |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (duplicate) |
| 422 | Unprocessable Entity | Semantic errors |
| 429 | Too Many Requests | Rate limit exceeded |

### 5xx Server Errors

| Code | Name | Usage |
|------|------|-------|
| 500 | Internal Server Error | Unexpected server error |
| 502 | Bad Gateway | Upstream service error |
| 503 | Service Unavailable | Server overloaded or maintenance |
| 504 | Gateway Timeout | Upstream service timeout |

---

## Authentication Errors

### 401 Unauthorized

**Missing Token:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Invalid Token:**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**Expired Token:**
```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is expired"
    }
  ]
}
```

### 403 Forbidden

**Account Locked:**
```json
{
  "success": false,
  "error": "Account temporarily locked due to multiple failed attempts. Try again later.",
  "lockout": true,
  "retry_after": 900
}
```

**Account Disabled:**
```json
{
  "success": false,
  "error": "Account is disabled. Please contact support."
}
```

**Insufficient Permissions:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Validation Errors

### 400 Bad Request

**Missing Required Fields:**
```json
{
  "success": false,
  "error": "Email and password are required"
}
```

**Invalid Email Format:**
```json
{
  "email": [
    "Enter a valid email address."
  ]
}
```

**Weak Password:**
```json
{
  "success": false,
  "error": "This password is too common., This password is entirely numeric."
}
```

**Multiple Field Errors:**
```json
{
  "email": [
    "This field is required."
  ],
  "password": [
    "This field is required."
  ],
  "phone_number": [
    "Enter a valid phone number."
  ]
}
```

**Invalid Data Type:**
```json
{
  "quantity": [
    "A valid integer is required."
  ],
  "price": [
    "A valid number is required."
  ]
}
```

**Out of Range:**
```json
{
  "success": false,
  "error": "Quantity must be between 1 and 100"
}
```

---

## Resource Errors

### 404 Not Found

**Product Not Found:**
```json
{
  "detail": "Not found."
}
```

**Order Not Found:**
```json
{
  "success": false,
  "error": "Order not found"
}
```

**User Not Found:**
```json
{
  "success": false,
  "error": "User with this email does not exist"
}
```

### 409 Conflict

**Duplicate Email:**
```json
{
  "success": false,
  "error": "A user with this email already exists."
}
```

**Duplicate Wishlist Item:**
```json
{
  "success": false,
  "error": "Item already in wishlist"
}
```

**Duplicate SKU:**
```json
{
  "sku": [
    "Product variant with this SKU already exists."
  ]
}
```

---

## Business Logic Errors

### Insufficient Stock

```json
{
  "success": false,
  "error": "Insufficient stock. Only 5 items available.",
  "available_stock": 5,
  "requested_quantity": 10
}
```

### Empty Cart

```json
{
  "success": false,
  "error": "Cart is empty. Add items before creating an order."
}
```

### Order Cannot Be Cancelled

```json
{
  "success": false,
  "error": "Order cannot be cancelled. Status: shipped",
  "current_status": "shipped",
  "cancellable_statuses": ["pending", "paid"]
}
```

### Invalid Order Status Transition

```json
{
  "success": false,
  "error": "Cannot transition from 'delivered' to 'pending'",
  "current_status": "delivered",
  "requested_status": "pending"
}
```

### Payment Failed

```json
{
  "success": false,
  "error": "Payment processing failed",
  "payment_error": "Card declined",
  "code": "card_declined"
}
```

---

## Rate Limiting Errors

### 429 Too Many Requests

```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds.",
  "retry_after": 3600
}
```

**Response Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705760400
Retry-After: 3600
```

---

## Server Errors

### 500 Internal Server Error

```json
{
  "success": false,
  "error": "An unexpected error occurred. Please try again later.",
  "error_id": "abc123xyz789"
}
```

**Note:** Error details logged server-side, not exposed to client.

### 502 Bad Gateway

```json
{
  "success": false,
  "error": "Service temporarily unavailable. Please try again."
}
```

### 503 Service Unavailable

```json
{
  "success": false,
  "error": "Service is under maintenance. Please try again later.",
  "retry_after": 1800
}
```

---

## Error Handling Best Practices

### Client-Side Handling

**1. Check Status Code:**
```javascript
if (response.status === 401) {
  // Token expired, refresh or redirect to login
  refreshToken();
} else if (response.status === 403) {
  // Forbidden, show access denied message
  showAccessDenied();
} else if (response.status === 404) {
  // Not found, show 404 page
  show404Page();
}
```

**2. Parse Error Response:**
```javascript
const errorData = await response.json();
if (errorData.error) {
  showErrorMessage(errorData.error);
} else if (errorData.detail) {
  showErrorMessage(errorData.detail);
}
```

**3. Handle Field Errors:**
```javascript
if (response.status === 400) {
  const errors = await response.json();
  Object.keys(errors).forEach(field => {
    showFieldError(field, errors[field][0]);
  });
}
```

**4. Retry Logic:**
```javascript
async function fetchWithRetry(url, options, retries = 3) {
  try {
    const response = await fetch(url, options);
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      await sleep(retryAfter * 1000);
      return fetchWithRetry(url, options, retries - 1);
    }
    return response;
  } catch (error) {
    if (retries > 0) {
      await sleep(1000);
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
}
```

**5. Global Error Handler:**
```javascript
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    } else if (error.response.status === 500) {
      // Show generic error
      showErrorToast('Something went wrong. Please try again.');
    }
    return Promise.reject(error);
  }
);
```

### Server-Side Handling

**1. Catch Exceptions:**
```python
try:
    # Business logic
    result = process_order(order_data)
    return Response(result, status=200)
except ValidationError as e:
    return Response({'error': str(e)}, status=400)
except PermissionDenied as e:
    return Response({'error': str(e)}, status=403)
except ObjectDoesNotExist:
    return Response({'error': 'Resource not found'}, status=404)
except Exception as e:
    logger.error(f'Unexpected error: {str(e)}')
    return Response({'error': 'Internal server error'}, status=500)
```

**2. Custom Exception Handler:**
```python
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        response.data = {
            'success': False,
            'error': response.data.get('detail', 'An error occurred'),
            'code': exc.__class__.__name__
        }
    
    return response
```

**3. Validation:**
```python
def validate_order_data(data):
    if not data.get('address'):
        raise ValidationError('Delivery address is required')
    
    if not data.get('items'):
        raise ValidationError('Order must contain at least one item')
    
    for item in data['items']:
        if item['quantity'] < 1:
            raise ValidationError('Quantity must be at least 1')
```

---

## Error Logging

### Log Levels

| Level | Usage | Example |
|-------|-------|---------|
| DEBUG | Development debugging | Variable values, flow |
| INFO | General information | User logged in, order created |
| WARNING | Potential issues | Failed login, low stock |
| ERROR | Errors that need attention | Payment failed, API error |
| CRITICAL | System failures | Database down, service crash |

### Logging Examples

```python
import logging
logger = logging.getLogger(__name__)

# Info
logger.info(f'User {user.id} logged in from IP: {ip_address}')

# Warning
logger.warning(f'Failed login attempt for email: {email}')

# Error
logger.error(f'Payment processing failed for order {order.id}: {error}')

# Critical
logger.critical(f'Database connection lost: {error}')
```

### What to Log

**✓ Log:**
- User actions (login, logout, orders)
- Failed authentication attempts
- Permission denials
- Payment transactions
- System errors
- Performance metrics

**✗ Don't Log:**
- Passwords (even hashed)
- Credit card numbers
- Full email addresses (use user ID)
- API keys or secrets
- Personal health information

---

## Debugging Tips

### 1. Check Swagger/ReDoc

Test endpoints interactively:
- https://modestwear.onrender.com/docs/
- https://modestwear.onrender.com/redoc/

### 2. Use Django Debug Toolbar (Development)

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### 3. Enable Verbose Logging

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',  # Show all logs
    },
}
```

### 4. Test with cURL

```bash
# Test authentication
curl -X POST https://modestwear.onrender.com/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}' \
  -v  # Verbose output

# Test with token
curl https://modestwear.onrender.com/api/orders/cart/ \
  -H "Authorization: Bearer <token>" \
  -v
```

### 5. Check Render Logs

```bash
# View live logs
render logs -f

# Search logs
render logs | grep "ERROR"
```

---

## Common Issues & Solutions

### Issue: Token Expired

**Error:**
```json
{
  "detail": "Token is expired",
  "code": "token_not_valid"
}
```

**Solution:**
1. Use refresh token to get new access token
2. Retry original request with new token
3. If refresh fails, redirect to login

### Issue: CORS Error

**Error:**
```
Access to fetch at 'https://modestwear.onrender.com/api/...' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
1. Add origin to CORS_ALLOWED_ORIGINS
2. Ensure credentials included in request
3. Check CORS headers in response

### Issue: 502 Bad Gateway

**Error:**
```json
{
  "success": false,
  "error": "Service temporarily unavailable"
}
```

**Solution:**
1. Check if service is sleeping (Render free tier)
2. Wait for service to wake up (~30 seconds)
3. Implement retry logic with exponential backoff

### Issue: Database Connection Error

**Error:**
```
django.db.utils.OperationalError: could not connect to server
```

**Solution:**
1. Check DATABASE_URL is correct
2. Verify SSL mode: `?sslmode=require`
3. Check Neon database is active
4. Verify connection pooling settings

---

## Error Response Examples

### Complete Error Response

```json
{
  "success": false,
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "email": ["Enter a valid email address."],
    "password": ["This field is required."]
  },
  "timestamp": "2024-01-20T16:45:00Z",
  "path": "/api/users/register/",
  "request_id": "abc123xyz789"
}
```

### Minimal Error Response

```json
{
  "error": "Not found"
}
```

---

## Next Steps

- Review [Security Architecture](../architecture/security.md)
- Explore [API Documentation](authentication.md)
- Learn about [Deployment](../architecture/deployment.md)
