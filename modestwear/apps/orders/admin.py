from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from .models import Order, OrderItem, CartItem, WishList

class OrderItemInline(admin.TabularInline):
	model = OrderItem
	readonly_fields = ('price_at_purchase',)
	extra = 0
	fields = ('variant', 'quantity', 'price_at_purchase')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'user',
		'status',
		'total_price',
		'created_at'
	)
	list_filter = (
		'status',
		'created_at'
	)
	search_fields = ('user__email', 'user__first_name', 'user__last_name', 'id')
	list_editable = ('status',)
	actions = ['mark_shipped', 'mark_delivered', 'mark_cancelled']
	inlines = [OrderItemInline]
	list_per_page = 25
	date_hierarchy = 'created_at'

	@admin.action(description="Mark selected orders as shipped")
	def mark_shipped(self, request, queryset):
		updated = queryset.update(status='shipped')
		self.message_user(request, f"{updated} orders marked as shipped.", messages.SUCCESS)

	@admin.action(description="Mark selected orders as delivered")
	def mark_delivered(self, request, queryset):
		updated = queryset.update(status='delivered')
		self.message_user(request, f"{updated} orders marked as delivered.", messages.SUCCESS)

	@admin.action(description="Mark selected orders as cancelled")
	def mark_cancelled(self, request, queryset):
		updated = queryset.update(status='cancelled')
		self.message_user(request, f"{updated} orders cancelled.", messages.WARNING)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
	list_display = ('order', 'variant', 'quantity', 'price_at_purchase')
	list_filter = ('order__status', 'order__created_at')
	search_fields = ('order__id', 'variant__product__name', 'variant__sku')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
	list_display = ('user', 'variant', 'quantity', 'created_at')
	list_filter = ('created_at', 'variant__product__category')
	search_fields = ('user__email', 'session_key', 'variant__product__name')

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
	list_display = ('user', 'variant', 'added_at')
	list_filter = ('added_at', 'variant__product__category')
	search_fields = ('user__email', 'variant__product__name')
	date_hierarchy = 'added_at'