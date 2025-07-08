from typing import Self
from django.test import Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from student.exercises.models import Exercise, ExerciseHistory, KnowledgePoint, StudentProfile
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
            question='Python中如何定义函数？',
            answer={
                'reference_answer': 'def func():',
                'options': [
                    'function func()',
                    'def func():',
                    'func = () ->'
                ],
                'hint': '使用def关键字'
            },
            difficulty='medium'
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
        self.assertIn('question', response.data)
        self.assertIn('options', response.data)
        self.assertEqual(len(response.data['options']), 3)

    def test_generate_with_invalid_difficulty(self):
        url = reverse('generate-exercise')
        data = {
            'student_id': self.student.id,
            'difficulty': 'invalid',
            'knowledge_point_ids': [self.kp1.id]
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EvaluateAnswerViewTest(ExerciseTestBase):
    def test_correct_answer_evaluation(self):
        url = reverse('evaluate-answer')
        data = {
            'exercise_id': self.exercise.id,
            'student_id': self.student.id,
            'student_answer': 'def func():'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_correct'])
        self.assertIn('feedback', response.data)

    def test_incorrect_answer_evaluation(self):
        url = reverse('evaluate-answer')
        data = {
            'exercise_id': self.exercise.id,
            'student_id': self.student.id,
            'student_answer': 'wrong answer'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_correct'])


class ExerciseHistoryViewTest(ExerciseTestBase):
    def setUp(self):
        super().setUp()
        # 创建历史记录
        self.history = ExerciseHistory.objects.create(
            student_id=self.student.id,
            exercise=self.exercise,
            submitted_answer={'answer': 'def func():'},
            is_correct=True,
            feedback='回答正确'
        )

    def test_get_history_success(self):
        url = reverse('exercise-history', args=[self.student.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.history.id)
        self.assertTrue(response.data[0]['is_correct'])

    def test_history_ordering(self):
        
        # 创建更早的记录（明确设置创建时间）
        old_history = ExerciseHistory.objects.create(
            student_id=self.student.id,
            exercise=self.exercise,
            submitted_answer={'answer': 'old answer'},
            is_correct=False,
            feedback='旧记录',
            created_at=timezone.now() - timedelta(days=1)  # 明确设置为1天前
        )
    
     # 新记录使用默认的auto_now_add（当前时间）
        new_history = ExerciseHistory.objects.create(
            student_id=self.student.id,
            exercise=self.exercise,
            submitted_answer={'answer': 'new answer'},
            is_correct=True,
            feedback='新记录'
        )
    
        url = reverse('exercise-history', args=[self.student.id])
        response = self.client.get(url)
    
        # 验证新记录在前
        self.assertEqual(response.data[0]['id'], new_history.id)  # 最新创建的在前
        self.assertEqual(response.data[1]['id'], old_history.id)  # 较早创建的在后





class SubmitExerciseViewTest(ExerciseTestBase):
    def test_submit_exercise_success(self):
        url = reverse('submit-exercise')
        data = {
            'exercise_id': self.exercise.id,
            'student_id': self.student.id,
            'student_answer': 'def func():'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_correct'])
        self.assertIn('history_id', response.data)
        
        # 验证历史记录已创建
        history = ExerciseHistory.objects.get(id=response.data['history_id'])
        self.assertEqual(history.student_id, self.student.id)

    def test_submit_with_invalid_exercise(self):
        url = reverse('submit-exercise')
        data = {
            'exercise_id': 999,  # 不存在的ID
            'student_id': self.student.id,
            'student_answer': 'def func():'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

