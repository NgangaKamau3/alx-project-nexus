import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from apps.catalog.models import Category, Product, ProductVariant
from apps.orders.models import Order, OrderItem
from apps.outfits.models import Outfit
from core.admin import ModestWearAdminSite
from apps.catalog.admin import ProductAdmin, CategoryAdmin
from apps.orders.admin import OrderAdmin
from apps.users.admin import UserAdmin

User = get_user_model()

@pytest.mark.django_db
class AdminSiteTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.site = ModestWearAdminSite()
    
    def test_admin_site_configuration(self):
        self.assertEqual(self.site.site_header, 'ModestWear Administration')
        self.assertEqual(self.site.site_title, 'ModestWear Admin')
        self.assertEqual(self.site.index_title, 'ModestWear Dashboard')
    
    def test_admin_login_required(self):
        self.client.logout()
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_dashboard_access(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ModestWear Dashboard')

@pytest.mark.django_db
class CustomAdminDashboardTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.dashboard = ModestWearAdminSite()
        
        # Create test data
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
            stock_quantity=5  # Low stock
        )
    
    def test_get_total_users(self):
        total_users = self.dashboard.get_total_users()
        self.assertEqual(total_users, 2)  # admin + regular user
    
    def test_get_total_products(self):
        total_products = self.dashboard.get_total_products()
        self.assertEqual(total_products, 1)
    
    def test_get_total_orders(self):
        Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('99.99'),
            status='completed'
        )
        total_orders = self.dashboard.get_total_orders()
        self.assertEqual(total_orders, 1)
    
    def test_get_total_revenue(self):
        Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('99.99'),
            status='completed'
        )
        Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('149.99'),
            status='completed'
        )
        total_revenue = self.dashboard.get_total_revenue()
        self.assertEqual(total_revenue, Decimal('249.98'))
    
    def test_get_recent_orders(self):
        order1 = Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('99.99'),
            status='pending'
        )
        order2 = Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('149.99'),
            status='completed'
        )
        recent_orders = self.dashboard.get_recent_orders()
        self.assertEqual(len(recent_orders), 2)
        self.assertEqual(recent_orders[0], order2)  # Most recent first
    
    def test_get_low_stock_products(self):
        # Create another product with normal stock
        normal_product = Product.objects.create(
            name="Normal Stock Dress",
            slug="normal-dress",
            category=self.category,
            base_price=Decimal('79.99')
        )
        ProductVariant.objects.create(
            product=normal_product,
            size='M',
            color='Red',
            price=Decimal('79.99'),
            stock_quantity=20
        )
        
        low_stock_products = self.dashboard.get_low_stock_products()
        self.assertEqual(len(low_stock_products), 1)
        self.assertEqual(low_stock_products[0], self.variant)
    
    def test_get_popular_products(self):
        # Create orders with items to test popularity
        order = Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('99.99'),
            status='completed'
        )
        OrderItem.objects.create(
            order=order,
            product_variant=self.variant,
            quantity=2,
            price=Decimal('99.99')
        )
        
        popular_products = self.dashboard.get_popular_products()
        self.assertGreaterEqual(len(popular_products), 0)

@pytest.mark.django_db
class ProductAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.site = AdminSite()
        self.admin = ProductAdmin(Product, self.site)
        self.category = Category.objects.create(name="Dresses", slug="dresses")
    
    def test_product_admin_list_display(self):
        expected_fields = ['name', 'category', 'base_price', 'is_active', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_product_admin_list_filter(self):
        expected_filters = ['category', 'is_active', 'created_at']
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_product_admin_search_fields(self):
        expected_fields = ['name', 'description', 'category__name']
        self.assertEqual(list(self.admin.search_fields), expected_fields)
    
    def test_product_creation_via_admin(self):
        url = reverse('admin:catalog_product_add')
        data = {
            'name': 'Admin Test Dress',
            'slug': 'admin-test-dress',
            'description': 'Created via admin',
            'category': self.category.pk,
            'base_price': '129.99',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Product.objects.filter(name='Admin Test Dress').exists())

@pytest.mark.django_db
class CategoryAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.site = AdminSite()
        self.admin = CategoryAdmin(Category, self.site)
    
    def test_category_admin_list_display(self):
        expected_fields = ['name', 'slug', 'parent', 'is_active']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_category_admin_prepopulated_fields(self):
        expected = {'slug': ('name',)}
        self.assertEqual(self.admin.prepopulated_fields, expected)
    
    def test_category_creation_via_admin(self):
        url = reverse('admin:catalog_category_add')
        data = {
            'name': 'Admin Test Category',
            'slug': 'admin-test-category',
            'description': 'Created via admin',
            'is_active': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='Admin Test Category').exists())

