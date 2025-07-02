import { createRouter, createWebHistory } from 'vue-router';
import LessonPreparation from '../views/Teacher/LessonPreparation.vue';

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
  }
  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;