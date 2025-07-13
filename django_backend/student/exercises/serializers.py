from rest_framework import serializers
from .models import (
    KnowledgePoint,
    Exercise,
    Document,
    StudentProfile,
    ExerciseAttempt
)
from django.contrib.auth import get_user_model

User = get_user_model()

class KnowledgePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgePoint
        fields = [
            'id', 
            'name', 
            'description',
            'parent',
            'prerequisite',
            'difficulty_level'
        ]
        read_only_fields = ['id']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'document_type',
            'file',
            'summary',
            'upload_date'
        ]
        read_only_fields = ['id', 'upload_date']

class ExerciseSerializer(serializers.ModelSerializer):
    knowledge_points = KnowledgePointSerializer(many=True, read_only=True)
    source_document = DocumentSerializer(read_only=True)
    
    class Meta:
        model = Exercise
        fields = [
            'id',
            'title',
            'content',
            'question_type',
            'source_document',
            'answer',
            'solution_steps',
            'explanation',
            'difficulty',
            'calculated_difficulty',
            'knowledge_points',
            'hints',
            'common_mistakes',
            'feedback_template',
            'created_at',
            'updated_at',
            'is_active'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'calculated_difficulty'
        ]

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        read_only_fields = fields

class ExerciseAttemptSerializer(serializers.ModelSerializer):
    student = UserSimpleSerializer(read_only=True)
    exercise = ExerciseSerializer(read_only=True)
    attempt_id = serializers.IntegerField(source='id')  # 添加字段映射
    
    class Meta:
        model = ExerciseAttempt
        fields = [
            'attempt_id',  # 新增字段
            'id',
            'student',
            'exercise',
            'student_answer',
            'attempt_number',
            'time_spent',
            'used_hints',
            'is_correct',
            'score',
            'partial_scores',
            'feedback',
            'detailed_feedback',
            'ai_feedback',
            'feedback_rating',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'is_correct',
            'score',
            'partial_scores'
        ]
    
    def validate_attempt_number(self, value):
        """验证尝试次数"""
        if value < 1:
            raise serializers.ValidationError("尝试次数必须大于0")
        return value

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    knowledge_mastery = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'knowledge_mastery',
            'skill_distribution',
            'learning_style',
            'preferred_difficulty',
            'total_exercises',
            'correct_rate',
            'avg_time_per_question',
            'last_updated'
        ]
        read_only_fields = [
            'id',
            'total_exercises',
            'correct_rate',
            'avg_time_per_question',
            'last_updated'
        ]
    
    def get_knowledge_mastery(self, obj):
        """格式化知识点掌握度数据"""
        from .models import KnowledgePoint
        mastery_data = obj.knowledge_mastery or {}
        
        # 获取所有相关知识点
        kp_ids = mastery_data.keys()
        knowledge_points = KnowledgePoint.objects.filter(id__in=kp_ids)
        
        # 构建响应数据
        return {
            str(kp.id): {
                'name': kp.name,
                'mastery_score': mastery_data.get(str(kp.id), 0),
                'difficulty_level': kp.difficulty_level
            }
            for kp in knowledge_points
        }