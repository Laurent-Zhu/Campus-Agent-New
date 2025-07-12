# utils/jwt_utils.py
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class FastAPIJWTValidator:
    """
    用于验证 FastAPI 生成的 JWT 令牌
    """
    @staticmethod
    def validate_token(token: str) -> dict:
        """
        验证 JWT 并返回 payload
        :param token: JWT 令牌字符串（不带 'Bearer ' 前缀）
        :return: 解码后的 payload
        :raises: AuthenticationFailed 如果验证失败
        """
        try:
            payload = jwt.decode(
                token,
                settings.FASTAPI_JWT['SECRET_KEY'],
                algorithms=[settings.FASTAPI_JWT['ALGORITHM']],
                options={
                    'verify_exp': True,  # 验证过期时间
                    'verify_signature': True,  # 验证签名
                }
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')