// src/api/student/exerciseService.js
import axios from '@/api/axios'




/**
 * 生成练习题
 * @param {Object} config - 配置参数
 * @param {string|number} config.studentId - 学生ID
 * @param {string} [config.difficulty='medium'] - 难度级别
 * @param {Array} [config.knowledgePointIds=[]] - 知识点ID数组
 * @returns {Promise<Object>} 题目数据
 */
export const generateExercise = async ({ studentId, difficulty = 'medium', knowledgePointIds = [] }) => {
  try {
    const response = await axios.post('/student/exercises/generate/', {
      student_id: String(studentId),
      difficulty,
      knowledge_point_ids: knowledgePointIds.map(String) // 确保所有ID都是字符串
    })

    console.debug('[API] 题目生成成功:', response.data)
    return response.data
  } catch (error) {
    console.error('[API] 生成题目失败:', {
      url: error.config?.url,
      status: error.response?.status,
      error: error.response?.data || error.message
    })
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