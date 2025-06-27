# 🤖 生活管家 AI Agent 2.0

基于AI的智能生活规划助手 - 现代化Web应用版本，支持前后端分离、数据库存储和TodoList管理。

## ✨ 功能特性

### 🌟 核心功能
- 🤖 **智能计划生成**: 使用AI生成个性化的每日/7天计划
- 📅 **现代化Web界面**: 响应式设计，支持手机和电脑访问
- 📋 **TodoList管理**: 完整的待办事项管理系统
- 📊 **数据可视化**: 实时统计图表和分析报告
- 🔄 **计划转换**: 一键将AI计划转换为TodoList

### 🚀 技术特性
- 🏗️ **前后端分离**: FastAPI + 现代前端技术栈
- 🗄️ **数据库支持**: SQLite/PostgreSQL/MySQL多数据库支持
- 🐳 **容器化部署**: Docker + Docker Compose一键部署
- 🌐 **RESTful API**: 完整的API文档和接口
- 💾 **智能记忆**: 学习用户习惯，持续优化建议

### 📱 用户体验
- 🎯 **任务优先级**: 自动评估和排序任务重要性
- 📈 **进度跟踪**: 实时监控计划执行情况
- 🔔 **智能提醒**: 任务提醒和截止时间管理
- 📊 **分析报告**: 详细的完成率和效率分析

## 🚀 快速开始

### 方式1: 直接运行（推荐新手）

```bash
# 1. 克隆项目
git clone <repository_url>
cd life-manager-agent

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python start.py
```

### 方式2: Docker部署（推荐生产）

```bash
# 1. 克隆项目
git clone <repository_url>
cd life-manager-agent

# 2. 使用Docker Compose启动
docker-compose up -d

# 3. 访问应用
# 浏览器打开: http://localhost:8000
```

### 方式3: 开发模式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（可选）
cp env.example .env
# 编辑.env文件设置API密钥

# 3. 初始化数据库
python database.py

# 4. 启动开发服务器
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 📱 使用指南

### 🌐 Web界面操作

1. **仪表板**: 查看整体统计和快速操作
2. **计划管理**: 创建和管理AI生成的智能计划
3. **TodoList**: 管理日常待办事项
4. **数据分析**: 查看效率统计和趋势

### 🤖 创建智能计划

1. 点击"创建智能计划"按钮
2. 选择计划类型（每日/7天）
3. 详细描述目标：
   ```
   示例: 我想学习Python编程，掌握基础语法和面向对象编程
   ```
4. 输入时间偏好（可选）：
   ```
   示例: 我早上9-11点比较有精神，适合学习；下午2-5点比较忙
   ```
5. AI将生成详细的执行计划

### 📋 TodoList管理

- **添加事项**: 支持优先级、分类、截止时间
- **状态管理**: 一键标记完成/未完成
- **筛选功能**: 按状态、分类、优先级筛选
- **批量操作**: 批量完成、删除操作

### 🔄 计划转TodoList

1. 在计划列表中找到目标计划
2. 点击"转Todo"按钮
3. 系统自动将计划任务转换为TodoList项目
4. 可在TodoList页面管理转换后的任务

## 🏗️ 项目结构

```
life-manager-agent/
├── 🌐 前端文件
│   └── static/
│       ├── index.html          # 主页面
│       ├── css/style.css       # 样式文件
│       └── js/app.js          # 前端逻辑
├── 🚀 后端核心
│   ├── app.py                 # FastAPI主应用
│   ├── database.py            # 数据库模型
│   ├── services.py            # 业务逻辑层
│   ├── api_models.py          # API数据模型
│   └── life_manager_agent.py  # AI Agent核心
├── 🐳 部署文件
│   ├── Dockerfile             # Docker镜像
│   ├── docker-compose.yml     # 容器编排
│   └── start.py              # 启动脚本
├── ⚙️ 配置文件
│   ├── requirements.txt       # Python依赖
│   ├── env.example           # 环境变量模板
│   └── config.py             # 应用配置
└── 📚 文档
    └── README.md             # 项目文档
```

## 🛠️ 技术架构

