# django_backend/student/urls.py
from django.urls import path

from django_backend.student.exercises.views import (
    ExerciseHistoryView,
    GenerateExerciseView,
    EvaluateAnswerView,
    
)

urlpatterns = [
    path('exercises/generate/', GenerateExerciseView.as_view()),
    path('exercises/evaluate/', EvaluateAnswerView.as_view()),
    path('history/', ExerciseHistoryView.as_view()),
]