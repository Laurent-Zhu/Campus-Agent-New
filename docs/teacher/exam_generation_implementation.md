# 教师端考核生成功能实现文档

## 1. 功能概述

教师端考核生成功能允许教师选择课程、知识点、题型和难度等参数，通过智谱 AI API 自动生成考试试卷。目前已实现:

- 前端考试生成界面
- 后端生成 API
- 数据库存储
- AI 模型调用

## 2. 前端实现

### 2.1 考试生成页面 (ExamGenerator.vue)

```vue
<template>
  <div class="exam-generator">
    <el-card class="form-card">
      <!-- 生成配置表单 -->
      <el-form :model="examConfig" label-width="120px">
        <el-form-item label="选择课程">
          <el-select v-model="examConfig.courseId" placeholder="请选择课程">
            <el-option
              v-for="course in courseOptions"
              :key="course.id" 
              :label="course.name"
              :value="course.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="知识点">
          <el-select v-model="examConfig.knowledgePoints" multiple>
            <el-option
              v-for="point in knowledgePoints"
              :key="point"
              :label="point" 
              :value="point"
            />
          </el-select>
        </el-form-item>

        <!-- 题型配置 -->
        <el-form-item label="题型配置">
          <div v-for="type in questionTypes" :key="type.value">
            <span>{{type.label}}</span>
            <el-input-number 
              v-model="examConfig.questionTypes[type.value]"
              :min="0"
              :max="10"
            />
          </div>
        </el-form-item>

        <el-form-item label="难度等级">
          <el-rate v-model="examConfig.difficulty" :max="5"/>
        </el-form-item>

        <el-button type="primary" @click="handleGenerate">
          生成试卷
        </el-button>
      </el-form>
    </el-card>

    <!-- 预览试卷 -->
    <el-card v-if="examData" class="preview-card">
      <template #header>
        <div class="card-header">
          <span>试卷预览</span>
          <div>
            <el-button type="primary" @click="handleSave">保存</el-button>
            <el-button @click="handleExport">导出</el-button>
          </div>
        </div>
      </template>

      <div class="exam-preview">
        <!-- 试卷内容展示 -->
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useExamStore } from '@/stores/exam'

const examStore = useExamStore()
const examConfig = ref({
  courseId: '',
  knowledgePoints: [],
  questionTypes: {
    choice: 0,
    completion: 0,
    programming: 0
  },
  difficulty: 3
})

// 生成试卷
const handleGenerate = async () => {
  try {
    const result = await examStore.generateExam(examConfig.value)
    examData.value = result
  } catch (error) {
    ElMessage.error(error.message)
  }
}
</script>
```

### 2.2 状态管理 (exam.js)

```javascript
import { defineStore } from 'pinia'
import axios from 'axios'

export const useExamStore = defineStore('exam', {
  state: () => ({
    examList: [],
    currentExam: null,
    courseOptions: [
      { id: 1, name: '计算机网络' },
      { id: 2, name: '操作系统' },
      { id: 3, name: '数据结构' }
    ],
    knowledgePointMap: {
      1: ['TCP/IP协议', '网络安全', '路由协议'],
      2: ['进程管理', '内存管理', '文件系统'],
      3: ['链表', '树', '图', '排序算法']
    }
  }),
  
  actions: {
    async generateExam(config) {
      const response = await axios.post('/api/v1/exams/generate', config)
      return response.data
    }
  }
})
```

## 3. 后端实现

### 3.1 数据模型

```python
# models/exam.py
class Exam(Base):
    __tablename__ = "exams"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    title: Mapped[str] = Column(String(100))
    description: Mapped[str] = Column(Text)
    course_id: Mapped[int] = Column(Integer, ForeignKey("courses.id"))
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = Column(DateTime)
    duration: Mapped[int] = Column(Integer)
    total_score: Mapped[int] = Column(Integer)
    status: Mapped[str] = Column(String(20))
    
    questions: Mapped[list["Question"]] = relationship("Question", back_populates="exam")

class Question(Base):
    __tablename__ = "questions"
    
    id: Mapped[int] = Column(Integer, primary_key=True)
    exam_id: Mapped[int] = Column(Integer, ForeignKey("exams.id"))
    type: Mapped[str] = Column(String(20))
    content: Mapped[str] = Column(Text)
    options: Mapped[str] = Column(Text)
    answer: Mapped[str] = Column(Text)
    analysis: Mapped[str] = Column(Text)
    score: Mapped[int] = Column(Integer)
    knowledge_point: Mapped[str] = Column(String(100))
    difficulty: Mapped[int] = Column(Integer)
```

