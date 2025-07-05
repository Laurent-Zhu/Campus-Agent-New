<!-- components/ClassCard.vue -->
<template>
  <div class="card" @click="$emit('select', classData.id)">
    <h3>{{ classData.name }}</h3>
    <div class="meta">
      <span>👨‍🎓 {{ classData.studentCount }}人</span>
      <span>📊 平均 {{ classData.averageScore }}分</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  classData: Object
})
</script>

<style scoped>
.card {
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s;
}
.card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
</style>