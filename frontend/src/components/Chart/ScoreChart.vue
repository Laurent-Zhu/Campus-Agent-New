<!-- components/ScoreChart.vue -->
<template>
  <div class="chart">
    <div 
      v-for="(score, i) in scores" 
      :key="i"
      class="bar"
      :style="{ height: score + 'px' }"
    >
      <span class="label">第{{ i+1 }}次</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  scores: Array
})
</script>