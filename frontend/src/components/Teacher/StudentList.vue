<!-- src/components/StudentList.vue -->
<template>
  <div class="student-list-container">
    <h3>学生列表</h3>
    <div class="student-list">
      <div 
        v-for="student in students" 
        :key="student.id"
        class="student-item"
        @click="handleSelect(student.id)"
      >
        <div class="student-avatar">
          <!-- 这里可以放头像，暂时用首字母代替 -->
          {{ student.name.charAt(0) }}
        </div>
        <div class="student-info">
          <div class="student-name">{{ student.name }}</div>
          <div class="student-id">学号: {{ student.id }}</div>
          <div class="student-score">最近得分: {{ student.latestScore || '暂无' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  students: {
    type: Array,
    required: true,
    default: () => []
  }
})

const emit = defineEmits(['select'])

const handleSelect = (studentId) => {
  emit('select', studentId)
}
</script>

<style scoped>
.student-list-container {
  margin-top: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  background-color: #fff;
}

.student-list {
  display: grid;
  gap: 12px;
}

.student-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.student-item:hover {
  background-color: #f5f5f5;
  transform: translateY(-2px);
}

.student-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #4a6baf;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-weight: bold;
}

.student-info {
  flex: 1;
}

.student-name {
  font-weight: 500;
  margin-bottom: 2px;
}

.student-id,
.student-score {
  font-size: 12px;
  color: #666;
}

.student-score {
  margin-top: 2px;
}
</style>