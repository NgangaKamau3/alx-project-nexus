from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from apps.orders.models import WishList, CartItem, Order, OrderItem
from apps.orders.serializers import WishListSerializer, CartItemSerializer, OrderSerializer
from apps.orders.services import create_order_from_cart
from django.core.exceptions import ValidationError

class WishListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishListSerializer

    def get_queryset(self):
        return WishList.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartView(generics.ListCreateAPIView):
        permission_classes = [IsAuthenticated]
        serializer_class = CartItemSerializer
        def get_queryset(self):
            return CartItem.objects.filter(user=self.request.user)

        def perform_create(self, serializer):
            variant = serializer.validated_data['variant']
            item, created = CartItem.objects.get_or_create(
                user = self.request.user,
                variant = variant 
        )
            if not created:
                item.quantity += serializer.validated_data.get('quantity', 1)
                item.save()

        
class MoveToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            wishlist_item = WishList.objects.get(id=item_id, user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user, 
                variant=wishlist_item.variant
                )
            wishlist_item.delete()
            return Response({'message': 'Item moved to cart'}, status=status.HTTP_200_OK)
        except  WishList.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        

class CheckoutView(APIView):
    def post(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        try:
            order = create_order_from_cart(
                user=request.user,
                cart_items=cart_items,
                address=request.data.get('address')
            )
            return Response(OrderSerializer(order).data, status=201)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)