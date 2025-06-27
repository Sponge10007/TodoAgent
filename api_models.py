#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API请求和响应模型
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PlanType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"  # 自定义天数计划

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Priority(str, Enum):
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

# 用户相关
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 计划相关
class PlanCreate(BaseModel):
    goal: str = Field(..., min_length=5, max_length=500)
    time_preference: Optional[str] = Field(None, max_length=200)
    plan_type: PlanType = PlanType.DAILY
    duration_days: Optional[int] = Field(None, ge=1, le=365, description="计划持续天数")
    user_preferred_days: Optional[int] = Field(None, ge=1, le=365, description="用户希望的天数")

class PlanUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    goal: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None

class TaskCreate(BaseModel):
    user_id: int
    plan_id: int
    description: str = Field(..., min_length=1, max_length=500)
    time: Optional[str] = Field(None, max_length=10, description="任务时间，如09:00")
    duration: int = Field(60, ge=5, le=480, description="预计时长（分钟）")
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    reason: Optional[str] = Field(None, max_length=500, description="任务原因或说明")
    parent_task_id: Optional[int] = None
    order_index: int = Field(0, ge=0, description="排序索引")

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    reason: Optional[str]
    start_time: Optional[str]
    duration: int
    priority: str
    status: str
    completion_rate: float
    scheduled_date: Optional[datetime]
    completed_at: Optional[datetime]
    parent_task_id: Optional[int] = None  # 父任务ID
    is_subtask: bool = False  # 是否为子任务
    order_index: int = 0  # 排序索引
    ai_estimated_days: Optional[int] = None  # AI估计天数
    user_preferred_days: Optional[int] = None  # 用户偏好天数
    subtasks: List["TaskResponse"] = []  # 子任务列表
    
    class Config:
        from_attributes = True

class PlanResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    goal: str
    plan_type: str
    duration_days: int  # 计划持续天数
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    estimated_total_time: int
    ai_suggested_days: Optional[int] = None  # AI建议天数
    user_preferred_days: Optional[int] = None  # 用户偏好天数
    created_at: datetime
    tasks: List[TaskResponse] = []
    
    class Config:
        from_attributes = True

# TodoList相关
class TodoItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Priority.MEDIUM
    category: Optional[str] = Field(None, max_length=50)
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None

class TodoItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    category: Optional[str] = Field(None, max_length=50)
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    is_completed: Optional[bool] = None

class TodoItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    category: Optional[str]
    due_date: Optional[datetime]
    reminder_time: Optional[datetime]
    is_completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    task_id: Optional[int]
    
    class Config:
        from_attributes = True

# 子任务相关
class SubtaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    duration: int = Field(60, ge=5, le=480, description="预计时长（分钟）")
    priority: Priority = Priority.MEDIUM
    order_index: int = Field(0, ge=0, description="排序索引")

class TaskWithSubtasks(BaseModel):
    task: TaskResponse
    subtasks: List[TaskResponse]

# 任务更新
class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    completion_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    completed_at: Optional[datetime] = None
    parent_task_id: Optional[int] = None
    order_index: Optional[int] = None

# 分析统计
class DashboardData(BaseModel):
    total_plans: int
    active_plans: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    total_todos: int
    completed_todos: int
    recent_activities: List[Dict[str, Any]]

class AnalyticsResponse(BaseModel):
    daily_completion: List[Dict[str, Any]]
    weekly_summary: Dict[str, Any]
    productivity_trends: List[Dict[str, Any]]
    category_distribution: Dict[str, int]

# 搜索和过滤
class TaskFilter(BaseModel):
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class TodoFilter(BaseModel):
    is_completed: Optional[bool] = None
    priority: Optional[Priority] = None
    category: Optional[str] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None

# 通用响应
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[str] = None

# 解决自引用问题
TaskResponse.model_rebuild() 