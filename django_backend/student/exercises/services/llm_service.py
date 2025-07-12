from openai import OpenAI  # 或使用其他LLM SDK

class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key="your_api_key")  # 替换为实际API密钥
    
    # 生成题目
    def generate_question(self, student_data, knowledge_points):
        prompt = f"""
        根据以下学生信息生成1道{difficulty}难度的练习题：
        - 学生ID: {student_data['id']}
        - 平均分: {student_data['average_score']}
        - 薄弱知识点: {knowledge_points}
        
        要求：
        1. 题目类型：选择题
        2. 格式：{{"question": "问题文本", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "解析"}}
        """
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return self._parse_response(response.choices[0].message.content)
    
    def evaluate_answer(self, question, student_answer):
        prompt = f"""
        题目：{question['text']}
        正确答案：{question['answer']}
        学生答案：{student_answer}
        
        请分析：
        1. 是否正确（布尔值）
        2. 错误原因（若错误）
        3. 改进建议
        返回JSON格式：{{"is_correct": bool, "feedback": str}}
        """
        response = self.client.chat.completions.create(...)
        return json.loads(response.choices[0].message.content)
    
    def _parse_response(self, text):
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # 处理LLM返回格式错误
            return {"error": "LLM返回格式异常"}