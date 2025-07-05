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
      >
        生成题目
      </el-button>
    </div>

    <exercise-generator
      v-if="currentExercise"
      :exercise="currentExercise"
      @submit="handleAnswerSubmit"
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
import ExerciseGenerator from '@/components/Student/ExerciseGenerator.vue'
import AnswerEvaluator from '@/components/Student/AnswerEvaluator.vue'
import HistoryPanel from '@/components/Student/HistoryPanel.vue'
import { generateExercise, submitAnswer } from '@/api/Student/exerciseService'

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
  knowledgePoint: null
})

const currentExercise = ref(null)
const evaluationResult = ref(null)
const exerciseHistory = ref([])
const generating = ref(false)

const generateNewExercise = async () => {
  try {
    generating.value = true
    const res = await generateExercise(exerciseConfig.value)
    currentExercise.value = res.data
    evaluationResult.value = null
  } finally {
    generating.value = false
  }
}

const handleAnswerSubmit = async (answer) => {
  const res = await submitAnswer({
    exerciseId: currentExercise.value.id,
    answer
  })
  evaluationResult.value = res.data
  exerciseHistory.value.unshift({
    exercise: currentExercise.value,
    result: res.data,
    timestamp: new Date()
  })
}

const handleRetryExercise = (exercise) => {
  currentExercise.value = exercise
  evaluationResult.value = null
}

onMounted(() => {
  generateNewExercise()
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
}
</style>