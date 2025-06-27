// 生活管家AI Agent - 前端应用逻辑

// 全局状态管理
const AppState = {
    currentUser: 1, // 默认用户ID
    currentSection: 'dashboard',
    plans: [],
    todos: [],
    dashboardData: null,
    charts: {}
};

// API基础配置
const API_BASE = '/api';

// 工具函数
const Utils = {
    // 显示加载指示器
    showLoading() {
        document.getElementById('loading').style.display = 'flex';
    },
    
    // 隐藏加载指示器
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    },
    
    // 显示Toast通知
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastBody = document.getElementById('toast-body');
        const toastHeader = toast.querySelector('.toast-header i');
        
        toastBody.textContent = message;
        
        // 更新图标和样式
        if (type === 'success') {
            toastHeader.className = 'bi bi-check-circle text-success me-2';
        } else if (type === 'error') {
            toastHeader.className = 'bi bi-exclamation-triangle text-danger me-2';
        } else {
            toastHeader.className = 'bi bi-info-circle text-primary me-2';
        }
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    },
    
    // API请求封装
    async apiRequest(url, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }
        
        try {
            const response = await fetch(API_BASE + url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || '请求失败');
            }
            
            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    },
    
    // 格式化日期
    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // 格式化优先级
    formatPriority(priority) {
        const priorityMap = {
            '高': '<span class="priority-badge high">高</span>',
            '中': '<span class="priority-badge medium">中</span>',
            '低': '<span class="priority-badge low">低</span>'
        };
        return priorityMap[priority] || priority;
    },
    
    // 格式化状态
    formatStatus(status) {
        const statusMap = {
            'active': '<span class="status-badge active">进行中</span>',
            'completed': '<span class="status-badge completed">已完成</span>',
            'paused': '<span class="status-badge paused">已暂停</span>',
            'pending': '<span class="status-badge active">待开始</span>',
            'in_progress': '<span class="status-badge active">进行中</span>'
        };
        return statusMap[status] || status;
    }
};

