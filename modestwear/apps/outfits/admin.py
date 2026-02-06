from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from .models import Outfit, OutfitItem

class OutfitItemInline(admin.TabularInline):
	model = OutfitItem
	extra = 1
	fields = ('product', 'position')
	autocomplete_fields = ['product']

@admin.register(Outfit)
class OutfitAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'user_link',
		'item_count',
		'is_public',
		'created_at',
		'updated_at'
	)
	list_filter = (
		'is_public',
		'created_at',
		'updated_at'
	)
	search_fields = (
		'name',
		'description',
		'user__email',
		'user__first_name',
		'user__last_name'
	)
	list_editable = ('is_public',)
	actions = ['make_public', 'make_private']
	inlines = [OutfitItemInline]
	list_per_page = 25
	date_hierarchy = 'created_at'

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user').annotate(
			item_count=Count('items')
		)

	def user_link(self, obj):
		url = reverse('admin:users_user_change', args=[obj.user.id])
		return format_html('<a href="{}">{}</a>', url, obj.user.email)
	user_link.short_description = 'User'
	user_link.admin_order_field = 'user__email'

	def item_count(self, obj):
		count = obj.item_count
		if count > 0:
			return format_html('<strong>{} items</strong>', count)
		return '0 items'
	item_count.short_description = 'Items'
	item_count.admin_order_field = 'item_count'

	@admin.action(description='Make selected outfits public')
	def make_public(self, request, queryset):
		updated = queryset.update(is_public=True)
		self.message_user(request, f'{updated} outfits made public.')

	@admin.action(description='Make selected outfits private')
	def make_private(self, request, queryset):
		updated = queryset.update(is_public=False)
		self.message_user(request, f'{updated} outfits made private.')

@admin.register(OutfitItem)
class OutfitItemAdmin(admin.ModelAdmin):
	list_display = ('outfit_link', 'product', 'position')
	list_filter = ('outfit__is_public', 'product__category')
	search_fields = ('outfit__name', 'product__name')
	autocomplete_fields = ['outfit', 'product']

	def outfit_link(self, obj):
		url = reverse('admin:outfits_outfit_change', args=[obj.outfit.id])
		return format_html('<a href="{}">{}</a>', url, obj.outfit.name)
	outfit_link.short_description = 'Outfit'
	outfit_link.admin_order_field = 'outfit__name'
