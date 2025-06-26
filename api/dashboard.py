from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any
from models.database import get_db
from services.goal_service import GoalService
from services.task_service import TaskService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """获取仪表板摘要信息"""
    goal_service = GoalService()
    task_service = TaskService()
    
    # 获取用户统计信息
    goals = goal_service.get_user_goals(db, user_id=1)
    active_goals = goal_service.get_active_goals(db, user_id=1)
    
    # 获取今日任务
    today = datetime.utcnow()
    daily_tasks = task_service.get_daily_tasks(db, user_id=1, today)
    
    # 获取逾期任务
    overdue_tasks = task_service.get_overdue_tasks(db, user_id=1)
    
    # 获取即将到来的任务
    upcoming_tasks = task_service.get_upcoming_tasks(db, user_id=1, days=7)
    
    # 计算完成率
    total_tasks = len(daily_tasks)
    completed_tasks = len([task for task in daily_tasks if task.status == "completed"])
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return {
        "total_goals": len(goals),
        "active_goals": len(active_goals),
        "today_tasks": len(daily_tasks),
        "completed_today": completed_tasks,
        "completion_rate": round(completion_rate, 1),
        "overdue_tasks": len(overdue_tasks),
        "upcoming_tasks": len(upcoming_tasks)
    }

@router.get("/goals/progress")
def get_goals_progress(db: Session = Depends(get_db)):
    """获取目标进度信息"""
    goal_service = GoalService()
    active_goals = goal_service.get_active_goals(db, user_id=1)
    
    goals_progress = []
    for goal in active_goals:
        progress = goal_service.calculate_goal_progress(db, goal.id)
        goals_progress.append({
            "id": goal.id,
            "title": goal.title,
            "category": goal.category,
            "progress": progress,
            "start_date": goal.start_date,
            "end_date": goal.end_date
        })
    
    return goals_progress

@router.get("/tasks/calendar")
def get_tasks_calendar(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """获取日历视图的任务"""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "日期格式错误，请使用YYYY-MM-DD格式"}
    
    task_service = TaskService()
    calendar_tasks = []
    
    current_date = start
    while current_date <= end:
        daily_tasks = task_service.get_daily_tasks(db, user_id=1, current_date)
        if daily_tasks:
            calendar_tasks.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "status": task.status,
                        "priority": task.priority
                    }
                    for task in daily_tasks
                ]
            })
        current_date += timedelta(days=1)
    
    return calendar_tasks

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    """获取分析数据"""
    goal_service = GoalService()
    task_service = TaskService()
    
    # 获取过去30天的数据
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # 按类别统计目标
    categories = ["健身", "学习", "工作", "其他"]
    category_stats = {}
    
    for category in categories:
        goals = goal_service.get_goals_by_category(db, user_id=1, category=category)
        category_stats[category] = len(goals)
    
    # 任务完成趋势（简化处理）
    completion_trend = {
        "labels": [(end_date - timedelta(days=i)).strftime("%m-%d") for i in range(7, 0, -1)],
        "data": [85, 90, 75, 88, 92, 87, 95]  # 示例数据
    }
    
    return {
        "category_stats": category_stats,
        "completion_trend": completion_trend
    } 