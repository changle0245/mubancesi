"""
慕班策思 - 热点内容生成系统
主程序入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from backend.database import init_db
from backend.routes import auth_routes, chat_routes, content_routes, platform_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    print("✅ 数据库初始化完成")
    yield
    # 关闭时的清理工作
    print("👋 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="慕班策思 - 热点内容生成系统",
    description="基于AI的热点搜索和内容改写系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置（允许前端跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)
app.include_router(content_routes.router)
app.include_router(platform_routes.router)

# 挂载静态文件（前端页面）
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """首页"""
    # 如果存在前端页面，返回前端页面
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()

    # 否则返回API信息
    return """
    <html>
        <head>
            <title>慕班策思 - 热点内容生成系统</title>
            <meta charset="utf-8">
            <style>
                body {
                    font-family: system-ui, -apple-system, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                }
                h1 { margin-top: 0; }
                a {
                    color: #fff;
                    text-decoration: none;
                    padding: 10px 20px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 5px;
                    display: inline-block;
                    margin: 10px 5px;
                }
                a:hover { background: rgba(255,255,255,0.3); }
                .features {
                    margin: 30px 0;
                    line-height: 2;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 慕班策思 - 热点内容生成系统</h1>
                <p>基于AI的热点搜索和内容改写系统</p>

                <div class="features">
                    <h3>✨ 核心功能</h3>
                    <ul>
                        <li>🔥 热点搜索 - 从多个平台搜索热点内容</li>
                        <li>💬 AI对话 - 与AI互动创建内容结构</li>
                        <li>📝 内容生成 - 基于热点素材生成优质内容</li>
                        <li>🌐 多平台适配 - 支持25个国内外主流平台</li>
                        <li>📚 历史记录 - 保留30天的生成历史</li>
                    </ul>
                </div>

                <div>
                    <h3>📖 快速开始</h3>
                    <a href="/docs" target="_blank">API文档</a>
                    <a href="/redoc" target="_blank">API文档(ReDoc)</a>
                </div>

                <div style="margin-top: 30px; font-size: 14px; opacity: 0.8;">
                    <p>API状态: ✅ 运行中</p>
                    <p>版本: v1.0.0</p>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "message": "服务运行正常",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式下自动重载
    )
