# CampusAgent

#### 介绍
校园实训智能体

#### 软件架构
软件架构说明


#### 安装教程

1. 配置环境

   ```bash
   # 安装依赖（仅项目用到的）
   pip install requirements.txt
   # 安装依赖（从虚拟环境导出的所有依赖）
   pip install requirements-all.txt
   ```

2. 数据库配置

   - 当前采用`SQLite`数据库

   - 配置文件位于`backend/app/core/config.py`，也可通过`backend/.env`动态加载配置

   - 初始化数据库

     ```bash
     python -c "from config.database import init_db; init_db()"
     ```

   - 数据库迁移：项目当前使用 Alembic 进行数据库迁移管理

     ```bash
     # 初始化 Alembic：
     alembic init migrations
     # 生成迁移脚本：
     alembic revision --autogenerate -m "initial"
     # 应用迁移：
     alembic upgrade head
     ```

     

3.  xxxx

#### 使用说明

1.  启动后端服务：
```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
2.  启动前端：
```bash
cd frontend
npm run dev
```

3. 教师端——备课与设计功能使用django实现
   
3.1 启动前端服务：
```bash
cd frontend
npm run dev
```
3.2 启动后端服务：
```bash
cd backend
python manage.py runserver
```
需要DEEPSEEK_API_KEYS
环境变量设置一下：
> 在PowerShell中设置环境变量：
$env:DEEPSEEK_API_KEY="你的DeepSeek Key"

> 在cmd中设置环境变量：
set DEEPSEEK_API_KEY=你的DeepSeek Key

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
