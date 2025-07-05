<template>
  <el-card class="evaluation-card">
    <template #header>
      <div class="evaluation-header">
        <span>答案批改结果</span>
        <el-tag :type="result.isCorrect ? 'success' : 'danger'">
          {{ result.isCorrect ? '正确' : '错误' }}
        </el-tag>
      </div>
    </template>
    
    <div class="evaluation-content">
      <el-row :gutter="20">
        <el-col :span="12">
          <h4>你的答案：</h4>
          <div class="answer-box">{{ result.userAnswer }}</div>
        </el-col>
        <el-col :span="12">
          <h4>参考答案：</h4>
          <div class="answer-box">{{ result.correctAnswer }}</div>
        </el-col>
      </el-row>
      
      <div class="feedback-section">
        <h4>详细解析：</h4>
        <div v-html="result.analysis"></div>
      </div>
      
      <div class="suggestion-section">
        <h4>学习建议：</h4>
        <div v-html="result.suggestion"></div>
      </div>
    </div>
    
    <div class="evaluation-footer">
      <el-button type="primary" @click="$emit('next')">
        继续练习
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    required: true,
    default: () => ({
      isCorrect: false,
      userAnswer: '',
      correctAnswer: '',
      analysis: '',
      suggestion: ''
    })
  }
})
</script>

<style scoped>
.evaluation-card {
  margin-bottom: 20px;
}
.evaluation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.answer-box {
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  min-height: 50px;
}
.feedback-section,
.suggestion-section {
  margin-top: 20px;
}
.evaluation-footer {
  margin-top: 20px;
  text-align: right;
}
</style>