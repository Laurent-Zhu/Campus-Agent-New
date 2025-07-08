# django_backend/student/urls.py
from django.urls import path

from django_backend.student.exercises.views import (
    ExerciseHistoryView,
    GenerateExerciseView,
    EvaluateAnswerView,
    SubmitExerciseView,
    
)

urlpatterns = [
    # 练习相关路由
    path("exercises/generate/", GenerateExerciseView.as_view(), name="generate-exercise"),
    path("exercises/evaluate/", EvaluateAnswerView.as_view(), name="evaluate-answer"),
    path("exercises/submit/", SubmitExerciseView.as_view(), name="submit-exercise"),
    
    # 历史记录路由
    path("history/<int:student_id>/", ExerciseHistoryView.as_view(), name="exercise-history"),
]