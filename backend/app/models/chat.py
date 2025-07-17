from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from datetime import datetime
from backend.app.db.base_class import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    title: Mapped[str] = Column(String(100), default="新会话")
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = Column(Integer, ForeignKey("chat_sessions.id"))
    role: Mapped[str] = Column(String(10))  # 'user' or 'bot'
    content: Mapped[str] = Column(Text)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
