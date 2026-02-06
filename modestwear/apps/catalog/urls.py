from django.urls import path, include

from apps.catalog import views
from apps.catalog.recommendation_views import (
    user_recommendations,
    product_recommendations,
    popular_products,
    trending_products,
    similar_price_products
)

app_name = "catalog"

urlpatterns = [
	path('products/', views.LatestProductList.as_view(), name='product-list'),
	path('products/search/', views.search, name='product-search'),
	path('products/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail.as_view(), name='product-detail'),
	
	# Recommendation endpoints
	path('recommendations/for-me/', user_recommendations, name='user-recommendations'),
	path('recommendations/product/<int:product_id>/', product_recommendations, name='product-recommendations'),
	path('recommendations/popular/', popular_products, name='popular-products'),
	path('recommendations/trending/', trending_products, name='trending-products'),
	path('recommendations/similar-price/<int:product_id>/', similar_price_products, name='similar-price'),
]