export const generateClasses = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: `class-${i+1}`,
    name: `${['一', '二', '三'][i]}年级${i+1}班`,
    studentCount: 30,
    averageScore: Math.floor(70 + Math.random() * 20),
    subject: 'Python编程'
  }))
}