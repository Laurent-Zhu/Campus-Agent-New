import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL

export const generateExercise = async (config) => {
  const response = await axios.post(`${API_BASE}/exercises/generate`, config)
  return response.data
}

export const submitAnswer = async (data) => {
  const response = await axios.post(`${API_BASE}/exercises/evaluate`, data)
  return response.data
}

// Mock 数据生成器（开发用）
export const mockGenerateExercise = () => {
  return {
    id: Math.random().toString(36).substring(2),
    type: ['multiple_choice', 'fill_blank', 'subjective'][Math.floor(Math.random() * 3)],
    content: '请计算：2 × (3 + 5) = ?',
    options: ['10', '16', '18', '20'],
    knowledgePoint: '四则运算',
    difficulty: 'easy'
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