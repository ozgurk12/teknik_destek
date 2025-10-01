# Import all models here so Alembic can detect them
# This file is specifically for Alembic to discover all models

from app.db.base_class import Base  # noqa
from app.models.user import User, Module, user_modules  # noqa
from app.models.kazanim import Kazanim  # noqa
from app.models.etkinlik import Etkinlik  # noqa
from app.models.gunluk_plan import GunlukPlan  # noqa
from app.models.aylik_plan import AylikPlan  # noqa
from app.models.curriculum import (  # noqa
    ButunlesikBilesenler,
    Degerler,
    Egilimler,
    KavramsalBeceriler,
    SurecBilesenleri
)