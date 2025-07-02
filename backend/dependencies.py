from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from transformers import AutoTokenizer, AutoModel
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_llm():
    """获取语言模型实例"""
    model_path = os.getenv("MODEL_PATH")
    device = os.getenv("DEVICE", "cpu")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to(device)
    
    return model

async def get_current_teacher(token: str = Depends(oauth2_scheme)):
    """获取当前登录教师"""
    # TODO: 实现教师认证逻辑
    return {"id": "test_teacher", "role": "teacher"}