from .goals import router as goals_router
from .tasks import router as tasks_router
from .users import router as users_router
from .dashboard import router as dashboard_router

__all__ = ['goals_router', 'tasks_router', 'users_router', 'dashboard_router'] 