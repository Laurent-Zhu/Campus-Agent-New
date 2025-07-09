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
import QuestionAnswer from "../views/Student/QuestionAnswer.vue";


//学生端路由
import ExerciseView from '../views/Student/ExerciseView.vue';
import ResourceAdmin from '../views/Administor/ResourceAdmin.vue';

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
  {
    path: "/student/qa",
    name: "QuestionAnswer",
    component: QuestionAnswer,
  },

  // 管理员端路由
  // 课件资源管理模块
  {
    path: '/admin/resources',
    name: 'ResourceAdmin',
    component: ResourceAdmin,
    meta: { 
      title: '课件资源管理',
      requiresAuth: true,
      role: 'admin'
    }
  }

  // Add other routes as needed
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 权限校验，暂不开放
// router.beforeEach((to, from, next) => { 
//   const token = localStorage.getItem('token')
//   const userRole = localStorage.getItem('role')// 假设角色存储在localStorage中

//   if (to.meta.requiresAuth && !token) {
//     next('/login') // 未登录，跳转到登录页面
//   } else if (to.meta.role && userRole !== to.meta.role) {
//     next('/forbidden') // 角色不匹配，跳转到无权限页
//   } else {
//     next() // 允许通过
//   }
// })

export default router;