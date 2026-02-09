# Authentication API

Complete reference for user authentication, registration, and token management.

## Overview

ModestWear implements a hybrid authentication system:
- **Traditional**: Email/password with JWT tokens
- **Social OAuth**: Google and Facebook login
- **Email Verification**: Required for full access
- **Security**: Account lockout, token blacklisting, password validation

## Endpoints Summary

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/users/register/` | POST | No | Create new account |
| `/api/users/login/` | POST | No | Authenticate user |
| `/api/users/logout/` | POST | Yes | Invalidate tokens |
| `/api/users/verify-email/` | POST | No | Verify email address |
| `/api/users/token/refresh/` | POST | No | Refresh access token |
| `/api/users/token/validate/` | GET | Yes | Validate current token |
| `/api/users/social/google/` | POST | No | Google OAuth login |
| `/api/users/social/facebook/` | POST | No | Facebook OAuth login |
| `/api/users/profile/` | GET | Yes | Get user profile |
| `/api/users/profile/` | PUT/PATCH | Yes | Update profile |

---

## Registration

### POST /api/users/register/

Create a new user account with email and password.

**Authentication:** Not required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | Valid email address (unique) |
| password | string | Yes | Min 8 chars, not too common |
| full_name | string | Yes | Auto-split into first/last name |
| phone_number | string | No | Contact number |

**Password Requirements:**
- Minimum 8 characters
- Cannot be too similar to email/username
- Cannot be entirely numeric
- Cannot be a commonly used password

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah@example.com",
    "password": "SecurePass123!",
    "full_name": "Sarah Ahmed",
    "phone_number": "+27123456789"
  }'
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 15,
      "email": "sarah@example.com",
      "username": "sarah",
      "first_name": "Sarah",
      "last_name": "Ahmed",
      "phone_number": "+27123456789",
      "profile_picture": null,
      "profile_picture_url": null,
      "created_at": "2024-01-20T14:30:00Z"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "Bearer",
      "expires_in": 900,
      "refresh_expires_in": 1209600
    },
    "is_new_user": true,
    "email_verified": false
  }
}
```

**Business Logic:**
1. Validates email format and uniqueness
2. Validates password against Django's validators
3. Auto-generates username from email prefix
4. Sets `is_verified=false` initially
5. Sends verification email asynchronously
6. Returns JWT tokens immediately (user can browse)
7. Logs registration event with IP address

**Error Responses:**

**Email Already Exists (400):**
```json
{
  "success": false,
  "error": "A user with this email already exists."
}
```

**Weak Password (400):**
```json
{
  "success": false,
  "error": "This password is too common., This password is entirely numeric."
}
```

**Missing Fields (400):**
```json
{
  "success": false,
  "error": "Email, password, and full name are required"
}
```

---

## Email Verification

### POST /api/users/verify-email/

Verify user's email address using token from email.

**Authentication:** Not required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | Verification token from email |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123xyz789..."
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Email verified successfully",
  "data": {
    "email": "sarah@example.com",
    "is_verified": true
  }
}
```

**Business Logic:**
1. Decodes and validates token
2. Checks token expiration (72 hours)
3. Updates `is_verified=true` in database
4. Clears verification token cache
5. Logs verification event

**Token Format:**
- Base64 encoded JSON: `{"user_id": 15, "email": "sarah@example.com", "timestamp": 1705756800}`
- Signed with SECRET_KEY
- Expires after 72 hours (EMAIL_VERIFICATION_TIMEOUT)

**Error Responses:**

**Invalid Token (400):**
```json
{
  "success": false,
  "error": "Invalid verification token"
}
```

**Expired Token (400):**
```json
{
  "success": false,
  "error": "Verification token has expired"
}
```

**Already Verified (400):**
```json
{
  "success": false,
  "error": "Email already verified"
}
```

---

## Login

### POST /api/users/login/

Authenticate user and receive JWT tokens.

**Authentication:** Not required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email address |
| password | string | Yes | User's password |
| device_info | object | No | Device metadata for audit |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah@example.com",
    "password": "SecurePass123!",
    "device_info": {
      "device_type": "mobile",
      "os": "iOS 17",
      "app_version": "1.0.0"
    }
  }'
```

