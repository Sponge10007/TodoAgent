from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from models.models import Task, TaskProgress
from models.schemas import TaskCreate

class TaskService:
    def create_task(self, db: Session, task_data: Dict[str, Any], goal_id: int) -> Task:
        """创建新任务"""
        task = Task(
            title=task_data["title"],
            description=task_data["description"],
            due_date=task_data["due_date"],
            priority=task_data["priority"],
            estimated_duration=task_data["estimated_duration"],
            goal_id=goal_id
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    
    def get_goal_tasks(self, db: Session, goal_id: int) -> List[Task]:
        """获取目标的所有任务"""
        return db.query(Task).filter(Task.goal_id == goal_id).all()
    
    def get_task(self, db: Session, task_id: int) -> Optional[Task]:
        """获取特定任务"""
        return db.query(Task).filter(Task.id == task_id).first()
    
    def update_task_status(self, db: Session, task_id: int, status: str) -> Optional[Task]:
        """更新任务状态"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            task.status = status
            if status == "completed":
                # 创建完成记录
                progress = TaskProgress(
                    task_id=task_id,
                    completed=True,
                    completion_date=datetime.utcnow()
                )
                db.add(progress)
            db.commit()
            db.refresh(task)
        return task
    
    def get_daily_tasks(self, db: Session, user_id: int, target_date: datetime) -> List[Task]:
        """获取指定日期的任务"""
        from models.models import Goal
        
        # 获取用户的所有目标
        goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        goal_ids = [goal.id for goal in goals]
        
        # 获取指定日期的任务
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        tasks = db.query(Task).filter(
            Task.goal_id.in_(goal_ids),
            Task.due_date >= start_of_day,
            Task.due_date < end_of_day
        ).all()
        
        return tasks
    
    def get_overdue_tasks(self, db: Session, user_id: int) -> List[Task]:
        """获取逾期任务"""
        from models.models import Goal
        
        goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        goal_ids = [goal.id for goal in goals]
        
        return db.query(Task).filter(
            Task.goal_id.in_(goal_ids),
            Task.due_date < datetime.utcnow(),
            Task.status.in_(["pending", "in_progress"])
        ).all()
    
    def get_upcoming_tasks(self, db: Session, user_id: int, days: int = 7) -> List[Task]:
        """获取即将到来的任务"""
        from models.models import Goal
        
        goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        goal_ids = [goal.id for goal in goals]
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days)
        
        return db.query(Task).filter(
            Task.goal_id.in_(goal_ids),
            Task.due_date >= start_date,
            Task.due_date <= end_date,
            Task.status.in_(["pending", "in_progress"])
        ).all()
    
    def add_task_progress(self, db: Session, task_id: int, completed: bool, notes: str = None) -> TaskProgress:
        """添加任务进度记录"""
        progress = TaskProgress(
            task_id=task_id,
            completed=completed,
            notes=notes,
            completion_date=datetime.utcnow() if completed else None
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress
    
    def get_task_progress(self, db: Session, task_id: int) -> List[TaskProgress]:
        """获取任务进度记录"""
        return db.query(TaskProgress).filter(TaskProgress.task_id == task_id).all()
    
    def delete_task(self, db: Session, task_id: int) -> bool:
        """删除任务"""
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            db.delete(task)
            db.commit()
            return True
        return False
    
    def get_tasks_by_priority(self, db: Session, user_id: int, priority: str) -> List[Task]:
        """按优先级获取任务"""
        from models.models import Goal
        
        goals = db.query(Goal).filter(Goal.user_id == user_id).all()
        goal_ids = [goal.id for goal in goals]
        
        return db.query(Task).filter(
            Task.goal_id.in_(goal_ids),
            Task.priority == priority
        ).all() 