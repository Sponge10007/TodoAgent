# 生活管家AI Agent 使用指南

## 🎯 项目概述

生活管家AI Agent是一个智能的生活管理助手，能够帮助用户：

1. **管理长期目标** - 创建和管理各种生活目标
2. **智能任务拆解** - 将大目标自动拆解为可执行的小任务
3. **时间规划** - 制定详细的时间表和进度跟踪
4. **定期推送** - 每天推送任务提醒和进度更新
5. **进度可视化** - 直观展示目标完成进度

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
python main.py
```

或者使用启动脚本：

```bash
python run.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:8000

## 📖 使用示例

### 创建健身目标

1. **访问目标管理页面**
   - 点击侧边栏的"目标管理"
   - 点击"创建新目标"按钮

2. **填写目标信息**
   ```
   目标标题：两个月内改变自己
   目标描述：通过科学的健身计划和饮食调整，在两个月内改善体态，增强体质，建立健康的生活方式
   目标类别：健身
   开始日期：2024-01-01
   结束日期：2024-03-01
   ```

3. **AI自动生成任务计划**
   系统会自动为你生成以下任务：
   - 第1-2周：建立运动习惯
   - 第3-4周：增加运动强度
   - 第5-6周：优化饮食
   - 第7-8周：巩固成果

### 查看每日任务

1. **访问仪表板**
   - 主页显示今日任务概览
   - 查看任务完成进度

2. **管理任务状态**
   - 点击"标记完成"按钮完成任务
   - 查看任务详情和预计时长

### 接收推送提醒

系统会在以下时间自动推送提醒：
- **上午9点**：今日任务提醒
- **下午6点**：进度更新和激励消息

## 🔧 API接口

### 目标管理

```bash
# 创建目标
POST /api/goals/
{
    "title": "目标标题",
    "description": "目标描述",
    "category": "健身",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-03-01T23:59:59"
}

# 获取目标列表
GET /api/goals/

# 获取特定目标
GET /api/goals/{goal_id}

# 更新目标进度
PUT /api/goals/{goal_id}/progress?progress=50.0

# 删除目标
DELETE /api/goals/{goal_id}
```

### 任务管理

```bash
# 获取任务列表
GET /api/tasks/

# 获取今日任务
GET /api/tasks/daily/{date}

# 更新任务状态
PUT /api/tasks/{task_id}/status
{
    "status": "completed"
}

# 获取逾期任务
GET /api/tasks/overdue/

# 获取即将到来的任务
GET /api/tasks/upcoming/?days=7
```

### 仪表板数据

```bash
# 获取仪表板摘要
GET /api/dashboard/summary

# 获取目标进度
GET /api/dashboard/goals/progress

# 获取日历视图
GET /api/dashboard/tasks/calendar?start_date=2024-01-01&end_date=2024-01-31

# 获取分析数据
GET /api/dashboard/analytics
```

## 🎨 界面功能

### 仪表板
- **统计卡片**：显示总目标数、今日任务、完成率、逾期任务
- **目标进度**：可视化展示各目标的完成进度
- **今日任务**：显示今日需要完成的任务列表
- **完成趋势**：图表展示任务完成趋势

### 目标管理
- **目标列表**：查看所有目标及其状态
- **创建目标**：通过表单创建新目标
- **目标详情**：查看目标的详细信息和相关任务
- **进度更新**：手动更新目标完成进度

### 任务管理
- **任务列表**：按不同条件筛选任务
- **任务状态**：标记任务为待完成、进行中、已完成
- **任务详情**：查看任务描述、预计时长等信息
- **进度记录**：记录任务完成情况和备注

## 🤖 AI功能

### 智能任务拆解
系统根据目标类别自动拆解任务：

**健身目标**：
- 阶段1：建立运动习惯
- 阶段2：增加运动强度
- 阶段3：优化饮食结构
- 阶段4：巩固成果

**学习目标**：
- 阶段1：确定学习目标和计划
- 阶段2：开始基础学习和实践

**工作目标**：
- 阶段1：分析现状和制定计划
- 阶段2：执行改进措施

### 激励消息生成
根据完成进度自动生成激励消息：
- 0-25%：鼓励开始
- 25-50%：肯定进展
- 50-75%：激励坚持
- 75-100%：冲刺鼓励

## 📊 数据统计

### 目标统计
- 按类别统计目标数量
- 目标完成率统计
- 目标时间分布

### 任务统计
- 每日任务完成情况
- 任务完成趋势
- 逾期任务统计

### 用户行为分析
- 任务完成模式
- 目标设定偏好
- 时间管理效率

## 🔧 配置选项

### 通知设置
```python
# 在 services/notification_service.py 中配置
schedule.every().day.at("09:00").do(self.send_daily_notifications)  # 每日提醒时间
schedule.every().day.at("18:00").do(self.send_progress_updates)     # 进度更新时间
```

### 数据库配置
```python
# 在 models/database.py 中配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./life_agent.db"  # 数据库文件路径
```

### 任务模板
```python
# 在 services/ai_planner.py 中自定义任务模板
self.task_templates = {
    "健身": {
        "阶段1": {
            "duration_weeks": 2,
            "tasks": [...]
        }
    }
}
```

## 🚀 部署指南

### 本地部署
1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 启动应用：`python main.py`
4. 访问：http://localhost:8000

### 生产部署
1. 使用Gunicorn部署：
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. 使用Docker部署：
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库文件权限
   - 确保SQLite已安装

2. **依赖安装失败**
   - 升级pip：`pip install --upgrade pip`
   - 使用虚拟环境

3. **端口被占用**
   - 修改端口：`uvicorn.run("main:app", port=8001)`
   - 或停止占用端口的进程

4. **通知服务不工作**
   - 检查系统时间设置
   - 查看日志输出

### 日志查看
```bash
# 启动时查看详细日志
python main.py --log-level debug
```

## 📞 技术支持

如果遇到问题，请：
1. 查看控制台错误信息
2. 检查API文档：http://localhost:8000/docs
3. 查看项目日志文件

## 🎉 开始使用

现在你已经了解了生活管家AI Agent的所有功能，开始创建你的第一个目标吧！

记住：
- 🎯 设定明确的目标
- 📅 坚持每日任务
- 📊 定期查看进度
- 💪 保持积极心态

祝你使用愉快！ 