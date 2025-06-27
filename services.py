#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务逻辑服务层
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import hashlib
import json

from database import User, Plan, Task, TodoItem, Memory, Analytics
from api_models import UserCreate, PlanCreate, TodoItemCreate, TodoItemUpdate, TaskUpdate, SubtaskCreate, PlanUpdate, TaskCreate
from life_manager_agent import LifeManagerAgentQwen

# 初始化AI Agent
ai_agent = LifeManagerAgentQwen()

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

# 用户服务
def create_user_service(db: Session, user: UserCreate) -> User:
    """创建用户"""
    # 检查用户名和邮箱是否已存在
    if db.query(User).filter(User.username == user.username).first():
        raise ValueError("用户名已存在")
    if db.query(User).filter(User.email == user.email).first():
        raise ValueError("邮箱已存在")
    
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_service(db: Session, user_id: int) -> User:
    """获取用户"""
    return db.query(User).filter(User.id == user_id).first()

# 计划服务
def create_plan_service(db: Session, plan: PlanCreate, user_id: int) -> Plan:
    """创建计划（使用AI Agent）"""
    # 使用AI Agent生成计划
    if plan.plan_type == "daily":
        ai_plan = ai_agent.create_daily_plan(plan.goal, plan.time_preference or "")
        if not ai_plan:
            raise Exception("AI生成每日计划失败")
        
        # 创建数据库记录
        db_plan = Plan(
            user_id=user_id,
            title=ai_plan.plan_title,
            goal=ai_plan.goal,
            plan_type="daily",
            duration_days=1,
            start_date=datetime.strptime(ai_plan.date, "%Y-%m-%d"),
            estimated_total_time=ai_plan.estimated_total_time,
            status="active"
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        
        # 创建任务和子任务
        for task_data in ai_plan.tasks:
            db_task = Task(
                plan_id=db_plan.id,
                title=task_data.description,
                description=task_data.description,
                reason=task_data.reason,
                start_time=task_data.time,
                duration=task_data.duration,
                priority=task_data.priority,
                scheduled_date=db_plan.start_date,
                ai_estimated_days=task_data.ai_estimated_days
            )
            db.add(db_task)
            db.flush()  # 获取task id
            
            # 创建子任务
            for idx, subtask_data in enumerate(task_data.subtasks):
                db_subtask = Task(
                    plan_id=db_plan.id,
                    parent_task_id=db_task.id,
                    title=subtask_data.description,
                    description=subtask_data.description,
                    reason=subtask_data.reason,
                    start_time=subtask_data.time,
                    duration=subtask_data.duration,
                    priority=subtask_data.priority,
                    scheduled_date=db_plan.start_date,
                    is_subtask=True,
                    order_index=idx,
                    ai_estimated_days=subtask_data.ai_estimated_days
                )
                db.add(db_subtask)
        
    elif plan.plan_type == "weekly":
        ai_weekly_plan = ai_agent.create_weekly_plan(plan.goal, plan.time_preference or "")
        if not ai_weekly_plan:
            raise Exception("AI生成7天计划失败")
        
        # 创建数据库记录
        db_plan = Plan(
            user_id=user_id,
            title=ai_weekly_plan.plan_title,
            goal=ai_weekly_plan.main_goal,
            plan_type="weekly",
            duration_days=7,
            start_date=datetime.strptime(ai_weekly_plan.start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(ai_weekly_plan.end_date, "%Y-%m-%d"),
            estimated_total_time=sum(daily.estimated_total_time for daily in ai_weekly_plan.daily_plans),
            status="active"
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        
        # 创建每日任务
        for daily_plan in ai_weekly_plan.daily_plans:
            for task_data in daily_plan.tasks:
                db_task = Task(
                    plan_id=db_plan.id,
                    title=task_data.description,
                    description=task_data.description,
                    reason=task_data.reason,
                    start_time=task_data.time,
                    duration=task_data.duration,
                    priority=task_data.priority,
                    scheduled_date=datetime.strptime(daily_plan.date, "%Y-%m-%d"),
                    ai_estimated_days=task_data.ai_estimated_days
                )
                db.add(db_task)
                db.flush()  # 获取task id
                
                # 创建子任务
                for idx, subtask_data in enumerate(task_data.subtasks):
                    db_subtask = Task(
                        plan_id=db_plan.id,
                        parent_task_id=db_task.id,
                        title=subtask_data.description,
                        description=subtask_data.description,
                        reason=subtask_data.reason,
                        start_time=subtask_data.time,
                        duration=subtask_data.duration,
                        priority=subtask_data.priority,
                        scheduled_date=datetime.strptime(daily_plan.date, "%Y-%m-%d"),
                        is_subtask=True,
                        order_index=idx,
                        ai_estimated_days=subtask_data.ai_estimated_days
                    )
                    db.add(db_subtask)
    
    elif plan.plan_type == "custom":
        # 自定义天数计划
        duration_days = plan.duration_days or 7
        ai_custom_plan = ai_agent.create_custom_plan(
            plan.goal, 
            duration_days, 
            plan.user_preferred_days,
            plan.time_preference or ""
        )
        if not ai_custom_plan:
            raise Exception(f"AI生成{duration_days}天计划失败")
        
        # 创建数据库记录
        db_plan = Plan(
            user_id=user_id,
            title=ai_custom_plan.plan_title,
            goal=ai_custom_plan.main_goal,
            plan_type="custom",
            duration_days=ai_custom_plan.duration_days,
            start_date=datetime.strptime(ai_custom_plan.start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(ai_custom_plan.end_date, "%Y-%m-%d"),
            estimated_total_time=ai_custom_plan.estimated_total_time,
            ai_suggested_days=ai_custom_plan.ai_suggested_days,
            user_preferred_days=ai_custom_plan.user_preferred_days,
            status="active"
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        
        # 创建每日任务
        for daily_plan in ai_custom_plan.daily_plans:
            for task_data in daily_plan.tasks:
                db_task = Task(
                    plan_id=db_plan.id,
                    title=task_data.description,
                    description=task_data.description,
                    reason=task_data.reason,
                    start_time=task_data.time,
                    duration=task_data.duration,
                    priority=task_data.priority,
                    scheduled_date=datetime.strptime(daily_plan.date, "%Y-%m-%d"),
                    ai_estimated_days=task_data.ai_estimated_days
                )
                db.add(db_task)
                db.flush()  # 获取task id
                
                # 创建子任务
                for idx, subtask_data in enumerate(task_data.subtasks):
                    db_subtask = Task(
                        plan_id=db_plan.id,
                        parent_task_id=db_task.id,
                        title=subtask_data.description,
                        description=subtask_data.description,
                        reason=subtask_data.reason,
                        start_time=subtask_data.time,
                        duration=subtask_data.duration,
                        priority=subtask_data.priority,
                        scheduled_date=datetime.strptime(daily_plan.date, "%Y-%m-%d"),
                        is_subtask=True,
                        order_index=idx,
                        ai_estimated_days=subtask_data.ai_estimated_days
                    )
                    db.add(db_subtask)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan

def get_user_plans_service(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[Plan]:
    """获取用户计划列表"""
    return db.query(Plan).filter(Plan.user_id == user_id).offset(skip).limit(limit).all()

def get_plan_service(db: Session, plan_id: int) -> Plan:
    """获取计划详情"""
    return db.query(Plan).filter(Plan.id == plan_id).first()

def update_plan_status_service(db: Session, plan_id: int, status: str) -> bool:
    """更新计划状态"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if plan:
        plan.status = status
        plan.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False

# 任务服务
def get_tasks_service(
    db: Session, 
    user_id: int, 
    plan_id: int = None, 
    status: str = None,
    skip: int = 0, 
    limit: int = 50
) -> List[Task]:
    """获取任务列表"""
    query = db.query(Task).join(Plan).filter(Plan.user_id == user_id)
    
    if plan_id:
        query = query.filter(Task.plan_id == plan_id)
    if status:
        query = query.filter(Task.status == status)
    
    return query.offset(skip).limit(limit).all()

def update_task_service(db: Session, task_id: int, task_update: TaskUpdate) -> Task:
    """更新任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        if task_update.status:
            task.status = task_update.status
        if task_update.completion_rate is not None:
            task.completion_rate = task_update.completion_rate
        if task_update.completed_at:
            task.completed_at = task_update.completed_at
        
        task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(task)
    return task

# TodoList服务
def create_todo_service(db: Session, todo: TodoItemCreate, user_id: int) -> TodoItem:
    """创建Todo项目"""
    db_todo = TodoItem(
        user_id=user_id,
        title=todo.title,
        description=todo.description,
        priority=todo.priority,
        category=todo.category,
        due_date=todo.due_date,
        reminder_time=todo.reminder_time
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def get_todos_service(
    db: Session,
    user_id: int,
    is_completed: bool = None,
    category: str = None,
    skip: int = 0,
    limit: int = 50
) -> List[TodoItem]:
    """获取Todo列表"""
    query = db.query(TodoItem).filter(TodoItem.user_id == user_id)
    
    if is_completed is not None:
        query = query.filter(TodoItem.is_completed == is_completed)
    if category:
        query = query.filter(TodoItem.category == category)
    
    return query.order_by(TodoItem.created_at.desc()).offset(skip).limit(limit).all()

def update_todo_service(db: Session, todo_id: int, todo_update: TodoItemUpdate) -> TodoItem:
    """更新Todo项目"""
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if todo:
        update_data = todo_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        
        if todo_update.is_completed and not todo.completed_at:
            todo.completed_at = datetime.utcnow()
        elif not todo_update.is_completed and todo.completed_at:
            todo.completed_at = None
            
        todo.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(todo)
    return todo

def delete_todo_service(db: Session, todo_id: int) -> bool:
    """删除Todo项目"""
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if todo:
        db.delete(todo)
        db.commit()
        return True
    return False

# 分析统计服务
def get_dashboard_service(db: Session, user_id: int) -> Dict[str, Any]:
    """获取仪表板数据"""
    # 计划统计
    total_plans = db.query(Plan).filter(Plan.user_id == user_id).count()
    active_plans = db.query(Plan).filter(
        and_(Plan.user_id == user_id, Plan.status == "active")
    ).count()
    
    # 任务统计
    tasks_query = db.query(Task).join(Plan).filter(Plan.user_id == user_id)
    completed_tasks = tasks_query.filter(Task.status == "completed").count()
    pending_tasks = tasks_query.filter(Task.status == "pending").count()
    total_tasks = tasks_query.count()
    
    completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
    
    # Todo统计
    total_todos = db.query(TodoItem).filter(TodoItem.user_id == user_id).count()
    completed_todos = db.query(TodoItem).filter(
        and_(TodoItem.user_id == user_id, TodoItem.is_completed == True)
    ).count()
    
    # 最近活动
    recent_activities = []
    recent_tasks = tasks_query.filter(Task.status == "completed").order_by(
        Task.completed_at.desc()
    ).limit(5).all()
    
    for task in recent_tasks:
        recent_activities.append({
            "type": "task_completed",
            "title": task.title,
            "timestamp": task.completed_at.isoformat() if task.completed_at else None
        })
    
    return {
        "total_plans": total_plans,
        "active_plans": active_plans,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": completion_rate,
        "total_todos": total_todos,
        "completed_todos": completed_todos,
        "recent_activities": recent_activities
    }

def get_analytics_service(db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
    """获取分析统计数据"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 每日完成情况
    daily_completion = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        completed_count = db.query(Task).join(Plan).filter(
            and_(
                Plan.user_id == user_id,
                Task.status == "completed",
                func.date(Task.completed_at) == date.date()
            )
        ).count()
        
        daily_completion.append({
            "date": date.strftime("%Y-%m-%d"),
            "completed": completed_count
        })
    
    # 分类分布
    category_query = db.query(
        TodoItem.category,
        func.count(TodoItem.id).label('count')
    ).filter(TodoItem.user_id == user_id).group_by(TodoItem.category)
    
    category_distribution = {
        row.category or "未分类": row.count 
        for row in category_query.all()
    }
    
    return {
        "daily_completion": daily_completion,
        "weekly_summary": {},
        "productivity_trends": [],
        "category_distribution": category_distribution
    }

# 计划转TodoList服务
def plan_to_todos_service(db: Session, plan_id: int) -> bool:
    """将计划任务转换为TodoList项目"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return False
    
    tasks = db.query(Task).filter(Task.plan_id == plan_id).all()
    
    for task in tasks:
        # 检查是否已经转换过
        existing_todo = db.query(TodoItem).filter(TodoItem.task_id == task.id).first()
        if existing_todo:
            continue
            
        todo = TodoItem(
            user_id=plan.user_id,
            task_id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            category="计划任务",
            due_date=task.scheduled_date,
            is_completed=(task.status == "completed")
        )
        db.add(todo)
    
    db.commit()
    return True

# 子任务服务
def create_subtask_service(db: Session, parent_task_id: int, subtask: SubtaskCreate, user_id: int) -> Task:
    """为主任务创建子任务"""
    # 验证父任务存在且属于用户
    parent_task = db.query(Task).join(Plan).filter(
        Task.id == parent_task_id,
        Plan.user_id == user_id
    ).first()
    
    if not parent_task:
        raise ValueError("父任务不存在或无权限")
    
    # 创建子任务
    db_subtask = Task(
        plan_id=parent_task.plan_id,
        parent_task_id=parent_task_id,
        title=subtask.title,
        description=subtask.description,
        duration=subtask.duration,
        priority=subtask.priority,
        scheduled_date=parent_task.scheduled_date,
        is_subtask=True,
        order_index=subtask.order_index
    )
    db.add(db_subtask)
    db.commit()
    db.refresh(db_subtask)
    return db_subtask

def get_task_with_subtasks_service(db: Session, task_id: int, user_id: int) -> Dict[str, Any]:
    """获取任务及其子任务"""
    # 获取主任务
    main_task = db.query(Task).join(Plan).filter(
        Task.id == task_id,
        Plan.user_id == user_id,
        Task.is_subtask == False
    ).first()
    
    if not main_task:
        return None
    
    # 获取子任务
    subtasks = db.query(Task).filter(
        Task.parent_task_id == task_id
    ).order_by(Task.order_index).all()
    
    return {
        "task": main_task,
        "subtasks": subtasks
    }

def update_subtask_order_service(db: Session, subtask_id: int, new_order: int, user_id: int) -> bool:
    """更新子任务排序"""
    subtask = db.query(Task).join(Plan).filter(
        Task.id == subtask_id,
        Plan.user_id == user_id,
        Task.is_subtask == True
    ).first()
    
    if subtask:
        subtask.order_index = new_order
        subtask.updated_at = datetime.utcnow()
        db.commit()
        return True
    return False

def delete_subtask_service(db: Session, subtask_id: int, user_id: int) -> bool:
    """删除子任务"""
    subtask = db.query(Task).join(Plan).filter(
        Task.id == subtask_id,
        Plan.user_id == user_id,
        Task.is_subtask == True
    ).first()
    
    if subtask:
        db.delete(subtask)
        db.commit()
        return True
    return False

# AI天数估算服务
def estimate_task_days_service(db: Session, task_description: str) -> Dict[str, Any]:
    """使用AI估算任务所需天数"""
    ai_estimated = ai_agent._estimate_required_days(task_description)
    
    return {
        "ai_estimated_days": ai_estimated,
        "confidence_level": 0.8  # 简单的置信度
    }

def suggest_plan_duration_service(db: Session, goal: str, user_preferred_days: Optional[int] = None) -> Dict[str, Any]:
    """AI建议计划持续时间"""
    ai_estimated = ai_agent._estimate_required_days(goal)
    
    suggestions = {
        "ai_suggested_days": ai_estimated,
        "user_preferred_days": user_preferred_days,
        "recommended_days": ai_estimated,
        "reasoning": f"基于目标复杂度分析，建议{ai_estimated}天完成"
    }
    
    # 如果用户偏好与AI建议差异较大，提供调整建议
    if user_preferred_days and abs(user_preferred_days - ai_estimated) > 3:
        if user_preferred_days < ai_estimated:
            suggestions["warning"] = f"用户期望的{user_preferred_days}天可能过于紧张，建议至少{ai_estimated}天"
        else:
            suggestions["note"] = f"用户期望的{user_preferred_days}天较为宽松，可以安排更深入的学习内容"
    
    return suggestions

# 计划管理服务
def update_plan_service(db: Session, plan_id: int, plan_update: PlanUpdate) -> Plan:
    """更新计划信息"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return None
    
    # 更新字段
    if plan_update.title is not None:
        plan.title = plan_update.title
    if plan_update.goal is not None:
        plan.goal = plan_update.goal
    if plan_update.description is not None:
        plan.description = plan_update.description
    if plan_update.status is not None:
        plan.status = plan_update.status
    
    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)
    return plan

def delete_plan_service(db: Session, plan_id: int) -> bool:
    """删除计划及其所有任务"""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return False
    
    # 删除计划相关的所有任务（包括子任务）
    db.query(Task).filter(Task.plan_id == plan_id).delete()
    
    # 删除计划
    db.delete(plan)
    db.commit()
    return True

def create_task_service(db: Session, task: TaskCreate) -> Task:
    """创建新任务"""
    # 验证计划存在
    plan = db.query(Plan).filter(Plan.id == task.plan_id).first()
    if not plan:
        raise ValueError("计划不存在")
    
    db_task = Task(
        plan_id=task.plan_id,
        title=task.description,  # 使用description作为title
        description=task.description,
        time=task.time,
        duration=task.duration,
        priority=task.priority,
        status=task.status,
        reason=task.reason,
        parent_task_id=task.parent_task_id,
        is_subtask=task.parent_task_id is not None,
        order_index=task.order_index,
        scheduled_date=datetime.utcnow()  # 默认为当前日期
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task_service(db: Session, task_id: int) -> bool:
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    
    # 如果是主任务，也删除所有子任务
    if not task.is_subtask:
        db.query(Task).filter(Task.parent_task_id == task_id).delete()
    
    db.delete(task)
    db.commit()
    return True 