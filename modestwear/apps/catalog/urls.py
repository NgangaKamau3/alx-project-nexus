from django.urls import path, include

from apps.catalog import views

app_name = "catalog"

urlpatterns = [
	path('latest-products/', views.LatestProductList.as_view()),
	path('products/search/', views.search),
	path('products/<slug:category_slug>/<slug:product_slug>', views.ProductDetail.as_view())
]