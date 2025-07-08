from django.db.models import Q
import random


from student.exercises.models import Exercise, StudentExerciseLog, StudentProfile
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_personalized_exercise(student_id, difficulty=None, knowledge_point_ids=None):
    # 1. 验证难度参数
    valid_difficulties = ['easy', 'medium', 'hard']
    
    try:
        student = User.objects.get(id=student_id)
    except User.DoesNotExist:
        raise ValueError(f"用户ID {student_id} 不存在")
    
     # 2. 自动推断难度（如果没有显式指定）
    if not difficulty:
        try:
            profile = StudentProfile.objects.get(user=student)
            difficulty = 'easy' if profile.average_score < 60 else 'hard'
        except StudentProfile.DoesNotExist:
            difficulty = 'easy'  # 默认难度

    
    # 3. 验证难度是否有效
    if difficulty.lower() not in valid_difficulties:
        raise ValueError(f"无效难度级别: {difficulty}。请使用: {valid_difficulties}")

    # 4. 过滤题目（排除最近做过的）
    recent_exercises = StudentExerciseLog.objects.filter(
        student=student
    ).values_list('exercise_id', flat=True)[:10]
    
    # 5. 构建基础查询集
    queryset = Exercise.objects.filter(difficulty__iexact=difficulty).exclude(
        id__in=recent_exercises
    )
    
    # 6. 应用知识点过滤
    if knowledge_point_ids:
        queryset = queryset.filter(knowledge_points__id__in=knowledge_point_ids)
    else:
        try:
            weak_points = student.studentprofile.weak_knowledge_points.all()
            if weak_points.exists():
                queryset = queryset.filter(knowledge_points__in=weak_points)
        except StudentProfile.DoesNotExist:
            pass  # 如果学生画像不存在，跳过薄弱知识点过滤

    # 7. 检查是否有可用题目
    if not queryset.exists():
        # 尝试放宽条件（不排除最近做过的题目）
        queryset = Exercise.objects.filter(difficulty__iexact=difficulty)
        if knowledge_point_ids:
            queryset = queryset.filter(knowledge_points__id__in=knowledge_point_ids)
        
        if not queryset.exists():
            raise ValueError(f"没有找到符合条件的题目（难度: {difficulty}）")

    # 8. 随机选择一道题
    return random.choice(queryset)