**Success Response (200 OK):**
```json
{
  "data": {
    "user": {
      "id": 15,
      "email": "sarah@example.com",
      "username": "sarah",
      "first_name": "Sarah",
      "last_name": "Ahmed",
      "phone_number": "+27123456789",
      "profile_picture_url": "https://res.cloudinary.com/.../profile.jpg",
      "created_at": "2024-01-20T14:30:00Z"
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "Bearer",
      "expires_in": 900,
      "refresh_expires_in": 1209600
    },
    "email_verified": true,
    "verification_needed": false
  }
}
```

**Business Logic:**
1. Checks for account lockout (Redis cache)
2. Authenticates credentials with Django's auth system
3. Validates account is active
4. Clears failed login attempts on success
5. Updates `last_login` timestamp
6. Generates new JWT token pair
7. Logs successful login with IP and user agent
8. Returns user profile and tokens

**Security Features:**
- **Rate Limiting:** 5 failed attempts = 15-minute lockout
- **Failed Attempt Tracking:** Stored in Redis with 30-minute TTL
- **IP Logging:** All login attempts logged with IP address
- **Device Tracking:** Optional device_info for audit trail

**Error Responses:**

**Invalid Credentials (401):**
```json
{
  "success": false,
  "error": "Invalid email or password"
}
```

**Account Locked (403):**
```json
{
  "success": false,
  "error": "Account temporarily locked due to multiple failed attempts. Try again later.",
  "lockout": true
}
```

**Account Disabled (403):**
```json
{
  "success": false,
  "error": "Account is disabled. Please contact support."
}
```

**Unverified Email (200 with flag):**
```json
{
  "data": {
    "user": {...},
    "tokens": {...},
    "email_verified": false,
    "verification_needed": true
  }
}
```

---

## Token Refresh

### POST /api/users/token/refresh/

Get new access token using refresh token.

**Authentication:** Not required (uses refresh token)

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh_token | string | Yes | Valid refresh token |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

**Business Logic:**
1. Validates refresh token signature
2. Checks token not blacklisted
3. Checks token not expired (14 days)
4. Generates new access token (15 minutes)
5. Rotates refresh token (new one issued)
6. Blacklists old refresh token
7. Returns new token pair

**Token Rotation:**
- `ROTATE_REFRESH_TOKENS=True`: New refresh token on each refresh
- `BLACKLIST_AFTER_ROTATION=True`: Old token blacklisted
- Prevents token reuse attacks

**Error Responses:**

**Invalid Token (401):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**Blacklisted Token (401):**
```json
{
  "detail": "Token is blacklisted",
  "code": "token_not_valid"
}
```

---

## Token Validation

### GET /api/users/token/validate/

Validate current access token and get user info.

**Authentication:** Required (Bearer token)

**Example Request:**
```bash
curl https://modestwear.onrender.com/api/users/token/validate/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "user_id": 15,
    "email_verified": true
  }
}
```

**Business Logic:**
1. Extracts token from Authorization header
2. Validates token signature and expiration
3. Checks user_id matches authenticated user
4. Retrieves verification status (cached)
5. Returns validation result

**Use Cases:**
- Frontend token validation on app load
- Check if token still valid before API calls
- Verify email verification status

---

## Logout

### POST /api/users/logout/

Invalidate refresh token and log out user.

**Authentication:** Required (Bearer token)

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh_token | string | Optional | Token to blacklist |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Successfully logged out"
}
```

**Business Logic:**
1. Extracts JTI (JWT ID) from refresh token
2. Adds JTI to blacklist (Redis + database)
3. Logs logout event
4. Clears HTTP-only cookie if used
5. Returns success message

**Note:** Access token remains valid until expiration (15 minutes). Frontend should discard it immediately.

---

## Google OAuth

### POST /api/users/social/google/

Authenticate using Google account.

**Authentication:** Not required

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| token | string | Yes | Google ID token from frontend |

**Example Request:**
```bash
curl -X POST https://modestwear.onrender.com/api/users/social/google/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE4MmU0..."
  }'
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 16,
      "email": "sarah@gmail.com",
      "username": "sarah",
      "first_name": "Sarah",
      "last_name": "Ahmed",
      "profile_picture_url": "https://lh3.googleusercontent.com/...",
      "is_verified": true
    },
    "tokens": {
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "token_type": "Bearer",
      "expires_in": 900
    },
    "is_new_user": false,
    "provider": "google"
  }
}
```

**Business Logic:**
1. Verifies Google token with Google's API
2. Extracts user info (email, name, picture)
3. Checks if user exists by email
4. **If new user:**
   - Creates account with random password
   - Sets `is_verified=true` (Google verified)
   - Downloads and uploads profile picture to Cloudinary
5. **If existing user:**
   - Links Google account if not already linked
   - Updates profile picture if changed
6. Generates JWT tokens
7. Returns user data and tokens

**Google OAuth Flow:**
```
Frontend                    Backend                     Google
   |                           |                           |
   |-- 1. Initiate OAuth ----->|                           |
   |                           |-- 2. Redirect to Google ->|
   |<------------------------- 3. Google Login ------------|
   |-- 4. Send ID Token ------>|                           |
   |                           |-- 5. Verify Token ------->|
   |                           |<-- 6. User Info ----------|
   |                           |-- 7. Create/Link User     |
   |<-- 8. JWT Tokens ---------|                           |
