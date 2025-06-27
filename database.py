#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模型和配置
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
import urllib.parse
from datetime import datetime
from sqlalchemy import text

# 数据库配置
def get_database_url():
    """构建数据库连接字符串"""
    db_type = os.getenv("DB_TYPE", "sqlite")
    
    if db_type.lower() == "sqlserver":
        # SQL Server 配置
        server = os.getenv("DB_SERVER", "localhost")
        database = os.getenv("DB_NAME", "life_manager")
        username = os.getenv("DB_USER", "sa")
        password = os.getenv("DB_PASSWORD", "")
        driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        port = os.getenv("DB_PORT", "1433")
        
        # 构建连接字符串
        if password:
            # 使用用户名密码认证
            connection_string = f"mssql+pyodbc://{username}:{urllib.parse.quote_plus(password)}@{server}:{port}/{database}?driver={urllib.parse.quote_plus(driver)}"
        else:
            # 使用 Windows 集成认证
            connection_string = f"mssql+pyodbc://@{server}:{port}/{database}?driver={urllib.parse.quote_plus(driver)}&trusted_connection=yes"
        
        return connection_string
    
    elif db_type.lower() == "sqlite":
        # SQLite 配置（默认）
        return os.getenv("DATABASE_URL", "sqlite:///./life_manager.db")
    
    else:
        # 其他数据库类型，直接使用 DATABASE_URL
        return os.getenv("DATABASE_URL", "sqlite:///./life_manager.db")

DATABASE_URL = get_database_url()

# 根据数据库类型设置引擎参数
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
elif "mssql" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # 设为 True 可以看到 SQL 语句
        pool_pre_ping=True,  # 连接池预检查
        pool_recycle=3600,   # 连接回收时间
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    plans = relationship("Plan", back_populates="user")
    todos = relationship("TodoItem", back_populates="user")
    memories = relationship("Memory", back_populates="user")

class Plan(Base):
    """计划模型"""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    goal = Column(Text, nullable=False)
    plan_type = Column(String(20), nullable=False)  # 'daily', 'weekly', 'custom'
    duration_days = Column(Integer, default=1)  # 计划持续天数
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")  # 'active', 'completed', 'paused'
    estimated_total_time = Column(Integer, default=0)  # 分钟
    ai_suggested_days = Column(Integer, nullable=True)  # AI建议的天数
    user_preferred_days = Column(Integer, nullable=True)  # 用户偏好的天数
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="plans")
    tasks = relationship("Task", back_populates="plan", cascade="all, delete-orphan")

class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 父任务ID，支持子任务
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reason = Column(Text, nullable=True)
    start_time = Column(String(20), nullable=True)  # "09:00"
    duration = Column(Integer, default=60)  # 分钟
    priority = Column(String(10), default="中")  # 高/中/低
    status = Column(String(20), default="pending")  # 'pending', 'in_progress', 'completed'
    completion_rate = Column(Float, default=0.0)  # 0.0-1.0
    scheduled_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    ai_estimated_days = Column(Integer, nullable=True)  # AI估计需要的天数
    user_preferred_days = Column(Integer, nullable=True)  # 用户希望的天数
    is_subtask = Column(Boolean, default=False)  # 是否为子任务
    order_index = Column(Integer, default=0)  # 排序索引
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    plan = relationship("Plan", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")

class TodoItem(Base):
    """TodoList项目模型"""
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 可以关联到计划任务
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(10), default="中")
    category = Column(String(50), nullable=True)  # 工作/学习/生活/健康等
    due_date = Column(DateTime, nullable=True)
    reminder_time = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="todos")
    task = relationship("Task", foreign_keys=[task_id])

