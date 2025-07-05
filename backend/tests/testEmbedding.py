from zhipuai import ZhipuAI
import os 
from dotenv import load_dotenv, find_dotenv
from zhipuai import ZhipuAI


# 读取本地/项目的环境变量。

# find_dotenv() 寻找并定位 .env 文件的路径
# load_dotenv() 读取该 .env 文件，并将其中的环境变量加载到当前的运行环境中  
# 如果你设置的是全局的环境变量，这行代码则没有任何作用。
_ = load_dotenv(find_dotenv())
def zhipu_embedding(text: str):

    api_key = os.environ["ZHIPU_API_KEY"]
    client = ZhipuAI(api_key=api_key)
    response = client.embeddings.create(
        model="embedding-3",
        input=text,
    )
    return response

text = '要生成 embedding 的输入文本，字符串形式。'
response = zhipu_embedding(text=text)
print(response)
