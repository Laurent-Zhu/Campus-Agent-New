from typing import Self
from django.test import Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from student.exercises.models import Exercise, ExerciseAttempt, KnowledgePoint, StudentProfile
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()

class ExerciseTestBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        # 创建测试用户
        cls.student = User.objects.create_user(
            username='test_student',
            password='testpass123'
        )

        cls.profile = StudentProfile.objects.create(
            user=cls.student,
        )
        
        # 创建知识点
        cls.kp1 = KnowledgePoint.objects.create(
            name='Python基础',
            description='基础语法'
        )
        cls.kp2 = KnowledgePoint.objects.create(
            name='函数',
            description='函数定义与调用'
        )
        
        # 创建练习题
        cls.exercise = Exercise.objects.create(
            title='Python函数定义',
            content='Python中如何定义函数？',
            question_type='mc',
            answer={
                'reference_answer': 'def func():',
                'options': [
                    'function func()',
                    'def func():',
                    'func = () ->'
                ],
                'explanation': '使用def关键字定义函数'
            },
            difficulty='medium',
            hints=['Python使用def关键字定义函数'],
            feedback_template='注意函数定义语法'
        )
        cls.exercise.knowledge_points.add(cls.kp1)
        
        # 认证
        cls.client.force_authenticate(user=cls.student)

class GenerateExerciseViewTest(ExerciseTestBase):
    def test_generate_exercise_success(self):
        url = reverse('generate-exercise')
        data = {
            'student_id': self.student.id,
            'difficulty': 'medium',
            'knowledge_point_ids': [self.kp1.id]
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('exercise_id', response.data)
        self.assertIn('title', response.data)
        self.assertIn('content', response.data)
        self.assertIn('question_type', response.data)
        self.assertIn('hints', response.data)
        self.assertIn('difficulty', response.data)
        self.assertIn('knowledge_points', response.data)

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
        self.assertIn('error', response.data)

    def test_missing_student_id(self):
        url = reverse('generate-exercise')
        data = {
            'difficulty': 'medium',
            'knowledge_point_ids': [self.kp1.id]
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], '缺少必要参数: student_id')

class EvaluateAnswerViewTest(ExerciseTestBase):
    def test_correct_answer_evaluation(self):
        url = reverse('evaluate-answer')
        data = {
            'exercise_id': self.exercise.id,
            'student_id': self.student.id,
            'student_answer': 'def func():',
            'time_spent': 30
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_correct'])
        self.assertIn('feedback', response.data)
        self.assertIn('score', response.data)
        
        # 验证学生画像已更新
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_exercises, 1)
        self.assertEqual(self.profile.correct_rate, 1.0)

    def test_incorrect_answer_evaluation(self):
        url = reverse('evaluate-answer')
        data = {
            'exercise_id': self.exercise.id,
            'student_id': self.student.id,
            'student_answer': 'wrong answer',
            'time_spent': 45
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_correct'])
        self.assertIn('detailed_feedback', response.data)
        
        # 验证学生画像已更新
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.total_exercises, 1)
        self.assertEqual(self.profile.correct_rate, 0.0)

    def test_missing_required_fields(self):
        url = reverse('evaluate-answer')
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

class ExerciseHistoryViewTest(ExerciseTestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        
        # 创建历史记录 - 使用不同的attempt_number
        cls.history1 = ExerciseAttempt.objects.create(
            student=cls.student,
            exercise=cls.exercise,
            student_answer={'answer': 'def func():'},
            attempt_number=1,  # 明确指定
            is_correct=True,
            score=1.0,
            time_spent=30,
            feedback='回答正确',
            created_at=timezone.now() - timedelta(days=1)
        )
        cls.history2 = ExerciseAttempt.objects.create(
            student=cls.student,
            exercise=cls.exercise,
            student_answer={'answer': 'wrong answer'},
            attempt_number=2,  # 递增
            is_correct=False,
            score=0.0,
            time_spent=45,
            feedback='回答错误',
            created_at=timezone.now()
        )

    def test_get_history_success(self):
        url = reverse('exercise-history', args=[self.student.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # 验证按创建时间降序排列
        self.assertEqual(response.data[0]['id'], self.history2.id)
        self.assertEqual(response.data[1]['id'], self.history1.id)
        # 验证序列化字段
        self.assertIn('exercise', response.data[0])
        self.assertIn('student_answer', response.data[0])
        self.assertIn('is_correct', response.data[0])

    def test_history_limit(self):
    # 创建105条记录，使用不同的exercise和attempt_number组合
        exercises = [
            Exercise.objects.create(
                title=f"练习{i}",
                content=f"内容{i}",
                question_type="mc",
                answer={"reference_answer": "A"}
            ) for i in range(105)
        ]
    
        for i, exercise in enumerate(exercises):
            ExerciseAttempt.objects.create(
                student=self.student,
                exercise=exercise,  # 每个练习都是唯一的
                student_answer={"answer": f"answer {i}"},
                attempt_number=1,  # 因为exercise不同，所以attempt_number可以从1开始
                is_correct=(i % 2 == 0)
            )
    
        url = reverse('exercise-history', args=[self.student.id])
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)  # 验证限制为100条

    def test_nonexistent_user(self):
        url = reverse('exercise-history', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)







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
        self.assertIn('attempt_id', response.data)
        self.assertIn('attempt_number', response.data)
        self.assertEqual(response.data['attempt_number'], 1)
        
        # 验证记录已创建
        attempt = ExerciseAttempt.objects.get(id=response.data['attempt_id'])
        self.assertEqual(attempt.student.id, self.student.id)
        self.assertEqual(attempt.exercise.id, self.exercise.id)
        self.assertEqual(attempt.time_spent, 30)
        self.assertEqual(attempt.used_hints, [1, 2])

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
        self.assertEqual(response.data['attempt_number'], 2)  # 验证尝试次数递增

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
        self.assertEqual(response.data['error'], '缺少必要参数: exercise_id')