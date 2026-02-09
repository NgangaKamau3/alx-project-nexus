# Deployment Architecture

Complete guide to ModestWear's production deployment on free-tier services.

## Overview

ModestWear is deployed using a cost-effective, scalable architecture leveraging free tiers:

- **Backend:** Render (Free tier)
- **Database:** Neon PostgreSQL (Serverless, Free tier)
- **Redis:** Upstash Redis (Free tier)
- **Media Storage:** Cloudinary (Free tier)
- **Frontend:** Vercel (Free tier)

**Total Monthly Cost:** $0 (within free tier limits)

---

## Architecture Diagram

```
┌─────────────────┐
│   Vercel CDN    │  Frontend (Next.js)
│  modestwear-app │  https://modestwear-app.vercel.app
└────────┬────────┘
         │ HTTPS
         ↓
┌─────────────────┐
│  Render Web     │  Backend (Django + Gunicorn)
│  Service        │  https://modestwear.onrender.com
└────┬───┬───┬────┘
     │   │   │
     │   │   └──────→ ┌──────────────┐
     │   │            │  Cloudinary  │  Media Storage
     │   │            └──────────────┘
     │   │
     │   └──────────→ ┌──────────────┐
     │                │ Upstash Redis│  Cache + Celery
     │                └──────────────┘
     │
     └──────────────→ ┌──────────────┐
                      │Neon PostgreSQL│  Database
                      └──────────────┘
```

---

## Backend Deployment (Render)

### Service Configuration

**Service Type:** Web Service
**Environment:** Python 3.11
**Build Command:** `pip install -r requirements.txt`
**Start Command:** `bash deploy.sh`

### deploy.sh Script

```bash
#!/bin/bash

# Run database migrations
python modestwear/manage.py migrate --no-input

# Collect static files
python modestwear/manage.py collectstatic --no-input

# Create superuser if doesn't exist
python modestwear/manage.py shell << EOF
from django.contrib.auth import get_user_model
import os
User = get_user_model()
email = os.getenv('DJANGO_SUPERUSER_EMAIL')
if email and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        username=os.getenv('DJANGO_SUPERUSER_USERNAME'),
        password=os.getenv('DJANGO_SUPERUSER_PASSWORD')
    )
    print(f'Superuser {email} created')
EOF

# Start Gunicorn server
cd modestwear
gunicorn core.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

### Gunicorn Configuration

- **Workers:** 2 (optimal for free tier: 512MB RAM)
- **Threads:** 4 per worker
- **Timeout:** 120 seconds
- **Worker Class:** sync (default)

**Formula:** `workers = (2 × CPU cores) + 1`
For Render free tier (0.5 CPU): 2 workers

### Environment Variables

```bash
# Django
SECRET_KEY=<generate-with-django>
DEBUG=False
ALLOWED_HOSTS=modestwear.onrender.com,modestwear-app.vercel.app

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# Redis
REDIS_URL=rediss://default:token@host:6379
CELERY_BROKER_URL=rediss://default:token@host:6379
CELERY_RESULT_BACKEND=rediss://default:token@host:6379

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cloudinary
CLOUDINARY_URL=cloudinary://key:secret@cloud

# Social Auth
GOOGLE_CLIENT_ID=your-client-id
FACEBOOK_APP_ID=your-app-id

# Frontend
FRONTEND_URL=https://modestwear-app.vercel.app

# Superuser (auto-created on deploy)
DJANGO_SUPERUSER_EMAIL=admin@modestwear.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=<secure-password>
```

### Free Tier Limitations

- **RAM:** 512 MB
- **CPU:** 0.5 vCPU
- **Bandwidth:** 100 GB/month
- **Build Minutes:** 500 minutes/month
- **Sleep:** Service sleeps after 15 minutes of inactivity

### Preventing Sleep

**Solution:** External cron job pinging health endpoint

```bash
# UptimeRobot or cron-job.org
GET https://modestwear.onrender.com/healthz
Interval: Every 10 minutes
```

**Health Endpoints:**

```python
# /healthz - Lightweight
def healthz(request):
    return JsonResponse({"status": "ok"})

