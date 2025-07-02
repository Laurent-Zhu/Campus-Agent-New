//
//类型定义文件


//时间范围类型
type TimeRangeType = 'week' | 'month' | 'term' | 'year'


//班级核心结构
interface ClassOverview {
  id: string
  name: string
  studentCount: number
  averageScore: number
  students: StudentBrief[]
  subject: string
  recentActivity: string
}

// 作业得分类型
interface AssignmentScore {
  assignmentId: string
  title: string
  score: number          // 实际得分
  classAverage: number   // 班级平均分
  rank: number           // 班级排名
  completionDate: string // 提交日期
}

//学生层级结构
//学生简略信息
interface StudentBrief {
  id: string
  name: string
  overallScore: number
  accuracyTrend: number[]
}

//学生详情
interface StudentDetail extends StudentBrief {
  wrongQuestions: WrongQuestion[]
  knowledgeWeaknesses: KnowledgeMastery[]
  assignmentScores: AssignmentScore[]
  behaviorAnalysis: {
    submissionTimeliness: number
    practiceFrequency: number
  }
}


//错题分析
interface WrongQuestion {
  questionId: string
  knowledgePoint: string
  errorType: string
  times: number
  lastAttempt: string
}

//知识点掌握度
interface KnowledgeMastery {
  knowledgeId: string
  name: string
  masteryRate: number
  trend: number[]
  relatedQuestions: string[]
}

//作业分析结构
interface AssignmentStat {
  id: string
  title: string
  averageScore: number
  completionRate: number
  difficulty: number
  questionAnalysis: QuestionAnalysis[]
}

//题目级分析
interface QuestionAnalysis {
  questionId: string
  correctRate: number
  commonErrors: string[]
}