#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI主应用 - 生活管家AI Agent Web版
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from database import get_db, init_db
from api_models import *
from services import *

# 初始化FastAPI应用
app = FastAPI(
    title="生活管家AI Agent",
    description="智能计划制定和TodoList管理平台",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请修改为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()

# 根路径 - 返回前端页面
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse('static/index.html')

# API路由

# 用户管理
@app.post("/api/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    try:
        db_user = create_user_service(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取用户信息"""
    db_user = get_user_service(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

# 计划管理
@app.post("/api/plans/", response_model=PlanResponse)
async def create_plan(plan: PlanCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """创建新计划（每日或7天）"""
    try:
        db_plan = create_plan_service(db, plan, user_id)
        return db_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建计划失败: {str(e)}")

@app.get("/api/plans/", response_model=List[PlanResponse])
async def get_plans(user_id: int = 1, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """获取用户的计划列表"""
    plans = get_user_plans_service(db, user_id, skip, limit)
    return plans

@app.get("/api/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """获取特定计划详情"""
    plan = get_plan_service(db, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="计划不存在")
    return plan

@app.put("/api/plans/{plan_id}/status")
async def update_plan_status(plan_id: int, status: str, db: Session = Depends(get_db)):
    """更新计划状态"""
    success = update_plan_status_service(db, plan_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="计划不存在")
    return SuccessResponse(message="计划状态更新成功")

# 任务管理
@app.get("/api/tasks/", response_model=List[TaskResponse])
async def get_tasks(
    user_id: int = 1, 
    plan_id: int = None, 
    status: str = None,
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    tasks = get_tasks_service(db, user_id, plan_id, status, skip, limit)
    return tasks

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """更新任务状态"""
    task = update_task_service(db, task_id, task_update)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task

# TodoList管理
@app.post("/api/todos/", response_model=TodoItemResponse)
async def create_todo(todo: TodoItemCreate, user_id: int = 1, db: Session = Depends(get_db)):
    """创建新的Todo项目"""
    db_todo = create_todo_service(db, todo, user_id)
    return db_todo

@app.get("/api/todos/", response_model=List[TodoItemResponse])
async def get_todos(
    user_id: int = 1,
    is_completed: bool = None,
    category: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取Todo列表"""
    todos = get_todos_service(db, user_id, is_completed, category, skip, limit)
    return todos

@app.put("/api/todos/{todo_id}", response_model=TodoItemResponse)
async def update_todo(todo_id: int, todo_update: TodoItemUpdate, db: Session = Depends(get_db)):
    """更新Todo项目"""
    todo = update_todo_service(db, todo_id, todo_update)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo项目不存在")
    return todo

@app.delete("/api/todos/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """删除Todo项目"""
    success = delete_todo_service(db, todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo项目不存在")
    return SuccessResponse(message="Todo项目删除成功")

# 分析统计
@app.get("/api/dashboard/{user_id}", response_model=DashboardData)
async def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    """获取仪表板数据"""
    dashboard_data = get_dashboard_service(db, user_id)
    return dashboard_data

@app.get("/api/analytics/{user_id}", response_model=AnalyticsResponse)
async def get_analytics(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    """获取分析统计数据"""
    analytics_data = get_analytics_service(db, user_id, days)
    return analytics_data

# 计划转TodoList
@app.post("/api/plans/{plan_id}/to-todos")
async def plan_to_todos(plan_id: int, db: Session = Depends(get_db)):
    """将计划任务转换为TodoList项目"""
    success = plan_to_todos_service(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="计划不存在")
    return SuccessResponse(message="计划任务已转换为TodoList项目")

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "生活管家AI Agent运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 