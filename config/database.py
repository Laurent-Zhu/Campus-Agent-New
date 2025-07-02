from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database import Base
import os
from dotenv import load_dotenv

load_dotenv()

# 获取数据库URL
DATABASE_URL = os.getenv("DB_URL", "sqlite:///./campus_agent.db")

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite需要
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 初始化数据库
def init_db():
    Base.metadata.create_all(bind=engine)