from unittest.mock import ANY, patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from student.exercises.models import Exercise, ExerciseHistory, KnowledgePoint
from rest_framework.test import APIClient

from django_backend.student.exercises.services import exercise_generator


class SubmitExerciseIntegrationTest(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='test', password='123')
        self.exercise = Exercise.objects.create(
            question="Test",
            answer={"reference_answer": "42"},
            difficulty="easy"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    @patch('django_backend.student.exercises.services.evaluator.evaluate_answer')
    def test_submit_exercise_success(self, mock_evaluate):
        # 1. 模拟评估结果
        mock_evaluate.return_value = {
            'is_correct': True,
            'feedback': 'Good job!'
        }

        # print(f"Mock配置返回值: {mock_evaluate.return_value}")
        # print(f"Mock是否被调用: {mock_evaluate.called}")

        # 2. 使用reverse获取正确的URL路径
        url = reverse('submit-exercise')  # 使用urls.py中定义的name
        
        # 3. 调用API
        response = self.client.post(url, {
            'exercise_id': self.exercise.id,
            'student_id': self.student.id,
            'student_answer': "42"
        }, format='json')  # 明确指定JSON格式

        # print(f"Mock实际调用参数: {mock_evaluate.call_args}")
        self.assertTrue(mock_evaluate.called)  # 确保mock被调用

        # 4. 验证响应
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['is_correct'])
        
        # 5. 验证数据库记录
        history = ExerciseHistory.objects.first()
        self.assertEqual(history.feedback, 'Good job!')
        
        # 6. 验证mock调用
        mock_evaluate.assert_called_once_with(
            exercise_id=self.exercise.id,
            student_id=self.student.id,
            student_answer="42"
        )



class GenerateExerciseIntegrationTest(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='test', password='123')
        self.kp = KnowledgePoint.objects.create(name='Python', description='...')
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)


    @patch.object(exercise_generator, 'generate_personalized_exercise')
    def test_generate_exercise_success(self, mock_generate):
        # 配置 mock
        mock_exercise = Exercise.objects.create(
            question="测试问题",
            answer={"reference_answer": "答案", "options": ["A", "B"]},
            difficulty="easy"
        )
        mock_exercise.knowledge_points.add(self.kp)
        mock_generate.return_value = mock_exercise

        # 调用 API
        response = self.client.post(reverse('generate-exercise'), {
            'student_id': self.student.id,
            'knowledge_point_ids': [self.kp.id]
        }, format='json')

        # 验证
        self.assertEqual(response.status_code, 200)
        mock_generate.assert_called_once_with(
            student_id=ANY,
            knowledge_point_ids=[self.kp.id],
            difficulty=None
        )




# 测试历史记录查询
class HistoryViewIntegrationTest(APITestCase):
    def setUp(self):

        self.student = User.objects.create_user(username='test', password='123')
        self.exercise = Exercise.objects.create(
            question="Test question",
            answer={"reference_answer": "42"}
        )
        # 创建测试历史记录
        ExerciseHistory.objects.create(
            student=self.student,
            exercise=self.exercise,
            student_answer={"answer": "42"},
            is_correct=True
        )

         # 初始化API客户端
        self.client = APIClient()
        # 模拟用户认证
        self.client.force_authenticate(user=self.student)

    def test_get_history(self):
        response = self.client.get(f'/api/student/history/{self.student.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertTrue(response.data[0]['is_correct'])