from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ARRAY, Index, JSON
from sqlalchemy.sql import func
from app.db.base import BaseModel

class Etkinlik(BaseModel):
    __tablename__ = "etkinlikler"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Temel Bilgiler
    etkinlik_adi = Column(String(255), nullable=False)
    alan_adi = Column(String(100), index=True)
    yas_grubu = Column(String(20), index=True)
    sure = Column(Integer)  # dakika cinsinden
    uygulama_yeri = Column(String(100))
    
    # Etkinlik Detayları
    etkinlik_amaci = Column(Text)
    materyaller = Column(Text)
    uygulama_sureci = Column(Text)
    giris_bolumu = Column(Text)
    gelisme_bolumu = Column(Text)
    yansima_cemberi = Column(Text)
    sonuc_bolumu = Column(Text)
    
    # Uyarlama ve Farklılaştırma
    uyarlama = Column(Text)
    farklilastirma_kapsayicilik = Column(Text)
    
    # Değerlendirme
    degerlendirme_program = Column(Text)
    degerlendirme_beceriler = Column(Text)
    degerlendirme_ogrenciler = Column(Text)
    
    # İlişkili Kazanımlar
    kazanim_idleri = Column(ARRAY(Integer))
    kazanim_metinleri = Column(ARRAY(Text))

    # Müfredat Bileşenleri (Kazanımlardan çıkarılan)
    curriculum_data = Column(JSON)  # Tüm müfredat verileri JSON formatında
    alan_becerileri = Column(JSON)  # {"Matematik Alanı": ["MAB1. ...", "MAB2. ..."]}
    ogrenme_ciktilari = Column(JSON)  # {"Matematik Alanı": ["MAB.1.a ...", "MAB.2.b ..."]}
    kavramsal_beceriler = Column(ARRAY(Text))  # ["KB1.5.Bulmak", "KB2.7.SB1 ..."]
    egilimler = Column(ARRAY(Text))  # ["E1.1. Merak", "E3.2. Yaratıcılık"]
    sosyal_duygusal = Column(ARRAY(Text))  # ["SDB2.1.SB2. ..."]
    degerler = Column(ARRAY(Text))  # ["D5.2. Çevreye karşı duyarlılık"]
    okuryazarlik = Column(ARRAY(Text))  # ["OB4.2.SB1. ..."]

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100))
    ai_generated = Column(Boolean, default=True)
    prompt_used = Column(Text)
    model_version = Column(String(50), default='gemini-1.5-flash')
    json_data = Column(Text)  # Store original JSON structure
    
    # Indexes
    __table_args__ = (
        Index('idx_etkinlik_alan_yas', 'alan_adi', 'yas_grubu'),
    )
    
    def __repr__(self):
        return f"<Etkinlik(id={self.id}, etkinlik_adi={self.etkinlik_adi}, alan_adi={self.alan_adi})>"