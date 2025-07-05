// src/stores/analyticsStore.js
import { defineStore } from 'pinia'
import { useClassStore, useStudentStore } from '@/stores'
import { 
  fetchKnowledgeMastery,
  fetchAssignmentAnalysis 
} from '@/api/teacher'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    currentView: 'class',      // 当前视图模式
    currentClass: null,       // 当前班级ID
    compareMode: false,
    comparedClass: null       // 对比班级ID
  }),

  getters: {
    // 当前班级完整数据
    currentClassDetail(state) {
      const classStore = useClassStore()
      return state.currentClass 
        ? classStore.rawClasses.find(c => c.id === state.currentClass) 
        : null
    },

    // 学生排名 (基于班级数据)
    rankedStudents(state) {
      if (!this.currentClassDetail) return []
      return [...(this.currentClassDetail.students || [])]
        .sort((a, b) => b.overallScore - a.overallScore)
    }
  },

  actions: {
    // 选择班级
    async selectClass(classId) {
      this.currentClass = classId
      this.currentView = 'class'
      
      if (classId) {
        await Promise.all([
          this.fetchClassKnowledgeData(),
          this.fetchAssignmentStats()
        ])
      }
    },

    // 选择学生 (现在只管理视图状态)
    selectStudent(studentId) {
      const studentStore = useStudentStore()
      this.currentView = 'student'
      return studentStore.fetchStudentDetail({
        classId: this.currentClass,
        studentId
      })
    },

    // 班级知识点数据
    async fetchClassKnowledgeData() {
      if (!this.currentClass) return
      
      try {
        this.knowledgeMastery = await fetchKnowledgeMastery({
          classId: this.currentClass,
          timeRange: 'month' // 使用默认或从studentStore获取
        })
      } catch (err) {
        console.error('获取知识点数据失败:', err)
        throw err
      }
    },

    // 班级作业数据
    async fetchAssignmentStats() {
      if (!this.currentClass) return
      
      try {
        this.assignmentStats = await fetchAssignmentAnalysis({
          classId: this.currentClass,
          timeRange: 'month'
        })
      } catch (err) {
        console.error('获取作业数据失败:', err)
        throw err
      }
    },

    // 切换对比模式
    toggleCompareMode(classId) {
      this.compareMode = !this.compareMode
      this.comparedClass = this.compareMode ? classId : null
    }
  },

  persist: {
    key: 'teacher-analytics',
    paths: ['currentClass', 'compareMode']
  }
})