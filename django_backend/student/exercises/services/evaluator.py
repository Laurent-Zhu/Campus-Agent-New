import difflib
from django.db import transaction

from models.database import User

def evaluate_answer(exercise_id, student_id, student_answer):
    from ..models import Exercise, StudentExerciseLog, StudentProfile
    
    exercise = Exercise.objects.get(id=exercise_id)
    student = User.objects.get(id=student_id)
    
    # 1. 对比答案（简单实现，实际可调用大模型API）
    is_correct, feedback = simple_code_compare(
        student_answer, 
        exercise.answer['reference_answer']
    )
    
    # 2. 记录结果并更新学生画像
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
            profile = StudentProfile.objects.get(user=student)
            for kp in exercise.knowledge_points.all():
                profile.weak_knowledge_points.add(kp)
    
    return {
        'is_correct': is_correct,
        'feedback': feedback,
        'correct_answer': exercise.answer['reference_answer']
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