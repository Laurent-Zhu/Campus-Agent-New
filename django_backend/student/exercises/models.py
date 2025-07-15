from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User
from django.forms import ValidationError



class KnowledgePoint(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='children'
    )
    prerequisite = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        blank=True,
        related_name='required_by'
    )    
    difficulty_level = models.FloatField(default=0.5)
    related_documents = models.ManyToManyField(
        'Document', 
        blank=True,
        related_name='knowledge_points'
    )

    def __str__(self):
        return self.name

class Document(models.Model):
    DOCUMENT_TYPES = [
        ('textbook', '教材'),
        ('lecture', '讲义'),
        ('paper', '论文'),
        ('example', '案例'),
        ('other', '其他')
    ]

    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    content = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Exercise(models.Model):
    DIFFICULTY_CHOICES = [('easy', '简单'), ('medium', '中等'), ('hard', '困难')]
    QUESTION_TYPES = [
        ('mc', '选择题'),
        ('tf', '判断题'),
        ('fb', '填空题'),
        ('code', '编程题'),
        ('doc', '文档分析题')
    ]
    EXERCISE_TYPE_CHOICES = [
        ('knowledge', '知识点巩固'),
        ('weakness', '弱点专项'),
        ('simulation', '模拟测试'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mc')
    source_document = models.ForeignKey(
        Document, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    
    answer = models.JSONField(default=dict)
    solution_steps = models.JSONField(default=list)
    explanation = models.TextField(blank=True)

    calculated_difficulty = models.FloatField(default=0.5)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    knowledge_points = models.ManyToManyField(
        KnowledgePoint,
        related_name='exercises'
    )
    exercise_type = models.CharField(
        max_length=20, 
        choices=EXERCISE_TYPE_CHOICES, 
        default='knowledge',  # 默认知识点巩固
        help_text='练习类型：知识点巩固、弱点专项、模拟测试'
    )

    hints = models.JSONField(default=list)
    common_mistakes = models.JSONField(default=list)
    feedback_template = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if 'reference_answer' not in self.answer:
            raise ValidationError("answer必须包含reference_answer字段")

class StudentProfile(models.Model):
    fastapi_user_id = models.IntegerField(unique=True)  # 存储 FastAPI 的 user_id
    username = models.CharField(max_length=100)  # 存储 FastAPI 的 username

    weak_knowledge_points = models.ManyToManyField(
        KnowledgePoint,
        blank=True,
        related_name='weak_student_profiles'
    )

    knowledge_mastery = models.JSONField(default=dict)
    skill_distribution = models.JSONField(default=dict)
    learning_style = models.CharField(max_length=50, blank=True)
    preferred_difficulty = models.FloatField(default=0.5)
    correct_count = models.IntegerField(default=0)
    total_exercises = models.IntegerField(default=0)
    correct_rate = models.FloatField(default=0)
    avg_time_per_question = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def update_stats(self):
        logs = self.user.exercise_attempts.all()

        self.total_exercises = logs.count()
        self.correct_count = logs.filter(is_correct=True).count()

        if self.total_exercises > 0:
            self.correct_rate = self.correct_count / self.total_exercises
            self.avg_time_per_question = logs.aggregate(
                avg_time=Avg('time_spent')
            )['avg_time'] or 0
        
        self.save()

class ExerciseAttempt(models.Model):
    fastapi_user_id = models.IntegerField()
    username = models.CharField(max_length=100)  # 存储 FastAPI 的 username

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    student_answer = models.JSONField()
    attempt_number = models.PositiveIntegerField(default=1)
    time_spent = models.PositiveIntegerField(default=0)
    used_hints = models.JSONField(default=list)
    
    is_correct = models.BooleanField()
    score = models.FloatField(null=True, blank=True)
    partial_scores = models.JSONField(null=True, blank=True)
    
    feedback = models.TextField(blank=True)
    detailed_feedback = models.JSONField(default=dict)
    ai_feedback = models.TextField(blank=True)
    feedback_rating = models.SmallIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['fastapi_user_id', 'exercise', 'attempt_number']]
        verbose_name = '练习记录'
        verbose_name_plural = '练习记录'

    def __str__(self):
        return f"{self.student.username} 第{self.attempt_number}次尝试 {self.exercise.title}"