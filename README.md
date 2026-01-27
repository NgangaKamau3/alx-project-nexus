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
    %% Client Layer
    User((User)) --> WebApp[Next.js Frontend]

    subgraph "Django Backend (DRF)"
        WebApp --> Router[DRF URL Router]
        
        subgraph "Apps / Modules"
            Router --> UsersApp[Users App: JWT Auth / Personalization]
            Router --> CatalogApp[Catalog App: Discovery / Product Pages]
            Router --> OrderApp[Order App: Cart / Checkout / Delivery]
            Router --> FeatureApp[Experimental App: Outfit Builder / Virtual Try-On]
            Router --> AdminApp[Admin App: Custom Management UI]
        end

        %% Middleware & Tools
        UsersApp --> SimpleJWT[Simple JWT Middleware]
        CatalogApp --> Swagger[drf-yasg: OpenAPI Docs]
    end

    subgraph "Data Storage & Services"
        UsersApp & CatalogApp & OrderApp --> Postgres[(PostgreSQL DB)]
        CatalogApp -.-> Redis((Redis Cache))
        FeatureApp --> S3[AWS S3: Media Storage]
    end

    subgraph "External Integrations"
        OrderApp --> Stripe[Stripe / PayFast API]
        FeatureApp --> TryOnAI[AI VTO API / GPU Service]
    end

    %% Infrastructure
    Postgres -.-> Docker[Docker / Compose Environment]
```
