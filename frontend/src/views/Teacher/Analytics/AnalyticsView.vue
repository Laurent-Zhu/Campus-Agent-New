<!-- views/AnalyticsView.vue -->
<template>
  <div class="analytics-container">
    <!-- 班级选择导航 -->
    <div class="class-selector">
      <router-link 
        v-for="cls in classStore.classesBrief"
        :key="cls.id"
        :to="`/classes/${cls.id}`"
        :class="{ active: classStore.currentClassId === cls.id }"
      >
        {{ cls.name }} ({{ cls.studentCount }}人)
      </router-link>
    </div>

    <!-- 时间范围选择器 -->
    <div class="time-range-selector">
      <select v-model="timeRange">
        <option value="week">最近一周</option>
        <option value="month">最近一月</option>
        <option value="semester">本学期</option>
      </select>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 班级整体分析 -->
      <ClassAnalytics 
        :class-data="classStore.currentClass"
        :time-range="timeRange"
      />
      
      <!-- 学生列表 -->
      <StudentList 
        :students="classStore.currentClass?.students || []"
        @select="selectStudent"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useClassStore } from '@/stores/classStore'
import ClassAnalytics from '@/components/Teacher/ClassAnalytics.vue'
import StudentList from '@/components/Teacher/StudentList.vue'

const route = useRoute()
const router = useRouter()
const classStore = useClassStore()
const timeRange = ref('month')

// 初始化加载
onMounted(async () => {
  if (classStore.rawClasses.length === 0) {
    await classStore.loadClasses()
  }
  classStore.setCurrentClass(route.params.classId)
})

// 监听路由变化
watch(() => route.params.classId, (newId) => {
  classStore.setCurrentClass(newId)
})

const selectStudent = (studentId) => {
  router.push(`/students/${studentId}`)
}
</script>