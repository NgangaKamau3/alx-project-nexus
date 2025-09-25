from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('profile/', views.user_profile, name='user-profile'),
    path('favorites/', views.user_favorites, name='user-favorites'),
    path('favorites/<int:tmdb_id>/', views.favorite_movie, name='favorite-movie'),
]