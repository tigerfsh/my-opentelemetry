from django.http import JsonResponse
from users.exceptions import GlobalExceptionHandler


class GlobalExceptionMiddleware:
    """
    全局异常处理中间件
    捕获所有未被处理的异常并返回标准化错误响应
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        处理视图中未捕获的异常
        """
        # 使用全局异常处理器处理异常
        return GlobalExceptionHandler.handle_exception(exception)