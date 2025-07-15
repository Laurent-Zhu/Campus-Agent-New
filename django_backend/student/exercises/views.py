from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.core.exceptions import ObjectDoesNotExist

from student.exercises.models import Exercise, ExerciseAttempt, KnowledgePoint, StudentProfile
from student.exercises.serializers import ExerciseAttemptSerializer, ExerciseSerializer
from .services import exercise_generator, evaluator

from django.db import transaction  

User = get_user_model()

import logging

# 初始化日志
logger = logging.getLogger(__name__)

class GenerateExerciseView(APIView):
    serializer_class = ExerciseSerializer

    def post(self, request):
        # ===== 1. 从中间件获取已验证的用户信息（关键调整：从 request.user 提取）=====
        # 检查是否通过中间件认证
        if not hasattr(request, 'user') or not request.user:
            logger.warning("未认证用户尝试访问生成题目接口")
            return Response(
                {'error': '未提供有效认证'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ===== 2. 验证用户角色和信息完整性 =====
        # 从中间件返回的 user_data 中提取必要字段（user_id、role）
        user_id = request.user.get('user_id')  # 对应 FastAPI 验证接口返回的 user_id
        role = request.user.get('role')

        # 检查用户信息是否完整
        if not user_id or not role:
            logger.error("中间件返回的用户信息不完整")
            return Response(
                {'error': '认证信息无效'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 验证是否为学生角色
        if role != 'student':
            logger.warning(f"非学生用户（角色：{role}，ID：{user_id}）尝试生成题目")
            return Response(
                {'error': '仅限学生用户访问'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # ===== 3. 参数处理（使用中间件验证后的可信 user_id）=====
        data = request.data.copy()
        try:
            # 强制使用中间件验证后的 user_id（防止前端篡改）
            trusted_student_id = user_id  # 直接使用中间件返回的 user_id
            
            # 验证用户在数据库中是否存在
            try:
                # 假设你的用户模型是 User，且 ID 为字符串或整数类型
                student = User.objects.get(id=trusted_student_id)
            except User.DoesNotExist:
                logger.error(f"用户 ID {trusted_student_id} 在数据库中不存在")
                return Response(
                    {'error': f'用户不存在'},  # 不暴露具体 ID，避免信息泄露
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # 透传学生 ID 到参数（可选，用于后续逻辑）
            data['student_id'] = str(trusted_student_id)
            
            # 验证必要参数（难度）
            required_fields = ['difficulty']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return Response(
                    {'error': f'缺少必要参数: {", ".join(missing_fields)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 验证知识点存在性（如果有）
            knowledge_point_ids = data.get('knowledge_point_ids', [])
            if knowledge_point_ids:
                # 假设 KnowledgePoint 的 ID 是整数，需先转换为整数列表（避免字符串匹配问题）
                try:
                    kp_ids_int = [int(kp_id) for kp_id in knowledge_point_ids]
                except ValueError:
                    return Response(
                        {'error': '知识点 ID 必须为整数'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                existing_kps = KnowledgePoint.objects.filter(id__in=kp_ids_int)
                if existing_kps.count() != len(kp_ids_int):
                    # 计算不存在的知识点 ID
                    existing_ids = {kp.id for kp in existing_kps}
                    invalid_ids = [str(kp_id) for kp_id in kp_ids_int if kp_id not in existing_ids]
                    return Response(
                        {'error': f'知识点不存在: {", ".join(invalid_ids)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # ===== 4. 生成题目 =====
            logger.info(f"开始为学生 {trusted_student_id} 生成题目，难度: {data['difficulty']}")
            try:
                exercise = exercise_generator.generate_personalized_exercise(
                    student_id=trusted_student_id,
                    difficulty=data['difficulty'],
                    knowledge_point_ids=knowledge_point_ids
                )
            except Exception as e:
                logger.error(f"题目生成服务错误: {str(e)}", exc_info=True)
                return Response(
                    {'error': '题目生成失败'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
            logger.info(f"题目生成成功，ID: {exercise.id}")
            
            # ===== 5. 返回响应 =====
            return Response({
                'exercise_id': exercise.id,
                'title': exercise.title,
                'content': exercise.content,
                'question_type': exercise.question_type,
                'hints': exercise.hints if hasattr(exercise, 'hints') else None,
                'difficulty': exercise.difficulty,
                'knowledge_points': [kp.name for kp in exercise.knowledge_points.all()],
                'meta': {
                    'student_id_used': trusted_student_id,
                    'auth_source': 'fastapi_jwt'  # 明确标识认证来源
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"参数错误: {str(e)}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST  # 修正笔误：BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"题目生成失败 - 学生ID {trusted_student_id}: {str(e)}", exc_info=True)
            return Response(
                {'error': '服务器内部错误'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class EvaluateAnswerView(APIView):
    serializer_class = ExerciseAttemptSerializer

    def post(self, request):
        try:
            # 1. 验证必要参数
            required_fields = ['exercise_id', 'student_id', 'student_answer']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {'error': f'缺少必要参数: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # 2. 评估答案
            result = evaluator.evaluate_answer(
                exercise_id=request.data['exercise_id'],
                student_id=request.data['student_id'],
                student_answer=request.data['student_answer']
            )
            
            # 3. 确保返回结果包含 detailed_feedback
            response_data = {
                'is_correct': result.get('is_correct', False),
                'score': result.get('score', 0),
                'feedback': result.get('feedback', ''),
                'detailed_feedback': result.get('detailed_feedback', {}),  # 确保有这个字段
                'correct_answer': result.get('correct_answer', ''),
                'attempt_id': result.get('attempt_id')  # 如果有的话
            }

            # 4. 更新学生能力画像
            self._update_student_profile(
                student_id=request.data['student_id'],
                is_correct=response_data['is_correct'],
                time_spent=request.data.get('time_spent', 0)
            )
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _update_student_profile(self, student_id, is_correct, time_spent):
        """更新学生能力画像"""
        profile, _ = StudentProfile.objects.get_or_create(user_id=student_id)
        profile.update_stats()






class ExerciseHistoryView(APIView):
    serializer_class = ExerciseAttemptSerializer 

    def get(self, request, student_id):
        try:
            # 验证学生是否存在
            User.objects.get(id=student_id)
            
            attempts = ExerciseAttempt.objects.filter(
                student_id=student_id
            ).select_related('exercise').order_by('-created_at','-id')[:100]
            
            serializer = ExerciseAttemptSerializer(attempts, many=True)
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
    serializer_class = ExerciseAttemptSerializer

    def post(self, request):
        data = request.data
        
        try:
            # 1. 验证必要参数
            required_fields = ['student_id', 'exercise_id', 'student_answer']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return Response(
                    {'error': f'缺少必要参数: {", ".join(missing_fields)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. 验证学生和练习存在
            try:
                student = User.objects.get(id=data['student_id'])
                exercise = Exercise.objects.get(id=data['exercise_id'])
            except User.DoesNotExist:
                return Response(
                    {'error': '学生不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exercise.DoesNotExist:
                return Response(
                    {'error': '练习不存在'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 3. 确保学生档案存在
            StudentProfile.objects.get_or_create(user=student)

            # 4. 计算尝试次数（使用原子操作避免竞争条件）
            with transaction.atomic():
                attempt_number = ExerciseAttempt.objects.filter(
                    student=student,
                    exercise=exercise
                ).count() + 1

                # 5. 评估答案
                evaluation_result = self._evaluate_answer(exercise, data['student_answer'])

                # 6. 创建练习尝试记录（严格匹配模型字段）
                attempt = ExerciseAttempt.objects.create(
                    student=student,
                    exercise=exercise,
                    student_answer=data['student_answer'],
                    attempt_number=attempt_number,
                    time_spent=data.get('time_spent', 0),
                    used_hints=data.get('used_hints', []),
                    is_correct=evaluation_result['is_correct'],
                    score=evaluation_result.get('score', 0.0),
                    feedback=evaluation_result.get('feedback', ''),
                    detailed_feedback=evaluation_result.get('detailed_feedback', {})
                )

            # 7. 更新学生统计数据
            self._update_student_stats(student, attempt.is_correct)

            # 8. 返回响应
            serializer = ExerciseAttemptSerializer(attempt)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"提交练习失败: {str(e)}", exc_info=True)
            return Response(
                {'error': '服务器内部错误: ' + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _evaluate_answer(self, exercise, student_answer):
        """评估答案并返回完整结果"""
        try:
            # 从练习中获取参考答案
            reference_answer = exercise.answer.get('reference_answer') if isinstance(exercise.answer, dict) else exercise.answer
            
            is_correct = str(reference_answer) == str(student_answer)
            return {
                'is_correct': is_correct,
                'score': 1.0 if is_correct else 0.0,
                'feedback': '答案正确' if is_correct else f'正确答案: {reference_answer}',
                'detailed_feedback': {
                    'expected': str(reference_answer),
                    'provided': str(student_answer),
                    'is_correct': is_correct
                }
            }
        except Exception as e:
            logger.error(f"答案评估失败: {str(e)}")
            return {
                'is_correct': False,
                'score': 0.0,
                'feedback': '评估答案时出错',
                'detailed_feedback': {'error': str(e)}
            }

    def _update_student_stats(self, student, is_correct):
        """更新学生统计数据"""
        try:
            profile = StudentProfile.objects.get(user=student)
            profile.total_exercises += 1
            if is_correct:
                profile.correct_count = getattr(profile, 'correct_count', 0) + 1
            profile.correct_rate = profile.correct_count / profile.total_exercises
            profile.save()
        except Exception as e:
            logger.error(f"更新学生统计失败: {str(e)}")