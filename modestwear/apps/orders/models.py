from django.db import models
from django.conf import settings
from apps.catalog.models import ProductVariant
class WishList(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('user', 'variant')

class CartItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	session_key = models.CharField(max_length=40, null=True, blank=True)
	variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)
	created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
	STATUS_CHOICES = (
		("pending", "Pending"),
		("paid", "Paid"),
		("shipped", "Shipped"),
		("delivered", "Delivered"),
		("cancelled", "Cancelled")
	)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	address = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
	variant = models.ForeignKey(ProductVariant, on_delete= models.CASCADE)
	quantity = models.PositiveIntegerField()
	price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

