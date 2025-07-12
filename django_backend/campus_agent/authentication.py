# authentication.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from .utils.jwt_utils import FastAPIJWTValidator

class FastAPIAuthBackend(BaseAuthentication):
    """
    Django REST Framework 认证后端，用于验证 FastAPI 的 JWT
    """
    keyword = 'Bearer'  # 认证头前缀

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None  # 返回 None 让其他认证后端处理

        try:
            # 分离 'Bearer ' 和实际的 token
            auth_parts = auth_header.split()
            if len(auth_parts) != 2 or auth_parts[0].lower() != self.keyword.lower():
                raise AuthenticationFailed(_('Authorization header must be "Bearer <token>"'))
            
            token = auth_parts[1]
            payload = FastAPIJWTValidator.validate_token(token)
            
            # 这里你可以根据需要创建 Django 用户对象或直接返回 payload
            # 示例：返回一个元组 (user, auth)，user 可以是 None
            return (None, payload)  # 或者返回你的自定义用户对象
            
        except Exception as e:
            raise AuthenticationFailed(str(e))