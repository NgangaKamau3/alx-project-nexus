import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from apps.outfits.models import Outfit, OutfitItem
from apps.outfits.api.serializers import OutfitSerializer, OutfitItemSerializer
from apps.catalog.models import Category, Product, ProductVariant

User = get_user_model()

@pytest.mark.django_db
class OutfitModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.outfit = Outfit.objects.create(
            user=self.user,
            name='Summer Outfit',
            description='Perfect for summer days',
            is_public=True
        )
    
    def test_outfit_creation(self):
        self.assertEqual(self.outfit.user, self.user)
        self.assertEqual(self.outfit.name, 'Summer Outfit')
        self.assertTrue(self.outfit.is_public)
        self.assertIsNotNone(self.outfit.created_at)
    
    def test_outfit_str_method(self):
        expected = f"{self.outfit.name} by {self.user.username}"
        self.assertEqual(str(self.outfit), expected)
    
    def test_outfit_total_price_empty(self):
        self.assertEqual(self.outfit.total_price, Decimal('0.00'))
    
    def test_outfit_total_price_with_items(self):
        category = Category.objects.create(name="Dresses", slug="dresses")
        product = Product.objects.create(
            name="Test Dress",
            slug="test-dress",
            category=category,
            base_price=Decimal('99.99')
        )
        variant = ProductVariant.objects.create(
            product=product,
            size='M',
            color='Blue',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        OutfitItem.objects.create(
            outfit=self.outfit,
            product_variant=variant
        )
        self.assertEqual(self.outfit.total_price, Decimal('99.99'))

@pytest.mark.django_db
class OutfitItemModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit'
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
        self.outfit_item = OutfitItem.objects.create(
            outfit=self.outfit,
            product_variant=self.variant
        )
    
    def test_outfit_item_creation(self):
        self.assertEqual(self.outfit_item.outfit, self.outfit)
        self.assertEqual(self.outfit_item.product_variant, self.variant)
        self.assertIsNotNone(self.outfit_item.added_at)
    
    def test_outfit_item_str_method(self):
        expected = f"{self.product.name} in {self.outfit.name}"
        self.assertEqual(str(self.outfit_item), expected)
    
    def test_outfit_item_unique_constraint(self):
        # Test that we can't add the same variant twice to the same outfit
        with self.assertRaises(Exception):
            OutfitItem.objects.create(
                outfit=self.outfit,
                product_variant=self.variant
            )

@pytest.mark.django_db
class OutfitAPIViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
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
    
    def test_create_outfit_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('outfits:outfit-list')
        data = {
            'name': 'My New Outfit',
            'description': 'A beautiful outfit',
            'is_public': True
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'My New Outfit')
        self.assertEqual(response.data['user'], self.user.pk)
    
    def test_create_outfit_unauthenticated(self):
        url = reverse('outfits:outfit-list')
        data = {
            'name': 'My New Outfit',
            'description': 'A beautiful outfit'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_user_outfits(self):
        self.client.force_authenticate(user=self.user)
        Outfit.objects.create(
            user=self.user,
            name='Outfit 1',
            is_public=True
        )
        Outfit.objects.create(
            user=self.user,
            name='Outfit 2',
            is_public=False
        )
        # Create outfit for other user
        Outfit.objects.create(
            user=self.other_user,
            name='Other Outfit',
            is_public=True
        )
        
        url = reverse('outfits:outfit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only user's outfits
    
    def test_list_public_outfits(self):
        Outfit.objects.create(
            user=self.user,
            name='Public Outfit 1',
            is_public=True
        )
        Outfit.objects.create(
            user=self.user,
            name='Private Outfit',
            is_public=False
        )
        Outfit.objects.create(
            user=self.other_user,
            name='Public Outfit 2',
            is_public=True
        )
        
        url = reverse('outfits:public-outfits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only public outfits
    
    def test_outfit_detail_view(self):
        outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit',
            is_public=True
        )
        url = reverse('outfits:outfit-detail', kwargs={'pk': outfit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Outfit')
    
    def test_update_own_outfit(self):
        self.client.force_authenticate(user=self.user)
        outfit = Outfit.objects.create(
            user=self.user,
            name='Original Name'
        )
        url = reverse('outfits:outfit-detail', kwargs={'pk': outfit.pk})
        data = {'name': 'Updated Name'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')
    
    def test_update_other_user_outfit_forbidden(self):
        self.client.force_authenticate(user=self.user)
        outfit = Outfit.objects.create(
            user=self.other_user,
            name='Other User Outfit'
        )
        url = reverse('outfits:outfit-detail', kwargs={'pk': outfit.pk})
        data = {'name': 'Hacked Name'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_own_outfit(self):
        self.client.force_authenticate(user=self.user)
        outfit = Outfit.objects.create(
            user=self.user,
            name='To Delete'
        )
        url = reverse('outfits:outfit-detail', kwargs={'pk': outfit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Outfit.objects.filter(pk=outfit.pk).exists())

@pytest.mark.django_db
class OutfitItemAPIViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit'
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
    
    def test_add_item_to_outfit(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('outfits:add-item-to-outfit', kwargs={'outfit_pk': self.outfit.pk})
        data = {'product_variant': self.variant.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            OutfitItem.objects.filter(
                outfit=self.outfit,
                product_variant=self.variant
            ).exists()
        )
    
    def test_add_duplicate_item_to_outfit(self):
        self.client.force_authenticate(user=self.user)
        OutfitItem.objects.create(
            outfit=self.outfit,
            product_variant=self.variant
        )
        url = reverse('outfits:add-item-to-outfit', kwargs={'outfit_pk': self.outfit.pk})
        data = {'product_variant': self.variant.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_remove_item_from_outfit(self):
        self.client.force_authenticate(user=self.user)
        outfit_item = OutfitItem.objects.create(
            outfit=self.outfit,
            product_variant=self.variant
        )
        url = reverse('outfits:remove-item-from-outfit', kwargs={
            'outfit_pk': self.outfit.pk,
            'pk': outfit_item.pk
        })
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            OutfitItem.objects.filter(pk=outfit_item.pk).exists()
        )
    
    def test_list_outfit_items(self):
        OutfitItem.objects.create(
            outfit=self.outfit,
            product_variant=self.variant
        )
        url = reverse('outfits:outfit-items', kwargs={'outfit_pk': self.outfit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class OutfitSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit',
            description='Test description'
        )
    
    def test_outfit_serializer_read(self):
        serializer = OutfitSerializer(self.outfit)
        self.assertEqual(serializer.data['name'], 'Test Outfit')
        self.assertEqual(serializer.data['user'], self.user.pk)
        self.assertIn('items', serializer.data)
        self.assertIn('total_price', serializer.data)
    
    def test_outfit_serializer_create(self):
        data = {
            'name': 'New Outfit',
            'description': 'New description',
            'is_public': True
        }
        serializer = OutfitSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_outfit_serializer_invalid_data(self):
        data = {'name': ''}  # Empty name
        serializer = OutfitSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

class OutfitItemSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.outfit = Outfit.objects.create(
            user=self.user,
            name='Test Outfit'
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
        self.outfit_item = OutfitItem.objects.create(
            outfit=self.outfit,
            product_variant=self.variant
        )
    
    def test_outfit_item_serializer_read(self):
        serializer = OutfitItemSerializer(self.outfit_item)
        self.assertEqual(serializer.data['outfit'], self.outfit.pk)
        self.assertEqual(serializer.data['product_variant'], self.variant.pk)
        self.assertIn('product_details', serializer.data)
    
    def test_outfit_item_serializer_create(self):
        data = {
            'outfit': self.outfit.pk,
            'product_variant': self.variant.pk
        }
        serializer = OutfitItemSerializer(data=data)
        # This will fail due to unique constraint, but validates structure
        self.assertFalse(serializer.is_valid())

@pytest.mark.django_db
class OutfitIntegrationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
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
            base_price=Decimal('79.99')
        )
        self.variant1 = ProductVariant.objects.create(
            product=self.product1,
            size='M',
            color='Blue',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.variant2 = ProductVariant.objects.create(
            product=self.product2,
            size='L',
            color='Red',
            price=Decimal('79.99'),
            stock_quantity=5
        )
    
    def test_complete_outfit_workflow(self):
        self.client.force_authenticate(user=self.user)
        
        # 1. Create outfit
        outfit_url = reverse('outfits:outfit-list')
        outfit_data = {
            'name': 'Complete Outfit',
            'description': 'A complete outfit test',
            'is_public': True
        }
        outfit_response = self.client.post(outfit_url, outfit_data)
        self.assertEqual(outfit_response.status_code, status.HTTP_201_CREATED)
        outfit_id = outfit_response.data['id']
        
        # 2. Add first item
        add_item_url = reverse('outfits:add-item-to-outfit', kwargs={'outfit_pk': outfit_id})
        item1_data = {'product_variant': self.variant1.pk}
        item1_response = self.client.post(add_item_url, item1_data)
        self.assertEqual(item1_response.status_code, status.HTTP_201_CREATED)
        
        # 3. Add second item
        item2_data = {'product_variant': self.variant2.pk}
        item2_response = self.client.post(add_item_url, item2_data)
        self.assertEqual(item2_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Verify outfit details
        detail_url = reverse('outfits:outfit-detail', kwargs={'pk': outfit_id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(detail_response.data['items']), 2)
        expected_total = Decimal('99.99') + Decimal('79.99')
        self.assertEqual(Decimal(detail_response.data['total_price']), expected_total)
        
        # 5. Remove one item
        outfit_items = OutfitItem.objects.filter(outfit_id=outfit_id)
        remove_url = reverse('outfits:remove-item-from-outfit', kwargs={
            'outfit_pk': outfit_id,
            'pk': outfit_items.first().pk
        })
        remove_response = self.client.delete(remove_url)
        self.assertEqual(remove_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # 6. Verify updated outfit
        final_response = self.client.get(detail_url)
        self.assertEqual(len(final_response.data['items']), 1)
    
    def test_outfit_privacy_settings(self):
        # Create private outfit
        private_outfit = Outfit.objects.create(
            user=self.user,
            name='Private Outfit',
            is_public=False
        )
        
        # Create public outfit
        public_outfit = Outfit.objects.create(
            user=self.user,
            name='Public Outfit',
            is_public=True
        )
        
        # Test public outfits endpoint
        public_url = reverse('outfits:public-outfits')
        public_response = self.client.get(public_url)
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        
        # Should only show public outfit
        outfit_names = [outfit['name'] for outfit in public_response.data['results']]
        self.assertIn('Public Outfit', outfit_names)
        self.assertNotIn('Private Outfit', outfit_names)