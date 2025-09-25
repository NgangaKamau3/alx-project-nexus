from django.urls import path
from . import views

urlpatterns = [
    path('trending/', views.trending_movies, name='trending-movies'),
    path('recommendations/', views.recommendations, name='movie-recommendations'),
]