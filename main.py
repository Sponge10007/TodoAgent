from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# 导入模型和数据库
from models.database import engine, Base
from models import models

# 导入API路由
from api import goals_router, tasks_router, users_router, dashboard_router

# 导入服务
from services.notification_service import NotificationService

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="生活管家AI Agent",
    description="一个智能的生活管理助手，帮助用户管理目标、拆解任务并定期推送提醒",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

# 注册API路由
app.include_router(goals_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

# 启动通知服务
notification_service = NotificationService()
notification_service.start_scheduler()

@app.get("/")
async def home(request: Request):
    """主页"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/goals")
async def goals_page(request: Request):
    """目标管理页面"""
    return templates.TemplateResponse("goals.html", {"request": request})

@app.get("/tasks")
async def tasks_page(request: Request):
    """任务管理页面"""
    return templates.TemplateResponse("tasks.html", {"request": request})

@app.get("/calendar")
async def calendar_page(request: Request):
    """日历视图页面"""
    return templates.TemplateResponse("calendar.html", {"request": request})

@app.get("/analytics")
async def analytics_page(request: Request):
    """数据分析页面"""
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/create-goal")
async def create_goal_page(request: Request):
    """创建目标页面"""
    return templates.TemplateResponse("create_goal.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("🚀 生活管家AI Agent 启动中...")
    print("📅 通知服务已启动")
    print("🌐 访问地址: http://localhost:8000")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    print("🛑 正在关闭生活管家AI Agent...")
    notification_service.stop_scheduler()
    print("✅ 通知服务已停止")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 