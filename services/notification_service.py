from datetime import datetime, timedelta
from typing import List, Dict, Any
import schedule
import time
import threading
from sqlalchemy.orm import Session
from models.database import SessionLocal
from .task_service import TaskService
from .goal_service import GoalService
from .ai_planner import AIPlanner

class NotificationService:
    def __init__(self):
        self.task_service = TaskService()
        self.goal_service = GoalService()
        self.ai_planner = AIPlanner()
        self.is_running = False
        self.scheduler_thread = None
    
    def start_scheduler(self):
        """启动定时任务调度器"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # 设置每天上午9点推送任务提醒
        schedule.every().day.at("09:00").do(self.send_daily_notifications)
        
        # 设置每天下午6点推送进度更新
        schedule.every().day.at("18:00").do(self.send_progress_updates)
        
        # 启动调度器线程
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """停止定时任务调度器"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
    
    def _run_scheduler(self):
        """运行调度器"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def send_daily_notifications(self):
        """发送每日任务提醒"""
        db = SessionLocal()
        try:
            # 获取所有用户（这里简化处理，实际应该有用户管理）
            from models.models import User
            users = db.query(User).all()
            
            for user in users:
                today = datetime.utcnow()
                daily_tasks = self.task_service.get_daily_tasks(db, user.id, today)
                
                if daily_tasks:
                    notification = self._create_daily_notification(user, daily_tasks)
                    self._send_notification(notification)
                    
        finally:
            db.close()
    
    def send_progress_updates(self):
        """发送进度更新通知"""
        db = SessionLocal()
        try:
            from models.models import User
            users = db.query(User).all()
            
            for user in users:
                active_goals = self.goal_service.get_active_goals(db, user.id)
                
                for goal in active_goals:
                    # 计算进度
                    progress = self.goal_service.calculate_goal_progress(db, goal.id)
                    
                    # 更新目标进度
                    self.goal_service.update_goal_progress(db, goal.id, progress)
                    
                    # 生成激励消息
                    motivation = self.ai_planner.generate_motivation_message(goal.title, progress)
                    
                    notification = self._create_progress_notification(user, goal, progress, motivation)
                    self._send_notification(notification)
                    
        finally:
            db.close()
    
    def _create_daily_notification(self, user, daily_tasks: List) -> Dict[str, Any]:
        """创建每日通知内容"""
        task_list = []
        for task in daily_tasks:
            task_list.append({
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "estimated_duration": task.estimated_duration
            })
        
        return {
            "type": "daily_tasks",
            "user_id": user.id,
            "username": user.username,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "tasks": task_list,
            "message": f"早上好，{user.username}！今天你有 {len(daily_tasks)} 个任务需要完成。"
        }
    
    def _create_progress_notification(self, user, goal, progress: float, motivation: str) -> Dict[str, Any]:
        """创建进度更新通知内容"""
        return {
            "type": "progress_update",
            "user_id": user.id,
            "username": user.username,
            "goal_title": goal.title,
            "progress": progress,
            "message": motivation,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
    
    def _send_notification(self, notification: Dict[str, Any]):
        """发送通知（这里可以集成邮件、短信、推送等）"""
        # 这里简化处理，实际应该集成具体的通知渠道
        print(f"发送通知: {notification}")
        
        # 示例：可以集成邮件服务
        # self._send_email_notification(notification)
        
        # 示例：可以集成短信服务
        # self._send_sms_notification(notification)
        
        # 示例：可以集成推送服务
        # self._send_push_notification(notification)
    
    def send_immediate_notification(self, user_id: int, message: str, notification_type: str = "info"):
        """发送即时通知"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                notification = {
                    "type": notification_type,
                    "user_id": user_id,
                    "username": user.username,
                    "message": message,
                    "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                }
                self._send_notification(notification)
        finally:
            db.close()
    
    def get_user_notifications(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """获取用户的通知历史"""
        # 这里简化处理，实际应该从数据库获取通知历史
        return []
    
    def mark_notification_read(self, notification_id: int, user_id: int):
        """标记通知为已读"""
        # 这里简化处理，实际应该更新数据库中的通知状态
        pass 