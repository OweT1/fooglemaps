from .auth import router as auth_router
from .settings import router as settings_router
from .posts import router as posts_router
from .creators import router as creators_router
from .places import router as places_router
from .cuisines import router as cuisines_router

__all__ = [
    "auth_router",
    "settings_router",
    "posts_router",
    "creators_router",
    "places_router",
    "cuisines_router",
]
