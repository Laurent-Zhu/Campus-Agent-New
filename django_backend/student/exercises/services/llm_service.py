import json
from openai import OpenAI
from typing import Dict, List, Optional
from student.exercises.models import KnowledgePoint

class LLMService:
    def __init__(self, api_key: str = "your_api_key"):
        """
        初始化LLM服务
        :param api_key: OpenAI API密钥
        """
        self.client = OpenAI(api_key=api_key)
        self.default_model = "gpt-4-1106-preview"  # 使用最新模型

    def generate_question(
        self,
        student_data: Dict,
        difficulty: str = "medium",
        knowledge_points: Optional[List[KnowledgePoint]] = None,
        question_type: str = "mc"
    ) -> Dict:
        """
        生成个性化练习题
        
        :param student_data: 学生数据 {id, correct_rate, weak_points}
        :param difficulty: 题目难度 (easy/medium/hard)
        :param knowledge_points: 关联知识点列表
        :param question_type: 题目类型 (mc/tf/fb/code/doc)
        :return: 生成的题目数据
        """
        # 构建知识点描述
        kp_descriptions = []
        if knowledge_points:
            kp_descriptions = [f"{kp.name}（难度: {kp.difficulty_level:.1f}）" for kp in knowledge_points]
        
        prompt = f"""
        根据以下要求生成一道{difficulty}难度的练习题：
        
        学生信息：
        - 正确率: {student_data.get('correct_rate', 0.7):.1%}
        - 薄弱点: {student_data.get('weak_points', [])}
        {f"- 关联知识点: {', '.join(kp_descriptions)}" if kp_descriptions else ""}
        
        题目要求：
        1. 题目类型: {self._get_question_type_desc(question_type)}
        2. 难度级别: {difficulty}
        3. 必须包含详细解析和常见错误分析
        
        返回JSON格式：
        {{
            "title": "题目标题",
            "content": "题目内容",
            "question_type": "{question_type}",
            "difficulty": "{difficulty}",
            "answer": {{
                "reference_answer": "参考答案",
                "options": ["选项A", "选项B", ...],  // 选择题需要
                "explanation": "详细解析",
                "common_mistakes": ["常见错误1", ...]
            }},
            "hints": ["提示1", "提示2"],
            "knowledge_points": ["知识点1", ...]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            # 后处理：确保关键字段存在
            result.setdefault("title", "AI生成题目")
            result["answer"].setdefault("common_mistakes", [])
            result.setdefault("hints", [])
            
            return result
        except Exception as e:
            return {
                "error": str(e),
                "question_type": question_type,
                "difficulty": difficulty
            }

    def evaluate_answer(
        self,
        exercise: Dict,
        student_answer: str,
        student_data: Optional[Dict] = None
    ) -> Dict:
        """
        评估学生答案并生成详细反馈
        
        :param exercise: 题目数据 {content, answer, question_type}
        :param student_answer: 学生答案
        :param student_data: 学生数据（用于个性化反馈）
        :return: 评估结果 {
            is_correct: bool,
            score: float,
            feedback: str,
            detailed_feedback: dict
        }
        """
        prompt = f"""
        题目：{exercise['content']}
        题目类型：{exercise['question_type']}
        参考答案：{exercise['answer']['reference_answer']}
        学生答案：{student_answer}
        
        评估要求：
        1. 判断是否正确（严格标准）
        2. 给出详细解析（使用中文）
        3. 针对学生答案的个性化改进建议
        4. 如果错误，分析错误原因
        5. 根据题目难度和学生水平给出评分（0-1）
        
        返回JSON格式：
        {{
            "is_correct": bool,
            "score": float,
            "feedback": "简要反馈",
            "detailed_feedback": {{
                "analysis": "详细分析",
                "mistake_type": "错误类型",
                "improvement_suggestions": ["建议1", "建议2"],
                "knowledge_gaps": ["薄弱知识点"]
            }}
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # 更低温度以获得更确定性响应
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            # 确保关键字段存在
            result.setdefault("score", 1.0 if result.get("is_correct", False) else 0.0)
            result["detailed_feedback"].setdefault("knowledge_gaps", [])
            
            return result
        except Exception as e:
            return {
                "is_correct": False,
                "score": 0.0,
                "feedback": f"评估失败: {str(e)}",
                "detailed_feedback": {}
            }

    def generate_feedback_template(
        self,
        exercise: Dict,
        attempt_history: List[Dict]
    ) -> str:
        """
        生成个性化反馈模板
        
        :param exercise: 题目数据
        :param attempt_history: 学生尝试历史
        :return: 反馈模板文本
        """
        prompt = f"""
        根据以下信息生成学习反馈：
        
        题目：{exercise['content']}
        正确率：{exercise.get('correct_rate', 0.7):.1%}
        
        学生尝试记录：
        {json.dumps(attempt_history, indent=2)}
        
        生成：
        1. 总体评价
        2. 主要薄弱环节
        3. 针对性练习建议
        4. 鼓励性语言
        """
        response = self.client.chat.completions.create(...)
        return response.choices[0].message.content

    def _get_question_type_desc(self, question_type: str) -> str:
        """获取题目类型描述"""
        type_map = {
            "mc": "选择题（4个选项）",
            "tf": "判断题（正确/错误）",
            "fb": "填空题",
            "code": "编程题",
            "doc": "文档分析题"
        }
        return type_map.get(question_type, "选择题")