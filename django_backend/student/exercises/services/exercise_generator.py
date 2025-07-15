from django.db.models import Q
import random
import json
from django.core.exceptions import ObjectDoesNotExist
from student.exercises.models import Exercise, ExerciseAttempt, StudentProfile, KnowledgePoint
# 移除对 Django User 模型的依赖
from .llm_service import LLMService

llm = LLMService()  # 初始化LLM服务


from django.contrib.auth import get_user_model
User = get_user_model()


def generate_personalized_exercise(student_id, difficulty=None, knowledge_point_ids=None, username=None, exercise_type=None):
    """
    生成个性化练习题（优先LLM生成，失败时降级到数据库）
    
    参数:
        student_id: 学生ID（从FastAPI获取的ID）
        difficulty: 可选难度 ('easy', 'medium', 'hard')
        knowledge_point_ids: 可选知识点ID列表
        exercise_type: 练习类型 ('knowledge', 'weakness', 'simulation')
        
    返回:
        Exercise对象
        
    异常:
        ValueError: 参数无效或没有可用题目
    """

    print(f"\n====== 开始生成题目调试信息 ======")
    print(f"传入参数: student_id={student_id}({type(student_id)}), difficulty={difficulty}, knowledge_point_ids={knowledge_point_ids}, exercise_type={exercise_type}({type(exercise_type)}")


    # 1. 验证参数
    valid_difficulties = ['easy', 'medium', 'hard']
    valid_types = ['knowledge', 'weakness', 'simulation']
    
    try:
        # 仅验证student_id是否为整数，不查询数据库
        student_id_int = int(student_id)
    except (ValueError, TypeError):
        raise ValueError(f"无效的用户ID格式: {student_id}")

     # 验证练习类型
    if exercise_type and exercise_type not in valid_types:
        raise ValueError(f"无效的练习类型: {exercise_type}。请使用: {valid_types}")


    # 2. 自动推断难度（如果未指定）
    if not difficulty:
        try:
            profile = StudentProfile.objects.get(fastapi_user_id=student_id_int)            # 根据正确率推断难度
            if profile.correct_rate < 0.6:
                difficulty = 'easy'
            elif profile.correct_rate < 0.8:
                difficulty = 'medium'
            else:
                difficulty = 'hard'
        except StudentProfile.DoesNotExist:
            # 学生档案不存在时，创建默认档案（需先确保 User 存在，或允许匿名）
            print(f"学生 {student_id_int} 档案不存在，创建默认档案")
            try:
                 # 基于fastapi_user_id和username创建档案（不关联Django User）
                profile = StudentProfile.objects.create(
                    fastapi_user_id=student_id_int,
                    username=username or f"user_{student_id_int}",  # 用FastAPI的username或默认名
                    correct_rate=0.5  # 默认正确率
                )
                difficulty = 'easy'
            except Exception as e:
                print(f"创建档案失败: {e}，使用默认难度")
                difficulty = 'easy'
        except Exception as e:
            print(f"[难度推断] 错误: {e}，使用默认难度")
            difficulty = 'easy'


    # 3. 验证难度有效性
    if difficulty.lower() not in valid_difficulties:
        raise ValueError(f"无效难度级别: {difficulty}。请使用: {valid_difficulties}")


    # 4. 获取学生数据（用于LLM生成，不依赖User表）
    try:
        # 通过fastapi_user_id查询学习档案
        profile = StudentProfile.objects.get(fastapi_user_id=student_id_int)
        # 提取学生数据（正确率、薄弱知识点）
        student_data = {
            "id": student_id_int,
            "username": profile.username,  # 从档案获取用户名
            "correct_rate": profile.correct_rate,
            "weak_points": list(profile.weak_knowledge_points.values_list('name', flat=True))
        }
    except StudentProfile.DoesNotExist:
        # 档案不存在时使用默认数据
        student_data = {
            "id": student_id_int,
            "username": username or f"user_{student_id_int}",
            "correct_rate": 0.5,
            "weak_points": []
        }
    except Exception as e:
        print(f"[学生数据获取] 错误: {e}，使用默认数据")
        student_data = {
            "id": student_id_int,
            "username": username or f"user_{student_id_int}",
            "correct_rate": 0.5,
            "weak_points": []
        }

    # 5. 根据练习类型调整参数
    if exercise_type == 'weakness':
        # 弱点专项：使用学生的薄弱知识点
        if not knowledge_point_ids and student_data['weak_points']:
            # 如果前端未指定知识点，使用学生的薄弱知识点
            weak_point_ids = list(KnowledgePoint.objects.filter(
                name__in=student_data['weak_points']
            ).values_list('id', flat=True))
            if weak_point_ids:
                knowledge_point_ids = weak_point_ids
                print(f"[弱点专项] 使用学生薄弱知识点: {student_data['weak_points']}")
    
    elif exercise_type == 'simulation':
        # 模拟测试：通常覆盖多个知识点
        if not knowledge_point_ids:
            # 如果未指定知识点，选择热门或核心知识点
            knowledge_point_ids = list(KnowledgePoint.objects.filter(
                is_core=True
            ).values_list('id', flat=True))
            print(f"[模拟测试] 使用核心知识点: {knowledge_point_ids}")



    # 5. 优先尝试LLM生成题目
    if _should_use_llm(student_data):
        try:
            llm_result = llm.generate_question(
                student_data=student_data,
                difficulty=difficulty,
                knowledge_point_ids=knowledge_point_ids,
                exercise_type=exercise_type 
            )
            
            if "error" not in llm_result:
                # 创建并返回新题目（适配Exercise模型）
                return Exercise.objects.create(
                    title=llm_result.get("title", "AI生成题目"),
                    content=llm_result["question"],
                    question_type=llm_result.get("question_type", "mc"),
                    difficulty=difficulty,
                    answer={
                        "reference_answer": llm_result["answer"]["reference_answer"],  # 适配LLM返回格式
                        "options": llm_result.get("options", []),
                        "explanation": llm_result["answer"].get("explanation", "")
                    },
                    explanation=llm_result["answer"].get("explanation", ""),
                    is_active=True,
                    exercise_type=exercise_type  # 存储练习类型
                )
        except Exception as e:
            print(f"[LLM Fallback] 生成失败: {str(e)}")


    # 6. 降级到数据库题目
    return _get_fallback_exercise(
        student_id=student_id_int,
        difficulty=difficulty,
        knowledge_point_ids=knowledge_point_ids,
        exercise_type=exercise_type  
    )





