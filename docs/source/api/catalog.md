# Catalog API

Product discovery and filtering endpoints.

## List Products

Get paginated list of products with advanced filtering.

**Endpoint:** `GET /api/catalog/products/`

**Authentication:** Not required

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category slug |
| `coverage_level` | string | Filter by modesty level: `full`, `moderate`, `light` |
| `min_price` | decimal | Minimum price filter |
| `max_price` | decimal | Maximum price filter |
| `search` | string | Full-text search in name/description |
| `ordering` | string | Sort by: `price`, `-price`, `date_added`, `-date_added` |
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Items per page (default: 20, max: 100) |

### Example Request

```bash
curl "https://modestwear.onrender.com/api/catalog/products/?coverage_level=full&category=dresses&min_price=500&max_price=2000&ordering=-date_added&page=1&page_size=10"
```

### Example Response

```json
{
  "count": 45,
  "next": "https://modestwear.onrender.com/api/catalog/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Elegant Maxi Dress",
      "slug": "elegant-maxi-dress",
      "description": "Beautiful flowing maxi dress with full coverage",
      "base_price": "1299.99",
      "category": {
        "id": 2,
        "name": "Dresses",
        "slug": "dresses"
      },
      "coverage_level": {
        "id": 1,
        "name": "Full Coverage",
        "description": "Maximum modesty"
      },
      "is_featured": true,
      "date_added": "2024-01-15T10:30:00Z",
      "images": [
        {
          "id": 1,
          "image": "https://res.cloudinary.com/.../dress1.jpg",
          "thumbnail": "https://res.cloudinary.com/.../dress1_thumb.jpg",
          "is_feature": true
        }
      ],
      "variants": [
        {
          "id": 5,
          "sku": "DRESS-001-M-BLK",
          "size": "M",
          "color": "Black",
          "stock_available": 15,
          "is_active": true
        }
      ]
    }
  ]
}
```

## Get Product Details

Retrieve detailed information about a specific product.

**Endpoint:** `GET /api/catalog/products/{id}/`

**Authentication:** Not required

### Example Request

```bash
curl https://modestwear.onrender.com/api/catalog/products/1/
```

### Example Response

```json
{
  "id": 1,
  "name": "Elegant Maxi Dress",
  "slug": "elegant-maxi-dress",
  "description": "Beautiful flowing maxi dress perfect for formal occasions...",
  "base_price": "1299.99",
  "category": {
    "id": 2,
    "name": "Dresses",
    "slug": "dresses",
    "parent": {
      "id": 1,
      "name": "Clothing",
      "slug": "clothing"
    }
  },
  "coverage_level": {
    "id": 1,
    "name": "Full Coverage",
    "description": "Maximum modesty with long sleeves and floor length"
  },
  "is_featured": true,
  "date_added": "2024-01-15T10:30:00Z",
  "images": [
    {
      "id": 1,
      "image": "https://res.cloudinary.com/.../dress1.jpg",
      "thumbnail": "https://res.cloudinary.com/.../dress1_thumb.jpg",
      "is_feature": true
    },
    {
      "id": 2,
      "image": "https://res.cloudinary.com/.../dress1_back.jpg",
      "thumbnail": "https://res.cloudinary.com/.../dress1_back_thumb.jpg",
      "is_feature": false
    }
  ],
  "variants": [
    {
      "id": 5,
      "sku": "DRESS-001-M-BLK",
      "size": "M",
      "color": "Black",
      "stock_available": 15,
      "is_active": true
    },
    {
      "id": 6,
      "sku": "DRESS-001-L-BLK",
      "size": "L",
      "color": "Black",
      "stock_available": 8,
      "is_active": true
    }
  ]
}
```

## List Categories

Get all product categories with hierarchy.

**Endpoint:** `GET /api/catalog/categories/`

**Authentication:** Not required

### Example Request

```bash
curl https://modestwear.onrender.com/api/catalog/categories/
```

### Example Response

```json
[
  {
    "id": 1,
    "name": "Clothing",
    "slug": "clothing",
    "parent": null,
    "is_active": true,
    "children": [
      {
        "id": 2,
        "name": "Dresses",
        "slug": "dresses",
        "parent": 1
      },
      {
        "id": 3,
        "name": "Abayas",
        "slug": "abayas",
        "parent": 1
      }
    ]
  },
  {
    "id": 10,
    "name": "Accessories",
    "slug": "accessories",
    "parent": null,
    "is_active": true
  }
]
```

## Get Available Filters

Get all available filter options for products.

**Endpoint:** `GET /api/catalog/filters/`

**Authentication:** Not required

### Example Request

```bash
curl https://modestwear.onrender.com/api/catalog/filters/
```

### Example Response

```json
{
  "categories": [
    {"id": 1, "name": "Clothing", "slug": "clothing"},
    {"id": 2, "name": "Dresses", "slug": "dresses"},
    {"id": 3, "name": "Abayas", "slug": "abayas"}
  ],
  "coverage_levels": [
    {"id": 1, "name": "Full Coverage", "description": "Maximum modesty"},
    {"id": 2, "name": "Moderate Coverage", "description": "Balanced coverage"},
    {"id": 3, "name": "Light Coverage", "description": "Minimal coverage"}
  ],
  "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
  "colors": ["Black", "Navy", "Beige", "White", "Grey"],
  "price_range": {
    "min": 299.99,
    "max": 4999.99
  }
}
```

## Coverage Levels

ModestWear's unique feature for filtering by modesty level:

| Level | Description | Typical Features |
|-------|-------------|------------------|
| **Full Coverage** | Maximum modesty | Long sleeves, floor length, high neckline |
| **Moderate Coverage** | Balanced coverage | 3/4 sleeves, midi length, modest neckline |
| **Light Coverage** | Minimal coverage | Short sleeves, knee length, standard neckline |

## Size Chart

| Size | US | UK | EU | Bust (cm) | Waist (cm) | Hips (cm) |
|------|----|----|----| ----------|------------|-----------|
| XS | 0-2 | 4-6 | 32-34 | 78-82 | 60-64 | 86-90 |
| S | 4-6 | 8-10 | 36-38 | 82-86 | 64-68 | 90-94 |
| M | 8-10 | 12-14 | 40-42 | 86-90 | 68-72 | 94-98 |
| L | 12-14 | 16-18 | 44-46 | 90-96 | 72-78 | 98-104 |
| XL | 16-18 | 20-22 | 48-50 | 96-102 | 78-84 | 104-110 |
| XXL | 20-22 | 24-26 | 52-54 | 102-110 | 84-92 | 110-118 |

## Error Responses

### Product Not Found
```json
{
  "detail": "Not found."
}
```
**Status Code:** 404

### Invalid Filter Parameters
```json
{
  "error": "Invalid coverage_level. Must be one of: full, moderate, light"
}
```
**Status Code:** 400

## Best Practices

1. **Use pagination** - Don't request all products at once
2. **Cache filter options** - Categories and coverage levels change rarely
3. **Combine filters** - Use multiple filters for precise results
4. **Handle empty results** - Show helpful message when no products match
5. **Optimize images** - Use thumbnails for list views, full images for details

## Next Steps

- Learn about [Order Management](orders.md)
- Explore [Outfit Builder](outfits.md)
