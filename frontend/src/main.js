import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'; 

const app = createApp(App);
app.use(router);

// 开发环境下启用 Mock API
if (import.meta.env.MODE === 'development') {
  import('./api/mocks/browser').then(({ worker }) => {
    worker.start()
  }).then(() => {
    // Mock 服务启动后再挂载 Vue 应用
    app.mount('#app')
  })
} else {
  // 生产环境直接挂载
  app.mount('#app')
}