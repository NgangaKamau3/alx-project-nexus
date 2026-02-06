from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_order_payment(order_id):
    """
    Process order payment asynchronously
    """
    try:
        from apps.orders.models import Order
        
        order = Order.objects.get(id=order_id)
        # Payment processing logic here
        logger.info(f"Processing payment for order {order_id}")
        return f"Payment processed for order {order_id}"
        
    except Exception as exc:
        logger.error(f"Payment processing failed: {str(exc)}")
        raise


@shared_task
def update_inventory_stock(variant_id, quantity):
    """
    Update inventory stock levels
    """
    try:
        from apps.catalog.models import ProductVariant
        
        variant = ProductVariant.objects.get(id=variant_id)
        variant.stock_available -= quantity
        variant.save()
        
        logger.info(f"Stock updated for variant {variant_id}")
        return f"Stock updated: {variant.sku}"
        
    except Exception as exc:
        logger.error(f"Stock update failed: {str(exc)}")
        raise


@shared_task
def check_low_stock_alerts():
    """
    Periodic task to check for low stock items
    Run hourly via Celery Beat
    """
    from apps.catalog.models import ProductVariant
    
    low_stock_items = ProductVariant.objects.filter(
        stock_available__lte=5,
        is_active=True
    )
    
    for item in low_stock_items:
        logger.warning(f"Low stock alert: {item.product.name} - {item.sku} ({item.stock_available} left)")
    
    return f"Checked {low_stock_items.count()} low stock items"
