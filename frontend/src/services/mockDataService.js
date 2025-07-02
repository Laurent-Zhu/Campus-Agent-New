// src/services/mockDataService.js
import {
  mockClassrooms,
  mockAssignments,
  mockStudentAnswers
} from '@/mock/teacherData'

//获取教师负责的所有班级
export const getTeacherClasses = (teacherId) => {
  return mockClassrooms.filter(c => c.teacherId === teacherId)
}

//生成班级的学情报告
export const getClassAnalytics = (classId) => {
  const students = mockClassrooms.find(c => c.id === classId)?.students || []
  const assignments = mockAssignments.filter(a => a.classId === classId)
  
  return {
    avgAccuracy: Math.round(students.reduce((sum, s) => sum + s.accuracy, 0) / students.length),
    weakPoints: ['循环结构', '函数参数'],
    knowledgeDistribution: [
      { name: '变量定义', mastery: 82 },
      { name: '循环结构', mastery: 65 }
    ]
  }
}

//获取学生的错题详情
export const getStudentDetails = (studentId) => {
  const answers = mockStudentAnswers.filter(a => a.studentId === studentId)
  return {
    wrongQuestions: answers.flatMap(a => 
      a.answers.filter(ans => !ans.isCorrect).map(ans => {
        const question = mockAssignments
          .flatMap(a => a.questions)
          .find(q => q.id === ans.questionId)
        return {
          ...question,
          studentAnswer: ans.answer,
          errorType: ans.errorType
        }
      })
  )}
}