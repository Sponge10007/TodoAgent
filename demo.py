#!/usr/bin/env python3
"""
生活管家AI Agent 演示脚本
展示如何使用系统创建目标和任务
"""

import requests
import json
from datetime import datetime, timedelta

# API基础URL
BASE_URL = "http://localhost:8000/api"

def create_demo_user():
    """创建演示用户"""
    user_data = {
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "demo123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/", json=user_data)
        if response.status_code == 200:
            print("✅ 演示用户创建成功")
            return response.json()
        else:
            print("⚠️ 用户可能已存在")
            return None
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        return None

def create_fitness_goal():
    """创建健身目标示例"""
    goal_data = {
        "title": "两个月内改变自己",
        "description": "通过科学的健身计划和饮食调整，在两个月内改善体态，增强体质，建立健康的生活方式。目标是减重5公斤，增加肌肉量，提高体能水平。",
        "category": "健身",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=60)).isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/goals/", json=goal_data)
        if response.status_code == 200:
            goal = response.json()
            print("✅ 健身目标创建成功")
            print(f"   目标ID: {goal['id']}")
            print(f"   标题: {goal['title']}")
            return goal
        else:
            print(f"❌ 创建目标失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建目标失败: {e}")
        return None

def create_study_goal():
    """创建学习目标示例"""
    goal_data = {
        "title": "掌握Python Web开发",
        "description": "系统学习Python Web开发技术栈，包括FastAPI、SQLAlchemy、前端技术等，完成一个完整的Web应用项目。",
        "category": "学习",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=45)).isoformat()
    }
    
    try:
        response = requests.post(f"{BASE_URL}/goals/", json=goal_data)
        if response.status_code == 200:
            goal = response.json()
            print("✅ 学习目标创建成功")
            print(f"   目标ID: {goal['id']}")
            print(f"   标题: {goal['title']}")
            return goal
        else:
            print(f"❌ 创建目标失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建目标失败: {e}")
        return None

def view_goals():
    """查看所有目标"""
    try:
        response = requests.get(f"{BASE_URL}/goals/")
        if response.status_code == 200:
            goals = response.json()
            print(f"\n📋 当前共有 {len(goals)} 个目标:")
            for goal in goals:
                print(f"   - {goal['title']} ({goal['category']}) - 进度: {goal['progress']:.1f}%")
            return goals
        else:
            print("❌ 获取目标列表失败")
            return []
    except Exception as e:
        print(f"❌ 获取目标列表失败: {e}")
        return []

def view_tasks(goal_id=None):
    """查看任务"""
    try:
        if goal_id:
            response = requests.get(f"{BASE_URL}/tasks/?goal_id={goal_id}")
        else:
            response = requests.get(f"{BASE_URL}/tasks/")
            
        if response.status_code == 200:
            tasks = response.json()
            print(f"\n📝 当前共有 {len(tasks)} 个任务:")
            for task in tasks:
                status_emoji = "✅" if task['status'] == 'completed' else "⏳"
                print(f"   {status_emoji} {task['title']} - {task['status']}")
            return tasks
        else:
            print("❌ 获取任务列表失败")
            return []
    except Exception as e:
        print(f"❌ 获取任务列表失败: {e}")
        return []

def view_dashboard():
    """查看仪表板数据"""
    try:
        response = requests.get(f"{BASE_URL}/dashboard/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"\n📊 仪表板摘要:")
            print(f"   总目标数: {summary['total_goals']}")
            print(f"   活跃目标: {summary['active_goals']}")
            print(f"   今日任务: {summary['today_tasks']}")
            print(f"   完成率: {summary['completion_rate']}%")
            print(f"   逾期任务: {summary['overdue_tasks']}")
            return summary
        else:
            print("❌ 获取仪表板数据失败")
            return None
    except Exception as e:
        print(f"❌ 获取仪表板数据失败: {e}")
        return None

def simulate_task_completion():
    """模拟任务完成"""
    try:
        # 获取任务列表
        response = requests.get(f"{BASE_URL}/tasks/")
        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                # 完成第一个任务
                task = tasks[0]
                update_response = requests.put(
                    f"{BASE_URL}/tasks/{task['id']}/status",
                    json={"status": "completed"}
                )
                if update_response.status_code == 200:
                    print(f"✅ 任务 '{task['title']}' 已完成")
                else:
                    print("❌ 更新任务状态失败")
            else:
                print("⚠️ 没有可完成的任务")
    except Exception as e:
        print(f"❌ 模拟任务完成失败: {e}")

def main():
    """主演示函数"""
    print("🎯 生活管家AI Agent 演示")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/dashboard/summary")
        if response.status_code != 200:
            print("❌ 无法连接到服务，请确保应用正在运行")
            print("   运行命令: python main.py")
            return
    except Exception:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("   运行命令: python main.py")
        return
    
    print("✅ 服务连接正常")
    
    # 创建演示用户
    create_demo_user()
    
    # 创建示例目标
    print("\n🎯 创建示例目标...")
    fitness_goal = create_fitness_goal()
    study_goal = create_study_goal()
    
    # 查看目标
    goals = view_goals()
    
    # 查看任务
    if fitness_goal:
        print(f"\n📝 查看健身目标的任务:")
        view_tasks(fitness_goal['id'])
    
    # 查看仪表板
    view_dashboard()
    
    # 模拟任务完成
    print("\n🔄 模拟任务完成...")
    simulate_task_completion()
    
    # 再次查看仪表板
    print("\n📊 更新后的仪表板:")
    view_dashboard()
    
    print("\n🎉 演示完成！")
    print("🌐 访问 http://localhost:8000 查看Web界面")
    print("📚 查看API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 