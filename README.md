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

### System architecture
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
