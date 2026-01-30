from django.contrib import admin

from .models import Category, Product, ProductImage, ProductVariant, CoverageLevel

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