from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from student.exercises.services import exercise_generator
from student.exercises.models import (
    Exercise, 
    ExerciseAttempt,
    KnowledgePoint,
    StudentProfile,
    Document
)
from rest_framework import status
import json
from unittest.mock import patch, ANY
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ExerciseTestBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # 创建测试用户
        cls.student = User.objects.create_user(
            username='test_student',
            password='testpass123'
        )
        cls.profile = StudentProfile.objects.create(user=cls.student)
        
        # 创建知识点
        cls.kp1 = KnowledgePoint.objects.create(
            name='Python基础',
            description='基础语法'
        )
        
        # 创建文档
        cls.document = Document.objects.create(
            title='Python入门',
            document_type='textbook',
            content='Python基础语法内容'
        )
        
        # 创建练习题
        cls.exercise = Exercise.objects.create(
            title='Python函数定义',
            content='Python中如何定义函数？',
            question_type='mc',
            answer={
                'reference_answer': 'def func():',
                'options': ['function func()', 'def func():', 'func = () ->'],
                'explanation': '使用def关键字定义函数'
            },
            difficulty='medium',
            hints=['Python使用def关键字定义函数'],
            feedback_template='注意函数定义语法'
        )
        cls.exercise.knowledge_points.add(cls.kp1)
        cls.exercise.source_document = cls.document
        cls.exercise.save()
        
        # 初始化客户端
        cls.client = APIClient()
        cls.client.force_authenticate(user=cls.student)

class SubmitExerciseViewTest(ExerciseTestBase):
    def test_submit_exercise_success(self):
        url = reverse('submit-exercise')
        data = {
            'exercise_id': self.exercise.id,
            'student_id': self.student.id,
            'student_answer': 'def func():',
            'time_spent': 30,
            'used_hints': [1, 2]
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_correct'])
        self.assertEqual(response.data['attempt_number'], 1)
        
        # 验证数据库记录
        attempt = ExerciseAttempt.objects.get(id=response.data['id'])
        self.assertEqual(attempt.student.id, self.student.id)
        self.assertEqual(attempt.exercise.id, self.exercise.id)
        self.assertEqual(attempt.time_spent, 30)
        self.assertEqual(attempt.used_hints, [1, 2])
        
        # 验证学生画像更新
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_exercises, 1)
        self.assertEqual(self.profile.correct_count, 1)

    def test_submit_multiple_attempts(self):
        # 第一次提交
        self.client.post(
            reverse('submit-exercise'),
            data=json.dumps({
                'exercise_id': self.exercise.id,
                'student_id': self.student.id,
                'student_answer': 'def func():'
            }),
            content_type='application/json'
        )
        
        # 第二次提交
        response = self.client.post(
            reverse('submit-exercise'),
            data=json.dumps({
                'exercise_id': self.exercise.id,
                'student_id': self.student.id,
                'student_answer': 'function func()'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['attempt_number'], 2)

    def test_submit_with_invalid_exercise(self):
        url = reverse('submit-exercise')
        data = {
            'exercise_id': 999,
            'student_id': self.student.id,
            'student_answer': 'def func():'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields(self):
        url = reverse('submit-exercise')
        data = {
            'student_id': self.student.id,
            'student_answer': 'def func():'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




class GenerateExerciseViewTest(ExerciseTestBase):
    @patch('student.exercises.views.exercise_generator.generate_personalized_exercise')
    def test_generate_exercise_success(self, mock_generate):
        print(f"Mock对象实际路径: {mock_generate._mock_module}")

        # 创建测试练习
        mock_exercise = Exercise.objects.create(
            title='生成的练习',
            content='生成的内容',
            question_type='mc',
            answer={'reference_answer': '答案'},
            difficulty='easy'
        )
        mock_exercise.knowledge_points.add(self.kp1)
        
        # 配置mock
        mock_generate.return_value = mock_exercise

        # 准备请求数据
        url = '/api/student/exercises/generate/'

        data = {
            'student_id': self.student.id,
            'difficulty': 'easy',
            'knowledge_point_ids': [self.kp1.id]
        }
        
        response = self.client.post(
        url,
        data={
            'student_id': self.student.id,
            'difficulty': 'easy',
            'knowledge_point_ids': [self.kp1.id]
        },
        format='json'  # 关键修改点：替换content_type
    )
    
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.content}")
        print(f"Mock调用状态: {mock_generate.called}")
        print(f"Mock调用参数: {mock_generate.call_args if mock_generate.called else '未调用'}")
        
        # 验证响应
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['exercise_id'], mock_exercise.id)
        
        # 验证mock调用
        mock_generate.assert_called_once_with(
            student_id=str(self.student.id),
            knowledge_point_ids=[self.kp1.id],
            difficulty='easy'
        )

    def test_generate_with_invalid_difficulty(self):
        url = reverse('generate-exercise')
        data = {
            'student_id': self.student.id,
            'difficulty': 'invalid',
            'knowledge_point_ids': [self.kp1.id]
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)







class ExerciseHistoryViewTest(ExerciseTestBase):
    def setUp(self):
        super().setUp()
    
    # 清除可能存在的旧数据
        ExerciseAttempt.objects.all().delete()
    
    # 明确设置不同的创建时间（增加时间间隔）
        now = timezone.now()
        self.older_history = ExerciseAttempt.objects.create(
            student=self.student,
            exercise=self.exercise,
            student_answer={'answer': 'def func():'},
            attempt_number=1,
            is_correct=True,
            created_at=now - timedelta(minutes=5)  # 改为5分钟间隔
        )
        self.newer_history = ExerciseAttempt.objects.create(
            student=self.student,
            exercise=self.exercise,
            student_answer={'answer': 'wrong answer'},
            attempt_number=2,
            is_correct=False,
            created_at=now
        )

    def test_get_history_success(self):
        url = reverse('exercise-history', args=[self.student.id])
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    # 直接验证ID顺序（不再依赖时间比较）
        self.assertEqual(response.data[0]['id'], self.newer_history.id)
        self.assertEqual(response.data[1]['id'], self.older_history.id)

    def test_history_limit(self):
        # 创建超过限制的记录
        for i in range(105):
            exercise = Exercise.objects.create(
                title=f'练习{i}',
                content=f'内容{i}',
                question_type='mc',
                answer={'reference_answer': '答案'}
            )
            ExerciseAttempt.objects.create(
                student=self.student,
                exercise=exercise,
                student_answer={'answer': f'答案{i}'},
                attempt_number=1,
                is_correct=True,
                created_at=timezone.now() - timedelta(days=i)  # 确保不同创建时间
            )
        
        url = reverse('exercise-history', args=[self.student.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)  # 验证限制为100条