from django.shortcuts import render

# Create your views here.

# student/views.py
from django.http import JsonResponse
from .models import Exercise, StudentExerciseLog

def generate_exercise(request):
    if request.method == 'POST':
        # 解析请求参数
        student_id = request.POST.get('student_id')
        difficulty = request.POST.get('difficulty', 'medium')  # 默认中等难度
        knowledge_point_ids = request.POST.get('knowledge_point_ids', [])

        # 业务逻辑：生成题目（示例）
        exercise = Exercise.objects.filter(
            difficulty=difficulty,
            knowledge_points__id__in=knowledge_point_ids
        ).order_by('?').first()  # 随机选一题

        return JsonResponse({
            "exercise_id": exercise.id,
            "question": exercise.question,
            "options": exercise.answer.get('options', []),
            "hint": "注意递归的终止条件"  # 可从数据库读取
        })

def evaluate_answer(request):
    if request.method == 'POST':
        exercise_id = request.POST.get('exercise_id')
        student_answer = request.POST.get('student_answer')

        # 业务逻辑：评测答案（示例）
        exercise = Exercise.objects.get(id=exercise_id)
        is_correct = (student_answer == exercise.answer['correct_answer'])

        # 保存记录
        log = StudentExerciseLog.objects.create(
            student_id=request.POST.get('student_id'),
            exercise=exercise,
            student_answer=student_answer,
            is_correct=is_correct
        )

        return JsonResponse({
            "is_correct": is_correct,
            "score": 0.6,  # 实际需计算
            "feedback": "您的函数缺少对n=0的处理...",
            "correct_answer": exercise.answer['correct_answer']
        })

def get_history(request):
    student_id = request.GET.get('student_id')
    limit = int(request.GET.get('limit', 5))

    logs = StudentExerciseLog.objects.filter(
        student_id=student_id
    ).order_by('-timestamp')[:limit]

    results = [{
        "exercise_id": log.exercise.id,
        "question": log.exercise.question[:50] + "...",  # 摘要
        "is_correct": log.is_correct,
        "timestamp": log.timestamp.isoformat()
    } for log in logs]

    return JsonResponse({"results": results})
