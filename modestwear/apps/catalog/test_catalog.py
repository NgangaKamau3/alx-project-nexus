import pytest
from rest_framework import status
from django.urls import reverse
from apps.catalog.models import Product

pytestmark = pytest.mark.django_db


@pytest.mark.catalog
class TestProductList:
    """Test product listing endpoints"""
    
    def test_latest_products(self, api_client, multiple_products):
        """Test getting latest products"""
        url = '/catalog/items/latest-products/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) <= 4  # Should return max 4 products
    
    def test_latest_products_empty(self, api_client):
        """Test latest products with no products"""
        url = '/catalog/items/latest-products/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.catalog
class TestProductDetail:
    """Test product detail endpoint"""
    
    def test_get_product_detail(self, api_client, product, category):
        """Test getting product detail"""
        url = f'/catalog/items/products/{category.slug}/{product.slug}/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name
        assert response.data['base_price'] == str(product.base_price)
    
    def test_get_nonexistent_product(self, api_client, category):
        """Test getting non-existent product"""
        url = f'/catalog/items/products/{category.slug}/nonexistent/'
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.catalog
class TestProductSearch:
    """Test product search endpoint"""
    
    def test_search_products_by_name(self, api_client, product):
        """Test searching products by name"""
        url = '/catalog/items/products/search/'
        data = {'query': 'Elegant'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert any('Elegant' in p['name'] for p in response.data)
    
    def test_search_products_by_description(self, api_client, product):
        """Test searching products by description"""
        url = '/catalog/items/products/search/'
        data = {'query': 'modest'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
    
    def test_search_no_results(self, api_client, product):
        """Test search with no results"""
        url = '/catalog/items/products/search/'
        data = {'query': 'nonexistent'}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_search_empty_query(self, api_client):
        """Test search with empty query"""
        url = '/catalog/items/products/search/'
        data = {'query': ''}
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'products' in response.data
        assert response.data['products'] == []


@pytest.mark.catalog
@pytest.mark.unit
class TestProductModel:
    """Test Product model"""
    
    def test_product_creation(self, product):
        """Test product is created correctly"""
        assert product.name == 'Elegant Maxi Dress'
        assert product.slug == 'elegant-maxi-dress'
        assert product.base_price == 89.99
    
    def test_product_str(self, product):
        """Test product string representation"""
        assert str(product) == 'Elegant Maxi Dress'
    
    def test_product_absolute_url(self, product, category):
        """Test product absolute URL"""
        expected_url = f'/{category.slug}/{product.slug}/'
        assert product.get_absolute_url() == expected_url


@pytest.mark.catalog
@pytest.mark.unit
class TestCategoryModel:
    """Test Category model"""
    
    def test_category_creation(self, category):
        """Test category is created correctly"""
        assert category.name == 'Dresses'
        assert category.slug == 'dresses'
        assert category.is_active is True
    
    def test_category_str(self, category):
        """Test category string representation"""
        assert str(category) == 'Dresses'
    
    def test_category_absolute_url(self, category):
        """Test category absolute URL"""
        assert category.get_absolute_url() == '/dresses/'


@pytest.mark.catalog
@pytest.mark.unit
class TestProductVariantModel:
    """Test ProductVariant model"""
    
    def test_variant_creation(self, product_variant):
        """Test product variant is created correctly"""
        assert product_variant.sku == 'EMD-001-M-NAVY'
        assert product_variant.size == 10
        assert product_variant.color == 'Navy Blue'
        assert product_variant.stock_available == 50
        assert product_variant.is_active is True
    
    def test_variant_product_relationship(self, product_variant, product):
        """Test variant is linked to product"""
        assert product_variant.product == product
        assert product_variant in product.variants.all()
