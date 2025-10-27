# 慕班策思 - 热点内容生成系统

基于AI的热点搜索和内容改写系统，支持多平台内容分发。

## 功能特性

### 🔥 核心功能
- **AI对话创建结构** - 与AI互动，定制你的内容结构模板
- **热点搜索** - 从微博、知乎、抖音、百度等平台搜索热点
- **智能内容生成** - 基于热点素材和用户风格生成优质内容
- **多平台适配** - 支持25个国内外主流自媒体平台
- **历史记录** - 保留30天的生成历史

### 🌐 支持的平台

#### 国内平台
- 微信公众号、微信朋友圈
- 抖音、快手、B站、西瓜视频
- 小红书、微博、知乎
- 今日头条、百家号、趣头条

#### 国外平台
- Twitter/X、Facebook、Instagram
- TikTok、YouTube
- LinkedIn、Pinterest、Reddit
- Medium、Quora
- Telegram、Discord、Threads

### 🤖 AI模型支持
- **OpenAI GPT-4** - 强大的内容生成能力
- **DeepSeek V3** - 国产高性价比模型

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite
- **前端**: HTML + CSS + JavaScript (原生)
- **AI**: OpenAI SDK + DeepSeek API
- **数据库**: SQLite (可切换到PostgreSQL/MySQL)

## 快速开始

### 1. 环境要求

- Python 3.9+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

API密钥已配置在 `.env` 文件中。

### 4. 启动服务

```bash
python main.py
```

或使用启动脚本：

```bash
./start.sh
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问应用

打开浏览器访问：
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **API文档(ReDoc)**: http://localhost:8000/redoc

## 使用流程

### 1. 注册/登录

首次使用需要注册账号。

### 2. 创建内容结构

在"AI对话"页面与AI互动，定制你的内容结构。

### 3. 搜索热点生成内容

在"生成内容"页面：
1. 输入关键词
2. 点击"搜索热点"
3. 选择内容结构模板
4. 选择目标平台
5. 点击"生成内容"

### 4. 查看历史记录

在"历史记录"页面查看最近30天的生成记录。

## 项目结构

```
mubancesi/
├── backend/                # 后端代码
│   ├── models.py          # 数据库模型
│   ├── database.py        # 数据库连接
│   ├── auth.py            # 用户认证
│   ├── schemas.py         # Pydantic模型
│   ├── routes/            # API路由
│   └── services/          # 业务服务
├── frontend/              # 前端代码
│   ├── index.html        # 主页面
│   ├── css/style.css     # 样式文件
│   └── js/app.js         # 应用逻辑
├── config/               # 配置文件
│   ├── prompts.yaml     # 提示词模板
│   ├── settings.yaml    # 系统设置
│   └── platforms.yaml   # 25个平台配置
├── data/                # 数据目录
├── main.py             # 主程序入口
├── requirements.txt    # Python依赖
├── start.sh           # 启动脚本
└── README.md          # 说明文档
```

## 许可证

MIT License

---

**慕班策思 - 让内容创作更简单** 🚀
