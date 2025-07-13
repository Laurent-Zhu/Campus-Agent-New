from django.conf import settings
from django.db import models
from django.db.models import Avg

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

# 知识点分类
class KnowledgePoint(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='children'  # 添加这个
    )
    prerequisite = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        blank=True,
        related_name='required_by'  # 添加这个
    )    
    difficulty_level = models.FloatField(default=0.5)  # 知识点难度系数(0-1)
    related_documents = models.ManyToManyField('Document', blank=True) 

    def __str__(self):
        return self.name  # 返回知识点名称
    
    class Meta:
        app_label = 'exercises'
        db_table = 'exercises_knowledgepoint'


# 练习题模型
class Exercise(models.Model):
    DIFFICULTY_CHOICES = [('easy', '简单'), ('medium', '中等'), ('hard', '困难')]
    QUESTION_TYPES = [
        ('mc', '选择题'),
        ('tf', '判断题'),
        ('fb', '填空题'),
        ('code', '编程题'),
        ('doc', '文档分析题')
    ]

    # 基础信息
    title = models.CharField(max_length=200)
    content = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mc')
    source_document = models.ForeignKey('Document', null=True, blank=True, on_delete=models.SET_NULL)
    
    # 答案与解析
    answer = models.JSONField(default=dict)
    solution_steps = models.JSONField(default=list)  # 解题步骤
    explanation = models.TextField(blank=True)  # 题目解析

    # 难度与知识点
    calculated_difficulty = models.FloatField(default=0.5)  # 系统计算的动态难度(0-1)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    knowledge_points = models.ManyToManyField(KnowledgePoint)

    # 交互与反馈
    hints = models.JSONField(default=list)  # 分步提示
    common_mistakes = models.JSONField(default=list)  # 常见错误及分析
    feedback_template = models.TextField(blank=True)  # 反馈模板

    # 元数据
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        """验证answer字段结构"""
        super().clean()
        if 'reference_answer' not in self.answer:
            raise ValidationError("answer必须包含reference_answer字段")
        
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
    content = models.TextField(blank=True)  # 文本内容(可搜索)
    summary = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)  # 是否已处理(如提取文本等)
    related_knowledge_points = models.ManyToManyField(
        'KnowledgePoint', 
        blank=True,
        related_name='documents_related'  # 添加明确的related_name
    )

    def __str__(self):
        return self.title


# 学生能力画像
class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='studentprofile'  # 添加这个
    )

    weak_knowledge_points = models.ManyToManyField(
        'KnowledgePoint',
        blank=True,
        related_name='weak_for_profiles'
    )

    # 能力指标
    knowledge_mastery = models.JSONField(default=dict)  # 知识点掌握度 {knowledge_id: mastery_score}
    skill_distribution = models.JSONField(default=dict)  # 技能分布

    # 学习行为
    learning_style = models.CharField(max_length=50, blank=True)  # 学习风格
    preferred_difficulty = models.FloatField(default=0.5)  # 偏好难度

    # 统计信息
    correct_count = models.IntegerField(default=0)  # 新增字段
    total_exercises = models.IntegerField(default=0)
    correct_rate = models.FloatField(default=0)
    avg_time_per_question = models.FloatField(default=0)

    last_updated = models.DateTimeField(auto_now=True)

    def update_stats(self):
        """更新统计信息"""
        # 通过user关系获取练习记录
        logs = ExerciseAttempt.objects.filter(student=self.user)

        self.total_exercises = logs.count()
        self.correct_count = logs.filter(is_correct=True).count()

        if self.total_exercises > 0:
            self.correct_rate = self.correct_count / self.total_exercises  # 使用已计算的correct_count
            self.avg_time_per_question = logs.aggregate(
                avg_time=Avg('time_spent')
            )['avg_time'] or 0
        
        self.save()




class ExerciseAttempt(models.Model):
    """合并后的学生练习记录模型"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_attempts'
    )
    exercise = models.ForeignKey(
        'Exercise',
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    # 答题信息
    student_answer = models.JSONField()
    attempt_number = models.PositiveIntegerField(default=1)# 学生对同一练习题的尝试次数
    time_spent = models.PositiveIntegerField(default=0)  # 秒
    used_hints = models.JSONField(default=list)
    
    # 评估结果
    is_correct = models.BooleanField()
    score = models.FloatField(null=True, blank=True)  # 0-1
    partial_scores = models.JSONField(null=True, blank=True)
    
    # 反馈系统
    feedback = models.TextField(blank=True)
    detailed_feedback = models.JSONField(default=dict)
    ai_feedback = models.TextField(blank=True)
    feedback_rating = models.SmallIntegerField(null=True, blank=True)
    
    # 元数据
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['student', 'exercise', 'attempt_number']] # 唯一约束
        verbose_name = '练习记录'
        verbose_name_plural = '练习记录'

    def __str__(self):
        return f"{self.student.username} 第{self.attempt_number}次尝试 {self.exercise.title}"