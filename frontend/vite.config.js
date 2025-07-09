import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve:{
    alias:{
      '@':path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api/django': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/django/, '/api'),
      },
      '/api/fastapi': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api\/fastapi/, '/api'),
      },
    }
  },

  // server: {
  //   proxy: {
  //     '/api': {
  //       target: 'https://dsp.lenovo.com.cn',
  //       changeOrigin: true,
  //       rewrite: (path) => path.replace(/^\/api/, '/lenovo'),
  //       secure: false, // 如果目标服务器使用 HTTPS 但证书有问题，可以加上这个
  //     }
  //   }
  // }
})