### 🏗️ 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端(Web)     │───▶│  后端(FastAPI)  │───▶│   AI Agent      │
│  - Bootstrap    │    │  - RESTful API  │    │  - 智能规划     │
│  - Chart.js     │    │  - 业务逻辑     │    │  - 记忆学习     │
│  - 响应式设计   │    │  - 数据验证     │    │  - 模型调用     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  数据库层       │
                       │  - SQLAlchemy   │
                       │  - 多数据库支持 │
                       │  - 数据持久化   │
                       └─────────────────┘
```

### 🛠️ 技术栈
- **前端**: HTML5 + CSS3 + JavaScript + Bootstrap 5 + Chart.js
- **后端**: Python 3.11 + FastAPI + SQLAlchemy + Pydantic
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **AI引擎**: OpenAI GPT / 通义千问
- **部署**: Docker + Docker Compose + Uvicorn
- **开发**: Python Type Hints + 异步编程

## 📖 API文档

启动应用后访问API文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

```
GET  /api/dashboard/{user_id}     # 获取仪表板数据
POST /api/plans/                  # 创建智能计划
GET  /api/plans/                  # 获取计划列表
POST /api/todos/                  # 创建TodoList项目
GET  /api/todos/                  # 获取Todo列表
PUT  /api/todos/{todo_id}         # 更新Todo状态
POST /api/plans/{plan_id}/to-todos # 计划转TodoList
GET  /api/analytics/{user_id}     # 获取分析数据
```

## ⚙️ 配置说明

### 环境变量配置

复制 `env.example` 为 `.env` 并根据需要修改：

```bash
# 数据库配置
DATABASE_URL=sqlite:///./life_manager.db

# AI API配置  
OPENAI_API_KEY=your_openai_api_key_here
QWEN_API_KEY=your_qwen_api_key_here

# 应用配置
DEBUG=true
SECRET_KEY=your_secret_key_here
```

### 数据库配置

支持多种数据库：
- **开发环境**: SQLite (默认)
- **生产环境**: PostgreSQL, MySQL, SQL Server

#### SQL Server 配置

1. **安装依赖**:
   ```bash
   pip install pyodbc pymssql
   ```

2. **配置环境变量**:
   ```bash
   # 复制SQL Server配置模板
   cp env.sqlserver.example .env
   
   # 编辑配置文件
   DB_TYPE=sqlserver
   DB_SERVER=localhost
   DB_PORT=1433
   DB_NAME=life_manager
   DB_USER=sa
   DB_PASSWORD=YourPassword123!
   ```

3. **初始化数据库**:
   ```bash
   python init_sqlserver.py
   ```

4. **启动应用**:
   ```bash
   python start.py
   ```

#### 连接字符串格式

```bash
# 用户名密码认证
DATABASE_URL=mssql+pyodbc://username:password@server:port/database?driver=ODBC+Driver+17+for+SQL+Server

# Windows 集成认证
DATABASE_URL=mssql+pyodbc://@server:port/database?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

### AI模型配置

支持多种AI模型：
- OpenAI GPT系列 (默认)
- 阿里云通义千问
- 可扩展其他模型

## 🚀 部署指南

### 本地开发

```bash
# 启动开发服务器
python start.py

# 或使用uvicorn
uvicorn app:app --reload
```

### Docker部署

```bash
# 构建镜像
docker build -t life-manager-agent .

# 运行容器
docker run -p 8000:8000 life-manager-agent

# 或使用docker-compose
docker-compose up -d
```

### 云端部署

支持部署到：
- 阿里云
- AWS
- Azure
- Google Cloud
- 或任何支持Docker的云平台

## 🌟 特色亮点

1. **智能理解**: AI深度理解用户意图，生成专业计划
2. **时间优化**: 根据用户作息习惯智能安排任务时间
3. **任务分解**: 将复杂目标分解为可执行的具体任务
4. **进度跟踪**: 实时追踪执行进度，提供改进建议
5. **习惯学习**: 系统学习用户偏好，持续优化推荐
6. **数据安全**: 本地数据库存储，保护用户隐私

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Bootstrap 文档](https://getbootstrap.com/)
- [阿里云通义千问](https://dashscope.console.aliyun.com/)
- [OpenAI API](https://platform.openai.com/docs)

---

🌟 **让AI帮你规划更美好的生活！** 🌟 