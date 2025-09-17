from fastapi import APIRouter
from app.api.endpoints import kazanimlar, etkinlikler, curriculum, gunluk_planlar

api_router = APIRouter()

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