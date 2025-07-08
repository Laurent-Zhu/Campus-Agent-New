from rest_framework import serializers
from .models import ExerciseHistory

class ExerciseHistorySerializer(serializers.ModelSerializer):
    exercise_question = serializers.CharField(source='exercise.question', read_only=True)
    
    class Meta:
        model = ExerciseHistory
        fields = [
            'id',
            'exercise_id',
            'exercise_question',
            'submitted_answer',
            'is_correct',
            'feedback',
            'created_at'
        ]