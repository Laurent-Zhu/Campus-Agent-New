<template> 
    <nav class="navbar">
        <div class="container">
            <!-- logo -->
            <div class="logo">
                 <router-link to="/"><img src="../assets/img/xiaobai_answer_avatar.webp" alt="logo" class="logo-img"></router-link>
            </div>
        
            <!-- 导航菜单 -->
            <ul class="menu">
                <li>
                    <router-link to="/" :class="{active: $route.path === '/'}">首页</router-link>
                </li>
                <li>
                    <router-link to="/teacher/lesson-preparation" :class="{active: $route.path === '/teacher/lesson-preparation'}">备课与设计</router-link>
                </li>
                <li>
                    <router-link to="/" :class="{active: $route.path === '/'}">考核内容生成</router-link>
                </li>
                <li>
                    <router-link to="/" :class="{active: $route.path === '/'}">学情分析</router-link>
                </li>
            </ul>

            <ul class="login">
                <li>
                    <router-link to="/login" :class="{active: $route.path === '/login'}">登录</router-link>
                </li>
                <li>
                    <router-link to="/register" :class="{active: $route.path === '/register'}">注册</router-link>
                </li>   
            </ul>
        </div>
    </nav>  
</template>

<style scoped>
    .navbar {
        /* background-color: #ababab; */
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
        /* margin-right: 40px; */
    }
    .logo-img {
        width: 70px;
        height: auto;
        margin-right: 10px;
    }
    .logo a {
        color: #fff;
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
</style>