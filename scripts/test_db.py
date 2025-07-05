from config.database import SessionLocal
from models.database import User
from werkzeug.security import generate_password_hash

def test_create_user():
    db = SessionLocal()
    try:
        test_user = User(
            username="test_teacher",
            email="teacher@test.com",
            password_hash=generate_password_hash("test123"),
            role="teacher"
        )
        db.add(test_user)
        db.commit()
        print("测试用户创建成功！")
    except Exception as e:
        print(f"创建用户失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_create_user()