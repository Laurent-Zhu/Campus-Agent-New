from django.conf import settings
from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

# 知识点分类（如编程、数学）
class KnowledgePoint(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name  # 返回知识点名称
    
    class Meta:
        app_label = 'exercises'
        db_table = 'exercises_knowledgepoint'


# 练习题模型
class Exercise(models.Model):
    DIFFICULTY_CHOICES = [('easy', '简单'), ('medium', '中等'), ('hard', '困难')]
    
    question = models.TextField()  # 题目内容（支持Markdown）
    answer = models.JSONField(default=dict, help_text="必须包含reference_answer字段")

    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    knowledge_points = models.ManyToManyField(KnowledgePoint)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """验证answer字段结构"""
        super().clean()
        if 'reference_answer' not in self.answer:
            raise ValidationError("answer必须包含reference_answer字段")
        
        

# 学生练习记录
class StudentExerciseLog(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    student_answer = models.JSONField()  # 学生提交的答案
    is_correct = models.BooleanField()
    feedback = models.TextField()       # 系统生成的纠错反馈
    timestamp = models.DateTimeField(auto_now_add=True)

# 学生能力画像
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weak_knowledge_points = models.ManyToManyField(KnowledgePoint)  # 薄弱知识点
    average_score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username}的档案"

# 学生历史记录
class ExerciseHistory(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_histories'
    )
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    submitted_answer = models.JSONField()
    is_correct = models.BooleanField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']    
