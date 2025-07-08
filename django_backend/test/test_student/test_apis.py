# tests/test_apis.py
import json
from django.urls import reverse

@pytest.mark.django_db
def test_generate_exercise_api(client):
    # 创建测试用户和数据
    profile = StudentProfileFactory()
    ExerciseFactory.create_batch(3, difficulty="medium")
    
    # 调用API
    url = reverse("generate-exercise")
    response = client.post(
        url,
        data=json.dumps({"student_id": profile.user.id}),
        content_type="application/json"
    )
    
    # 验证响应
    assert response.status_code == 200
    assert "question" in response.json()
    assert "options" in response.json()

@pytest.mark.django_db
def test_evaluate_api(client):
    exercise = ExerciseFactory(
        answer={"reference_answer": "print('Hello')"}
    )
    student = UserFactory()
    
    response = client.post(
        reverse("evaluate-answer"),
        data=json.dumps({
            "exercise_id": exercise.id,
            "student_id": student.id,
            "student_answer": "print('Hi')"  # 错误答案
        }),
        content_type="application/json"
    )
    
    data = response.json()
    assert response.status_code == 200
    assert data["is_correct"] is False
    assert "Hi" in data["feedback"]