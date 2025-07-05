<!-- views/StudentView.vue -->
<template>
  <div class="student-view">
    <button @click="goBack">返回班级分析</button>
    
    <StudentProfile :student="studentStore.currentStudent" />
    
    <div class="analysis-sections">
      <ScoreTrendChart :scores="studentStore.accuracyTrend" />
      <WeakKnowledgePoints :points="studentStore.weakPoints" />
    </div>
    
    <TeachingSuggestions :student="studentStore.currentStudent" />
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import { useStudentStore } from '@/stores/studentStore'
import StudentProfile from '@/components/StudentProfile.vue'

const route = useRoute()
const router = useRouter()
const studentStore = useStudentStore()

// 加载学生数据
onMounted(async () => {
  await studentStore.fetchStudent(route.params.studentId)
})

const goBack = () => {
  router.go(-1)
}
</script>