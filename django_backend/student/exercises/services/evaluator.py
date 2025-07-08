import difflib
from django.db import transaction

from student.exercises.models import Exercise, StudentExerciseLog, StudentProfile
from django.contrib.auth import get_user_model

User = get_user_model()



def evaluate_answer(exercise_id, student_id, student_answer):
    try:
        # 1. 获取题目和学生信息（添加异常处理）
        exercise = Exercise.objects.get(id=exercise_id)
        student = User.objects.get(id=student_id)
        profile, created = StudentProfile.objects.get_or_create(user=student)
        
        # 2. 对比答案
        is_correct, feedback = simple_code_compare(
            student_answer, 
            exercise.answer.get('reference_answer', '')
        )
        
        # 3. 记录结果并更新学生画像（原子操作）
        with transaction.atomic():
            log = StudentExerciseLog.objects.create(
                student=student,
                exercise=exercise,
                student_answer=student_answer,
                is_correct=is_correct,
                feedback=feedback
            )
            
            # 更新学生薄弱知识点
            if not is_correct:
                for kp in exercise.knowledge_points.all():
                    profile.weak_knowledge_points.add(kp)
        
        return {
            'is_correct': is_correct,
            'feedback': feedback,
            'correct_answer': exercise.answer.get('reference_answer', '')
        }
        
    except Exercise.DoesNotExist:
        return {
            'error': '题目不存在',
            'is_correct': False,
            'feedback': '指定的题目不存在或已被删除'
        }
    except User.DoesNotExist:
        return {
            'error': '用户不存在',
            'is_correct': False,
            'feedback': '用户信息无效'
        }
    except KeyError as e:
        return {
            'error': '题目数据不完整',
            'is_correct': False,
            'feedback': f'缺少必要字段: {str(e)}'
        }



def simple_code_compare(student_code, reference_code):
    """简单代码对比（实际项目应集成大模型API）"""
    diff = difflib.ndiff(
        student_code.splitlines(), 
        reference_code.splitlines()
    )
    diff_text = '\n'.join(diff)
    similarity = difflib.SequenceMatcher(
        None, student_code, reference_code
    ).ratio()
    
    is_correct = similarity > 0.8
    feedback = f"代码匹配度：{similarity:.2f}\n差异对比：\n{diff_text}" if not is_correct else ""
    return is_correct, feedback