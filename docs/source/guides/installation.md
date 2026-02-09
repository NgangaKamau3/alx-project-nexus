# Installation Guide

Complete guide to setting up ModestWear API locally for development.

## Prerequisites

- **Python:** 3.11 or higher
- **PostgreSQL:** 15 or higher
- **Redis:** 7.0 or higher (optional for caching)
- **Git:** For cloning repository

## Quick Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/modestwear.git
cd modestwear
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
cd modestwear
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in `modestwear/core/` directory:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-generate-with-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/modestwear

# Redis (optional for development)
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# Email (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cloudinary (optional for development)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# Social Auth
GOOGLE_CLIENT_ID=your-google-client-id
FACEBOOK_APP_ID=your-facebook-app-id

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 5. Setup Database

```bash
# Create PostgreSQL database
createdb modestwear

# Or using psql
psql -U postgres
CREATE DATABASE modestwear;
\q
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Load Sample Data (Optional)

```bash
python manage.py loaddata fixtures/sample_data.json
```

### 9. Run Development Server

```bash
python manage.py runserver
```

API will be available at: `http://localhost:8000`

---

## Detailed Setup

### PostgreSQL Setup

#### Windows

1. Download PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. Install with default settings
3. Remember the password for `postgres` user
4. Add PostgreSQL bin to PATH

```bash
# Create database
psql -U postgres
CREATE DATABASE modestwear;
CREATE USER modestwear_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE modestwear TO modestwear_user;
\q
```

#### macOS

```bash
# Install via Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb modestwear
```

#### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE modestwear;
CREATE USER modestwear_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE modestwear TO modestwear_user;
\q
```

### Redis Setup (Optional)

#### Windows

1. Download Redis from [redis.io](https://redis.io/download)
2. Or use WSL: `wsl --install`
3. In WSL: `sudo apt install redis-server`

#### macOS

```bash
brew install redis
brew services start redis
```

#### Linux

```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### Cloudinary Setup (Optional)

1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Get your `CLOUDINARY_URL` from dashboard
3. Add to `.env` file

For local development, you can skip Cloudinary and use local media storage.

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized origins:
   - `http://localhost:8000`
   - `http://localhost:3000`
6. Copy Client ID to `.env`

---

## Project Structure

```
modestwear/
├── core/                       # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── .env                    # Environment variables
├── apps/                       # Application modules
│   ├── users/                  # Authentication & profiles
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── auth/               # Auth logic
│   │   └── verification/       # Email verification
│   ├── catalog/                # Product catalog
│   │   ├── models.py
│   │   ├── views.py
│   │   └── services.py
│   ├── orders/                 # Cart & orders
│   │   ├── models.py
│   │   └── views.py
│   └── outfits/                # Outfit builder
│       ├── models.py
│       └── views.py
├── static/                     # Static files
├── media/                      # Uploaded files (local)
├── templates/                  # Email templates
├── manage.py
└── requirements.txt
```

---

## Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.catalog

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

---

## Development Tools

### Django Admin

Access at: `http://localhost:8000/admin/`

Login with superuser credentials created earlier.

### API Documentation

- **Swagger UI:** `http://localhost:8000/docs/`
- **ReDoc:** `http://localhost:8000/redoc/`

### Django Shell

```bash
python manage.py shell

# Example: Create test data
from apps.catalog.models import Category, Product
category = Category.objects.create(name="Dresses", slug="dresses")
```

### Database Shell

```bash
python manage.py dbshell
```

---

## Common Issues

### Issue: ModuleNotFoundError

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Database connection error

**Solution:**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Test connection: `psql -U modestwear_user -d modestwear`

### Issue: Redis connection error

**Solution:**
- Check Redis is running: `redis-cli ping` (should return PONG)
- Or disable Redis in settings for development

### Issue: Email not sending

**Solution:**
- Use Gmail App Password (not regular password)
- Enable "Less secure app access" or use App Password
- Or use console backend for development:
  ```python
  EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
  ```

### Issue: Static files not loading

**Solution:**
```bash
python manage.py collectstatic
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/new-feature
```

### 2. Make Changes

Edit code, add features, fix bugs.

### 3. Run Tests

```bash
python manage.py test
```

### 4. Check Code Quality

```bash
# Install tools
pip install flake8 black

# Format code
black .

# Check linting
flake8 .
```

### 5. Commit Changes

```bash
git add .
git commit -m "Add new feature"
```

### 6. Push and Create PR

```bash
git push origin feature/new-feature
```

---

## Environment-Specific Settings

### Development

```python
# core/settings.py
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Staging

```python
DEBUG = False
ALLOWED_HOSTS = ['staging.modestwear.com']
SECURE_SSL_REDIRECT = True
```

### Production

```python
DEBUG = False
ALLOWED_HOSTS = ['modestwear.onrender.com', 'modestwear.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

---

## Next Steps

- Read [Authentication Guide](authentication.md)
- Explore [API Endpoints](../api/catalog.md)
- Learn about [Deployment](../architecture/deployment.md)
