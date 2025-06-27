'''
Author: userName userEmail
Date: 2025-06-26 22:39:34
LastEditors: userName userEmail
LastEditTime: 2025-06-27 01:26:11
FilePath: \agent\life_manager_agent_qwen.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
#!/usr/bin/env python3
"""
生活管家AI Agent - 通义千问版本（国内用户友好）
增强版：包含记忆系统和错误处理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import requests
from dotenv import load_dotenv
import time

from models import DailyPlan, Task, WeeklyPlan

# 加载环境变量
load_dotenv()

class MemorySystem:
    """记忆系统 - 管理短期、长期和工作记忆"""
    
    def __init__(self):
        self.short_term_memory = []  # 最近对话历史
        self.long_term_memory = self._load_long_term_memory()  # 用户偏好和历史数据
        self.working_memory = {}  # 当前会话状态
        self.conversation_history = []  # 对话历史
        
    def _load_long_term_memory(self) -> Dict[str, Any]:
        """加载长期记忆"""
        memory_file = "memory_storage.json"
        try:
            if os.path.exists(memory_file):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载记忆文件失败: {e}")
        
        # 默认记忆结构
        return {
            "user_preferences": {
                "preferred_time_slots": [],
                "common_goals": [],
                "productivity_patterns": {},
                "favorite_activities": []
            },
            "plan_history": [],
            "completion_stats": {
                "total_plans": 0,
                "completed_tasks": 0,
                "success_rate": 0.0
            }
        }
    
    def save_long_term_memory(self):
        """保存长期记忆到文件"""
        try:
            with open("memory_storage.json", 'w', encoding='utf-8') as f:
                json.dump(self.long_term_memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆失败: {e}")
    
    def add_conversation(self, user_input: str, agent_response: str):
        """添加对话到短期记忆"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "agent": agent_response
        }
        self.short_term_memory.append(conversation)
        self.conversation_history.append(conversation)
        
        # 保持短期记忆在合理范围内（最近10条）
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)
    
    def archive_plan(self, plan: DailyPlan, completion_status: Dict[str, bool] = None):
        """归档计划到长期记忆"""
        plan_record = {
            "date": plan.date,
            "goal": plan.goal,
            "total_tasks": plan.total_tasks,
            "estimated_time": plan.estimated_total_time,
            "completion_status": completion_status or {},
            "archived_at": datetime.now().isoformat()
        }
        
        self.long_term_memory["plan_history"].append(plan_record)
        self.long_term_memory["completion_stats"]["total_plans"] += 1
        
        # 分析用户偏好
        self._analyze_user_preferences(plan)
        self.save_long_term_memory()
    
    def _analyze_user_preferences(self, plan: DailyPlan):
        """分析用户偏好模式"""
        preferences = self.long_term_memory["user_preferences"]
        
        # 分析常见目标类型
        goal_keywords = plan.goal.lower().split()
        for keyword in goal_keywords:
            if keyword not in preferences["common_goals"]:
                preferences["common_goals"].append(keyword)
        
        # 保持列表长度合理
        if len(preferences["common_goals"]) > 20:
            preferences["common_goals"] = preferences["common_goals"][-20:]
    
    def get_user_context(self) -> str:
        """获取用户上下文信息用于AI生成"""
        context = []
        
        # 添加历史偏好
        if self.long_term_memory["user_preferences"]["common_goals"]:
            common_goals = ", ".join(self.long_term_memory["user_preferences"]["common_goals"][-5:])
            context.append(f"用户常见目标关键词: {common_goals}")
        
        # 添加最近对话
        if self.short_term_memory:
            recent_conversation = self.short_term_memory[-1]
            context.append(f"最近交互: {recent_conversation['user']}")
        
        return "\n".join(context) if context else "无历史上下文"

class LifeManagerAgentQwen:
    """使用通义千问的生活管家AI Agent - 增强版"""
    
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")  # 通义千问API密钥
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.memory_system = MemorySystem()  # 记忆系统
        
        if not self.api_key:
            print("❌ 请设置 DASHSCOPE_API_KEY 环境变量")
            print("获取地址: https://dashscope.console.aliyun.com/apiKey")
    
    def _call_qwen_with_retry(self, prompt: str, max_retries: int = 3, timeout: int = 60) -> str:
        """调用通义千问API，包含重试机制"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "qwen-turbo",  # 使用快速模型
            "input": {
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "temperature": 0.1,
                "max_tokens": 2000
            }
        }
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 尝试调用API (第 {attempt + 1}/{max_retries} 次)...")
                
                response = requests.post(
                    self.base_url, 
                    headers=headers, 
                    json=data, 
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['output']['text']
                else:
                    print(f"API错误: {response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        print(f"⏳ 等待 {(attempt + 1) * 2} 秒后重试...")
                        time.sleep((attempt + 1) * 2)
                    
            except requests.Timeout:
                print(f"❌ API调用超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"⏳ 等待 {(attempt + 1) * 3} 秒后重试...")
                    time.sleep((attempt + 1) * 3)
                    
            except Exception as e:
                print(f"❌ API调用失败: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ 等待 {(attempt + 1) * 2} 秒后重试...")
                    time.sleep((attempt + 1) * 2)
        
        print("❌ 所有重试尝试都失败了")
        return None
    
    def create_daily_plan(self, goal_description: str, time_preference: str = "") -> Optional[DailyPlan]:
        """快速创建每日计划 - 增强版，包含记忆上下文"""
        if not self.api_key:
            print("❌ 缺少API密钥")
            return None
        
        print("🤖 正在使用通义千问制定计划（包含个人偏好分析）...")
        
        # 获取用户上下文
        user_context = self.memory_system.get_user_context()
        
        # 智能识别用户意图
        is_multi_day_goal = any(keyword in goal_description.lower() for keyword in 
                               ["30天", "一个月", "几周", "长期", "持续", "阶段"])
        
        if is_multi_day_goal:
            day_context = "（注意：这是一个长期目标的第一天计划）"
            plan_title_prefix = "第1天："
        else:
            day_context = ""
            plan_title_prefix = ""
        
        prompt = f"""
请根据以下信息制定一个详细的今日计划{day_context}，以JSON格式输出：

目标: {goal_description}
时间偏好: {time_preference if time_preference else "无特殊偏好"}
日期: {datetime.now().strftime('%Y-%m-%d')}

用户历史上下文:
{user_context}

要求：
1. 只制定今天一天的计划，包含今天可以执行的具体任务
2. 如果是长期目标，请制定第一天的启动计划
3. 任务要实用且可执行，避免过于宽泛的描述
4. 包含具体的时间段、任务描述、持续时间、优先级和理由
5. 总任务数控制在4-6个之间
6. 确保输出标准JSON格式

JSON格式示例：
{{
  "plan_title": "{plan_title_prefix}AI Agent项目实践计划",
  "goal": "{goal_description}",
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "total_tasks": 5,
  "estimated_total_time": 300,
  "tasks": [
    {{
      "time": "09:00-10:30",
      "description": "环境搭建：安装Python、创建虚拟环境",
      "duration": 90,
      "priority": "高",
      "reason": "良好的开发环境是项目成功的基础"
    }}
  ]
}}

请生成今天的具体可执行计划：
"""
        
        try:
            response = self._call_qwen_with_retry(prompt)
            if not response:
                return self._create_fallback_plan(goal_description)
            
            # 记录对话
            self.memory_system.add_conversation(goal_description, response[:100] + "...")
            
            # 提取JSON部分
            json_content = self._extract_json_from_response(response)
            
            # 检查响应长度，防止生成过长的计划
            if len(json_content) > 3000:
                print("⚠️ AI响应过长，可能生成了多日计划，使用备用方案")
                return self._create_fallback_plan(goal_description)
            
            # 解析JSON
            plan_data = json.loads(json_content)
            plan = DailyPlan(**plan_data)
            print("✅ 计划制定完成！")
            
            # 更新工作记忆
            self.memory_system.working_memory["current_plan"] = plan
            
            return plan
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print("🔄 尝试修复JSON格式...")
            
            # 尝试修复JSON
            fixed_json = self._fix_json_errors(json_content)
            if fixed_json:
                try:
                    plan_data = json.loads(fixed_json)
                    plan = DailyPlan(**plan_data)
                    print("✅ JSON修复成功，计划制定完成！")
                    self.memory_system.working_memory["current_plan"] = plan
                    return plan
                except:
                    pass
            
            print("🔄 JSON修复失败，使用备用计划...")
            return self._create_fallback_plan(goal_description)
        except Exception as e:
            print(f"❌ 创建计划失败: {e}")
            return self._create_fallback_plan(goal_description)
    
    def _extract_json_from_response(self, response: str) -> str:
        """从响应中提取JSON内容"""
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            return response[json_start:json_end].strip()
        elif "{" in response and "}" in response:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            return response[json_start:json_end]
        else:
            return response
    
    def _fix_json_errors(self, json_str: str) -> str:
        """修复常见的JSON错误"""
        try:
            # 移除可能的多余逗号
            lines = json_str.split('\n')
            fixed_lines = []
            
            for i, line in enumerate(lines):
                # 如果这行以逗号结尾，但下一行是}或]，则移除逗号
                if line.strip().endswith(','):
                    next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                    if next_line.startswith('}') or next_line.startswith(']'):
                        line = line.rstrip().rstrip(',')
                fixed_lines.append(line)
            
            return '\n'.join(fixed_lines)
        except:
            return json_str
    
    def _create_fallback_plan(self, goal_description: str) -> DailyPlan:
        """创建备用计划（当API失败时）- 改进版"""
        print("🔄 API失败，使用智能备用计划...")
        
        # 智能分析目标类型，生成对应的备用计划
        goal_lower = goal_description.lower()
        
        if any(keyword in goal_lower for keyword in ["ai", "agent", "编程", "开发", "代码"]):
            return self._create_ai_project_fallback(goal_description)
        elif any(keyword in goal_lower for keyword in ["学习", "python", "技术", "教程"]):
            return self._create_learning_fallback(goal_description)
        elif any(keyword in goal_lower for keyword in ["健身", "运动", "锻炼", "身体"]):
            return self._create_fitness_fallback(goal_description)
        elif any(keyword in goal_lower for keyword in ["工作", "面试", "职业", "简历"]):
            return self._create_career_fallback(goal_description)
        else:
            return self._create_general_fallback(goal_description)
    
    def _create_ai_project_fallback(self, goal_description: str) -> DailyPlan:
        """AI项目相关的备用计划"""
        return DailyPlan(
            plan_title="AI Agent项目实践 - 启动计划",
            goal=goal_description,
            date=datetime.now().strftime('%Y-%m-%d'),
            total_tasks=6,
            estimated_total_time=360,
            tasks=[
                Task(
                    time="09:00-10:30",
                    description="环境搭建：安装Python、pip、创建虚拟环境",
                    duration=90,
                    priority="高",
                    reason="良好的开发环境是项目成功的基础"
                ),
                Task(
                    time="10:45-12:00",
                    description="学习LangChain/LlamaIndex基础概念和架构",
                    duration=75,
                    priority="高",
                    reason="理解AI Agent框架的核心概念"
                ),
                Task(
                    time="14:00-15:30",
                    description="实践：创建第一个简单的聊天机器人",
                    duration=90,
                    priority="高",
                    reason="通过实践加深理解，建立信心"
                ),
                Task(
                    time="15:45-16:30",
                    description="阅读官方文档和最佳实践案例",
                    duration=45,
                    priority="中",
                    reason="学习行业标准和最佳实践"
                ),
                Task(
                    time="16:30-17:15",
                    description="设计项目架构和30天学习路径",
                    duration=45,
                    priority="中",
                    reason="制定清晰的学习计划，确保持续进步"
                ),
                Task(
                    time="19:00-20:00",
                    description="总结今日成果，记录学习笔记",
                    duration=60,
                    priority="中",
                    reason="反思和记录有助于知识巩固"
                )
            ]
        )
    
    def _create_learning_fallback(self, goal_description: str) -> DailyPlan:
        """学习相关的备用计划"""
        return DailyPlan(
            plan_title="学习计划 - 第一天",
            goal=goal_description,
            date=datetime.now().strftime('%Y-%m-%d'),
            total_tasks=5,
            estimated_total_time=300,
            tasks=[
                Task(
                    time="09:00-10:30",
                    description="收集学习资源：教程、文档、视频课程",
                    duration=90,
                    priority="高",
                    reason="优质的学习资源是高效学习的前提"
                ),
                Task(
                    time="10:45-12:00",
                    description="学习基础概念和核心理论",
                    duration=75,
                    priority="高",
                    reason="扎实的理论基础是实践的根本"
                ),
                Task(
                    time="14:00-15:30",
                    description="完成第一个练习项目或作业",
                    duration=90,
                    priority="高",
                    reason="实践是检验理解程度的最佳方法"
                ),
                Task(
                    time="15:45-16:30",
                    description="整理学习笔记，标记重点和疑问",
                    duration=45,
                    priority="中",
                    reason="整理笔记有助于知识体系化"
                ),
                Task(
                    time="19:00-20:00",
                    description="制定后续学习计划和时间表",
                    duration=60,
                    priority="中",
                    reason="有计划的学习更加高效"
                )
            ]
        )
    
    def _create_fitness_fallback(self, goal_description: str) -> DailyPlan:
        """健身相关的备用计划"""
        return DailyPlan(
            plan_title="健身计划 - 启动日",
            goal=goal_description,
            date=datetime.now().strftime('%Y-%m-%d'),
            total_tasks=5,
            estimated_total_time=270,
            tasks=[
                Task(
                    time="07:00-07:30",
                    description="身体评估：测量体重、体脂率、基础数据",
                    duration=30,
                    priority="中",
                    reason="了解起始状态，便于追踪进度"
                ),
                Task(
                    time="08:00-09:00",
                    description="制定健身计划：确定运动类型和强度",
                    duration=60,
                    priority="高",
                    reason="科学的计划是健身成功的关键"
                ),
                Task(
                    time="09:30-10:30",
                    description="第一次训练：基础有氧运动和拉伸",
                    duration=60,
                    priority="高",
                    reason="从基础开始，避免运动伤害"
                ),
                Task(
                    time="18:00-19:00",
                    description="轻度力量训练：自重训练或轻器械",
                    duration=60,
                    priority="高",
                    reason="力量训练有助于提升基础代谢"
                ),
                Task(
                    time="21:00-22:00",
                    description="总结今日运动感受，调整明日计划",
                    duration=60,
                    priority="中",
                    reason="及时调整计划，确保可持续性"
                )
            ]
        )
    
    def _create_career_fallback(self, goal_description: str) -> DailyPlan:
        """职业发展相关的备用计划"""
        return DailyPlan(
            plan_title="职业发展计划 - 第一步",
            goal=goal_description,
            date=datetime.now().strftime('%Y-%m-%d'),
            total_tasks=5,
            estimated_total_time=300,
            tasks=[
                Task(
                    time="09:00-10:30",
                    description="简历更新：整理工作经历和技能清单",
                    duration=90,
                    priority="高",
                    reason="完善的简历是求职的基础工具"
                ),
                Task(
                    time="10:45-12:00",
                    description="技能评估：分析现有技能和市场需求差距",
                    duration=75,
                    priority="高",
                    reason="了解差距才能制定针对性的提升计划"
                ),
                Task(
                    time="14:00-15:30",
                    description="网络建设：更新LinkedIn，联系行业人士",
                    duration=90,
                    priority="中",
                    reason="人脉网络是职业发展的重要资源"
                ),
                Task(
                    time="15:45-16:30",
                    description="行业研究：了解目标公司和岗位要求",
                    duration=45,
                    priority="高",
                    reason="知己知彼，提高成功概率"
                ),
                Task(
                    time="19:00-20:00",
                    description="制定学习计划：确定需要提升的技能",
                    duration=60,
                    priority="中",
                    reason="持续学习是职业发展的动力"
                )
            ]
        )
    
    def _create_general_fallback(self, goal_description: str) -> DailyPlan:
        """通用备用计划"""
        return DailyPlan(
            plan_title=f"目标实现计划：{goal_description[:20]}...",
            goal=goal_description,
            date=datetime.now().strftime('%Y-%m-%d'),
            total_tasks=4,
            estimated_total_time=240,
            tasks=[
                Task(
                    time="09:00-10:30",
                    description="目标分析：将大目标分解为具体可执行的小步骤",
                    duration=90,
                    priority="高",
                    reason="明确的行动步骤是实现目标的前提"
                ),
                Task(
                    time="10:45-12:00",
                    description="资源准备：收集实现目标所需的工具和信息",
                    duration=75,
                    priority="高",
                    reason="充分的准备能提高执行效率"
                ),
                Task(
                    time="14:00-15:30",
                    description="开始执行：完成第一个具体的行动步骤",
                    duration=90,
                    priority="高",
                    reason="立即行动是克服拖延的最好方法"
                ),
                Task(
                    time="16:00-17:00",
                    description="总结回顾：评估进度，调整后续计划",
                    duration=60,
                    priority="中",
                    reason="及时回顾和调整确保方向正确"
                )
            ]
        )
    
    def display_plan(self, plan: DailyPlan):
        """美观地显示计划"""
        print("\n" + "="*50)
        print(f"📋 {plan.plan_title}")
        print("="*50)
        print(f"🎯 目标: {plan.goal}")
        print(f"📅 日期: {plan.date}")
        print(f"📊 总任务数: {plan.total_tasks}")
        print(f"⏱️  预计总时间: {plan.estimated_total_time}分钟")
        print("\n📝 详细任务安排:")
        print("-"*30)
        
        for i, task in enumerate(plan.tasks, 1):
            print(f"{i}. ⏰ {task.time} | 🔥 {task.priority}")
            print(f"   📌 {task.description}")
            print(f"   💡 {task.reason}")
            print(f"   ⏳ 预计用时: {task.duration}分钟")
            print()
        
        print("="*50)
    
    def save_plan(self, plan: DailyPlan, filename: str = "plan_qwen.json"):
        """保存计划到文件并归档到记忆系统"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(plan.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"📁 计划已保存到 {filename}")
            
            # 归档到记忆系统
            self.memory_system.archive_plan(plan)
            print("💾 计划已归档到记忆系统")
            
        except Exception as e:
            print(f"保存计划时出错: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        return {
            "short_term_conversations": len(self.memory_system.short_term_memory),
            "total_plans": self.memory_system.long_term_memory["completion_stats"]["total_plans"],
            "common_goals": self.memory_system.long_term_memory["user_preferences"]["common_goals"][-5:],
            "working_memory_active": bool(self.memory_system.working_memory)
        }
    
    def display_memory_stats(self):
        """显示记忆系统状态"""
        stats = self.get_memory_stats()
        print("\n" + "🧠" * 20)
        print("🧠 记忆系统状态")
        print("🧠" * 20)
        print(f"💭 短期记忆对话数: {stats['short_term_conversations']}")
        print(f"📊 历史计划总数: {stats['total_plans']}")
        print(f"🎯 常见目标: {', '.join(stats['common_goals']) if stats['common_goals'] else '暂无'}")
        print(f"⚡ 工作记忆活跃: {'是' if stats['working_memory_active'] else '否'}")
        print("🧠" * 20 + "\n")
    
    def modify_plan(self, current_plan: DailyPlan, modification_request: str) -> Optional[DailyPlan]:
        """修改现有计划"""
        if not self.api_key:
            print("❌ 缺少API密钥")
            return None
        
        print("🔄 正在修改计划...")
        
        prompt = f"""
请根据以下修改要求调整计划：

当前计划：
{current_plan.model_dump_json(indent=2)}

修改要求：{modification_request}

请输出修改后的完整计划，保持JSON格式：
"""
        
        try:
            response = self._call_qwen_with_retry(prompt)
            if not response:
                return None
            
            # 提取JSON部分
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_content = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_content = response[json_start:json_end]
            else:
                json_content = response
            
            # 解析JSON
            plan_data = json.loads(json_content)
            plan = DailyPlan(**plan_data)
            print("✅ 计划修改完成！")
            return plan
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 修改计划失败: {e}")
            return None

    def create_weekly_plan(self, goal_description: str, time_preference: str = "") -> Optional[WeeklyPlan]:
        """创建7天计划"""
        if not self.api_key:
            print("❌ 缺少API密钥")
            return None
        
        print("🤖 正在制定7天计划...")
        
        # 获取用户上下文
        user_context = self.memory_system.get_user_context()
        
        # 计算日期范围
        start_date = datetime.now()
        end_date = start_date + timedelta(days=6)
        
        prompt = f"""
请根据以下信息制定一个详细的7天计划，以JSON格式输出：

目标: {goal_description}
时间偏好: {time_preference if time_preference else "无特殊偏好"}
开始日期: {start_date.strftime('%Y-%m-%d')}
结束日期: {end_date.strftime('%Y-%m-%d')}

用户历史上下文:
{user_context}

要求：
1. 制定连续7天的计划，每天2-4个核心任务
2. 任务要循序渐进，符合学习/实践规律
3. 考虑工作日和周末的不同安排
4. 每个任务包含具体时间、描述、持续时间、优先级和理由
5. 确保输出标准JSON格式

JSON格式示例：
{{
  "plan_title": "AI Agent项目7天实践计划",
  "main_goal": "{goal_description}",
  "start_date": "{start_date.strftime('%Y-%m-%d')}",
  "end_date": "{end_date.strftime('%Y-%m-%d')}",
  "daily_plans": [
    {{
      "plan_title": "第1天：环境搭建和基础学习",
      "goal": "搭建开发环境，学习基础概念",
      "date": "{start_date.strftime('%Y-%m-%d')}",
      "total_tasks": 3,
      "estimated_total_time": 240,
      "tasks": [
        {{
          "time": "09:00-10:30",
          "description": "环境搭建：安装Python、pip、创建虚拟环境",
          "duration": 90,
          "priority": "高",
          "reason": "良好的开发环境是项目成功的基础"
        }}
      ]
    }}
  ]
}}

请生成完整的7天计划：
"""
        
        try:
            response = self._call_qwen_with_retry(prompt, timeout=45)
            if not response:
                return self._create_weekly_fallback_plan(goal_description)
            
            # 记录对话
            self.memory_system.add_conversation(f"7天计划: {goal_description}", response[:100] + "...")
            
            # 提取JSON部分
            json_content = self._extract_json_from_response(response)
            
            # 检查响应长度
            if len(json_content) > 15000:
                print("⚠️ AI响应过长，使用备用7天计划")
                return self._create_weekly_fallback_plan(goal_description)
            
            # 解析JSON
            plan_data = json.loads(json_content)
            
            # 验证daily_plans格式
            if 'daily_plans' in plan_data:
                for daily_plan_data in plan_data['daily_plans']:
                    # 确保每个daily_plan都有必需的字段
                    if 'tasks' not in daily_plan_data:
                        daily_plan_data['tasks'] = []
                    if 'total_tasks' not in daily_plan_data:
                        daily_plan_data['total_tasks'] = len(daily_plan_data['tasks'])
                    if 'estimated_total_time' not in daily_plan_data:
                        daily_plan_data['estimated_total_time'] = sum(task.get('duration', 60) for task in daily_plan_data['tasks'])
            
            weekly_plan = WeeklyPlan(**plan_data)
            print("✅ 7天计划制定完成！")
            
            # 更新工作记忆
            self.memory_system.working_memory["current_weekly_plan"] = weekly_plan
            
            return weekly_plan
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print("🔄 使用备用7天计划...")
            return self._create_weekly_fallback_plan(goal_description)
        except Exception as e:
            print(f"❌ 创建7天计划失败: {e}")
            return self._create_weekly_fallback_plan(goal_description)
    
    def _create_weekly_fallback_plan(self, goal_description: str) -> WeeklyPlan:
        """创建备用7天计划"""
        print("🔄 生成智能备用7天计划...")
        
        start_date = datetime.now()
        goal_lower = goal_description.lower()
        
        # 根据目标类型生成不同的7天计划
        if any(keyword in goal_lower for keyword in ["ai", "agent", "编程", "开发", "代码"]):
            return self._create_ai_weekly_fallback(goal_description, start_date)
        elif any(keyword in goal_lower for keyword in ["学习", "python", "技术", "教程"]):
            return self._create_learning_weekly_fallback(goal_description, start_date)
        elif any(keyword in goal_lower for keyword in ["健身", "运动", "锻炼", "身体"]):
            return self._create_fitness_weekly_fallback(goal_description, start_date)
        else:
            return self._create_general_weekly_fallback(goal_description, start_date)
    
    def _create_ai_weekly_fallback(self, goal_description: str, start_date: datetime) -> WeeklyPlan:
        """AI项目7天备用计划"""
        daily_plans = []
        
        # 第1天：环境搭建
        daily_plans.append(DailyPlan(
            plan_title="第1天：环境搭建和基础学习",
            goal="搭建AI Agent开发环境",
            date=(start_date + timedelta(days=0)).strftime('%Y-%m-%d'),
            total_tasks=3,
            estimated_total_time=240,
            tasks=[
                Task(time="09:00-10:30", description="安装Python、pip、创建虚拟环境", duration=90, priority="高", reason="开发环境是基础"),
                Task(time="14:00-15:30", description="学习LangChain基础概念", duration=90, priority="高", reason="理解框架核心"),
                Task(time="19:00-20:00", description="阅读官方文档和示例", duration=60, priority="中", reason="获取实践指导")
            ]
        ))
        
        # 第2天：第一个项目
        daily_plans.append(DailyPlan(
            plan_title="第2天：创建第一个AI Agent",
            goal="完成简单的聊天机器人",
            date=(start_date + timedelta(days=1)).strftime('%Y-%m-%d'),
            total_tasks=3,
            estimated_total_time=270,
            tasks=[
                Task(time="09:00-10:30", description="创建基础聊天机器人框架", duration=90, priority="高", reason="实践基础概念"),
                Task(time="14:00-16:00", description="集成LLM模型和简单对话逻辑", duration=120, priority="高", reason="核心功能实现"),
                Task(time="19:00-20:00", description="测试和调试聊天机器人", duration=60, priority="中", reason="确保功能正常")
            ]
        ))
        
        # 第3天：功能扩展
        daily_plans.append(DailyPlan(
            plan_title="第3天：功能扩展和优化",
            goal="为AI Agent添加更多功能",
            date=(start_date + timedelta(days=2)).strftime('%Y-%m-%d'),
            total_tasks=3,
            estimated_total_time=240,
            tasks=[
                Task(time="09:00-10:30", description="添加记忆功能和上下文管理", duration=90, priority="高", reason="提升对话连贯性"),
                Task(time="14:00-15:30", description="实现简单的工具调用功能", duration=90, priority="高", reason="增强Agent能力"),
                Task(time="19:00-20:00", description="优化响应速度和错误处理", duration=60, priority="中", reason="提升用户体验")
            ]
        ))
        
        # 第4天：高级特性
        daily_plans.append(DailyPlan(
            plan_title="第4天：高级特性开发",
            goal="实现复杂的AI Agent功能",
            date=(start_date + timedelta(days=3)).strftime('%Y-%m-%d'),
            total_tasks=3,
            estimated_total_time=270,
            tasks=[
                Task(time="09:00-10:30", description="学习和实现RAG（检索增强生成）", duration=90, priority="高", reason="提升知识处理能力"),
                Task(time="14:00-16:00", description="集成外部API和数据源", duration=120, priority="高", reason="扩展Agent功能边界"),
                Task(time="19:00-20:00", description="实现多轮对话和状态管理", duration=60, priority="中", reason="提升交互体验")
            ]
        ))
        
        # 第5天：项目整合
        daily_plans.append(DailyPlan(
            plan_title="第5天：项目整合和测试",
            goal="整合所有功能并进行全面测试",
            date=(start_date + timedelta(days=4)).strftime('%Y-%m-%d'),
            total_tasks=4,
            estimated_total_time=300,
            tasks=[
                Task(time="09:00-10:30", description="代码重构和模块化整理", duration=90, priority="高", reason="提升代码质量"),
                Task(time="11:00-12:00", description="编写单元测试和集成测试", duration=60, priority="高", reason="确保功能稳定"),
                Task(time="14:00-15:30", description="性能优化和内存管理", duration=90, priority="中", reason="提升运行效率"),
                Task(time="19:00-20:00", description="用户界面改进和体验优化", duration=60, priority="中", reason="提升易用性")
            ]
        ))
        
        # 第6天：部署和文档
        daily_plans.append(DailyPlan(
            plan_title="第6天：部署和文档编写",
            goal="准备项目部署和编写文档",
            date=(start_date + timedelta(days=5)).strftime('%Y-%m-%d'),
            total_tasks=3,
            estimated_total_time=240,
            tasks=[
                Task(time="09:00-10:30", description="编写项目文档和使用说明", duration=90, priority="高", reason="便于他人理解使用"),
                Task(time="14:00-15:30", description="准备部署环境和配置", duration=90, priority="高", reason="实现项目上线"),
                Task(time="19:00-20:00", description="制作演示和展示材料", duration=60, priority="中", reason="准备项目展示")
            ]
        ))
        
        # 第7天：总结和规划
        daily_plans.append(DailyPlan(
            plan_title="第7天：项目总结和未来规划",
            goal="总结学习成果并规划下一步",
            date=(start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            total_tasks=3,
            estimated_total_time=180,
            tasks=[
                Task(time="09:00-10:30", description="项目成果展示和demo演示", duration=90, priority="高", reason="验证学习成果"),
                Task(time="14:00-15:00", description="总结经验教训和技术要点", duration=60, priority="中", reason="巩固学习成果"),
                Task(time="19:00-20:00", description="制定后续深入学习计划", duration=60, priority="中", reason="持续技能提升")
            ]
        ))
        
        return WeeklyPlan(
            plan_title="AI Agent项目7天深度实践计划",
            main_goal=goal_description,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=(start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            daily_plans=daily_plans
        )
    
    def _create_learning_weekly_fallback(self, goal_description: str, start_date: datetime) -> WeeklyPlan:
        """学习类7天备用计划"""
        daily_plans = []
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            day_name = ["第1天", "第2天", "第3天", "第4天", "第5天", "第6天", "第7天"][day]
            
            if day < 2:  # 前两天：基础学习
                daily_plans.append(DailyPlan(
                    plan_title=f"{day_name}：基础知识学习",
                    goal=f"掌握核心概念（第{day+1}部分）",
                    date=current_date.strftime('%Y-%m-%d'),
                    total_tasks=3,
                    estimated_total_time=210,
                    tasks=[
                        Task(time="09:00-10:30", description="理论学习：核心概念和原理", duration=90, priority="高", reason="建立理论基础"),
                        Task(time="14:00-15:30", description="视频教程学习和笔记整理", duration=90, priority="高", reason="多角度理解概念"),
                        Task(time="19:00-19:30", description="复习今日内容，预习明日内容", duration=30, priority="中", reason="巩固记忆")
                    ]
                ))
            elif day < 5:  # 中间三天：实践练习
                daily_plans.append(DailyPlan(
                    plan_title=f"{day_name}：实践练习",
                    goal=f"完成实践项目（第{day-1}阶段）",
                    date=current_date.strftime('%Y-%m-%d'),
                    total_tasks=3,
                    estimated_total_time=240,
                    tasks=[
                        Task(time="09:00-10:30", description="完成练习项目编码部分", duration=90, priority="高", reason="实践巩固理论"),
                        Task(time="14:00-15:30", description="调试和优化代码", duration=90, priority="高", reason="提升编程技能"),
                        Task(time="19:00-20:00", description="记录问题和解决方案", duration=60, priority="中", reason="积累经验")
                    ]
                ))
            else:  # 最后两天：总结和扩展
                daily_plans.append(DailyPlan(
                    plan_title=f"{day_name}：总结和扩展",
                    goal="总结学习成果，规划进阶路径",
                    date=current_date.strftime('%Y-%m-%d'),
                    total_tasks=3,
                    estimated_total_time=180,
                    tasks=[
                        Task(time="09:00-10:30", description="整理学习笔记和项目成果", duration=90, priority="中", reason="系统化知识结构"),
                        Task(time="14:00-15:00", description="探索高级主题和扩展知识", duration=60, priority="中", reason="拓展学习边界"),
                        Task(time="19:00-19:30", description="制定后续学习计划", duration=30, priority="中", reason="持续改进")
                    ]
                ))
        
        return WeeklyPlan(
            plan_title="7天深度学习计划",
            main_goal=goal_description,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=(start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            daily_plans=daily_plans
        )
    
    def _create_fitness_weekly_fallback(self, goal_description: str, start_date: datetime) -> WeeklyPlan:
        """健身类7天备用计划"""
        daily_plans = []
        
        fitness_schedule = [
            ("第1天：适应期", "轻度有氧运动和拉伸"),
            ("第2天：力量训练", "上肢力量训练"),
            ("第3天：有氧运动", "中等强度有氧运动"),
            ("第4天：力量训练", "下肢力量训练"),
            ("第5天：综合训练", "全身综合训练"),
            ("第6天：恢复训练", "瑜伽和拉伸"),
            ("第7天：总结评估", "测试和计划调整")
        ]
        
        for day, (title, focus) in enumerate(fitness_schedule):
            current_date = start_date + timedelta(days=day)
            
            daily_plans.append(DailyPlan(
                plan_title=title,
                goal=focus,
                date=current_date.strftime('%Y-%m-%d'),
                total_tasks=3,
                estimated_total_time=120,
                tasks=[
                    Task(time="07:00-07:30", description="热身运动", duration=30, priority="高", reason="预防运动伤害"),
                    Task(time="08:00-09:00", description=focus, duration=60, priority="高", reason="核心训练内容"),
                    Task(time="21:00-21:30", description="放松拉伸", duration=30, priority="中", reason="促进恢复")
                ]
            ))
        
        return WeeklyPlan(
            plan_title="7天健身启动计划",
            main_goal=goal_description,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=(start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            daily_plans=daily_plans
        )
    
    def _create_general_weekly_fallback(self, goal_description: str, start_date: datetime) -> WeeklyPlan:
        """通用7天备用计划"""
        daily_plans = []
        
        for day in range(7):
            current_date = start_date + timedelta(days=day)
            day_name = f"第{day+1}天"
            
            daily_plans.append(DailyPlan(
                plan_title=f"{day_name}：目标推进",
                goal=f"推进目标实现（阶段{day+1}）",
                date=current_date.strftime('%Y-%m-%d'),
                total_tasks=3,
                estimated_total_time=180,
                tasks=[
                    Task(time="09:00-10:30", description=f"执行核心任务（第{day+1}部分）", duration=90, priority="高", reason="推进主要目标"),
                    Task(time="14:00-15:00", description="回顾进度，调整策略", duration=60, priority="中", reason="确保方向正确"),
                    Task(time="19:00-19:30", description="总结今日成果", duration=30, priority="中", reason="记录进展")
                ]
            ))
        
        return WeeklyPlan(
            plan_title="7天目标实现计划",
            main_goal=goal_description,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=(start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
            daily_plans=daily_plans
        )
    
    def display_weekly_plan(self, weekly_plan: WeeklyPlan):
        """美观地显示7天计划"""
        print("\n" + "="*60)
        print(f"📅 {weekly_plan.plan_title}")
        print("="*60)
        print(f"🎯 主要目标: {weekly_plan.main_goal}")
        print(f"📆 计划周期: {weekly_plan.start_date} 至 {weekly_plan.end_date}")
        print(f"📊 总计划天数: {len(weekly_plan.daily_plans)}天")
        
        total_time = sum(plan.estimated_total_time for plan in weekly_plan.daily_plans)
        total_tasks = sum(plan.total_tasks for plan in weekly_plan.daily_plans)
        
        print(f"📝 总任务数: {total_tasks}个")
        print(f"⏱️  预计总时间: {total_time//60}小时{total_time%60}分钟")
        
        print("\n" + "📋 每日计划详情:")
        print("-"*60)
        
        for i, daily_plan in enumerate(weekly_plan.daily_plans, 1):
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][(i-1) % 7]
            
            print(f"\n🗓️  {weekday} ({daily_plan.date}) - {daily_plan.plan_title}")
            print(f"   🎯 目标: {daily_plan.goal}")
            print(f"   📊 任务数: {daily_plan.total_tasks}个 | ⏱️ 预计时间: {daily_plan.estimated_total_time}分钟")
            
            for j, task in enumerate(daily_plan.tasks, 1):
                priority_emoji = {"高": "🔥", "中": "⭐", "低": "📝"}
                emoji = priority_emoji.get(task.priority, "📝")
                print(f"   {j}. ⏰ {task.time} | {emoji} {task.priority}")
                print(f"      📌 {task.description}")
                print(f"      💡 {task.reason}")
                print(f"      ⏳ {task.duration}分钟")
        
        print("\n" + "="*60)
    
    def save_weekly_plan(self, weekly_plan: WeeklyPlan, filename: str = "weekly_plan.json"):
        """保存7天计划到文件并归档到记忆系统"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(weekly_plan.model_dump(), f, ensure_ascii=False, indent=2)
            print(f"📁 7天计划已保存到 {filename}")
            
            # 归档到记忆系统
            for daily_plan in weekly_plan.daily_plans:
                self.memory_system.archive_plan(daily_plan)
            print("💾 7天计划已归档到记忆系统")
            
        except Exception as e:
            print(f"保存7天计划时出错: {e}")

def test_qwen_simple():
    """测试通义千问简单连接"""
    print("🧪 测试通义千问连接...")
    
    agent = LifeManagerAgentQwen()
    if not agent.api_key:
        print("请先获取通义千问API密钥：")
        print("1. 访问: https://dashscope.console.aliyun.com/apiKey")
        print("2. 注册/登录阿里云账号")
        print("3. 创建API密钥")
        print("4. 在.env文件中添加: DASHSCOPE_API_KEY=你的密钥")
        return False
    
    # 测试简单调用
    response = agent._call_qwen_with_retry("你好，请用一句话介绍自己", timeout=10)
    if response:
        print(f"✅ 通义千问连接成功！")
        print(f"回复: {response[:100]}...")
        return True
    else:
        print("❌ 通义千问连接失败")
        return False

if __name__ == "__main__":
    # 快速测试
    test_qwen_simple() 