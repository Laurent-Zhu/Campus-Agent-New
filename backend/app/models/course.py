from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from typing import List
from backend.app.db.base_class import Base

class Course(Base):
    __tablename__ = "courses"
    
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(100), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    teacher_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    exams: Mapped[List["Exam"]] = relationship(
        "Exam",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    teacher: Mapped["User"] = relationship("User")