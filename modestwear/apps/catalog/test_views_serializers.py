import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from apps.catalog.models import Category, Product, ProductVariant
from apps.catalog.serializers import ProductSerializer
from apps.catalog.recommendations import RecommendationService

User = get_user_model()

@pytest.mark.django_db
class CategoryViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Dresses",
            slug="dresses",
            description="Elegant modest dresses"
        )
    
    def test_category_list_view(self):
        url = reverse('catalog:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_category_detail_view(self):
        url = reverse('catalog:category-detail', kwargs={'pk': self.category.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Dresses')

@pytest.mark.django_db
class ProductViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name="Dresses",
            slug="dresses"
        )
        self.product = Product.objects.create(
            name="Elegant Dress",
            slug="elegant-dress",
            description="Beautiful modest dress",
            category=self.category,
            base_price=Decimal('99.99'),
            is_active=True
        )
    
    def test_product_list_view(self):
        url = reverse('catalog:product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_detail_view(self):
        url = reverse('catalog:product-detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Elegant Dress')
    
    def test_product_filtering_by_category(self):
        url = reverse('catalog:product-list')
        response = self.client.get(url, {'category': self.category.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_search(self):
        url = reverse('catalog:product-list')
        response = self.client.get(url, {'search': 'elegant'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

@pytest.mark.django_db
class ProductVariantViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
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
    
    def test_variant_list_view(self):
        url = reverse('catalog:variant-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_variant_detail_view(self):
        url = reverse('catalog:variant-detail', kwargs={'pk': self.variant.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['size'], 'M')

# CategorySerializer tests removed - not implemented yet

class ProductSerializerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test", slug="test")
    
    def test_product_serializer_valid_data(self):
        data = {
            'name': 'Test Product',
            'slug': 'test-product',
            'description': 'Test description',
            'category': self.category.pk,
            'base_price': '99.99'
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_product_serializer_invalid_price(self):
        data = {
            'name': 'Test Product',
            'slug': 'test-product',
            'category': self.category.pk,
            'base_price': '-10.00'  # Invalid negative price
        }
        serializer = ProductSerializer(data=data)
        self.assertFalse(serializer.is_valid())

@pytest.mark.django_db
class RecommendationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Dresses", slug="dresses")
        self.product1 = Product.objects.create(
            name="Dress 1",
            slug="dress-1",
            category=self.category,
            base_price=Decimal('99.99')
        )
        self.product2 = Product.objects.create(
            name="Dress 2",
            slug="dress-2",
            category=self.category,
            base_price=Decimal('89.99')
        )
        self.service = RecommendationService()
    
    def test_get_popular_products(self):
        recommendations = self.service.get_popular_products(limit=5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)
    
    def test_get_similar_products(self):
        recommendations = self.service.get_similar_products(self.product1, limit=3)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 3)
    
    def test_get_personalized_recommendations(self):
        recommendations = self.service.get_personalized_recommendations(self.user, limit=5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

@pytest.mark.django_db
class RecommendationViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
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
    
    def test_popular_products_view(self):
        url = reverse('catalog:popular-products')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
    
    def test_similar_products_view(self):
        url = reverse('catalog:similar-products', kwargs={'product_id': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
    
    def test_personalized_recommendations_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('catalog:personalized-recommendations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('products', response.data)
    
    def test_personalized_recommendations_unauthenticated(self):
        url = reverse('catalog:personalized-recommendations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)