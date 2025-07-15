from django.db.models import Q
import random
import json
from django.core.exceptions import ObjectDoesNotExist
from student.exercises.models import Exercise, ExerciseAttempt, StudentProfile, KnowledgePoint
from django.contrib.auth import get_user_model
from .llm_service import LLMService

User = get_user_model()
llm = LLMService()  # 初始化LLM服务

def generate_personalized_exercise(student_id, difficulty=None, knowledge_point_ids=None):
    """
    生成个性化练习题（优先LLM生成，失败时降级到数据库）
    
    参数:
        student_id: 学生ID（String/Int）
        difficulty: 可选难度 ('easy', 'medium', 'hard')
        knowledge_point_ids: 可选知识点ID列表
        
    返回:
        Exercise对象
        
    异常:
        ValueError: 参数无效或没有可用题目
    """

    print(f"\n====== 开始生成题目调试信息 ======")
    print(f"传入参数: student_id={student_id}({type(student_id)}), difficulty={difficulty}, knowledge_point_ids={knowledge_point_ids}")


    # 1. 验证参数
    valid_difficulties = ['easy', 'medium', 'hard']
    
    try:

        try:
            student_id_int = int(student_id)
        except (ValueError, TypeError):
            raise ValueError(f"无效的用户ID格式: {student_id}")

        student = User.objects.get(id=student_id_int)
    except User.DoesNotExist:
        raise ValueError(f"用户ID {student_id} 不存在")
    
    # 2. 自动推断难度（如果未指定）
    if not difficulty:
        try:
            profile = StudentProfile.objects.get(user=student)
            if profile.correct_rate < 0.6:  # 使用正确率代替average_score
                difficulty = 'easy'
            elif profile.correct_rate < 0.8:
                difficulty = 'medium'
            else:
                difficulty = 'hard'
        except StudentProfile.DoesNotExist:
            difficulty = 'easy'  # 默认难度

    # 3. 验证难度有效性
    if difficulty.lower() not in valid_difficulties:
        raise ValueError(f"无效难度级别: {difficulty}。请使用: {valid_difficulties}")

    # 4. 获取学生数据（用于LLM生成）
    try:
        profile = student.studentprofile
        student_data = {
            "id": student_id_int,
            "correct_rate": profile.correct_rate,
            "weak_points": list(profile.weak_knowledge_points.values_list('name', flat=True))
        }
    except StudentProfile.DoesNotExist:
         # 如果不存在学生档案，创建默认档案
        profile = StudentProfile.objects.create(user=student)
        student_data = {
            "id": student_id_int,
            "correct_rate": 0.5,  # 默认正确率
            "weak_points": []
        }

    # 5. 优先尝试LLM生成题目
    if _should_use_llm(student_data):
        try:
            llm_result = llm.generate_question(
                student_data=student_data,
                difficulty=difficulty,
                knowledge_points=knowledge_point_ids
            )
            
            if "error" not in llm_result:
                # 创建并返回新题目（适配新的Exercise模型）
                return Exercise.objects.create(
                    title=llm_result.get("title", "AI生成题目"),
                    content=llm_result["question"],
                    question_type=llm_result.get("question_type", "mc"),
                    difficulty=difficulty,
                    answer={
                        "reference_answer": llm_result["answer"],
                        "options": llm_result.get("options", []),
                        "explanation": llm_result.get("explanation", "")
                    },
                    explanation=llm_result.get("explanation", ""),
                    is_active=True
                )
        except Exception as e:
            print(f"[LLM Fallback] 生成失败: {str(e)}")

    # 6. 降级到数据库题目
    return _get_fallback_exercise(
        student_id=student_id_int,
        difficulty=difficulty,
        knowledge_point_ids=knowledge_point_ids
    )

def _should_use_llm(student_data):
    """判断是否满足LLM生成条件"""
    # 规则示例：当学生有薄弱知识点时优先使用LLM
    return len(student_data.get("weak_points", [])) > 0

def _get_fallback_exercise(student_id, difficulty, knowledge_point_ids):
    """
    从数据库获取题目降级方案
    """
    # 1. 排除最近做过的题目（最近10条）
    recent_exercises = ExerciseAttempt.objects.filter(
        student_id=student_id
    ).order_by('-created_at').values_list('exercise_id', flat=True)[:10]
    
    # 2. 构建基础查询
    queryset = Exercise.objects.filter(
        difficulty__iexact=difficulty,
        is_active=True  # 只使用活跃题目
    ).exclude(id__in=recent_exercises)
    
    # 3. 应用知识点过滤
    if knowledge_point_ids:
        queryset = queryset.filter(
            knowledge_points__id__in=knowledge_point_ids
        ).distinct()
    else:
        # 如果没有指定知识点，尝试使用学生薄弱点
        try:
            student = User.objects.get(id=student_id)
            weak_points = student.studentprofile.weak_knowledge_points.all()
            if weak_points.exists():
                queryset = queryset.filter(
                    knowledge_points__in=weak_points
                ).distinct()
        except (ObjectDoesNotExist, AttributeError):
            pass
    
    # 4. 如果无结果，放宽条件（允许重复题目）
    if not queryset.exists():
        queryset = Exercise.objects.filter(
            difficulty__iexact=difficulty,
            is_active=True
        )
        if knowledge_point_ids:
            queryset = queryset.filter(
                knowledge_points__id__in=knowledge_point_ids
            ).distinct()
    
    # 5. 最终检查
    if not queryset.exists():
        raise ValueError(f"没有找到符合条件的题目（难度: {difficulty}）")
    
    # 6. 随机选择一道题
    return random.choice(queryset)