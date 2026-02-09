# Security Architecture

Comprehensive security measures implemented in ModestWear API.

## Overview

ModestWear implements defense-in-depth security with multiple layers:
- **Authentication:** JWT tokens with rotation
- **Authorization:** Role-based access control
- **Data Protection:** Encryption at rest and in transit
- **Input Validation:** Comprehensive sanitization
- **Rate Limiting:** Prevent abuse
- **Monitoring:** Security event logging

---

## Authentication Security

### JWT Token Management

**Token Structure:**
```json
{
  "token_type": "access",
  "exp": 1705757700,
  "iat": 1705756800,
  "jti": "unique-token-id",
  "user_id": 15
}
```

**Security Features:**

1. **Short-Lived Access Tokens**
   - Lifetime: 15 minutes
   - Reduces exposure window
   - Forces regular refresh

2. **Token Rotation**
   - New refresh token on each refresh
   - Old token immediately blacklisted
   - Prevents token reuse attacks

3. **Token Blacklisting**
   - Logout blacklists refresh token
   - Stored in Redis + database
   - Checked on every token use

4. **Secure Algorithm**
   - HS256 (HMAC-SHA256)
   - Secret key never exposed
   - Signature verification on every request

**Implementation:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}
```

### Password Security

**Hashing:**
- Algorithm: PBKDF2-SHA256
- Iterations: 390,000 (Django 4.2 default)
- Salt: Unique per password
- Never stored in plaintext

**Validation Rules:**
```python
AUTH_PASSWORD_VALIDATORS = [
    'UserAttributeSimilarityValidator',  # Not similar to username/email
    'MinimumLengthValidator',            # Min 8 characters
    'CommonPasswordValidator',           # Not in common password list
    'NumericPasswordValidator',          # Not entirely numeric
]
```

**Example Rejected Passwords:**
- `password123` (too common)
- `12345678` (entirely numeric)
- `sarah@example.com` (similar to email)

### Account Lockout

**Brute Force Protection:**
```python
# After 5 failed attempts
cache.set(f'account_lockout:{email}', True, timeout=900)  # 15 minutes
```

**Features:**
- Tracks failed login attempts (Redis)
- 5 attempts = 15-minute lockout
- Counter resets on successful login
- Logs all failed attempts with IP

**Implementation:**
```python
failed_attempts = cache.get(f'failed_logins:{email}', 0) + 1
cache.set(f'failed_logins:{email}', failed_attempts, timeout=1800)

if failed_attempts >= 5:
    cache.set(f'account_lockout:{email}', True, timeout=900)
    logger.warning(f'Account locked: {email} from IP: {ip_address}')
```

### Email Verification

**Token Generation:**
```python
token_data = {
    'user_id': user.id,
    'email': user.email,
    'timestamp': int(time.time())
}
token = base64.urlsafe_b64encode(
    signing.dumps(token_data).encode()
).decode()
```

**Security Features:**
- Signed with SECRET_KEY
- Expires after 72 hours
- One-time use (deleted after verification)
- Tamper-proof (signature validation)

### Social OAuth Security

**Google OAuth Flow:**
1. Frontend receives ID token from Google
2. Backend verifies token with Google's API
3. Validates token signature and expiration
4. Extracts verified email
5. Creates/links user account
6. Issues JWT tokens

**Security Measures:**
- Server-side token verification
- No client secrets exposed
- Email auto-verified (trusted provider)
- Profile picture securely stored

**Implementation:**
```python
from google.oauth2 import id_token
from google.auth.transport import requests

# Verify token with Google
idinfo = id_token.verify_oauth2_token(
    token, 
    requests.Request(), 
    settings.GOOGLE_CLIENT_ID
)

# Extract verified data
email = idinfo['email']
email_verified = idinfo['email_verified']
```

---

## Authorization & Access Control

### Permission Levels

| Level | Description | Access |
|-------|-------------|--------|
| **Anonymous** | Unauthenticated users | Public products, categories |
| **Authenticated** | Logged-in users | Cart, wishlist, orders, profile |
| **Staff** | Admin users | Admin panel, all data |
| **Superuser** | System admins | Full system access |

### Endpoint Protection

**Public Endpoints:**
```python
@permission_classes([AllowAny])
def product_list(request):
    # Anyone can view products
