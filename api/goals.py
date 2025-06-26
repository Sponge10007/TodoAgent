from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from models.schemas import Goal, GoalCreate
from services.goal_service import GoalService

router = APIRouter(prefix="/goals", tags=["goals"])

@router.post("/", response_model=Goal)
def create_goal(goal: GoalCreate, db: Session = Depends(get_db)):
    """创建新目标"""
    goal_service = GoalService()
    # 这里简化处理，假设用户ID为1，实际应该有用户认证
    return goal_service.create_goal(db, goal, user_id=1)

@router.get("/", response_model=List[Goal])
def get_goals(db: Session = Depends(get_db)):
    """获取用户的所有目标"""
    goal_service = GoalService()
    # 这里简化处理，假设用户ID为1
    return goal_service.get_user_goals(db, user_id=1)

@router.get("/{goal_id}", response_model=Goal)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """获取特定目标"""
    goal_service = GoalService()
    goal = goal_service.get_goal(db, goal_id, user_id=1)
    if not goal:
        raise HTTPException(status_code=404, detail="目标未找到")
    return goal

@router.put("/{goal_id}/progress")
def update_goal_progress(goal_id: int, progress: float, db: Session = Depends(get_db)):
    """更新目标进度"""
    goal_service = GoalService()
    goal = goal_service.update_goal_progress(db, goal_id, progress)
    if not goal:
        raise HTTPException(status_code=404, detail="目标未找到")
    return {"message": "进度更新成功", "progress": progress}

@router.delete("/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """删除目标"""
    goal_service = GoalService()
    success = goal_service.delete_goal(db, goal_id, user_id=1)
    if not success:
        raise HTTPException(status_code=404, detail="目标未找到")
    return {"message": "目标删除成功"}

@router.get("/category/{category}", response_model=List[Goal])
def get_goals_by_category(category: str, db: Session = Depends(get_db)):
    """按类别获取目标"""
    goal_service = GoalService()
    return goal_service.get_goals_by_category(db, user_id=1, category=category)

@router.get("/active/", response_model=List[Goal])
def get_active_goals(db: Session = Depends(get_db)):
    """获取活跃目标"""
    goal_service = GoalService()
    return goal_service.get_active_goals(db, user_id=1) 