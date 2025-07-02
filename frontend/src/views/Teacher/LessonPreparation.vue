<template>
  <div class="lesson-preparation-container">
    <h1>智能备课与教学设计</h1>

    <p>根据本地课程大纲、课程知识库文档等智能设计教学内容。</p>

    <div class="input-section">
      <h2>输入教学材料</h2>
      <input type="file" @change="handleFileUpload" accept=".pdf,.docx">
      <button @click="uploadMaterials">上传</button>
      <p v-if="fileName">已选择文件: {{ fileName }}</p>
    </div>

    <div class="design-options">
      <h2>设计选项</h2>
      <label for="courseOutline">课程大纲:</label>
      <textarea id="courseOutline" v-model="courseOutline" rows="5" placeholder="粘贴或输入课程大纲..."></textarea>

      <label for="teachingGoals">教学目标:</label>
      <textarea id="teachingGoals" v-model="teachingGoals" rows="3" placeholder="输入教学目标..."></textarea>

      <button @click="generateLessonPlan">生成备课内容</button>
    </div>

    <div v-if="lessonPlan" class="output-section">
      <h2>生成的备课内容</h2>
      <div v-html="lessonPlan"></div>
      <button @click="downloadLessonPlan">下载备课内容</button>
      <button @click="editLessonPlan">手动调整</button>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="loading" class="loading-message">正在生成备课内容，请稍候...</p>

  </div>
</template>

<script>
import axios from 'axios'; // Import axios

export default {
  name: 'LessonPreparation',
  data() {
    return {
      selectedFile: null, 
      fileName: '',
      courseOutline: '', 
      teachingGoals: '',
      lessonPlan: null,
      loading: false,
      errorMessage: ''
    };
  },
  methods: {
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
      if (this.selectedFile) {
        this.fileName = this.selectedFile.name;
      } else {
        this.fileName = '';
      }
    },
    async uploadMaterials() {
      if (!this.selectedFile) {
        this.errorMessage = '请选择要上传的文件。';
        return;
      }

      this.loading = true;
      this.errorMessage = '';

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      try {
        // Replace with your Django backend API endpoint for file upload
        const response = await axios.post('YOUR_DJANGO_BACKEND_API/upload-materials/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        console.log('File uploaded successfully:', response.data);
        // You might want to store some ID or confirmation from the backend
        alert('文件上传成功！');
      } catch (error) {
        console.error('Error uploading file:', error);
        this.errorMessage = '文件上传失败，请重试。';
      } finally {
        this.loading = false;
      }
    },
    async generateLessonPlan() {
      this.loading = true;
      this.errorMessage = '';
      this.lessonPlan = null;

      try {
        // This is where you'd call your Django backend API that interacts with the LangChain agent.
        // The backend would handle:
        // - Loading content (from uploaded file or text input) 
        // - Using LangChain + Document Loader 
        // - Using RetrievalQA/QAChain with Prompt templates to generate the lesson plan 
        const response = await axios.post('YOUR_DJANGO_BACKEND_API/generate-lesson-plan/', {
          course_outline: this.courseOutline,
          teaching_goals: this.teachingGoals,
          // You might send a reference to the uploaded file here if applicable
          // file_id: <id_from_upload>
        });

        this.lessonPlan = response.data.lesson_plan_html; // Assuming backend returns HTML or Markdown
      } catch (error) {
        console.error('Error generating lesson plan:', error);
        this.errorMessage = '生成备课内容失败，请重试。';
      } finally {
        this.loading = false;
      }
    },
    downloadLessonPlan() {
      // Implement logic to download the generated lesson plan (e.g., as a PDF or DOCX)
      // This might involve creating a blob from the lessonPlan content and triggering a download.
      // Or, your Django backend could provide a dedicated download endpoint.
      alert('下载功能待实现。');
    },
    editLessonPlan() {
      // Implement logic to allow manual adjustment of the lesson plan.
      // You could convert the lessonPlan content into a textarea for editing.
      alert('手动调整功能待实现。');
    }
  }
};
</script>

<style scoped>
.lesson-preparation-container {
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

.input-section, .design-options, .output-section {
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

input[type="file"],
textarea {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* Ensures padding doesn't add to width */
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