from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from models.models import Goal, User
from models.schemas import GoalCreate
from .ai_planner import AIPlanner

class GoalService:
    def __init__(self):
        self.ai_planner = AIPlanner()
    
    def create_goal(self, db: Session, goal_data: GoalCreate, user_id: int) -> Goal:
        """创建新目标并自动生成任务计划"""
        # 创建目标
        goal = Goal(
            title=goal_data.title,
            description=goal_data.description,
            category=goal_data.category,
            start_date=goal_data.start_date,
            end_date=goal_data.end_date,
            user_id=user_id
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        
        # 使用AI规划器生成任务
        tasks = self.ai_planner.plan_goal(
            goal_data.title,
            goal_data.description,
            goal_data.category,
            goal_data.start_date,
            goal_data.end_date
        )
        
        # 创建任务
        from .task_service import TaskService
        task_service = TaskService()
        for task_data in tasks:
            task_service.create_task(db, task_data, goal.id)
        
        return goal
    
    def get_user_goals(self, db: Session, user_id: int) -> List[Goal]:
        """获取用户的所有目标"""
        return db.query(Goal).filter(Goal.user_id == user_id).all()
    
    def get_goal(self, db: Session, goal_id: int, user_id: int) -> Optional[Goal]:
        """获取特定目标"""
        return db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
    
    def update_goal_progress(self, db: Session, goal_id: int, progress: float) -> Optional[Goal]:
        """更新目标进度"""
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if goal:
            goal.progress = progress
            if progress >= 100:
                goal.status = "completed"
            db.commit()
            db.refresh(goal)
        return goal
    
    def delete_goal(self, db: Session, goal_id: int, user_id: int) -> bool:
        """删除目标"""
        goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == user_id).first()
        if goal:
            db.delete(goal)
            db.commit()
            return True
        return False
    
    def calculate_goal_progress(self, db: Session, goal_id: int) -> float:
        """计算目标完成进度"""
        from .task_service import TaskService
        task_service = TaskService()
        
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            return 0.0
        
        tasks = task_service.get_goal_tasks(db, goal_id)
        if not tasks:
            return 0.0
        
        completed_tasks = sum(1 for task in tasks if task.status == "completed")
        total_tasks = len(tasks)
        
        progress = (completed_tasks / total_tasks) * 100
        return min(progress, 100.0)
    
    def get_goals_by_category(self, db: Session, user_id: int, category: str) -> List[Goal]:
        """按类别获取目标"""
        return db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.category == category
        ).all()
    
    def get_active_goals(self, db: Session, user_id: int) -> List[Goal]:
        """获取活跃目标"""
        return db.query(Goal).filter(
            Goal.user_id == user_id,
            Goal.status == "active"
        ).all() 