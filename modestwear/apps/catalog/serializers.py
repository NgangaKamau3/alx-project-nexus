from rest_framework import serializers
from .models import Category, Product

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = (
			"category",
			"name",
			"get_absolute_url",
			"description",
			"base_price",

		)