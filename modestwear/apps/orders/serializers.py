from rest_framework import serializers
from .models import WishList, CartItem, Order, OrderItem
from apps.catalog.models import ProductVariant

class VariantBriefSerializer(serializers.ModelSerializer):
	product_name = serializers.ReadOnlyField(source='product.name')

	class Meta:
		model = ProductVariant
		fields = ['id', 'product_name', 'size', 'color']

class WishListSerializer(serializers.ModelSerializer):
	variant_details = VariantBriefSerializer(source='variant', read_only=True)
	class Meta:
		model = WishList
		fields = ['id', 'variant', 'variant_details', 'added_at']

class CartItemSerializer(serializers.ModelSerializer):
	variant_details = VariantBriefSerializer(source='variant', read_only=True)
	subtotal = serializers.SerializerMethodField()

	class Meta:
		model = CartItem
		fields = ['id', 'variant', 'variant_details', 'quantity', 'subtotal']
	
	def get_subtotal(self, obj):
		return obj.variant.product.base_price * obj.quantity
		
class OrderItemSerializer(serializers.ModelSerializer):
	variant_details = VariantBriefSerializer(source='variant', read_only=True)
	class Meta:
		model = OrderItem
		fields = ['id', 'variant_details', 'quantity', 'price_at_purchase']

class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)
	class Meta:
		model = Order
		fields = ['id', 'status', 'total_price', 'address', 'created_at', 'items']