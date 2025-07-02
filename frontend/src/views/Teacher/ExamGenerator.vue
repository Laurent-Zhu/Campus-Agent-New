<template>
  <div class="exam-generator-container">
    <h1>智能试卷生成</h1>
    <p>根据课程知识点和题型配置生成试卷。</p>

    <div class="input-section">
      <h2>上传知识材料（可选）</h2>
      <input type="file" @change="handleFileUpload" accept=".pdf,.docx" />
      <button @click="uploadMaterials">上传</button>
      <p v-if="fileName">已选择文件: {{ fileName }}</p>
    </div>

    <div class="input-section">
      <h2>试卷配置</h2>

      <label>选择课程:</label>
      <el-select
        v-model="examConfig.courseId"
        placeholder="请选择课程"
        @change="onCourseChange"
        style="width: 100%; margin-bottom: 15px;"
      >
        <el-option
          v-for="course in courseOptions"
          :key="course.id"
          :label="course.name"
          :value="course.id"
        />
      </el-select>

      <label>知识点:</label>
      <el-select
        v-model="examConfig.knowledgePoints"
        multiple
        placeholder="请选择知识点"
        :disabled="!examConfig.courseId"
        style="width: 100%; margin-bottom: 15px;"
      >
        <el-option
          v-for="point in currentKnowledgePoints"
          :key="point"
          :label="point"
          :value="point"
        />
      </el-select>

      <label>题型配置:</label>
      <div v-for="type in questionTypes" :key="type.value" style="margin-bottom: 8px;">
        <span>{{ type.label }}</span>
        <el-input-number
          v-model="examConfig.questionTypes[type.value]"
          :min="0"
          :max="10"
          style="margin-left: 12px;"
        />
      </div>

      <!-- <label>难度等级:</label>
      <el-rate v-model="examConfig.difficulty" :max="5" style="margin-bottom: 15px;" />

      <button @click="generateExam" :disabled="loading">生成试卷</button> -->
      <div class="difficulty-section" style="margin-bottom: 20px;">
        <label for="difficulty">难度等级:</label>
        <el-rate
          id="difficulty"
          v-model="examConfig.difficulty"
          :max="5"
          :colors="['#ff4d4f', '#ffa940', '#52c41a']"
          style="display: block; margin-top: 8px; margin-bottom: 15px;"
        />
      </div>

      <div class="action-buttons" style="display: flex; justify-content: flex-start; gap: 10px;">
        <button
          @click="generateExam"
          :disabled="loading"
          class="primary-button"
        >
          {{ loading ? '正在生成...' : '生成试卷' }}
        </button>
        <button
          @click="resetForm"
          :disabled="loading"
          class="secondary-button"
        >
          重置
        </button>
      </div>
    </div>

    <!-- <div v-if="examData" class="output-section">
      <h2>试卷预览</h2>
      <h3>{{ examData.title }}</h3>
      <div v-for="(q, idx) in examData.questions" :key="q.id" style="margin-bottom: 16px;">
        <div><b>Q{{ idx + 1 }} ({{ q.type }})：</b>{{ q.content }}</div>
        <div v-if="q.options" style="margin-left: 12px;">
          <div v-for="(opt, i) in q.options" :key="i">{{ opt }}</div>
        </div>
        <div><b>答案：</b>{{ q.answer }}</div>
        <div><b>解析：</b>{{ q.analysis }}</div>
      </div>
    </div> -->
    <div v-if="examData" class="output-section">
      <h2>试卷预览</h2>
      <h3>{{ examData.title }}</h3>
      <div class="download-buttons" style="display: flex; gap: 10px; margin-bottom: 16px;">
        <button @click="handleDownloadPDF(false)">下载试题(.pdf)</button>
        <button @click="handleDownloadPDF(true)">下载试题+答案解析(.pdf)</button>
        <button @click="handleDownloadWORD(false)">下载试题(.docx)</button>
        <button @click="handleDownloadWORD(true)">下载试题+答案解析(.docx)</button>
      </div>
      <div v-for="(q, idx) in examData.questions" :key="q.id" style="margin-bottom: 16px; text-align: left;">
        <div><b>Q{{ idx + 1 }} ({{ q.type }})：</b>{{ q.content }}</div>
        <div v-if="q.options" style="margin-left: 12px; text-align: left;">
          <div v-for="(opt, i) in q.options" :key="i">{{ opt }}</div>
        </div>
        <div style="text-align: left;"><b>答案：</b>{{ q.answer }}</div>
        <div style="text-align: left;"><b>解析：</b>{{ q.analysis }}</div>
      </div>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="loading" class="loading-message">正在生成试卷，请稍候...</p>
  </div>
</template>

<script>
import axios from 'axios'
import { useExamStore } from '@/stores/exam'

