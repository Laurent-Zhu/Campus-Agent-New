<!-- 题目生成组件 -->
<template>
  <el-card class="exercise-card">
    <template #header>
      <div class="exercise-header">
        <span class="knowledge-tag">{{ exercise.knowledgePoint }}</span>
        <span class="difficulty-tag">{{ formatDifficulty(exercise.difficulty) }}</span>
      </div>
    </template>
    
    <div class="exercise-content">
      <div v-html="exercise.content"></div>
      
      <!-- 选择题 -->
      <el-radio-group 
        v-if="exercise.type === 'multiple_choice'"
        v-model="selectedOption"
      >
        <el-radio 
          v-for="(option, index) in exercise.options" 
          :key="index"
          :label="option"
          class="option-item"
        >
          {{ option }}
        </el-radio>
      </el-radio-group>
      
      <!-- 填空题 -->
      <el-input
        v-else-if="exercise.type === 'fill_blank'"
        v-model="fillAnswer"
        placeholder="请输入你的答案"
      />
      
      <!-- 主观题 -->
      <el-input
        v-else
        v-model="subjectiveAnswer"
        type="textarea"
        :rows="5"
        placeholder="请详细作答..."
      />
    </div>
    
    <div class="exercise-footer">
      <el-button 
        type="primary" 
        @click="handleSubmit"
        :disabled="!isAnswerValid"
      >
        提交答案
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  exercise: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['submit'])

const selectedOption = ref('')
const fillAnswer = ref('')
const subjectiveAnswer = ref('')

const isAnswerValid = computed(() => {
  switch (props.exercise.type) {
    case 'multiple_choice':
      return selectedOption.value !== ''
    case 'fill_blank':
      return fillAnswer.value.trim() !== ''
    default:
      return subjectiveAnswer.value.trim() !== ''
  }
})

const handleSubmit = () => {
  let answer
  switch (props.exercise.type) {
    case 'multiple_choice':
      answer = selectedOption.value
      break
    case 'fill_blank':
      answer = fillAnswer.value
      break
    default:
      answer = subjectiveAnswer.value
  }
  emit('submit', answer)
}

const formatDifficulty = (level) => {
  const map = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return map[level] || level
}
</script>

<style scoped>
.exercise-card {
  margin-bottom: 20px;
}
.exercise-header {
  display: flex;
  justify-content: space-between;
}
.knowledge-tag {
  background-color: #409eff;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.difficulty-tag {
  background-color: #67c23a;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.option-item {
  display: block;
  margin: 10px 0;
}
.exercise-footer {
  margin-top: 20px;
  text-align: right;
}
</style>