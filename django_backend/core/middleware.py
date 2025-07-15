# django_backend/core/middleware.py
import jwt
from django.conf import settings
from django.http import JsonResponse

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth.startswith('Bearer '):
            token = auth.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
                request.user_id = payload['sub']  # 这里sub是FastAPI签发时的用户id
                request.user_role = payload['role']
            except jwt.ExpiredSignatureError:
                return JsonResponse({'detail': 'Token已过期'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'detail': '无效Token'}, status=401)
        return self.get_response(request)