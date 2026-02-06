from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from apps.catalog.models import Product, Category
from apps.orders.models import Order, OrderItem
from apps.users.models import User
from apps.outfits.models import Outfit

class ModestWearAdminSite(admin.AdminSite):
    site_header = 'ModestWear Administration'
    site_title = 'ModestWear Admin'
    index_title = 'ModestWear Dashboard'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Date ranges
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        last_7_days = today - timedelta(days=7)
        
        # Key metrics
        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(status='delivered').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Recent activity
        recent_orders = Order.objects.filter(
            created_at__gte=last_7_days
        ).count()
        
        recent_users = User.objects.filter(
            date_joined__gte=last_7_days
        ).count()
        
        # Top products
        top_products = Product.objects.annotate(
            order_count=Count('variants__orderitem')
        ).filter(order_count__gt=0).order_by('-order_count')[:5]
        
        # Order status breakdown
        order_status = Order.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Low stock alerts
        low_stock_products = Product.objects.filter(
            variants__stock_available__lte=5,
            variants__is_active=True
        ).distinct()[:10]
        
        # Category performance
        category_performance = Category.objects.annotate(
            product_count=Count('products'),
            order_count=Count('products__variants__orderitem')
        ).filter(is_active=True).order_by('-order_count')[:5]
        
        context = {
            **self.each_context(request),
            'total_users': total_users,
            'total_products': total_products,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'recent_orders': recent_orders,
            'recent_users': recent_users,
            'top_products': top_products,
            'order_status': order_status,
            'low_stock_products': low_stock_products,
            'category_performance': category_performance,
        }
        
        return TemplateResponse(request, 'admin/dashboard.html', context)
    
    def index(self, request, extra_context=None):
        # Redirect to custom dashboard
        return self.dashboard_view(request)

# Create custom admin site instance
admin_site = ModestWearAdminSite(name='modestwear_admin')