# ai_agents/teacher/lesson/agent_tools.py
from langchain_core.tools import tool
from langchain_community.document_loaders import UnstructuredPDFLoader, UnstructuredWordDocumentLoader

@tool
def parse_document(file_path: str) -> str:
    """解析PDF或DOCX文件，并返回结构化文本内容"""
    if file_path.endswith('.pdf'):
        loader = UnstructuredPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = UnstructuredWordDocumentLoader(file_path)
    else:
        return "仅支持PDF或DOCX文件"
    docs = loader.load()
    return "\n".join([doc.page_content for doc in docs])

@tool
def generate_lesson_plan(context: str) -> str:
    """根据机构化内容生成教案草稿"""
    return f"【教案草稿】\n根据内容：{context[:200]}..."

@tool
def generate_training_plan(context: str) -> str:
    """根据结构化内容生成实训计划"""
    return f"【实训计划】\n根据内容：{context[:200]}..."

@tool
def generate_schedule(context: str) -> str:
    """根据结构化内容生成时间安排表"""
    return f"【时间安排表】\n根据内容：{context[:200]}..."

@tool
def generate_ppt_outline(context: str)-> str:
    """根据结构化内容生成PPT大纲"""
    sections = content.split("\n")
    ppt_outline = {
        "title": sections[0],
        "slides": [
            {
                "title": section.split(":")[0],
                "content": section.split(":")[1]
            }
            for section in sections[1:] if ":" in section
        ]
    }
    return ppt_outline