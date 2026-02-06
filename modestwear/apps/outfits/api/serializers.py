from rest_framework import serializers
from apps.outfits.models import Outfit, OutfitItem
from apps.catalog.serializers import ProductSerializer

class OutfitItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OutfitItem
        fields = ['id', 'product', 'product_id', 'position']

class OutfitSerializer(serializers.ModelSerializer):
    items = OutfitItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Outfit
        fields = ['id', 'name', 'description', 'is_public', 'created_at', 'updated_at', 'items', 'items_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_items_count(self, obj):
        return obj.items.count()

class OutfitCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Outfit
        fields = ['name', 'description', 'is_public', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        outfit = Outfit.objects.create(user=self.context['request'].user, **validated_data)
        
        for item_data in items_data:
            OutfitItem.objects.create(
                outfit=outfit,
                product_id=item_data['product_id'],
                position=item_data.get('position', 0)
            )
        
        return outfit