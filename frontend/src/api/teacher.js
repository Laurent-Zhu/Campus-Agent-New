// src/api/teacher.js
import axios from 'axios';

export function uploadLessonPreparationFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  return axios.post('/api/teacher/lesson-preparation/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

// 模拟 API 请求延迟
const simulateNetworkDelay = () => new Promise(resolve => setTimeout(resolve, 300))

// 获取班级列表
export const fetchClassList = async () => {
  await simulateNetworkDelay()
  return [
    {
      id: 'class-1',
      name: '三年级二班',
      studentCount: 30,
      averageScore: 78,
      subject: 'Python编程',
      recentActivity: new Date().toISOString(),
      students: Array.from({length: 30}, (_, i) => ({
        id: `s-${i+1}`,
        name: `学生${i+1}`,
        overallScore: Math.floor(Math.random() * 30) + 70,
        accuracyTrend: [
          Math.floor(Math.random() * 20) + 70,
          Math.floor(Math.random() * 20) + 70,
          Math.floor(Math.random() * 20) + 70
        ]
      }))
    }
  ]
}

// 获取学生详情
export const fetchStudentDetails = async (params) => {
  await simulateNetworkDelay()
  
  return {
    id: params.studentId,
    name: `学生${params.studentId.split('-')[1]}`,
    overallScore: Math.floor(Math.random() * 30) + 70,
    accuracyTrend: [80, 75, 82],
    wrongQuestions: [
      {
        questionId: 'q-1',
        knowledgePoint: '循环结构',
        errorType: '边界条件错误',
        times: 3,
        lastAttempt: '2023-11-15'
      }
    ],
    knowledgeWeaknesses: [
      {
        knowledgeId: 'kp-1',
        name: '循环结构',
        masteryRate: 0.65,
        trend: [0.6, 0.63, 0.65],
        relatedQuestions: ['q-1', 'q-2']
      }
    ],
    assignmentScores: [
      {
        assignmentId: 'assign-1',
        title: 'Python基础测验',
        score: 85,
        classAverage: 78,
        rank: 12,
        completionDate: '2023-11-10'
      }
    ],
    behaviorAnalysis: {
      submissionTimeliness: 0.9,
      practiceFrequency: 3.5
    }
  }
}

// 获取知识点掌握数据
export const fetchKnowledgeMastery = async (params) => {
  await simulateNetworkDelay()
  
  return [
    {
      knowledgeId: 'kp-1',
      name: '循环结构',
      masteryRate: 0.72,
      trend: [0.68, 0.70, 0.72],
      relatedQuestions: ['q-1', 'q-2']
    },
    {
      knowledgeId: 'kp-2',
      name: '函数',
      masteryRate: 0.65,
      trend: [0.60, 0.63, 0.65],
      relatedQuestions: ['q-3', 'q-4']
    }
  ]
}

// 获取作业分析数据
export const fetchAssignmentAnalysis = async (params) => {
  await simulateNetworkDelay()
  
  return [
    {
      id: 'assign-1',
      title: 'Python基础测验',
      averageScore: 78,
      completionRate: 0.95,
      difficulty: 0.6,
      questionAnalysis: [
        {
          questionId: 'q-1',
          correctRate: 0.75,
          commonErrors: ['语法错误', '逻辑错误']
        }
      ]
    }
  ]
}