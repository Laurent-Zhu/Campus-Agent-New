import json
from typing import Dict, List, Optional
from student.exercises.models import KnowledgePoint
from django.conf import settings

# 根据模型导入知识点模型（用于获取知识点名称）
from student.exercises.models import KnowledgePoint

import json
from typing import Dict, Any
from zhipuai import ZhipuAI



class LLMService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, 'ZHIPUAI_API_KEY', '')
        if not self.api_key:
            raise ValueError("未配置ZHIPUAI_API_KEY")
        self.client = ZhipuAI(api_key=self.api_key)
    
    def _call_zhipuai(self, prompt: str) -> str:
        """调用智谱AI接口"""
        try:
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}  # 要求返回JSON格式
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = f"智谱API调用异常: {str(e)}"
            if "401" in str(e):
                error_msg = "API认证失败，请检查API Key"
            elif "429" in str(e):
                error_msg = "API调用过于频繁，请稍后再试"
            raise ValueError(error_msg)
    
    def generate_question(self, student_data: Dict[str, Any], difficulty: str, knowledge_point_ids: list) -> Dict[str, str]:
        """生成题目"""
        try:
            prompt = self._build_prompt(student_data, difficulty, knowledge_point_ids)
            llm_output = self._call_zhipuai(prompt)
            
            # 尝试解析JSON
            try:
                result = json.loads(llm_output)
            except json.JSONDecodeError:
                # 如果解析失败，尝试提取可能的JSON部分
                if "{" in llm_output and "}" in llm_output:
                    json_str = llm_output[llm_output.index("{"):llm_output.rindex("}")+1]
                    result = json.loads(json_str)
                else:
                    raise ValueError("API返回结果不是有效的JSON格式")
            
            # 验证结果格式
            required_fields = ["title", "question", "answer"]
            if not all(key in result for key in required_fields):
                raise ValueError(f"返回结果缺少必要字段，需要包含: {', '.join(required_fields)}")
                
            return result
            
        except Exception as e:
            raise ValueError(f"题目生成失败: {str(e)}")

    def _build_prompt(self, student_data: Dict[str, Any], difficulty: str, knowledge_point_ids: list) -> str:
        """构造生成题目的提示词"""
        prompt = f"""你必须返回一个严格的JSON格式响应，包含title、question和answer三个字段。
根据以下要求生成一个数学题目：
- 学生正确率: {student_data['correct_rate']}
- 薄弱点: {', '.join(student_data['weak_points'])}
- 难度: {difficulty}
- 知识点ID: {', '.join(map(str, knowledge_point_ids))}

返回示例格式：
{{
    "title": "题目标题",
    "question": "题目内容",
    "answer": "题目答案"
}}"""
        return prompt

    def _validate_output(self, data: Dict) -> Dict:
        """验证LLM输出结构"""
        required_fields = ["title", "question", "question_type", "answer", "hints"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"缺少必填字段: {field}")
        
        if "reference_answer" not in data["answer"]:
            raise ValueError("answer必须包含reference_answer字段")
        
        valid_types = ["mc", "tf", "fb", "code", "doc"]
        if data["question_type"] not in valid_types:
            raise ValueError(f"无效题型: {data['question_type']}")
        
        # 选项验证
        if data["question_type"] in ["mc", "tf"]:
            if not isinstance(data.get("options"), list):
                raise ValueError("options必须是列表")
            if data["question_type"] == "mc" and len(data["options"]) != 4:
                raise ValueError("选择题需4个选项")
            if data["question_type"] == "tf" and len(data["options"]) != 2:
                raise ValueError("判断题需2个选项")
        
        # 列表类型转换
        if not isinstance(data["hints"], list):
            data["hints"] = [data["hints"]]
        if "common_mistakes" in data and not isinstance(data["common_mistakes"], list):
            data["common_mistakes"] = [data["common_mistakes"]]
        
        return data















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