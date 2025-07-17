from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db, get_vector_store
from ai_agents.factory import AgentFactory
from typing import Optional, List
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from utils.model_client import ChatGLMClient
from backend.app.models.chat import ChatSession, ChatMessage
from backend.app.core.deps import get_current_user
from backend.app.db.base_class import Base
from backend.app.db.session import engine
from backend.app.models.user import User

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = None
    session_id: Optional[int] = None  # 新增

class AnswerResponse(BaseModel):
    answer: str

@router.post("/qa", response_model=AnswerResponse)
async def student_qa(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    vector_store=Depends(get_vector_store),
    current_user: User = Depends(get_current_user)
):
    """
    学生问答接口，支持知识库检索和模型回答
    """
    try:
        # 如果没传history但有session_id，则自动查历史
        history = request.history
        if history is None and request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            if session:
                history = [
                    {"role": m.role, "content": m.content}
                    for m in session.messages[-10:]
                ]
            else:
                history = []
        # 创建问答智能体
        agent = AgentFactory.create_agent("qa_agent")
        if not agent:
            raise ValueError("创建问答智能体失败")
        answer = await agent.answer_question(
            question=request.question,
            vector_store=vector_store,
            history=history or []
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")

@router.get("/sessions")
async def get_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()
    return [
        {"id": s.id, "title": s.title, "created_at": s.created_at}
        for s in sessions
    ]

@router.get("/sessions/{session_id}")
async def get_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "messages": [
            {"role": m.role, "content": m.content, "created_at": m.created_at}
            for m in session.messages
        ]
    }

@router.post("/sessions")
async def create_session(title: str = "新会话", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = ChatSession(user_id=current_user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"id": session.id, "title": session.title, "created_at": session.created_at}

class MessageRequest(BaseModel):
    role: str
    content: str

@router.post("/sessions/{session_id}/messages")
async def add_message(
    session_id: int,
    message: MessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = ChatMessage(session_id=session_id, role=message.role, content=message.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"id": msg.id, "role": msg.role, "content": msg.content, "created_at": msg.created_at}

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.delete(session)
    db.commit()
    return {"msg": "会话已删除"}