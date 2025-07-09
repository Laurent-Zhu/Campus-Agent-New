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
      :key="currentExercise.exercise_id"
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

const TEMP_STUDENT_ID = '1'

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


const handleTypeChange = (selectedType) => {
  try {
    // 更新当前选择的类型
    exerciseConfig.value.type = selectedType
    
    // 可选：显示加载状态
    generating.value = true
    
    // 类型变化后立即生成新题目
    // await generateNewExercise()
    
  } catch (error) {
    console.error('处理类型变化时出错:', error)
    // 可以使用Element Plus的消息提示
    ElMessage.error('切换练习类型失败: ' + error.message)
  } finally {
    generating.value = false
  }
}



const generateNewExercise = async () => {
  try {
    // generating.value = true

     const payload = {
      ...exerciseConfig.value,
      student_id: TEMP_STUDENT_ID // 明确添加
    }
    
    const response = await generateExercise(payload)

    currentExercise.value = response
    evaluationResult.value = null

  } finally {
    generating.value = false
  }
}

const handleAnswerSubmit = async (answer) => {
  try {
    const res = await submitAnswer({
      exerciseId: currentExercise.value.exercise_id, // 使用后端返回的字段名
      studentId: TEMP_STUDENT_ID, // 临时测试ID
      answer: answer
    })

    // 直接使用后端返回的数据结构（暂不转换字段名）
    evaluationResult.value = res
    
    // 记录历史（保持简单结构）
    exerciseHistory.value.unshift({
      exercise: currentExercise.value,
      result: res,
      timestamp: new Date()
    })

  } catch (error) {
    console.error('提交答案出错:', error)
    ElMessage.error(error.response?.data?.error || '提交失败，请检查数据')
  }
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