```

**Authenticated Endpoints:**
```python
@permission_classes([IsAuthenticated])
def cart_view(request):
    # Only logged-in users
```

**Owner-Only Access:**
```python
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    if order.user != request.user:
        return Response(status=403)  # Forbidden
```

### CORS Configuration

**Allowed Origins:**
```python
CORS_ALLOWED_ORIGINS = [
    'https://modestwear-app.vercel.app',  # Production frontend
    'https://modestwear.onrender.com',    # Backend
]
```

**Security Headers:**
```python
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'authorization',
    'content-type',
    'x-csrftoken',
]
```

### CSRF Protection

**Token-Based:**
```python
CSRF_COOKIE_SECURE = True  # HTTPS only
CSRF_COOKIE_HTTPONLY = True  # No JavaScript access
CSRF_COOKIE_SAMESITE = 'Strict'
```

**Trusted Origins:**
```python
CSRF_TRUSTED_ORIGINS = [
    'https://modestwear-app.vercel.app',
    'https://modestwear.onrender.com',
]
```

---

## Data Protection

### Encryption in Transit

**HTTPS/TLS:**
- All traffic encrypted (TLS 1.2+)
- Automatic SSL certificates (Render/Vercel)
- HSTS enabled (force HTTPS)

**Django Settings:**
```python
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Encryption at Rest

**Database:**
- Neon PostgreSQL: Encrypted at rest (AES-256)
- Automatic backups encrypted

**Media Files:**
- Cloudinary: Encrypted storage
- Secure URLs with signed tokens

**Sensitive Data:**
```python
# Passwords
password = make_password(raw_password)  # PBKDF2-SHA256

# API Keys
SECRET_KEY = os.getenv('SECRET_KEY')  # Never in code
```

### PII Protection

**Personal Identifiable Information:**
- Email addresses
- Phone numbers
- Delivery addresses
- Payment information

**Protection Measures:**
1. **Access Control:** Only owner can view
2. **Logging:** PII never logged
3. **Encryption:** Encrypted in transit and at rest
4. **Retention:** Deleted on account deletion

**Example:**
```python
# Never log PII
logger.info(f'User logged in: {user.id}')  # ✓ User ID only
logger.info(f'User logged in: {user.email}')  # ✗ Email exposed
```

---

## Input Validation & Sanitization

### Request Validation

**Django REST Framework Serializers:**
```python
class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
```

### SQL Injection Prevention

**Django ORM:**
- Parameterized queries (automatic)
- No raw SQL without parameters
- Input sanitization

**Safe:**
```python
Product.objects.filter(name=user_input)  # ✓ Parameterized
```

**Unsafe:**
```python
Product.objects.raw(f"SELECT * FROM products WHERE name='{user_input}'")  # ✗ SQL injection
```

### XSS Prevention

**Output Escaping:**
- Django templates auto-escape HTML
- API returns JSON (not HTML)
- Content-Type headers enforced

**Security Headers:**
```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### File Upload Security

**Image Validation:**
```python
def validate_image(file):
    # Check file size
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("File too large")
    
    # Check file type
    if not file.content_type.startswith('image/'):
        raise ValidationError("Invalid file type")
    
    # Verify image integrity
    try:
        Image.open(file)
    except:
        raise ValidationError("Corrupted image")
```

**Cloudinary Security:**
- Automatic malware scanning
- Format validation
- Size limits enforced

---

## Rate Limiting

### Throttling Configuration

**Anonymous Users:**
```python
class AnonRateThrottle(BaseThrottle):
    rate = '100/hour'  # 100 requests per hour
```

**Authenticated Users:**
```python
class UserRateThrottle(BaseThrottle):
    rate = '1000/hour'  # 1000 requests per hour
```

**Sensitive Endpoints:**
```python
class LoginRateThrottle(BaseThrottle):
    rate = '5/minute'  # 5 login attempts per minute
```

### Implementation

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'login': '5/minute',
    }
}
```

---

## Security Monitoring

### Logging

**Security Events Logged:**
- Failed login attempts
- Account lockouts
- Token blacklisting
- Permission denials
- Suspicious activity