export default {
  name: 'ExamGenerator',
  data() {
    return {
      loading: false,
      errorMessage: '',
      examData: null,
      selectedFile: null,
      fileName: '',
      examConfig: {
        courseId: '',
        knowledgePoints: [],
        questionTypes: {
          single_choice: 0,
          multiple_choice: 0,
          true_false: 0,
          completion: 0,
          case_analysis: 0,
          programming: 0
        },
        difficulty: 3
      },
      questionTypes: [
        { value: 'single_choice', label: '单选题' },
        { value: 'multiple_choice', label: '多选题' },
        { value: 'true_false', label: '判断题' },
        { value: 'completion', label: '填空题' },
        { value: 'case_analysis', label: '案例分析题' },
        { value: 'programming', label: '编程题' }
      ]
    }
  },
  computed: {
    examStore() {
      return useExamStore()
    },
    courseOptions() {
      console.log('课程选项:', this.examStore.courseOptions)
      return this.examStore.courseOptions
    },
    knowledgePointMap() {
      console.log('知识点映射:', this.examStore.knowledgePointMap)
      return this.examStore.knowledgePointMap
    },
    currentKnowledgePoints() {
      console.log('当前知识点:', this.examConfig.courseId ? this.knowledgePointMap[this.examConfig.courseId] : [])
      return this.examConfig.courseId
        ? this.knowledgePointMap[this.examConfig.courseId] || []
        : []
    }
  },
  created() {
    // 方法一：在组件中注入课程和知识点数据
    const store = this.examStore
    console.log('courseOptions from store:', this.courseOptions)
    console.log('knowledgePointMap from store:', this.knowledgePointMap)
    store.courseOptions = [...store.courseOptions] // 强制触发响应式更新
    store.knowledgePointMap = { ...store.knowledgePointMap } // 强制触发响应式更新
    if (!store.courseOptions.length) {
      store.courseOptions = [
        { id: 1, name: 'TensorFlow.js应用开发' },
        { id: 2, name: 'TensorFlow Lite部署' },
        { id: 3, name: '嵌入式Python开发' }
      ]
    }
    if (Object.keys(store.knowledgePointMap).length === 0) {
      store.knowledgePointMap = {
        1: ['浏览器端部署', 'tfjs-vis', 'CNN'],
        2: ['量化优化', '模型转换器', 'PoseNet'],
        3: ['树莓派', 'Jetson Nano', 'OpenCV']
      }
    }
    console.log('课程初始化完成:', store.courseOptions)
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0]
      this.fileName = this.selectedFile?.name || ''
    },
    async uploadMaterials() {
      if (!this.selectedFile) {
        this.errorMessage = '请选择要上传的文件。'
        return
      }
      this.loading = true
      this.errorMessage = ''
      const formData = new FormData()
      formData.append('file', this.selectedFile)

      try {
        await axios.post('/api/v1/upload-materials', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        alert('文件上传成功！')
      } catch (error) {
        console.error(error)
        this.errorMessage = '文件上传失败，请重试。'
      } finally {
        this.loading = false
      }
    },
    onCourseChange() {
      this.examConfig.knowledgePoints = []
    },
    async generateExam() {
      this.loading = true
      this.errorMessage = ''
      try {
        const token = localStorage.getItem('token')
        const res = await axios.post(
          '/api/v1/exams/generate',
          {
            course_id: this.examConfig.courseId,
            knowledge_points: this.examConfig.knowledgePoints,
            question_types: this.examConfig.questionTypes,
            difficulty: this.examConfig.difficulty
          },
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        )
        this.examData = res.data
      } catch (error) {
        this.examData = null
        this.errorMessage = error?.response?.data?.detail || '生成失败'
      } finally {
        this.loading = false
      }
    },
    async handleDownloadPDF(includeAnalysis) {
      if (!this.examData) return
      try {
        const res = await axios.post(
          '/api/v1/exams/generate-pdf',
          this.examData,
          {
            params: { include_analysis: includeAnalysis },
            responseType: 'blob'
          }
        )
        const blob = new Blob([res.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${this.examData.title || 'exam'}${includeAnalysis ? '_with_analysis' : ''}.pdf`
        a.click()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        this.errorMessage = 'PDF 下载失败，请重试。'
      }
    },
    async handleDownloadWORD(includeAnalysis) {
      if (!this.examData) return
      try {
        const res = await axios.post(
          '/api/v1/exams/generate-word',
          this.examData,
          {
            params: { include_analysis: includeAnalysis },
            responseType: 'blob'
          }
        )
        const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${this.examData.title || 'exam'}${includeAnalysis ? '_with_analysis' : ''}.docx`
        a.click()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        this.errorMessage = 'Word 下载失败，请重试。'
      }
    }
  }
}
</script>

<style scoped>
.exam-generator-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 20px;
}

.input-section,
.output-section {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

h2 {
  color: #555;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

input[type='file'],
textarea {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  background-color: #007bff;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  margin-right: 10px;
}

button:hover {
  background-color: #0056b3;
}

.output-section {
  background-color: #e6ffe6;
  border-color: #a3e6a3;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.loading-message {
  color: #007bff;
  margin-top: 10px;
}
</style>
