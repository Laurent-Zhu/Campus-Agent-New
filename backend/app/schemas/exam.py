from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict

class QuestionBase(BaseModel):
    type: str
    content: str
    options: Optional[List[str]] = None  # 选择题选项，数据库存储为JSON字符串
    answer: str
    analysis: Optional[str] = None
    score: int
    knowledge_point: str
    difficulty: int

class QuestionCreate(BaseModel):
    type: str
    content: str
    options: Optional[List[str]]
    answer: str
    analysis: Optional[str]
    difficulty: int
    knowledge_point: str
    score: int

class Question(QuestionBase):
    id: Optional[int] = None
    exam_id: Optional[int] = None

    class Config:
        from_attributes = True

class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int
    duration: int
    total_score: int

# class ExamCreate(ExamBase):
#     questions: List[QuestionCreate]
class ExamCreate(BaseModel):
    id: Optional[int] = None
    title: str
    course_id: int
    total_score: int
    duration: int
    questions: List[QuestionCreate]
    created_at: datetime
    created_by: Optional[int]
    status: str

class Exam(ExamBase):
    id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    status: str
    questions: List[Question]

    class Config:
        from_attributes = True

class ExamGenerateRequest(BaseModel):
    course_id: int
    knowledge_points: List[str]
    question_types: dict
    question_scores: Optional[dict] = None  # 新增
    difficulty: int
    exam_title: Optional[str] = None
    extra_context: Optional[str] = None

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    total_score: Optional[int] = None
    status: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = None