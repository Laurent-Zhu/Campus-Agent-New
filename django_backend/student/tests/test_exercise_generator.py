from django.test import TestCase
from unittest.mock import patch
from student.exercises.services.exercise_generator import generate_personalized_exercise
from student.exercises.models import Exercise, StudentProfile, KnowledgePoint
from django.contrib.auth import get_user_model

User = get_user_model()

class TestExerciseGenerator(TestCase):
    @classmethod
    def setUpTestData(cls):
        """初始化测试数据（替代 pytest fixture）"""
        # 创建测试学生
        cls.student = User.objects.create(username="test_student")
        cls.profile = StudentProfile.objects.create(
            user=cls.student,
            average_score=75
        )
        # 创建薄弱知识点
        cls.kp = KnowledgePoint.objects.create(name="代数")
        cls.profile.weak_knowledge_points.add(cls.kp)
        
        # 创建预置题目（替代 preset_exercises）
        cls.ex1 = Exercise.objects.create(
            question="预置题目1",
            difficulty="easy",
            answer={"options": ["A", "B"], "correct_answer": "A"}
        )
        cls.ex2 = Exercise.objects.create(
            question="预置题目2",
            difficulty="hard",
            answer={"options": ["C", "D"], "correct_answer": "D"}
        )
        cls.preset_exercises = [cls.ex1, cls.ex2]

    def test_fallback_to_database(self):
        """测试LLM失败时降级到数据库题目"""
        with patch('services.llm_service.LLMService.generate_question', side_effect=Exception("Mock Error")):
            exercise = generate_personalized_exercise(self.student.id)
            self.assertIn(exercise, self.preset_exercises)

    def test_llm_generation_success(self):
        """测试LLM生成成功场景"""
        mock_response = {
            "question": "LLM生成的问题",
            "options": ["A", "B", "C"],
            "answer": "B",
            "explanation": "测试解析"
        }
        with patch('services.llm_service.LLMService.generate_question', return_value=mock_response):
            exercise = generate_personalized_exercise(self.student.id)
            self.assertEqual(exercise.question, "LLM生成的问题")
            self.assertTrue(exercise.is_custom)

    def test_difficulty_auto_selection(self):
        """测试难度自动推断"""
        # 测试低分学生
        self.profile.average_score = 50
        self.profile.save()
        exercise = generate_personalized_exercise(self.student.id)
        self.assertEqual(exercise.difficulty, "easy")