from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

@require_http_methods(["GET"])
@permission_classes([AllowAny])
@never_cache
def health_check(request):
    """Comprehensive health check with database verification"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)

@require_http_methods(["GET"])
@permission_classes([AllowAny])
@never_cache
def healthz(request):
    """Lightweight keep-alive endpoint for cron jobs"""
    return JsonResponse({'status': 'ok'})