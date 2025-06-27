#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件服务测试脚本
用于独立测试邮件发送功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service

def test_email_connection():
    """测试邮件服务连接"""
    print("🔧 测试邮件服务连接...")
    
    # 显示配置信息
    print(f"SMTP服务器: {email_service.smtp_server}")
    print(f"SMTP端口: {email_service.smtp_port}")
    print(f"用户名: {email_service.username}")
    print(f"发件人名称: {email_service.from_name}")
    
    if not email_service.username or not email_service.password:
        print("❌ 邮件配置不完整，请检查环境变量:")
        print("   EMAIL_USERNAME - 邮箱用户名")
        print("   EMAIL_PASSWORD - 邮箱密码/授权码")
        return False
    
    # 测试连接
    success = email_service.test_connection()
    if success:
        print("✅ 邮件服务连接测试成功！")
        return True
    else:
        print("❌ 邮件服务连接测试失败！")
        return False

def test_send_email():
    """测试发送邮件"""
    test_email = input("请输入测试邮箱地址: ").strip()
    
    if not test_email:
        print("❌ 邮箱地址不能为空")
        return
    
    print(f"📧 正在向 {test_email} 发送测试邮件...")
    
    success = email_service.send_email(
        to_email=test_email,
        subject="🤖 生活管家AI - 邮件服务测试",
        content="""
        <h2>🎉 邮件服务测试成功！</h2>
        <p>恭喜！您的邮件服务配置正确，可以正常发送邮件提醒。</p>
        
        <h3>📋 配置信息</h3>
        <ul>
            <li><strong>SMTP服务器:</strong> {smtp_server}</li>
            <li><strong>端口:</strong> {smtp_port}</li>
            <li><strong>发件人:</strong> {from_name}</li>
        </ul>
        
        <h3>🔔 支持的提醒类型</h3>
        <ul>
            <li>任务开始前提醒</li>
            <li>每日计划开始提醒</li>
            <li>每日完成情况总结</li>
        </ul>
        
        <p>现在您可以在生活管家AI中设置邮件提醒了！</p>
        
        <hr>
        <p><small>此邮件由生活管家AI邮件服务测试脚本发送</small></p>
        """.format(
            smtp_server=email_service.smtp_server,
            smtp_port=email_service.smtp_port,
            from_name=email_service.from_name
        ),
        is_html=True
    )
    
    if success:
        print("✅ 测试邮件发送成功！请检查您的邮箱（包括垃圾邮件箱）")
    else:
        print("❌ 测试邮件发送失败！")

def test_task_reminder():
    """测试任务提醒邮件"""
    test_email = input("请输入测试邮箱地址: ").strip()
    
    if not test_email:
        print("❌ 邮箱地址不能为空")
        return
    
    print(f"📧 正在向 {test_email} 发送任务提醒测试邮件...")
    
    success = email_service.send_task_reminder(
        to_email=test_email,
        task_title="学习Python编程基础",
        task_time="14:30",
        duration=60,
        plan_title="Python学习计划"
    )
    
    if success:
        print("✅ 任务提醒邮件发送成功！")
    else:
        print("❌ 任务提醒邮件发送失败！")

def test_daily_start():
    """测试每日开始提醒邮件"""
    test_email = input("请输入测试邮箱地址: ").strip()
    
    if not test_email:
        print("❌ 邮箱地址不能为空")
        return
    
    print(f"📧 正在向 {test_email} 发送每日开始提醒测试邮件...")
    
    success = email_service.send_daily_start_reminder(
        to_email=test_email,
        plan_title="Python学习计划",
        goal="掌握Python基础语法和面向对象编程",
        total_tasks=5
    )
    
    if success:
        print("✅ 每日开始提醒邮件发送成功！")
    else:
        print("❌ 每日开始提醒邮件发送失败！")

def test_daily_summary():
    """测试每日总结邮件"""
    test_email = input("请输入测试邮箱地址: ").strip()
    
    if not test_email:
        print("❌ 邮箱地址不能为空")
        return
    
    print(f"📧 正在向 {test_email} 发送每日总结测试邮件...")
    
    success = email_service.send_daily_summary(
        to_email=test_email,
        plan_title="Python学习计划",
        total_tasks=5,
        completed_tasks=4
    )
    
    if success:
        print("✅ 每日总结邮件发送成功！")
    else:
        print("❌ 每日总结邮件发送失败！")

def show_config_help():
    """显示配置帮助信息"""
    print("\n📋 邮件服务配置说明")
    print("="*50)
    print("请在 .env 文件中配置以下环境变量：")
    print()
    print("# 邮件服务配置")
    print("EMAIL_SMTP_SERVER=smtp.gmail.com")
    print("EMAIL_SMTP_PORT=587")
    print("EMAIL_USERNAME=your_email@gmail.com")
    print("EMAIL_PASSWORD=your_app_password")
    print("EMAIL_FROM_NAME=生活管家AI")
    print()
    print("💡 常用邮箱配置：")
    print("Gmail: smtp.gmail.com:587 (需要应用专用密码)")
    print("QQ邮箱: smtp.qq.com:587 (需要授权码)")
    print("163邮箱: smtp.163.com:587 (需要授权码)")
    print("Outlook: smtp-mail.outlook.com:587")
    print()
    print("⚠️ 注意：")
    print("- Gmail需要启用两步验证并生成应用专用密码")
    print("- QQ/163邮箱需要开启SMTP服务并生成授权码")
    print("- 不要使用主账户密码，使用专门的应用密码/授权码")

def main():
    """主函数"""
    print("🤖 生活管家AI - 邮件服务测试工具")
    print("="*50)
    
    while True:
        print("\n请选择测试项目：")
        print("1. 测试邮件服务连接")
        print("2. 发送基础测试邮件")
        print("3. 测试任务提醒邮件")
        print("4. 测试每日开始提醒邮件")
        print("5. 测试每日总结邮件")
        print("6. 显示配置帮助")
        print("0. 退出")
        
        choice = input("\n请输入选项 (0-6): ").strip()
        
        if choice == "1":
            test_email_connection()
        elif choice == "2":
            if test_email_connection():
                test_send_email()
        elif choice == "3":
            if test_email_connection():
                test_task_reminder()
        elif choice == "4":
            if test_email_connection():
                test_daily_start()
        elif choice == "5":
            if test_email_connection():
                test_daily_summary()
        elif choice == "6":
            show_config_help()
        elif choice == "0":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main() 