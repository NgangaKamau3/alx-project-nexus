# Testing Guide

Comprehensive guide to testing the ModestWear API.

## Overview

ModestWear uses a multi-layered testing approach:
- **Unit Tests:** Test individual functions and methods
- **Integration Tests:** Test API endpoints and workflows
- **Manual Testing:** Interactive testing via Swagger/ReDoc
- **Load Testing:** Performance and scalability testing

---

## Running Tests

### All Tests

```bash
cd modestwear
python manage.py test
```

### Specific App

```bash
python manage.py test apps.users
python manage.py test apps.catalog
python manage.py test apps.orders
python manage.py test apps.outfits
```

### Specific Test Class

```bash
python manage.py test apps.users.tests.test_auth.AuthenticationTestCase
```

### Specific Test Method

```bash
python manage.py test apps.users.tests.test_auth.AuthenticationTestCase.test_user_registration
```

### With Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# View report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

---

## Test Structure

### Directory Layout

```
modestwear/
├── apps/
│   ├── users/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_verification.py
│   │   │   └── test_social_auth.py
│   ├── catalog/
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_filters.py
│   ├── orders/
│   │   ├── tests/
│   │   │   ├── test_cart.py
│   │   │   ├── test_orders.py
│   │   │   └── test_wishlist.py
│   └── outfits/
│       ├── tests/
│       │   ├── test_models.py
│       │   └── test_views.py
```

---

## Unit Tests

### Model Tests

```python
from django.test import TestCase
from apps.users.models import User

class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            username='testuser'
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('TestPass123!'))
        self.assertFalse(self.user.is_verified)
    
    def test_user_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.user), 'test@example.com')
    
    def test_email_uniqueness(self):
        """Test email must be unique"""
        with self.assertRaises(Exception):
            User.objects.create_user(
                email='test@example.com',
                password='AnotherPass123!',
                username='testuser2'
            )
```

### Serializer Tests

```python
from django.test import TestCase
from apps.catalog.models import Product, Category
from apps.catalog.serializers import ProductSerializer

class ProductSerializerTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Dresses',
            slug='dresses'
        )
        self.product_data = {
            'name': 'Test Dress',
            'slug': 'test-dress',
            'category': self.category.id,
            'base_price': '1299.99',
            'description': 'Test description'
        }
    
    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        serializer = ProductSerializer(data=self.product_data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_with_invalid_price(self):
        """Test serializer rejects negative price"""
        self.product_data['base_price'] = '-100.00'
        serializer = ProductSerializer(data=self.product_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('base_price', serializer.errors)
```

---

## Integration Tests

### API Endpoint Tests

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.users.models import User

