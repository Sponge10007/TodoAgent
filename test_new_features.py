#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新功能：子任务和自定义天数计划
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ai_estimation():
    """测试AI估算功能"""
    print("🧪 测试AI估算功能...")
    
    # 测试估算天数
    params = {"task_description": "学习Python编程，掌握基础语法和面向对象编程"}
    response = requests.post(f"{BASE_URL}/api/ai/estimate-days", params=params)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ AI估算结果: {result['ai_estimated_days']}天")
    else:
        print(f"❌ AI估算失败: {response.text}")

def test_custom_plan():
    """测试自定义天数计划"""
    print("\n🧪 测试自定义天数计划...")
    
    plan_data = {
        "goal": "深入学习机器学习，包括线性回归、决策树、神经网络等算法",
        "time_preference": "每天晚上7-9点学习",
        "plan_type": "custom",
        "duration_days": 21,
        "user_preferred_days": 21
    }
    
    response = requests.post(f"{BASE_URL}/api/plans/?user_id=1", 
                           json=plan_data)
    
    if response.status_code == 200:
        plan = response.json()
        print(f"✅ 自定义计划创建成功: {plan['title']}")
        print(f"   持续天数: {plan['duration_days']}天")
        print(f"   AI建议天数: {plan.get('ai_suggested_days', '未设置')}天")
        print(f"   任务数量: {len(plan['tasks'])}")
        return plan['id']
    else:
        print(f"❌ 创建自定义计划失败: {response.text}")
        return None

def test_subtasks(plan_id):
    """测试子任务功能"""
    if not plan_id:
        print("\n⚠️ 跳过子任务测试（无有效计划ID）")
        return
    
    print("\n🧪 测试子任务功能...")
    
    # 获取计划任务
    response = requests.get(f"{BASE_URL}/api/tasks/?user_id=1&plan_id={plan_id}")
    if response.status_code != 200:
        print(f"❌ 获取任务失败: {response.text}")
        return
    
    tasks = response.json()
    if not tasks:
        print("⚠️ 计划中没有任务")
        return
    
    # 为第一个主任务添加子任务
    main_task = None
    for task in tasks:
        if not task.get('is_subtask', False):
            main_task = task
            break
    
    if not main_task:
        print("⚠️ 没有找到主任务")
        return
    
    print(f"   选择主任务: {main_task['title']}")
    
    # 添加子任务
    subtask_data = {
        "title": "阅读相关理论资料",
        "description": "深入理解算法原理",
        "duration": 45,
        "priority": "高",
        "order_index": 0
    }
    
    response = requests.post(f"{BASE_URL}/api/tasks/{main_task['id']}/subtasks?user_id=1", 
                           json=subtask_data)
    
    if response.status_code == 200:
        subtask = response.json()
        print(f"✅ 子任务创建成功: {subtask['title']}")
        
        # 测试获取任务及其子任务
        response = requests.get(f"{BASE_URL}/api/tasks/{main_task['id']}/with-subtasks?user_id=1")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取任务及子任务成功:")
            print(f"   主任务: {result['task']['title']}")
            print(f"   子任务数量: {len(result['subtasks'])}")
            return subtask['id']
        else:
            print(f"❌ 获取任务及子任务失败: {response.text}")
    else:
        print(f"❌ 创建子任务失败: {response.text}")
    
    return None

def test_subtask_management(subtask_id):
    """测试子任务管理功能"""
    if not subtask_id:
        print("\n⚠️ 跳过子任务管理测试（无有效子任务ID）")
        return
    
    print("\n🧪 测试子任务管理...")
    
    # 更新子任务状态
    update_data = {
        "status": "completed",
        "completed_at": "2025-01-15T10:00:00Z"
    }
    
    response = requests.put(f"{BASE_URL}/api/tasks/{subtask_id}", 
                          json=update_data)
    
    if response.status_code == 200:
        print("✅ 子任务状态更新成功")
    else:
        print(f"❌ 更新子任务状态失败: {response.text}")

def main():
    """主测试函数"""
    print("🚀 开始测试新功能...")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    try:
        # 测试服务是否可用
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 服务不可用")
            return
        print("✅ 服务正常运行")
        
        # 执行测试
        test_ai_estimation()
        plan_id = test_custom_plan()
        subtask_id = test_subtasks(plan_id)
        test_subtask_management(subtask_id)
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        
        # 显示访问地址
        print(f"\n🌐 访问应用: {BASE_URL}")
        print("💡 新功能:")
        print("   1. 创建计划时选择 '自定义天数'")
        print("   2. 在计划任务中点击 '子任务' 按钮管理子任务")
        print("   3. AI会自动估算所需天数并提供建议")
        
    except requests.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main() 