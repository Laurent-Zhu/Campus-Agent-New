import { defineStore } from 'pinia'
import axios from 'axios'

export const useExamStore = defineStore('exam', {
  state: () => ({
    courseOptions: [
      { id: 1, name: 'TensorFlow.js应用开发' },
      { id: 2, name: 'TensorFlow Lite部署' },
      { id: 3, name: '嵌入式Python开发' }
    ],
    knowledgePointMap: {
      1: [
        'TensorFlow.js',
        'JavaScript机器学习库',
        '浏览器端部署',
        'Layers API',
        'Core API',
        '张量(Tensor)',
        '模型序列化',
        'tfjs-vis可视化',
        '线性回归模型',
        '手写数字识别(CNN)'
      ],
      2: [
        'TensorFlow Lite(TFLite)',
        'FlatBuffers格式',
        '模型转换器(Converter)',
        '解释器(Interpreter)',
        '量化优化',
        'MobileNet模型',
        'Android部署(AAR)',
        '硬件加速代理(GPU/NNAPI)',
        'PoseNet模型'
      ],
      3: [
        '树莓派(Raspberry Pi)',
        'NVIDIA Jetson Nano',
        'GPIO接口',
        'OpenCV',
        'face_recognition库',
        'CSI摄像头',
        'GStreamer管道',
        '边缘计算',
        'Jupyter Lab',
        'Wiring Pi库'
      ]
    }
  }),
  
  actions: {
    async generateExam(config) {
      const response = await axios.post('/api/v1/exams/generate', config)
      return response.data
    },
    
    async saveExam(exam) {
      const response = await axios.post('/api/v1/exams', exam)
      return response.data
    }
  }
})