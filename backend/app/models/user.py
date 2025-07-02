from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from typing import List
from backend.app.db.base_class import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    username: Mapped[str] = Column(String(50), unique=True, index=True)
    email: Mapped[str] = Column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = Column(String(100))
    role: Mapped[str] = Column(String(20))  # admin/teacher/student
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    created_exams: Mapped[List["Exam"]] = relationship(
        "Exam",
        back_populates="creator",
        cascade="all, delete-orphan"
    )