// 页面管理
const PageManager = {
    // 显示指定页面
    showSection(sectionName) {
        // 隐藏所有页面
        document.querySelectorAll('.section').forEach(section => {
            section.style.display = 'none';
        });
        
        // 显示目标页面
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
            AppState.currentSection = sectionName;
        }
        
        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[onclick="showSection('${sectionName}')"]`)?.classList.add('active');
        
        // 加载页面数据
        this.loadSectionData(sectionName);
    },
    
    // 加载页面数据
    async loadSectionData(sectionName) {
        try {
            switch (sectionName) {
                case 'dashboard':
                    await DashboardManager.loadDashboard();
                    break;
                case 'plans':
                    await PlanManager.loadPlans();
                    break;
                case 'todos':
                    await TodoManager.loadTodos();
                    break;
                case 'analytics':
                    await AnalyticsManager.loadAnalytics();
                    break;
            }
        } catch (error) {
            console.error('加载页面数据失败:', error);
            Utils.showToast('加载数据失败，请稍后重试', 'error');
        }
    }
};

// 仪表板管理
const DashboardManager = {
    async loadDashboard() {
        Utils.showLoading();
        
        try {
            const data = await Utils.apiRequest(`/dashboard/${AppState.currentUser}`);
            AppState.dashboardData = data;
            this.renderDashboard(data);
        } catch (error) {
            console.error('加载仪表板失败:', error);
            Utils.showToast('加载仪表板失败', 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    renderDashboard(data) {
        // 更新统计卡片
        document.getElementById('active-plans').textContent = data.active_plans;
        document.getElementById('completed-tasks').textContent = data.completed_tasks;
        document.getElementById('pending-todos').textContent = data.total_todos - data.completed_todos;
        document.getElementById('completion-rate').textContent = Math.round(data.completion_rate * 100) + '%';
        
        // 渲染最近活动
        this.renderRecentActivities(data.recent_activities);
    },
    
    renderRecentActivities(activities) {
        const container = document.getElementById('recent-activities');
        
        if (!activities || activities.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无活动记录</p>';
            return;
        }
        
        const html = `
            <div class="activity-timeline">
                ${activities.map(activity => `
                    <div class="activity-item">
                        <div class="activity-time">${Utils.formatDate(activity.timestamp)}</div>
                        <div class="activity-content">${activity.title}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
    }
};

// 计划管理
const PlanManager = {
    async loadPlans() {
        Utils.showLoading();
        
        try {
            const plans = await Utils.apiRequest(`/plans/?user_id=${AppState.currentUser}`);
            AppState.plans = plans;
            this.renderPlans(plans);
        } catch (error) {
            console.error('加载计划失败:', error);
            Utils.showToast('加载计划失败', 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    renderPlans(plans) {
        const container = document.getElementById('plans-list');
        
        if (!plans || plans.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-calendar-x"></i>
                        <h5>暂无计划</h5>
                        <p>创建您的第一个智能计划，让AI帮您规划时间</p>
                        <button class="btn btn-primary" onclick="showCreatePlanModal()">
                            <i class="bi bi-plus-circle"></i> 创建计划
                        </button>
                    </div>
                </div>
            `;
            return;
        }
        
        const html = plans.map(plan => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card plan-card ${plan.plan_type} ${plan.status}">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">${plan.title}</h6>
                        ${Utils.formatStatus(plan.status)}
                    </div>
                    <div class="card-body">
                        <p class="text-muted mb-2">${plan.description || plan.goal}</p>
                        <div class="mb-3">
                            <small class="text-muted">
                                <i class="bi bi-calendar"></i> ${Utils.formatDate(plan.start_date)}
                                ${plan.end_date ? ' - ' + Utils.formatDate(plan.end_date) : ''}
                            </small>
                        </div>
                        <div class="mb-3">
                            <small class="text-muted">
                                <i class="bi bi-clock"></i> 预计 ${Math.round(plan.estimated_total_time / 60)} 小时
                            </small>
                        </div>
                        <div class="task-summary">
                            <h6>任务概览:</h6>
                            ${plan.tasks.slice(0, 3).map(task => `
                                <div class="task-item task-item-sm">
                                    <small>${task.title}</small>
                                </div>
                            `).join('')}
                            ${plan.tasks.length > 3 ? `<small class="text-muted">... 还有 ${plan.tasks.length - 3} 个任务</small>` : ''}
                        </div>
                    </div>
                    <div class="card-footer bg-transparent">
                        <div class="btn-group w-100">
                            <button class="btn btn-outline-primary btn-sm" onclick="viewPlanDetails(${plan.id})">
                                <i class="bi bi-eye"></i> 查看
                            </button>
                            <button class="btn btn-outline-success btn-sm" onclick="planToTodos(${plan.id})">
                                <i class="bi bi-arrow-right"></i> 转Todo
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    },
    
    async createPlan(planData) {
        Utils.showLoading();
        
        try {
            const newPlan = await Utils.apiRequest('/plans/', {
                method: 'POST',
                body: planData
            });
            
            Utils.showToast('计划创建成功！');
            await this.loadPlans();
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('createPlanModal'));
            modal.hide();
            
        } catch (error) {
            console.error('创建计划失败:', error);
            Utils.showToast('创建计划失败: ' + error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    }
};

// Todo管理
const TodoManager = {
    async loadTodos(filters = {}) {
        Utils.showLoading();
        
        try {
            let url = `/todos/?user_id=${AppState.currentUser}`;
            
            // 添加过滤参数
            if (filters.is_completed !== undefined) {
                url += `&is_completed=${filters.is_completed}`;
            }
            if (filters.category) {
                url += `&category=${filters.category}`;
            }
            if (filters.priority) {
                url += `&priority=${filters.priority}`;
            }
            
            const todos = await Utils.apiRequest(url);
            AppState.todos = todos;
            this.renderTodos(todos);
        } catch (error) {
            console.error('加载Todo失败:', error);
            Utils.showToast('加载Todo失败', 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    renderTodos(todos) {
        const container = document.getElementById('todos-list');
        
        if (!todos || todos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-check2-square"></i>
                    <h5>暂无待办事项</h5>
                    <p>添加您的第一个待办事项开始管理任务</p>
                    <button class="btn btn-primary" onclick="showCreateTodoModal()">
                        <i class="bi bi-plus-circle"></i> 添加事项
                    </button>
                </div>
            `;
            return;
        }
        
        const html = todos.map(todo => `
            <div class="todo-item ${todo.is_completed ? 'completed' : ''} priority-${todo.priority.toLowerCase()}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="todo-title">${todo.title}</h6>
                        ${todo.description ? `<p class="text-muted mb-2">${todo.description}</p>` : ''}
                        <div class="todo-meta">
                            <span class="me-3">
                                <i class="bi bi-flag"></i> ${Utils.formatPriority(todo.priority)}
                            </span>
                            ${todo.category ? `
                                <span class="me-3">
                                    <i class="bi bi-tag"></i> ${todo.category}
                                </span>
                            ` : ''}
                            ${todo.due_date ? `
                                <span class="me-3">
                                    <i class="bi bi-calendar"></i> ${Utils.formatDate(todo.due_date)}
                                </span>
                            ` : ''}
                        </div>
                    </div>
                    <div class="todo-actions">
                        <button class="btn btn-sm ${todo.is_completed ? 'btn-outline-warning' : 'btn-outline-success'}" 
                                onclick="toggleTodo(${todo.id}, ${!todo.is_completed})">
                            <i class="bi ${todo.is_completed ? 'bi-arrow-counterclockwise' : 'bi-check'}"></i>
                            ${todo.is_completed ? '撤销' : '完成'}
                        </button>
                        <button class="btn btn-sm btn-outline-primary" onclick="editTodo(${todo.id})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTodo(${todo.id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    },
    
    async createTodo(todoData) {
        Utils.showLoading();
        
        try {
            const newTodo = await Utils.apiRequest('/todos/', {
                method: 'POST',
                body: todoData
            });
            
            Utils.showToast('待办事项添加成功！');
            await this.loadTodos();
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('createTodoModal'));
            modal.hide();
            
        } catch (error) {
            console.error('创建Todo失败:', error);
            Utils.showToast('创建待办事项失败: ' + error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async updateTodo(todoId, updates) {
        Utils.showLoading();
        
        try {
            await Utils.apiRequest(`/todos/${todoId}`, {
                method: 'PUT',
                body: updates
            });
            
            Utils.showToast('更新成功！');
            await this.loadTodos();
        } catch (error) {
            console.error('更新Todo失败:', error);
            Utils.showToast('更新失败: ' + error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    async deleteTodo(todoId) {
        if (!confirm('确定要删除这个待办事项吗？')) {
            return;
        }
        
        Utils.showLoading();
        
        try {
            await Utils.apiRequest(`/todos/${todoId}`, {
                method: 'DELETE'
            });
            
            Utils.showToast('删除成功！');
            await this.loadTodos();
        } catch (error) {
            console.error('删除Todo失败:', error);
            Utils.showToast('删除失败: ' + error.message, 'error');
        } finally {
            Utils.hideLoading();
        }
    }
};

// 分析统计管理
const AnalyticsManager = {
    async loadAnalytics() {
        Utils.showLoading();
        
        try {
            const analytics = await Utils.apiRequest(`/analytics/${AppState.currentUser}`);
            this.renderCharts(analytics);
        } catch (error) {
            console.error('加载分析数据失败:', error);
            Utils.showToast('加载分析数据失败', 'error');
        } finally {
            Utils.hideLoading();
        }
    },
    
    renderCharts(analytics) {
        this.renderCompletionChart(analytics.daily_completion);
        this.renderCategoryChart(analytics.category_distribution);
    },
    
    renderCompletionChart(data) {
        const ctx = document.getElementById('completion-chart').getContext('2d');
        
        if (AppState.charts.completion) {
            AppState.charts.completion.destroy();
        }
        
        AppState.charts.completion = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => new Date(d.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })),
                datasets: [{
                    label: '完成任务数',
                    data: data.map(d => d.completed),
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    },
    
    renderCategoryChart(data) {
        const ctx = document.getElementById('category-chart').getContext('2d');
        
        if (AppState.charts.category) {
            AppState.charts.category.destroy();
        }
        
        const colors = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0'];
        
        AppState.charts.category = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    data: Object.values(data),
                    backgroundColor: colors.slice(0, Object.keys(data).length)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
};

// 全局函数 - 页面操作
function showSection(sectionName) {
    PageManager.showSection(sectionName);
}

function showCreatePlanModal() {
    const modal = new bootstrap.Modal(document.getElementById('createPlanModal'));
    modal.show();
}

function showCreateTodoModal() {
    const modal = new bootstrap.Modal(document.getElementById('createTodoModal'));
    modal.show();
}

// 全局函数 - 计划操作
async function createPlan() {
    const form = document.getElementById('createPlanForm');
    const formData = new FormData(form);
    
    const planData = {
        goal: document.getElementById('planGoal').value,
        time_preference: document.getElementById('timePreference').value,
        plan_type: document.querySelector('input[name="planType"]:checked').value
    };
    
    if (!planData.goal.trim()) {
        Utils.showToast('请输入目标描述', 'error');
        return;
    }
    
    await PlanManager.createPlan(planData);
    
    // 清空表单
    form.reset();
    document.getElementById('daily').checked = true;
}

async function planToTodos(planId) {
    if (!confirm('确定要将计划任务转换为待办事项吗？')) {
        return;
    }
    
    Utils.showLoading();
    
    try {
        await Utils.apiRequest(`/plans/${planId}/to-todos`, {
            method: 'POST'
        });
        
        Utils.showToast('计划任务已成功转换为待办事项！');
        
        // 如果当前在Todo页面，刷新列表
        if (AppState.currentSection === 'todos') {
            await TodoManager.loadTodos();
        }
    } catch (error) {
        console.error('转换失败:', error);
        Utils.showToast('转换失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

// 全局函数 - Todo操作
async function createTodo() {
    const todoData = {
        title: document.getElementById('todoTitle').value,
        description: document.getElementById('todoDescription').value,
        priority: document.getElementById('todoPriority').value,
        category: document.getElementById('todoCategory').value || null,
        due_date: document.getElementById('todoDueDate').value || null
    };
    
    if (!todoData.title.trim()) {
        Utils.showToast('请输入标题', 'error');
        return;
    }
    
    await TodoManager.createTodo(todoData);
    
    // 清空表单
    document.getElementById('createTodoForm').reset();
}

async function toggleTodo(todoId, isCompleted) {
    await TodoManager.updateTodo(todoId, { is_completed: isCompleted });
}

async function deleteTodo(todoId) {
    await TodoManager.deleteTodo(todoId);
}

// 全局函数 - 过滤操作
async function filterTodos() {
    const filters = {
        is_completed: document.getElementById('todo-status-filter').value || undefined,
        category: document.getElementById('todo-category-filter').value || undefined,
        priority: document.getElementById('todo-priority-filter').value || undefined
    };
    
    await TodoManager.loadTodos(filters);
}

function clearTodoFilters() {
    document.getElementById('todo-status-filter').value = '';
    document.getElementById('todo-category-filter').value = '';
    document.getElementById('todo-priority-filter').value = '';
    TodoManager.loadTodos();
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 默认显示仪表板
    PageManager.showSection('dashboard');
    
    // 设置定时刷新仪表板
    setInterval(() => {
        if (AppState.currentSection === 'dashboard') {
            DashboardManager.loadDashboard();
        }
    }, 30000); // 30秒刷新一次
});

// 导出模块（如果需要）
window.AppState = AppState;
window.Utils = Utils;
window.PageManager = PageManager;
window.DashboardManager = DashboardManager;
window.PlanManager = PlanManager;
window.TodoManager = TodoManager;
window.AnalyticsManager = AnalyticsManager; 