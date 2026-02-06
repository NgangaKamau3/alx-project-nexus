from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.urls import reverse
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'full_name', 'phone_number', 'is_staff', 'is_active', 'date_joined', 'order_count', 'total_spent')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    list_per_page = 25
    actions = ['activate_users', 'deactivate_users']
    
    # Required for custom user models without 'username'
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number'),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            order_count=Count('order'),
            total_spent=Sum('order__total_price')
        )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "No name"
    full_name.short_description = 'Full Name'
    
    def order_count(self, obj):
        count = obj.order_count or 0
        if count > 0:
            url = reverse('admin:orders_order_changelist') + f'?user__id__exact={obj.id}'
            return format_html('<a href="{}">{} orders</a>', url, count)
        return '0 orders'
    order_count.short_description = 'Orders'
    order_count.admin_order_field = 'order_count'
    
    def total_spent(self, obj):
        total = obj.total_spent or 0
        if total > 0:
            return format_html('<strong>${:.2f}</strong>', total)
        return '$0.00'
    total_spent.short_description = 'Total Spent'
    total_spent.admin_order_field = 'total_spent'
    
    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')
    
    @admin.action(description='Deactivate selected users')
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
