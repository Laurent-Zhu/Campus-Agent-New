<template>
    <div class="dashboard-overview">
        <h1>大屏概览</h1>
    
        <!-- 教师使用情况 -->
        <div class="usage-section">
            <h2>教师使用情况</h2>
            <div class="usage-card">
                <h3>使用次数统计</h3>
                <BarChart :chart-data="teacherUsageData" :options="chartOptions" />
            </div>
            <div class="usage-card">
                <h3>活跃板块</h3>
                <PieChart :chart-data="teacherActiveModulesData" />
            </div>
        </div>
  
        <!-- 学生使用情况 -->
        <div class="usage-section">
            <h2>学生使用情况</h2>
            <div class="usage-card">
                <h3>使用次数统计</h3>
                <BarChart :chart-data="studentUsageData" :options="chartOptions" />
            </div>
            <div class="usage-card">
                <h3>活跃板块</h3>
                <PieChart :chart-data="studentActiveModulesData" />
            </div>
        </div>
  
        <!-- 教学效率指数和学生学习效果 -->
        <div class="efficiency-section">
            <h2>教学效率指数和学生学习效果</h2>
            <div class="usage-card">
                <h3>教学效率指数</h3>
                <div>{{ teachingEfficiencyIndex }}</div>
            </div>
            <div class="usage-card">
                <h3>学生学习效果</h3>
                <div>{{ studentLearningEffect }}</div>
            </div>
        </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed } from 'vue'
  import BarChart from '../../components/Chart/BarChart.vue'
  import PieChart from '../../components/Chart/PieChart.vue'
  
  // 模拟数据
  const teacherUsageData = computed(() => {
    return {
      labels: ['备课与设计', '考核内容生成', '学情分析'],
      datasets: [{
        label: '使用次数',
        data: [30, 20, 40],
        backgroundColor: '#4e73df'
      }]
    }
  })
  
  const teacherActiveModulesData = computed(() => {
    return {
      labels: ['备课与设计', '考核内容生成', '学情分析'],
      datasets: [{
        data: [30, 20, 50],
        backgroundColor: [
          '#e74a3b', '#f6c23e', '#36b9cc'
        ]
      }]
    }
  })
  
  const studentUsageData = computed(() => {
    return {
      labels: ['智能练习评测', '题目练习', '练习历史'],
      datasets: [{
        label: '使用次数',
        data: [50, 30, 20],
        backgroundColor: '#4e73df'
      }]
    }
  })
  
  const studentActiveModulesData = computed(() => {
    return {
      labels: ['智能练习评测', '题目练习', '练习历史'],
      datasets: [{
        data: [50, 30, 20],
        backgroundColor: [
          '#e74a3b', '#f6c23e', '#36b9cc'
        ]
      }]
    }
  })
  
  const teachingEfficiencyIndex = ref(80)
  const studentLearningEffect = ref('良好')
  
  const chartOptions = computed(() => {
    return {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  })
  </script>
  
  <style scoped>
  .dashboard-overview {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  .usage-section {
    margin-bottom: 30px;
  }
  
  .usage-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }
  
  .efficiency-section {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  </style>