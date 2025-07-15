# from pydantic_settings import BaseSettings

# class Settings(BaseSettings):
#     # 数据库配置
#     DATABASE_URL: str = "sqlite:///./campus_agent.db"
    
#     # AI模型配置
#     MODEL_PATH: str = "../models/chatglm3-6b"
#     MODEL_TYPE: str = "chatglm3"  # 可选：chatglm3/qwen/baichuan2
    
#     # 知识库配置
#     VECTOR_STORE_PATH: str = "../knowledge/vector_store"
#     DOCUMENT_STORE_PATH: str = "../knowledge/documents"
    
#     # API配置
#     API_V1_STR: str = "/api/v1"
#     SECRET_KEY: str = "your-secret-key-here"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
#     class Config:
#         env_file = ".env"

# settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 项目信息
    PROJECT_NAME: str = "Campus Agent"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./campus_agent.db"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # AI模型配置
    MODEL_PATH: str = "./models/chatglm3-6b"
    MODEL_TYPE: str = "chatglm3"
    
    class Config:
        case_sensitive = True

settings = Settings()