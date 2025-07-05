// src/mock/teacherData.js
export const mockClassrooms = [
  {
    id: 'class-1',
    name: '三年级二班',
    teacherId: 't-001',
    
    students: [
      { id: 's-001', name: '张三', accuracy: 82 },
      { id: 's-002', name: '李四', accuracy: 65 },
      { id: 's-003', name: '王五', accuracy: 73 }
    ]
  }
]

export const mockAssignments = [
  {
    id: 'assign-1',
    classId: 'class-1',
    title: 'Python基础测验',
    questions: [
      {
        id: 'q-1',
        knowledgePoint: '变量定义',
        content: '如何正确声明变量？',
        correctAnswer: 'var_name = value'
      }
    ]
  }
]

export const mockStudentAnswers = [
  {
    studentId: 's-001',
    assignmentId: 'assign-1',
    answers: [
      {
        questionId: 'q-1',
        answer: 'varName = value',
        isCorrect: false,
        errorType: '命名规范错误'
      }
    ]
  }
]