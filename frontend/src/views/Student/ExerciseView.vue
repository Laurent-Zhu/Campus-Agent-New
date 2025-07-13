<template>
  <div class="exercise-container">
    <div class="header">
      <h2>智能练习评测</h2>
      <el-select 
        v-model="exerciseConfig.type" 
        placeholder="选择练习类型"
        @change="handleTypeChange"
      >
        <el-option
          v-for="item in exerciseTypes"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      
      <el-select
        v-model="exerciseConfig.difficulty"
        placeholder="选择难度"
        style="margin-left: 10px;"
      >
        <el-option
          v-for="level in difficultyLevels"
          :key="level.value"
          :label="level.label"
          :value="level.value"
        />
      </el-select>
      
      <el-button 
        type="primary" 
        @click="generateNewExercise"
        :loading="generating"
        :disabled="!exerciseConfig.type"
      >
        生成题目
      </el-button>
    </div>

    <div v-if="errorMessage" class="error-message">
      <el-alert :title="errorMessage" type="error" show-icon />
    </div>

    <exercise-generator
      v-if="currentExercise"
      :exercise="currentExercise"
      @submit="handleAnswerSubmit"
      :key="currentExercise.exercise_id"
      :loading="submitting"
    />
    
    <answer-evaluator
      v-if="evaluationResult"
      :result="evaluationResult"
      @next="generateNewExercise"
    />
    
    <history-panel
      :history="exerciseHistory"
      @retry="handleRetryExercise"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import ExerciseGenerator from '@/components/Student/ExerciseGenerator.vue'
import AnswerEvaluator from '@/components/Student/AnswerEvaluator.vue'
import HistoryPanel from '@/components/Student/HistoryPanel.vue'
import { generateExercise, submitAnswer, getHistory } from '@/api/Student/exerciseService'

const authStore = useAuthStore()
const studentId = computed(() => authStore.user?.id || null) // 获取真实学生ID

const exerciseTypes = [
  { value: 'knowledge', label: '知识点巩固' },
  { value: 'weakness', label: '弱点专项' },
  { value: 'simulation', label: '模拟测试' }
]

const difficultyLevels = [
  { value: 'easy', label: '简单' },
  { value: 'medium', label: '中等' },
  { value: 'hard', label: '困难' }
]

const exerciseConfig = ref({
  type: 'knowledge',
  difficulty: 'medium',
  knowledge_point_ids: [],
})

const currentExercise = ref(null)
const evaluationResult = ref(null)
const exerciseHistory = ref([])
const generating = ref(false)
const submitting = ref(false)
const errorMessage = ref('')

const handleTypeChange = (selectedType) => {
  exerciseConfig.value.type = selectedType
  // Reset error when changing type
  errorMessage.value = ''
}

const generateNewExercise = async () => {
  try {
    const studentId = authStore.studentId;
    if (!studentId) {
      throw new Error('未获取到学生ID，请先登录');
    }

    generating.value = true
    errorMessage.value = ''
    
    const payload = {
      studentId: studentId,
      difficulty: exerciseConfig.value.difficulty,
      knowledgePointIds: exerciseConfig.value.knowledge_point_ids
    }
    
    const response = await generateExercise(payload)
    currentExercise.value = response
    evaluationResult.value = null
    
    // Load history after generating new exercise
    await loadHistory()
    
  } catch (error) {
    errorMessage.value = '生成题目失败: ' + (error.response?.data?.error || error.message)
    console.error('生成题目出错:', error)
  } finally {
    generating.value = false
  }
}

const handleAnswerSubmit = async (submissionData) => {
  try {
    const studentId = authStore.studentId;
    
    if (!studentId) {
      throw new Error('未获取到学生ID，请先登录');
    }
    
    submitting.value = true
    errorMessage.value = ''
    
    const { answer, timeSpent, usedHints } = submissionData
    
    const res = await submitAnswer({
      exerciseId: currentExercise.value.exercise_id,
      studentId: studentId,
      answer,
      timeSpent: timeSpent || 0,
      usedHints: usedHints || []
    })

    evaluationResult.value = res
    
    // Update history after submission
    await loadHistory()
    
  } catch (error) {
    errorMessage.value = '提交答案失败: ' + (error.response?.data?.error || error.message)
    console.error('提交答案出错:', error)
  } finally {
    submitting.value = false
  }
}

const loadHistory = async () => {
  try {
    const studentId = authStore.studentId;
    
    if (!studentId) {
      throw new Error('未获取到学生ID，请先登录');
    }

    const history = await getHistory(studentId)
    exerciseHistory.value = history
  } catch (error) {
    console.error('加载历史记录失败:', error)
    // Don't show error to user for history loading
  }
}

const handleRetryExercise = (exercise) => {
  currentExercise.value = exercise
  evaluationResult.value = null
  errorMessage.value = ''
}

onMounted(async () => {
  await generateNewExercise()
})
</script>

<style scoped>
.exercise-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
.header {
  display: flex;
  margin-bottom: 20px;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.error-message {
  margin-bottom: 20px;
}
</style>