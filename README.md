# Modest Wear.
ModestWear is a mobile-first fashion e-commerce website offering elegant and modest
women’s clothing.

## Project Goals
CRUD APIs: Build APIs for managing products, categories, and user authentication.<br>
Filtering, Sorting, Pagination: Implement robust logic for efficient product discovery.<br>
Database Optimization: Design a high-performance database schema to support seamless queries.

## Technologies Used
Django: For building a scalable backend framework.<br>
PostgreSQL: As the relational database for optimized performance.<br>
JWT: For secure user authentication.<br>
Swagger/OpenAPI: To document and test APIs.

## System architecture
```mermaid
graph TB
    %% Styling for Elegance
    classDef box fill:none,stroke:#fff,stroke-width:1px,color:#fff;
    classDef storage fill:#1a1a1a,stroke:#fff,stroke-width:1px,color:#ccc;

    subgraph Client ["Frontend (Next.js + Tailwind)"]
        UI[ModestWear Web App]
        OB[Outfit Builder UI]
    end

    subgraph Server ["Backend (Django REST Framework)"]
        direction TB
        Auth[SimpleJWT Auth]
        Catalog[Product Catalog API]
        OutfitEngine[Outfit Recommendation Logic]
        Orders[Order & Cart Service]
    end

    subgraph PersistentStorage ["Data & Media (Free Tier)"]
        DB[(PostgreSQL + pgvector)]
        Cloudinary[Cloudinary: Media Hosting]
    end

    %% Flow Connections
    UI ==>|JWT Auth| Auth
    UI --> Catalog
    UI --> OB
    OB --> OutfitEngine
    
    Catalog --> DB
    OutfitEngine -->|Similarity Search| DB
    Orders -->|Payments| Stripe[Stripe / Paystack]
    
    %% Media Connections
    Catalog -.->|Fetch URL| Cloudinary

    %% Apply Style Classes
    class Client,Server box;
    class PersistentStorage storage;
```
## Project structure

```
modestwear/
├── core/                       # Project root 
│   ├── settings.py             # Base, Dev, and Production settings
│   ├── urls.py                 # Root URL config (includes all app URLs)
│   ├── wsgi.py / asgi.py       # Deployment entry points
├── apps/                       # Subdirectory for all business logic
│   ├── users/                  # Custom User model, Profiles, JWT logic
│   │   ├── api/                # API layer for this app
│   │   │   ├── serializers.py
│   │   │   └── views.py
│   │   ├── models.py
│   │   └── urls.py
│   ├── catalog/                # Product Discovery, Filters, Search
│   │   ├── api/
│   │   │   ├── serializers.py
│   │   │   └── views.py
│   │   ├── models.py
│   │   └── services.py         # Business logic (e.g., complex search)
│   ├── orders/                 # Cart, Checkout, Stripe Webhooks
│   ├── outfits/                # Outfit Builder & pgvector logic
├── static/                     # Collected static files (for Swagger/Admin)
├── tests/                      # Global integration tests
├── .env                        # Environment variables (DB_URL, SECRET_KEY)
├── docker-compose.yml          # Setup for Local Postgres & Redis
├── requirements.txt            # Dependencies (DRF, Simple-JWT, pgvector)
└── manage.py
```

git filter-branch -f --env-filter '
OLD_EMAIL=""
CORRECT_NAME="NgangaKamau3"
CORRECT_EMAIL="your-verified-github-email@example.com"
if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags