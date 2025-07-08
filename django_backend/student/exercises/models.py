from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

# 知识点分类（如编程、数学）
class KnowledgePoint(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

# 练习题模型
class Exercise(models.Model):
    DIFFICULTY_CHOICES = [('easy', '简单'), ('medium', '中等'), ('hard', '困难')]
    
    question = models.TextField()  # 题目内容（支持Markdown）
    answer = models.JSONField()    # 结构化答案（如选择题选项+正确答案）
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    knowledge_points = models.ManyToManyField(KnowledgePoint)
    created_at = models.DateTimeField(auto_now_add=True)

# 学生练习记录
class StudentExerciseLog(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
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

# 学生历史记录
class ExerciseHistory(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    exercise = models.ForeignKey('Exercise', on_delete=models.CASCADE)
    submitted_answer = models.JSONField()
    is_correct = models.BooleanField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']    
