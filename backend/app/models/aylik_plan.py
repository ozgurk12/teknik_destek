from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class AylikPlan(Base):
    __tablename__ = "aylik_planlar"

    id = Column(Integer, primary_key=True, index=True)
    plan_adi = Column(String(500), nullable=False)
    yas_grubu = Column(String(50), nullable=False)
    ay = Column(String(20), nullable=False)
    yil = Column(Integer, nullable=False)

    # Alan Becerileri
    alan_becerileri = Column(JSON, nullable=False)

    # Kavramsal Beceriler
    kavramsal_beceriler = Column(JSON, nullable=False)

    # Eğilimler
    egilimler = Column(JSON, nullable=False)

    # Programlar Arası Bileşenler
    sosyal_duygusal_beceriler = Column(JSON, nullable=False)
    degerler = Column(JSON, nullable=False)
    okuryazarlik_becerileri = Column(JSON, nullable=False)

    # Öğrenme Çıktıları ve Süreç Bileşenleri
    ogrenme_ciktilari = Column(JSON, nullable=False)

    # Anahtar Kavramlar
    anahtar_kavramlar = Column(JSON, nullable=False)

    # Değerlendirme
    degerlendirme = Column(JSON, nullable=False)

    # Öğrenme-Öğretme Yaşantıları
    ogrenme_ogretme_yasantilari = Column(Text, nullable=False)

    # Farklılaştırma ve Zenginleştirme
    farklilastirma_zenginlestirme = Column(Text, nullable=True)

    # Destekleme
    destekleme = Column(Text, nullable=True)

    # Aile/Toplum Katılımı
    aile_toplum_katilimi = Column(Text, nullable=True)

    # Özel talimatlar
    custom_instructions = Column(Text, nullable=True)

    # AI üretimi
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)
    ai_prompt = Column(Text, nullable=True)

    # Kullanıcı bilgileri
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Seçilen kazanımlar ve curriculum bilgileri
    kazanim_ids = Column(JSON, nullable=True)
    curriculum_ids = Column(JSON, nullable=True)