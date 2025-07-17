<template>
  <div class="exam-generator-container">
    <h1>智能试卷生成</h1>
    <p>根据课程知识点和题型配置生成试卷。</p>

    <div class="input-section">
      <h2>上传知识材料（可选）</h2>
      <input type="file" @change="handleFileUpload" accept=".pdf,.docx,.txt" />
      <button @click="uploadMaterials">上传</button>
      <p v-if="fileName">已选择文件: {{ fileName }}</p>
    </div>

    <div class="input-section">
      <h2>试卷配置</h2>

      <label>
        选择课程:<span style="color: red;">*</span>
      </label>
      <el-select
        v-model="examConfig.courseId"
        placeholder="请选择课程"
        @change="onCourseChange"
        style="width: 100%; margin-bottom: 15px;"
        required
      >
        <el-option
          v-for="course in courseOptions"
          :key="course.id"
          :label="course.name"
          :value="course.id"
        />
      </el-select>

      <label>知识点:<span style="color: red;">*</span></label>
      <el-select
        v-model="examConfig.knowledgePoints"
        multiple
        placeholder="请选择知识点"
        :disabled="!examConfig.courseId"
        style="width: 100%; margin-bottom: 15px;"
        required
      >
        <el-option
          v-for="point in currentKnowledgePoints"
          :key="point"
          :label="point"
          :value="point"
        />
      </el-select>

      <label>题型配置:</label>
      <div v-for="type in questionTypes" :key="type.value" style="margin-bottom: 8px; display: flex; align-items: center;">
        <span>{{ type.label }}</span>
        <el-input-number
          v-model="examConfig.questionTypes[type.value]"
          :min="0"
          style="margin-left: 12px; width: 150px;"
        />
        <span style="margin-left: 16px;">分值：</span>
        <el-input-number
          v-model="examConfig.questionScores[type.value]"
          :min="1"
          style="margin-left: 4px; width: 150px;"
        />
      </div>
      <div style="margin: 12px 0; font-weight: bold; color: #007bff;">
        当前试卷总分：{{ totalScore }} 分
      </div>

      <el-input
        type="textarea"
        v-model="examConfig.customKnowledgePoints"
        placeholder="可自定义知识点，每行一个"
        :rows="3"
        style="margin-bottom: 15px;"
      />
      <el-input
        v-model="examConfig.examTitle"
        placeholder="请输入试卷名称（可选）"
        style="margin-bottom: 15px;"
      />

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
          :disabled="loading || !examConfig.courseId || !examConfig.knowledgePoints.length"
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
        <div v-if="isSectionTitle(q.content)" style="font-weight:bold; margin:8px 0; white-space:pre-line;">
          {{ getSectionTitle(q.content) }}
        </div>
        <div v-for="line in q.content.split('\n')" :key="line" style="white-space: pre-line;">
          {{ line }}
        </div>
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
import mammoth from "mammoth";
// import * as pdfjsLib from "pdfjs-dist/build/pdf";
// import pdfjsWorker from "pdfjs-dist/build/pdf.worker.entry";

// pdfjsLib.GlobalWorkerOptions.workerSrc = pdfjsWorker;
import * as pdfjsLib from "pdfjs-dist/build/pdf";
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export default {
  name: 'ExamGenerator',
  data() {
    return {
      loading: false,
      errorMessage: '',
      examData: null,
      selectedFile: null,
      fileName: '',
      uploadedFileContent: '', // 新增
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
        questionScores: { // 新增
          single_choice: 5,
          multiple_choice: 5,
          true_false: 5,
          completion: 5,
          case_analysis: 10,
          programming: 20
        },
        difficulty: 3,
        customKnowledgePoints: '', // 新增
        examTitle: '' // 新增
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
    },
    totalScore() {
      let sum = 0;
      for (const type of this.questionTypes) {
        const count = Number(this.examConfig.questionTypes[type.value]) || 0;
        const score = Number(this.examConfig.questionScores[type.value]) || 0;
        sum += count * score;
      }
      return sum;
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
    async handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
      this.fileName = this.selectedFile?.name || '';
      this.uploadedFileContent = '';

      if (!this.selectedFile) return;

      const file = this.selectedFile;
      const ext = file.name.split('.').pop().toLowerCase();

      if (ext === 'txt') {
        // 纯文本
        const reader = new FileReader();
        reader.onload = (e) => {
          this.uploadedFileContent = e.target.result;
        };
        reader.readAsText(file);
      } else if (ext === 'docx') {
        // Word
        const arrayBuffer = await file.arrayBuffer();
        const result = await mammoth.extractRawText({ arrayBuffer });
        this.uploadedFileContent = result.value;
      } else if (ext === 'pdf') {
        // PDF
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        let text = '';
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          text += content.items.map(item => item.str).join(' ') + '\n';
        }
        this.uploadedFileContent = text;
      } else {
        this.errorMessage = '暂不支持该文件类型';
      }
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
        await axios.post('/api/fastapi/v1/upload-materials', formData, {
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
      if (!this.examConfig.courseId) {
        this.errorMessage = '请选择课程后再生成试卷。';
        return;
      }
      if (!this.examConfig.knowledgePoints || this.examConfig.knowledgePoints.length === 0) {
        this.errorMessage = '请选择知识点后再生成试卷。';
        return;
      }
      this.loading = true
      this.errorMessage = ''
      try {
        const customPoints = this.examConfig.customKnowledgePoints
          ? this.examConfig.customKnowledgePoints.split('\n').map(s => s.trim()).filter(Boolean)
          : [];
        const allKnowledgePoints = [...this.examConfig.knowledgePoints, ...customPoints];

        const token = localStorage.getItem('token')
        const res = await axios.post(
          '/api/fastapi/v1/exams/generate',
          {
            course_id: this.examConfig.courseId,
            knowledge_points: allKnowledgePoints,
            question_types: this.examConfig.questionTypes,
            question_scores: this.examConfig.questionScores, // 传递分值
            difficulty: this.examConfig.difficulty,
            exam_title: this.examConfig.examTitle || undefined,
            extra_context: this.uploadedFileContent || undefined // 新增
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
          '/api/fastapi/v1/exams/generate-pdf',
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
          '/api/fastapi/v1/exams/generate-word',
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
    },
    isSectionTitle(content) {
      return content.startsWith('### ') || content.startsWith('## ') || content.startsWith('# ');
    },
    getSectionTitle(content) {
      if (content.startsWith('### ')) {
        return content.substring(4);
      } else if (content.startsWith('## ')) {
        return content.substring(3);
      } else if (content.startsWith('# ')) {
        return content.substring(2);
      }
      return content;
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
