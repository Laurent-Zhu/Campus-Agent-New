# from django.shortcuts import render
from ai_agents.teacher.lesson.lesson_preparation_agent import lesson_preparation_agent, generate_ppt_from_outline
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from .models import LessonPreparationRecord
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()

class LessonPreparationView(APIView):
    permission_classes = [AllowAny] # 暂时允许所有用户访问
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '请上传课程大纲或教学目标文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 临时用id=1的用户
        default_user = User.objects.get(id=1)
        record = LessonPreparationRecord.objects.create(
            teacher=default_user,
            outline_file=file
        )

        # 保存文件
        # record = LessonPreparationRecord.objects.create(
        #     teacher=request.user,
        #     outline_file=file
        # )
        file_path = record.outline_file.path

        # 调用AI Agent
        try:
            result = lesson_preparation_agent(file_path)
            record.result_json = result
            record.save()

            # generate_ppt
            pptx_url = None
            if isinstance(result, dict) and "ppt_outline" in result:
                pptx_filename = f"lesson_{record.id}.pptx"
                pptx_path = os.path.join(settings.MEDIA_ROOT, 'lesson_preparation', pptx_filename)
                generate_ppt_from_outline(result.get("ppt_outline", {}), pptx_path)
                pptx_url = request.build_absolute_uri(settings.MEDIA_URL + f"lesson_preparation/{pptx_filename}")

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "lesson_plan": result,
            "pptx_url": pptx_url
        }, status=status.HTTP_200_OK)

# Create your views here.