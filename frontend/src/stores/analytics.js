// src/stores/analytics.js

import { defineStore } from 'pinia'
import { 
  fetchClassList, 
  fetchStudentDetails,
  fetchAssignmentAnalysis 
} from '../api/teacher'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    timeRange: 'month',
    currentView: 'class',
    loading: false,
    error: null,
    classes: [],
    currentClass: null,
    selectedStudent: null,
    assignmentStats: [],
    knowledgeMastery: [],
    compareMode: false,
    comparedClass: null
  }),

  getters: {
    rankedStudents(state) {
      if (!state.currentClass) return []
      return [...(state.currentClass.students || [])]
        .sort((a, b) => b.overallScore - a.overallScore)
    },

    weakKnowledgePoints(state) {
      return state.knowledgeMastery
        .filter(item => item.masteryRate < 0.6)
        .sort((a, b) => a.masteryRate - b.masteryRate)
    },

    timeRangeLabel(state) {
      const ranges = {
        'week': '最近一周',
        'month': '最近一月',
        'term': '本学期',
        'year': '本学年'
      }
      return ranges[state.timeRange] || ''
    }
  },

  actions: {
    async initLoad() {
      try {
        this.loading = true
        this.classes = await fetchClassList()
        if (this.classes.length > 0) {
          await this.selectClass(this.classes[0].id)
        }
      } catch (err) {
        this.error = err.message || '加载失败'
      } finally {
        this.loading = false
      }
    },

    async selectClass(classId) {
      this.currentClass = this.classes.find(c => c.id === classId) || null
      this.currentView = 'class'
      
      if (this.currentClass) {
        await Promise.all([
          this.fetchClassKnowledgeData(),
          this.fetchAssignmentStats()
        ])
      }
    },

    async selectStudent(studentId) {
      if (!this.currentClass) return
      
      this.loading = true
      try {
        this.selectedStudent = await fetchStudentDetails({
          classId: this.currentClass.id,
          studentId,
          timeRange: this.timeRange
        })
        this.currentView = 'student'
      } catch (err) {
        this.error = err.message || '加载学生数据失败'
      } finally {
        this.loading = false
      }
    },

    async fetchClassKnowledgeData() {
      if (!this.currentClass) return
      
      this.knowledgeMastery = await fetchKnowledgeMastery({
        classId: this.currentClass.id,
        timeRange: this.timeRange
      })
    },

    async fetchAssignmentStats() {
      if (!this.currentClass) return
      
      this.assignmentStats = await fetchAssignmentAnalysis({
        classId: this.currentClass.id,
        timeRange: this.timeRange
      })
    },

    async changeTimeRange(range) {
      this.timeRange = range
      if (this.currentClass) {
        await Promise.all([
          this.fetchClassKnowledgeData(),
          this.fetchAssignmentStats()
        ])
      }
      if (this.selectedStudent) {
        await this.selectStudent(this.selectedStudent.id)
      }
    },

    toggleCompareMode(classId) {
      this.compareMode = !this.compareMode
      if (this.compareMode && classId) {
        this.comparedClass = this.classes.find(c => c.id === classId) || null
      } else {
        this.comparedClass = null
      }
    },

    resetView() {
      this.currentView = 'class'
      this.selectedStudent = null
      this.compareMode = false
      this.comparedClass = null
    }
  },

  persist: {
    key: 'teacher-analytics',
    paths: ['timeRange', 'currentClass.id', 'compareMode']
  }
})