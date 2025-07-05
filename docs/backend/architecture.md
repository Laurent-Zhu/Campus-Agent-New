# 后端架构设计说明文档

## 1. 目录结构

```
backend/
├── app/
│   ├── api/                 # API路由层
│   │   └── endpoints/       # 具体API实现
│   │       └── exam.py      # 考试相关接口
│   ├── core/               # 核心配置
│   │   ├── config.py       # 全局配置
│   │   ├── deps.py         # 依赖注入
│   │   └── security.py     # 安全相关
│   ├── db/                 # 数据库
│   │   ├── base_class.py   # 基础模型类
│   │   └── session.py      # 数据库会话
│   ├── models/             # 数据模型
│   │   ├── user.py         # 用户模型
│   │   ├── course.py       # 课程模型
│   │   └── exam.py         # 考试模型
│   ├── schemas/            # Pydantic模型
│   │   └── exam.py         # 考试相关Schema
│   ├── services/           # 业务逻辑层
│   │   └── exam_service.py # 考试生成服务
│   └── utils/              # 工具函数
└── main.py                 # 应用入口
```

## 2. 核心组件说明

### 2.1 数据模型 (Models)

#### User Model
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int]
    username: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[str]  # admin/teacher/student
    created_exams: Mapped[List["Exam"]]
```

#### Course Model
```python
class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str]
    teacher_id: Mapped[int]
    exams: Mapped[List["Exam"]]
```

#### Exam Model
```python
class Exam(Base):
    __tablename__ = "exams"
    id: Mapped[int]
    title: Mapped[str]
    course_id: Mapped[int]
    questions: Mapped[List["Question"]]
    status: Mapped[str]  # draft/published
```

### 2.2 依赖注入

```python
# 数据库会话
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 当前用户
async def get_current_user(
    db: Session,
    token: str
) -> User:
    # 验证token并返回用户
```

### 2.3 业务流程

#### 考试生成流程
1. 接收前端请求（课程、知识点、题型配置）
2. 验证教师权限
3. 调用ExamGenerator生成试题
4. 保存到数据库
5. 返回生成结果

```python
@router.post("/generate")
async def generate_exam(
    request: ExamGenerateRequest,
    current_user: User,
    db: Session
) -> ExamCreate
```

## 3. 安全机制

### 3.1 认证
- JWT Token认证
- Token过期时间: 7天
- 刷新Token机制

### 3.2 权限控制
- 基于角色(RBAC)
- 接口级别权限
- 资源所有者验证

## 4. 数据流

```mermaid
graph TD
    A[前端请求] --> B[API路由]
    B --> C{权限验证}
    C -->|通过| D[业务逻辑]
    C -->|失败| E[错误响应]
    D --> F[数据持久化]
    D --> G[调用AI服务]
    F --> H[返回响应]
    G --> H
```

## 5. 错误处理

```python
# HTTP异常
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="权限不足"
)

# 数据库事务
try:
    db.commit()
except SQLAlchemyError:
    db.rollback()
    raise
```

## 6. API响应格式

```json
{
    "code": 0,
    "data": {
        "id": "xxx",
        "title": "xxx"
    },
    "message": "success"
}
```

## 7. 配置管理

通过环境变量配置：
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
MODEL_PATH=/path/to/model
```

## 8. 后续优化方向

1. 缓存层
   - Redis缓存常用数据
   - 试题模板缓存

2. 任务队列
   - Celery处理异步任务
   - 试卷生成任务异步化

3. 日志系统
   - ELK日志收集
   - 操作审计

4. 性能优化
   - 数据库索引优化
   - 批量操作优化
   - N+1查询优化

5. 监控告警
   - 服务健康检查
   - 性能指标监控
   - 异常情况告警

## 9. 开发规范

1. API命名
   - 使用RESTful风格
   - 版本控制：/api/v1/

2. 代码风格
   - 遵循PEP 8
   - 类型注解
   - 文档字符串

3. 提交规范
   - feature: 新功能
   - fix: 修复bug
   - docs: 文档更新
   - style: 代码格式
   - refactor: 重构
   - test: 测试相关
