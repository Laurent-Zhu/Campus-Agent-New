from pydantic_settings import BaseSettings
from typing import List
import os
import os
from dotenv import load_dotenv

class ModelConfig(BaseSettings):
    """模型配置"""
    API_KEY: str = os.getenv("ZHIPU_API_KEY") #"c5ee8594faa94adfaca3a9c5f4128a20.s98xk3HJBhHQMVPF" # 
    API_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    API_VERSION: str = "glm-4-plus"

    class Config:
        env_file = ".env"
        extra = "allow"  # 允许额外的环境变量