from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Order

@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
	if created:
		print(f"Sending confirmation email to {instance.user.email}")