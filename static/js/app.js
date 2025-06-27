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
        const loadingEl = document.getElementById('loading');
        if (loadingEl) {
            loadingEl.style.display = 'flex';
        }
    },
    
    // 隐藏加载指示器
    hideLoading() {
        const loadingEl = document.getElementById('loading');
        if (loadingEl) {
            // 使用 !important 来确保样式被应用，并添加一个延时以处理可能的渲染竞争
            setTimeout(() => {
                loadingEl.style.cssText = 'display: none !important;';
            }, 100); // 100毫秒的延时
        }
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
        document.querySelectorAll('main .section').forEach(section => {
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
        const activeLink = document.querySelector(`[onclick="PageManager.showSection('${sectionName}')"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
        
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
                        <i class="bi bi-check-circle-fill activity-icon"></i>
                        <div class="activity-content">
                            <span class="activity-title">${activity.title}</span>
                            <small class="activity-time text-muted">${Utils.formatDate(activity.timestamp)}</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        container.innerHTML = html;
        
        // 强制隐藏加载指示器，确保UI状态正确
        Utils.hideLoading();
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
                                <div class="task-item task-item-sm d-flex justify-content-between align-items-center">
                                    <div class="flex-grow-1">
                                        <small>${task.title}</small>
                                        ${task.is_subtask ? '' : 
                                            `<div class="mt-1">
                                                <button class="btn btn-outline-secondary btn-xs" onclick="showSubtaskModal(${task.id})">
                                                    <i class="bi bi-list-ul"></i> 子任务
                                                </button>
                                            </div>`
                                        }
                                    </div>
                                    <span class="task-status-indicator ${task.status}">${Utils.formatStatus(task.status)}</span>
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
                        <div class="btn-group w-100 mt-2">
                            <button class="btn btn-outline-info btn-sm" onclick="showAIQuestions('${plan.goal}', '${plan.plan_type}')">
                                <i class="bi bi-robot"></i> AI优化
                            </button>
                            <button class="btn btn-outline-warning btn-sm" onclick="showReminderModal(${plan.id})">
                                <i class="bi bi-bell"></i> 设置提醒
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
            
            // 关闭创建计划模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('createPlanModal'));
            modal.hide();
            
            // 🎯 自动触发AI反问功能
            setTimeout(() => {
                showAIQuestions(planData.goal, planData.plan_type);
            }, 500); // 延迟500ms确保模态框完全关闭
            
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
    Utils.showLoading();
    
    try {
        const planType = document.querySelector('input[name="planType"]:checked').value;
        const goal = document.getElementById('planGoal').value.trim();
        const timePreference = document.getElementById('timePreference').value.trim();
        
        if (!goal) {
            Utils.showToast('请填写目标描述', 'error');
            return;
        }
        
        const planData = {
            goal: goal,
            time_preference: timePreference,
            plan_type: planType
        };
        
        // 自定义天数计划的额外参数
        if (planType === 'custom') {
            const userPreferredDays = document.getElementById('userPreferredDays').value;
            if (!userPreferredDays || userPreferredDays < 1) {
                Utils.showToast('请输入有效的天数', 'error');
                return;
            }
            planData.duration_days = parseInt(userPreferredDays);
            planData.user_preferred_days = parseInt(userPreferredDays);
        }
        
        await PlanManager.createPlan(planData);
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('createPlanModal'));
        modal.hide();
        
        // 清空表单
        document.getElementById('createPlanForm').reset();
        document.getElementById('customDaysSection').style.display = 'none';
        document.getElementById('aiSuggestedDays').textContent = '点击估算获取';
        document.getElementById('aiSuggestionWarning').style.display = 'none';
        
        // 重新加载计划列表
        if (AppState.currentSection === 'plans') {
            await PlanManager.loadPlans();
        }
        
        Utils.showToast('计划创建成功！', 'success');
        
    } catch (error) {
        console.error('创建计划失败:', error);
        Utils.showToast('创建计划失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
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
    filterTodos();
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

// 新增功能：自定义天数和子任务支持

// 切换自定义天数显示
function toggleCustomDays() {
    const planType = document.querySelector('input[name="planType"]:checked').value;
    const customDaysSection = document.getElementById('customDaysSection');
    
    if (planType === 'custom') {
        customDaysSection.style.display = 'block';
        // 自动估算天数
        autoEstimateDays();
    } else {
        customDaysSection.style.display = 'none';
    }
}

// 自动估算天数（当用户输入目标后）
async function autoEstimateDays() {
    const planType = document.querySelector('input[name="planType"]:checked').value;
    if (planType !== 'custom') return;
    
    const goal = document.getElementById('planGoal').value.trim();
    if (!goal) return;
    
    try {
        const result = await Utils.apiRequest('/ai/estimate-days', {
            method: 'POST',
            body: { task_description: goal }
        });
        
        document.getElementById('aiSuggestedDays').textContent = result.ai_estimated_days + '天';
        
        // 检查用户输入与AI建议的差异
        const userPreferredDays = document.getElementById('userPreferredDays').value;
        if (userPreferredDays) {
            checkDaysDifference(parseInt(userPreferredDays), result.ai_estimated_days);
        }
        
    } catch (error) {
        console.error('AI估算失败:', error);
        document.getElementById('aiSuggestedDays').textContent = '估算失败';
    }
}

// 手动估算天数
async function estimateDays() {
    const goal = document.getElementById('planGoal').value.trim();
    if (!goal) {
        Utils.showToast('请先填写目标描述', 'error');
        return;
    }
    
    Utils.showLoading();
    try {
        await autoEstimateDays();
        Utils.showToast('AI估算完成', 'success');
    } catch (error) {
        Utils.showToast('AI估算失败', 'error');
    } finally {
        Utils.hideLoading();
    }
}

// 检查天数差异并显示建议
function checkDaysDifference(userDays, aiDays) {
    const warningDiv = document.getElementById('aiSuggestionWarning');
    const textDiv = document.getElementById('aiSuggestionText');
    
    if (Math.abs(userDays - aiDays) > 3) {
        if (userDays < aiDays) {
            textDiv.textContent = `您期望的${userDays}天可能过于紧张，AI建议至少${aiDays}天完成。`;
            warningDiv.className = 'alert alert-warning mt-2';
        } else {
            textDiv.textContent = `您期望的${userDays}天较为宽松，可以安排更深入的学习内容。`;
            warningDiv.className = 'alert alert-info mt-2';
        }
        warningDiv.style.display = 'block';
    } else {
        warningDiv.style.display = 'none';
    }
}

// 子任务管理
let currentTaskId = null;

// 显示子任务管理模态框
async function showSubtaskModal(taskId) {
    currentTaskId = taskId;
    
    try {
        Utils.showLoading();
        const result = await Utils.apiRequest(`/tasks/${taskId}/with-subtasks?user_id=${AppState.currentUser}`);
        
        document.getElementById('mainTaskTitle').textContent = result.task.title;
        document.getElementById('mainTaskDescription').textContent = result.task.description || '无描述';
        
        renderSubtasks(result.subtasks);
        
        const modal = new bootstrap.Modal(document.getElementById('subtaskModal'));
        modal.show();
        
    } catch (error) {
        console.error('加载子任务失败:', error);
        Utils.showToast('加载子任务失败', 'error');
    } finally {
        Utils.hideLoading();
    }
}

// 渲染子任务列表
function renderSubtasks(subtasks) {
    const container = document.getElementById('subtasksList');
    
    if (!subtasks || subtasks.length === 0) {
        container.innerHTML = '<p class="text-muted text-center">暂无子任务</p>';
        return;
    }
    
    container.innerHTML = subtasks.map((subtask, index) => `
        <div class="list-group-item d-flex justify-content-between align-items-center">
            <div class="flex-grow-1">
                <h6 class="mb-1">${subtask.title}</h6>
                <small class="text-muted">
                    ${Utils.formatPriority(subtask.priority)} | 
                    ${subtask.duration}分钟 | 
                    ${Utils.formatStatus(subtask.status)}
                </small>
            </div>
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-success" onclick="updateSubtaskStatus(${subtask.id}, 'completed')" 
                        ${subtask.status === 'completed' ? 'disabled' : ''}>
                    <i class="bi bi-check"></i>
                </button>
                <button class="btn btn-outline-danger" onclick="deleteSubtask(${subtask.id})">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

// 添加子任务
async function addSubtask() {
    const title = document.getElementById('subtaskTitle').value.trim();
    const duration = parseInt(document.getElementById('subtaskDuration').value) || 30;
    const priority = document.getElementById('subtaskPriority').value;
    
    if (!title) {
        Utils.showToast('请输入子任务标题', 'error');
        return;
    }
    
    try {
        const subtaskData = {
            title: title,
            duration: duration,
            priority: priority,
            order_index: 0
        };
        
        await Utils.apiRequest(`/tasks/${currentTaskId}/subtasks?user_id=${AppState.currentUser}`, {
            method: 'POST',
            body: subtaskData
        });
        
        // 清空表单
        document.getElementById('subtaskTitle').value = '';
        document.getElementById('subtaskDuration').value = '30';
        document.getElementById('subtaskPriority').value = '中';
        
        // 重新加载子任务列表
        await showSubtaskModal(currentTaskId);
        
        Utils.showToast('子任务添加成功', 'success');
        
    } catch (error) {
        console.error('添加子任务失败:', error);
        Utils.showToast('添加子任务失败', 'error');
    }
}

// 更新子任务状态
async function updateSubtaskStatus(subtaskId, status) {
    try {
        await Utils.apiRequest(`/tasks/${subtaskId}`, {
            method: 'PUT',
            body: { 
                status: status,
                completed_at: status === 'completed' ? new Date().toISOString() : null 
            }
        });
        
        // 重新加载子任务列表
        await showSubtaskModal(currentTaskId);
        
        Utils.showToast('子任务状态更新成功', 'success');
        
    } catch (error) {
        console.error('更新子任务状态失败:', error);
        Utils.showToast('更新子任务状态失败', 'error');
    }
}

// 删除子任务
async function deleteSubtask(subtaskId) {
    if (!confirm('确定要删除这个子任务吗？')) {
        return;
    }
    
    Utils.showLoading();
    
    try {
        await Utils.apiRequest(`/subtasks/${subtaskId}`, {
            method: 'DELETE'
        });
        
        Utils.showToast('子任务删除成功！');
        
        // 重新加载子任务列表
        const currentTaskId = document.getElementById('subtaskModal').dataset.taskId;
        await showSubtaskModal(currentTaskId);
        
    } catch (error) {
        console.error('删除子任务失败:', error);
        Utils.showToast('删除子任务失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

// 计划详情管理
let currentPlan = null;
let isEditMode = false;

async function viewPlanDetails(planId) {
    Utils.showLoading();
    
    try {
        // 获取计划详情
        const plan = await Utils.apiRequest(`/plans/${planId}`);
        
        // 获取计划的任务
        const tasks = await Utils.apiRequest(`/tasks/?user_id=${AppState.currentUser}&plan_id=${planId}`);
        
        currentPlan = { ...plan, tasks };
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('planDetailsModal'));
        modal.show();
        
        // 渲染计划详情
        renderPlanDetails(currentPlan);
        
        // 默认为查看模式
        switchToViewMode();
        
    } catch (error) {
        console.error('加载计划详情失败:', error);
        Utils.showToast('加载计划详情失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

function renderPlanDetails(plan) {
    // 渲染计划基本信息
    document.getElementById('planTitleDisplay').textContent = plan.title;
    document.getElementById('planTitleInput').value = plan.title;
    
    document.getElementById('planGoalDisplay').textContent = plan.goal || '无描述';
    document.getElementById('planGoalInput').value = plan.goal || '';
    
    document.getElementById('planTypeDisplay').textContent = getPlanTypeText(plan.plan_type);
    document.getElementById('planDateDisplay').textContent = Utils.formatDate(plan.created_at);
    document.getElementById('planTaskCountDisplay').textContent = plan.tasks ? plan.tasks.length : 0;
    
    // 显示自定义计划的额外信息
    if (plan.duration_days) {
        document.getElementById('planDurationInfo').style.display = 'block';
        document.getElementById('planDurationDisplay').textContent = plan.duration_days;
        document.getElementById('planAiSuggestedDisplay').textContent = plan.ai_suggested_days || '未知';
    } else {
        document.getElementById('planDurationInfo').style.display = 'none';
    }
    
    // 渲染任务列表
    renderPlanTasks(plan.tasks || []);
}

function renderPlanTasks(tasks) {
    const container = document.getElementById('tasksContainer');
    
    if (!tasks || tasks.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="bi bi-list-task fs-1"></i>
                <p>此计划暂无任务</p>
            </div>
        `;
        return;
    }
    
    const html = tasks.map(task => `
        <div class="plan-detail-task" data-task-id="${task.id}">
            <!-- 查看模式 -->
            <div class="task-view">
                <div class="task-header">
                    <h6 class="task-title">${task.description}</h6>
                    <div class="d-flex gap-2">
                        <span class="task-priority-badge ${task.priority.toLowerCase()}">${task.priority}</span>
                        <span class="task-status-badge ${task.status.toLowerCase()}">${Utils.formatStatus(task.status)}</span>
                    </div>
                </div>
                
                <div class="task-meta">
                    <i class="bi bi-clock"></i> ${task.time || '未设置时间'} 
                    <span class="ms-3"><i class="bi bi-hourglass"></i> ${task.duration || 60}分钟</span>
                </div>
                
                ${task.reason ? `
                    <div class="task-reason">
                        <i class="bi bi-lightbulb"></i> ${task.reason}
                    </div>
                ` : ''}
                
                <div class="task-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="toggleTaskStatus(${task.id}, '${task.status}')">
                        <i class="bi ${task.status === 'completed' ? 'bi-arrow-counterclockwise' : 'bi-check'}"></i>
                        ${task.status === 'completed' ? '标记未完成' : '标记完成'}
                    </button>
                    
                    ${!task.parent_task_id ? `
                        <button class="btn btn-sm btn-outline-info" onclick="showSubtaskModal(${task.id})">
                            <i class="bi bi-list-ul"></i> 子任务
                        </button>
                    ` : ''}
                    
                    <button class="btn btn-sm btn-outline-warning edit-task-btn" onclick="editTask(${task.id})">
                        <i class="bi bi-pencil"></i> 编辑
                    </button>
                    
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(${task.id})">
                        <i class="bi bi-trash"></i> 删除
                    </button>
                </div>
            </div>
            
            <!-- 编辑模式 -->
            <div class="task-edit-form">
                <div class="mb-3">
                    <label class="form-label">任务描述</label>
                    <input type="text" class="form-control task-desc-input" value="${task.description}">
                </div>
                
                <div class="row">
                    <div class="col-md-3 mb-3">
                        <label class="form-label">时间</label>
                        <input type="text" class="form-control task-time-input" value="${task.time || ''}" placeholder="例如: 09:00">
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">时长(分钟)</label>
                        <input type="number" class="form-control task-duration-input" value="${task.duration || 60}" min="5" max="480">
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">优先级</label>
                        <select class="form-select task-priority-input">
                            <option value="高" ${task.priority === '高' ? 'selected' : ''}>高</option>
                            <option value="中" ${task.priority === '中' ? 'selected' : ''}>中</option>
                            <option value="低" ${task.priority === '低' ? 'selected' : ''}>低</option>
                        </select>
                    </div>
                    <div class="col-md-3 mb-3">
                        <label class="form-label">状态</label>
                        <select class="form-select task-status-input">
                            <option value="pending" ${task.status === 'pending' ? 'selected' : ''}>待完成</option>
                            <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>进行中</option>
                            <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>已完成</option>
                        </select>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">任务原因/说明</label>
                    <textarea class="form-control task-reason-input" rows="2">${task.reason || ''}</textarea>
                </div>
                
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-success" onclick="saveTaskEdit(${task.id})">
                        <i class="bi bi-save"></i> 保存
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="cancelTaskEdit(${task.id})">
                        <i class="bi bi-x"></i> 取消
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function switchToViewMode() {
    isEditMode = false;
    
    // 更新按钮状态
    document.getElementById('viewModeBtn').classList.add('active');
    document.getElementById('editModeBtn').classList.remove('active');
    
    // 隐藏编辑相关元素
    document.getElementById('planTitleView').style.display = 'block';
    document.getElementById('planTitleEdit').style.display = 'none';
    document.getElementById('planGoalView').style.display = 'block';
    document.getElementById('planGoalEdit').style.display = 'none';
    document.getElementById('editModeActions').style.display = 'none';
    
    // 隐藏任务编辑按钮
    document.querySelectorAll('.edit-task-btn').forEach(btn => {
        btn.style.display = 'inline-block';
    });
    
    // 取消所有任务编辑状态
    document.querySelectorAll('.plan-detail-task.editing').forEach(task => {
        task.classList.remove('editing');
    });
}

function switchToEditMode() {
    isEditMode = true;
    
    // 更新按钮状态
    document.getElementById('viewModeBtn').classList.remove('active');
    document.getElementById('editModeBtn').classList.add('active');
    
    // 显示编辑相关元素
    document.getElementById('planTitleView').style.display = 'none';
    document.getElementById('planTitleEdit').style.display = 'block';
    document.getElementById('planGoalView').style.display = 'none';
    document.getElementById('planGoalEdit').style.display = 'block';
    document.getElementById('editModeActions').style.display = 'block';
    
    // 显示任务编辑按钮
    document.querySelectorAll('.edit-task-btn').forEach(btn => {
        btn.style.display = 'inline-block';
    });
}

function editTask(taskId) {
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskElement) {
        taskElement.classList.add('editing');
    }
}

function cancelTaskEdit(taskId) {
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    if (taskElement) {
        taskElement.classList.remove('editing');
        // 重新渲染以恢复原始值
        renderPlanDetails(currentPlan);
    }
}

async function saveTaskEdit(taskId) {
    const taskElement = document.querySelector(`[data-task-id="${taskId}"]`);
    if (!taskElement) return;
    
    // 获取编辑后的值
    const description = taskElement.querySelector('.task-desc-input').value.trim();
    const time = taskElement.querySelector('.task-time-input').value.trim();
    const duration = parseInt(taskElement.querySelector('.task-duration-input').value);
    const priority = taskElement.querySelector('.task-priority-input').value;
    const status = taskElement.querySelector('.task-status-input').value;
    const reason = taskElement.querySelector('.task-reason-input').value.trim();
    
    if (!description) {
        Utils.showToast('任务描述不能为空', 'error');
        return;
    }
    
    Utils.showLoading();
    
    try {
        const updates = {
            description,
            time: time || null,
            duration,
            priority,
            status,
            reason: reason || null
        };
        
        await Utils.apiRequest(`/tasks/${taskId}`, {
            method: 'PUT',
            body: updates
        });
        
        Utils.showToast('任务更新成功！');
        
        // 更新本地数据
        const taskIndex = currentPlan.tasks.findIndex(t => t.id === taskId);
        if (taskIndex !== -1) {
            currentPlan.tasks[taskIndex] = { ...currentPlan.tasks[taskIndex], ...updates };
        }
        
        // 重新渲染
        renderPlanDetails(currentPlan);
        
    } catch (error) {
        console.error('更新任务失败:', error);
        Utils.showToast('更新任务失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

async function toggleTaskStatus(taskId, currentStatus) {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    
    Utils.showLoading();
    
    try {
        await Utils.apiRequest(`/tasks/${taskId}`, {
            method: 'PUT',
            body: { status: newStatus }
        });
        
        Utils.showToast(`任务已标记为${newStatus === 'completed' ? '完成' : '未完成'}！`);
        
        // 更新本地数据
        const taskIndex = currentPlan.tasks.findIndex(t => t.id === taskId);
        if (taskIndex !== -1) {
            currentPlan.tasks[taskIndex].status = newStatus;
        }
        
        // 重新渲染
        renderPlanDetails(currentPlan);
        
    } catch (error) {
        console.error('更新任务状态失败:', error);
        Utils.showToast('更新任务状态失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

async function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？此操作不可撤销。')) {
        return;
    }
    
    Utils.showLoading();
    
    try {
        await Utils.apiRequest(`/tasks/${taskId}`, {
            method: 'DELETE'
        });
        
        Utils.showToast('任务删除成功！');
        
        // 从本地数据中移除
        currentPlan.tasks = currentPlan.tasks.filter(t => t.id !== taskId);
        
        // 重新渲染
        renderPlanDetails(currentPlan);
        
        // 刷新计划列表
        await PlanManager.loadPlans();
        
    } catch (error) {
        console.error('删除任务失败:', error);
        Utils.showToast('删除任务失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

async function addNewTask() {
    const container = document.getElementById('tasksContainer');
    
    // 检查是否已经有新任务表单
    if (document.querySelector('.new-task-form')) {
        return;
    }
    
    const newTaskForm = `
        <div class="new-task-form">
            <h6><i class="bi bi-plus-circle"></i> 添加新任务</h6>
            
            <div class="mb-3">
                <label class="form-label">任务描述 *</label>
                <input type="text" class="form-control" id="newTaskDesc" placeholder="请输入任务描述">
            </div>
            
            <div class="row">
                <div class="col-md-3 mb-3">
                    <label class="form-label">时间</label>
                    <input type="text" class="form-control" id="newTaskTime" placeholder="例如: 09:00">
                </div>
                <div class="col-md-3 mb-3">
                    <label class="form-label">时长(分钟)</label>
                    <input type="number" class="form-control" id="newTaskDuration" value="60" min="5" max="480">
                </div>
                <div class="col-md-3 mb-3">
                    <label class="form-label">优先级</label>
                    <select class="form-select" id="newTaskPriority">
                        <option value="高">高</option>
                        <option value="中" selected>中</option>
                        <option value="低">低</option>
                    </select>
                </div>
                <div class="col-md-3 mb-3">
                    <label class="form-label">状态</label>
                    <select class="form-select" id="newTaskStatus">
                        <option value="pending" selected>待完成</option>
                        <option value="in_progress">进行中</option>
                        <option value="completed">已完成</option>
                    </select>
                </div>
            </div>
            
            <div class="mb-3">
                <label class="form-label">任务原因/说明</label>
                <textarea class="form-control" id="newTaskReason" rows="2" placeholder="为什么要做这个任务？"></textarea>
            </div>
            
            <div class="d-flex gap-2">
                <button class="btn btn-success" onclick="saveNewTask()">
                    <i class="bi bi-save"></i> 保存任务
                </button>
                <button class="btn btn-secondary" onclick="cancelNewTask()">
                    <i class="bi bi-x"></i> 取消
                </button>
            </div>
        </div>
    `;
    
    // 在任务列表开头插入新任务表单
    container.insertAdjacentHTML('afterbegin', newTaskForm);
}

async function saveNewTask() {
    const description = document.getElementById('newTaskDesc').value.trim();
    const time = document.getElementById('newTaskTime').value.trim();
    const duration = parseInt(document.getElementById('newTaskDuration').value);
    const priority = document.getElementById('newTaskPriority').value;
    const status = document.getElementById('newTaskStatus').value;
    const reason = document.getElementById('newTaskReason').value.trim();
    
    if (!description) {
        Utils.showToast('任务描述不能为空', 'error');
        return;
    }
    
    Utils.showLoading();
    
    try {
        const taskData = {
            user_id: AppState.currentUser,
            plan_id: currentPlan.id,
            description,
            time: time || null,
            duration,
            priority,
            status,
            reason: reason || null
        };
        
        const newTask = await Utils.apiRequest('/tasks/', {
            method: 'POST',
            body: taskData
        });
        
        Utils.showToast('新任务添加成功！');
        
        // 添加到本地数据
        currentPlan.tasks.push(newTask);
        
        // 重新渲染
        renderPlanDetails(currentPlan);
        
        // 刷新计划列表
        await PlanManager.loadPlans();
        
    } catch (error) {
        console.error('添加任务失败:', error);
        Utils.showToast('添加任务失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

function cancelNewTask() {
    const form = document.querySelector('.new-task-form');
    if (form) {
        form.remove();
    }
}

async function savePlanChanges() {
    const title = document.getElementById('planTitleInput').value.trim();
    const goal = document.getElementById('planGoalInput').value.trim();
    
    if (!title) {
        Utils.showToast('计划标题不能为空', 'error');
        return;
    }
    
    Utils.showLoading();
    
    try {
        const updates = {
            title,
            goal: goal || null
        };
        
        await Utils.apiRequest(`/plans/${currentPlan.id}`, {
            method: 'PUT',
            body: updates
        });
        
        Utils.showToast('计划信息更新成功！');
        
        // 更新本地数据
        currentPlan.title = title;
        currentPlan.goal = goal;
        
        // 重新渲染
        renderPlanDetails(currentPlan);
        
        // 刷新计划列表
        await PlanManager.loadPlans();
        
        // 切换到查看模式
        switchToViewMode();
        
    } catch (error) {
        console.error('更新计划失败:', error);
        Utils.showToast('更新计划失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

async function deletePlan() {
    if (!confirm('确定要删除这个计划吗？此操作将删除计划及其所有任务，且不可撤销。')) {
        return;
    }
    
    Utils.showLoading();
    
    try {
        await Utils.apiRequest(`/plans/${currentPlan.id}`, {
            method: 'DELETE'
        });
        
        Utils.showToast('计划删除成功！');
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('planDetailsModal'));
        modal.hide();
        
        // 刷新计划列表
        await PlanManager.loadPlans();
        
        // 刷新仪表板
        await DashboardManager.loadDashboard();
        
    } catch (error) {
        console.error('删除计划失败:', error);
        Utils.showToast('删除计划失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

function getPlanTypeText(planType) {
    const types = {
        'daily': '每日计划',
        'weekly': '7天计划',
        'custom': '自定义计划'
    };
    return types[planType] || planType;
}

// AI反问功能
let currentQuestions = [];
let currentAnswers = {};
let currentPlanGoal = '';

async function showAIQuestions(goal, planType = 'daily') {
    Utils.showLoading();
    
    try {
        // 获取AI生成的问题
        const response = await Utils.apiRequest(`/ai/follow-up-questions?goal_description=${encodeURIComponent(goal)}&plan_type=${planType}`);
        
        currentQuestions = response.questions;
        currentAnswers = {};
        currentPlanGoal = goal;
        
        // 渲染问题
        renderAIQuestions(response.questions);
        
        // 更新模态框标题，显示计划目标
        const modalTitle = document.querySelector('#aiQuestionModal .modal-title');
        modalTitle.innerHTML = `
            <i class="bi bi-robot"></i> AI智能问答 - 优化您的计划
            <br><small class="text-muted">目标: ${goal}</small>
        `;
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('aiQuestionModal'));
        modal.show();
        
        // 显示欢迎提示
        Utils.showToast('🤖 AI想了解更多细节来为您优化计划！', 'info');
        
    } catch (error) {
        console.error('获取AI问题失败:', error);
        Utils.showToast('获取AI问题失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

function renderAIQuestions(questions) {
    const container = document.getElementById('questionsContainer');
    
    const html = questions.map((question, index) => `
        <div class="question-item mb-4" data-question-index="${index}">
            <div class="card">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="bi bi-question-circle text-primary"></i> 
                        问题 ${index + 1}
                    </h6>
                    <p class="card-text">${question}</p>
                    
                    <div class="mt-3">
                        <textarea 
                            class="form-control question-answer" 
                            rows="3" 
                            placeholder="请输入您的回答，或留空跳过此问题..."
                            oninput="updateAnswerProgress(${index}, this.value)"
                        ></textarea>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
    
    // 更新进度
    updateProgressDisplay();
}

function updateAnswerProgress(questionIndex, answer) {
    if (answer.trim()) {
        currentAnswers[questionIndex] = {
            question: currentQuestions[questionIndex],
            answer: answer.trim()
        };
    } else {
        delete currentAnswers[questionIndex];
    }
    
    updateProgressDisplay();
}

function updateProgressDisplay() {
    const answeredCount = Object.keys(currentAnswers).length;
    const totalCount = currentQuestions.length;
    const percentage = totalCount > 0 ? (answeredCount / totalCount) * 100 : 0;
    
    document.getElementById('questionProgress').style.width = `${percentage}%`;
    document.getElementById('progressText').textContent = `${answeredCount}/${totalCount}`;
}

async function submitAIAnswers() {
    Utils.showLoading();
    
    try {
        // 这里可以根据用户回答创建增强版计划
        // 目前先显示收集到的信息
        
        const answeredQuestions = Object.keys(currentAnswers).length;
        
        if (answeredQuestions === 0) {
            Utils.showToast('您还没有回答任何问题，将使用标准计划', 'info');
        } else {
            Utils.showToast(`感谢您回答了${answeredQuestions}个问题！AI将根据您的回答优化计划`, 'success');
            
            // 保存用户偏好到本地存储
            localStorage.setItem('userPreferences', JSON.stringify({
                goal: currentPlanGoal,
                answers: currentAnswers,
                timestamp: new Date().toISOString()
            }));
        }
        
        // 关闭模态框
        const modal = bootstrap.Modal.getInstance(document.getElementById('aiQuestionModal'));
        modal.hide();
        
        // 可以在这里触发重新生成计划或显示优化建议
        
    } catch (error) {
        console.error('提交AI回答失败:', error);
        Utils.showToast('提交失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

// 提醒功能
let currentReminderPlanId = null;

function showReminderModal(planId) {
    currentReminderPlanId = planId;
    
    // 显示模态框
    const modal = new bootstrap.Modal(document.getElementById('reminderModal'));
    modal.show();
    
    // 监听邮件提醒复选框变化
    document.getElementById('emailReminder').addEventListener('change', function() {
        const emailSection = document.getElementById('emailSection');
        emailSection.style.display = this.checked ? 'block' : 'none';
    });
}

async function setupReminders() {
    if (!currentReminderPlanId) {
        Utils.showToast('未选择计划', 'error');
        return;
    }
    
    const browserNotification = document.getElementById('browserNotification').checked;
    const emailReminder = document.getElementById('emailReminder').checked;
    const userEmail = document.getElementById('userEmail').value.trim();
    
    if (emailReminder && !userEmail) {
        Utils.showToast('请输入邮箱地址', 'error');
        return;
    }
    
    Utils.showLoading();
    
    try {
        // 设置浏览器通知权限
        if (browserNotification) {
            if (Notification.permission === 'default') {
                const permission = await Notification.requestPermission();
                if (permission !== 'granted') {
                    Utils.showToast('浏览器通知权限被拒绝', 'warning');
                }
            }
        }
        
        // 调用后端API设置提醒
        const response = await Utils.apiRequest(`/reminders/schedule?plan_id=${currentReminderPlanId}${userEmail ? `&user_email=${encodeURIComponent(userEmail)}` : ''}`, {
            method: 'POST'
        });
        
        if (response.success) {
            Utils.showToast('提醒设置成功！', 'success');
            
            // 保存提醒设置到本地
            localStorage.setItem('reminderSettings', JSON.stringify({
                planId: currentReminderPlanId,
                browserNotification,
                emailReminder,
                userEmail,
                dailyStartTime: document.getElementById('dailyStartTime').value,
                dailySummaryTime: document.getElementById('dailySummaryTime').value,
                timestamp: new Date().toISOString()
            }));
            
            // 如果启用浏览器通知，设置定时提醒
            if (browserNotification && response.data && response.data.reminders) {
                scheduleNotifications(response.data.reminders);
            }
            
            // 关闭模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('reminderModal'));
            modal.hide();
        }
        
    } catch (error) {
        console.error('设置提醒失败:', error);
        Utils.showToast('设置提醒失败: ' + error.message, 'error');
    } finally {
        Utils.hideLoading();
    }
}

function scheduleNotifications(reminders) {
    reminders.forEach(reminder => {
        const reminderTime = new Date(reminder.reminder_time);
        const now = new Date();
        const timeUntilReminder = reminderTime.getTime() - now.getTime();
        
        if (timeUntilReminder > 0) {
            setTimeout(() => {
                showBrowserNotification(reminder);
            }, timeUntilReminder);
            
            console.log(`已安排提醒: ${reminder.message} 在 ${reminderTime.toLocaleString()}`);
        }
    });
    
    Utils.showToast(`已安排${reminders.length}个提醒`, 'info');
}

function showBrowserNotification(reminder) {
    if (Notification.permission === 'granted') {
        const notification = new Notification('🤖 生活管家AI提醒', {
            body: reminder.message,
            icon: '/static/images/logo.png',
            badge: '/static/images/badge.png',
            tag: 'task-reminder',
            requireInteraction: true,
            actions: [
                {
                    action: 'start',
                    title: '开始任务'
                },
                {
                    action: 'snooze',
                    title: '稍后提醒'
                }
            ]
        });
        
        notification.onclick = function() {
            window.focus();
            notification.close();
            
            // 如果是任务提醒，可以跳转到任务详情
            if (reminder.task_id) {
                // 这里可以添加跳转逻辑
                Utils.showToast('点击查看任务详情', 'info');
            }
        };
        
        // 10秒后自动关闭
        setTimeout(() => notification.close(), 10000);
    }
}

// 页面加载时检查提醒设置
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否有保存的提醒设置
    const savedSettings = localStorage.getItem('reminderSettings');
    if (savedSettings) {
        try {
            const settings = JSON.parse(savedSettings);
            // 可以在这里恢复用户的提醒设置
            console.log('发现保存的提醒设置:', settings);
        } catch (error) {
            console.error('解析提醒设置失败:', error);
        }
    }
    
    // 检查浏览器通知权限
    if ('Notification' in window) {
        console.log('浏览器通知权限状态:', Notification.permission);
    }
}); 