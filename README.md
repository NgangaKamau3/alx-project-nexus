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
    %% Styling for the 'Elegant' Boxes
    classDef box fill:none,stroke:#fff,stroke-width:1px,color:#fff;
    classDef dashed stroke-dasharray: 5 5;

    subgraph Client ["CLIENT (Next.js / Tailwind CSS)"]
        direction LR
        UI1[Product Discovery] --- UI2[Outfit Builder] --- UI3[Virtual Try-On]
    end

    %% API Layer based on Django REST Framework
    subgraph Django ["DJANGO API SERVER (DRF)"]
        direction TB
        subgraph Views ["Views / Serializers"]
            V1[CatalogView: Search & Filters]
            V2[OrderView: Cart & Stripe SDK]
            V3[OutfitView: Mix & Match Logic]
            V4[TryOnView: AI Image Processing]
        end
    end

    %% Data & Task Layer
    subgraph Storage ["PostgreSQL & Task Layer"]
        DB[(PostgreSQL)]
        Redis((Redis Broker))
    end

    Worker[Celery Worker]

    %% Connections and Data Flow
    Client ==>|JWT Auth / HTTP| Django
    V1 & V2 & V3 -->|Save/Query| DB
    V4 -->|Queue Task| Redis
    Redis -.->|Async| Worker
    Worker -->|Store Media| S3[AWS S3 / Storage]

    %% Apply Style Classes
    class Client,Django,Views,Storage,Worker box;
```
