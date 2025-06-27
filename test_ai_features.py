#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI反问和提醒功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_ai_follow_up_questions():
    """测试AI反问功能"""
    print("🧪 测试AI反问功能...")
    
    # 测试不同类型的目标
    test_cases = [
        {
            "goal": "学习Python编程",
            "plan_type": "daily"
        },
        {
            "goal": "学习C++版面向对象程序设计",
            "plan_type": "custom"
        },
        {
            "goal": "30天健身计划",
            "plan_type": "custom"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {case['goal']}")
        
        try:
            # 调用AI反问API
            response = requests.get(
                f"{BASE_URL}/ai/follow-up-questions",
                params={
                    "goal_description": case["goal"],
                    "plan_type": case["plan_type"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取 {data['total_questions']} 个问题")
                
                for j, question in enumerate(data['questions'], 1):
                    print(f"   {j}. {question}")
                    
            else:
                print(f"❌ 请求失败: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def test_reminder_schedule():
    """测试提醒功能"""
    print("\n🔔 测试提醒功能...")
    
    try:
        # 先获取现有计划
        plans_response = requests.get(f"{BASE_URL}/plans/", params={"user_id": 1})
        
        if plans_response.status_code == 200:
            plans = plans_response.json()
            
            if plans:
                plan_id = plans[0]['id']
                print(f"📋 使用计划ID: {plan_id}")
                
                # 测试设置提醒
                reminder_response = requests.post(
                    f"{BASE_URL}/reminders/schedule",
                    params={
                        "plan_id": plan_id,
                        "user_email": "test@example.com"
                    }
                )
                
                if reminder_response.status_code == 200:
                    data = reminder_response.json()
                    print(f"✅ 提醒设置成功")
                    print(f"   计划: {data['data']['plan_title']}")
                    print(f"   提醒数量: {data['data']['total_reminders']}")
                    
                    for reminder in data['data']['reminders'][:3]:  # 只显示前3个
                        print(f"   - {reminder['message']}")
                        
                else:
                    print(f"❌ 设置提醒失败: {reminder_response.status_code} - {reminder_response.text}")
            else:
                print("⚠️ 没有找到计划，请先创建一个计划")
        else:
            print(f"❌ 获取计划失败: {plans_response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_notification_js():
    """测试浏览器通知JavaScript生成"""
    print("\n🌐 测试浏览器通知功能...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/reminders/notification-js",
            params={
                "message": "📝 即将开始：学习Python基础 (60分钟)",
                "task_id": 1
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 浏览器通知代码生成成功")
            print(f"   消息: {data['reminder']['message']}")
            print("   JavaScript代码已生成 ✓")
        else:
            print(f"❌ 生成失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试AI反问和提醒功能")
    print("=" * 50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    # 检查服务器是否可用
    try:
        health_response = requests.get(f"{BASE_URL}/../health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print("⚠️ 服务器可能未完全启动")
    except:
        print("❌ 无法连接到服务器，请确保服务器已启动")
        return
    
    # 运行测试
    test_ai_follow_up_questions()
    test_reminder_schedule()
    test_notification_js()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    print("\n💡 使用说明:")
    print("1. 创建计划后会自动弹出AI反问对话框")
    print("2. 在计划卡片上点击'AI优化'按钮可手动触发反问")
    print("3. 点击'设置提醒'按钮可配置浏览器和邮件提醒")
    print("4. 浏览器通知需要用户授权权限")

if __name__ == "__main__":
    main() 