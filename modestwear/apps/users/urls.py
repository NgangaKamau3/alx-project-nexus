from django.urls import path, include
from .views import UserProfileView

urlpatterns = [
    # Djoser endpoints: /login, /logout, /register, /password-reset
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
    # Custom profile endpoint
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]