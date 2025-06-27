import json
import time
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from config import PLAN_FILE_PATH
from models import DailyPlan

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.plan = None
        
    def load_plan(self, filename: str = PLAN_FILE_PATH) -> bool:
        """加载计划文件"""
        try:
            if not os.path.exists(filename):
                print(f"❌ 计划文件 {filename} 不存在")
                return False
                
            with open(filename, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)
            
            self.plan = DailyPlan(**plan_data)
            print(f"✅ 成功加载计划: {self.plan.plan_title}")
            return True
            
        except Exception as e:
            print(f"❌ 加载计划时出错: {e}")
            return False
    
    def notify_task(self, task_description: str, task_time: str, duration: int):
        """发送任务提醒"""
        current_time = datetime.now().strftime("%H:%M")
        print("\n" + "🔔" * 20)
        print(f"⏰ 任务提醒 - {current_time}")
        print("-" * 40)
        print(f"📌 任务: {task_description}")
        print(f"⏰ 计划时间: {task_time}")
        print(f"⏳ 预计用时: {duration}分钟")
        print("🔔" * 20 + "\n")
        
        # 播放提醒音（Windows系统）
        try:
            import winsound
            winsound.Beep(1000, 500)  # 频率1000Hz，持续500ms
        except ImportError:
            pass  # 非Windows系统跳过
    
    def setup_daily_reminders(self):
        """设置每日任务提醒"""
        if not self.plan:
            print("❌ 没有加载计划，无法设置提醒")
            return False
        
        print(f"📅 正在为 {self.plan.date} 设置任务提醒...")
        
        # 清除已有的任务
        self.scheduler.remove_all_jobs()
        
        # 为每个任务设置提醒
        for task in self.plan.tasks:
            try:
                # 解析时间
                hour, minute = map(int, task.time.split(':'))
                
                # 创建cron触发器（每天在指定时间执行）
                trigger = CronTrigger(hour=hour, minute=minute)
                
                # 添加任务
                self.scheduler.add_job(
                    func=self.notify_task,
                    trigger=trigger,
                    args=[task.description, task.time, task.duration],
                    id=f"task_{task.time}_{len(task.description)}",
                    name=f"提醒: {task.description[:20]}..."
                )
                
                print(f"✅ 已设置 {task.time} 的任务提醒: {task.description[:30]}...")
                
            except Exception as e:
                print(f"❌ 设置任务 {task.description} 的提醒时出错: {e}")
        
        return True
    
    def setup_daily_summary(self):
        """设置每日总结提醒"""
        if not self.plan:
            return
        
        # 在晚上9点提醒用户回顾今天的计划
        self.scheduler.add_job(
            func=self.daily_summary_reminder,
            trigger=CronTrigger(hour=21, minute=0),
            id="daily_summary",
            name="每日总结提醒"
        )
        print("✅ 已设置每日总结提醒 (21:00)")
    
    def daily_summary_reminder(self):
        """每日总结提醒"""
        print("\n" + "📊" * 20)
        print("🌙 每日总结时间到了！")
        print("-" * 40)
        print(f"📋 今日计划: {self.plan.plan_title}")
        print(f"📊 总任务数: {self.plan.total_tasks}")
        print("\n💭 请回顾一下今天的完成情况:")
        print("✅ 完成了哪些任务？")
        print("❌ 哪些任务没有完成？")
        print("💡 明天有什么需要改进的？")
        print("📊" * 20 + "\n")
    
    def setup_motivational_reminders(self):
        """设置激励提醒"""
        # 早上8点 - 激励开始
        self.scheduler.add_job(
            func=self.morning_motivation,
            trigger=CronTrigger(hour=8, minute=0),
            id="morning_motivation",
            name="早晨激励"
        )
        
        # 中午12点 - 中场休息
        self.scheduler.add_job(
            func=self.midday_break,
            trigger=CronTrigger(hour=12, minute=0),
            id="midday_break",
            name="午间提醒"
        )
        
        print("✅ 已设置激励提醒")
    
    def morning_motivation(self):
        """早晨激励"""
        print("\n🌅 早上好！新的一天开始了！")
        print(f"🎯 今日目标: {self.plan.goal}")
        print("💪 让我们一起实现今天的计划吧！\n")
    
    def midday_break(self):
        """午间提醒"""
        print("\n🍽️ 午休时间到了！")
        print("😌 记得休息一下，保持精力充沛！")
        print("🔄 下午继续加油！\n")
    
    def start_scheduler(self):
        """启动调度器"""
        if not self.plan:
            print("❌ 请先加载计划文件")
            return
        
        print("\n🚀 任务调度器启动中...")
        print(f"📋 计划: {self.plan.plan_title}")
        print(f"📅 日期: {self.plan.date}")
        print(f"📊 总任务数: {self.plan.total_tasks}")
        print("\n⏰ 调度器正在运行，按 Ctrl+C 停止")
        print("-" * 50)
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("\n👋 调度器已停止")
    
    def show_scheduled_jobs(self):
        """显示已安排的任务"""
        jobs = self.scheduler.get_jobs()
        if not jobs:
            print("📝 暂无已安排的任务")
            return
        
        print(f"\n📋 已安排的任务 (共{len(jobs)}个):")
        print("-" * 50)
        for job in jobs:
            print(f"⏰ {job.next_run_time.strftime('%H:%M')} - {job.name}")
        print("-" * 50)

def main():
    """主函数 - 启动调度器"""
    scheduler = TaskScheduler()
    
    # 加载计划
    if not scheduler.load_plan():
        print("无法启动调度器")
        return
    
    # 设置提醒
    scheduler.setup_daily_reminders()
    scheduler.setup_daily_summary()
    scheduler.setup_motivational_reminders()
    
    # 显示已安排的任务
    scheduler.show_scheduled_jobs()
    
    # 启动调度器
    scheduler.start_scheduler()

if __name__ == "__main__":
    main() 