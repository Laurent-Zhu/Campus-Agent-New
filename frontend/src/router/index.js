import { createRouter, createWebHistory } from 'vue-router';
import LessonPreparation from '../views/Teacher/LessonPreparation.vue';
import AnalyticsDashboard from '../views/Teacher/AnalyticsDashboard.vue';
import ClassList from '../views/Teacher/Analytics/ClassList.vue';
import AnalyticsView from '../views/Teacher/Analytics/AnalyticsView.vue';
import StudentView from '../components/StudentList.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
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