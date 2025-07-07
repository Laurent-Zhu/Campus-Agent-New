from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db, get_vector_store
from ai_agents.factory import AgentFactory

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str

@router.post("/qa", response_model=AnswerResponse)
async def student_qa(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    vector_store=Depends(get_vector_store)
):
    """
    学生问答接口，支持知识库检索和模型回答
    """
    try:
        # 创建问答智能体
        agent = AgentFactory.create_agent("qa_agent")
        if not agent:
            raise ValueError("创建问答智能体失败")

        # 调用智能体进行问答
        answer = await agent.answer_question(
            question=request.question,
            vector_store=vector_store  # 传递知识库
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")