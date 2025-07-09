import axios from 'axios'

const API_BASE = 'http://localhost:8001'

export const generateExercise = async (config) => {

  const payload = {
    student_id: String(config.student_id), // 注意后端使用下划线命名
    difficulty: config.difficulty || 'medium', // 默认中等难度
    knowledge_point_ids: config.knowledgePointIds || [] // 确保是数组
  }

  console.log('完整请求数据:', payload)

  try {
    const response = await axios.post(
      `${API_BASE}/api/student/exercises/generate/`,
      payload
    );

    console.log('响应数据:', response.data)

    return response.data
  } catch (error) {
    console.error('生成题目失败:', error.response?.data || error.message)
    throw error
  }
}


export const submitAnswer = async (data) => {
  const payload = {
    exercise_id: String(data.exerciseId),  // 转为下划线命名
    student_id: String(data.studentId),   // 添加必填字段
    student_answer: String(data.answer)   // 明确字段名
  }

  try {
    const response = await axios.post(
      `${API_BASE}/api/student/exercises/evaluate/`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
          // 'Authorization': `Bearer ${localStorage.getItem('token')}` // 添加认证
        }
      }
    )
    return response.data
  } catch (error) {
    console.error('提交答案错误:', {
      status: error.response?.status,
      data: error.response?.data
    })
    throw error // 抛出错误供上层处理
  }
}



// Mock 数据生成器（开发用）
export const mockGenerateExercise = () => {
  return {
    exercise_id: Math.random().toString(36).substring(2),
    question: '请计算：2 × (3 + 5) = ?',
    options: ['10', '16', '18', '20'],
    hint: '记得先计算括号内的内容',
    difficulty: 'easy',
    knowledge_points: ['四则运算']
  }
}

export const mockSubmitAnswer = () => {
  return {
    isCorrect: Math.random() > 0.3,
    userAnswer: '16',
    correctAnswer: '16',
    analysis: '本题考查基本的四则运算规则...',
    suggestion: '建议多做括号优先的练习题...'
  }
}