```

**Security:**
- Token verified server-side with Google
- No password stored for social users
- Email auto-verified (trusted provider)
- Profile picture securely stored on Cloudinary

**Error Responses:**

**Invalid Google Token (400):**
```json
{
  "success": false,
  "error": "Invalid Google token"
}
```

**Google API Error (500):**
```json
{
  "success": false,
  "error": "Failed to verify Google token"
}
```

---

## User Profile

### GET /api/users/profile/

Get authenticated user's profile.

**Authentication:** Required

**Example Request:**
```bash
curl https://modestwear.onrender.com/api/users/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

**Success Response (200 OK):**
```json
{
  "id": 15,
  "email": "sarah@example.com",
  "username": "sarah",
  "first_name": "Sarah",
  "last_name": "Ahmed",
  "phone_number": "+27123456789",
  "profile_picture": "users/profiles/sarah_abc123.jpg",
  "profile_picture_url": "https://res.cloudinary.com/.../sarah_abc123.jpg",
  "created_at": "2024-01-20T14:30:00Z"
}
```

### PUT/PATCH /api/users/profile/

Update user profile.

**Authentication:** Required

**Request Body:**

| Field | Type | Description |
|-------|------|-------------|
| first_name | string | User's first name |
| last_name | string | User's last name |
| phone_number | string | Contact number |
| profile_picture | file | Image file (multipart/form-data) |

**Example Request:**
```bash
curl -X PATCH https://modestwear.onrender.com/api/users/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Sarah",
    "last_name": "Ahmed Khan",
    "phone_number": "+27987654321"
  }'
```

**Success Response (200 OK):**
```json
{
  "id": 15,
  "email": "sarah@example.com",
  "username": "sarah",
  "first_name": "Sarah",
  "last_name": "Ahmed Khan",
  "phone_number": "+27987654321",
  "profile_picture_url": "https://res.cloudinary.com/.../sarah_abc123.jpg",
  "created_at": "2024-01-20T14:30:00Z"
}
```

**Business Logic:**
- Email and username cannot be changed
- Profile picture uploaded to Cloudinary
- Old profile picture deleted from Cloudinary
- Thumbnail auto-generated

---

## JWT Token Structure

### Access Token Payload
```json
{
  "token_type": "access",
  "exp": 1705757700,
  "iat": 1705756800,
  "jti": "abc123xyz789",
  "user_id": 15
}
```

### Refresh Token Payload
```json
{
  "token_type": "refresh",
  "exp": 1706966400,
  "iat": 1705756800,
  "jti": "def456uvw012",
  "user_id": 15
}
```

**Token Lifetimes:**
- Access: 15 minutes (900 seconds)
- Refresh: 14 days (1,209,600 seconds)

**Algorithm:** HS256 (HMAC with SHA-256)

---

## Security Best Practices

1. **Store tokens securely** - Use httpOnly cookies or secure storage
2. **Refresh proactively** - Refresh 1-2 minutes before expiration
3. **Handle 401 errors** - Redirect to login when unauthorized
4. **Use HTTPS only** - Never send tokens over HTTP
5. **Logout on sensitive actions** - Clear tokens on password change
6. **Validate on app load** - Check token validity on startup
7. **Don't log tokens** - Never log full tokens in frontend

## Next Steps

- Explore [Catalog API](catalog.md)
- Learn about [Orders API](orders.md)
- Read [Security Architecture](../architecture/security.md)
