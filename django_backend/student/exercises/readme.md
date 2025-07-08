核心API接口设计
接口1：生成个性化练习题
路由: POST /api/exercises/generate/

请求参数:

json
{
  "student_id": 1,
  "difficulty": "medium",  // 可选，不传则自动推断
  "knowledge_point_ids": [1, 2]  // 可选，指定知识点
}
响应:

json
{
  "exercise_id": 101,
  "question": "编写一个Python函数计算斐波那契数列...",
  "options": ["A. xxx", "B. xxx"],  // 如果是选择题
  "hint": "注意递归的终止条件"  // 可选提示
}
接口2：提交答案并获取评测
路由: POST /api/exercises/evaluate/

请求参数:

json
{
  "exercise_id": 101,
  "student_id": 1,
  "student_answer": "def fib(n):..."
}
响应:

json
{
  "is_correct": false,
  "score": 0.6,
  "feedback": "您的函数缺少对n=0的处理...",
  "correct_answer": "def fib(n):\n    if n <= 1:\n        return n\n    ..."
}
接口3：获取历史练习记录
路由: GET /api/history/?student_id=1&limit=5

响应:

json
{
  "results": [
    {
      "exercise_id": 101,
      "question": "编写一个Python函数...",
      "is_correct": false,
      "timestamp": "2023-10-01T14:30:00Z"
    }
  ]
}