<template>
  <div class="lesson-preparation-container">
    <h1>智能备课与教学设计</h1>

    <p>根据本地课程大纲、课程知识库文档等智能设计教学内容。</p>

    <div class="input-section">
      <h2>输入教学材料</h2>
      <input type="file" @change="handleFileUpload" accept=".pdf,.docx">
      <!-- <button @click="uploadMaterials">上传</button> -->
      <p v-if="fileName">已选择文件: {{ fileName }}</p>
    </div>

    <div class="design-options">
      <h2>设计选项</h2>
      <label for="courseOutline">课程大纲:</label>
      <textarea id="courseOutline" v-model="courseOutline" rows="5" placeholder="粘贴或输入课程大纲..."></textarea>

      <label for="teachingGoals">教学目标:</label>
      <textarea id="teachingGoals" v-model="teachingGoals" rows="3" placeholder="输入教学目标..."></textarea>

      <button @click="uploadAndGenerate">上传并生成备课内容</button>
    </div>

    <div v-if="lessonPlan" class="output-section">
      <h2>生成的备课内容</h2>
      <pre>{{ lessonPlan }}</pre>

      <div v-if="lessonPlan.structured_draft">
        <h3>课件草稿</h3>
        <div>标题：{{ lessonPlan.structured_draft.title }}</div>
        <div v-for="(mod, idx) in lessonPlan.structured_draft.modules" :key="idx">
          <strong>模块{{ idx+1 }}：</strong>{{ mod.name }}
          <ul>
            <li v-for="(point, pidx) in mod.points" :key="pidx">
              {{ point }}
            </li>
          </ul>
        </div>
      </div>
      <div v-if="lessonPlan.training_plan">
        <h3>实训计划</h3>
        <div>
          <strong>知识目标：</strong>
          <ul>
            <li v-for="(k, idx) in lessonPlan.training_plan.objectives.knowledge" :key="idx">{{ k }}</li>
          </ul>
          <strong>技能目标：</strong>
          <ul>
            <li v-for="(s, idx) in lessonPlan.training_plan.objectives.skills" :key="idx">{{ s }}</li>
          </ul>
          <strong>任务：</strong>
          <ul>
            <li v-for="(t, idx) in lessonPlan.training_plan.tasks" :key="idx">{{ t }}</li>
          </ul>
        </div>
      </div>
      <div v-if="lessonPlan.schedule">
        <h3>时间安排表</h3>
        <div>总课时：{{ lessonPlan.schedule.total_hours }}</div>
        <ul>
          <li v-for="(item, idx) in lessonPlan.schedule.details" :key="idx">
            第{{ item.hour }}小时：{{ item.activity }}
          </li>
        </ul>
      </div>

      <a v-if="pptxUrl" :href="pptxUrl" target="_blank" download>下载PPT</a>
      <!-- <button @click="downloadLessonPlan">下载备课内容</button> -->
      <!-- <button @click="editLessonPlan">手动调整</button> -->

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
      errorMessage: '',
      pptxUrl: null
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
    async  uploadAndGenerate() { 
      if(!this.selectedFile && (!this.courseOutline || !this.teachingGoals)){
        this.errorMessage = '请上传文件或填写课程大纲和教学目标。';
        return;
      }
      this.loading = true;
      this.errorMessage = '';
      const formData = new FormData();
      if(this.selectedFile) formData.append('file', this.selectedFile);
      formData.append('course_outline', this.courseOutline);
      formData.append('teaching_goals', this.teachingGoals);

      try {
        const response = await axios.post('/api/django/teacher/lesson-preparation/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        // JSON 解析和美化
        console.log('后端返回：', response.data);
        let data = response.data;
        if (typeof data === 'string') {
          data = data.replace(/```json|```/g, '');
          try {
            data = JSON.parse(data);
          } catch(e) {
            this.errorMessage = '返回解析内容失败，请重试。';
            return;
          }
        }
        this.lessonPlan = data;
        this.pptxUrl = response.data.pptx_url;
        console.log('lessonPlan:', this.lessonPlan);
      } catch (error) {
        // console.error('Error generating lesson plan:', error);
        this.errorMessage= error.response?.data?.error || '生成备课内容失败，请重试。';
      } finally {
        this.loading = false;
      }
    }

    // downloadLessonPlan() {
    //   // coding here
    //   alert('下载功能待实现。');
    // },
    // editLessonPlan() {
    //   // coding here
    //   alert('手动调整功能待实现。');
    // }
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