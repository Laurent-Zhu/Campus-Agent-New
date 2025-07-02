<template>
  <div class="analytics-container">
    <!-- 顶部导航 -->
    <div class="header">
      <h1>学情分析助手</h1>
      <div class="time-range-selector">
        <label>时间范围：</label>
        <select v-model="selectedTimeRange">
          <option value="week">最近一周</option>
          <option value="month">最近一月</option>
          <option value="semester">本学期</option>
        </select>
      </div>
    </div>

    <!-- 数据概览卡片 -->
    <div class="overview-cards">
      <div class="card">
        <div class="card-title">学生总数</div>
        <div class="card-value">{{ overviewData.totalStudents }}</div>
      </div>
      <div class="card">
        <div class="card-title">平均正确率</div>
        <div class="card-value">{{ overviewData.avgAccuracy }}%</div>
      </div>
      <div class="card">
        <div class="card-title">薄弱知识点</div>
        <div class="card-value">{{ overviewData.weakPoints }}</div>
      </div>
      <div class="card">
        <div class="card-title">待批改作业</div>
        <div class="card-value">{{ overviewData.pendingAssignments }}</div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：班级整体分析 -->
      <div class="class-analysis">
        <div class="section">
          <h2>班级知识点掌握情况</h2>
          <div class="chart-container">
            <BarChart 
              :chart-data="knowledgeMasteryData" 
              :options="chartOptions"
              v-if="!loading"
            />
            <div v-else class="loading">加载中...</div>
          </div>
        </div>

        <div class="section">
          <h2>错误类型分布</h2>
          <div class="chart-container">
            <PieChart 
              :chart-data="errorDistributionData"
              v-if="!loading"
            />
            <div v-else class="loading">加载中...</div>
          </div>
        </div>
      </div>

      <!-- 右侧：学生个体分析 -->
      <div class="student-analysis">
        <div class="section">
          <h2>学生错题分析</h2>
          <div class="student-selector">
            <label>选择学生：</label>
            <select v-model="selectedStudent">
              <option 
                v-for="student in studentList" 
                :key="student.id"
                :value="student"
              >
                {{ student.name }} ({{ student.id }})
              </option>
            </select>
          </div>

          <div v-if="selectedStudent" class="student-details">
            <div class="student-info">
              <div class="info-item">
                <span class="label">姓名：</span>
                <span>{{ selectedStudent.name }}</span>
              </div>
              <div class="info-item">
                <span class="label">学号：</span>
                <span>{{ selectedStudent.id }}</span>
              </div>
              <div class="info-item">
                <span class="label">综合正确率：</span>
                <span :class="getAccuracyClass(selectedStudent.accuracy)">
                  {{ selectedStudent.accuracy }}%
                </span>
              </div>
            </div>

            <div class="wrong-questions">
              <h3>近期错题分析</h3>
              <div 
                class="question-item"
                v-for="(question, index) in selectedStudent.wrongQuestions"
                :key="index"
              >
                <div class="question-header">
                  <span class="index">Q{{ index + 1 }}</span>
                  <span class="knowledge-point">{{ question.knowledgePoint }}</span>
                  <span class="error-type">{{ question.errorType }}</span>
                </div>
                <div class="question-content">
                  <p><strong>题目：</strong>{{ question.content }}</p>
                  <p><strong>学生答案：</strong>
                    <span class="wrong-answer">{{ question.studentAnswer }}</span>
                  </p>
                  <p><strong>正确答案：</strong>{{ question.correctAnswer }}</p>
                  <div class="suggestion">
                    <strong>建议：</strong>{{ question.suggestion }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="no-student-selected">
            请从上方选择学生查看详细分析
          </div>
        </div>
      </div>
    </div>

    <!-- 教学建议区 -->
    <div class="teaching-suggestions">
      <h2>教学建议</h2>
      <div class="suggestions-container">
        <div class="suggestion-card">
          <h3>班级整体建议</h3>
          <ul>
            <li v-for="(suggestion, index) in classSuggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </div>
        <div class="suggestion-card" v-if="selectedStudent">
          <h3>个性化建议 - {{ selectedStudent.name }}</h3>
          <ul>
            <li v-for="(suggestion, index) in individualSuggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
          <button class="generate-btn" @click="generateExercises">
            生成针对性练习
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import BarChart from '../../components/BarChart.vue'
import PieChart from '../../components/PieChart.vue'

export default {
  components: {
    BarChart,
    PieChart
  },
  setup() {
    // 数据状态
    const loading = ref(true)
    const selectedTimeRange = ref('month')
    const selectedStudent = ref(null)
    
    // 模拟数据
    const overviewData = ref({
      totalStudents: 42,
      avgAccuracy: 76.5,
      weakPoints: 5,
      pendingAssignments: 3
    })
    
    const studentList = ref([
      {
        id: 'S2023001',
        name: '张三',
        accuracy: 82,
        wrongQuestions: [
          {
            knowledgePoint: '函数定义',
            errorType: '概念理解错误',
            content: '下列哪个选项正确地定义了一个Python函数？',
            studentAnswer: 'def myFunc:',
            correctAnswer: 'def myFunc():',
            suggestion: '强调函数定义必须包含括号，即使没有参数'
          },
          {
            knowledgePoint: '循环结构',
            errorType: '逻辑错误',
            content: '编写一个从1加到10的程序',
            studentAnswer: 'total = 0\nfor i in range(11):\n    total += i',
            correctAnswer: 'total = 0\nfor i in range(1, 11):\n    total += i',
            suggestion: '讲解range()函数的参数含义，强调边界条件'
          }
        ]
      },
      {
        id: 'S2023002',
        name: '李四',
        accuracy: 65,
        wrongQuestions: [
          {
            knowledgePoint: '列表操作',
            errorType: '语法错误',
            content: '如何向列表末尾添加元素？',
            studentAnswer: 'list.add(5)',
            correctAnswer: 'list.append(5)',
            suggestion: '区分不同数据结构的方法名，列表使用append()'
          }
        ]
      }
    ])
    
    const knowledgePoints = [
      '变量与数据类型', '运算符', '条件语句', 
      '循环结构', '函数定义', '列表操作', '字典使用'
    ]
    
    // 计算属性
    const knowledgeMasteryData = computed(() => {
      return {
        labels: knowledgePoints,
        datasets: [{
          label: '掌握率(%)',
          data: knowledgePoints.map(() => Math.floor(Math.random() * 30) + 70),
          backgroundColor: '#4e73df'
        }]
      }
    })

    //添加数据检查
    watch(knowledgeMasteryData, (newVal) => {
        if (!newVal?.datasets?.[0]?.data) {
            console.error('图表数据格式不正确')
        }
    }, { immediate: true })
    
    const errorDistributionData = computed(() => {
      return {
        labels: ['概念理解错误', '语法错误', '逻辑错误', '计算错误', '其他'],
        datasets: [{
          data: [35, 25, 20, 15, 5],
          backgroundColor: [
            '#e74a3b', '#f6c23e', '#36b9cc', '#1cc88a', '#858796'
          ]
        }]
      }
    })
    
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
    
    const classSuggestions = computed(() => {
      return [
        '循环结构掌握较弱，建议增加相关练习',
        '函数定义错误率较高，下周重点讲解',
        '为前20%学生准备拓展材料',
        '安排一次关于列表操作的复习课'
      ]
    })
    
    const individualSuggestions = computed(() => {
      if (!selectedStudent.value) return []
      
      return [
        `${selectedStudent.value.name}在函数定义方面存在困难，建议一对一辅导`,
        '针对循环结构错误，提供额外练习题',
        '鼓励参与课后编程小组活动'
      ]
    })
    
    // 方法
    const getAccuracyClass = (accuracy) => {
      if (accuracy >= 80) return 'high-accuracy'
      if (accuracy >= 60) return 'medium-accuracy'
      return 'low-accuracy'
    }
    
    const generateExercises = () => {
      alert(`正在为 ${selectedStudent.value.name} 生成针对性练习...`)
      // 实际应用中这里会调用API
    }
    
    const fetchData = () => {
      loading.value = true
      // 模拟API请求延迟
      setTimeout(() => {
        loading.value = false
      }, 800)
    }
    
    // 生命周期
    onMounted(() => {
      fetchData()
    })
    
    return {
      loading,
      selectedTimeRange,
      selectedStudent,
      overviewData,
      studentList,
      knowledgeMasteryData,
      errorDistributionData,
      chartOptions,
      classSuggestions,
      individualSuggestions,
      getAccuracyClass,
      generateExercises
    }
  }
}
</script>

<style scoped>
.analytics-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #2c3e50;
  margin: 0;
}

