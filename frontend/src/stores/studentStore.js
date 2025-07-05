// src/stores/studentStore.js
import { defineStore } from 'pinia'
import { fetchStudentDetails } from '@/api/teacher'

export const useStudentStore = defineStore('student', {
  state: () => ({
    currentStudent: null,  // 当前查看的学生详情
    loading: false,
    error: null,
    timeRange: 'month'     // 学生数据的时间范围
  }),

  getters: {
    // 学生薄弱知识点 (示例)
    weakPoints(state) {
      return state.currentStudent?.knowledgeWeaknesses
        ?.filter(item => item.masteryRate < 0.6)
        ?.sort((a, b) => a.masteryRate - b.masteryRate) || []
    }
  },

  actions: {
    // 获取学生详情
    async fetchStudentDetail({ classId, studentId }) {
      this.loading = true
      this.error = null
      try {
        this.currentStudent = await fetchStudentDetails({
          classId,
          studentId,
          timeRange: this.timeRange
        })
      } catch (err) {
        this.error = err.message || '加载学生数据失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    // 更改时间范围并重新加载
    async changeTimeRange(range) {
      this.timeRange = range
      if (this.currentStudent) {
        await this.fetchStudentDetail({
          classId: this.currentStudent.classId,
          studentId: this.currentStudent.id
        })
      }
    }
  },

  persist: {
    key: 'student-store',
    paths: ['timeRange']
  }
})