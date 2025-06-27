#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI主应用 - 生活管家AI Agent Web版
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
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

@app.put("/api/plans/{plan_id}", response_model=PlanResponse)
async def update_plan(plan_id: int, plan_update: PlanUpdate, db: Session = Depends(get_db)):
    """更新计划信息"""
    plan = update_plan_service(db, plan_id, plan_update)
    if plan is None:
        raise HTTPException(status_code=404, detail="计划不存在")
    return plan

@app.delete("/api/plans/{plan_id}")
async def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    """删除计划及其所有任务"""
    success = delete_plan_service(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="计划不存在")
    return SuccessResponse(message="计划删除成功")

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

@app.get("/api/tasks/{task_id}/with-subtasks", response_model=TaskWithSubtasks)
async def get_task_with_subtasks(task_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """获取任务及其子任务"""
    result = get_task_with_subtasks_service(db, task_id, user_id)
    if result is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskWithSubtasks(task=result["task"], subtasks=result["subtasks"])

@app.post("/api/tasks/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建新任务"""
    try:
        db_task = create_task_service(db, task)
        return db_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务"""
    success = delete_task_service(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return SuccessResponse(message="任务删除成功")

@app.post("/api/tasks/{task_id}/subtasks", response_model=TaskResponse)
async def create_subtask(
    task_id: int, 
    subtask: SubtaskCreate, 
    user_id: int = 1, 
    db: Session = Depends(get_db)
):
    """为任务创建子任务"""
    try:
        db_subtask = create_subtask_service(db, task_id, subtask, user_id)
        return db_subtask
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/subtasks/{subtask_id}/order")
async def update_subtask_order(
    subtask_id: int, 
    new_order: int, 
    user_id: int = 1, 
    db: Session = Depends(get_db)
):
    """更新子任务排序"""
    success = update_subtask_order_service(db, subtask_id, new_order, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="子任务不存在")
    return SuccessResponse(message="子任务排序更新成功")

@app.delete("/api/subtasks/{subtask_id}")
async def delete_subtask(subtask_id: int, user_id: int = 1, db: Session = Depends(get_db)):
    """删除子任务"""
    success = delete_subtask_service(db, subtask_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="子任务不存在")
    return SuccessResponse(message="子任务删除成功")

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

# AI估算服务
@app.post("/api/ai/estimate-days")
async def estimate_task_days(task_description: str = Query(...), db: Session = Depends(get_db)):
    """AI估算任务所需天数"""
    result = estimate_task_days_service(db, task_description)
    return result

@app.post("/api/ai/suggest-duration")
async def suggest_plan_duration(
    goal: str = Query(...), 
    user_preferred_days: int = Query(None), 
    db: Session = Depends(get_db)
):
    """AI建议计划持续时间"""
    suggestions = suggest_plan_duration_service(db, goal, user_preferred_days)
    return suggestions

# AI反问功能
@app.get("/api/ai/follow-up-questions")
async def get_follow_up_questions(
    goal_description: str = Query(...),
    plan_type: str = Query("daily"),
    db: Session = Depends(get_db)
):
    """获取AI生成的后续问题"""
    from life_manager_agent import AIQuestioningSystem
    
    questions = AIQuestioningSystem.generate_follow_up_questions(goal_description, plan_type)
    
    return {
        "goal": goal_description,
        "plan_type": plan_type,
        "questions": questions,
        "total_questions": len(questions)
    }

@app.post("/api/ai/enhanced-plan")
async def create_enhanced_plan(
    plan: PlanCreate,
    user_answers: Dict[str, str] = None,
    user_id: int = 1,
    db: Session = Depends(get_db)
):
    """基于用户回答创建增强版计划"""
    try:
        # 先创建基础计划
        db_plan = create_plan_service(db, plan, user_id)
        
        # 如果有用户回答，进行计划增强
        if user_answers:
            # 这里可以根据用户回答调整计划
            # 例如调整任务时间、难度等
            pass
        
        return db_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建增强计划失败: {str(e)}")

# 提醒系统
@app.post("/api/reminders/schedule")
async def schedule_plan_reminders(
    plan_id: int,
    user_email: str = Query(None),
    db: Session = Depends(get_db)
):
    """为计划安排提醒"""
    plan = get_plan_service(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    
    try:
        from life_manager_agent import ReminderSystem, LifeManagerAgentQwen
        
        # 获取计划任务
        tasks = get_tasks_service(db, plan.user_id, plan_id)
        
        # 模拟创建DailyPlan对象（简化处理）
        from life_manager_agent import DailyPlan, Task as AgentTask
        
        agent_tasks = []
        for task in tasks:
            # 为数据库Task对象生成时间（如果没有的话）
            task_time = getattr(task, 'time', None) or "09:00"  # 默认上午9点
            task_reason = getattr(task, 'reason', None) or f"计划任务：{task.description}"  # 默认原因
            
            agent_task = AgentTask(
                time=task_time,
                description=task.description,
                duration=task.duration,
                priority=task.priority,
                reason=task_reason
            )
            agent_tasks.append(agent_task)
        
        daily_plan = DailyPlan(
            plan_title=plan.title,
            goal=plan.goal,
            date=plan.start_date.strftime('%Y-%m-%d'),
            tasks=agent_tasks,
            total_tasks=len(agent_tasks),
            estimated_total_time=sum(t.duration for t in agent_tasks)
        )
        
        # 创建提醒计划
        reminder_schedule = ReminderSystem.create_reminder_schedule(daily_plan, user_email)
        
        return {
            "success": True,
            "message": "提醒计划创建成功",
            "data": reminder_schedule
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建提醒失败: {str(e)}")

@app.get("/api/reminders/notification-js")
async def get_notification_javascript(
    message: str = Query(...),
    task_id: int = Query(None)
):
    """获取浏览器通知的JavaScript代码"""
    from life_manager_agent import ReminderSystem
    
    reminder = {
        "message": message,
        "task_id": task_id,
        "type": "browser_notification"
    }
    
    js_code = ReminderSystem.create_browser_notification_js(reminder)
    
    return {
        "success": True,
        "javascript": js_code,
        "reminder": reminder
    }

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