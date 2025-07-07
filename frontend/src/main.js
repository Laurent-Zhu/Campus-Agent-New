import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'  // ✅ 导入 Pinia
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const pinia = createPinia()

app.use(pinia)
app.use(router)  // ✅ 注册 Pinia 插件
app.use(ElementPlus)

// 启动 Mock 并挂载
// if (import.meta.env.MODE === 'development') {
//   import('./mocks/browser').then(({ worker }) => {
//     worker.start()
//   }).then(() => {
//     app.mount('#app')
//   })
// } else {
//   app.mount('#app')
// }

app.mount('#app')