from django.http import JsonResponse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    健康检查端点，返回应用和服务的健康状态
    """
    try:
        # 检查数据库连接
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # 检查Redis连接（如果使用了Redis）
        try:
            import redis
            from django.conf import settings
            
            redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379')
            redis_client = redis.from_url(redis_url)
            redis_client.ping()  # 尝试ping Redis服务器
            redis_status = True
        except Exception:
            redis_status = False
        
        # 组织健康检查响应
        health_status = {
            "status": "healthy",
            "details": {
                "database": {
                    "status": "healthy"
                },
                "redis": {
                    "status": "healthy" if redis_status else "unhealthy"
                },
                "application": {
                    "status": "healthy",
                    "version": getattr(settings, 'APP_VERSION', '1.0.0'),
                    "django": {
                        "version": __import__('django').get_version(),
                        "debug": settings.DEBUG
                    }
                }
            }
        }
        
        # 如果Redis不健康，整体状态标记为不健康
        if not redis_status:
            health_status["status"] = "unhealthy"
        
        return JsonResponse(health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status=503)

