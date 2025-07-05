// stores/classStore.js (更新版)
import { defineStore } from 'pinia'
import { fetchClassList } from '@/api/teacher'

export const useClassStore = defineStore('class', {
  state: () => ({
    rawClasses: [],
    loading: false,
    currentClassId: null
  }),
  getters: {
    currentClass(state) {
      return state.rawClasses.find(c => c.id === state.currentClassId)
    },
    classesBrief() {
      return this.rawClasses.map(c => ({
        id: c.id,
        name: c.name,
        studentCount: c.students?.length || 0
      }))
    }
  },
  actions: {
    async loadClasses() {
      this.loading = true
      try {
        this.rawClasses = await fetchClassList()
      } finally {
        this.loading = false
      }
    },
    setCurrentClass(id) {
      this.currentClassId = id
    }
  }
})