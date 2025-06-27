#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试数据脚本
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base, User, Plan, Task, TodoItem
from services import hash_password

# 创建所有表
Base.metadata.create_all(bind=engine)

def add_test_data():
    """向数据库添加测试数据"""
    db: Session = SessionLocal()
    
    try:
        print("🔧 开始添加测试数据...")

        # 1. 创建用户
        test_user = db.query(User).filter(User.id == 1).first()
        if not test_user:
            print("  - 创建测试用户...")
            test_user = User(
                id=1,
                username="testuser",
                email="test@example.com",
                hashed_password=hash_password("password123")
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        else:
            print("  - 测试用户已存在。")

        # 2. 检查是否已有计划，如果没有则创建
        if db.query(Plan).filter(Plan.user_id == test_user.id).count() > 0:
            print("✅ 计划数据已存在，无需添加。")
            return

        # 3. 创建一个计划
        print("  - 创建测试计划...")
        test_plan = Plan(
            user_id=test_user.id,
            title="学习Python编程",
            description="为期一周的Python入门学习计划",
            goal="掌握Python基础语法和面向对象编程",
            plan_type="weekly",
            start_date=datetime.utcnow().date(),
            end_date=datetime.utcnow().date() + timedelta(days=6),
            status="active",
            estimated_total_time=420  # 7小时
        )
        db.add(test_plan)
        db.commit()
        db.refresh(test_plan)

        # 4. 为计划添加任务
        print("  - 为计划添加任务...")
        tasks_data = [
            {"title": "学习Python变量和数据类型", "duration": 60, "priority": "高", "status": "completed", "day": 0, "completed_at": datetime.utcnow() - timedelta(days=1)},
            {"title": "掌握列表、元组和字典", "duration": 90, "priority": "高", "status": "completed", "day": 1, "completed_at": datetime.utcnow()},
            {"title": "学习条件语句和循环", "duration": 60, "priority": "中", "status": "in_progress", "day": 2},
            {"title": "学习函数和模块", "duration": 90, "priority": "中", "status": "pending", "day": 3},
            {"title": "理解面向对象编程", "duration": 120, "priority": "低", "status": "pending", "day": 4},
        ]
        
        for task_item in tasks_data:
            task = Task(
                plan_id=test_plan.id,
                title=task_item["title"],
                description=f"详细描述 - {task_item['title']}",
                reason="这是计划的基础部分",
                duration=task_item["duration"],
                priority=task_item["priority"],
                status=task_item["status"],
                scheduled_date=test_plan.start_date + timedelta(days=task_item["day"]),
                completed_at=task_item.get("completed_at"),
                completion_rate=1.0 if task_item["status"] == "completed" else 0.0
            )
            db.add(task)

        # 5. 创建一些独立的TodoList项目
        print("  - 创建独立的TodoList项目...")
        todos_data = [
            {"title": "晨跑5公里", "category": "健康", "priority": "高", "is_completed": True, "completed_at": datetime.utcnow()},
            {"title": "阅读《原子习惯》一章", "category": "学习", "priority": "中", "is_completed": False},
            {"title": "购买本周 groceries", "category": "生活", "priority": "中", "is_completed": False},
            {"title": "回复工作邮件", "category": "工作", "priority": "高", "is_completed": True, "completed_at": datetime.utcnow() - timedelta(hours=2)},
        ]

        for todo_item in todos_data:
            todo = TodoItem(
                user_id=test_user.id,
                title=todo_item["title"],
                category=todo_item["category"],
                priority=todo_item["priority"],
                is_completed=todo_item["is_completed"],
                completed_at=todo_item.get("completed_at"),
            )
            db.add(todo)
            
        db.commit()
        print("✅ 测试数据添加成功！")

    except Exception as e:
        print(f"❌ 添加测试数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data() 