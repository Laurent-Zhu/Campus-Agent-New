from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool
from typing import List, Dict
from langchain_community.vectorstores import FAISS
import random
import json
from datetime import datetime
import re
from backend.app.schemas.exam import QuestionCreate, Exam, ExamCreate  # 路径根据你的实际项目结构调整
from utils.model_client import ChatGLMClient

# 定义各题型的 prompt 模板字典
PROMPT_TEMPLATES = {
    "completion": """
你是一位资深命题专家，请根据以下要求生成一道填空题（不要给出选项）：

【知识点】
{knowledge_point}

【题型】
{question_type}

【难度】
{difficulty}/5

【背景材料】
{context}

请严格按照以下格式返回JSON（不要返回markdown代码块）：
{{
  "content": "题目内容（包含空白处）",
  "answer": "正确答案",
  "analysis": "解析说明",
  "score": 5
}}
""",
    "multiple_choice": """
你是一位资深命题专家，请根据以下要求生成一道多选题（正确选项必须大于等于2个）：

【知识点】
{knowledge_point}

【题型】
{question_type}

【难度】
{difficulty}/5

【背景材料】
{context}

请严格按照以下格式返回JSON（不要返回markdown代码块）：
{{
  "content": "题目内容",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "..."],
  "answer": ["A", "C"],
  "analysis": "解析说明",
  "score": 5
}}
""",
    "case_analysis": """
你是一位资深命题专家，请根据以下要求生成一道案例分析题（简答题，不要给选项）：

【知识点】
{knowledge_point}

【题型】
{question_type}

【难度】
{difficulty}/5

【背景材料】
{context}

请严格按照以下格式返回JSON（不要返回markdown代码块）：
{{
  "content": "题目内容",
  "answer": "正确答案",
  "analysis": "解析说明",
  "score": 5
}}
""",
    "true_false": """
你是一位资深命题专家，请根据以下要求生成一道判断题：

【知识点】
{knowledge_point}

【题型】
{question_type}

【难度】
{difficulty}/5

【背景材料】
{context}

请严格按照以下格式返回JSON（不要返回markdown代码块）：
{{
  "content": "题目内容",
  "answer": "正确答案",
  "analysis": "解析说明",
  "score": 5
}}
""",
    "programming": """
你是一位资深命题专家，请根据以下要求生成一道编程题，注意不是选择题，不要给出选项：

【知识点】
{knowledge_point}

【题型】
{question_type}

【难度】
{difficulty}/5

【背景材料】
{context}

请严格按照以下格式返回JSON（不要返回markdown代码块）：
{{
  "content": "题目内容",
  "answer": "正确答案",
  "analysis": "解析说明",
  "score": 5
}}
""",
    "single_choice": """
你是一位资深命题专家，请根据以下要求生成一道单选题：

【知识点】
{knowledge_point}

【题型】
{question_type}

【难度】
{difficulty}/5

【背景材料】
{context}

请严格按照以下格式返回JSON（不要返回markdown代码块）：
{{
  "content": "题目内容",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "..."],
  "answer": "正确答案",
  "analysis": "解析说明",
  "score": 5
}}
"""
}


def extract_json_from_codeblock(text: str) -> str:
    print("ai_agents/teacher/exam_generation/exam_generator.py的extract_json_from_codeblock在工作")
    # match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    # if match:
    #     return match.group(1)
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0)
    return text.strip()