def _should_use_llm(student_data):
    """判断是否使用LLM生成（有薄弱知识点或低正确率）"""
    return len(student_data.get("weak_points", [])) > 0 or student_data.get("correct_rate", 1) < 0.7






def _get_fallback_exercise(student_id, difficulty, knowledge_point_ids=None, exercise_type=None):
    """
    从数据库获取备选题目（优化逻辑：按优先级过滤，分步骤放宽条件）
    
    优先级：
    1. 匹配练习类型（exercise_type）
    2. 匹配难度（difficulty）
    3. 匹配知识点（knowledge_point_ids 或学生薄弱点）
    4. 排除近期做过的题目
    """
    from django.utils import timezone
    import datetime

    print(f"\n====== 开始数据库 fallback 逻辑 ======")
    print(f"参数: student_id={student_id}, difficulty={difficulty}, knowledge_point_ids={knowledge_point_ids}, exercise_type={exercise_type}")

    # 1. 排除最近7天内做过的题目（避免重复练习，比固定10道更灵活）
    seven_days_ago = timezone.now() - datetime.timedelta(days=7)
    recent_attempts = ExerciseAttempt.objects.filter(
        fastapi_user_id=student_id,
        created_at__gte=seven_days_ago  # 仅排除最近7天的记录
    ).values_list('exercise_id', flat=True)
    print(f"排除近期做过的题目ID: {list(recent_attempts)[:5]}...（共{len(recent_attempts)}道）")


    # 2. 构建基础查询集（核心条件：难度、练习类型、有效状态）
    base_query = Exercise.objects.filter(
        difficulty__iexact=difficulty,  # 严格匹配难度
        exercise_type=exercise_type if exercise_type else Exercise.exercise_type,  # 匹配练习类型（如果指定）
        is_active=True
    ).exclude(id__in=recent_attempts)  # 排除近期做过的
    print(f"基础查询（难度+类型）结果数: {base_query.count()}")


    # 3. 按知识点过滤（分优先级匹配）
    def get_qualified_query(base):
        # 优先级1：使用前端指定的知识点（如果有）
        if knowledge_point_ids and len(knowledge_point_ids) > 0:
            query = base.filter(knowledge_points__id__in=knowledge_point_ids).distinct()
            if query.exists():
                print(f"匹配前端指定知识点，结果数: {query.count()}")
                return query

        # 优先级2：使用学生的薄弱知识点（如果有）
        try:
            profile = StudentProfile.objects.get(fastapi_user_id=student_id)
            weak_points = profile.weak_knowledge_points.all()
            if weak_points.exists():
                query = base.filter(knowledge_points__in=weak_points).distinct()
                if query.exists():
                    print(f"匹配学生薄弱知识点，结果数: {query.count()}")
                    return query
        except (StudentProfile.DoesNotExist, Exception) as e:
            print(f"无有效薄弱知识点（{str(e)}），跳过该条件")

        # 优先级3：练习类型为模拟测试时，使用核心知识点
        if exercise_type == 'simulation':
            core_points = KnowledgePoint.objects.filter(is_core=True)
            if core_points.exists():
                query = base.filter(knowledge_points__in=core_points).distinct()
                if query.exists():
                    print(f"模拟测试使用核心知识点，结果数: {query.count()}")
                    return query

        # 优先级4：不限制知识点（仅保留基础条件）
        print(f"未匹配特定知识点，使用基础查询结果")
        return base if base.exists() else None

    # 执行知识点过滤
    queryset = get_qualified_query(base_query)


    # 4. 分步骤放宽条件（确保有题可返回）
    if not queryset or not queryset.exists():
        print("====== 开始放宽条件 ======")
        
        # 放宽1：取消“排除近期做过的题目”限制
        queryset = get_qualified_query(base_query | Exercise.objects.filter(
            difficulty__iexact=difficulty,
            exercise_type=exercise_type if exercise_type else Exercise.exercise_type,
            is_active=True
        ))  # 重新加入近期做过的题目
        if queryset and queryset.exists():
            print(f"放宽条件（允许重复做过的题目），结果数: {queryset.count()}")
        else:
            # 放宽2：放宽难度范围（如medium可匹配easy/medium/hard）
            difficulty_groups = {
                'easy': ['easy', 'medium'],
                'medium': ['easy', 'medium', 'hard'],
                'hard': ['medium', 'hard']
            }
            allowed_difficulties = difficulty_groups.get(difficulty, [difficulty])
            queryset = Exercise.objects.filter(
                difficulty__in=allowed_difficulties,
                exercise_type=exercise_type if exercise_type else Exercise.exercise_type,
                is_active=True
            )
            queryset = get_qualified_query(queryset)
            if queryset and queryset.exists():
                print(f"放宽条件（允许难度范围{allowed_difficulties}），结果数: {queryset.count()}")


    # 5. 最终检查（确保有可用题目）
    if not queryset or not queryset.exists():
        raise ValueError(
            f"无符合条件的题目（难度: {difficulty}，类型: {exercise_type}，知识点: {knowledge_point_ids[:3]}...）"
        )


    # 6. 智能选择（优先选择学生未完全掌握的知识点题目）
    try:
        # 尝试按学生知识点掌握度排序（优先选择掌握度低的）
        profile = StudentProfile.objects.get(fastapi_user_id=student_id)
        mastery = profile.knowledge_mastery  # 格式: {知识点ID: 掌握度(0-1)}
        
        # 为查询集添加掌握度评分（越低越优先）
        def get_mastery_score(exercise):
            kp_ids = [kp.id for kp in exercise.knowledge_points.all()]
            scores = [mastery.get(str(kp_id), 1.0) for kp_id in kp_ids]
            return sum(scores) / len(scores) if scores else 1.0  # 平均掌握度
        
        # 按掌握度升序排序（优先选择掌握度低的），再随机取前10中的一道
        sorted_exercises = sorted(queryset, key=get_mastery_score)
        return random.choice(sorted_exercises[:10])  # 前10道中随机，平衡精准度和随机性
    except Exception as e:
        print(f"掌握度排序失败，随机选择: {e}")
        # 无掌握度数据时，直接随机选择
        return queryset.order_by('?').first()  # 比random.choice更高效