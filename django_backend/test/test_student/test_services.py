# tests/test_services.py
import pytest
from exercises.services import exercise_generator
from tests.factories import ExerciseFactory, StudentProfileFactory

@pytest.mark.django_db
def test_generate_personalized_exercise():
    # 准备测试数据
    profile = StudentProfileFactory(average_score=75)
    exercise1 = ExerciseFactory(difficulty="medium")
    exercise2 = ExerciseFactory(difficulty="hard")
    
    # 调用被测函数
    result = exercise_generator.generate_personalized_exercise(
        student_id=profile.user.id,
        difficulty="medium"
    )
    
    # 验证结果
    assert result.difficulty == "medium"
    assert result.id in [exercise1.id, exercise2.id]


@pytest.mark.django_db
def test_evaluate_answer():
    from exercises.services import evaluator
    exercise = ExerciseFactory(
        answer={"reference_answer": "def add(a, b): return a + b"}
    )
    student = UserFactory()
    
    # 测试正确答案
    correct_res = evaluator.evaluate_answer(
        exercise_id=exercise.id,
        student_id=student.id,
        student_answer="def add(a, b): return a + b"
    )
    assert correct_res["is_correct"] is True
    
    # 测试错误答案
    wrong_res = evaluator.evaluate_answer(
        exercise_id=exercise.id,
        student_id=student.id,
        student_answer="def add(a, b): return a * b"  # 错误逻辑
    )
    assert wrong_res["is_correct"] is False
    assert "return a * b" in wrong_res["feedback"]
