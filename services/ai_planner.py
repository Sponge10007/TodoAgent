from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

class AIPlanner:
    """AI规划器，负责将大目标拆解为可执行的小任务"""
    
    def __init__(self):
        self.task_templates = {
            "健身": {
                "阶段1": {
                    "duration_weeks": 2,
                    "tasks": [
                        {"title": "制定运动计划", "description": "确定每周运动3-4次，每次30-45分钟", "duration": 30},
                        {"title": "准备运动装备", "description": "购买合适的运动鞋和运动服", "duration": 60},
                        {"title": "建立运动习惯", "description": "每天固定时间进行轻度运动", "duration": 30},
                        {"title": "记录运动日志", "description": "记录每次运动的内容和感受", "duration": 10}
                    ]
                },
                "阶段2": {
                    "duration_weeks": 2,
                    "tasks": [
                        {"title": "增加运动强度", "description": "逐步增加运动强度和时间", "duration": 45},
                        {"title": "尝试不同运动", "description": "尝试跑步、游泳、健身等不同运动", "duration": 60},
                        {"title": "制定营养计划", "description": "学习基本的营养知识", "duration": 30},
                        {"title": "调整作息时间", "description": "确保充足的睡眠和休息", "duration": 20}
                    ]
                },
                "阶段3": {
                    "duration_weeks": 2,
                    "tasks": [
                        {"title": "优化饮食结构", "description": "增加蛋白质摄入，减少垃圾食品", "duration": 45},
                        {"title": "制定详细计划", "description": "制定每周详细的运动和饮食计划", "duration": 60},
                        {"title": "寻找运动伙伴", "description": "找到志同道合的运动伙伴", "duration": 30},
                        {"title": "参加健身课程", "description": "参加专业的健身课程", "duration": 90}
                    ]
                },
                "阶段4": {
                    "duration_weeks": 2,
                    "tasks": [
                        {"title": "巩固运动习惯", "description": "保持稳定的运动频率和强度", "duration": 45},
                        {"title": "评估健身效果", "description": "测量体重、体脂等指标", "duration": 30},
                        {"title": "调整目标计划", "description": "根据进展调整下一步目标", "duration": 45},
                        {"title": "建立长期计划", "description": "制定长期的健身和健康计划", "duration": 60}
                    ]
                }
            },
            "学习": {
                "阶段1": {
                    "duration_weeks": 2,
                    "tasks": [
                        {"title": "确定学习目标", "description": "明确要学习的技能或知识", "duration": 30},
                        {"title": "制定学习计划", "description": "制定详细的学习时间表", "duration": 45},
                        {"title": "准备学习资源", "description": "收集相关的书籍、课程等资源", "duration": 60},
                        {"title": "建立学习环境", "description": "创造良好的学习环境", "duration": 30}
                    ]
                },
                "阶段2": {
                    "duration_weeks": 2,
                    "tasks": [
                        {"title": "开始基础学习", "description": "从基础知识开始学习", "duration": 60},
                        {"title": "记录学习笔记", "description": "整理和记录学习内容", "duration": 30},
                        {"title": "寻找学习伙伴", "description": "找到学习伙伴或加入学习小组", "duration": 30},
                        {"title": "实践应用", "description": "将学到的知识应用到实践中", "duration": 90}
                    ]
                }
            },
            "工作": {
                "阶段1": {
                    "duration_weeks": 2,
                    "tasks": [
                        {"title": "分析现状", "description": "分析当前工作状况和问题", "duration": 60},
                        {"title": "设定工作目标", "description": "明确工作改进的具体目标", "duration": 45},
                        {"title": "制定行动计划", "description": "制定详细的改进计划", "duration": 60},
                        {"title": "学习新技能", "description": "学习工作相关的新技能", "duration": 90}
                    ]
                }
            }
        }
    
    def plan_goal(self, goal_title: str, goal_description: str, category: str, 
                  start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """为指定目标制定详细的任务计划"""
        
        # 计算总周数
        total_weeks = (end_date - start_date).days // 7
        
        # 获取对应类别的任务模板
        if category in self.task_templates:
            template = self.task_templates[category]
        else:
            # 使用通用模板
            template = self._get_generic_template()
        
        tasks = []
        current_date = start_date
        
        # 为每个阶段创建任务
        for stage_name, stage_info in template.items():
            if current_date >= end_date:
                break
                
            stage_duration = stage_info["duration_weeks"]
            stage_end_date = min(current_date + timedelta(weeks=stage_duration), end_date)
            
            # 为阶段内的每个任务分配时间
            stage_tasks = stage_info["tasks"]
            days_per_task = (stage_end_date - current_date).days // len(stage_tasks)
            
            for i, task_template in enumerate(stage_tasks):
                task_due_date = current_date + timedelta(days=i * days_per_task)
                if task_due_date >= end_date:
                    break
                    
                task = {
                    "title": f"{stage_name}: {task_template['title']}",
                    "description": task_template['description'],
                    "due_date": task_due_date,
                    "priority": "medium",
                    "estimated_duration": task_template['duration']
                }
                tasks.append(task)
            
            current_date = stage_end_date
        
        return tasks
    
    def _get_generic_template(self) -> Dict[str, Any]:
        """获取通用任务模板"""
        return {
            "阶段1": {
                "duration_weeks": 2,
                "tasks": [
                    {"title": "目标分析", "description": "深入分析目标的具体要求", "duration": 60},
                    {"title": "制定计划", "description": "制定详细的执行计划", "duration": 90},
                    {"title": "准备资源", "description": "准备所需的资源和工具", "duration": 60},
                    {"title": "开始执行", "description": "开始执行计划的第一步", "duration": 45}
                ]
            },
            "阶段2": {
                "duration_weeks": 2,
                "tasks": [
                    {"title": "持续推进", "description": "按照计划持续推进", "duration": 60},
                    {"title": "记录进展", "description": "记录执行过程中的进展", "duration": 30},
                    {"title": "调整优化", "description": "根据进展调整计划", "duration": 45},
                    {"title": "寻求支持", "description": "寻找必要的支持和帮助", "duration": 30}
                ]
            }
        }
    
    def get_daily_tasks(self, all_tasks: List[Dict[str, Any]], target_date: datetime) -> List[Dict[str, Any]]:
        """获取指定日期的任务列表"""
        daily_tasks = []
        for task in all_tasks:
            task_date = task['due_date']
            if (task_date.year == target_date.year and 
                task_date.month == target_date.month and 
                task_date.day == target_date.day):
                daily_tasks.append(task)
        return daily_tasks
    
    def generate_motivation_message(self, goal_title: str, progress: float) -> str:
        """生成激励消息"""
        if progress < 25:
            return f"加油！{goal_title}才刚刚开始，每一步都是进步。今天也要继续努力哦！"
        elif progress < 50:
            return f"太棒了！{goal_title}已经完成了{progress:.1f}%，你已经走过了最困难的部分。继续保持！"
        elif progress < 75:
            return f"了不起！{goal_title}已经完成了{progress:.1f}%，胜利就在眼前。坚持就是胜利！"
        else:
            return f"太厉害了！{goal_title}已经完成了{progress:.1f}%，你马上就要成功了。最后冲刺！" 