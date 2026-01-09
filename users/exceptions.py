from enum import Enum
from django.http import JsonResponse


class BusinessErrorCode(Enum):
    """业务错误编码枚举"""
    # 用户相关错误
    USER_NOT_FOUND = {"code": "USER_001", "message": "用户不存在"}
    USERNAME_EXISTS = {"code": "USER_002", "message": "用户名已存在"}
    EMAIL_EXISTS = {"code": "USER_003", "message": "邮箱已被使用"}
    INVALID_USER_DATA = {"code": "USER_004", "message": "用户数据无效"}
    
    # 资料相关错误
    PROFILE_NOT_FOUND = {"code": "PROF_001", "message": "用户资料不存在"}
    INVALID_PROFILE_DATA = {"code": "PROF_002", "message": "资料数据无效"}
    
    # 权限相关错误
    PERMISSION_DENIED = {"code": "PERM_001", "message": "权限不足"}
    
    # 通用错误
    VALIDATION_ERROR = {"code": "GEN_001", "message": "数据验证失败"}
    JSON_FORMAT_ERROR = {"code": "GEN_002", "message": "JSON格式错误"}
    GENERAL_ERROR = {"code": "GEN_999", "message": "系统错误"}


class BusinessException(Exception):
    """业务异常基类"""
    
    def __init__(self, error_code: BusinessErrorCode, detail: str = None):
        self.error_code = error_code.value["code"]
        self.message = error_code.value["message"]
        self.detail = detail or self.message
        super().__init__(self.detail)
    
    def to_response(self, status_code=400):
        """转换为HttpResponse"""
        return JsonResponse(
            {
                'error_code': self.error_code,
                'message': self.message,
                'detail': self.detail
            },
            status=status_code
        )


class UserNotFoundException(BusinessException):
    """用户不存在异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.USER_NOT_FOUND, detail)


class UsernameExistsException(BusinessException):
    """用户名已存在异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.USERNAME_EXISTS, detail)


class EmailExistsException(BusinessException):
    """邮箱已存在异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.EMAIL_EXISTS, detail)


class InvalidUserDataException(BusinessException):
    """无效用户数据异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.INVALID_USER_DATA, detail)


class ProfileNotFoundException(BusinessException):
    """用户资料不存在异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.PROFILE_NOT_FOUND, detail)


class InvalidProfileDataException(BusinessException):
    """无效资料数据异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.INVALID_PROFILE_DATA, detail)


class ValidationErrorException(BusinessException):
    """数据验证失败异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.VALIDATION_ERROR, detail)


class JsonFormatErrorException(BusinessException):
    """JSON格式错误异常"""
    def __init__(self, detail: str = None):
        super().__init__(BusinessErrorCode.JSON_FORMAT_ERROR, detail)


class GlobalExceptionHandler:
    """全局异常处理器"""
    
    @staticmethod
    def handle_exception(exception):
        """处理异常并返回响应"""
        if isinstance(exception, UserNotFoundException):
            return exception.to_response(404)
        elif isinstance(exception, (UsernameExistsException, EmailExistsException)):
            return exception.to_response(400)
        elif isinstance(exception, ValidationErrorException):
            return exception.to_response(400)
        elif isinstance(exception, JsonFormatErrorException):
            return exception.to_response(400)
        elif isinstance(exception, BusinessException):
            return exception.to_response()
        elif isinstance(exception, ValueError):
            # 处理未被捕获的ValueError
            business_error = BusinessException(
                BusinessErrorCode.GENERAL_ERROR,
                str(exception)
            )
            return business_error.to_response(500)
        elif isinstance(exception, TypeError):
            # 处理类型错误
            business_error = BusinessException(
                BusinessErrorCode.GENERAL_ERROR,
                f"类型错误: {str(exception)}"
            )
            return business_error.to_response(500)
        else:
            # 未预期的其他异常
            business_error = BusinessException(
                BusinessErrorCode.GENERAL_ERROR,
                f"系统错误: {str(exception)}"
            )
            return business_error.to_response(500)