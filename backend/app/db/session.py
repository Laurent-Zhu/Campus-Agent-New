# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from ..core.config import settings

# engine = create_engine(
#     settings.DATABASE_URL,
#     pool_pre_ping=True,
#     echo=settings.DEBUG
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

@contextmanager
def get_db():
    """数据库会话生成器，确保会话正确关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()