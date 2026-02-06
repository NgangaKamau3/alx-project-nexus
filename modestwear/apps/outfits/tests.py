from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.outfits.models import Outfit, OutfitItem
from apps.catalog.models import Category, Product

User = get_user_model()

class OutfitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Dresses',
            slug='dresses'
        )
        self.product = Product.objects.create(
            name='Test Dress',
            slug='test-dress',
            category=self.category,
            base_price=99.99
        )
    
    def test_outfit_creation(self):
        outfit = Outfit.objects.create(
            user=self.user,
            name='Summer Outfit',
            description='Light and comfortable'
        )
        self.assertEqual(str(outfit), f"{self.user.username} - Summer Outfit")
    
    def test_outfit_item_creation(self):
        outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit'
        )
        outfit_item = OutfitItem.objects.create(
            outfit=outfit,
            product=self.product,
            position=1
        )
        self.assertEqual(str(outfit_item), "Test Outfit - Test Dress")

class OutfitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Dresses',
            slug='dresses'
        )
        self.product = Product.objects.create(
            name='Test Dress',
            slug='test-dress',
            category=self.category,
            base_price=99.99
        )
    
    def test_create_outfit_authenticated(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'My Outfit',
            'description': 'A nice outfit',
            'is_public': True
        }
        response = self.client.post('/outfits/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Outfit.objects.count(), 1)
    
    def test_create_outfit_unauthenticated(self):
        data = {'name': 'My Outfit'}
        response = self.client.post('/outfits/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
