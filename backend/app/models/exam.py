from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from backend.app.db.base_class import Base

class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    course_id: Mapped[int] = Column(Integer, ForeignKey("courses.id"))
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    duration: Mapped[int] = Column(Integer)  # 考试时长(分钟)
    total_score: Mapped[int] = Column(Integer)
    status: Mapped[str] = Column(String(20))  # draft/published

    questions: Mapped[list["Question"]] = relationship("Question", back_populates="exam")
    course: Mapped["Course"] = relationship("Course", back_populates="exams")
    creator: Mapped["User"] = relationship("User", back_populates="created_exams")

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    exam_id: Mapped[int] = Column(Integer, ForeignKey("exams.id"))
    type: Mapped[str] = Column(String(20))  # choice/completion/programming
    content: Mapped[str] = Column(Text, nullable=False)
    options: Mapped[str] = Column(Text, nullable=True)  # JSON字符串存储选项
    answer: Mapped[str] = Column(Text, nullable=False)
    analysis: Mapped[str] = Column(Text, nullable=True)
    score: Mapped[int] = Column(Integer)
    knowledge_point: Mapped[str] = Column(String(100))
    difficulty: Mapped[int] = Column(Integer)  # 1-5

    exam: Mapped["Exam"] = relationship("Exam", back_populates="questions")