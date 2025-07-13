import difflib
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from student.exercises.models import Exercise, ExerciseAttempt, StudentProfile, KnowledgePoint
from django.contrib.auth import get_user_model

User = get_user_model()

def evaluate_answer(exercise_id, student_id, student_answer):
    """
    评估学生答案并记录结果
    
    参数:
        exercise_id: 题目ID
        student_id: 学生ID
        student_answer: 学生提交的答案(JSON格式)
        
    返回:
        dict: 包含评估结果和反馈的字典
    """
    try:
        # 1. 获取题目和学生信息
        exercise = Exercise.objects.get(id=exercise_id)
        student = User.objects.get(id=student_id)
        profile, created = StudentProfile.objects.get_or_create(user=student)
        
        # 2. 对比答案
        is_correct, feedback = _evaluate_answers(
            student_answer, 
            exercise.answer.get('reference_answer', ''),
            exercise.question_type
        )
        
        # 3. 计算得分 (根据题目类型可能有不同的计算方式)
        score = 1.0 if is_correct else 0.0
        
        # 4. 记录结果并更新学生画像(原子操作)
        with transaction.atomic():
            attempt_number = ExerciseAttempt.objects.filter(
                student=student,
                exercise=exercise
            ).count() + 1
            
            attempt = ExerciseAttempt.objects.create(
                student=student,
                exercise=exercise,
                student_answer=student_answer,
                attempt_number=attempt_number,
                is_correct=is_correct,
                score=score,
                feedback=feedback,
                detailed_feedback={
                    'similarity': score,
                    'diff': feedback if not is_correct else ''
                }
            )
            
            # 更新学生薄弱知识点
            if not is_correct and exercise.knowledge_points.exists():
                weak_points = list(profile.weak_knowledge_points.all())
                for kp in exercise.knowledge_points.all():
                    if kp not in weak_points:
                        profile.weak_knowledge_points.add(kp)
                
                # 更新知识点掌握度
                knowledge_mastery = profile.knowledge_mastery
                for kp in exercise.knowledge_points.all():
                    kp_id = str(kp.id)
                    current_mastery = knowledge_mastery.get(kp_id, 0.5)  # 默认0.5
                    knowledge_mastery[kp_id] = max(0, current_mastery - 0.1)  # 答错降低掌握度
                
                profile.knowledge_mastery = knowledge_mastery
                profile.save()
        
        return {
            'is_correct': is_correct,
            'score': score,
            'feedback': feedback,
            'correct_answer': exercise.answer.get('reference_answer', ''),
            'attempt_id': attempt.id
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
    except Exception as e:
        return {
            'error': '评估过程中发生错误',
            'is_correct': False,
            'feedback': str(e)
        }

def _evaluate_answers(student_answer, reference_answer, question_type):
    """
    根据题目类型评估答案
    
    参数:
        student_answer: 学生答案
        reference_answer: 参考答案
        question_type: 题目类型
        
    返回:
        tuple: (是否正确, 反馈信息)
    """
    if question_type == 'code':
        # 编程题使用代码对比
        return _compare_code(student_answer, reference_answer)
    elif question_type == 'mc':
        # 选择题直接比较答案
        is_correct = str(student_answer).strip().lower() == str(reference_answer).strip().lower()
        feedback = "" if is_correct else f"正确答案是: {reference_answer}"
        return is_correct, feedback
    elif question_type == 'tf':
        # 判断题
        is_correct = bool(student_answer) == bool(reference_answer)
        feedback = "" if is_correct else f"正确答案是: {'正确' if reference_answer else '错误'}"
        return is_correct, feedback
    else:
        # 其他类型题目使用简单文本对比
        similarity = difflib.SequenceMatcher(
            None, 
            str(student_answer), 
            str(reference_answer)
        ).ratio()
        is_correct = similarity > 0.8
        feedback = f"匹配度: {similarity:.2f}" if not is_correct else ""
        return is_correct, feedback

def _compare_code(student_code, reference_code):
    """代码对比(更精细的实现)"""
    # 标准化代码(移除空格和空行)
    norm_student = '\n'.join(line.strip() for line in str(student_code).splitlines() if line.strip())
    norm_reference = '\n'.join(line.strip() for line in str(reference_code).splitlines() if line.strip())
    
    # 计算相似度
    similarity = difflib.SequenceMatcher(
        None, norm_student, norm_reference
    ).ratio()
    
    # 生成差异报告
    diff = difflib.unified_diff(
        norm_reference.splitlines(),
        norm_student.splitlines(),
        fromfile='reference',
        tofile='student',
        lineterm=''
    )
    diff_text = '\n'.join(diff)
    
    is_correct = similarity > 0.85  # 设置更高的阈值
    feedback = f"代码相似度: {similarity:.2f}\n差异对比:\n{diff_text}" if not is_correct else ""
    
    return is_correct, feedback