```

这份文档完整描述了后端架构，包括：
1. 清晰的目录结构
2. 核心组件说明
3. 数据流说明
4. 安全机制
5. 错误处理
6. 后续优化方向
7. 开发规范

需要我详细说明任何部分吗？// filepath: /home/laurentzhu/PycharmProjects/CampusAgent/campus-agent/docs/backend/architecture.md
# 后端架构设计说明文档

## 1. 目录结构

```
backend/
├── app/
│   ├── api/                 # API路由层
│   │   └── endpoints/       # 具体API实现
│   │       └── exam.py      # 考试相关接口
│   ├── core/               # 核心配置
│   │   ├── config.py       # 全局配置
│   │   ├── deps.py         # 依赖注入
│   │   └── security.py     # 安全相关
│   ├── db/                 # 数据库
│   │   ├── base_class.py   # 基础模型类
│   │   └── session.py      # 数据库会话
│   ├── models/             # 数据模型
│   │   ├── user.py         # 用户模型
│   │   ├── course.py       # 课程模型
│   │   └── exam.py         # 考试模型
│   ├── schemas/            # Pydantic模型
│   │   └── exam.py         # 考试相关Schema
│   ├── services/           # 业务逻辑层
│   │   └── exam_service.py # 考试生成服务
│   └── utils/              # 工具函数
└── main.py                 # 应用入口
```

## 2. 核心组件说明

### 2.1 数据模型 (Models)

#### User Model
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int]
    username: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[str]  # admin/teacher/student
    created_exams: Mapped[List["Exam"]]
```

#### Course Model
```python
class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int]
    name: Mapped[str]
    description: Mapped[str]
    teacher_id: Mapped[int]
    exams: Mapped[List["Exam"]]
```

#### Exam Model
```python
class Exam(Base):
    __tablename__ = "exams"
    id: Mapped[int]
    title: Mapped[str]
    course_id: Mapped[int]
    questions: Mapped[List["Question"]]
    status: Mapped[str]  # draft/published
```

### 2.2 依赖注入

```python
# 数据库会话
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 当前用户
async def get_current_user(
    db: Session,
    token: str
) -> User:
    # 验证token并返回用户
```

### 2.3 业务流程

#### 考试生成流程
1. 接收前端请求（课程、知识点、题型配置）
2. 验证教师权限
3. 调用ExamGenerator生成试题
4. 保存到数据库
5. 返回生成结果

```python
@router.post("/generate")
async def generate_exam(
    request: ExamGenerateRequest,
    current_user: User,
    db: Session
) -> ExamCreate
```

## 3. 安全机制

### 3.1 认证
- JWT Token认证
- Token过期时间: 7天
- 刷新Token机制

### 3.2 权限控制
- 基于角色(RBAC)
- 接口级别权限
- 资源所有者验证

## 4. 数据流

```mermaid
graph TD
    A[前端请求] --> B[API路由]
    B --> C{权限验证}
    C -->|通过| D[业务逻辑]
    C -->|失败| E[错误响应]
    D --> F[数据持久化]
    D --> G[调用AI服务]
    F --> H[返回响应]
    G --> H
```

## 5. 错误处理

```python
# HTTP异常
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="权限不足"
)

# 数据库事务
try:
    db.commit()
except SQLAlchemyError:
    db.rollback()
    raise
```

## 6. API响应格式

```json
{
    "code": 0,
    "data": {
        "id": "xxx",
        "title": "xxx"
    },
    "message": "success"
}
```

## 7. 配置管理

通过环境变量配置：
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
MODEL_PATH=/path/to/model
```

## 8. 后续优化方向

1. 缓存层
   - Redis缓存常用数据
   - 试题模板缓存

2. 任务队列
   - Celery处理异步任务
   - 试卷生成任务异步化

3. 日志系统
   - ELK日志收集
   - 操作审计

4. 性能优化
   - 数据库索引优化
   - 批量操作优化
   - N+1查询优化

5. 监控告警
   - 服务健康检查
   - 性能指标监控
   - 异常情况告警

## 9. 开发规范

1. API命名
   - 使用RESTful风格
   - 版本控制：/api/v1/

2. 代码风格
   - 遵循PEP 8
   - 类型注解
   - 文档字符串

3. 提交规范
   - feature: 新功能
   - fix: 修复bug
   - docs: 文档更新
   - style: 代码格式
   - refactor: 重构
   - test: 测试相关
```

这份文档完整描述了后端架构，包括：
1. 清晰的目录结构
2. 核心组件说明
3. 数据流说明
4. 安全机制
5. 错误处理
6. 后续优化方向
7. 开发规范

需要我详细说明任何部分吗？