// src/axios.js
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'; 
import { v4 as uuidv4 } from 'uuid';




const instance = axios.create({
  baseURL: 'http://localhost:8001/api', // 注意这里不带结尾斜杠
  timeout: 10000
})





// 统一的请求拦截器
instance.interceptors.request.use(config => {
  const authStore = useAuthStore()
  const requestId = uuidv4()

  // 1. 打印当前存储的令牌（关键调试信息）
  console.debug('[全局拦截器] 当前存储的token:', {
    tokenExists: !!authStore.token, // 是否存在令牌
    tokenPreview: authStore.token ? authStore.token.substring(0, 20) + '...' : '无令牌' // 令牌前20位预览（避免过长）
  });
  
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
    console.debug('[全局拦截器] 已添加Authorization头:', `Bearer ${authStore.token.substring(0, 20)}...`);
  }
  
  config.headers['X-Request-ID'] = requestId
  
  // 调试日志
  console.debug(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
    headers: config.headers,
    data: config.data
  })
  
  return config
}, error => {
  console.error('[API] Request interceptor error:', error)
  return Promise.reject(error)
})

export default instance