#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时通知服务模块
支持WebSocket和浏览器通知
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """通知类型枚举"""
    TASK_REMINDER = "task_reminder"
    TASK_COMPLETED = "task_completed"
    PLAN_CREATED = "plan_created"
    DEADLINE_APPROACHING = "deadline_approaching"
    SYSTEM_MESSAGE = "system_message"
    EMAIL_SENT = "email_sent"
    FILE_UPLOADED = "file_uploaded"

class NotificationPriority(Enum):
    """通知优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[int, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int) -> str:
        """建立连接"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(f"用户 {user_id} 建立WebSocket连接: {connection_id}")
        return connection_id
    
    def disconnect(self, connection_id: str, user_id: int):
        """断开连接"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"用户 {user_id} 断开WebSocket连接: {connection_id}")
    
    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """向特定用户发送消息"""
        if user_id not in self.user_connections:
            return
        
        disconnected_connections = []
        
        for connection_id in self.user_connections[user_id]:
            websocket = self.active_connections.get(connection_id)
            if websocket:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"发送消息失败: {e}")
                    disconnected_connections.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected_connections:
            self.disconnect(connection_id, user_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """广播消息给所有连接"""
        disconnected_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected_connections.append(connection_id)
        
        # 清理断开的连接
        for connection_id in disconnected_connections:
            # 找到对应的用户ID
            for user_id, conn_ids in self.user_connections.items():
                if connection_id in conn_ids:
                    self.disconnect(connection_id, user_id)
                    break

class NotificationService:
    """通知服务类"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.notification_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        
    async def send_notification(self, 
                              user_id: int,
                              notification_type: NotificationType,
                              title: str,
                              message: str,
                              priority: NotificationPriority = NotificationPriority.NORMAL,
                              data: Optional[Dict[str, Any]] = None):
        """发送通知"""
        
        notification = {
            "id": str(uuid.uuid4()),
            "type": notification_type.value,
            "title": title,
            "message": message,
            "priority": priority.value,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "read": False
        }
        
        # 保存到历史记录
        self.notification_history.append(notification)
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]
        
        # 通过WebSocket发送
        await self.connection_manager.send_to_user(user_id, {
            "type": "notification",
            "payload": notification
        })
        
        logger.info(f"发送通知给用户 {user_id}: {title}")
        return notification
    
    async def send_task_reminder(self, user_id: int, task_title: str, 
                               start_time: str, task_id: int):
        """发送任务提醒"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.TASK_REMINDER,
            title="📝 任务提醒",
            message=f"任务 \"{task_title}\" 即将开始 ({start_time})",
            priority=NotificationPriority.HIGH,
            data={
                "task_id": task_id,
                "task_title": task_title,
                "start_time": start_time,
                "action_url": f"/tasks/{task_id}"
            }
        )
    
    async def send_deadline_warning(self, user_id: int, task_title: str, 
                                  deadline: str, task_id: int):
        """发送截止时间警告"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.DEADLINE_APPROACHING,
            title="⏰ 截止时间提醒",
            message=f"任务 \"{task_title}\" 即将到期 ({deadline})",
            priority=NotificationPriority.URGENT,
            data={
                "task_id": task_id,
                "task_title": task_title,
                "deadline": deadline,
                "action_url": f"/tasks/{task_id}"
            }
        )
    
    async def send_plan_created(self, user_id: int, plan_title: str, plan_id: int):
        """发送计划创建通知"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.PLAN_CREATED,
            title="🎯 计划创建成功",
            message=f"新计划 \"{plan_title}\" 已创建",
            priority=NotificationPriority.NORMAL,
            data={
                "plan_id": plan_id,
                "plan_title": plan_title,
                "action_url": f"/plans/{plan_id}"
            }
        )
    
    async def send_file_uploaded(self, user_id: int, filename: str, file_id: str):
        """发送文件上传通知"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.FILE_UPLOADED,
            title="📎 文件上传成功",
            message=f"文件 \"{filename}\" 已上传",
            priority=NotificationPriority.LOW,
            data={
                "file_id": file_id,
                "filename": filename,
                "action_url": f"/files/{file_id}"
            }
        )
    
    async def send_system_message(self, user_id: int, title: str, message: str,
                                priority: NotificationPriority = NotificationPriority.NORMAL):
        """发送系统消息"""
        await self.send_notification(
            user_id=user_id,
            notification_type=NotificationType.SYSTEM_MESSAGE,
            title=title,
            message=message,
            priority=priority
        )
    
    def get_user_notifications(self, user_id: int, 
                             unread_only: bool = False,
                             limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户通知"""
        user_notifications = [
            n for n in self.notification_history 
            if n["user_id"] == user_id
        ]
        
        if unread_only:
            user_notifications = [n for n in user_notifications if not n["read"]]
        
        # 按时间倒序排列
        user_notifications.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return user_notifications[:limit]
    
    def mark_as_read(self, notification_id: str, user_id: int) -> bool:
        """标记通知为已读"""
        for notification in self.notification_history:
            if (notification["id"] == notification_id and 
                notification["user_id"] == user_id):
                notification["read"] = True
                return True
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """标记用户所有通知为已读"""
        count = 0
        for notification in self.notification_history:
            if (notification["user_id"] == user_id and 
                not notification["read"]):
                notification["read"] = True
                count += 1
        return count
    
    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """获取通知统计"""
        user_notifications = [
            n for n in self.notification_history 
            if n["user_id"] == user_id
        ]
        
        total = len(user_notifications)
        unread = len([n for n in user_notifications if not n["read"]])
        
        # 按类型统计
        by_type = {}
        for notification in user_notifications:
            ntype = notification["type"]
            if ntype not in by_type:
                by_type[ntype] = {"total": 0, "unread": 0}
            by_type[ntype]["total"] += 1
            if not notification["read"]:
                by_type[ntype]["unread"] += 1
        
        return {
            "total": total,
            "unread": unread,
            "by_type": by_type,
            "last_notification": user_notifications[0]["timestamp"] if user_notifications else None
        }
    
    async def cleanup_old_notifications(self, days: int = 30):
        """清理旧通知"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        original_count = len(self.notification_history)
        self.notification_history = [
            n for n in self.notification_history
            if datetime.fromisoformat(n["timestamp"]) > cutoff_date
        ]
        
        cleaned_count = original_count - len(self.notification_history)
        logger.info(f"清理了 {cleaned_count} 条旧通知")
        return cleaned_count

# 全局通知服务实例
notification_service = NotificationService()

# WebSocket连接管理器
connection_manager = notification_service.connection_manager 