import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.catalog.models import Category, Product, ProductVariant, CoverageLevel
from apps.orders.models import CartItem, WishList, Order

User = get_user_model()


@pytest.fixture
def api_client():
    """Return API client for testing"""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a test user"""
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='TestPass123!',
        is_verified=True
    )


@pytest.fixture
def unverified_user(db):
    """Create and return an unverified test user"""
    return User.objects.create_user(
        email='unverified@example.com',
        username='unverified',
        password='TestPass123!',
        is_verified=False
    )


@pytest.fixture
def admin_user(db):
    """Create and return an admin user"""
    return User.objects.create_superuser(
        email='admin@example.com',
        username='admin',
        password='AdminPass123!'
    )


@pytest.fixture
def user_tokens(user):
    """Generate JWT tokens for test user"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }


@pytest.fixture
def authenticated_client(api_client, user_tokens):
    """Return authenticated API client"""
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_tokens["access"]}')
    return api_client


@pytest.fixture
def category(db):
    """Create and return a test category"""
    return Category.objects.create(
        name='Dresses',
        slug='dresses',
        is_active=True
    )


@pytest.fixture
def coverage_level(db):
    """Create and return a coverage level"""
    return CoverageLevel.objects.create(
        name='Full Coverage',
        description='Provides full body coverage'
    )


@pytest.fixture
def product(db, category, coverage_level):
    """Create and return a test product"""
    return Product.objects.create(
        category=category,
        name='Elegant Maxi Dress',
        slug='elegant-maxi-dress',
        description='Beautiful modest maxi dress',
        base_price=89.99,
        is_featured=True,
        product_size=coverage_level
    )


@pytest.fixture
def product_variant(db, product, coverage_level):
    """Create and return a product variant"""
    return ProductVariant.objects.create(
        product=product,
        sku='EMD-001-M-NAVY',
        size=10,
        color='Navy Blue',
        coverage=coverage_level,
        stock_available=50,
        is_active=True
    )


@pytest.fixture
def cart_item(db, user, product_variant):
    """Create and return a cart item"""
    return CartItem.objects.create(
        user=user,
        variant=product_variant,
        quantity=2
    )


@pytest.fixture
def wishlist_item(db, user, product_variant):
    """Create and return a wishlist item"""
    return WishList.objects.create(
        user=user,
        variant=product_variant
    )


@pytest.fixture
def order(db, user):
    """Create and return an order"""
    return Order.objects.create(
        user=user,
        status='pending',
        total_price=179.98,
        address='123 Main St, City, State 12345'
    )


@pytest.fixture
def multiple_products(db, category, coverage_level):
    """Create multiple products for testing"""
    products = []
    for i in range(5):
        product = Product.objects.create(
            category=category,
            name=f'Product {i}',
            slug=f'product-{i}',
            description=f'Description for product {i}',
            base_price=50.00 + (i * 10),
            is_featured=(i % 2 == 0),
            product_size=coverage_level
        )
        products.append(product)
    return products
