# django_backend/admin/urls.py
from django.urls import path
from .views import (
    ResourceListCreateView, 
    ResourceDetailView, 
    ResourceDownloadView, 
    SubjectListView,
    CoursewareListView,
    CoursewareDeleteView,
    CoursewareDownloadView
)

urlpatterns = [
    # 资源列表和创建 (GET/POST)
    path('resources/', ResourceListCreateView.as_view(), name='resource-list'),
    
    # 单个资源操作 (GET/PUT/PATCH/DELETE)
    path('resources/<int:pk>/', ResourceDetailView.as_view(), name='resource-detail'),
    
    # 资源下载 (GET)
    path('resources/<int:pk>/download/', 
         ResourceDownloadView.as_view(), 
         name='resource-download'),
    
    # 学科列表 (GET)
    path('subjects/', SubjectListView.as_view(), name='subject-list'),

    # 课件列表 (GET)
    path('coursewares/', CoursewareListView.as_view(), name='courseware-list'),

    # 课件删除 (DELETE)
    path('coursewares/<int:pk>/', CoursewareDeleteView.as_view(), name='courseware-delete'),

    # 课件下载 (GET)
    path('coursewares/<int:pk>/download/', CoursewareDownloadView.as_view(), name='courseware-download'),
]