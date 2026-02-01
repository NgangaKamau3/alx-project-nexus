from django.db import transaction
from django.core.exceptions import ValidationError
from apps.orders.models import Order, OrderItem

def create_order_from_cart(user, cart_items, address):
    with transaction.atomic():
        for item in cart_items:
            if item.variant.stock_quantity < item.quantity:
                raise ValidationError(f"Not enough stock for {item.variant.product.name}")
            
        total_price = sum(item.variant.product.base_price * item.quantity for item in cart_items)

        for item in cart_items:
            order = OrderItem.objects.create(
                user=user,
                total_price=total_price,
                address=address
        )
            item.variant.stock_quantity -= item.quantity
            item.variant.save()
        cart_items.delete()
        return order