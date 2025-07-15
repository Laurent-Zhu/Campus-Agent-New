from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.app.core.deps import get_db, get_current_user
from backend.app.models.user import User
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.schemas.user import User as UserSchema, UserCreate

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

class UserCreateRequest(UserCreate):
    pass

class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None

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


@router.get("/users", response_model=list[UserSchema])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有已注册的用户信息，仅管理员可见
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员才能访问此接口")

    users = db.query(User).all()
    for user in users:
        if user.role is None:
            user.role = 'unknown'  # 或者其他默认值
    return users

# POST /api/v1/auth/users 创建用户
@router.post("/users", response_model=UserSchema)
async def create_user(
    request: UserCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新用户，仅管理员可见
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建用户"
        )

    user = db.query(User).filter((User.username == request.username) | (User.email == request.email)).first
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        role=request.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# PUT /api/v1/auth/users/{user_id} 更新用户
@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    request: UserUpdateRequest,
    user_id: int = Path(..., title="用户ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    
):
    """
    更新用户信息，仅管理员可以更新其他用户的信息
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以更新用户信息")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    if request.username:
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="用户名已存在")
        user.username = request.username

    if request.email:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="邮箱已存在")
        user.email = request.email

    if request.password:
        user.hashed_password = get_password_hash(request.password)

    if request.role:
        user.role = request.role

    db.commit()
    db.refresh(user)
    return user

# DELETE /api/v1/auth/users/{user_id} 删除用户
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int = Path(..., title="用户ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户，仅管理员可操作
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员才能删除用户")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}