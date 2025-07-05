<!-- views/ClassList.vue -->
<template>
  <div class="class-list">
    <h1>我的班级</h1>
    <div v-if="loading">加载中...</div>
    <div v-else class="grid">
      <ClassCard 
        v-for="cls in classes" 
        :key="cls.id"
        :class-data="cls"
        @select="selectClass"
      />
    </div>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useClassStore } from '@/stores/classStore'
import ClassCard from '@/components/ClassCard.vue'

const store = useClassStore()
const { classes, loading } = storeToRefs(store)
store.fetchClasses()

const selectClass = (id) => {
  router.push(`/class/${id}`)
}
</script>