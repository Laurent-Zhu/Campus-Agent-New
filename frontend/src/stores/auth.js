import { defineStore } from 'pinia';
import { computed, ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const isAuthenticated = ref(false);
  const user = ref(null); // { username: string, role: 'student'|'teacher'|'admin' }

  // Getters
  const isStudent = computed(() => user.value?.role === 'student');
  const isTeacher = computed(() => user.value?.role === 'teacher');
  const isAdmin = computed(() => user.value?.role === 'admin');

  // Actions
  const login = (userData) => {
    isAuthenticated.value = true;
    user.value = userData;
    localStorage.setItem('auth', JSON.stringify(userData));
  };

  const logout = () => {
    isAuthenticated.value = false;
    user.value = null;
    localStorage.removeItem('auth');
    localStorage.removeItem('token');
  };

  // 初始化时从本地存储恢复状态
  const init = () => {
    const savedAuth = localStorage.getItem('auth');
    if (savedAuth) {
      user.value = JSON.parse(savedAuth);
      isAuthenticated.value = true;
    }
  };

  init(); // 立即执行初始化

  return { 
    isAuthenticated, 
    user,
    isStudent,
    isTeacher,
    isAdmin,
    login, 
    logout 
  };
});