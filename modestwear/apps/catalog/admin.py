from django.contrib import admin
from django.utils.html import format_html

from apps.catalog.models import Category, Product, ProductImage, ProductVariant, CoverageLevel

class ProductVariantInline(admin.TabularInline):
	model = ProductVariant
	extra = 1

class ProductImageInline(admin.TabularInline):
	model = ProductImage
	extra = 2

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'category',
		'base_price',
		'product_size', 
		'date_added'
	)
	list_filter = (
		'category',
		'product_size', 
		'is_featured'
	)

	search_fields = (
		'name',
		'description',
		'slug'
	)

	prepopulated_fields = {'slug': ('name',)}
	inlines = [ProductImageInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'parent',
		'slug',
		'is_active'		
	)

	list_filter = (
		'is_active',
		'parent'
	)
	search_fields = (
		'name', 
		'slug'
	)
	prepopulated_fields = {'slug': ('name',)}

@admin.register(CoverageLevel)
class CoverageLevelAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'description'
	)
	search_fields = (
		'name',
	)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
	list_display = ('product', 'size', 'color', 'stock_available')

	def stock_status(self, obj):
		if obj.quantity <=0:
			color = 'red'
			text = 'OUT OF STOCK'
		elif obj.stock_available <=5:
			color = 'orange'
			text = f'LOW STOCK ({obj.stock_available})'
		else:
			color = 'green'
			text = 'IN STOCK'

		return format_html('<b style="color: {};">{}<"/b>', color, text)