from pydantic import BaseModel
from typing import List, Optional, Dict, Any


# Bütünleşik Bileşenler Schemas
class ButunlesikBilesenlerBase(BaseModel):
    butunlesik_bilesenler: str
    alt_butunlesik_bilesenler: Optional[str] = None
    surec_bilesenleri: Optional[str] = None


class ButunlesikBilesenlerCreate(ButunlesikBilesenlerBase):
    pass


class ButunlesikBilesenler(ButunlesikBilesenlerBase):
    id: int

    class Config:
        from_attributes = True


# Değerler Schemas
class DegerlerBase(BaseModel):
    ana_deger_kodu: str
    ana_deger_adi: str
    ana_deger_aciklamasi: Optional[str] = None
    alt_deger_kodu: Optional[str] = None
    alt_deger_adi: Optional[str] = None
    davranis_gostergesi_kodu: Optional[str] = None
    davranis_gostergesi_aciklamasi: Optional[str] = None
    ogretim_yontemleri: Optional[str] = None


class DegerlerCreate(DegerlerBase):
    pass


class Degerler(DegerlerBase):
    id: int

    class Config:
        from_attributes = True


class DavranisGostergesi(BaseModel):
    kod: str
    aciklama: str
    ogretim_yontemleri: Optional[str] = None


class AltDeger(BaseModel):
    kod: str
    adi: str
    davranis_gostergeleri: List[DavranisGostergesi]


class DegerGrouped(BaseModel):
    kod: str
    aciklama: Optional[str] = None
    alt_degerler: List[AltDeger]


# Eğilimler Schemas
class EgilimlerBase(BaseModel):
    ana_egilim: str
    alt_egilim: str


class EgilimlerCreate(EgilimlerBase):
    pass


class Egilimler(EgilimlerBase):
    id: int

    class Config:
        from_attributes = True


class EgilimlerGrouped(BaseModel):
    ana_egilim: str
    alt_egilimler: List[str]


# Kavramsal Beceriler Schemas
class KavramsalBecerilerBase(BaseModel):
    ana_beceri_kategorisi: str
    ana_beceri_kodu: str
    ana_beceri_adi: str
    alt_beceri_kodu: Optional[str] = None
    alt_beceri_adi: Optional[str] = None
    surec_bileseni_kodu: Optional[str] = None
    aciklama: Optional[str] = None


class KavramsalBecerilerCreate(KavramsalBecerilerBase):
    pass


class KavramsalBeceriler(KavramsalBecerilerBase):
    id: int

    class Config:
        from_attributes = True


class BeceriItem(BaseModel):
    kod: str
    adi: str
    alt_beceri_kodu: Optional[str] = None
    alt_beceri_adi: Optional[str] = None
    surec_bileseni_kodu: Optional[str] = None
    aciklama: Optional[str] = None


class KavramsalBecerilerGrouped(BaseModel):
    kategori: str
    beceriler: List[BeceriItem]


# Süreç Bileşenleri Schemas
class SurecBilesenleriBase(BaseModel):
    surec_bileseni_kodu: str
    surec_bileseni_adi: str
    gosterge_kodu: Optional[str] = None
    gosterge_aciklamasi: Optional[str] = None


class SurecBilesenleriCreate(SurecBilesenleriBase):
    pass


class SurecBilesenleri(SurecBilesenleriBase):
    id: int

    class Config:
        from_attributes = True


class Gosterge(BaseModel):
    kod: str
    aciklama: str


class SurecBileseniGrouped(BaseModel):
    kod: str
    adi: str
    gostergeler: List[Gosterge]


# Combined Selection Schema for Activity Creation
class CurriculumSelection(BaseModel):
    """Schema for curriculum selections in activity creation"""
    butunlesik_bilesenler_ids: List[int] = []
    degerler_ids: List[int] = []
    egilimler_ids: List[int] = []
    kavramsal_beceriler_ids: List[int] = []
    surec_bilesenleri_ids: List[int] = []
    
    class Config:
        from_attributes = True