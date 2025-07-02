from typing import Any, List, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMemory
from langchain.agents import Tool
from langchain.callbacks.manager import CallbackManager
from pydantic import BaseModel

class BaseAgent(BaseModel):
    """基础智能体类"""
    
    llm: Any  # 语言模型
    tools: List[Tool]  # 工具列表
    memory: Optional[BaseMemory] = None  # 记忆模块
    callback_manager: Optional[CallbackManager] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def initialize(self) -> None:
        """初始化智能体"""
        pass
    
    async def arun(self, input_text: str) -> str:
        """异步执行"""
        raise NotImplementedError
    
    def run(self, input_text: str) -> str:
        """同步执行"""
        raise NotImplementedError