# Import all models to ensure they are registered with SQLAlchemy
from app.models.kazanim import Kazanim
from app.models.etkinlik import Etkinlik
from app.models.curriculum import (
    ButunlesikBilesenler,
    Degerler,
    Egilimler,
    KavramsalBeceriler,
    SurecBilesenleri
)

__all__ = [
    "Kazanim",
    "Etkinlik",
    "ButunlesikBilesenler",
    "Degerler",
    "Egilimler",
    "KavramsalBeceriler",
    "SurecBilesenleri"
]