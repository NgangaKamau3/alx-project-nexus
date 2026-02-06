import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.orders.models import WishList, CartItem, Order, OrderItem
from apps.catalog.models import Category, Product, ProductVariant

User = get_user_model()

@pytest.mark.django_db
class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
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
    
    def test_order_str_method(self):
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('99.99'),
            status='pending',
            address='123 Test St'
        )
        self.assertTrue(str(order))  # Just check it doesn't error

@pytest.mark.django_db
class CartItemModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Dresses", slug="dresses")
        self.product = Product.objects.create(
            name="Test Dress",
            slug="test-dress",
            category=self.category,
            base_price=Decimal('99.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            price=Decimal('99.99'),
            stock_quantity=10
        )
    
    def test_cart_item_creation(self):
        cart_item = CartItem.objects.create(
            user=self.user,
            variant=self.variant,
            quantity=2
        )
        self.assertEqual(cart_item.user, self.user)
        self.assertEqual(cart_item.variant, self.variant)
        self.assertEqual(cart_item.quantity, 2)

@pytest.mark.django_db
class OrderItemModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Dresses", slug="dresses")
        self.product = Product.objects.create(
            name="Test Dress",
            slug="test-dress",
            category=self.category,
            base_price=Decimal('99.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('199.98'),
            status='pending',
            address='123 Test St'
        )
    
    def test_order_item_creation(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            variant=self.variant,
            quantity=2,
            price_at_purchase=Decimal('99.99')
        )
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.variant, self.variant)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price_at_purchase, Decimal('99.99'))

@pytest.mark.django_db
class WishListModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Dresses", slug="dresses")
        self.product = Product.objects.create(
            name="Test Dress",
            slug="test-dress",
            category=self.category,
            base_price=Decimal('99.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            price=Decimal('99.99'),
            stock_quantity=10
        )
    
    def test_wishlist_creation(self):
        wishlist_item = WishList.objects.create(
            user=self.user,
            variant=self.variant
        )
        self.assertEqual(wishlist_item.user, self.user)
        self.assertEqual(wishlist_item.variant, self.variant)
    
    def test_wishlist_unique_constraint(self):
        WishList.objects.create(user=self.user, variant=self.variant)
        # Should raise error on duplicate
        with self.assertRaises(Exception):
            WishList.objects.create(user=self.user, variant=self.variant)

@pytest.mark.django_db
class OrderIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Dresses", slug="dresses")
        self.product = Product.objects.create(
            name="Test Dress",
            slug="test-dress",
            category=self.category,
            base_price=Decimal('99.99')
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            price=Decimal('99.99'),
            stock_quantity=10
        )
    
    def test_complete_order_workflow(self):
        # Create order
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('199.98'),
            status='pending',
            address='123 Test St'
        )
        
        # Add items to order
        order_item = OrderItem.objects.create(
            order=order,
            variant=self.variant,
            quantity=2,
            price_at_purchase=Decimal('99.99')
        )
        
        # Verify order has items
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first(), order_item)
        
        # Update order status
        order.status = 'paid'
        order.save()
        self.assertEqual(order.status, 'paid')