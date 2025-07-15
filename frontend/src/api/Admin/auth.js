// 用于处理用户管理 API 请求
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1/auth/';

// 获取用户列表
export const fetchUsers = async (token) => {
    try {
        const response = await axios.get(API_URL + 'users', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        return response.data;
      } catch (error) {
        console.error('获取用户列表失败:', error);
        throw error;
      }
};

// 创建用户
export const createUser = async (token, userData) => {
    try {
      const response = await axios.post(API_URL + 'users', userData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('创建用户失败:', error);
      throw error;
    }
  };
  
// 更新用户
  export const updateUser = async (token, userId, userData) => {
    try {
      const response = await axios.put(API_URL + `users/${userId}`, userData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      return response.data;
    } catch (error) {
      console.error('更新用户失败:', error);
      throw error;
    }
  };
  
// 删除用户
  export const deleteUser = async (token, userId) => {
    try {
      await axios.delete(API_URL + `users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('删除用户失败:', error);
      throw error;
    }
  };