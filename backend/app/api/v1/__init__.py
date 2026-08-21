"""API v1 module for Open Body Tracker."""

from .auth_routes import router as auth_router
from .user import router as user_router
from .assessments import router as assessments_router
from .data import router as data_router
from .metrics import router as metrics_router

__all__ = ["auth_router", "user_router", "assessments_router", "data_router", "metrics_router"]
