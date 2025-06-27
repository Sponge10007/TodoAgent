from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, time

class Task(BaseModel):
    """单个任务模型"""
    time: str = Field(description="任务的开始时间，格式为 HH:MM")
    description: str = Field(description="任务的具体描述")
    reason: str = Field(description="为什么安排这个任务的简要理由")
    duration: int = Field(description="预计完成时间（分钟）", default=30)
    priority: str = Field(description="任务优先级：高/中/低", default="中")

class DailyPlan(BaseModel):
    """每日计划模型"""
    plan_title: str = Field(description="整个计划的标题")
    goal: str = Field(description="用户的目标")
    date: str = Field(description="计划日期，格式为 YYYY-MM-DD")
    tasks: List[Task] = Field(description="包含全天所有任务的列表")
    total_tasks: int = Field(description="总任务数量")
    estimated_total_time: int = Field(description="预计总时间（分钟）")

class WeeklyPlan(BaseModel):
    """周计划模型"""
    plan_title: str = Field(description="周计划标题")
    main_goal: str = Field(description="主要目标")
    start_date: str = Field(description="开始日期")
    end_date: str = Field(description="结束日期")
    daily_plans: List[DailyPlan] = Field(description="每日计划列表")

class UserGoal(BaseModel):
    """用户目标模型"""
    title: str = Field(description="目标标题")
    description: str = Field(description="目标描述")
    deadline: str = Field(description="目标截止时间")
    category: str = Field(description="目标类别：健身/学习/工作/生活等")
    difficulty: str = Field(description="目标难度：简单/中等/困难")
    time_preference: Optional[str] = Field(description="用户时间偏好", default=None) 