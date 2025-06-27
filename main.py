#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生活管家AI Agent - 主程序
帮助用户制定和管理生活计划
"""

import os
import sys
import json
from datetime import datetime

from config import validate_config
from life_manager_agent import LifeManagerAgentQwen as LifeManagerAgent
from scheduler import TaskScheduler

def print_welcome():
    """打印欢迎信息"""
    print("\n" + "🌟" * 25)
    print("   🤖 生活管家AI Agent")
    print("🌟" * 25)
    print("💡 帮您制定智能生活计划，实现目标管理")
    print("📅 支持任务拆解、时间规划、定时提醒")
    print("-" * 50)

def print_menu():
    """打印主菜单"""
    print("\n📋 请选择功能:")
    print("1. 🎯 创建新的每日计划")
    print("2. 📅 创建7天计划")
    print("3. 📝 查看当前计划")
    print("4. ✏️  修改现有计划")
    print("5. ⏰ 启动任务提醒")
    print("6. 📊 查看计划统计")
    print("7. 🧠 查看记忆系统状态")
    print("8. ❓ 使用帮助")
    print("0. 👋 退出程序")
    print("-" * 30)

def get_user_goal():
    """获取用户目标信息"""
    print("\n🎯 请详细描述您的目标:")
    print("例如: '我想学习Python编程，掌握基础语法'")
    print("     '准备明天的面试，复习技术问题'")
    print("     '开始健身计划，改善身体状况'")
    
    goal = input("\n目标描述: ").strip()
    
    if not goal:
        print("❌ 目标描述不能为空")
        return None, None
    
    print("\n⏰ 请告诉我您的时间偏好 (可选):")
    print("例如: '我早上比较有精神，适合学习'")
    print("     '下午2-5点比较忙，安排轻松任务'")
    print("     '晚上想放松，不要安排太多任务'")
    
    time_pref = input("\n时间偏好 (直接回车跳过): ").strip()
    
    return goal, time_pref

def create_plan(agent):
    """创建每日计划流程"""
    print("\n" + "="*50)
    print("🎯 创建新的每日计划")
    print("="*50)
    
    # 获取用户目标
    goal, time_pref = get_user_goal()
    if not goal:
        return
    
    # 创建计划
    plan = agent.create_daily_plan(goal, time_pref)
    
    if plan:
        # 显示计划
        agent.display_plan(plan)
        
        # 询问是否保存
        save = input("\n💾 是否保存此计划? (y/n): ").lower().strip()
        if save in ['y', 'yes', '是', '']:
            agent.save_plan(plan)
            print("✅ 计划已保存!")
            
            # 询问是否需要修改
            modify = input("\n🔧 需要修改计划吗? (y/n): ").lower().strip()
            if modify in ['y', 'yes', '是']:
                modify_plan_interactive(agent, plan)
        else:
            print("📝 计划未保存")
    else:
        print("❌ 创建计划失败，请检查网络连接和API配置")

def create_weekly_plan(agent):
    """创建7天计划流程"""
    print("\n" + "="*50)
    print("📅 创建7天计划")
    print("="*50)
    
    # 获取用户目标
    goal, time_pref = get_user_goal()
    if not goal:
        return
    
    print("🤖 正在制定7天计划，这可能需要一些时间...")
    
    # 创建7天计划
    weekly_plan = agent.create_weekly_plan(goal, time_pref)
    
    if weekly_plan:
        # 显示7天计划
        agent.display_weekly_plan(weekly_plan)
        
        # 询问是否保存
        save = input("\n💾 是否保存此7天计划? (y/n): ").lower().strip()
        if save in ['y', 'yes', '是', '']:
            agent.save_weekly_plan(weekly_plan)
            print("✅ 7天计划已保存!")
        else:
            print("📝 7天计划未保存")
    else:
        print("❌ 创建7天计划失败，请检查网络连接和API配置")

def view_current_plan(agent):
    """查看当前计划"""
    print("\n" + "="*50)
    print("📋 当前计划")
    print("="*50)
    
    # 检查是否有当前的每日计划
    current_daily_plan = agent.memory_system.working_memory.get("current_plan")
    # 检查是否有当前的7天计划
    current_weekly_plan = agent.memory_system.working_memory.get("current_weekly_plan")
    
    if current_weekly_plan:
        print("📅 找到7天计划:")
        agent.display_weekly_plan(current_weekly_plan)
        
        # 询问是否要查看详细的每日计划
        detail = input("\n🔍 是否查看某一天的详细计划? (输入1-7或n): ").strip()
        if detail.isdigit() and 1 <= int(detail) <= 7:
            day_index = int(detail) - 1
            if day_index < len(current_weekly_plan.daily_plans):
                selected_day = current_weekly_plan.daily_plans[day_index]
                print(f"\n📋 第{detail}天详细计划:")
                agent.display_plan(selected_day)
    elif current_daily_plan:
        print("📋 找到每日计划:")
        agent.display_plan(current_daily_plan)
    else:
        print("📝 暂无当前活跃计划")
        print("\n🎯 您想创建什么类型的计划?")
        print("1. 📋 每日计划")
        print("2. 📅 7天计划")
        
        choice = input("\n请选择 (1/2/n): ").strip()
        if choice == '1':
            create_plan(agent)
        elif choice == '2':
            create_weekly_plan(agent)

def modify_plan_interactive(agent, current_plan=None):
    """交互式修改计划"""
    print("\n" + "="*50)
    print("✏️  修改计划")
    print("="*50)
    
    if not current_plan:
        current_plan = agent.memory_system.working_memory.get("current_plan")
        if not current_plan:
            print("❌ 没有找到可修改的计划")
            return
    
    # 显示当前计划
    print("\n📋 当前计划:")
    agent.display_plan(current_plan)
    
    print("\n🔧 请描述您想要的修改:")
    print("例如: '把学习时间从早上调到下午'")
    print("     '增加30分钟的休息时间'")
    print("     '删除第3个任务'")
    print("     '调整任务顺序'")
    
    modification = input("\n修改要求: ").strip()
    
    if not modification:
        print("❌ 修改要求不能为空")
        return
    
    # 执行修改
    modified_plan = agent.modify_plan(current_plan, modification)
    
    if modified_plan:
        print("\n✅ 修改完成!")
        agent.display_plan(modified_plan)
        
        # 询问是否保存
        save = input("\n💾 是否保存修改后的计划? (y/n): ").lower().strip()
        if save in ['y', 'yes', '是', '']:
            agent.save_plan(modified_plan)
            print("✅ 修改已保存!")
        else:
            print("📝 修改未保存")
    else:
        print("❌ 修改失败，请重新尝试")

def start_reminders():
    """启动任务提醒"""
    print("\n" + "="*50)
    print("⏰ 启动任务提醒")
    print("="*50)
    
    scheduler = TaskScheduler()
    
    if scheduler.load_plan():
        print("\n⚙️  正在设置提醒...")
        scheduler.setup_daily_reminders()
        scheduler.setup_daily_summary() 
        scheduler.setup_motivational_reminders()
        
        scheduler.show_scheduled_jobs()
        
        print("\n🚀 提醒系统即将启动...")
        print("💡 程序将持续运行，在指定时间发送提醒")
        print("⚠️  请保持程序运行状态")
        
        start = input("\n是否开始? (y/n): ").lower().strip()
        if start in ['y', 'yes', '是', '']:
            scheduler.start_scheduler()
        else:
            print("❌ 已取消启动")
    else:
        print("❌ 无法加载计划文件，请先创建计划")

def show_statistics(agent):
    """显示计划统计"""
    print("\n" + "="*50)
    print("📊 计划统计")
    print("="*50)
    
    current_plan = agent.memory_system.working_memory.get("current_plan")
    if not current_plan:
        print("📝 暂无计划数据")
        return
    
    # 统计信息
    total_time = current_plan.estimated_total_time
    hours = total_time // 60
    minutes = total_time % 60
    
    # 按优先级分类
    high_priority = len([t for t in current_plan.tasks if t.priority == "高"])
    medium_priority = len([t for t in current_plan.tasks if t.priority == "中"])  
    low_priority = len([t for t in current_plan.tasks if t.priority == "低"])
    
    # 时间分布
    morning_tasks = len([t for t in current_plan.tasks if int(t.time.split(':')[0]) < 12])
    afternoon_tasks = len([t for t in current_plan.tasks if 12 <= int(t.time.split(':')[0]) < 18])
    evening_tasks = len([t for t in current_plan.tasks if int(t.time.split(':')[0]) >= 18])
    
    print(f"📋 计划名称: {current_plan.plan_title}")
    print(f"🎯 主要目标: {current_plan.goal}")
    print(f"📅 计划日期: {current_plan.date}")
    print("-" * 30)
    print(f"📊 总任务数量: {current_plan.total_tasks}")
    print(f"⏱️  预计总时间: {hours}小时{minutes}分钟")
    print("-" * 30)
    print("🔥 优先级分布:")
    print(f"   高优先级: {high_priority} 个")
    print(f"   中优先级: {medium_priority} 个")
    print(f"   低优先级: {low_priority} 个")
    print("-" * 30)
    print("🕐 时间分布:")
    print(f"   上午 (00-12): {morning_tasks} 个任务")
    print(f"   下午 (12-18): {afternoon_tasks} 个任务")
    print(f"   晚上 (18-24): {evening_tasks} 个任务")

def show_memory_stats(agent):
    """显示记忆系统状态"""
    print("\n" + "="*50)
    print("🧠 记忆系统状态")
    print("="*50)
    
    # 显示记忆统计
    agent.display_memory_stats()
    
    # 提供记忆管理选项
    print("\n🔧 记忆管理选项:")
    print("1. 📜 查看对话历史")
    print("2. 📊 查看计划历史")
    print("3. 🗑️  清除短期记忆")
    print("4. 💾 导出记忆数据")
    print("0. 🔙 返回主菜单")
    
    try:
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '1':
            show_conversation_history(agent)
        elif choice == '2':
            show_plan_history(agent)
        elif choice == '3':
            clear_short_term_memory(agent)
        elif choice == '4':
            export_memory_data(agent)
        elif choice == '0':
            return
        else:
            print("❌ 无效选择")
    except Exception as e:
        print(f"❌ 操作失败: {e}")

def show_conversation_history(agent):
    """显示对话历史"""
    print("\n💭 最近对话历史:")
    print("-" * 40)
    
    conversations = agent.memory_system.short_term_memory
    if not conversations:
        print("📝 暂无对话记录")
        return
    
    for i, conv in enumerate(conversations[-5:], 1):  # 显示最近5条
        timestamp = conv['timestamp'][:19].replace('T', ' ')
        print(f"{i}. [{timestamp}]")
        print(f"   👤 用户: {conv['user'][:50]}...")
        print(f"   🤖 助手: {conv['agent'][:50]}...")
        print()

def show_plan_history(agent):
    """显示计划历史"""
    print("\n📊 历史计划记录:")
    print("-" * 40)
    
    history = agent.memory_system.long_term_memory.get("plan_history", [])
    if not history:
        print("📝 暂无历史计划")
        return
    
    for i, plan in enumerate(history[-5:], 1):  # 显示最近5个计划
        print(f"{i}. [{plan.get('date', 'N/A')}] {plan.get('goal', 'N/A')[:30]}...")
        print(f"   📊 任务数: {plan.get('total_tasks', 0)}")
        print(f"   ⏱️  预计时间: {plan.get('estimated_time', 0)}分钟")
        print()

def clear_short_term_memory(agent):
    """清除短期记忆"""
    confirm = input("⚠️  确定要清除短期记忆吗？(y/n): ").lower().strip()
    if confirm in ['y', 'yes', '是']:
        agent.memory_system.short_term_memory.clear()
        print("✅ 短期记忆已清除")
    else:
        print("❌ 操作已取消")

def export_memory_data(agent):
    """导出记忆数据"""
    try:
        filename = f"memory_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "short_term_memory": agent.memory_system.short_term_memory,
            "long_term_memory": agent.memory_system.long_term_memory,
            "export_time": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 记忆数据已导出到: {filename}")
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def show_help():
    """显示帮助信息"""
    print("\n" + "="*50)
    print("❓ 使用帮助")
    print("="*50)
    
    print("""
