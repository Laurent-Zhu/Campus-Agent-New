from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Question(BaseModel):
    """题目模型"""
    id: Optional[int] = None
    type: str  # 选择题/填空题/简答题/编程题
    content: str
    options: Optional[List[str]] = None  # 选择题选项，数据库存储为JSON字符串
    answer: str
    analysis: Optional[str] = None
    difficulty: int = Field(ge=1, le=5)
    knowledge_point: str
    score: int
    exam_id: Optional[int] = None

class Exam(BaseModel):
    """试卷模型"""
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    course_id: int
    total_score: int
    duration: int
    questions: List[Question]
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    status: str = "draft"