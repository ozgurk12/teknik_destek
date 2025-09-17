# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Date, ARRAY
from sqlalchemy.sql import func
from app.db.base_class import Base

class GunlukPlan(Base):
    __tablename__ = "gunluk_planlar"

    id = Column(Integer, primary_key=True, index=True)

    # Temel Bilgiler
    plan_adi = Column(String(255), nullable=False)
    tarih = Column(Date, nullable=False)
    yas_grubu = Column(String(50), nullable=False)
    sinif = Column(String(100))
    ogretmen = Column(String(255))

    # Seçilen Etkinlikler (ID listesi)
    etkinlik_idleri = Column(ARRAY(Integer), default=[])

    # Alan Becerileri - Kazanımlardan otomatik toplanacak
    alan_becerileri = Column(JSON, default={})

    # Kavramsal Beceriler - Curriculumlardan toplanacak
    kavramsal_beceriler = Column(JSON, default={})

    # Eğilimler
    egilimler = Column(JSON, default={})

    # Programlar Arası Bileşenler
    programlar_arasi_bilesenler = Column(JSON, default={})  # Combined field for frontend
    sosyal_duygusal_beceriler = Column(JSON, default={})
    degerler = Column(JSON, default={})
    okuryazarlik_becerileri = Column(JSON, default={})

    # Öğrenme Çıktıları ve Süreç Bileşenleri
    ogrenme_ciktilari = Column(JSON, default={})

    # İçerik Çerçevesi
    kavramlar = Column(Text)
    sozcukler = Column(Text)
    materyaller = Column(Text)
    egitim_ortamlari = Column(Text)

    # Öğrenme-Öğretme Yaşantıları
    gune_baslama = Column(Text)
    ogrenme_merkezleri = Column(Text)
    beslenme_toplanma = Column(Text)
    etkinlikler = Column(Text)  # Seçilen etkinliklerin detaylı içeriği
    degerlendirme = Column(Text)

    # Farklılaştırma
    farklilastirma = Column(JSON, default={})  # Combined field for frontend
    zenginlestirme = Column(Text)
    destekleme = Column(Text)

    # Aile/Toplum Katılımı
    aile_toplum_katilimi = Column(JSON, default={})  # Combined field for frontend
    aile_katilimi = Column(Text)
    toplum_katilimi = Column(Text)

    # Notlar
    notlar = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255))

    # AI desteği ile oluşturuldu mu?
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)

    def __repr__(self):
        return f"<GunlukPlan(id={self.id}, plan_adi='{self.plan_adi}', tarih={self.tarih})>"