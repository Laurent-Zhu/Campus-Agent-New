from rest_framework import serializers
from .models import (
    KnowledgePoint,
    Exercise,
    StudentExerciseLog,
    StudentProfile,
    ExerciseHistory
)
from django.contrib.auth import get_user_model

User = get_user_model()

class KnowledgePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgePoint
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class ExerciseSerializer(serializers.ModelSerializer):
    knowledge_points = KnowledgePointSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exercise
        fields = [
            'id', 
            'question', 
            'answer', 
            'difficulty', 
            'knowledge_points', 
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']

class StudentExerciseLogSerializer(serializers.ModelSerializer):
    student = UserSimpleSerializer(read_only=True)
    exercise = ExerciseSerializer(read_only=True)
    
    class Meta:
        model = StudentExerciseLog
        fields = [
            'id',
            'student',
            'exercise',
            'student_answer',
            'is_correct',
            'feedback',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    weak_knowledge_points = KnowledgePointSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id',
            'user',
            'weak_knowledge_points',
            'average_score'
        ]
        read_only_fields = ['id']

class ExerciseHistorySerializer(serializers.ModelSerializer):
    student = UserSimpleSerializer(read_only=True)
    exercise = ExerciseSerializer(read_only=True)
    
    class Meta:
        model = ExerciseHistory
        fields = [
            'id',
            'student',
            'exercise',
            'submitted_answer',
            'is_correct',
            'feedback',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']