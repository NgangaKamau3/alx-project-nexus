import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from apps.catalog.models import Category, Product, ProductVariant
from apps.catalog.serializers import ProductSerializer

User = get_user_model()

@pytest.mark.django_db
class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Dresses",
            slug="dresses",
            description="Elegant modest dresses"
        )
        self.product = Product.objects.create(
            name="Elegant Dress",
            slug="elegant-dress",
            description="Beautiful modest dress",
            category=self.category,
            base_price=Decimal('99.99'),
            is_active=True
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Elegant Dress")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.base_price, Decimal('99.99'))
        self.assertTrue(self.product.is_active)
    
    def test_product_str_method(self):
        self.assertEqual(str(self.product), "Elegant Dress")

@pytest.mark.django_db
class CategoryModelTests(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            description="Test description"
        )
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.slug, "test-category")
    
    def test_category_str_method(self):
        category = Category.objects.create(name="Test Category", slug="test")
        self.assertEqual(str(category), "Test Category")

@pytest.mark.django_db
class ProductVariantModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Dresses", slug="dresses")
        self.product = Product.objects.create(
            name="Test Dress",
            slug="test-dress",
            category=self.category,
            base_price=Decimal('99.99')
        )
    
    def test_variant_creation(self):
        variant = ProductVariant.objects.create(
            product=self.product,
            size='M',
            color='Blue',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.assertEqual(variant.product, self.product)
        self.assertEqual(variant.size, 'M')
        self.assertEqual(variant.color, 'Blue')
        self.assertEqual(variant.stock_quantity, 10)

class ProductSerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test", slug="test")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            description="Test description",
            category=self.category,
            base_price=Decimal('99.99')
        )
    
    def test_product_serializer_read(self):
        serializer = ProductSerializer(self.product)
        self.assertEqual(serializer.data['name'], 'Test Product')
        self.assertEqual(serializer.data['base_price'], '99.99')
        self.assertIn('category', serializer.data)
    
    def test_product_serializer_create(self):
        data = {
            'name': 'New Product',
            'description': 'New description',
            'category': self.category.pk,
            'base_price': '79.99'
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())

@pytest.mark.django_db
class CatalogIntegrationTests(TestCase):
    def setUp(self):
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
    
    def test_product_with_variants(self):
        self.assertEqual(self.product.variants.count(), 1)
        variant = self.product.variants.first()
        self.assertEqual(variant.size, 'M')
        self.assertEqual(variant.color, 'Blue')
    
    def test_category_with_products(self):
        self.assertEqual(self.category.products.count(), 1)
        product = self.category.products.first()
        self.assertEqual(product.name, "Test Dress")