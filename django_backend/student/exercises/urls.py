from django.urls import path
from .views import (
    GenerateExerciseView,
    EvaluateAnswerView,
    ExerciseHistoryView,
    SubmitExerciseView
)

urlpatterns = [
    path('generate/', GenerateExerciseView.as_view()),
    path('evaluate/', EvaluateAnswerView.as_view()),
    path('history/<int:student_id>/', ExerciseHistoryView.as_view()),
    path('submit/', SubmitExerciseView.as_view()),  # 合并提交和评估
]