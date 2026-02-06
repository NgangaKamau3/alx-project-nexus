from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from core.admin import admin_site

# Import admin registry to register models
import core.admin_registry

schema_view = swagger_get_schema_view(
	openapi.Info(
		title="ModestWear API",
		default_version="1.0.0",
		description="ModestWear Fashion E-commerce API - Complete solution for modest fashion retail",
	),
	public=True,
	permission_classes=[permissions.AllowAny]
)

urlpatterns = [
    path("admin/", admin_site.urls),  # Custom admin
    path("django-admin/", admin.site.urls),  # Fallback admin
	path("api/auth/", include('users.urls')),
	path("catalog/", 
	    include([
			path("items/", include("apps.catalog.urls")),
			])
),
	path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-schema"),
	path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-schema"),
	path("orders/", include("apps.orders.urls")),
	path("outfits/", include("apps.outfits.urls")),
	
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
