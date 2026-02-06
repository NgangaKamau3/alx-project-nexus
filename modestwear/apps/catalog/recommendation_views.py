from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.catalog.models import Product
from apps.catalog.serializers import ProductSerializer
from apps.catalog.recommendations import RecommendationService

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def user_recommendations(request):
    """
    Get personalized recommendations for authenticated user
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required for personalized recommendations'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    limit = int(request.GET.get('limit', 10))
    recommendations = RecommendationService.get_recommendations(
        user=request.user, 
        limit=limit
    )
    
    serializer = ProductSerializer(recommendations, many=True)
    return Response({
        'recommendations': serializer.data,
        'count': len(recommendations),
        'type': 'personalized'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def product_recommendations(request, product_id):
    """
    Get recommendations based on a specific product
    """
    product = get_object_or_404(Product, id=product_id)
    limit = int(request.GET.get('limit', 10))
    
    user = request.user if request.user.is_authenticated else None
    recommendations = RecommendationService.get_recommendations(
        user=user,
        product=product,
        limit=limit
    )
    
    serializer = ProductSerializer(recommendations, many=True)
    return Response({
        'recommendations': serializer.data,
        'count': len(recommendations),
        'type': 'product_based',
        'based_on': ProductSerializer(product).data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def popular_products(request):
    """
    Get popular products based on sales and usage
    """
    limit = int(request.GET.get('limit', 10))
    popular = RecommendationService._popularity_based(limit)
    
    serializer = ProductSerializer(popular, many=True)
    return Response({
        'recommendations': serializer.data,
        'count': len(popular),
        'type': 'popular'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def trending_products(request):
    """
    Get trending products based on recent activity
    """
    limit = int(request.GET.get('limit', 10))
    trending = RecommendationService.get_trending_products(limit)
    
    serializer = ProductSerializer(trending, many=True)
    return Response({
        'recommendations': serializer.data,
        'count': len(trending),
        'type': 'trending'
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def similar_price_products(request, product_id):
    """
    Get products in similar price range
    """
    product = get_object_or_404(Product, id=product_id)
    limit = int(request.GET.get('limit', 10))
    
    similar = RecommendationService.get_price_based_recommendations(product, limit)
    
    serializer = ProductSerializer(similar, many=True)
    return Response({
        'recommendations': serializer.data,
        'count': len(similar),
        'type': 'similar_price',
        'price_range': f"${product.base_price}",
        'based_on': ProductSerializer(product).data
    })