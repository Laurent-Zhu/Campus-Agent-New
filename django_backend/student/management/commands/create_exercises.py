import os
import django
import json
from pathlib import Path
from django.core.management.base import BaseCommand

from student.exercises.models import Exercise, KnowledgePoint

class Command(BaseCommand):
    help = 'Create technical exercises for the system'

    def handle(self, *args, **options):
        self.stdout.write("Starting to create technical exercises...")
        self.create_tech_exercises()
        self.stdout.write(self.style.SUCCESS("Successfully created technical exercises!"))

    def create_tech_exercises(self):
        # 清除旧数据（可选）
        KnowledgePoint.objects.all().delete()
        Exercise.objects.all().delete()
        
        # 1. 创建知识点
        tfjs_kp = KnowledgePoint.objects.create(
            name="TensorFlow.js",
            description="TensorFlow的JavaScript版本，用于浏览器和Node.js中的机器学习",
            difficulty_level=0.6
        )
        
        tflite_kp = KnowledgePoint.objects.create(
            name="TensorFlow Lite",
            description="TensorFlow的轻量级版本，用于移动和嵌入式设备",
            difficulty_level=0.7
        )
        
        raspberry_kp = KnowledgePoint.objects.create(
            name="树莓派GPIO控制",
            description="树莓派的通用输入输出引脚控制",
            difficulty_level=0.5
        )
        
        jetson_kp = KnowledgePoint.objects.create(
            name="Jetson Nano开发",
            description="NVIDIA Jetson Nano边缘计算开发板",
            difficulty_level=0.7
        )
        
        opencv_kp = KnowledgePoint.objects.create(
            name="OpenCV人脸检测",
            description="使用OpenCV进行计算机视觉和人脸检测",
            difficulty_level=0.6
        )

        # 2. 创建选择题
        mc_questions = [
            {
                "title": "TensorFlow.js主要优势",
                "content": "TensorFlow.js的主要优势不包括以下哪一项？\nA. 支持在浏览器中直接运行机器学习模型\nB. 支持与微信小程序集成\nC. 需要服务器端支持才能运行模型\nD. 提供预训练模型（如图像识别、语音识别）",
                "answer": {
                    "reference_answer": "C",
                    "options": ["A", "B", "C", "D"],
                    "correct_options": ["C"]
                },
                "explanation": "TensorFlow.js可以直接在浏览器中运行，无需服务器端支持。",
                "difficulty": "easy",
                "knowledge_points": [tfjs_kp]
            },
            {
                "title": "TensorFlow Lite FlatBuffers",
                "content": "TensorFlow Lite模型转换过程中，FlatBuffers格式的主要作用是？\nA. 提高模型训练速度\nB. 减少模型大小并支持内存高效加载\nC. 增加模型的可视化功能\nD. 支持多语言模型开发",
                "answer": {
                    "reference_answer": "B",
                    "options": ["A", "B", "C", "D"],
                    "correct_options": ["B"]
                },
                "explanation": "FlatBuffers格式减少了模型大小，并允许直接映射到内存中，无需额外解析。",
                "difficulty": "medium",
                "knowledge_points": [tflite_kp]
            },
            # 添加其他选择题...
        ]

        # 3. 创建填空题
        fb_questions = [
            {
                "title": "TensorFlow.js API类型",
                "content": "TensorFlow.js的两种创建模型的方式是______和______。",
                "answer": {
                    "reference_answer": ["Layers API", "Core API"],
                    "possible_answers": [["Layers API", "Core API"], ["Core API", "Layers API"]]
                },
                "explanation": "Layers API是高级API，Core API是低级API。",
                "difficulty": "easy",
                "knowledge_points": [tfjs_kp]
            },
            {
                "title": "TensorFlow Lite加速器",
                "content": "在TensorFlow Lite中，解释器通过______调用硬件加速器（如GPU）来提升模型推理性能。",
                "answer": {
                    "reference_answer": ["Delegate"],
                    "possible_answers": [["Delegate"], ["代理"], ["delegate"]]
                },
                "explanation": "例如GPU Delegate可以调用GPU加速计算。",
                "difficulty": "medium",
                "knowledge_points": [tflite_kp]
            },
            # 添加其他填空题...
        ]

        # 4. 创建简答题
        sa_questions = [
            {
                "title": "TensorFlow Lite模型转换",
                "content": "简述TensorFlow Lite模型转换的步骤及其作用。",
                "answer": {
                    "reference_answer": [
                        "选择模型：使用预训练模型或自定义模型。",
                        "转换模型：通过TFLite转换器将TensorFlow模型转换为.tflite格式，过程中可进行量化等优化。",
                        "部署到设备：在移动端或嵌入式设备上使用TFLite解释器运行模型。",
                        "优化模型：通过量化、剪枝等技术减少模型大小和延迟。"
                    ]
                },
                "explanation": "模型转换是部署到边缘设备的关键步骤。",
                "difficulty": "hard",
                "knowledge_points": [tflite_kp]
            }
        ]

        # 5. 创建编程题
        code_questions = [
            {
                "title": "树莓派LED控制",
                "content": "如何在树莓派上通过Python控制LED灯的闪烁？请写出关键代码片段。",
                "answer": {
                    "reference_answer": [
                        "import RPi.GPIO as GPIO",
                        "import time",
                        "GPIO.setmode(GPIO.BCM)",
                        "GPIO.setup(21, GPIO.OUT)",
                        "try:",
                        "    while True:",
                        "        GPIO.output(21, GPIO.HIGH)",
                        "        time.sleep(1)",
                        "        GPIO.output(21, GPIO.LOW)",
                        "        time.sleep(1)",
                        "except KeyboardInterrupt:",
                        "    GPIO.cleanup()"
                    ],
                    "code_template": "import RPi.GPIO as GPIO\nimport time\n# 你的代码 here"
                },
                "explanation": "使用BCM编号模式控制GPIO引脚。",
                "difficulty": "medium",
                "knowledge_points": [raspberry_kp]
            }
        ]

        # 6. 保存所有题目到数据库
        for q in mc_questions:
            exercise = Exercise.objects.create(
                title=q["title"],
                content=q["content"],
                question_type="mc",
                answer=q["answer"],
                explanation=q["explanation"],
                difficulty=q["difficulty"]
            )
            for kp in q["knowledge_points"]:
                exercise.knowledge_points.add(kp)

        for q in fb_questions:
            exercise = Exercise.objects.create(
                title=q["title"],
                content=q["content"],
                question_type="fb",
                answer=q["answer"],
                explanation=q["explanation"],
                difficulty=q["difficulty"]
            )
            for kp in q["knowledge_points"]:
                exercise.knowledge_points.add(kp)

        for q in sa_questions:
            exercise = Exercise.objects.create(
                title=q["title"],
                content=q["content"],
                question_type="doc",  # 使用文档分析题类型作为简答题
                answer=q["answer"],
                explanation=q["explanation"],
                difficulty=q["difficulty"]
            )
            for kp in q["knowledge_points"]:
                exercise.knowledge_points.add(kp)

        for q in code_questions:
            exercise = Exercise.objects.create(
                title=q["title"],
                content=q["content"],
                question_type="code",
                answer=q["answer"],
                explanation=q["explanation"],
                difficulty=q["difficulty"]
            )
            for kp in q["knowledge_points"]:
                exercise.knowledge_points.add(kp)