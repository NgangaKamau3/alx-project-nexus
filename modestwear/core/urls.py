from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg import openapi
from rest_framework import permissions
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from core.admin import admin_site
from .health import health_check
from .views import index

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
    path("", index, name="index"),
    path("admin/", admin_site.urls),
    path("django-admin/", admin.site.urls),
    path("health/", health_check, name="health-check"),
	path("api/auth/", include('users.urls')),
	path("api/catalog/", include("apps.catalog.urls")),
	path("api/orders/", include("apps.orders.urls")),
	path("api/outfits/", include("apps.outfits.urls")),
	path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-schema"),
	path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc-schema"),
	
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
