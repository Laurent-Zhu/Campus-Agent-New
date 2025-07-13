<template>
  <div class="login-container">
    <h1>用户登录</h1>
    <div class="login-card">
      <el-form 
        :model="form" 
        @submit.prevent="handleLogin" 
        label-position="top"
      >
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
          <el-button
            type="primary"
            @click="handleLogin"
            :loading="authStore.loading"
            native-type="submit"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <p v-if="authStore.error" class="error-message">
        {{ authStore.error }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const form = ref({
  username: '',
  password: '',
  role: ''
});

const handleLogin = async () => {
  try {
    const success = await authStore.login(form.value);
    if (!success && authStore.error) {
      ElMessage.error(authStore.error); // 使用Element Plus显示错误
    }
  } catch (err) {
    console.error('登录异常:', err);
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