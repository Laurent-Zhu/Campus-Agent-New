<template>
    <nav class="navbar">
        <div class="container">
            <!-- logo -->
            <div class="logo">
                <router-link to="/"><img src="../assets/img/xiaobai_answer_avatar.webp" alt="logo" class="logo-img"></router-link>
            </div>
        
            <!-- 导航菜单 -->
            <ul class="menu">
                <!-- 公共路由（始终显示） -->
                <li>
                    <router-link to="/" :class="{active: $route.path === '/'}">首页</router-link>
                </li>
                
                <!-- 动态路由（根据登录状态和角色显示） -->
                <template v-if="isAuthenticated">
                    <!-- 教师专属路由 -->
                    <template v-if="userRole === 'teacher'">
                        <li>
                            <router-link to="/teacher/lesson-preparation" :class="{active: $route.path === '/teacher/lesson-preparation'}">备课与设计</router-link>
                        </li>
                        <li>
                            <router-link to="/teacher/exam-generator" :class="{active: $route.path === '/teacher/exam-generator'}">考核内容生成</router-link>
                        </li>
                        <li>
                            <router-link to="/teacher/analytics" :class="{active: $route.path === '/teacher/analytics'}">学情分析</router-link>
                        </li>
                    </template>
                    
                    <!-- 学生专属路由 -->
                    <template v-else-if="userRole === 'student'">
                        <li>
                            <router-link to="/student/exercise" :class="{active: $route.path === '/student/exercise'}">实时测评助手</router-link>
                        </li>
                        <li>
                            <router-link to="/student/qa" :class="{active: $route.path === '/student/qa'}">在线学习助手</router-link>
                        </li>
                    </template>
                    
                    <!-- 管理员专属路由 -->
                    <template v-if="userRole === 'admin'">
                        <li>
                            <router-link to="/admin/resources" :class="{active: $route.path === '/admin/resources'}">资源管理</router-link>
                        </li>
                    </template>
                </template>
            </ul>

            <!-- 登录/注册或用户信息 -->
            <ul class="login">
                <template v-if="!isAuthenticated">
                    <li>
                        <router-link to="/login" :class="{active: $route.path === '/login'}">登录</router-link>
                    </li>
                    <li>
                        <router-link to="/register" :class="{active: $route.path === '/register'}">注册</router-link>
                    </li>
                </template>
                <template v-else>
                    <li>
                        <span class="username">{{ username }}</span>
                    </li>
                    <li>
                        <a href="#" @click.prevent="logout">退出</a>
                    </li>
                </template>
            </ul>
        </div>
    </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // 假设使用Pinia管理状态

const router = useRouter()
const authStore = useAuthStore()

// 从状态管理获取用户信息
const isAuthenticated = computed(() => authStore.isAuthenticated)
const userRole = computed(() => authStore.user?.role)
const username = computed(() => authStore.user?.username)

const logout = () => {
    authStore.logout()
    router.push('/login')
}
</script>

<style scoped>
/* 保持原有样式不变 */
.navbar {
    background-color: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 100;
}

.container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    height: 60px;
}

.logo {
    display: flex;
    align-items: center;
}
.logo-img {
    width: 70px;
    height: auto;
    margin-right: 10px;
}

.menu {
    display: flex;
    list-style: none;
    gap: 30px;
    margin: 0;
    padding: 0;
}

.menu li a {
    color: #111;
    text-decoration: none;
    padding: 20px 12px;
    transition: background-color 0.3s ease;
}

.menu li a.active {
    background-color: #cdcdcd;
}

.menu li a:hover {
    color: #757575;
}

.login {
    display: flex;
    list-style: none;
    gap: 20px;
    margin: 0;
    padding: 0;
}

.login li a {
    color: #8a8ff7;
    text-decoration: none;
    padding: 20px 12px;
    transition: background-color 0.3s ease;
}

.login li a:hover {
    color: #101ad0;
}

.username {
    color: #333;
    padding: 20px 12px;
    display: inline-block;
}
</style>