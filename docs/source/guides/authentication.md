# Authentication Guide

ModestWear API uses JWT (JSON Web Tokens) for authentication with support for traditional email/password and social OAuth.

## Authentication Methods

### 1. Email/Password Registration

**Endpoint:** `POST /api/users/register/`

**Required Fields:**
- `email` (string) - User's email address
- `password` (string) - Must meet security requirements

**Optional Fields:**
- `full_name` (string) - Automatically split into first/last name
- `phone_number` (string) - Contact number

**Example:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "Jane Doe",
    "phone_number": "+27123456789"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "user",
      "is_verified": false
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1Qi...",
      "refresh_token": "eyJ0eXAiOiJKV1Qi...",
      "token_type": "Bearer",
      "expires_in": 900
    },
    "email_verified": false
  }
}
```

:::{note}
A verification email is automatically sent. Users can browse but may have limited access until verified.
:::

### 2. Email Verification

**Endpoint:** `POST /api/users/verify-email/`

**Parameters:**
- `token` (string) - Verification token from email

**Example:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123xyz..."
  }'
```

### 3. Login

**Endpoint:** `POST /api/users/login/`

**Parameters:**
- `email` (string)
- `password` (string)

**Example:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "Jane",
      "last_name": "Doe"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1Qi...",
      "refresh_token": "eyJ0eXAiOiJKV1Qi...",
      "token_type": "Bearer",
      "expires_in": 900
    },
    "email_verified": true
  }
}
```

### 4. Google OAuth Login

**Endpoint:** `POST /api/users/social/google/`

**Parameters:**
- `token` (string) - Google ID token from frontend

**Flow:**
1. Frontend initiates Google OAuth
2. Google returns ID token
3. Send token to this endpoint
4. Backend verifies with Google
5. Returns JWT tokens

**Example:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/social/google/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "google_id_token_here"
  }'
```

:::{tip}
Social users are automatically verified since Google confirms their email.
:::

## Token Management

### Access Token
- **Lifetime:** 15 minutes
- **Usage:** Include in Authorization header for all authenticated requests
- **Format:** `Authorization: Bearer <access_token>`

### Refresh Token
- **Lifetime:** 14 days
- **Usage:** Get new access token without re-login
- **Rotation:** New refresh token issued on each refresh

### Token Refresh

**Endpoint:** `POST /api/users/token/refresh/`

**Parameters:**
- `refresh_token` (string)

**Example:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1Qi..."
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token",
    "refresh_token": "new_refresh_token",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

## Using Tokens

Include the access token in all authenticated requests:

```bash
curl https://modestwear.onrender.com/api/orders/cart/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1Qi..."
```

## Logout

**Endpoint:** `POST /api/users/logout/`

**Parameters:**
- `refresh_token` (string, optional)

**Example:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1Qi..."
  }'
```

:::{warning}
Logout blacklists the refresh token. The access token remains valid until expiration.
:::

## Security Features

- **Password Validation:** Minimum 8 characters, not too common, not all numeric
- **Account Lockout:** 5 failed attempts = 15-minute lockout
- **Token Blacklisting:** Refresh tokens blacklisted on logout/rotation
- **Email Verification:** Required for full access
- **HTTPS Only:** All production traffic encrypted

## Error Responses

### Invalid Credentials
```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

### Account Locked
```json
{
  "success": false,
  "error": "Account temporarily locked due to multiple failed attempts",
  "lockout": true
}
```

### Token Expired
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

## Best Practices

1. **Store tokens securely** - Use httpOnly cookies or secure storage
2. **Refresh proactively** - Refresh before access token expires
3. **Handle 401 errors** - Redirect to login when token invalid
4. **Logout on sensitive actions** - Clear tokens on password change
5. **Use HTTPS** - Never send tokens over HTTP

## Next Steps

- Explore [Catalog API](../api/catalog.md)
- Learn about [Order Management](../api/orders.md)
