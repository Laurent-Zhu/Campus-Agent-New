// src/api/mocks/handlers.js
import { http } from 'msw'  // 改为从msw导入http


export const handlers = [
  // 使用新的 http 方法
  http.get('/api/classes', () => {
    return Response.json([generateClasses()])
  }),
  
  http.get('/api/students/:id', ({ params }) => {
    return Response.json(generateStudentDetail(params.id))
  }),

  // POST 请求示例
  http.post('/api/submit', async ({ request }) => {
    const data = await request.json()
    return Response.json({ success: true })
  })
]