# /health - Comprehensive
def health_check(request):
    # Check database connection
    # Check Redis connection
    # Return detailed status
```

---

## Database (Neon PostgreSQL)

### Configuration

- **Provider:** Neon (Serverless PostgreSQL)
- **Version:** PostgreSQL 15
- **Region:** EU Central (Frankfurt)
- **Connection Pooling:** Enabled
- **SSL:** Required

### Connection String

```
postgresql://user:password@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

### Django Settings

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'neondb',
        'USER': 'neondb_owner',
        'PASSWORD': '<password>',
        'HOST': 'ep-xxx.eu-central-1.aws.neon.tech',
        'PORT': 5432,
        'OPTIONS': {'sslmode': 'require'},
        'CONN_MAX_AGE': 600,  # Connection pooling
        'CONN_HEALTH_CHECKS': True,
    }
}
```

### Free Tier Limits

- **Storage:** 512 MB
- **Compute:** 0.25 vCPU
- **Active Time:** 100 hours/month
- **Branches:** 10

### Optimization

1. **Connection Pooling:** Reuse connections (CONN_MAX_AGE=600)
2. **Indexes:** All foreign keys and frequently queried fields
3. **Query Optimization:** Use select_related() and prefetch_related()
4. **Pagination:** Limit result sets

---

## Redis (Upstash)

### Configuration

- **Provider:** Upstash
- **Type:** Redis 7.0
- **Region:** Global (edge locations)
- **TLS:** Required (rediss://)

### Connection String

```
rediss://default:token@host.upstash.io:6379
```

### Django Settings

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'rediss://default:token@host:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'IGNORE_EXCEPTIONS': True,  # Graceful degradation
        }
    }
}

# Celery
CELERY_BROKER_URL = 'rediss://default:token@host:6379'
CELERY_RESULT_BACKEND = 'rediss://default:token@host:6379'
CELERY_BROKER_USE_SSL = {'ssl_cert_reqs': ssl.CERT_NONE}
```

### Free Tier Limits

- **Storage:** 256 MB
- **Commands:** 10,000/day
- **Bandwidth:** 1 GB/month

### Celery Configuration

**Free Tier Optimization:** Run tasks synchronously

```python
CELERY_TASK_ALWAYS_EAGER = True  # Execute immediately
CELERY_TASK_EAGER_PROPAGATES = True
```

**Why?**
- Render free tier: Single service only
- No separate worker process
- Tasks run in web process
- Suitable for low-volume async tasks (emails)

**Production Alternative:**
- Upgrade to paid tier
- Run separate worker service
- Set CELERY_TASK_ALWAYS_EAGER = False

---

## Media Storage (Cloudinary)

### Configuration

- **Provider:** Cloudinary
- **Plan:** Free tier
- **Features:** Image optimization, transformations, CDN

### Django Settings

```python
import cloudinary

cloudinary.config(
    cloudinary_url=os.getenv('CLOUDINARY_URL')
)

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

### Free Tier Limits

- **Storage:** 25 GB
- **Bandwidth:** 25 GB/month
- **Transformations:** 25,000/month

### Features Used

1. **Auto-optimization:** Compress images
2. **Thumbnails:** Auto-generate on upload
3. **CDN:** Global delivery
4. **Transformations:** Resize, crop, format conversion

---

## Frontend (Vercel)

### Configuration

- **Framework:** Next.js 14
- **Deployment:** Automatic from Git
- **Domain:** modestwear-app.vercel.app

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://modestwear.onrender.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id
```

### Free Tier Limits

- **Bandwidth:** 100 GB/month
- **Build Minutes:** 6,000 minutes/month
- **Serverless Functions:** 100 GB-hours

---

## CI/CD Pipeline

### Automatic Deployment

```
Git Push → GitHub → Render/Vercel → Deploy
```

