from backend.app.core.config import settings
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.core.deps import get_db
from backend.app.models.user import User
from backend.app.core.security import get_password_hash, verify_password, create_access_token

from jose import JWTError, jwt



# 配置JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# 用于获取请求头中的 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 定义路由
router = APIRouter()






class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    print("开始处理注册请求\n")
    user = db.query(User).filter((User.username == request.username) | (User.email == request.email)).first()
    if user:
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        role=request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "注册成功"}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password) or user.role != request.role:
        raise HTTPException(status_code=401, detail="用户名或密码或身份错误")
    token = create_access_token(user.id, user.role)

    # # 调试输出 Token
    # print("="*50)
    # print(f"DEBUG TOKEN: {token}")  # 控制台直接打印 Token
    # print("="*50)

    return {"access_token": token, "token_type": "bearer"}




# 验证 token 的函数
def verify_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)  # 通过依赖注入获取db会话
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
        
        # 直接使用通过依赖注入获取的db会话
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
            
        return {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")



# Token 验证接口（供 Django 调用）
@router.get("/validate")
def validate_token(user: dict = Depends(verify_token)):
    return {
        "valid": True,
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"]
    }


