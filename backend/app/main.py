from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings
# from app.api.endpoints import exam, auth
# from app.db.session import engine
# from app.models.base import Base
from backend.app.core.config import settings
from backend.app.api.endpoints import exam, auth
from backend.app.db.session import engine
from backend.app.models.base import Base
import math

from langchain.embeddings.base import Embeddings
from zhipuai import ZhipuAI

import nltk
nltk.data.path.append('/home/laurentzhu/nltk_data')


class ZhipuAIEmbeddings(Embeddings):
    def __init__(self, api_key: str, model: str = "embedding-3"):
        self.client = ZhipuAI(api_key=api_key)
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        all_embeddings = []
        batch_size = 64
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(model=self.model, input=batch)
            embeddings = [item.embedding for item in response.data]  # 这里改了
            all_embeddings.extend(embeddings)
        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model, input=[text])
        return response.data[0].embedding




app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # 必须包含"Authorization"
)

# 注册 /api/v1/exams 路由
app.include_router(
    exam.router,
    prefix=f"{settings.API_V1_STR}/exams",
    tags=["exam"]
)

# 注册 /api/v1/auth 路由
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)




from backend.app.api.endpoints.student import router as student_router

app.include_router(student_router, prefix="/api/v1/student", tags=["Student"])

# 启动时自动建表（仅开发环境用，生产建议用alembic）
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to Campus Agent API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_knowledge_base(directory: str):
    # print(f"扫描目录: {os.path.abspath(directory)}")  # 添加这行
    # print(f"目录内容: {os.listdir(directory)}")      # 添加这行
    """加载知识库中的 .docx 文件"""
    documents = []
    for filename in os.listdir(directory):
        # print(f"正在处理文件: {filename}")
        if filename.endswith(".docx"):
            # print(f"加载 .docx 文件: {filename}") 
            loader = UnstructuredWordDocumentLoader(os.path.join(directory, filename))
            doc = loader.load()
            documents.extend(doc)
    # 分割文档内容
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    print(f"共加载 {len(documents)} 个文档块")

    return split_docs

from langchain_community.vectorstores import FAISS

def build_vector_store(documents):
    """构建向量存储"""
    # embeddings = embed_documents_with_zhipuai(documents)
    embeddings = ZhipuAIEmbeddings(api_key=os.getenv("ZHIPU_API_KEY"))
    vector_store = FAISS.from_texts([doc.page_content for doc in documents], embeddings)
    return vector_store

def initialize_knowledge_base():
    """初始化知识库"""
    # print("=== 初始化知识库（调试）===")
    knowledge_directory = "./knowledge/mooc"  # 知识库目录
    documents = load_knowledge_base(knowledge_directory)
    vector_store = build_vector_store(documents)
    return vector_store

vector_store = initialize_knowledge_base()

from backend.app.models import *  # 确保chat表被创建
Base.metadata.create_all(bind=engine)