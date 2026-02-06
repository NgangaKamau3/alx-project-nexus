from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.catalog.models import Category, Product, ProductImage, ProductVariant, CoverageLevel

class ProductVariantInline(admin.TabularInline):
	model = ProductVariant
	extra = 1
	fields = ('sku', 'size', 'color', 'coverage', 'stock_available', 'is_active')
	readonly_fields = ('sku',)

	def get_readonly_fields(self, request, obj=None):
		if obj:  # Editing existing object
			return self.readonly_fields + ('sku',)
		return self.readonly_fields

class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 1
	fields = ('image', 'thumbnail_preview', 'is_feature')
	readonly_fields = ('thumbnail_preview',)

	def thumbnail_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.get_thumbnail())
		return "No image"
	thumbnail_preview.short_description = "Preview"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'category',
		'base_price',
		'product_size',
		'is_featured',
		'total_stock',
		'variant_count',
		'date_added'
	)
	list_filter = (
		'category',
		'product_size',
		'is_featured',
		'date_added'
	)
	list_editable = ('is_featured', 'base_price')
	search_fields = (
		'name',
		'description',
		'slug',
		'variants__sku'
	)
	prepopulated_fields = {'slug': ('name',)}
	inlines = [ProductVariantInline, ProductImageInline]
	actions = ['make_featured', 'remove_featured']
	list_per_page = 25

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('category', 'product_size').prefetch_related('variants')

	def total_stock(self, obj):
		total = sum(variant.stock_available for variant in obj.variants.all())
		if total == 0:
			return format_html('<span style="color: red; font-weight: bold;">OUT OF STOCK</span>')
		elif total <= 10:
			return format_html('<span style="color: orange; font-weight: bold;">{} (LOW)</span>', total)
		return format_html('<span style="color: green;">{}</span>', total)
	total_stock.short_description = 'Total Stock'
	total_stock.admin_order_field = 'variants__stock_available'

	def variant_count(self, obj):
		return obj.variants.count()
	variant_count.short_description = 'Variants'

	@admin.action(description='Mark selected products as featured')
	def make_featured(self, request, queryset):
		updated = queryset.update(is_featured=True)
		self.message_user(request, f'{updated} products marked as featured.')

	@admin.action(description='Remove featured status')
	def remove_featured(self, request, queryset):
		updated = queryset.update(is_featured=False)
		self.message_user(request, f'{updated} products removed from featured.')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'parent',
		'slug',
		'product_count',
		'is_active'
	)
	list_filter = (
		'is_active',
		'parent'
	)
	list_editable = ('is_active',)
	search_fields = (
		'name',
		'slug'
	)
	prepopulated_fields = {'slug': ('name',)}
	actions = ['activate_categories', 'deactivate_categories']

	def get_queryset(self, request):
		return super().get_queryset(request).annotate(product_count=Count('products'))

	def product_count(self, obj):
		return obj.product_count
	product_count.short_description = 'Products'
	product_count.admin_order_field = 'product_count'

	@admin.action(description='Activate selected categories')
	def activate_categories(self, request, queryset):
		updated = queryset.update(is_active=True)
		self.message_user(request, f'{updated} categories activated.')

	@admin.action(description='Deactivate selected categories')
	def deactivate_categories(self, request, queryset):
		updated = queryset.update(is_active=False)
		self.message_user(request, f'{updated} categories deactivated.')

@admin.register(CoverageLevel)
class CoverageLevelAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'description',
		'product_count'
	)
	search_fields = ('name',)

	def get_queryset(self, request):
		return super().get_queryset(request).annotate(product_count=Count('products'))

	def product_count(self, obj):
		return obj.product_count
	product_count.short_description = 'Products Using'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
	list_display = ('product', 'sku', 'size', 'color', 'stock_status', 'is_active')
	list_filter = ('is_active', 'size', 'color', 'product__category')
	search_fields = ('sku', 'product__name', 'color')
	list_editable = ('is_active',)
	actions = ['mark_out_of_stock', 'restock_items']

	def stock_status(self, obj):
		if obj.stock_available <= 0:
			color = 'red'
			text = 'OUT OF STOCK'
		elif obj.stock_available <= 5:
			color = 'orange'
			text = f'LOW STOCK ({obj.stock_available})'
		else:
			color = 'green'
			text = f'IN STOCK ({obj.stock_available})'
		return format_html('<b style="color: {};">{}</b>', color, text)
	stock_status.short_description = 'Stock Status'

	@admin.action(description='Mark as out of stock')
	def mark_out_of_stock(self, request, queryset):
		updated = queryset.update(stock_available=0, is_active=False)
		self.message_user(request, f'{updated} variants marked as out of stock.')

	@admin.action(description='Restock items (set to 10)')
	def restock_items(self, request, queryset):
		updated = queryset.update(stock_available=10, is_active=True)
		self.message_user(request, f'{updated} variants restocked.')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ('product', 'image_preview', 'is_feature')
	list_filter = ('is_feature', 'product__category')
	search_fields = ('product__name',)
	list_editable = ('is_feature',)

	def image_preview(self, obj):
		if obj.image:
			return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.get_thumbnail())
		return "No image"
	image_preview.short_description = "Preview"