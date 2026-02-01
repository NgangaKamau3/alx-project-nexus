from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import OrderItem

@receiver(post_save, sender=OrderItem)
def check_stock_level(sender, instance, **kwargs):
	variant = instance.variant
	if variant.stock_quantity <=5: 
		print(f"Alarm: Low stock for {variant.product.name} - {variant.size}. Only {variant.stock_available} left.")