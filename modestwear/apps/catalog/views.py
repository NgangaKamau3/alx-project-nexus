from django.http import Http404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.catalog.models import Product, Category, ProductVariant
from .serializers import ProductSerializer

class LatestProductList(APIView):
	permission_classes = [AllowAny]
	
	def get(self, request, format=None):
		products = Product.objects.all()[0:4]
		serializer = ProductSerializer(products, many=True)
		return Response(serializer.data)
	

class ProductDetail(APIView):
	permission_classes = [AllowAny]
	
	def get_object(self, category_slug, product_slug):
		try:
			return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
		except Product.DoesNotExist:
			raise Http404
		
	def get(self, request, category_slug, product_slug, format=None):
		product = self.get_object(category_slug, product_slug)
		serializer = ProductSerializer(product)
		return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def search(request):
	query = request.data.get('query', '')

	if query:
		products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
		serializer = ProductSerializer(products, many=True)
		return Response(serializer.data)
	else:
		return Response({"products": []})


@api_view(['GET'])
@permission_classes([AllowAny])
def categories_list(request):
	categories = Category.objects.filter(is_active=True)
	return Response([{
		'id': cat.slug,
		'name': cat.name,
		'count': cat.products.count()
	} for cat in categories])


@api_view(['GET'])
@permission_classes([AllowAny])
def get_filters(request):
	colors = list(ProductVariant.objects.values_list('color', flat=True).distinct())
	return Response({
		'sizes': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
		'colors': colors,
		'price_ranges': [
			{'label': 'Under R250', 'min': 0, 'max': 250},
			{'label': 'R250 - R350', 'min': 250, 'max': 350},
			{'label': 'R350 - R450', 'min': 350, 'max': 450},
			{'label': 'Over R450', 'min': 450, 'max': 10000},
		]
	})