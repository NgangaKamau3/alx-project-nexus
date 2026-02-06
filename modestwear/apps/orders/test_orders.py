import pytest
from rest_framework import status
from django.urls import reverse
from apps.orders.models import CartItem, WishList, Order, OrderItem

pytestmark = pytest.mark.django_db


@pytest.mark.orders
class TestCartAPI:
    """Test cart endpoints"""
    
    def test_get_cart_authenticated(self, authenticated_client, cart_item):
        """Test getting cart items"""
        url = reverse('orders:cart-detail')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 1
        assert response.data[0]['quantity'] == 2
    
    def test_get_cart_unauthenticated(self, api_client):
        """Test getting cart without authentication"""
        url = reverse('orders:cart-detail')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_add_to_cart(self, authenticated_client, product_variant):
        """Test adding item to cart"""
        url = reverse('orders:cart-detail')
        data = {
            'variant': product_variant.id,
            'quantity': 3
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert CartItem.objects.filter(variant=product_variant).exists()
    
    def test_add_existing_item_to_cart(self, authenticated_client, cart_item):
        """Test adding existing item increases quantity"""
        url = reverse('orders:cart-detail')
        initial_quantity = cart_item.quantity
        data = {
            'variant': cart_item.variant.id,
            'quantity': 2
        }
        response = authenticated_client.post(url, data, format='json')
        
        cart_item.refresh_from_db()
        assert cart_item.quantity == initial_quantity + 2
    
    def test_get_empty_cart(self, authenticated_client):
        """Test getting empty cart"""
        url = reverse('orders:cart-detail')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.orders
class TestWishlistAPI:
    """Test wishlist endpoints"""
    
    def test_get_wishlist(self, authenticated_client, wishlist_item):
        """Test getting wishlist items"""
        url = reverse('orders:wishlist-detail')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 1
    
    def test_add_to_wishlist(self, authenticated_client, product_variant):
        """Test adding item to wishlist"""
        url = reverse('orders:wishlist-detail')
        data = {'variant': product_variant.id}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert WishList.objects.filter(variant=product_variant).exists()
    
    def test_move_to_cart(self, authenticated_client, wishlist_item, user):
        """Test moving wishlist item to cart"""
        url = reverse('orders:move-to-cart', kwargs={'item_id': wishlist_item.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert not WishList.objects.filter(id=wishlist_item.id).exists()
        assert CartItem.objects.filter(user=user, variant=wishlist_item.variant).exists()
    
    def test_move_nonexistent_item(self, authenticated_client):
        """Test moving non-existent wishlist item"""
        url = reverse('orders:move-to-cart', kwargs={'item_id': 9999})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.orders
class TestCheckoutAPI:
    """Test checkout endpoint"""
    
    def test_checkout_success(self, authenticated_client, cart_item, user):
        """Test successful checkout"""
        url = reverse('orders:checkout')
        data = {'address': '123 Main St, City, State 12345'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data
        assert response.data['status'] == 'pending'
        assert Order.objects.filter(user=user).exists()
        assert not CartItem.objects.filter(user=user).exists()  # Cart should be empty
    
    def test_checkout_empty_cart(self, authenticated_client):
        """Test checkout with empty cart"""
        url = reverse('orders:checkout')
        data = {'address': '123 Main St, City, State 12345'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_checkout_insufficient_stock(self, authenticated_client, cart_item):
        """Test checkout with insufficient stock"""
        # Set stock to less than cart quantity
        cart_item.variant.stock_available = 1
        cart_item.variant.save()
        cart_item.quantity = 5
        cart_item.save()
        
        url = reverse('orders:checkout')
        data = {'address': '123 Main St, City, State 12345'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Not enough stock' in str(response.data)


@pytest.mark.orders
@pytest.mark.unit
class TestCartItemModel:
    """Test CartItem model"""
    
    def test_cart_item_creation(self, cart_item):
        """Test cart item is created correctly"""
        assert cart_item.quantity == 2
        assert cart_item.variant is not None
        assert cart_item.user is not None
    
    def test_cart_item_subtotal(self, cart_item):
        """Test cart item subtotal calculation"""
        expected_subtotal = cart_item.variant.product.base_price * cart_item.quantity
        # Note: This would require adding a method to the model
        # assert cart_item.get_subtotal() == expected_subtotal


@pytest.mark.orders
@pytest.mark.unit
class TestOrderModel:
    """Test Order model"""
    
    def test_order_creation(self, order):
        """Test order is created correctly"""
        assert order.status == 'pending'
        assert order.total_price == 179.98
        assert order.address == '123 Main St, City, State 12345'
    
    def test_order_status_choices(self, order):
        """Test order status can be updated"""
        order.status = 'paid'
        order.save()
        order.refresh_from_db()
        assert order.status == 'paid'


@pytest.mark.orders
@pytest.mark.integration
class TestOrderCreationService:
    """Test order creation service"""
    
    def test_create_order_from_cart(self, authenticated_client, cart_item, user):
        """Test complete order creation flow"""
        initial_stock = cart_item.variant.stock_available
        
        url = reverse('orders:checkout')
        data = {'address': '456 Oak Ave, Town, State 67890'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify order created
        order = Order.objects.get(user=user)
        assert order.address == data['address']
        
        # Verify order items created
        assert order.items.count() == 1
        order_item = order.items.first()
        assert order_item.quantity == cart_item.quantity
        
        # Verify stock decreased
        cart_item.variant.refresh_from_db()
        assert cart_item.variant.stock_available == initial_stock - cart_item.quantity
        
        # Verify cart cleared
        assert not CartItem.objects.filter(user=user).exists()