.time-range-selector select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.card-title {
  color: #7f8c8d;
  font-size: 16px;
  margin-bottom: 10px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.section h2 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 20px;
}

.chart-container {
  height: 300px;
  position: relative;
}

.loading {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #7f8c8d;
}

.student-selector {
  margin-bottom: 20px;
}

.student-selector select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
  min-width: 200px;
}

.student-details {
  margin-top: 20px;
}

.student-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
}

.label {
  font-weight: bold;
  color: #7f8c8d;
}

.high-accuracy {
  color: #1cc88a;
}

.medium-accuracy {
  color: #f6c23e;
}

.low-accuracy {
  color: #e74a3b;
}

.wrong-questions {
  margin-top: 20px;
}

.question-item {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
}

.question-header {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  align-items: center;
}

.index {
  background: #4e73df;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.knowledge-point {
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.error-type {
  background: #feeae9;
  color: #e74a3b;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.question-content {
  line-height: 1.6;
}

.wrong-answer {
  color: #e74a3b;
  text-decoration: line-through;
}

.suggestion {
  background: #f0f7ff;
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.teaching-suggestions {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.suggestions-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.suggestion-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 20px;
}

.suggestion-card h3 {
  margin-top: 0;
  color: #2c3e50;
}

.suggestion-card ul {
  padding-left: 20px;
}

.suggestion-card li {
  margin-bottom: 8px;
}

.generate-btn {
  background: #4e73df;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 15px;
  transition: background 0.3s;
}

.generate-btn:hover {
  background: #2e59d9;
}

.no-student-selected {
  text-align: center;
  padding: 40px;
  color: #7f8c8d;
  background: #f8f9fa;
  border-radius: 6px;
}
</style>