**Render:**
1. Detects push to main branch
2. Runs build command
3. Executes migrations
4. Starts new service
5. Health check
6. Routes traffic to new version

**Vercel:**
1. Detects push to main branch
2. Builds Next.js app
3. Deploys to CDN
4. Preview deployments for PRs

### Manual Deployment

```bash
# Render
git push origin main

# Or trigger from dashboard
# Render Dashboard → Manual Deploy
```

---

## Monitoring & Logging

### Render Logs

```bash
# View logs in dashboard
Render Dashboard → Service → Logs

# Or via CLI
render logs -f
```

### Django Logging

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
        'level': 'INFO',
    },
}
```

### Health Monitoring

- **UptimeRobot:** Ping every 10 minutes
- **Alerts:** Email on downtime
- **Status Page:** Public status page

---

## Security

### HTTPS/TLS

- **Render:** Automatic SSL certificates
- **Vercel:** Automatic SSL certificates
- **Neon:** TLS required
- **Upstash:** TLS required (rediss://)

### Django Security Settings

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

### CORS Configuration

```python
CORS_ALLOWED_ORIGINS = [
    'https://modestwear-app.vercel.app',
    'https://modestwear.onrender.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://modestwear-app.vercel.app',
    'https://modestwear.onrender.com',
]
```

---

## Scaling Strategy

### Current (Free Tier)

- **Users:** ~100 concurrent
- **Requests:** ~10,000/day
- **Storage:** ~500 MB database

### Scaling Path

**Phase 1: Optimize Free Tier**
- Add caching (Redis)
- Optimize queries
- CDN for static files

**Phase 2: Paid Tier ($7-20/month)**
- Render: Starter plan ($7/month)
- Neon: Scale plan ($19/month)
- Separate Celery worker

**Phase 3: Horizontal Scaling**
- Multiple Render instances
- Load balancer
- Read replicas (Neon)
- Dedicated Redis

**Phase 4: Enterprise**
- AWS/GCP migration
- Kubernetes
- Auto-scaling
- Multi-region

---

## Backup & Recovery

### Database Backups

**Neon:** Automatic daily backups (7-day retention)

**Manual Backup:**
```bash
pg_dump $DATABASE_URL > backup.sql
```

**Restore:**
```bash
psql $DATABASE_URL < backup.sql
```

### Media Backups

**Cloudinary:** Automatic backups included

**Manual Backup:**
```bash
# Download all media
cloudinary-cli download --all
```

---

## Troubleshooting

### Service Won't Start

**Check:**
1. Build logs for errors
2. Environment variables set correctly
3. Database connection string
4. Migrations completed

### Database Connection Errors

**Solutions:**
1. Check DATABASE_URL format
2. Verify SSL mode: `?sslmode=require`
3. Test connection: `psql $DATABASE_URL`
4. Check Neon active hours

### Redis Connection Errors

**Solutions:**
1. Verify rediss:// (with double 's')
2. Check SSL configuration
3. Test: `redis-cli -u $REDIS_URL ping`
4. Enable IGNORE_EXCEPTIONS for graceful degradation

### Out of Memory

**Solutions:**
1. Reduce Gunicorn workers
2. Optimize queries
3. Add pagination
4. Upgrade to paid tier

---

## Cost Optimization

### Current Setup (Free)

| Service | Plan | Cost |
|---------|------|------|
| Render | Free | $0 |
| Neon | Free | $0 |
| Upstash | Free | $0 |
| Cloudinary | Free | $0 |
| Vercel | Free | $0 |
| **Total** | | **$0/month** |

### Paid Upgrade Path

| Service | Plan | Cost |
|---------|------|------|
| Render | Starter | $7/month |
| Neon | Scale | $19/month |
| Upstash | Pay-as-you-go | ~$5/month |
| Cloudinary | Plus | $89/month |
| Vercel | Pro | $20/month |
| **Total** | | **$140/month** |

---

## Next Steps

- Review [Security Architecture](security.md)
- Learn about [Database Design](database.md)
- Explore [API Documentation](../api/authentication.md)
