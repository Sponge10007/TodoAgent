from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class GoalBase(BaseModel):
    title: str
    description: str
    category: str
    start_date: datetime
    end_date: datetime

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: int
    status: str
    progress: float
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: str
    due_date: datetime
    priority: str
    estimated_duration: int

class TaskCreate(TaskBase):
    goal_id: int

class Task(TaskBase):
    id: int
    status: str
    goal_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskProgressBase(BaseModel):
    completed: bool
    notes: Optional[str] = None

class TaskProgressCreate(TaskProgressBase):
    task_id: int

class TaskProgress(TaskProgressBase):
    id: int
    task_id: int
    completion_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class GoalWithTasks(Goal):
    tasks: List[Task] = []
    
    class Config:
        from_attributes = True

class TaskWithProgress(Task):
    progress: List[TaskProgress] = []
    
    class Config:
        from_attributes = True 