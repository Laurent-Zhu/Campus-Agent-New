import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { jwtDecode } from 'jwt-decode'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  
  // 状态
  const user = ref(null);
  const token = ref(localStorage.getItem('token') || null);
  const loading = ref(false);
  const error = ref(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value);
  const isStudent = computed(() => user.value?.role === 'student');
  const isTeacher = computed(() => user.value?.role === 'teacher');
  const isAdmin = computed(() => user.value?.role === 'admin');
  
  // 学生ID计算属性
  const studentId = computed(() => {
    if (!isStudent.value || !user.value?.id) return null;
    const id = Number(user.value.id);
    return isNaN(id) ? null : id;
  });

  

  // 解码JWT token
  const decodeToken = (token) => {
    try {
      const decoded = jwtDecode(token);
      console.log('Token解码结果:', decoded); // 调试日志
    
      // 确保必须字段存在
      if (!decoded.sub || !decoded.role) {
        throw new Error('Token缺少必要字段');
      }
      
      return {
        id: decoded.sub, 
        role: decoded.role
      };
    } catch (error) {
      console.error('JWT解码失败:', error);
      logout();
      return null;
    }
  };

   // 初始化认证状态
  const initializeAuth = () => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      try {
        const decoded = decodeToken(savedToken);
        if (decoded) {
          user.value = decoded;
          token.value = savedToken;
        }
      } catch (error) {
        console.error('初始化认证失败:', error);
        logout();
      }
    }
  };

  // 登录方法（现在完全由store管理）
  const login = async (credentials) => {
    loading.value = true;
    error.value = null;
    try {
      // 1.发送登录请求
      const response = await axios.post('/api/fastapi/v1/auth/login', credentials);
      
      console.log('完整响应:', response); // 调试日志

      // 2.检查token是否存在
      if (!response.data.access_token) {
        throw new Error('登录失败：未获取到token');
      }

      // 3.解码并存储用户信息
      const decodedUser = decodeToken(response.data.access_token);
      if (!decodedUser) {
        throw new Error('Token解码失败');
      }
      
      // 4. 更新状态
      token.value = response.data.access_token;
      user.value = decodedUser; // 直接使用decodeToken返回的结构
      localStorage.setItem('token', token.value);

      // 根据角色跳转
      redirectByRole(decodedUser.role);

      return true;
    } catch (err) {
      error.value = err.response?.data?.detail || '登录失败';
      return false;
    } finally {
      loading.value = false;
    }
  };

  // 登出
  const logout = () => {
    user.value = null;
    token.value = null;
    localStorage.removeItem('token');
    localStorage.removeItem('auth');
    router.push('/login');
  };

  // 角色跳转逻辑
  const redirectByRole = (role) => {
    const routes = {
      student: '/student/exercise',
      teacher: '/teacher/exam-generator',
      admin: '/admin/resources'
    };
    router.push(routes[role] || '/');
  };

  // 初始化执行
  initializeAuth();

  return {
    user,
    token,
    isAuthenticated,
    isStudent,
    isTeacher,
    isAdmin,
    studentId,
    loading,
    error,
    login,
    logout,
    redirectByRole
  };
});