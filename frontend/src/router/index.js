import { createRouter, createWebHistory } from 'vue-router';
import LessonPreparation from '../views/Teacher/LessonPreparation.vue';
import AnalyticsDashboard from '../views/Teacher/AnalyticsDashboard.vue';
import ExamGenerator from '../views/Teacher/ExamGenerator.vue';
import Login from '../views/login.vue';
import Register from '../views/register.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    // redirect: '/login' // 默认跳转到登录页面
    // component: navbar => import('../components/navbar.vue'),
  },
  {
    path: '/teacher/lesson-preparation',
    name: 'LessonPreparation',
    component: LessonPreparation
  },
  {
    path:'/teacher/analytics',
    name:'Analytics',
    component:AnalyticsDashboard,
  },
  {
    path: '/teacher/exam-generator',
    name: 'ExamGenerator',
    component: ExamGenerator
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  }
  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;