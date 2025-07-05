import { createRouter, createWebHistory } from 'vue-router';
import LessonPreparation from '../views/Teacher/LessonPreparation.vue';
import AnalyticsDashboard from '../views/Teacher/AnalyticsDashboard.vue';
import ExamGenerator from '../views/Teacher/ExamGenerator.vue';
import Login from '../views/login.vue';
import Register from '../views/register.vue';
import ClassList from '../views/Teacher/Analytics/ClassList.vue';
import AnalyticsView from '../views/Teacher/Analytics/AnalyticsView.vue';
import StudentView from '../components/StudentList.vue';

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
  },
  {
    path:'/teacher/classes',
    component: ClassList
  },
  {
    path:'/teacher/classes/:classId',
    component: AnalyticsView,
    props: true     //将路径参数作为props传递给组件
  },
   {
    path: '/teacher/students/:studentId',
    component: StudentView,
    props: true
  },
  {
    path: '/teacher',
    redirect: '/classes'
  }
  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;