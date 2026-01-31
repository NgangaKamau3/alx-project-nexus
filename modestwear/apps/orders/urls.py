from django.urls import path
from apps.orders import views

app_name = 'orders'

urlpatterns = [
	path('cart/', views.CartView.as_view(), name='cart-detail'),
	path('wishlist/', views.WishListView.as_view(), name='wishlist-detail'),
	path('wishlist/move-to-cart/<int:item_id>/', views.MoveToCartView.as_view(), name='move-to-cart'),
	path('checkout/', views.CheckoutView.as_view(), name='checkout'),
]