<template>
  <div class="exercise-container">
    <div class="header">
      <h2>智能练习评测</h2>
      
      <!-- 练习类型选择 -->
      <el-select 
        v-model="exerciseConfig.type" 
        placeholder="选择练习类型"
        @change="handleTypeChange"
        style="width: 160px;"
      >
        <el-option
          v-for="item in exerciseTypes"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      
      <!-- 难度模式切换（自动/手动） -->
      <el-radio-group 
        v-model="difficultyMode" 
        @change="handleDifficultyModeChange"
        style="margin: 0 15px;"
      >
        <el-radio label="auto" border>自动推荐</el-radio>
        <el-radio label="manual" border>手动选择</el-radio>
      </el-radio-group>
      
      <!-- 难度选择框（自动模式下禁用但仍显示推荐难度） -->
      <el-select
        v-model="exerciseConfig.difficulty"
        placeholder="选择难度"
        :disabled="difficultyMode === 'auto'"
        style="width: 120px;"
      >
        <el-option
          v-for="level in difficultyLevels"
          :key="level.value"
          :label="level.label"
          :value="level.value"
        />
      </el-select>
      
      <!-- 生成题目按钮 -->
      <el-button 
        type="primary" 
        @click="generateNewExercise"
        :loading="generating"
        :disabled="!exerciseConfig.type"
      >
        生成题目
      </el-button>
      
      <!-- 历史记录按钮 -->
      <el-button 
        type="info" 
        @click="showHistoryPanel = !showHistoryPanel"
        style="margin-left: 10px;"
      >
        {{ showHistoryPanel ? '隐藏历史' : '查看历史' }}
      </el-button>
    </div>

    <!-- 自动推荐难度提示 -->
    <div v-if="difficultyMode === 'auto' && recommendedDifficultyReason" class="recommendation-hint">
      <el-alert 
        :title="recommendedDifficultyReason" 
        type="info" 
        show-icon 
      />
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-message">
      <el-alert :title="errorMessage" type="error" show-icon />
    </div>

    <!-- 题目生成区域 -->
    <div v-if="currentExercise" class="exercise-area">
      <exercise-generator
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
    </div>
    
    <!-- 历史记录面板 -->
    <el-collapse-transition>
      <div v-if="showHistoryPanel" class="history-panel-container">
        <el-card class="history-card">
          <template #header>
            <div class="history-header">
              <span>历史练习记录</span>
              <el-button 
                type="text" 
                @click="refreshHistory"
                :loading="loadingHistory"
              >
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          
          <el-table
            :data="exerciseHistory"
            style="width: 100%"
            v-loading="loadingHistory"
            empty-text="暂无历史记录"
          >
            <el-table-column prop="created_at" label="日期" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="title" label="题目" />
            <el-table-column prop="difficulty" label="难度" width="100">
              <template #default="{ row }">
                <el-tag :type="getDifficultyTagType(row.difficulty)">
                  {{ row.difficulty }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button 
                  size="small" 
                  @click="viewHistoryExercise(row)"
                >
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import ExerciseGenerator from '@/components/Student/ExerciseGenerator.vue'
import AnswerEvaluator from '@/components/Student/AnswerEvaluator.vue'
import { generateExercise, submitAnswer, getHistory } from '@/api/Student/exerciseService'
import { formatDate } from '@/utils/date'

// 状态管理
const authStore = useAuthStore()
const studentId = computed(() => authStore.user?.id || null)

// 练习配置
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

// 状态管理
const currentExercise = ref(null)
const evaluationResult = ref(null)
const exerciseHistory = ref([])
const generating = ref(false)
const submitting = ref(false)
const loadingHistory = ref(false)
const errorMessage = ref('')
const showHistoryPanel = ref(false)

// 新增：难度模式（自动/手动）
const difficultyMode = ref('auto')
const recommendedDifficultyReason = ref('')

// 获取难度标签类型
const getDifficultyTagType = (difficulty) => {
  const map = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return map[difficulty] || ''
}

// 监听难度模式变化，自动计算推荐难度
watch(difficultyMode, async (newMode) => {
  if (newMode === 'auto' && studentId.value) {
    await calculateRecommendedDifficulty()
  }
})

const handleDifficultyModeChange = (newMode) => {
  console.log("切换难度模式为：", newMode);
};

// 计算推荐难度（基于历史记录）
const calculateRecommendedDifficulty = async () => {
  try {
    // 无历史记录时默认中等难度
    if (exerciseHistory.value.length === 0) {
      exerciseConfig.value.difficulty = 'medium'
      recommendedDifficultyReason.value = '暂无练习记录，默认推荐中等难度'
      return
    }

    // 计算历史正确率
    const correctCount = exerciseHistory.value.filter(item => item.is_correct).length
    const totalCount = exerciseHistory.value.length
    const correctRate = correctCount / totalCount

    // 根据正确率推荐难度（与后端逻辑一致）
    if (correctRate < 0.6) {
      exerciseConfig.value.difficulty = 'easy'
      recommendedDifficultyReason.value = `历史正确率${(correctRate * 100).toFixed(1)}%，推荐简单难度巩固基础`
    } else if (correctRate < 0.8) {
      exerciseConfig.value.difficulty = 'medium'
      recommendedDifficultyReason.value = `历史正确率${(correctRate * 100).toFixed(1)}%，推荐中等难度提升能力`
    } else {
      exerciseConfig.value.difficulty = 'hard'
      recommendedDifficultyReason.value = `历史正确率${(correctRate * 100).toFixed(1)}%，推荐困难难度挑战自我`
    }
    
    console.log(`[自动推荐] 历史正确率: ${(correctRate * 100).toFixed(1)}%，推荐难度: ${exerciseConfig.value.difficulty}`)
  } catch (error) {
    console.error('计算推荐难度失败:', error)
    exerciseConfig.value.difficulty = 'medium'
    recommendedDifficultyReason.value = '推荐难度计算失败，默认使用中等难度'
  }
}

// 生成新题目（修改：始终传递difficulty参数）
const generateNewExercise = async () => {
  try {
    if (!studentId.value) {
      throw new Error('请先登录')
    }

    generating.value = true
    errorMessage.value = ''
    
    // 构建请求参数（始终包含difficulty）
    const requestParams = {
      studentId: studentId.value,
      difficulty: exerciseConfig.value.difficulty, 
      knowledgePointIds: exerciseConfig.value.knowledge_point_ids,
      type: exerciseConfig.value.type
    }

    console.log("发送给后端的题目生成参数:", requestParams)
    
    const response = await generateExercise(requestParams)
    currentExercise.value = response
    evaluationResult.value = null
    showHistoryPanel.value = false
    
    console.log("从后端接收的题目:", response)
    
  } catch (error) {
    errorMessage.value = '生成题目失败: ' + (error.response?.data?.error || error.message)
    console.error('生成题目出错:', error)
  } finally {
    generating.value = false
  }
}

// 提交答案
const handleAnswerSubmit = async (submissionData) => {
  try {
    if (!studentId.value) {
      throw new Error('请先登录')
    }
    
    submitting.value = true
    errorMessage.value = ''
    
    const res = await submitAnswer({
      exerciseId: currentExercise.value.exercise_id,
      studentId: studentId.value,
      answer: submissionData.answer,
      timeSpent: submissionData.timeSpent || 0,
      usedHints: submissionData.usedHints || []
    })

    evaluationResult.value = res
    await loadHistory()  // 提交后刷新历史
    
  } catch (error) {
    errorMessage.value = '提交答案失败: ' + (error.response?.data?.error || error.message)
    console.error('提交答案出错:', error)
  } finally {
    submitting.value = false
  }
}

// 加载历史记录
const loadHistory = async () => {
  try {
    if (!studentId.value) return
    
    loadingHistory.value = true
    const history = await getHistory(studentId.value)
    exerciseHistory.value = history
    
    // 加载历史后，若为自动模式则重新计算推荐难度
    if (difficultyMode.value === 'auto') {
      await calculateRecommendedDifficulty()
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

// 刷新历史记录
const refreshHistory = async () => {
  await loadHistory()
}

// 查看历史题目
const viewHistoryExercise = (row) => {
  currentExercise.value = {
    exercise_id: row.exercise_id,
    title: row.title,
    content: row.content,
    difficulty: row.difficulty,
    knowledge_points: row.knowledge_points || []
  }
  evaluationResult.value = null
  showHistoryPanel.value = false
}

// 切换练习类型
const handleTypeChange = (selectedType) => {
  exerciseConfig.value.type = selectedType
  errorMessage.value = ''
}

// 初始化
onMounted(async () => {
  await loadHistory()
})
</script>

<style scoped>
.exercise-container {
  max-width: 900px;
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

.recommendation-hint {
  margin-bottom: 20px;
  padding: 0 10px;
}

.exercise-area {
  margin-bottom: 20px;
}

.history-panel-container {
  margin-top: 20px;
}

.history-card {
  border-radius: 8px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-table .cell) {
  word-break: break-word;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header > * {
    width: 100%;
    margin-bottom: 10px;
  }
}
</style>