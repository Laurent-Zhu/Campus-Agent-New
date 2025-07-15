<template>
    <div class="user-admin-container">
        <h2>用户管理</h2>

        <!-- 添加用户表单 -->
        <div class="add-user-form">
            <input type="text" v-model="newUser.username" placeholder="用户名" class="input-field"> 
            <input type="email" v-model="newUser.email" placeholder="邮箱" class="input-field">
            <input type="password" v-model="newUser.password" placeholder="密码" class="input-field"></input>
            <select name="role" v-model="newUser.role" class="input-field">
                <option value="teacher">教师</option>
                <option value="student">学生</option>
                <option value="admin">管理员</option>
            </select>
            <button @click="handleCreateUser" class="action-button">添加用户</button>
        </div>

        <!-- 搜索框 -->
        <div class="search-container">
            <input type="text" v-model="searchQuery" @input="filterUsers" placeholder="搜索用户名..." class="search-input">
        </div>
        
        <!-- 用户列表 -->
        <ul class="user-list">
            <li v-for="user in filterUsers" :key="user.id" class="user-item">
                <div class="user-info">
                    <span class="username">{{ user.username }}</span>
                    <span class="role badge">{{ user.role }}</span>
                </div>
                <div class="user-actions">
                    <button @click="editUser(user)" class="edit-button">编辑</button>
                    <button @click="handleDeleteUser(user.id)" class="delete-button">删除</button>
                </div>
            </li>
        </ul>

        <!-- 编辑用户模态框 -->
        <div v-if="isEditing" class="modal">
            <div class="modal-content">
                <h3>编辑用户</h3>
                <input type="text" v-model="editingUser.username" placeholder="用户名" class="input-field">
                <input type="email" v-model="editingUser.email" placeholder="邮箱" class="input-field">
                <select v-model="editingUser.role" class="input-field">
                    <option value="teacher">教师</option>
                    <option value="student">学生</option>
                    <option value="admin">管理员</option>
                </select>

                <div class="modal-actions">
                    <button @click="cancelEdit" class="cancel-button">取消</button>
                    <button @click="handleUpdateUser" class="save-button">保存</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {fetchUsers, createUser, updateUser, deleteUser} from '@/api/Admin/auth'

    export default {
        data() {
            return {
                users: [],
                filteredUsers:[],
                newUser: {
                    username: '',
                    email: '',
                    password: '',
                    role: 'user'
                },
                searchQuery: '',
                isEditing: false,
                editingUser: {
                    id: '',
                    username: '',
                    email: '',
                    role: 'user'
                }
            }
        },
        mounted() {
            this.loadUsers()
        },
        methods: {
            // 加载用户
            async loadUsers() {
                const token = localStorage.getItem('token')

                try {
                    const users = await fetchUsers(token);
                    this.users = users;
                    this.filterUsers = users; 
                } catch (error) {
                    console.error("获取用户列表失败:", error);
                }
            },

            // 搜索用户
            filterUsers(){
                if(!this.searchQuery){
                    this.filterUsers = this.users;
                    return;
                }

                const query = this.searchQuery.toLowerCase();
                this.filterUsers = this.users.filter(user => 
                    user.username.toLowerCase().includes(query)
                )
            },

            // 编辑用户
            editUser(user) {
                this.isEditing = true;
                this.editingUser = {...user}; // 创建副本，避免直接修改原数据
            },

            // 取消编辑
            cancelEdit() {
                this.isEditing = false;
                this.editingUser = {
                    id: null,
                    username: '',
                    email: '',
                    role: 'user'
                };
            },

            // 处理创建用户
            async handleCreateUser () {
                const token = localStorage.getItem('token');

                try {
                    await createUser(token, this.newUser);
                    this.loadUsers(); // 重新加载用户列表
                    this.newUser = { // 重置表单
                        username: '',
                        email: '',
                        password: '',
                        role: 'user'
                    };
                    // 提示创建成功
                    ElMessage.success('用户创建成功');
                } catch (error) {
                    console.error('创建用户失败:', error);
                }
            },

            // 处理更新用户
            async handleUpdateUser() { 
                const token = localStorage.getItem('token');

                try {
                    await updateUser(token, this.editingUser.id, this.editingUser);
                    this.loadUsers();
                    this.cancelEdit();
                    ElMessage.success('更新用户成功');
                } catch (error) {
                    console.error('更新用户失败:', error);
                    ElMessage.error('更新用户失败');
                }
            },

            // 处理删除用户
            async handleDeleteUser(userId) {
                if (!confirm('确定要删除此用户吗？')) {
                    return
                }

                const token = localStorage.getItem('token');

                try {
                    await deleteUser(token, userId);
                    this.loadUsers();

                    alert('删除成功');
                } catch (error) {
                    console.error('删除用户失败:', error);
                    alert('删除失败');
                }
            },
        }
    }
</script>

<style scoped> 
.user-admin-container {
    max-width: 800px;
    margin: 0  auto;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.add-user-form { 
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.search-container {
    margin-bottom: 20px;
}

.search-input {
    width: 80%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.input-field {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.user-list {
    list-style-type: none;
    padding: 0;
}

.user-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    margin-bottom: 10px;
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}

.user-item:hover {
    background-color: #f0f0f0;
}

.user-info { 
    flex: 1;
}

.username {
    font-weight: bold;
    color: #333;
    margin-right: 10px;
}

.badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
}

.badge.teacher,
.badge.student {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.badge.admin {
  background-color: #e3f2fd;
  color: #1976d2;
}

.user-actions {
  display: flex;
  gap: 5px;
}

.action-button,
.edit-button,
.delete-button,
.cancel-button,
.save-button {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}

.action-button {
  background-color: #4caf50;
  color: white;
}

.edit-button {
  background-color: #2196f3;
  color: white;
}

.delete-button {
  background-color: #f44336;
  color: white;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
  width: 400px;
  max-width: 90%;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button {
  background-color: #ddd;
  color: #333;
}

.save-button {
  background-color: #4caf50;
  color: white;
}
</style>