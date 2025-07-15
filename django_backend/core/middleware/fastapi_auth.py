# core/middleware/fastapi_auth.py
import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

class FastAPIAuthMiddleware(MiddlewareMixin):
    """用于验证 FastAPI 生成的 JWT 令牌的中间件"""
    
    def process_request(self, request):
         # 打印请求基本信息
        print(f"\n===== [AuthMiddleware 调试] 开始处理请求 =====")
        print(f"请求方法: {request.method} | 请求路径: {request.path}")


        # 1. 跳过不需要认证的接口（如登录、注册）
        if request.path in ["/api/auth/login", "/api/auth/register"]:
            print(f"[AuthMiddleware 调试] 路径 {request.path} 无需认证，直接放行")
            return None  
        
        # 2. 从请求头提取令牌
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        # print(f"[AuthMiddleware 调试] 提取到的认证头: {auth_header}")
        if not auth_header or not auth_header.startswith("Bearer "):
            print(f"[AuthMiddleware 调试] 错误：未提供有效的 Bearer 令牌")
            return HttpResponse('未提供有效的令牌（格式：Bearer <token>）', status=401)
        
        token = auth_header.split("Bearer ")[1].strip()  # 提取令牌内容
        # print(f"[AuthMiddleware 调试] 提取到令牌: {token}")


        
        # 3. 调用 FastAPI 的 /validate 接口验证令牌
        try:
            # 向 FastAPI 发送验证请求（使用你配置的 FASTAPI_AUTH_VALIDATE_URL）
            response = requests.get(
                url=settings.FASTAPI_AUTH_VALIDATE_URL,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            print(f"[AuthMiddleware 调试] 验证响应状态码: {response.status_code}")
            # print(f"[AuthMiddleware 调试] 响应内容（前200字符）: {response.text[:200]}...")

            # 4. 处理 FastAPI 的返回结果
            if response.status_code == 200:
                # 验证成功：将用户信息绑定到 request 对象，供视图使用
                user_data = response.json()  # 例如：{"user_id": 1, "role": "student"}
                 # 设置到原生请求对象的 META 中
                request.META['FASTAPI_AUTH_USER'] = user_data
                # 打印原生 META 键确认
                # print(f"[中间件调试] 原生 request.META 键: {request.META.keys()}")
                print(f"[中间件调试] FASTAPI_AUTH_USER 值: {user_data}")
                return None
            
            else:
                # 验证失败（令牌无效、过期等）
                return HttpResponse(f"令牌验证失败：{response.json().get('detail', '未知错误')}", status=401)
        
        except requests.exceptions.RequestException as e:
            # 与 FastAPI 通信失败（如 FastAPI 未启动）
            print(f"[AuthMiddleware 调试] 认证服务通信失败：{str(e)}")
            return HttpResponseForbidden(f"认证服务不可用：{str(e)}")