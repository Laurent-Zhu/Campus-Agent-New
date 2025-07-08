from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from student.exercises.models import ExerciseHistory
from student.exercises.serializers import ExerciseHistorySerializer
from .services import exercise_generator, evaluator

class GenerateExerciseView(APIView):
    def post(self, request):
        data = request.data
        exercise = exercise_generator.generate_personalized_exercise(
            student_id=data['student_id'],
            difficulty=data.get('difficulty'),
            knowledge_point_ids=data.get('knowledge_point_ids', [])
        )
        return Response({
            'exercise_id': exercise.id,
            'question': exercise.question,
            'options': exercise.answer.get('options', []),
            'hint': exercise.answer.get('hint', '')
        })

class EvaluateAnswerView(APIView):
    def post(self, request):
        result = evaluator.evaluate_answer(
            exercise_id=request.data['exercise_id'],
            student_id=request.data['student_id'],
            student_answer=request.data['student_answer']
        )
        return Response(result)
    
class ExerciseHistoryView(APIView):
    """获取学生的练习历史记录"""
    def get(self, request, student_id):
        histories = ExerciseHistory.objects.filter(
            student_id=student_id
        ).select_related('exercise')[:100]  # 限制最近100条
        serializer = ExerciseHistorySerializer(histories, many=True)
        return Response(serializer.data)

class SubmitExerciseView(APIView):
    """提交练习并记录历史"""
    def post(self, request):
        # 先评估答案
        evaluation_result = evaluator.evaluate_answer(
            exercise_id=request.data['exercise_id'],
            student_id=request.data['student_id'],
            student_answer=request.data['student_answer']
        )
        
        # 保存历史记录
        history = ExerciseHistory.objects.create(
            student_id=request.data['student_id'],
            exercise_id=request.data['exercise_id'],
            submitted_answer=request.data['student_answer'],
            is_correct=evaluation_result['is_correct'],
            feedback=evaluation_result.get('feedback', '')
        )
        
        return Response({
            **evaluation_result,
            'history_id': history.id
        }, status=status.HTTP_201_CREATED)
