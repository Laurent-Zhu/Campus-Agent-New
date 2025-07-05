import asyncio
import os
from dotenv import load_dotenv
from utils.model_client import ChatGLMClient

async def test_api():
    """测试智谱API连接"""
    client = ChatGLMClient()
    try:
        print("正在测试API连接...")
        response = await client.generate_text("你是谁？")
        print("\n✅ API连接成功！")
        print("\n模型响应:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    except Exception as e:
        print(f"\n❌ API连接失败: {str(e)}")
    finally:
        await client.close()

if __name__ == "__main__":
    # 加载环境变量
    load_dotenv()
    
    # 运行测试
    asyncio.run(test_api())