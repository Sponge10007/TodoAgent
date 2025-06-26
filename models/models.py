from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    goals = relationship("Goal", back_populates="user")
    
class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    category = Column(String)  # 健身、学习、工作等
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String, default="active")  # active, completed, paused
    progress = Column(Float, default=0.0)  # 0-100
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal")
    
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    due_date = Column(DateTime)
    priority = Column(String, default="medium")  # low, medium, high
    status = Column(String, default="pending")  # pending, in_progress, completed
    estimated_duration = Column(Integer)  # 预计完成时间（分钟）
    goal_id = Column(Integer, ForeignKey("goals.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    goal = relationship("Goal", back_populates="tasks")
    progress = relationship("TaskProgress", back_populates="task")
    
class TaskProgress(Base):
    __tablename__ = "task_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="progress") 