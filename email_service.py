#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件服务模块
提供邮件发送、模板渲染等功能
"""

import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jinja2 import Template
import asyncio
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        """初始化邮件服务"""
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.username = os.getenv('EMAIL_USERNAME', '')
        self.password = os.getenv('EMAIL_PASSWORD', '')
        self.from_name = os.getenv('EMAIL_FROM_NAME', '生活管家AI')
        
        # 线程池用于异步发送邮件
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # 验证配置
        if not self.username or not self.password:
            logger.warning("邮件服务配置不完整，请检查环境变量")
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """创建SMTP连接"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # 启用TLS加密
            server.login(self.username, self.password)
            return server
        except Exception as e:
            logger.error(f"SMTP连接失败: {e}")
            raise
    
    def send_email(self, to_email: str, subject: str, content: str, 
                   is_html: bool = True) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            is_html: 是否为HTML格式
            
        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.username}>"
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加邮件内容
            if is_html:
                msg.attach(MIMEText(content, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            with self._create_smtp_connection() as server:
                server.send_message(msg)
            
            logger.info(f"邮件发送成功: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False
    
    async def send_email_async(self, to_email: str, subject: str, 
                              content: str, is_html: bool = True) -> bool:
        """异步发送邮件"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self.send_email, to_email, subject, content, is_html
        )
    
    def send_task_reminder(self, to_email: str, task_title: str, 
                          task_time: str, duration: int, plan_title: str) -> bool:
        """
        发送任务提醒邮件
        
        Args:
            to_email: 收件人邮箱
            task_title: 任务标题
            task_time: 任务时间
            duration: 任务时长
            plan_title: 计划标题
            
        Returns:
            bool: 发送是否成功
        """
        subject = f"🔔 任务提醒：{task_title}"
        
        # 邮件HTML模板
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .task-info { background: white; padding: 20px; border-radius: 8px; 
                            border-left: 4px solid #667eea; margin: 20px 0; }
                .time-badge { background: #667eea; color: white; padding: 5px 15px; 
                             border-radius: 20px; display: inline-block; margin: 5px 0; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                .btn { background: #667eea; color: white; padding: 12px 24px; 
                      text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 生活管家AI提醒</h1>
                    <p>您的专属任务助手</p>
                </div>
                <div class="content">
                    <h2>📝 任务提醒</h2>
                    <p>您好！以下任务即将开始，请做好准备：</p>
                    
                    <div class="task-info">
                        <h3>📌 {{ task_title }}</h3>
                        <p><strong>📅 计划：</strong> {{ plan_title }}</p>
                        <p><strong>⏰ 开始时间：</strong> <span class="time-badge">{{ task_time }}</span></p>
                        <p><strong>⏳ 预计用时：</strong> {{ duration }} 分钟</p>
                    </div>
                    
                    <p>💡 <strong>温馨提示：</strong></p>
                    <ul>
                        <li>建议提前5分钟准备相关材料</li>
                        <li>确保环境安静，专注完成任务</li>
                        <li>如需调整时间，请及时更新计划</li>
                    </ul>
                    
                    <div style="text-align: center;">
                        <a href="http://localhost:8000" class="btn">📱 打开应用</a>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由生活管家AI自动发送，请勿回复</p>
                    <p>如需取消提醒，请在应用中修改设置</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 渲染模板
        template = Template(html_template)
        content = template.render(
            task_title=task_title,
            task_time=task_time,
            duration=duration,
            plan_title=plan_title
        )
        
        return self.send_email(to_email, subject, content, is_html=True)
    
    def send_daily_summary(self, to_email: str, plan_title: str, 
                          total_tasks: int, completed_tasks: int) -> bool:
        """
        发送每日总结邮件
        
        Args:
            to_email: 收件人邮箱
            plan_title: 计划标题
            total_tasks: 总任务数
            completed_tasks: 已完成任务数
            
        Returns:
            bool: 发送是否成功
        """
        subject = f"📊 每日总结：{plan_title}"
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                         color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .stats { display: flex; justify-content: space-around; margin: 20px 0; }
                .stat-item { text-align: center; background: white; padding: 20px; 
                            border-radius: 8px; flex: 1; margin: 0 10px; }
                .stat-number { font-size: 2em; font-weight: bold; color: #f5576c; }
                .progress-bar { background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden; }
                .progress-fill { background: linear-gradient(90deg, #f093fb, #f5576c); 
                                height: 100%; transition: width 0.3s ease; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌙 每日总结</h1>
                    <p>{{ plan_title }}</p>
                </div>
                <div class="content">
                    <h2>📊 今日完成情况</h2>
                    
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-number">{{ completed_tasks }}</div>
                            <div>已完成</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{{ total_tasks }}</div>
                            <div>总任务</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">{{ completion_rate }}%</div>
                            <div>完成率</div>
                        </div>
                    </div>
                    
                    <div style="margin: 20px 0;">
                        <h3>完成进度</h3>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {{ completion_rate }}%;"></div>
                        </div>
                    </div>
                    
                    {% if completion_rate >= 80 %}
                    <p>🎉 <strong>太棒了！</strong>您今天的表现非常出色，完成率达到了{{ completion_rate }}%！</p>
                    {% elif completion_rate >= 60 %}
                    <p>👍 <strong>不错！</strong>您今天完成了大部分任务，继续保持！</p>
                    {% else %}
                    <p>💪 <strong>继续努力！</strong>明天可以调整计划，争取更好的完成率。</p>
                    {% endif %}
                    
                    <p>💭 <strong>反思建议：</strong></p>
                    <ul>
                        <li>哪些任务完成得比较顺利？</li>
                        <li>遇到了什么困难或挑战？</li>
                        <li>明天可以如何改进？</li>
                    </ul>
                </div>
                <div class="footer">
                    <p>此邮件由生活管家AI自动发送</p>
                    <p>继续加油，明天会更好！</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        content = template.render(
            plan_title=plan_title,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            completion_rate=int(completion_rate)
        )
        
        return self.send_email(to_email, subject, content, is_html=True)
    
    def send_daily_start_reminder(self, to_email: str, plan_title: str, 
                                 goal: str, total_tasks: int) -> bool:
        """
        发送每日开始提醒邮件
        
        Args:
            to_email: 收件人邮箱
            plan_title: 计划标题
            goal: 目标描述
            total_tasks: 总任务数
            
        Returns:
            bool: 发送是否成功
        """
        subject = f"🌅 新的一天开始了：{plan_title}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                         color: #333; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
                .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
                .goal-box { background: white; padding: 20px; border-radius: 8px; 
                           border-left: 4px solid #fcb69f; margin: 20px 0; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                .motivational { background: #fff3cd; padding: 15px; border-radius: 8px; 
                               border-left: 4px solid #ffc107; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌅 早上好！</h1>
                    <p>新的一天，新的开始</p>
                </div>
                <div class="content">
                    <h2>🎯 今日目标</h2>
                    
                    <div class="goal-box">
                        <h3>{{ plan_title }}</h3>
                        <p><strong>目标：</strong>{{ goal }}</p>
                        <p><strong>任务数量：</strong>{{ total_tasks }} 个任务等待完成</p>
                    </div>
                    
                    <div class="motivational">
                        <h3>💪 今日励志</h3>
                        <p><em>"每一个成功者都有一个开始。勇于开始，才能找到成功的路。"</em></p>
                    </div>
                    
                    <p>🌟 <strong>今日建议：</strong></p>
                    <ul>
                        <li>先完成最重要的任务</li>
                        <li>保持专注，避免分心</li>
                        <li>适当休息，保持精力</li>
                        <li>遇到困难不要放弃</li>
                    </ul>
                    
                    <p style="text-align: center; font-size: 18px; color: #fcb69f;">
                        <strong>相信自己，今天一定会很棒！</strong>
                    </p>
                </div>
                <div class="footer">
                    <p>生活管家AI为您加油助威！</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        content = template.render(
            plan_title=plan_title,
            goal=goal,
            total_tasks=total_tasks
        )
        
        return self.send_email(to_email, subject, content, is_html=True)
    
    def test_connection(self) -> bool:
        """测试邮件服务连接"""
        try:
            with self._create_smtp_connection() as server:
                logger.info("邮件服务连接测试成功")
                return True
        except Exception as e:
            logger.error(f"邮件服务连接测试失败: {e}")
            return False

# 全局邮件服务实例
email_service = EmailService() 