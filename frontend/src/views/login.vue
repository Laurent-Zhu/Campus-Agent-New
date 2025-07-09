<template>
    <div class="login-container">
      <h1>用户登录</h1>
      <div class="login-card">
        <el-form :model="form" @submit.prevent="handleLogin" label-position="top">
          <h2>登录信息</h2>
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              autocomplete="current-password"
            />
          </el-form-item>
          <el-form-item label="身份">
            <el-select v-model="form.role" placeholder="请选择身份">
              <el-option label="学生" value="student"></el-option>
              <el-option label="教师" value="teacher"></el-option>
              <el-option label="管理员" value="admin"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item>
            <button
              @click="handleLogin"
              :disabled="loading"
            >
              {{ loading ? '正在登录...' : '登录' }}
            </button>
          </el-form-item>
        </el-form>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'Login',
    data() {
      return {
        form: {
          username: '',
          password: '',
          role: ''
        },
        loading: false,
        errorMessage: ''
      };
    },
    methods: {
      async handleLogin() {
        this.loading = true;
        this.errorMessage = '';
        try {
          const res = await axios.post('/api/fastapi/v1/auth/login', {
            username: this.form.username,
            password: this.form.password,
            role: this.form.role
          });
          localStorage.setItem('token', res.data.access_token);
          this.$router.push('/teacher/exam-generator');
        } catch (e) {
          this.errorMessage = e?.response?.data?.detail || '登录失败';
        } finally {
          this.loading = false;
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .login-container {
    padding: 20px;
    max-width: 900px;
    margin: 0 auto;
    font-family: Arial, sans-serif;
  }
  
  h1 {
    color: #333;
    text-align: center;
    margin-bottom: 20px;
  }
  
  .login-card {
    background-color: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }
  
  h2 {
    color: #555;
    margin-bottom: 15px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: bold;
  }
  
  input,
  select {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 4px;
    box-sizing: border-box;
  }
  
  button {
    background-color: #007bff;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    width: 100%;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  
  button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .error-message {
    color: red;
    margin-top: 10px;
  }
  </style>