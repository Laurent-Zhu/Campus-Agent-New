// mock/dataGenerator.js

//生成班级错题数据
export const generateClassData = (classSize = 30) => {
  return Array.from({length: classSize}, (_, i) => ({
    id: `S${2023000 + i}`,
    name: `学生${i + 1}`,
    accuracy: Math.min(100, Math.floor(Math.random() * 30) + 70),
    wrongQuestions: generateWrongQuestions() // 关联知识点体系
  }))
}




// 完善的知识图谱
const knowledgeGraph = {
  '循环结构': {
    'for循环': ['语法错误', '边界条件错误', '变量未初始化'],
    'while循环': ['无限循环', '条件表达式错误'],
    '嵌套循环': ['逻辑错误', '性能问题']
  },
  '函数': {
    '定义': ['语法错误', '命名不规范'],
    '参数': ['传参顺序错误', '默认值使用不当'],
    '返回值': ['遗漏return', '返回类型错误']
  },
  '面向对象': {
    '类定义': ['属性定义错误', '方法缺少self'],
    '继承': ['多继承冲突', '方法重写错误']
  }
}

// 错误类型权重配置（常见错误出现概率更高）
const errorWeights = {
  '语法错误': 0.4,
  '逻辑错误': 0.3,
  '概念误解': 0.2,
  '粗心错误': 0.1
}

// 生成错题数据
export const generateWrongQuestions = (studentLevel = 'normal') => {
  const wrongQuestions = []
  const questionCount = Math.floor(Math.random() * 5) + 3 // 每个学生3-7道错题
  
  // 根据学生水平调整错误频率
  const levelWeights = {
    'weak': { base: 5, var: 3 },
    'normal': { base: 3, var: 2 },
    'good': { base: 1, var: 1 }
  }
  const { base, var: variance } = levelWeights[studentLevel] || levelWeights.normal

  // 随机选择知识点
  const knowledgePoints = Object.keys(knowledgeGraph)
  for (let i = 0; i < questionCount; i++) {
    const point = knowledgePoints[Math.floor(Math.random() * knowledgePoints.length)]
    const subPoints = knowledgeGraph[point]
    const subPoint = Object.keys(subPoints)[Math.floor(Math.random() * Object.keys(subPoints).length)]
    const errorTypes = subPoints[subPoint]
    
    // 选择错误类型（加权随机）
    const errorType = weightedRandomSelect([
      ...errorTypes.map(t => ({ value: t, weight: 0.7 })),
      { value: '粗心错误', weight: 0.1 },
      { value: '概念误解', weight: 0.2 }
    ])

    wrongQuestions.push({
      questionId: `q-${Math.floor(Math.random() * 1000)}`,
      knowledgePoint: point,
      subPoint: subPoint,
      errorType: errorType,
      times: base + Math.floor(Math.random() * variance), // 错误次数
      lastWrongTime: generateRandomDate(), // 最近出错时间
      relatedQuestions: generateRelatedQuestions(point, subPoint) // 关联题目
    })
  }

  return wrongQuestions
}


// 辅助函数：加权随机选择
const weightedRandomSelect = (options) => {
  const total = options.reduce((sum, opt) => sum + opt.weight, 0)
  let random = Math.random() * total
  for (const opt of options) {
    if (random < opt.weight) return opt.value
    random -= opt.weight
  }
  return options[0].value
}



// 生成关联题目ID（用于错题推荐）
const generateRelatedQuestions = (point, subPoint) => {
  const count = Math.floor(Math.random() * 3) + 1
  return Array.from({ length: count }, () => 
    `q-${point.slice(0,2)}${subPoint.slice(0,2)}${Math.floor(Math.random() * 50)}`
  )
}



// 生成随机日期（最近3个月内）
const generateRandomDate = () => {
  const now = new Date()
  const past = new Date(now)
  past.setMonth(now.getMonth() - 3)
  return new Date(
    past.getTime() + Math.random() * (now.getTime() - past.getTime())
  ).toISOString().split('T')[0]
}


