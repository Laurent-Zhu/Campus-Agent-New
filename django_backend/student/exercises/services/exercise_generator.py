from django.db.models import Q
import random

from models.database import User

def generate_personalized_exercise(student_id, difficulty=None, knowledge_point_ids=None):
    from ..models import Exercise, StudentExerciseLog, StudentProfile
    
    student = User.objects.get(id=student_id)
    
    # 1. 自动推断难度（如果没有显式指定）
    if not difficulty:
        profile = StudentProfile.objects.get(user=student)
        difficulty = 'easy' if profile.average_score < 60 else 'hard'
    
    # 2. 过滤题目（排除最近做过的）
    recent_exercises = StudentExerciseLog.objects.filter(
        student=student
    ).values_list('exercise_id', flat=True)[:10]
    
    # 3. 优先选择薄弱知识点题目
    queryset = Exercise.objects.filter(difficulty=difficulty)
    if knowledge_point_ids:
        queryset = queryset.filter(knowledge_points__id__in=knowledge_point_ids)
    else:
        weak_points = student.studentprofile.weak_knowledge_points.all()
        if weak_points.exists():
            queryset = queryset.filter(knowledge_points__in=weak_points)
    
    # 4. 随机选择一道题
    exercise = random.choice(list(queryset))
    return exercise