# Register all admin configurations with custom admin site
from core.admin import admin_site

# Import all admin classes
from apps.catalog.admin import (
    ProductAdmin, CategoryAdmin, CoverageLevelAdmin, 
    ProductVariantAdmin, ProductImageAdmin
)
from apps.users.admin import UserAdmin
from apps.orders.admin import OrderAdmin, OrderItemAdmin, CartItemAdmin, WishListAdmin
from apps.outfits.admin import OutfitAdmin, OutfitItemAdmin

# Import models
from apps.catalog.models import Product, Category, CoverageLevel, ProductVariant, ProductImage
from apps.users.models import User
from apps.orders.models import Order, OrderItem, CartItem, WishList
from apps.outfits.models import Outfit, OutfitItem

# Unregister from default admin first
from django.contrib import admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

# Register with custom admin site
admin_site.register(Product, ProductAdmin)
admin_site.register(Category, CategoryAdmin)
admin_site.register(CoverageLevel, CoverageLevelAdmin)
admin_site.register(ProductVariant, ProductVariantAdmin)
admin_site.register(ProductImage, ProductImageAdmin)

admin_site.register(User, UserAdmin)

admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem, OrderItemAdmin)
admin_site.register(CartItem, CartItemAdmin)
admin_site.register(WishList, WishListAdmin)

admin_site.register(Outfit, OutfitAdmin)
admin_site.register(OutfitItem, OutfitItemAdmin)