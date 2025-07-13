from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.utils import IntegrityError
from student.exercises.models import (
    KnowledgePoint,
    Document,
    Exercise,
    StudentProfile,
    ExerciseAttempt
)

class KnowledgePointModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.parent_kp = KnowledgePoint.objects.create(
            name="Python基础",
            description="Python基础知识点",
            difficulty_level=0.3
        )
        cls.child_kp = KnowledgePoint.objects.create(
            name="函数",
            description="函数定义与使用",
            parent=cls.parent_kp,
            difficulty_level=0.5
        )

    def test_knowledge_point_creation(self):
        self.assertEqual(self.parent_kp.name, "Python基础")
        self.assertEqual(self.child_kp.parent, self.parent_kp)
        self.assertEqual(self.parent_kp.difficulty_level, 0.3)

    def test_prerequisite_relationship(self):
        kp3 = KnowledgePoint.objects.create(name="面向对象")
        self.child_kp.prerequisite.add(kp3)
        self.assertIn(kp3, self.child_kp.prerequisite.all())
        self.assertIn(self.child_kp, kp3.required_by.all())  # 测试反向关系

    def test_string_representation(self):
        self.assertEqual(str(self.parent_kp), "Python基础")

class DocumentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.document = Document.objects.create(
            title="Python入门指南",
            document_type="textbook",
            content="Python基础语法讲解",
            summary="Python基础入门"
        )

    def test_document_creation(self):
        self.assertEqual(self.document.document_type, "textbook")
        self.assertTrue(self.document.upload_date <= timezone.now())

    def test_document_type_choices(self):
        field = Document._meta.get_field('document_type')
        self.assertEqual(len(field.choices), 5)

    def test_related_knowledge_points(self):
        kp = KnowledgePoint.objects.create(name="Python语法")
        self.document.related_knowledge_points.add(kp)  # 使用正确的related_name
        self.assertIn(kp, self.document.related_knowledge_points.all())

class ExerciseModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.document = Document.objects.create(title="Python练习题集")
        cls.kp1 = KnowledgePoint.objects.create(name="循环结构")
        cls.kp2 = KnowledgePoint.objects.create(name="条件语句")
        
        cls.exercise = Exercise.objects.create(
            title="for循环练习",
            content="Python中如何定义for循环？",
            question_type="code",
            source_document=cls.document,
            answer={
                "reference_answer": "for x in iterable:",
                "options": ["for x in iterable:", "while True:"],
                "explanation": "for循环基本语法"
            },
            solution_steps=["步骤1", "步骤2"],
            difficulty="medium",
            calculated_difficulty=0.6,
            feedback_template="注意冒号的使用"
        )
        cls.exercise.knowledge_points.add(cls.kp1, cls.kp2)

    def test_exercise_creation(self):
        self.assertEqual(self.exercise.question_type, "code")
        self.assertEqual(self.exercise.difficulty, "medium")
        self.assertEqual(len(self.exercise.knowledge_points.all()), 2)

    def test_answer_validation(self):
        # 测试缺少reference_answer的情况
        exercise = Exercise(
            title="无效题目",
            content="测试",
            question_type="mc",
            answer={"wrong_field": "value"}
        )
        with self.assertRaises(ValidationError):
            exercise.full_clean()

    def test_hints_field(self):
        self.exercise.hints = ["提示1", "提示2"]
        self.exercise.save()
        refreshed = Exercise.objects.get(pk=self.exercise.pk)
        self.assertEqual(len(refreshed.hints), 2)

class StudentProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建测试用户
        cls.user = User.objects.create_user(username="testuser")
        cls.profile = StudentProfile.objects.create(user=cls.user)
        
        # 创建测试练习
        cls.exercise1 = Exercise.objects.create(
            title="测试练习1",
            content="内容1",
            question_type="mc",
            answer={"reference_answer": "A"}
        )
        cls.exercise2 = Exercise.objects.create(
            title="测试练习2",
            content="内容2",
            question_type="mc",
            answer={"reference_answer": "B"}
        )
        cls.exercise3 = Exercise.objects.create(  # 新增第三个练习
            title="测试练习3",
            content="内容3",
            question_type="mc",
            answer={"reference_answer": "C"}
        )

    def test_update_stats(self):
        # 创建3条练习记录 (2正确, 1错误)
        # 第一次尝试 - 练习1
        ExerciseAttempt.objects.create(
            student=self.user,
            exercise=self.exercise1,
            student_answer={"answer": "A"},  # 正确答案
            attempt_number=1,  # 明确指定尝试次数
            is_correct=True,
            time_spent=30  # 耗时30秒
        )
        # 第一次尝试 - 练习2
        ExerciseAttempt.objects.create(
            student=self.user,
            exercise=self.exercise2,
            student_answer={"answer": "A"},  # 错误答案
            attempt_number=1,  # 不同练习，可以从1开始
            is_correct=False,
            time_spent=45  # 耗时45秒
        )
        # 第一次尝试 - 练习3
        ExerciseAttempt.objects.create(
            student=self.user,
            exercise=self.exercise3,
            student_answer={"answer": "A"},  # 正确答案
            attempt_number=1,  # 不同练习，可以从1开始
            is_correct=True,
            time_spent=60  # 耗时60秒
        )
        
        # 更新统计信息
        self.profile.update_stats()
        
        # 验证统计结果
        self.assertEqual(self.profile.total_exercises, 3)
        self.assertAlmostEqual(self.profile.correct_rate, 2/3)  # 2/3正确率
        self.assertEqual(self.profile.avg_time_per_question, (30+45+60)/3)  # 平均45秒
        
        # 测试无记录情况
        new_user = User.objects.create(username="newuser")
        new_profile = StudentProfile.objects.create(user=new_user)
        new_profile.update_stats()
        self.assertEqual(new_profile.total_exercises, 0)
        self.assertEqual(new_profile.correct_rate, 0)
        self.assertEqual(new_profile.avg_time_per_question, 0)

    # 添加测试相同练习多次尝试的情况
    def test_multiple_attempts_same_exercise(self):
        # 第一次尝试
        ExerciseAttempt.objects.create(
            student=self.user,
            exercise=self.exercise1,
            student_answer={"answer": "A"},
            attempt_number=1,
            is_correct=True,
            time_spent=20
        )
        # 第二次尝试
        ExerciseAttempt.objects.create(
            student=self.user,
            exercise=self.exercise1,
            student_answer={"answer": "B"},
            attempt_number=2,  # 相同练习，attempt_number递增
            is_correct=False,
            time_spent=30
        )
        
        self.profile.update_stats()
        self.assertEqual(self.profile.total_exercises, 2)
        self.assertEqual(self.profile.correct_rate, 0.5)
        self.assertEqual(self.profile.avg_time_per_question, 25)

class ExerciseAttemptModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="student1")
        cls.exercise = Exercise.objects.create(
            title="测试练习",
            content="问题内容",
            question_type="fb",
            answer={"reference_answer": "正确答案"}
        )
        
        # 第一次尝试
        cls.attempt1 = ExerciseAttempt.objects.create(
            student=cls.user,
            exercise=cls.exercise,
            student_answer={"answer": "学生答案"},
            attempt_number=1,
            time_spent=45,
            is_correct=False,
            score=0.5
        )
        
        # 第二次尝试（相同练习，不同attempt_number）
        cls.attempt2 = ExerciseAttempt.objects.create(
            student=cls.user,
            exercise=cls.exercise,
            student_answer={"answer": "新答案"},
            attempt_number=2,
            time_spent=30,
            is_correct=True,
            score=1.0
        )

    def test_attempt_creation(self):
        self.assertEqual(self.attempt1.attempt_number, 1)
        self.assertEqual(self.attempt2.attempt_number, 2)
        self.assertEqual(self.attempt1.time_spent, 45)
        self.assertFalse(self.attempt1.is_correct)
        self.assertTrue(self.attempt2.is_correct)

    def test_unique_constraint(self):
        # 测试唯一性约束
        with self.assertRaises(IntegrityError):
            ExerciseAttempt.objects.create(
                student=self.user,
                exercise=self.exercise,
                student_answer={},
                attempt_number=1  # 重复的attempt_number
            )

    def test_attempt_number_auto_increment(self):
        new_exercise = Exercise.objects.create(
        title="新练习",
        content="内容",
        question_type="mc",
        answer={"reference_answer": "A"}
        )
        new_attempt = ExerciseAttempt.objects.create(
            student=self.user,
            exercise=new_exercise,  # 使用不同的练习
            student_answer={},
            is_correct=True
        )
        self.assertEqual(new_attempt.attempt_number, 1)  # 因为是新练习，所以是第一次尝试

    def test_relationships(self):
        self.assertEqual(self.user.exercise_attempts.count(), 2)
        self.assertEqual(self.exercise.attempts.count(), 2)
        self.assertEqual(self.attempt1.student, self.user)
        self.assertEqual(self.attempt2.exercise, self.exercise)

    def test_feedback_fields(self):
        self.attempt1.detailed_feedback = {
            "accuracy": 0.8,
            "speed": 0.6,
            "suggestions": ["多练习", "注意细节"]
        }
        self.attempt1.save()
        refreshed = ExerciseAttempt.objects.get(pk=self.attempt1.pk)
        self.assertEqual(refreshed.detailed_feedback["accuracy"], 0.8)