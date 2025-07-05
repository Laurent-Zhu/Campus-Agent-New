import { faker } from '@faker-js/faker'

export const generateStudentDetail = (id) => ({
  id,
  name: faker.person.fullName(),
  score: Math.floor(60 + Math.random() * 40),
  wrongQuestions: Array.from({ length: 5 }, () => ({
    question: faker.lorem.sentence(),
    errorType: ['语法', '逻辑', '概念'][Math.floor(Math.random() * 3)]
  }))
})