### 3.2 API 实现

```python
# api/endpoints/exam.py
@router.post("/generate", response_model=ExamCreate)
async def generate_exam(
    request: ExamGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成考试题目"""
    try:
        agent = AgentFactory.create_agent("exam_generator")
        
        questions = await agent.arun(
            course=request.course_id,
            knowledge_points=request.knowledge_points,
            question_types=request.question_types,
            difficulty=request.difficulty
        )
        
        exam = ExamCreate(
            title=f"AI生成的考试-{datetime.now()}",
            course_id=request.course_id,
            questions=questions,
            total_score=sum(q.score for q in questions),
            duration=120
        )
        
        return exam
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3.3 AI 生成服务

```python
# services/exam_service.py
class ExamGenerator:
    def __init__(self):
        self.client = ChatGLMClient()
    
    async def _generate_question(
        self,
        knowledge_point: str,
        question_type: str,
        difficulty: int
    ) -> Question:
        prompt = f"""
        请生成一道考试题:
        知识点: {knowledge_point}
        题型: {question_type}
        难度等级: {difficulty}/5
        
        返回JSON格式包含:
        1. content: 题目内容
        2. options: 选项列表
        3. answer: 标准答案
        4. analysis: 解题思路
        """
        
        response = await self.client.generate_text(prompt)
        result = json.loads(response)
        
        return Question(
            type=question_type,
            content=result["content"],
            options=result.get("options"),
            answer=result["answer"],
            analysis=result["analysis"],
            difficulty=difficulty,
            knowledge_point=knowledge_point,
            score=self._calculate_score(question_type)
        )
```

## 4. 调用智谱 AI API

```python
# utils/model_client.py
class ChatGLMClient:
    def __init__(self):
        self.config = ModelConfig()
        self.api_key = self.config.API_KEY
        self.client = httpx.AsyncClient(
            base_url=self.config.API_BASE_URL,
            headers={
                "Authorization": self._generate_auth_string(),
                "Content-Type": "application/json"
            }
        )
    
    async def generate_text(self, prompt: str) -> str:
        request_data = {
            "model": self.config.API_VERSION,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        
        response = await self.client.post("/invoke", json=request_data)
        result = response.json()
        
        return result["data"]["choices"][0]["content"]
```

## 5. 数据库结构

### 5.1 试卷表(exams)
```sql
CREATE TABLE exams (
    id INTEGER PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    course_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    duration INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY(course_id) REFERENCES courses(id),
    FOREIGN KEY(created_by) REFERENCES users(id)
);
```

### 5.2 题目表(questions)
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    exam_id INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    options TEXT,
    answer TEXT NOT NULL,
    analysis TEXT,
    score INTEGER NOT NULL,
    knowledge_point VARCHAR(100) NOT NULL,
    difficulty INTEGER NOT NULL,
    FOREIGN KEY(exam_id) REFERENCES exams(id)
);
```

## 6. 环境配置

### 6.1 前端依赖
```json
{
  "dependencies": {
    "@element-plus/icons-vue": "^2.3.1",
    "axios": "^1.10.0",
    "element-plus": "^2.10.2",
    "pinia": "^3.0.3",
    "vue": "^3.5.17",
    "vue-router": "^4.5.1"
  }
}
```

### 6.2 后端依赖
```python
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
httpx==0.25.2
python-jose==3.3.0
```

### 6.3 环境变量
```env
ZHIPU_API_KEY=your-api-key
MODEL_NAME=chatglm_turbo
DATABASE_URL=sqlite:///./campus_agent.db
```