🎯 功能说明:
1. 创建计划: 描述您的目标，AI会自动制定详细的每日计划
2. 查看计划: 显示当前保存的计划内容
3. 修改计划: 根据您的要求调整现有计划
4. 任务提醒: 按时间自动提醒您完成各项任务
5. 计划统计: 查看计划的详细统计信息
6. 记忆系统: 管理AI的学习记忆和对话历史

💡 使用技巧:
• 目标描述越详细越好，AI能制定更精准的计划
• 可以提及时间偏好，如"早上精神好"、"下午比较忙"
• 启动提醒后请保持程序运行，才能收到定时提醒
• 计划会自动保存并归档到记忆系统

🔧 环境配置:
• 需要设置DASHSCOPE_API_KEY
• 在.env文件中配置API密钥
• 确保网络连接正常

❓ 常见问题:
Q: 为什么创建计划失败？
A: 请检查API密钥配置和网络连接

Q: 如何获取API密钥？
A: 通义千问: https://dashscope.console.aliyun.com/apiKey

Q: 提醒系统如何工作？
A: 程序会在后台运行，在指定时间显示提醒信息

Q: 记忆系统有什么用？
A: 帮助AI学习您的偏好，提供更个性化的计划建议
""")

def main():
    """主程序"""
    print_welcome()
    
    # 验证配置
    if not validate_config():
        print("\n❌ 配置验证失败，请检查.env文件中的API密钥设置")
        print("\n🔧 需要设置以下环境变量:")
        print("DASHSCOPE_API_KEY=你的通义千问API密钥")
        return
    
    print("✅ 配置验证通过")
    
    # 初始化Agent
    try:
        print("🤖 正在初始化AI Agent...")
        agent = LifeManagerAgent()
        print("✅ AI Agent初始化完成")
    except Exception as e:
        print(f"❌ AI Agent初始化失败: {e}")
        return
    
    # 主循环
    while True:
        try:
            print_menu()
            choice = input("请选择 (0-8): ").strip()
            
            if choice == '0':
                print("\n👋 感谢使用生活管家AI Agent，再见!")
                break
            elif choice == '1':
                create_plan(agent)
            elif choice == '2':
                create_weekly_plan(agent)
            elif choice == '3':
                view_current_plan(agent)
            elif choice == '4':
                modify_plan_interactive(agent)
            elif choice == '5':
                start_reminders()
            elif choice == '6':
                show_statistics(agent)
            elif choice == '7':
                show_memory_stats(agent)
            elif choice == '8':
                show_help()
            else:
                print("❌ 无效选择，请输入0-8之间的数字")
                
        except KeyboardInterrupt:
            print("\n\n👋 程序已退出")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            continue

if __name__ == "__main__":
    main() 