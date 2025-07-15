// src/api/student/exerciseService.js
import axios from '@/api/axios'
import { v4 as uuidv4 } from 'uuid';
import { useAuthStore } from '@/stores/auth'; 



/**
 * 生成练习题
 * @param {Object} config - 配置参数
 * @param {string|number} config.studentId - 学生ID
 * @param {string} [config.difficulty='medium'] - 难度级别
 * @param {Array} [config.knowledgePointIds=[]] - 知识点ID数组
 * @returns {Promise<Object>} 题目数据
 */
export const generateExercise = async ({ 
  studentId, 
  difficulty = 'medium', 
  knowledgePointIds = [] 
}) => {
  try {
    // 1. 单独验证令牌是否存在（关键调试）
  const authStore = useAuthStore();
  console.debug('[exerciseService] 调用generateExercise时的令牌信息:', {
    token: authStore.token ? authStore.token.substring(0, 20) + '...' : '无令牌',
    tokenExists: !!authStore.token,
    userRole: authStore.user?.role // 同时打印用户角色，确认是否为学生
  });

    // 请求数据准备
    const requestData = {
      student_id: String(studentId),
      difficulty,
      knowledge_point_ids: knowledgePointIds.map(String)
    }

    // 发送请求 
    const response = await axios.post('/student/exercises/generate/', requestData, {
      timeout: 30000  // 延长超时时间到30秒
    })

    console.debug('[API] 题目生成成功:', response.data)
    return response.data

  } catch (error) {
    const errorInfo = {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      error: error.response?.data || error.message,
      timestamp: new Date().toISOString()
    }
    
    console.error('[API] 生成题目失败:', errorInfo)
    
    // 如果是401错误，可以在这里添加重定向逻辑
    if (error.response?.status === 401) {
      console.warn('检测到未授权访问，可能需要重新登录')
      // 可以在这里触发登出操作或跳转到登录页
    }
    
    throw error
  }
}



/**
 * 提交答案
 * @param {Object} params - 提交参数
 * @param {string|number} params.exerciseId - 题目ID
 * @param {string|number} params.studentId - 学生ID
 * @param {string} params.answer - 学生答案
 * @param {number} [params.timeSpent=0] - 答题耗时(秒)
 * @param {Array} [params.usedHints=[]] - 使用的提示索引
 * @returns {Promise<Object>} 评估结果
 */
export const submitAnswer = async ({ exerciseId, studentId, answer, timeSpent = 0, usedHints = [] }) => {
  try {
    const response = await axios.post('/student/exercises/submit/', {
      exercise_id: String(exerciseId),
      student_id: String(studentId),
      student_answer: String(answer),
      time_spent: Number(timeSpent),
      used_hints: usedHints.map(Number) // 确保提示索引是数字
    })

    return response.data
  } catch (error) {
    console.error('[API] 提交答案失败:', {
      url: '/student/exercises/submit/',
      status: error.response?.status,
      error: error.response?.data || error.message
    })
    throw error
  }
}





/**
 * 获取历史记录
 * @param {string|number} studentId - 学生ID
 * @returns {Promise<Array>} 历史记录数组
 */
export const getHistory = async (studentId) => {
  try {
    const response = await axios.get(`/student/history/${studentId}/`)
    return response.data
  } catch (error) {
    console.error('[API] 获取历史记录失败:', {
      studentId,
      error: error.response?.data || error.message
    })
    throw error
  }
}