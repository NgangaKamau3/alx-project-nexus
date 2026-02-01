from django.contrib import admin, messages
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
	model = OrderItem
	readonly_fields = ('price_at_purchase',)
	extra = 0

@admin.action(description="Mark selected orders as shipped")
def make_shipped(modeladmin, request, queryset):
	updated = queryset.update(status='shipped')
	modeladmin.message_user(request, f"{updated} orders were successfully marked as shipped.", messages.SUCCESS)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		'user', 
		'status',
		'total_price',
		'created_at'
	)
	list_filter = (
		'status',
		'created_at'
	)
	actions = [make_shipped]
	inlines = [OrderItemInline]