class ExamGeneratorAgent:
    def __init__(self):
        self.client = ChatGLMClient()
    
    # async def _generate_question(
    #     self,
    #     knowledge_point: str,
    #     question_type: str,
    #     difficulty: int
    # ) -> QuestionCreate:
    #     # 根据题型生成不同的提示词
    #     if question_type == "填空题":
    #         prompt = f"""
    #         请根据以下要求生成一道填空题(不要给出选项，也就是说不要出成选择题):
    #         知识点: {knowledge_point}
    #         难度等级: {difficulty}/5

    #         返回JSON格式包含:
    #         1. content: 题目内容（包含空白处）
    #         2. answer: 标准答案
    #         3. analysis: 解题思路
    #         4. score: 分值
    #         """
    #     elif question_type == "多选题":
    #         prompt = f"""
    #         请根据以下要求生成一道多选题(注意, 正确选项必须大于等于2个):
    #         知识点: {knowledge_point}
    #         题型: {question_type}
    #         难度等级: {difficulty}/5

    #         返回JSON格式包含:
    #         1. content: 题目内容
    #         2. options: 选项列表
    #         3. answer: 标准答案
    #         4. analysis: 解题思路
    #         5. score: 分值
    #         """
    #     elif question_type == "案例分析题":
    #         prompt = f"""
    #         请根据以下要求生成一道案例分析题，要求学生以简答的形式回答，注意不是选择题，不要给出选项:
    #         知识点: {knowledge_point}
    #         题型: {question_type}
    #         难度等级: {difficulty}/5

    #         返回JSON格式包含:
    #         1. content: 题目内容
    #         2. answer: 标准答案
    #         3. analysis: 解题思路
    #         4. score: 分值
    #         """
    #     else:
    #         prompt = f"""
    #         请根据以下要求生成一道考试题:
    #         知识点: {knowledge_point}
    #         题型: {question_type}
    #         难度等级: {difficulty}/5

    #         返回JSON格式包含:
    #         1. content: 题目内容
    #         2. options: 选项列表(单选题必需，其他题型不需要这项内容)
    #         3. answer: 标准答案
    #         4. analysis: 解题思路
    #         5. score: 分值
    #         """
    #     print("ai_agents/teacher/exam_generation/exam_generator.py的_generate_question在工作")
    #     response = await self.client.generate_text(prompt)
    #     json_str = extract_json_from_codeblock(response)
    #     print("大模型返回的json_str:", json_str)
    #     try:
    #         result = json.loads(json_str)
    #     except Exception as e:
    #         print("解析JSON失败:", e)
    #         raise

    #     # 处理 options 字段（仅选择题需要）
    #     options = result.get("options")
    #     if options and isinstance(options, list) and isinstance(options[0], dict):
    #         options = [f"{opt.get('label', chr(65+i))}. {opt.get('text', '')}" for i, opt in enumerate(options)]
    #     else:
    #         options = options

    #     return QuestionCreate(
    #         id=None,
    #         type=question_type,
    #         content=result["content"],
    #         options=options,
    #         answer=result["answer"],
    #         analysis=result.get("analysis"),
    #         difficulty=difficulty,
    #         knowledge_point=knowledge_point,
    #         score=int(result.get("score", 5)),
    #         exam_id=None
    #     )

    
    async def _generate_question(
        self,
        knowledge_point: str,
        question_type: str,
        difficulty: int,
        vector_store: FAISS
    ) -> QuestionCreate:
        # 检索相关知识
        related_docs = vector_store.similarity_search(knowledge_point, k=3)
        context = "\n".join([doc.page_content for doc in related_docs])

        # 构建 LangChain 的 PromptTemplate
        # prompt_template = PromptTemplate(
        #     input_variables=["knowledge_point", "question_type", "difficulty", "context"],
        #     template="""
        #     请根据以下知识点生成一道{question_type}:
        #     知识点: {knowledge_point}
        #     难度等级: {difficulty}/5
        #     相关知识:
        #     {context}

        #     返回JSON格式包含:
        #     1. content: 题目内容
        #     2. options: 选项列表(选择题必需)
        #     3. answer: 标准答案
        #     4. analysis: 解题思路
        #     5. score: 分值
        #     """
        # )
        template_str = PROMPT_TEMPLATES.get(question_type)

        prompt_template = PromptTemplate(
            input_variables=["knowledge_point", "question_type","difficulty", "context"],
            template=template_str
        )

        prompt = prompt_template.format(
            knowledge_point=knowledge_point,
            question_type=question_type,
            difficulty=difficulty,
            context=context
        )

        # response = await self.client.generate_text(prompt)
        # json_str = extract_json_from_codeblock(response)
        # result = json.loads(json_str)

        # # 处理 options 字段
        # options = result.get("options")
        # if options and isinstance(options, list) and isinstance(options[0], dict):
        #     options = [f"{opt.get('label', chr(65+i))}. {opt.get('text', '')}" for i, opt in enumerate(options)]
        # else:
        #     options = options

        print("ai_agents/teacher/exam_generation/exam_generator.py的_generate_question在工作")
        response = await self.client.generate_text(prompt)
        json_str = extract_json_from_codeblock(response)
        print("大模型返回的json_str:", json_str)
        try:
            result = json.loads(json_str)
        except Exception as e:
            print("解析JSON失败:", e)
            raise

        options = result.get("options")
        if isinstance(options, list) and options:
            if all(isinstance(opt, dict) for opt in options):
                # 转换 dict -> 字符串格式
                options = [f"{opt.get('label', chr(65+i))}. {opt.get('text', '')}" for i, opt in enumerate(options)]
            elif all(isinstance(opt, str) for opt in options):
                # 已经是字符串列表，直接用
                pass
            else:
                # 结构异常，做日志或异常处理
                options = None
        else:
            options = None

        # 处理 answer 字段，确保是字符串
        answer = result.get("answer")
        if isinstance(answer, list):
            answer = ",".join(answer)

        return QuestionCreate(
            id=None,
            type=question_type,
            content=result["content"],
            options=options,
            answer=answer,
            analysis=result.get("analysis"),
            difficulty=difficulty,
            knowledge_point=knowledge_point,
            score=int(result.get("score", 5)),
            exam_id=None
        )

    async def generate_exam(
        self,
        course_id: int,
        knowledge_points: List[str],
        question_config: Dict[str, int],  # 包含题型和数量的配置
        difficulty: int = 3,
        duration: int = 90,
        created_by: int = None,
        vector_store: FAISS = None
    ) -> ExamCreate:
        questions = []
        total_score = 0
        print("ai_agents/teacher/exam_generation/exam_generator.py的_generate_exam在工作")

        # 根据题型和数量生成题目
        for q_type, count in question_config.items():
            for _ in range(count):
                # 随机选择一个知识点
                k_point = random.choice(knowledge_points)
                # 调用生成单题的方法
                question = await self._generate_question(k_point, q_type, difficulty, vector_store)
                questions.append(question)
                total_score += question.score

        # 返回试卷
        return ExamCreate(
            id=None,
            title=f"自动生成试卷-{datetime.now().strftime('%Y%m%d%H%M')}",
            course_id=course_id,
            total_score=total_score,
            duration=duration,
            questions=questions,  # 包含所有生成的题目
            created_at=datetime.now(),
            created_by=created_by,
            status="draft"
        )
