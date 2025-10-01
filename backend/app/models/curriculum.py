from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class ButunlesikBilesenler(Base):
    __tablename__ = "butunlesik_bilesenler"
    
    id = Column(Integer, primary_key=True, index=True)
    butunlesik_bilesenler = Column(String(255), nullable=False)
    alt_butunlesik_bilesenler = Column(String(255))
    surec_bilesenleri = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "butunlesik_bilesenler": self.butunlesik_bilesenler,
            "alt_butunlesik_bilesenler": self.alt_butunlesik_bilesenler,
            "surec_bilesenleri": self.surec_bilesenleri
        }


class Degerler(Base):
    __tablename__ = "degerler"
    
    id = Column(Integer, primary_key=True, index=True)
    ana_deger_kodu = Column(String(20), nullable=False)
    ana_deger_adi = Column(String(100), nullable=False)
    ana_deger_aciklamasi = Column(Text)
    alt_deger_kodu = Column(String(20))
    alt_deger_adi = Column(String(255))
    davranis_gostergesi_kodu = Column(String(20))
    davranis_gostergesi_aciklamasi = Column(Text)
    ogretim_yontemleri = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "ana_deger_kodu": self.ana_deger_kodu,
            "ana_deger_adi": self.ana_deger_adi,
            "ana_deger_aciklamasi": self.ana_deger_aciklamasi,
            "alt_deger_kodu": self.alt_deger_kodu,
            "alt_deger_adi": self.alt_deger_adi,
            "davranis_gostergesi_kodu": self.davranis_gostergesi_kodu,
            "davranis_gostergesi_aciklamasi": self.davranis_gostergesi_aciklamasi,
            "ogretim_yontemleri": self.ogretim_yontemleri
        }


class Egilimler(Base):
    __tablename__ = "egilimler"
    
    id = Column(Integer, primary_key=True, index=True)
    ana_egilim = Column(String(100), nullable=False)
    alt_egilim = Column(String(100), nullable=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "ana_egilim": self.ana_egilim,
            "alt_egilim": self.alt_egilim
        }


class KavramsalBeceriler(Base):
    __tablename__ = "kavramsal_beceriler"
    
    id = Column(Integer, primary_key=True, index=True)
    ana_beceri_kategorisi = Column(String(100), nullable=False)
    ana_beceri_kodu = Column(String(20), nullable=False)
    ana_beceri_adi = Column(String(100), nullable=False)
    alt_beceri_kodu = Column(String(20))
    alt_beceri_adi = Column(String(100))
    surec_bileseni_kodu = Column(Text)  # Changed from String(20) to Text for longer values
    aciklama = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "ana_beceri_kategorisi": self.ana_beceri_kategorisi,
            "ana_beceri_kodu": self.ana_beceri_kodu,
            "ana_beceri_adi": self.ana_beceri_adi,
            "alt_beceri_kodu": self.alt_beceri_kodu,
            "alt_beceri_adi": self.alt_beceri_adi,
            "surec_bileseni_kodu": self.surec_bileseni_kodu,
            "aciklama": self.aciklama
        }


class SurecBilesenleri(Base):
    __tablename__ = "surec_bilesenleri"
    
    id = Column(Integer, primary_key=True, index=True)
    surec_bileseni_kodu = Column(String(50), nullable=False)
    surec_bileseni_adi = Column(Text, nullable=False)
    gosterge_kodu = Column(String(50))
    gosterge_aciklamasi = Column(Text)
    
    def to_dict(self):
        return {
            "id": self.id,
            "surec_bileseni_kodu": self.surec_bileseni_kodu,
            "surec_bileseni_adi": self.surec_bileseni_adi,
            "gosterge_kodu": self.gosterge_kodu,
            "gosterge_aciklamasi": self.gosterge_aciklamasi
        }