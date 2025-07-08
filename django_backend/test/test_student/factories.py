# tests/factories.py
import factory
from django.contrib.auth.models import User
from exercises.models import KnowledgePoint, Exercise, StudentProfile

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"student_{n}")
    password = factory.PostGenerationMethodCall('set_password', 'test123')

class KnowledgePointFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KnowledgePoint
    
    name = factory.Sequence(lambda n: f"知识点_{n}")
    description = "默认描述"

class ExerciseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exercise
    
    question = "Python中如何反转列表？"
    answer = {
        "reference_answer": "lst[::-1]",
        "options": ["A. lst.reverse()", "B. reversed(lst)", "C. lst[::-1]"],
        "correct_index": 2
    }
    difficulty = "medium"

class StudentProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudentProfile
    
    user = factory.SubFactory(UserFactory)
    average_score = 70.0