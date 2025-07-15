# django_backend/administor/views.py
from rest_framework.generics import (
    ListCreateAPIView, 
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Resource, Subject
from .serializers import ResourceSerializer, SubjectSerializer
from django.http import FileResponse

class ResourceListCreateView(ListCreateAPIView):
    """资源列表和创建视图"""
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    filterset_fields = ['type', 'subject__id', 'shared']

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

class ResourceDetailView(RetrieveUpdateDestroyAPIView):
    """单个资源操作视图"""
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

class ResourceDownloadView(APIView):
    """资源下载视图"""
    def get(self, request, pk):
        resource = Resource.objects.get(pk=pk)
        return FileResponse(resource.file.open(), as_attachment=True)

class SubjectListView(ListAPIView):
    """学科列表视图"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

# 新增视图类
class CoursewareListView(ListAPIView):
    """课件列表视图"""
    queryset = Resource.objects.filter(type='courseware')  # 假设课件类型为 'courseware'
    serializer_class = ResourceSerializer

class CoursewareDeleteView(RetrieveUpdateDestroyAPIView):
    """课件删除视图"""
    queryset = Resource.objects.filter(type='courseware')
    serializer_class = ResourceSerializer

class CoursewareDownloadView(APIView):
    """课件下载视图"""
    def get(self, request, pk):
        resource = Resource.objects.filter(type='courseware', pk=pk).first()
        if resource:
            return FileResponse(resource.file.open(), as_attachment=True)
        return Response({'error': '课件不存在'}, status=404)