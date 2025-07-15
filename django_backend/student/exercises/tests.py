# tests.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.conf import settings
from student.exercises.services.llm_service import LLMService
import os
import json

class LLMServiceTestCase(TestCase):
    def setUp(self):
        self.real_api_key = os.getenv('ZHIPUAI_API_KEY', getattr(settings, 'ZHIPUAI_API_KEY', None))
    
    def test_generate_question_with_real_api(self):
        """测试真实API调用"""
        if not self.real_api_key:
            self.skipTest("未配置有效的ZHIPUAI_API_KEY，跳过真实API测试")
            
        llm = LLMService(api_key=self.real_api_key)
        try:
            # 使用更简单的测试数据
            result = llm.generate_question(
                student_data={"correct_rate": 0.5, "weak_points": ["代数"]},
                difficulty="easy",
                knowledge_point_ids=[1]
            )
            
            # 验证基本结构
            self.assertIsInstance(result, dict)
            for key in ["title", "question", "answer"]:
                self.assertIn(key, result)
                self.assertIsInstance(result[key], str)
                self.assertTrue(result[key].strip())
            
            print("\n真实API测试通过，生成结果：")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        except Exception as e:
            self.fail(f"真实API调用失败: {str(e)}")

    @patch('student.exercises.services.llm_service.ZhipuAI')
    def test_generate_question_with_mock(self, mock_zhipuai):
        """模拟API测试"""
        # 设置模拟响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "title": "模拟测试题",
            "question": "1 + 1等于多少？",
            "answer": "2"
        })
        
        # 设置模拟客户端
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_zhipuai.return_value = mock_client
        
        # 测试
        llm = LLMService(api_key="mock_key")
        result = llm.generate_question(
            student_data={"correct_rate": 0.5, "weak_points": ["算术"]},
            difficulty="easy",
            knowledge_point_ids=[1]
        )
        
        # 验证
        self.assertEqual(result["title"], "模拟测试题")
        self.assertEqual(result["question"], "1 + 1等于多少？")
        self.assertEqual(result["answer"], "2")