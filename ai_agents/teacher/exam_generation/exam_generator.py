from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool
from typing import List, Dict, Optional
from langchain_community.vectorstores import FAISS
import random
import json
from datetime import datetime
import re
from backend.app.schemas.exam import QuestionCreate, Exam, ExamCreate  # 路径根据你的实际项目结构调整
from utils.model_client import ChatGLMClient

# 定义各题型的 prompt 模板字典
PROMPT_TEMPLATES = {
    "section_intro": """
{section_number}、{section_name}(共{section_count}题，每题{score}分，共{section_total}分，题型说明：{section_desc})\n""",
    "completion": """
【填空题】请根据以下要求生成一道填空题（不要给出选项）：\n\n【知识点】\n{knowledge_point}\n\n【难度】\n{difficulty}/5\n\n【分值】\n{score}分\n\n【背景材料】\n{context}\n\n请严格按照以下格式返回JSON（不要返回markdown代码块）：\n{{\n  \"content\": \"题目内容（包含空白处）\",\n  \"answer\": \"正确答案\",\n  \"analysis\": \"解析说明\",\n  \"score\": {score}\n}}\n""",
    "multiple_choice": """
【多选题】请根据以下要求生成一道多选题（正确选项必须大于等于2个）：\n\n【知识点】\n{knowledge_point}\n\n【难度】\n{difficulty}/5\n\n【分值】\n{score}分\n\n【背景材料】\n{context}\n\n请严格按照以下格式返回JSON（不要返回markdown代码块）：\n{{\n  \"content\": \"题目内容\",\n  \"options\": [\"A. 选项1\", \"B. 选项2\", \"C. 选项3\", \"...\"],\n  \"answer\": [\"A\", \"C\"],\n  \"analysis\": \"解析说明\",\n  \"score\": {score}\n}}\n""",
    "case_analysis": """
【案例分析题】请根据以下要求生成一道案例分析题（简答题，不要给选项）：\n\n【知识点】\n{knowledge_point}\n\n【难度】\n{difficulty}/5\n\n【分值】\n{score}分\n\n【背景材料】\n{context}\n\n请严格按照以下格式返回JSON（不要返回markdown代码块）：\n{{\n  \"content\": \"题目内容\",\n  \"answer\": \"正确答案\",\n  \"analysis\": \"解析说明\",\n  \"score\": {score}\n}}\n""",
    "true_false": """
【判断题】请根据以下要求生成一道判断题：\n\n【知识点】\n{knowledge_point}\n\n【难度】\n{difficulty}/5\n\n【分值】\n{score}分\n\n【背景材料】\n{context}\n\n请严格按照以下格式返回JSON（不要返回markdown代码块）：\n{{\n  \"content\": \"题目内容\",\n  \"answer\": \"正确答案\",\n  \"analysis\": \"解析说明\",\n  \"score\": {score}\n}}\n""",
    "programming": """
【编程题】请根据以下要求生成一道编程题，注意不是选择题，不要给出选项：\n\n【知识点】\n{knowledge_point}\n\n【难度】\n{difficulty}/5\n\n【分值】\n{score}分\n\n【背景材料】\n{context}\n\n请严格按照以下格式返回JSON（不要返回markdown代码块）：\n{{\n  \"content\": \"题目内容\",\n  \"answer\": \"正确答案\",\n  \"analysis\": \"解析说明\",\n  \"score\": {score}\n}}\n""",
    "single_choice": """
【单选题】请根据以下要求生成一道单选题：\n\n【知识点】\n{knowledge_point}\n\n【难度】\n{difficulty}/5\n\n【分值】\n{score}分\n\n【背景材料】\n{context}\n\n请严格按照以下格式返回JSON（不要返回markdown代码块）：\n{{\n  \"content\": \"题目内容\",\n  \"options\": [\"A. 选项1\", \"B. 选项2\", \"C. 选项3\", \"...\"],\n  \"answer\": \"正确答案\",\n  \"analysis\": \"解析说明\",\n  \"score\": {score}\n}}\n"""
}

# 题型中文名和说明
SECTION_NAMES = {
    "single_choice": ("单选题", "每题只有一个正确答案，从四个选项中选择最合适的一个。\n"),
    "multiple_choice": ("多选题", "每题有两个或两个以上正确答案，全部选对才得分。\n"),
    "true_false": ("判断题", "判断下列说法是否正确。\n"),
    "completion": ("填空题", "在空格处填写正确答案。\n"),
    "case_analysis": ("案例分析题", "根据案例回答问题，简答型。\n"),
    "programming": ("编程题", "根据要求编写代码实现功能。\n")
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
        vector_store: FAISS,
        extra_context: Optional[str] = None,
        score: int = 5  # 新增
    ) -> QuestionCreate:
        # 检索相关知识
        related_docs = vector_store.similarity_search(knowledge_point, k=3)
        context = "\n".join([doc.page_content for doc in related_docs])
        # 拼接上传内容
        if extra_context:
            context += "\n" + extra_context

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
        if template_str is None:
            raise ValueError(f"未知题型: {question_type}")
        prompt_template = PromptTemplate(
            input_variables=["knowledge_point", "question_type", "difficulty", "context", "score"],
            template=template_str
        )
        prompt = prompt_template.format(
            knowledge_point=knowledge_point,
            question_type=question_type,
            difficulty=difficulty,
            context=context,
            score=score
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
            score=score,
            exam_id=None
        )

    async def generate_exam(
        self,
        course_id: int,
        knowledge_points: List[str],
        question_config: Dict[str, int],
        question_scores: Optional[Dict[str, int]] = None,
        difficulty: int = 3,
        duration: int = 90,
        created_by: int = None,
        vector_store: FAISS = None,
        exam_title: Optional[str] = None,
        extra_context: Optional[str] = None
    ) -> ExamCreate:
        questions = []
        total_score = 0
        print("ai_agents/teacher/exam_generation/exam_generator.py的_generate_exam在工作")

        # 题型顺序
        section_order = ["single_choice", "multiple_choice", "true_false", "completion", "case_analysis", "programming"]
        section_number = 1
        for q_type in section_order:
            count = question_config.get(q_type, 0)
            if count <= 0:
                continue
            score = question_scores.get(q_type, 5) if question_scores else 5
            section_name, section_desc = SECTION_NAMES.get(q_type, (q_type, ""))
            section_total = count * score
            # 生成大题说明
            section_intro = PROMPT_TEMPLATES["section_intro"].format(
                section_number=ExamGeneratorAgent._to_chinese_number(section_number),
                section_name=section_name,
                section_count=count,
                score=score,
                section_total=section_total,
                section_desc=section_desc
            )
            # 生成本大题所有小题
            for i in range(count):
                k_point = random.choice(knowledge_points)
                question = await self._generate_question(
                    k_point, q_type, difficulty, vector_store, extra_context=extra_context, score=score
                )
                # 在每个小题内容前加题号
                question.content = f"{i+1}. {question.content}"
                questions.append(question)
                total_score += score
            # 在大题第一个小题前插入大题说明
            questions[-count].content = section_intro + "\n" + questions[-count].content
            section_number += 1

        return ExamCreate(
            id=None,
            title=exam_title or f"自动生成试卷-{datetime.now().strftime('%Y%m%d%H%M')}",
            course_id=course_id,
            total_score=total_score,
            duration=duration,
            questions=questions,
            created_at=datetime.now(),
            created_by=created_by,
            status="draft"
        )

    @staticmethod
    def _to_chinese_number(num):
        # 1->一, 2->二, ...
        cn = "一二三四五六七八九十"
        if 1 <= num <= 10:
            return cn[num-1]
        return str(num)
