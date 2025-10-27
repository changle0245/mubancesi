# 慕班策思 - 热点内容生成系统

基于AI的热点搜索和内容改写系统，支持多平台内容分发。

## 功能特性

### 🔥 核心功能
- **AI对话创建结构** - 与AI互动，定制你的内容结构模板
- **真实热点搜索** ⭐ - 从微博、知乎、抖音、百度、今日头条等平台实时抓取热点
  - ✅ 微博热搜榜
  - ✅ 知乎热榜 + 搜索
  - ✅ 百度实时热点
  - ✅ 抖音热搜
  - ✅ 今日头条热榜
  - 🔒 智能反爬虫处理
  - ⚡ 频率限制保护
  - 🔄 自动重试机制
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
1. 输入关键词（如：人工智能、健康饮食）
2. 点击"搜索热点" - 系统会从微博、知乎、百度、抖音、今日头条实时抓取相关热点
3. 选择内容结构模板
4. 选择目标平台
5. 点击"生成内容" - AI会基于热点素材生成适配各平台的内容

### 4. 查看历史记录

在"历史记录"页面查看最近30天的生成记录。

## 项目结构

```
mubancesi/
├── backend/                      # 后端代码
│   ├── models.py                # 数据库模型
│   ├── database.py              # 数据库连接
│   ├── auth.py                  # 用户认证
│   ├── schemas.py               # Pydantic模型
│   ├── routes/                  # API路由
│   │   ├── auth_routes.py      # 用户认证API
│   │   ├── chat_routes.py      # AI对话API
│   │   ├── content_routes.py   # 内容管理API
│   │   └── platform_routes.py  # 平台信息API
│   └── services/                # 业务服务
│       ├── ai_service.py       # AI服务（OpenAI + DeepSeek）
│       ├── hot_search_service.py  # 热点搜索（真实爬虫）⭐
│       └── crawler_utils.py    # 爬虫工具类 ⭐
├── frontend/                    # 前端代码
│   ├── index.html              # 主页面（响应式）
│   ├── css/style.css           # 样式文件
│   └── js/app.js               # 应用逻辑
├── config/                      # 配置文件
│   ├── prompts.yaml            # 提示词模板
│   ├── settings.yaml           # 系统设置
│   └── platforms.yaml          # 25个平台配置
├── docs/                        # 文档
│   └── CRAWLER_GUIDE.md        # 爬虫使用指南 ⭐
├── data/                        # 数据目录
├── main.py                      # 主程序入口
├── requirements.txt             # Python依赖
├── start.sh                     # 启动脚本
└── README.md                    # 说明文档
```

## 爬虫功能说明

### ⚠️ 重要提示

系统已实现**真实爬虫功能**，可以从以下平台实时抓取热点数据：

- ✅ **微博热搜** - 实时热搜榜
- ✅ **知乎热榜** - 热榜 + 搜索
- ✅ **百度热搜** - 实时热点榜
- ✅ **抖音热点** - 热搜榜
- ✅ **今日头条** - 热点榜

### 特性

- **智能反爬虫**：User-Agent轮换、请求重试、频率限制
- **关键词匹配**：自动匹配包含关键词的热点
- **热度排序**：按热度值排序结果
- **错误处理**：优雅处理网络错误，不影响其他平台

### 详细文档

查看完整的爬虫使用指南：[docs/CRAWLER_GUIDE.md](docs/CRAWLER_GUIDE.md)

### 注意事项

1. **合规使用**：仅用于个人内容创作参考，遵守平台robots.txt
2. **频率限制**：系统限制60秒内最多20次请求
3. **定期维护**：平台API可能变化，需要定期更新爬虫代码

## 许可证

MIT License

---

**慕班策思 - 让内容创作更简单** 🚀