@pytest.mark.django_db
class OrderAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.site = AdminSite()
        self.admin = OrderAdmin(Order, self.site)
        
        self.order = Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('99.99'),
            status='pending'
        )
    
    def test_order_admin_list_display(self):
        expected_fields = ['order_number', 'user', 'status', 'total_amount', 'created_at']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_order_admin_list_filter(self):
        expected_filters = ['status', 'created_at', 'updated_at']
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_order_admin_readonly_fields(self):
        expected_fields = ['order_number', 'created_at', 'updated_at']
        self.assertEqual(list(self.admin.readonly_fields), expected_fields)
    
    def test_order_status_update_via_admin(self):
        url = reverse('admin:orders_order_change', args=[self.order.pk])
        data = {
            'user': self.regular_user.pk,
            'status': 'confirmed',
            'total_amount': '99.99',
            'shipping_address': '123 Test St',
            'payment_method': 'card'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')

@pytest.mark.django_db
class UserAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        self.site = AdminSite()
        self.admin = UserAdmin(User, self.site)
    
    def test_user_admin_list_display(self):
        expected_fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        self.assertEqual(list(self.admin.list_display), expected_fields)
    
    def test_user_admin_list_filter(self):
        expected_filters = ['is_active', 'is_staff', 'date_joined']
        self.assertEqual(list(self.admin.list_filter), expected_filters)
    
    def test_user_admin_search_fields(self):
        expected_fields = ['username', 'email', 'first_name', 'last_name']
        self.assertEqual(list(self.admin.search_fields), expected_fields)

@pytest.mark.django_db
class AdminBulkActionsTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        
        # Create test data
        self.category = Category.objects.create(name="Dresses", slug="dresses")
        self.product1 = Product.objects.create(
            name="Dress 1",
            slug="dress-1",
            category=self.category,
            base_price=Decimal('99.99'),
            is_active=True
        )
        self.product2 = Product.objects.create(
            name="Dress 2",
            slug="dress-2",
            category=self.category,
            base_price=Decimal('79.99'),
            is_active=True
        )
    
    def test_bulk_deactivate_products(self):
        url = reverse('admin:catalog_product_changelist')
        data = {
            'action': 'make_inactive',
            '_selected_action': [self.product1.pk, self.product2.pk]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        # Verify products were deactivated
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.assertFalse(self.product1.is_active)
        self.assertFalse(self.product2.is_active)

@pytest.mark.django_db
class AdminDashboardViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        self.client = Client()
        self.client.force_login(self.admin_user)
        
        # Create test data for dashboard
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
            stock_quantity=3  # Low stock
        )
        self.order = Order.objects.create(
            user=self.regular_user,
            total_amount=Decimal('99.99'),
            status='completed'
        )
        self.outfit = Outfit.objects.create(
            user=self.regular_user,
            name='Test Outfit',
            is_public=True
        )
    
    def test_dashboard_statistics_display(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Check that statistics are displayed
        self.assertContains(response, 'Total Users')
        self.assertContains(response, 'Total Products')
        self.assertContains(response, 'Total Orders')
        self.assertContains(response, 'Total Revenue')
        
        # Check actual values
        self.assertContains(response, '2')  # Total users (admin + regular)
        self.assertContains(response, '1')  # Total products
        self.assertContains(response, '1')  # Total orders
    
    def test_dashboard_recent_activity(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Check recent activity sections
        self.assertContains(response, 'Recent Orders')
        self.assertContains(response, 'Low Stock Alert')
        self.assertContains(response, 'Popular Products')
    
    def test_dashboard_low_stock_alert(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Should show low stock product
        self.assertContains(response, 'Test Dress')
        self.assertContains(response, '3 left')  # Stock quantity
    
    def test_dashboard_non_admin_access_denied(self):
        self.client.logout()
        self.client.force_login(self.regular_user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

@pytest.mark.django_db
class AdminSecurityTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
    
    def test_admin_access_superuser(self):
        self.client.force_login(self.admin_user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_access_staff_user(self):
        self.client.force_login(self.staff_user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_access_regular_user_denied(self):
        self.client.force_login(self.regular_user)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_admin_access_anonymous_user_denied(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login