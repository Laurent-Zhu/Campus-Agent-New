<template>
    <div class="register-container">
      <h1>用户注册</h1>
      <div class="register-card">
        <el-form :model="form" @submit.prevent="handleRegister" label-position="top">
          <h2>注册信息</h2>
          <el-form-item label="用户名">
            <el-input v-model="form.username" autocomplete="username" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="form.email" autocomplete="email" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input
              v-model="form.password"
              type="password"
              autocomplete="new-password"
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
              @click="handleRegister"
              :disabled="loading"
            >
              {{ loading ? '正在注册...' : '注册' }}
            </button>
          </el-form-item>
        </el-form>
        <div class="login-link">
          已有账号？<router-link to="/login">去登录</router-link>
        </div>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'Register',
    data() {
      return {
        form: {
          username: '',
          email: '',
          password: '',
          role: ''
        },
        loading: false,
        errorMessage: ''
      };
    },
    methods: {
      async handleRegister() {
        this.loading = true;
        this.errorMessage = '';
        try {
          await axios.post('/api/v1/auth/register', {
            username: this.form.username,
            email: this.form.email,
            password: this.form.password,
            role: this.form.role
          });
          this.$router.push('/login');
          alert('注册成功，请登录');
        } catch (e) {
          this.errorMessage = e?.response?.data?.detail || '注册失败';
        } finally {
          this.loading = false;
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .register-container {
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
  
  .register-card {
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
  
  .login-link {
    margin-top: 16px;
    font-size: 14px;
    color: #57606a;
    text-align: center;
  }
  
  .login-link a {
    color: #0969da;
    text-decoration: none;
  }
  
  .login-link a:hover {
    text-decoration: underline;
  }
  
  .error-message {
    color: red;
    margin-top: 10px;
  }
  </style>