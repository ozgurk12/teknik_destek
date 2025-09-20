from fastapi import APIRouter
from app.api.endpoints import kazanimlar, etkinlikler, curriculum, gunluk_planlar, auth, users, modules

api_router = APIRouter()

# Authentication endpoints (public)
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# User management endpoints
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Module management endpoints
api_router.include_router(
    modules.router,
    prefix="/modules",
    tags=["Modules"]
)

# Existing endpoints
api_router.include_router(
    kazanimlar.router,
    prefix="/kazanimlar",
    tags=["Kazanımlar"]
)

api_router.include_router(
    etkinlikler.router,
    prefix="/etkinlikler",
    tags=["Etkinlikler"]
)

api_router.include_router(
    curriculum.router,
    prefix="/curriculum",
    tags=["Müfredat Verileri"]
)

api_router.include_router(
    gunluk_planlar.router,
    tags=["Günlük Planlar"]
)