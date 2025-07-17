from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
from utils.model_client import ChatGLMClient
import json
import re
from typing import List, Optional

# class QAAgent:
#     def __init__(self):
#         self.client = ChatGLMClient()

#     async def answer_question(self, question: str, vector_store: FAISS) -> str:
#         # 检索相关知识
#         related_docs = vector_store.similarity_search(question, k=3)
#         context = "\n".join([doc.page_content for doc in related_docs])

#         # 构建 Prompt
#         prompt_template = PromptTemplate(
#             input_variables=["question", "context"],
#             template="""
#             你是一位智能问答助手，请根据以下问题和相关知识回答学生的问题。

#             【问题】：
#             {question}

#             【相关知识】：
#             {context}

#             请直接输出答案。
#             """
#         )
#         prompt = prompt_template.format(question=question, context=context)

#         # 调用模型生成答案
#         response = await self.client.generate_text(prompt)
#         return response.strip()
class QAAgent:
    def __init__(self):
        self.client = ChatGLMClient()

    async def answer_question(self, question: str, vector_store: FAISS, history: Optional[List[dict]] = None) -> str:
        related_docs = vector_store.similarity_search(question, k=3)
        context = "\n".join([doc.page_content for doc in related_docs])
        # 构建历史对话
        history_prompt = ""
        if history:
            for turn in history[-10:]:
                if turn["role"] == "user":
                    history_prompt += f"学生：{turn['content']}\n"
                else:
                    history_prompt += f"助手：{turn['content']}\n"
        prompt_template = PromptTemplate(
            input_variables=["history", "question", "context"],
            template="""
你是一位智能学习问答助手。请根据历史对话、当前问题和相关知识，回答学生的问题。

【历史对话】：
{history}

【问题】：
{question}

【相关知识】：
{context}

请直接输出答案。
"""
        )
        prompt = prompt_template.format(history=history_prompt, question=question, context=context)
        response = await self.client.generate_text(prompt)
        return response.strip()