<!-- 历史记录面板 -->


<template>
  <el-card class="history-panel">
    <template #header>
      <span>练习历史</span>
    </template>
    
    <el-timeline>
      <el-timeline-item
        v-for="(record, index) in history"
        :key="index"
        :timestamp="formatTime(record.timestamp)"
        placement="top"
      >
        <el-card>
          <div class="history-item">
            <div class="question-preview">
              {{ truncate(record.exercise.content, 50) }}
            </div>
            <div class="result-status">
              <el-tag :type="record.result.isCorrect ? 'success' : 'danger'">
                {{ record.result.isCorrect ? '正确' : '错误' }}
              </el-tag>
            </div>
            <div class="action-buttons">
              <el-button 
                size="small" 
                @click="$emit('retry', record.exercise)"
              >
                重做此题
              </el-button>
            </div>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </el-card>
</template>

<script setup>
import { format } from 'date-fns'

defineProps({
  history: {
    type: Array,
    default: () => []
  }
})

const formatTime = (timestamp) => {
  return format(new Date(timestamp), 'yyyy-MM-dd HH:mm')
}

const truncate = (text, length) => {
  if (text.length <= length) return text
  return text.substring(0, length) + '...'
}
</script>

<style scoped>
.history-panel {
  margin-top: 30px;
}
.history-item {
  display: flex;
  align-items: center;
}
.question-preview {
  flex: 1;
  margin-right: 15px;
}
.result-status {
  width: 60px;
  text-align: center;
}
.action-buttons {
  width: 100px;
  text-align: right;
}
</style>