class AuthenticationAPITestCase(APITestCase):
    def setUp(self):
        self.register_url = reverse('user-register')
        self.login_url = reverse('user-login')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'full_name': 'Test User'
        }
    
    def test_user_registration(self):
        """Test user can register"""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('tokens', response.data['data'])
        self.assertIn('user', response.data['data'])
    
    def test_user_login(self):
        """Test user can login"""
        # Create user first
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            username='testuser'
        )
        
        # Attempt login
        response = self.client.post(
            self.login_url,
            {
                'email': self.user_data['email'],
                'password': self.user_data['password']
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data['data'])
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with wrong password"""
        User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            username='testuser'
        )
        
        response = self.client.post(
            self.login_url,
            {
                'email': self.user_data['email'],
                'password': 'WrongPassword123!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
```

### Authenticated Endpoint Tests

```python
class CartAPITestCase(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!',
            username='testuser'
        )
        
        # Get tokens
        response = self.client.post(
            reverse('user-login'),
            {'email': 'test@example.com', 'password': 'TestPass123!'},
            format='json'
        )
        self.access_token = response.data['data']['tokens']['access_token']
        
        # Set authentication
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        # Create test product
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            base_price='999.99'
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001',
            size=2,  # M
            color='Black',
            stock_available=10
        )
    
    def test_add_to_cart(self):
        """Test adding item to cart"""
        response = self.client.post(
            reverse('cart-add'),
            {'variant_id': self.variant.id, 'quantity': 2},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    def test_view_cart(self):
        """Test viewing cart contents"""
        # Add item first
        CartItem.objects.create(
            user=self.user,
            variant=self.variant,
            quantity=2
        )
        
        response = self.client.get(reverse('cart-view'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['summary']['total_items'], 2)
```

---

## Workflow Tests

### Complete E-Commerce Flow

```python
class ECommerceWorkflowTestCase(APITestCase):
    def test_complete_purchase_flow(self):
        """Test complete flow: register → browse → cart → order"""
        
        # 1. Register user
        register_response = self.client.post(
            reverse('user-register'),
            {
                'email': 'customer@example.com',
                'password': 'SecurePass123!',
                'full_name': 'Test Customer'
            },
            format='json'
        )
        self.assertEqual(register_response.status_code, 201)
        access_token = register_response.data['data']['tokens']['access_token']
        
        # 2. Browse products
        products_response = self.client.get(reverse('product-list'))
        self.assertEqual(products_response.status_code, 200)
        
        # 3. Add to cart
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        cart_response = self.client.post(
            reverse('cart-add'),
            {'variant_id': 1, 'quantity': 2},
            format='json'
        )
        self.assertEqual(cart_response.status_code, 201)
        
        # 4. Create order
        order_response = self.client.post(
            reverse('order-create'),
            {
                'address': '123 Test St, Cape Town, South Africa',
                'payment_method': 'stripe'
            },
            format='json'
        )
        self.assertEqual(order_response.status_code, 201)
        self.assertIn('order_id', order_response.data['data'])
```

---

## Manual Testing

### Using Swagger UI

1. **Navigate to:** https://modestwear.onrender.com/docs/
2. **Test Authentication:**
   - Click on `/api/users/register/`
   - Click "Try it out"
   - Enter test data
   - Click "Execute"
   - Copy access token from response

3. **Authorize:**
   - Click "Authorize" button at top
   - Enter: `Bearer <your_access_token>`
   - Click "Authorize"

4. **Test Endpoints:**
   - All authenticated endpoints now work
   - Try adding to cart, creating orders, etc.

### Using cURL

```bash
# Register
curl -X POST https://modestwear.onrender.com/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST https://modestwear.onrender.com/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'

# Save token
TOKEN="<access_token_from_login>"

# Browse products
curl https://modestwear.onrender.com/api/catalog/products/

# Add to cart (authenticated)
curl -X POST https://modestwear.onrender.com/api/orders/cart/add/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_id": 1,
    "quantity": 2
  }'
```

### Using Postman

1. **Import Collection:**
   - Create new collection "ModestWear API"
   - Add base URL variable: `{{base_url}}` = `https://modestwear.onrender.com`

2. **Setup Authentication:**
   - Create "Register" request
   - Create "Login" request
   - Add test script to save token:
   ```javascript
   pm.test("Login successful", function () {
       var jsonData = pm.response.json();
       pm.environment.set("access_token", jsonData.data.tokens.access_token);
   });
   ```

3. **Use Token:**
   - In collection settings, add Authorization
   - Type: Bearer Token
   - Token: `{{access_token}}`

---

## Load Testing

### Using Locust

**Install:**
```bash
pip install locust
```

**Create locustfile.py:**
```python
from locust import HttpUser, task, between

class ModestWearUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get token"""
        response = self.client.post("/api/users/login/", json={
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        self.token = response.json()['data']['tokens']['access_token']
        self.client.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
    
    @task(3)
    def browse_products(self):
        """Browse products (most common action)"""
        self.client.get("/api/catalog/products/")
    
    @task(2)
    def view_product(self):
        """View product details"""
        self.client.get("/api/catalog/products/1/")
    
    @task(1)
    def view_cart(self):
        """View cart"""
        self.client.get("/api/orders/cart/")
    
    @task(1)
    def add_to_cart(self):
        """Add item to cart"""
        self.client.post("/api/orders/cart/add/", json={
            "variant_id": 1,
            "quantity": 1
        })
```

**Run Load Test:**
```bash
locust -f locustfile.py --host=https://modestwear.onrender.com
```

**Access UI:** http://localhost:8089

**Test Scenarios:**
- **Light Load:** 10 users, 1 user/second spawn rate
- **Medium Load:** 50 users, 5 users/second spawn rate
- **Heavy Load:** 100 users, 10 users/second spawn rate

---

## Test Data

### Fixtures

**Create fixture:**
```bash
python manage.py dumpdata catalog.Category catalog.Product > fixtures/products.json
```

**Load fixture:**
```bash
python manage.py loaddata fixtures/products.json
```

### Factory Pattern

```python
import factory
from apps.users.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_verified = True

# Usage in tests
user = UserFactory.create()
users = UserFactory.create_batch(10)
```

---

## Continuous Integration

### GitHub Actions

**.github/workflows/tests.yml:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        SECRET_KEY: test-secret-key
      run: |
        python modestwear/manage.py test
    
    - name: Upload coverage
      run: |
        coverage run --source='.' modestwear/manage.py test
        coverage report
```

---

## Test Coverage Goals

### Target Coverage

- **Overall:** 80%+
- **Models:** 90%+
- **Views/APIs:** 85%+
- **Serializers:** 80%+
- **Utilities:** 75%+

### Check Coverage

```bash
coverage report --fail-under=80
```

---

## Best Practices

1. **Test Isolation:** Each test should be independent
2. **Clear Names:** Test names describe what they test
3. **Arrange-Act-Assert:** Structure tests clearly
4. **Mock External Services:** Don't call real APIs in tests
5. **Test Edge Cases:** Not just happy paths
6. **Fast Tests:** Keep tests fast (< 1 second each)
7. **Continuous Testing:** Run tests on every commit

---

## Next Steps

- Review [API Documentation](../api/authentication.md)
- Learn about [Deployment](../architecture/deployment.md)
- Explore [Security](../architecture/security.md)
