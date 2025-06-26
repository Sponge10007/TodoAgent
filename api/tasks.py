from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from models.database import get_db
from models.schemas import Task, TaskCreate, TaskProgress, TaskProgressCreate
from services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/", response_model=List[Task])
def get_tasks(
    goal_id: Optional[int] = Query(None, description="按目标ID筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    priority: Optional[str] = Query(None, description="按优先级筛选"),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    task_service = TaskService()
    
    if goal_id:
        return task_service.get_goal_tasks(db, goal_id)
    elif status:
        # 这里简化处理，实际应该实现按状态筛选
        return []
    elif priority:
        return task_service.get_tasks_by_priority(db, user_id=1, priority=priority)
    else:
        # 获取所有任务（这里简化处理）
        return []

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取特定任务"""
    task_service = TaskService()
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return task

@router.put("/{task_id}/status")
def update_task_status(task_id: int, status: str, db: Session = Depends(get_db)):
    """更新任务状态"""
    task_service = TaskService()
    task = task_service.update_task_status(db, task_id, status)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return {"message": "状态更新成功", "status": status}

@router.get("/daily/{date}", response_model=List[Task])
def get_daily_tasks(date: str, db: Session = Depends(get_db)):
    """获取指定日期的任务"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")
    
    task_service = TaskService()
    return task_service.get_daily_tasks(db, user_id=1, target_date=target_date)

@router.get("/overdue/", response_model=List[Task])
def get_overdue_tasks(db: Session = Depends(get_db)):
    """获取逾期任务"""
    task_service = TaskService()
    return task_service.get_overdue_tasks(db, user_id=1)

@router.get("/upcoming/", response_model=List[Task])
def get_upcoming_tasks(days: int = Query(7, description="未来天数"), db: Session = Depends(get_db)):
    """获取即将到来的任务"""
    task_service = TaskService()
    return task_service.get_upcoming_tasks(db, user_id=1, days=days)

@router.post("/{task_id}/progress", response_model=TaskProgress)
def add_task_progress(
    task_id: int, 
    progress: TaskProgressCreate, 
    db: Session = Depends(get_db)
):
    """添加任务进度记录"""
    task_service = TaskService()
    return task_service.add_task_progress(
        db, 
        task_id, 
        progress.completed, 
        progress.notes
    )

@router.get("/{task_id}/progress", response_model=List[TaskProgress])
def get_task_progress(task_id: int, db: Session = Depends(get_db)):
    """获取任务进度记录"""
    task_service = TaskService()
    return task_service.get_task_progress(db, task_id)

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务"""
    task_service = TaskService()
    success = task_service.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务未找到")
    return {"message": "任务删除成功"} 