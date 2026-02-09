# ModestWear API Documentation

Comprehensive documentation for the ModestWear REST API built with Sphinx and MyST Parser.

## 📚 Documentation Contents

### Getting Started
- **Quickstart Guide** - Get up and running in 5 minutes
- **Authentication Guide** - Complete auth flow with examples
- **Installation Guide** - Local development setup

### API Reference
- **Authentication API** - Registration, login, OAuth, tokens (30+ endpoints)
- **Catalog API** - Products, categories, filtering, search
- **Orders API** - Cart, wishlist, orders, payment
- **Outfits API** - Outfit builder and recommendations
- **Error Handling** - Complete error reference

### Architecture
- **Database Schema** - ERD, design rationale, 11 tables
- **Deployment** - Production setup on free tier
- **Security** - Authentication, encryption, best practices

### Additional
- **Testing Guide** - Unit, integration, load testing

## 🚀 Quick Build

### 1. Install Dependencies

```bash
cd docs
pip install -r requirements.txt
```

### 2. Build HTML Documentation

```bash
# Windows
sphinx-build -b html source build/html

# macOS/Linux
make html
```

### 3. View Documentation

Open `build/html/index.html` in your browser.

## 📖 What's Included

### Comprehensive Coverage

✅ **30+ API Endpoints** - Every endpoint documented with:
- Request/response examples
- Authentication requirements
- Query parameters
- Error responses
- Business logic explanation
- Use cases

✅ **Database Architecture** - Complete schema with:
- 11 tables across 4 modules
- Entity Relationship Diagram
- Design rationale for each table
- Relationships and constraints
- Performance optimizations

✅ **Security** - Production-grade security:
- JWT authentication flow
- Password hashing (PBKDF2-SHA256)
- Account lockout mechanism
- CORS and CSRF protection
- Rate limiting
- Encryption at rest and in transit

✅ **Deployment** - Free tier architecture:
- Render (backend)
- Neon PostgreSQL (database)
- Upstash Redis (cache)
- Cloudinary (media)
- Vercel (frontend)
- Cost: $0/month

✅ **Error Handling** - Every error documented:
- HTTP status codes
- Error response formats
- Client-side handling
- Debugging tips

✅ **Testing** - Complete testing guide:
- Unit tests
- Integration tests
- Load testing with Locust
- Manual testing with Swagger/cURL/Postman

## 📝 Documentation Structure

```
docs/
├── source/
│   ├── index.md                      # Main landing page
│   ├── guides/
│   │   ├── quickstart.md             # 5-minute quick start
│   │   ├── authentication.md         # Complete auth guide
│   │   ├── installation.md           # Local setup
│   │   └── testing.md                # Testing guide
│   ├── api/
│   │   ├── authentication.md         # Auth endpoints (8 endpoints)
│   │   ├── catalog.md                # Product endpoints (4 endpoints)
│   │   ├── orders.md                 # Order endpoints (12 endpoints)
│   │   ├── outfits.md                # Outfit endpoints (7 endpoints)
│   │   └── errors.md                 # Error reference
│   └── architecture/
│       ├── database.md               # Database schema & ERD
│       ├── deployment.md             # Production deployment
│       └── security.md               # Security architecture
├── conf.py                           # Sphinx configuration
├── requirements.txt                  # Python dependencies
├── Makefile                          # Build commands (Unix)
└── README.md                         # This file
```

## ✨ Features

- **Markdown-based** - Easy to write and maintain
- **MyST extensions** - Admonitions, code blocks, tables
- **Read the Docs theme** - Professional, mobile-responsive
- **Code syntax highlighting** - With copy buttons
- **Search functionality** - Built-in full-text search
- **Cross-references** - Link between pages
- **Mermaid diagrams** - For ERDs and architecture
- **Interactive examples** - cURL, Python, JavaScript

## 🎯 Key Highlights

### Authentication API (8 Endpoints)
- Registration with email verification
- Login with JWT tokens
- Token refresh and validation
- Google OAuth integration
- Account lockout after 5 failed attempts
- Password validation (8+ chars, not common)

### Catalog API (4 Endpoints)
- Product listing with pagination
- Advanced filtering (category, coverage level, price)
- Full-text search
- Coverage level filtering (unique to modest fashion)

### Orders API (12 Endpoints)
- Shopping cart (guest + authenticated)
- Wishlist management
- Order creation and tracking
- Order status lifecycle
- Price history preservation

### Outfits API (7 Endpoints)
- Create outfit combinations
- Public/private sharing
- Community feed
- Foundation for AI recommendations

### Database (11 Tables)
- Users module (1 table)
- Catalog module (5 tables)
- Orders module (4 tables)
- Outfits module (2 tables)

## 🔧 Writing Documentation

### Markdown with MyST

All documentation is written in Markdown with MyST extensions:

```markdown
# Page Title

Regular markdown content...

## Code Blocks

\`\`\`python
def example():
    return "Hello"
\`\`\`

## Admonitions

:::{note}
This is a note
:::

:::{warning}
This is a warning
:::

:::{tip}
This is a tip
:::

## Cross-References

Link to other pages: [Authentication](authentication.md)
```

### Adding New Pages

1. Create `.md` file in appropriate directory
2. Add to `toctree` in `index.md` or parent page
3. Rebuild documentation: `make html`

## 🌐 Deployment Options

### GitHub Pages

```bash
# Build docs
make html

# Deploy to gh-pages branch
gh-pages -d build/html
```

### Read the Docs

1. Connect repository to Read the Docs
2. Configure build settings:
   - Requirements file: `docs/requirements.txt`
   - Python version: 3.11
3. Automatic builds on push

### Self-Hosted

Serve the `build/html` directory with any web server:

```bash
# Python simple server
cd build/html
python -m http.server 8000
```

## 📊 Documentation Stats

- **Total Pages:** 13
- **API Endpoints Documented:** 30+
- **Code Examples:** 100+
- **Tables:** 50+
- **Diagrams:** 5+
- **Word Count:** ~25,000 words

## 🔗 Live Documentation

- **Full Documentation**: https://alx-project-nexus.readthedocs.io/
- **Swagger UI**: https://modestwear.onrender.com/docs/
- **ReDoc**: https://modestwear.onrender.com/redoc/
- **API Base**: https://modestwear.onrender.com
- **Frontend**: https://modestwear-app.vercel.app

## 🤝 Contributing

1. Edit `.md` files in `source/` directory
2. Build locally to preview: `make html`
3. Submit pull request

## 📄 License

Proprietary - All rights reserved

---

**Built with ❤️ using Sphinx + MyST Parser**
