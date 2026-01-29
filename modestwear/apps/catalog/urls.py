from django.urls import path, include

from catalog import views

urlpatterns = [
	path('latest-products/', views.LatestProductList.as_view()),
]