from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from student.exercises.models import (
    KnowledgePoint,
    Exercise,
    StudentExerciseLog,
    StudentProfile,
    ExerciseHistory
)
from django.core.exceptions import ValidationError


# 测试知识点模型
class KnowledgePointModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kp1 = KnowledgePoint.objects.create(
            name="Python基础",
            description="Python语法基础知识点"
        )

    # 验证知识点创建和字段值
    def test_knowledge_point_creation(self):
        self.assertEqual(self.kp1.name, "Python基础")
        self.assertEqual(self.kp1.description, "Python语法基础知识点")

    # 检查名称字段的最大长度限制
    def test_name_max_length(self):
        max_length = self.kp1._meta.get_field('name').max_length
        self.assertEqual(max_length, 100)

    # 验证__str__方法返回知识点名称
    def test_str_representation(self):
        self.assertEqual(str(self.kp1), "Python基础")


# 测试练习题模型
class ExerciseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.kp1 = KnowledgePoint.objects.create(name="循环结构")
        cls.exercise = Exercise.objects.create(
            question="Python中如何定义for循环？",
            answer={
                "correct": "for x in iterable:",
                "options": [
                    "for x in range:",
                    "for x in iterable:",
                    "foreach x in iterable:"
                ]
            },
            difficulty="medium"
        )
        cls.exercise.knowledge_points.add(cls.kp1)

    def test_exercise_creation(self):
        self.assertEqual(self.exercise.question, "Python中如何定义for循环？")
        self.assertEqual(self.exercise.difficulty, "medium")
        self.assertTrue(self.exercise.knowledge_points.exists())

    def test_answer_json_field(self):
        self.assertIsInstance(self.exercise.answer, dict)
        self.assertIn("correct", self.exercise.answer)

    def test_difficulty_choices(self):
        field = self.exercise._meta.get_field('difficulty')
        self.assertEqual(field.choices, [('easy', '简单'), ('medium', '中等'), ('hard', '困难')])

    def test_invalid_difficulty(self):
        exercise = Exercise(
            question="Test",
            answer={},
            difficulty="invalid"
        )
        with self.assertRaises(ValidationError):
            exercise.full_clean()


# 测试学生练习记录
class StudentExerciseLogModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="12345")
        cls.kp = KnowledgePoint.objects.create(name="函数")
        cls.exercise = Exercise.objects.create(
            question="如何定义函数？",
            answer={"correct": "def func(): pass"},
            difficulty="easy"
        )
        cls.log = StudentExerciseLog.objects.create(
            student=cls.user,
            exercise=cls.exercise,
            student_answer={"answer": "def func(): pass"},
            is_correct=True,
            feedback="回答正确！"
        )

    def test_log_creation(self):
        self.assertEqual(self.log.student.username, "testuser")
        self.assertEqual(self.log.exercise.question, "如何定义函数？")
        self.assertTrue(self.log.is_correct)

    def test_student_answer_json(self):
        self.assertIsInstance(self.log.student_answer, dict)
        self.assertIn("answer", self.log.student_answer)

    def test_foreign_key_relationships(self):
        self.assertEqual(self.log.student.exercise_logs.first(), self.log)
        self.assertEqual(self.log.exercise.studentexerciselog_set.first(), self.log)

    def test_timestamp_auto_now_add(self):
        self.assertIsNotNone(self.log.timestamp)


# 测试学生档案
class StudentProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建测试数据
        cls.user = User.objects.create_user(username="profile_test", password="12345")
        cls.profile = StudentProfile.objects.create(user=cls.user, average_score=85.5)
        cls.kp1 = KnowledgePoint.objects.create(name="面向对象")
        cls.kp2 = KnowledgePoint.objects.create(name="异常处理")
        cls.profile.weak_knowledge_points.add(cls.kp1, cls.kp2)

    def test_profile_creation(self):
        """测试学生档案创建"""
        self.assertEqual(self.profile.user.username, "profile_test")
        self.assertEqual(self.profile.average_score, 85.5)

    def test_one_to_one_relationship(self):
        """测试一对一关系"""
        self.assertEqual(self.user.studentprofile, self.profile)

    def test_weak_knowledge_points(self):
        """测试薄弱知识点关联"""
        self.assertEqual(self.profile.weak_knowledge_points.count(), 2)
        self.assertEqual(
            list(self.profile.weak_knowledge_points.values_list('name', flat=True)),
            ["面向对象", "异常处理"]
        )

    def test_average_score_default(self):
        """测试平均分默认值"""
        new_user = User.objects.create(username="new_test_user")
        new_profile = StudentProfile.objects.create(user=new_user)
        self.assertEqual(new_profile.average_score, 0)  # 修正为完整的assertEqual
        # 或者如果模型中有不同的默认值，使用相应的值
        # self.assertEqual(new_profile.average_score, 0.0)

    def test_str_representation(self):
        """测试字符串表示"""
        self.assertEqual(str(self.profile), "profile_test的档案")