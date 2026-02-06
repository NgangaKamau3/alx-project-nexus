import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.catalog.models import Category, Product, ProductVariant, CoverageLevel
from apps.orders.models import Order, OrderItem
from apps.outfits.models import Outfit, OutfitItem

User = get_user_model()

@pytest.mark.django_db
class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name="Dresses",
            slug="dresses"
        )
        self.coverage = CoverageLevel.objects.create(
            name="Full Coverage",
            description="Complete coverage"
        )
        self.product = Product.objects.create(
            name="Test Dress",
            slug="test-dress",
            category=self.category,
            base_price=Decimal('99.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001',
            size=12,
            color='Blue',
            coverage=self.coverage,
            stock_available=10
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Dresses")
        self.assertEqual(self.category.slug, "dresses")
        self.assertTrue(self.category.is_active)
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Dress")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.base_price, Decimal('99.99'))
    
    def test_product_variant_creation(self):
        self.assertEqual(self.variant.product, self.product)
        self.assertEqual(self.variant.sku, 'TEST-001')
        self.assertEqual(self.variant.size, 12)
        self.assertEqual(self.variant.color, 'Blue')
        self.assertEqual(self.variant.stock_available, 10)
    
    def test_order_creation(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('199.98'),
            status='pending',
            address='123 Test St'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total_price, Decimal('199.98'))
    
    def test_order_item_creation(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('99.99'),
            status='pending',
            address='123 Test St'
        )
        order_item = OrderItem.objects.create(
            order=order,
            variant=self.variant,
            quantity=1,
            price_at_purchase=Decimal('99.99')
        )
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.variant, self.variant)
        self.assertEqual(order_item.quantity, 1)
    
    def test_outfit_creation(self):
        outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit',
            description='A test outfit',
            is_public=True
        )
        self.assertEqual(outfit.user, self.user)
        self.assertEqual(outfit.name, 'Test Outfit')
        self.assertTrue(outfit.is_public)
    
    def test_outfit_item_creation(self):
        outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit'
        )
        outfit_item = OutfitItem.objects.create(
            outfit=outfit,
            product=self.product
        )
        self.assertEqual(outfit_item.outfit, outfit)
        self.assertEqual(outfit_item.product, self.product)
    
    def test_user_creation(self):
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password('newpass123'))
    
    def test_model_relationships(self):
        # Test category -> products relationship
        self.assertEqual(self.category.products.count(), 1)
        self.assertEqual(self.category.products.first(), self.product)
        
        # Test product -> variants relationship
        self.assertEqual(self.product.variants.count(), 1)
        self.assertEqual(self.product.variants.first(), self.variant)
        
        # Test order workflow
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('99.99'),
            status='pending',
            address='123 Test St'
        )
        OrderItem.objects.create(
            order=order,
            variant=self.variant,
            quantity=1,
            price_at_purchase=Decimal('99.99')
        )
        self.assertEqual(order.items.count(), 1)
        
        # Test outfit workflow
        outfit = Outfit.objects.create(
            user=self.user,
            name='Complete Outfit'
        )
        OutfitItem.objects.create(
            outfit=outfit,
            product=self.product
        )
        self.assertEqual(outfit.items.count(), 1)

@pytest.mark.django_db
class IntegrationTests(TestCase):
    def test_complete_ecommerce_workflow(self):
        # Create user
        user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='customerpass123'
        )
        
        # Create category and product
        category = Category.objects.create(name="Abayas", slug="abayas")
        coverage = CoverageLevel.objects.create(name="Full", description="Full coverage")
        product = Product.objects.create(
            name="Black Abaya",
            slug="black-abaya",
            category=category,
            base_price=Decimal('149.99')
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku='ABAYA-001',
            size=14,
            color='Black',
            coverage=coverage,
            stock_available=5
        )
        
        # Create order
        order = Order.objects.create(
            user=user,
            total_price=Decimal('149.99'),
            status='pending',
            address='456 Customer St'
        )
        OrderItem.objects.create(
            order=order,
            variant=variant,
            quantity=1,
            price_at_purchase=Decimal('149.99')
        )
        
        # Create outfit
        outfit = Outfit.objects.create(
            user=user,
            name='Elegant Evening',
            is_public=True
        )
        OutfitItem.objects.create(
            outfit=outfit,
            product=product
        )
        
        # Verify everything is connected
        self.assertEqual(user.order_set.count(), 1)
        self.assertEqual(user.outfits.count(), 1)
        self.assertEqual(category.products.count(), 1)
        self.assertEqual(product.variants.count(), 1)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(outfit.items.count(), 1)