from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
from ..db.session import SessionLocal
from ..core.security import decode_access_token
from ..models.user import User

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    db: Session = Depends(get_db),
    token: dict = Depends(decode_access_token)
) -> User:
    print("Received token:", token)
    try:
        user = db.query(User).filter(User.id == token["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )

# deps.py
def get_vector_store():
    from backend.app.main import vector_store
    return vector_store
