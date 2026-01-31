from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

schema_view = swagger_get_schema_view(
	openapi.Info(
		title="Products Catalog API.",
		default_version="1.0.0",
		description="This is the API documentation for the product catalog API for modestwear.",
	),
	public=True,
)
urlpatterns = [
    path("admin/", admin.site.urls),
	path("api/v1/", include("djoser.urls")),
	path("api/v1/", include("djoser.urls.authtoken")),
	path("api/v1/", 
	    include([
			path("post/", include("apps.catalog.urls")),
			path("swagger/schema/", schema_view.with_ui("swagger", cache_timeout=0), name="swagger-schema"),
			])
		),
	path("api/v1/", include("apps.orders.urls")),
	
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
