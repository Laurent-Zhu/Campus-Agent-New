import { createRouter, createWebHistory } from 'vue-router';

//教师端路由
import LessonPreparation from '../views/Teacher/LessonPreparation.vue';
import AnalyticsDashboard from '../views/Teacher/AnalyticsDashboard.vue';
import ExamGenerator from '../views/Teacher/ExamGenerator.vue';
import Login from '../views/login.vue';
import Register from '../views/register.vue';
import ClassList from '../views/Teacher/Analytics/ClassList.vue';
import AnalyticsView from '../views/Teacher/Analytics/AnalyticsView.vue';
import StudentView from '../components/Teacher/StudentList.vue';

//学生端路由
import ExerciseView from '../views/Student/ExerciseView.vue';

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
  },
  {
    path: '/exercise',
    name: 'Exercise',
    component: ExerciseView
  },

  //学生端路由
  
  //实时练习评测助手
  {
    path: '/student/exercise',
    name: 'Exercise',
    component: ExerciseView,
    meta: { 
      title: '智能练习评测',
      requiresAuth: true,
      role: 'student'
    }
  },
  {
    path: '/student/exercise/:exerciseId',
    name: 'ExerciseDetail',
    component: ExerciseView,
    props: true,
    meta: { 
      title: '题目练习',
      requiresAuth: true,
      role: 'student'
    }
  },
  {
    path: '/student/exercise/:history',
    name: 'History',
    component: ExerciseView,
    props: true,
    meta: { 
      title: '练习历史',
      requiresAuth: true,
      role: 'student',
      showHistory: true
    }
  },

  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;