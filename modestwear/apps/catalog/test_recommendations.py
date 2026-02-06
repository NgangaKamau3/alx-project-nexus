from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.catalog.models import Category, Product
from apps.catalog.recommendations import RecommendationService
from decimal import Decimal

User = get_user_model()

class RecommendationServiceTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Dresses', slug='dresses')
        
        self.product1 = Product.objects.create(
            name='Dress 1', slug='dress-1', category=self.category, base_price=Decimal('50.00')
        )
        self.product2 = Product.objects.create(
            name='Dress 2', slug='dress-2', category=self.category, base_price=Decimal('55.00')
        )
    
    def test_content_based_filtering(self):
        recommendations = RecommendationService._content_based_filtering(self.product1, limit=5)
        # Should return similar products in same category and price range
        self.assertIsInstance(recommendations, list)
        # Product should not recommend itself
        self.assertNotIn(self.product1, recommendations)
    
    def test_popularity_based(self):
        popular = RecommendationService._popularity_based(limit=5)
        self.assertIsInstance(popular, list)
    
    def test_get_recommendations_basic(self):
        recommendations = RecommendationService.get_recommendations(limit=5)
        self.assertIsInstance(recommendations, list)
        self.assertLessEqual(len(recommendations), 5)

class RecommendationAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com', password='TestSecurePass123!'
        )
        self.category = Category.objects.create(name='Dresses', slug='dresses')
        self.product = Product.objects.create(
            name='Test Dress', slug='test-dress', category=self.category, base_price=Decimal('50.00')
        )
    
    def test_user_recommendations_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/catalog/items/recommendations/for-me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
        self.assertEqual(response.data['type'], 'personalized')
    
    def test_user_recommendations_unauthenticated(self):
        response = self.client.get('/catalog/items/recommendations/for-me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_product_recommendations(self):
        response = self.client.get(f'/catalog/items/recommendations/product/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
        self.assertEqual(response.data['type'], 'product_based')
    
    def test_popular_products(self):
        response = self.client.get('/catalog/items/recommendations/popular/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'popular')
    
    def test_trending_products(self):
        response = self.client.get('/catalog/items/recommendations/trending/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['type'], 'trending')