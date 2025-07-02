<template>
  <div class="chart-container">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

export default {
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const chartRef = ref(null)
    let chartInstance = null

    const renderChart = () => {
      if (!chartRef.value || !props.chartData) return
      
      if (chartInstance) {
        chartInstance.destroy()
      }

      chartInstance = new Chart(chartRef.value, {
        type: 'pie',  // 明确指定图表类型
        data: props.chartData,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          ...props.options
        }
      })
    }

    onMounted(renderChart)
    watch(() => props.chartData, renderChart, { deep: true })
    onBeforeUnmount(() => {
      if (chartInstance) chartInstance.destroy()
    })

    return { chartRef }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 100%;
  width: 100%;
  min-height: 300px;
}
</style>