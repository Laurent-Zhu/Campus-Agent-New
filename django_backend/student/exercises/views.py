from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from student.exercises.models import ExerciseHistory
from student.exercises.serializers import ExerciseHistorySerializer
from .services import exercise_generator, evaluator

from django.contrib.auth import get_user_model
User = get_user_model()

class GenerateExerciseView(APIView):
    def post(self, request):
        data = request.data
        
        try:
            # 1. 验证必要参数
            if 'student_id' not in data:
                return Response(
                    {'error': '缺少必要参数: student_id'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. 尝试生成题目
            exercise = exercise_generator.generate_personalized_exercise(
                student_id=data['student_id'],
                difficulty=data.get('difficulty'),
                knowledge_point_ids=data.get('knowledge_point_ids', [])
            )

            # 3. 成功返回题目数据
            return Response({
                'exercise_id': exercise.id,
                'question': exercise.question,
                'options': exercise.answer.get('options', []),
                'hint': exercise.answer.get('hint', ''),
                'difficulty': exercise.difficulty,
                'knowledge_points': [kp.name for kp in exercise.knowledge_points.all()]
            })

        except ValueError as e:
            # 处理已知的业务逻辑错误
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # 处理其他未预料到的错误
            return Response(
                {'error': '服务器内部错误'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EvaluateAnswerView(APIView):
    def post(self, request):
        result = evaluator.evaluate_answer(
            exercise_id=request.data['exercise_id'],
            student_id=request.data['student_id'],
            student_answer=request.data['student_answer']
        )
        return Response(result)
    
class ExerciseHistoryView(APIView):
    def get(self, request, student_id):
        try:
            # 验证学生是否存在
            User.objects.get(id=student_id)
            
            histories = ExerciseHistory.objects.filter(
                student_id=student_id
            ).select_related('exercise').order_by('-created_at')[:100]
            
            serializer = ExerciseHistorySerializer(histories, many=True)
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {'error': '用户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': '服务器内部错误'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class SubmitExerciseView(APIView):
    """提交练习并记录历史"""
    def post(self, request):
        # 1. 验证必要参数
        required_fields = ['exercise_id', 'student_id', 'student_answer']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {'error': f'缺少必要参数: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        try:
            # 2. 评估答案
            evaluation_result = evaluator.evaluate_answer(
                exercise_id=request.data['exercise_id'],
                student_id=request.data['student_id'],
                student_answer=request.data['student_answer']
            )
            
            # 3. 处理评估错误
            if 'error' in evaluation_result:
                status_code = status.HTTP_404_NOT_FOUND if evaluation_result['error'] == '题目不存在' \
                    else status.HTTP_400_BAD_REQUEST
                return Response(evaluation_result, status=status_code)
            
            # 4. 保存历史记录
            history = ExerciseHistory.objects.create(
                student_id=request.data['student_id'],
                exercise_id=request.data['exercise_id'],
                submitted_answer=request.data['student_answer'],
                is_correct=evaluation_result['is_correct'],
                feedback=evaluation_result.get('feedback', '')
            )
            
            # 5. 成功响应
            return Response({
                **evaluation_result,
                'history_id': history.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # 处理其他未预料到的错误
            return Response(
                {'error': '服务器内部错误', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
