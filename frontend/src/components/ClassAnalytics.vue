<!-- components/ClassAnalytics.vue -->
<template>
  <div class="class-analytics">
    <h2>{{ classData.name }} 学情分析</h2>
    
    <div class="overview-cards">
      <div class="card">
        <div>平均成绩</div>
        <div class="value">{{ classData.averageScore }}分</div>
      </div>
      <!-- 其他概览卡片... -->
    </div>

    <div class="charts">
      <KnowledgeMasteryChart 
        :class-id="classData.id"
        :time-range="timeRange"
      />
      <ErrorDistributionChart 
        :class-id="classData.id"
        :time-range="timeRange"
      />
    </div>
  </div>
</template>

<script setup>
defineProps({
  classData: Object,
  timeRange: String
})
</script>