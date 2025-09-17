from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.db.base import BaseModel

class Kazanim(BaseModel):
    __tablename__ = "kazanimlar"
    
    id = Column(Integer, primary_key=True, index=True)
    yas_grubu = Column(String(20), nullable=False, index=True)
    ders = Column(String(50), nullable=False, index=True)
    alan_becerileri = Column(Text)
    butunlesik_beceriler = Column(Text)
    surec_bilesenleri = Column(Text)
    ogrenme_ciktilari = Column(Text)
    alt_ogrenme_ciktilari = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Composite indexes for better query performance
    __table_args__ = (
        Index('idx_kazanim_yas_ders', 'yas_grubu', 'ders'),
    )
    
    def __repr__(self):
        return f"<Kazanim(id={self.id}, yas_grubu={self.yas_grubu}, ders={self.ders})>"