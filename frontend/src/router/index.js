import { createRouter, createWebHistory } from 'vue-router';
import LessonPreparation from '../views/Teacher/LessonPreparation.vue';
import AnalyticsDashboard from '../views/Teacher/AnalyticsDashboard.vue';

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
  }
  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;