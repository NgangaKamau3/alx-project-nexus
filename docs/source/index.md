# ModestWear API Documentation

Welcome to the **ModestWear API** documentation. This REST API powers a mobile-first e-commerce platform for modest fashion, serving women aged 16-50 in the African market.

```{image} https://img.shields.io/badge/Django-4.2-green
:alt: Django Version
```

```{image} https://img.shields.io/badge/DRF-3.14-blue
:alt: Django REST Framework
```

```{image} https://img.shields.io/badge/PostgreSQL-15-blue
:alt: PostgreSQL
```

## Quick Links

- **Live API**: [https://modestwear.onrender.com](https://modestwear.onrender.com)
- **Swagger Docs**: [https://modestwear.onrender.com/docs/](https://modestwear.onrender.com/docs/)
- **Frontend**: [https://modestwear-app.vercel.app](https://modestwear-app.vercel.app)

## Features

- 🔐 **JWT Authentication** with social login (Google/Facebook)
- 🛍️ **Product Catalog** with advanced filtering by coverage level
- 🛒 **Shopping Cart** supporting guest and authenticated users
- 📦 **Order Management** with status tracking
- 💝 **Wishlist** for saved items
- 👗 **Outfit Builder** for personalized recommendations
- 📊 **Admin Dashboard** for inventory and order management

## Technology Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL 15 (Neon serverless)
- **Authentication**: SimpleJWT + OAuth2
- **Media Storage**: Cloudinary
- **Task Queue**: Redis + Celery
- **Deployment**: Render (backend) + Vercel (frontend)

## Table of Contents

```{toctree}
:maxdepth: 2
:caption: Getting Started

guides/quickstart
guides/authentication
guides/installation
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/authentication
api/catalog
api/orders
api/outfits
api/errors
```

```{toctree}
:maxdepth: 2
:caption: Architecture

architecture/database
architecture/deployment
architecture/security
```

```{toctree}
:maxdepth: 1
:caption: Additional Resources

guides/testing
```

## Support

For questions or issues:
- **Email**: support@modestwear.com
- **GitHub**: [Repository Issues](https://github.com/yourusername/modestwear)

## License

This project is proprietary software. All rights reserved.
