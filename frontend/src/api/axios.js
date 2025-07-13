// src/axios.js
import axios from 'axios'

const instance = axios.create({
  baseURL: 'http://localhost:8001/api', // 注意这里不带结尾斜杠
  timeout: 10000
})

// 请求拦截器，自动添加Authorization头
instance.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default instance