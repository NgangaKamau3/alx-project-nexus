from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.outfits.models import Outfit, OutfitItem
from apps.catalog.models import Product
from .serializers import OutfitSerializer, OutfitCreateSerializer, OutfitItemSerializer

class OutfitListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OutfitCreateSerializer
        return OutfitSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Outfit.objects.none()
        return Outfit.objects.filter(user=self.request.user).prefetch_related('items__product')

class OutfitDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OutfitSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Outfit.objects.none()
        return Outfit.objects.filter(user=self.request.user).prefetch_related('items__product')

class PublicOutfitListView(generics.ListAPIView):
    serializer_class = OutfitSerializer
    queryset = Outfit.objects.filter(is_public=True).prefetch_related('items__product')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_to_outfit(request, outfit_id):
    outfit = get_object_or_404(Outfit, id=outfit_id, user=request.user)
    product_id = request.data.get('product_id')
    position = request.data.get('position', 0)
    
    if not product_id:
        return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    outfit_item, created = OutfitItem.objects.get_or_create(
        outfit=outfit,
        product=product,
        defaults={'position': position}
    )
    
    if not created:
        return Response({'error': 'Product already in outfit'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = OutfitItemSerializer(outfit_item)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_item_from_outfit(request, outfit_id, item_id):
    outfit = get_object_or_404(Outfit, id=outfit_id, user=request.user)
    outfit_item = get_object_or_404(OutfitItem, id=item_id, outfit=outfit)
    outfit_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)