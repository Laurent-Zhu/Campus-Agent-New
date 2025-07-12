# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .authentication import FastAPIAuthBackend  # 使用自定义认证类
from rest_framework.permissions import AllowAny

class ProtectedAPIView(APIView):
    # 指定认证方式（自动处理JWT验证）
    authentication_classes = [FastAPIAuthBackend]  
    
    # 要求用户必须通过认证
    permission_classes = [AllowAny]  

    def get(self, request):
        # 通过认证后，payload会自动存入request.auth
        return Response({
            'message': 'Access granted',
            'user': request.auth  # 直接使用验证后的JWT数据
        })