class Memory(Base):
    """记忆系统模型"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_type = Column(String(20), nullable=False)  # 'conversation', 'preference', 'pattern'
    content = Column(Text, nullable=False)
    meta_data = Column(Text, nullable=True)  # JSON字符串
    importance = Column(Float, default=1.0)  # 重要性权重
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="memories")

class Analytics(Base):
    """分析统计模型"""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    metric_name = Column(String(50), nullable=False)  # 'task_completion', 'time_spent', etc.
    metric_value = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    meta_data = Column(Text, nullable=True)  # JSON字符串
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建数据库表
def create_tables():
    Base.metadata.create_all(bind=engine)

def init_db():
    """初始化数据库"""
    create_tables()
    print("✅ 数据库初始化完成")

def migrate_database():
    """迁移数据库到新版本（添加子任务和多天计划支持）"""
    
    try:
        # 检查数据库类型
        if "sqlite" in DATABASE_URL:
            # SQLite 迁移
            with engine.connect() as conn:
                # 添加新字段到 plans 表
                try:
                    conn.execute(text("ALTER TABLE plans ADD COLUMN duration_days INTEGER DEFAULT 1"))
                    print("✅ 添加 plans.duration_days 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 plans.duration_days 失败: {e}")
                
                try:
                    conn.execute(text("ALTER TABLE plans ADD COLUMN ai_suggested_days INTEGER"))
                    print("✅ 添加 plans.ai_suggested_days 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 plans.ai_suggested_days 失败: {e}")
                
                try:
                    conn.execute(text("ALTER TABLE plans ADD COLUMN user_preferred_days INTEGER"))
                    print("✅ 添加 plans.user_preferred_days 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 plans.user_preferred_days 失败: {e}")
                
                # 添加新字段到 tasks 表
                try:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER"))
                    print("✅ 添加 tasks.parent_task_id 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 tasks.parent_task_id 失败: {e}")
                
                try:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN ai_estimated_days INTEGER"))
                    print("✅ 添加 tasks.ai_estimated_days 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 tasks.ai_estimated_days 失败: {e}")
                
                try:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN user_preferred_days INTEGER"))
                    print("✅ 添加 tasks.user_preferred_days 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 tasks.user_preferred_days 失败: {e}")
                
                try:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN is_subtask BOOLEAN DEFAULT 0"))
                    print("✅ 添加 tasks.is_subtask 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 tasks.is_subtask 失败: {e}")
                
                try:
                    conn.execute(text("ALTER TABLE tasks ADD COLUMN order_index INTEGER DEFAULT 0"))
                    print("✅ 添加 tasks.order_index 字段")
                except Exception as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"⚠️ 添加 tasks.order_index 失败: {e}")
                
                conn.commit()
        
        elif "mssql" in DATABASE_URL:
            # SQL Server 迁移
            with engine.connect() as conn:
                # Plans 表迁移
                migration_sqls = [
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('plans') AND name = 'duration_days') ALTER TABLE plans ADD duration_days INTEGER DEFAULT 1",
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('plans') AND name = 'ai_suggested_days') ALTER TABLE plans ADD ai_suggested_days INTEGER",
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('plans') AND name = 'user_preferred_days') ALTER TABLE plans ADD user_preferred_days INTEGER",
                    
                    # Tasks 表迁移
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('tasks') AND name = 'parent_task_id') ALTER TABLE tasks ADD parent_task_id INTEGER",
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('tasks') AND name = 'ai_estimated_days') ALTER TABLE tasks ADD ai_estimated_days INTEGER",
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('tasks') AND name = 'user_preferred_days') ALTER TABLE tasks ADD user_preferred_days INTEGER",
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('tasks') AND name = 'is_subtask') ALTER TABLE tasks ADD is_subtask BIT DEFAULT 0",
                    "IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('tasks') AND name = 'order_index') ALTER TABLE tasks ADD order_index INTEGER DEFAULT 0"
                ]
                
                for sql in migration_sqls:
                    try:
                        conn.execute(text(sql))
                        print(f"✅ 执行SQL: {sql[:50]}...")
                    except Exception as e:
                        print(f"⚠️ SQL执行失败: {e}")
                
                conn.commit()
        
        print("✅ 数据库迁移完成")
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")

if __name__ == "__main__":
    print("选择操作:")
    print("1. 初始化数据库")
    print("2. 迁移数据库")
    choice = input("请输入选择 (1/2): ")
    
    if choice == "1":
        init_db()
    elif choice == "2":
        migrate_database()
    else:
        print("无效选择") 