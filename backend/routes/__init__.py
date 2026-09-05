from backend.routes.dashboard import router as dashboard_router
from backend.routes.projects import router as projects_router
from backend.routes.contractors import router as contractors_router
from backend.routes.constituencies import router as constituencies_router
from backend.routes.alerts import router as alerts_router
from backend.routes.map import router as map_router
from backend.routes.insights import router as insights_router
from backend.routes.model import router as model_router
from backend.routes.data import router as data_router

__all__ = [
    "dashboard_router",
    "projects_router",
    "contractors_router",
    "constituencies_router",
    "alerts_router",
    "map_router",
    "insights_router",
    "model_router",
    "data_router"
]