**Implementation:**
```python
import logging
logger = logging.getLogger(__name__)

# Failed login
logger.warning(f'Failed login: {email} from IP: {ip_address}')

# Account lockout
logger.warning(f'Account locked: {email} from IP: {ip_address}')

# Permission denied
logger.warning(f'Unauthorized access attempt: User {user.id} to Order {order.id}')
```

### Audit Trail

**Database Logging:**
```python
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    resource = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

**Tracked Actions:**
- User registration
- Login/logout
- Password changes
- Order creation
- Admin actions

---

## Vulnerability Prevention

### Common Vulnerabilities

| Vulnerability | Prevention |
|---------------|------------|
| **SQL Injection** | Django ORM parameterized queries |
| **XSS** | Output escaping, Content-Type headers |
| **CSRF** | CSRF tokens, SameSite cookies |
| **Clickjacking** | X-Frame-Options: DENY |
| **MITM** | HTTPS/TLS, HSTS |
| **Brute Force** | Account lockout, rate limiting |
| **Session Hijacking** | Secure cookies, token rotation |
| **File Upload** | Type validation, size limits, scanning |

### Security Headers

```python
# Prevent clickjacking
X_FRAME_OPTIONS = 'DENY'

# Prevent MIME sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable XSS filter
SECURE_BROWSER_XSS_FILTER = True

# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

---

## Secrets Management

### Environment Variables

**Never in Code:**
```python
# ✗ Bad
SECRET_KEY = 'hardcoded-secret-key'

# ✓ Good
SECRET_KEY = os.getenv('SECRET_KEY')
```

**Storage:**
- Development: `.env` file (gitignored)
- Production: Render environment variables
- Never committed to Git

### Sensitive Data

**Protected:**
- SECRET_KEY
- DATABASE_URL
- Email passwords
- API keys (Cloudinary, Google, etc.)
- JWT signing keys

**Access Control:**
- Only admins can view
- Encrypted in Render dashboard
- Rotated regularly

---

## Compliance & Best Practices

### GDPR Compliance

**User Rights:**
1. **Right to Access:** Users can download their data
2. **Right to Deletion:** Account deletion removes all PII
3. **Right to Rectification:** Users can update their data
4. **Data Portability:** Export in JSON format

**Implementation:**
```python
# Data export
def export_user_data(user):
    return {
        'profile': UserSerializer(user).data,
        'orders': OrderSerializer(user.orders.all(), many=True).data,
        'wishlist': WishlistSerializer(user.wishlist.all(), many=True).data,
    }

# Account deletion
def delete_account(user):
    user.orders.all().update(user=None)  # Anonymize orders
    user.delete()  # Delete user and related data
```

### Security Best Practices

1. **Principle of Least Privilege:** Users only access their own data
2. **Defense in Depth:** Multiple security layers
3. **Secure by Default:** Secure settings out of the box
4. **Regular Updates:** Dependencies updated regularly
5. **Security Audits:** Regular code reviews
6. **Incident Response:** Plan for security breaches

---

## Security Checklist

### Development

- [ ] No secrets in code
- [ ] Input validation on all endpoints
- [ ] Output escaping enabled
- [ ] HTTPS in development (optional)
- [ ] Security headers configured

### Pre-Production

- [ ] All dependencies updated
- [ ] Security audit completed
- [ ] Penetration testing done
- [ ] Rate limiting configured
- [ ] Logging enabled

### Production

- [ ] HTTPS enforced
- [ ] HSTS enabled
- [ ] Secrets in environment variables
- [ ] Database encrypted
- [ ] Backups configured
- [ ] Monitoring enabled
- [ ] Incident response plan ready

---

## Incident Response

### Security Breach Protocol

1. **Detect:** Monitor logs for suspicious activity
2. **Contain:** Disable affected accounts/services
3. **Investigate:** Analyze logs, identify breach source
4. **Remediate:** Patch vulnerability, rotate secrets
5. **Notify:** Inform affected users (GDPR requirement)
6. **Review:** Post-mortem, improve security

### Contact

**Security Issues:** security@modestwear.com

**Responsible Disclosure:**
- Report vulnerabilities privately
- Allow 90 days for fix before public disclosure
- Acknowledgment in security hall of fame

---

## Next Steps

- Review [Deployment Architecture](deployment.md)
- Explore [Database Design](database.md)
- Read [API Documentation](../api/authentication.md)
