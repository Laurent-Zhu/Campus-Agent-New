# django_backend/teacher/urls.py
from django.urls import path
from .views import LessonPreparationView

urlpatterns = [
    path('lesson-preparation/', LessonPreparationView.as_view(), name='lesson_preparation'),
]