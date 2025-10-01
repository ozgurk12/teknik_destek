# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from uuid import UUID

class GunlukPlanBase(BaseModel):
    plan_adi: str = Field(..., description="Plan adı")
    tarih: date = Field(..., description="Plan tarihi")
    yas_grubu: str = Field(..., description="Yaş grubu (örn: 36-48 ay)")
    sinif: Optional[str] = Field(None, description="Sınıf adı")
    ogretmen: Optional[str] = Field(None, description="Öğretmen adı")
    etkinlik_idleri: List[int] = Field(default=[], description="Seçilen etkinliklerin ID'leri")

    # İçerik Çerçevesi
    kavramlar: Optional[str] = None
    sozcukler: Optional[str] = None
    materyaller: Optional[str] = None
    egitim_ortamlari: Optional[str] = None

    # Öğrenme-Öğretme Yaşantıları
    gune_baslama: Optional[str] = None
    ogrenme_merkezleri: Optional[str] = None
    beslenme_toplanma: Optional[str] = None
    degerlendirme: Optional[str] = None

    # Farklılaştırma
    zenginlestirme: Optional[str] = None
    destekleme: Optional[str] = None

    # Aile/Toplum Katılımı
    aile_katilimi: Optional[str] = None
    toplum_katilimi: Optional[str] = None

    notlar: Optional[str] = None

class GunlukPlanCreate(GunlukPlanBase):
    pass

class GunlukPlanUpdate(BaseModel):
    plan_adi: Optional[str] = None
    tarih: Optional[date] = None
    yas_grubu: Optional[str] = None
    sinif: Optional[str] = None
    ogretmen: Optional[str] = None
    etkinlik_idleri: Optional[List[int]] = None
    kavramlar: Optional[str] = None
    sozcukler: Optional[str] = None
    materyaller: Optional[str] = None
    egitim_ortamlari: Optional[str] = None
    gune_baslama: Optional[str] = None
    ogrenme_merkezleri: Optional[str] = None
    beslenme_toplanma: Optional[str] = None
    degerlendirme: Optional[str] = None
    zenginlestirme: Optional[str] = None
    destekleme: Optional[str] = None
    aile_katilimi: Optional[str] = None
    toplum_katilimi: Optional[str] = None
    notlar: Optional[str] = None

class GunlukPlanInDB(GunlukPlanBase):
    id: int
    alan_becerileri: Dict[str, Any] = {}
    kavramsal_beceriler: Any = []  # Can be Dict or List
    egilimler: Any = []  # Can be Dict or List
    programlar_arasi_bilesenler: Dict[str, Any] = {}  # Combined field for frontend
    sosyal_duygusal_beceriler: Any = []  # Can be Dict or List
    degerler: Any = []  # Can be Dict or List
    okuryazarlik_becerileri: Any = []  # Can be Dict or List
    ogrenme_ciktilari: Dict[str, Any] = {}
    farklilastirma: Dict[str, Any] = {}  # Combined field for frontend
    aile_toplum_katilimi: Dict[str, Any] = {}  # Combined field for frontend
    etkinlikler: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[UUID] = None
    created_by_username: Optional[str] = None
    created_by_fullname: Optional[str] = None
    ai_generated: bool = False
    ai_prompt: Optional[str] = None

    class Config:
        from_attributes = True

class GunlukPlanResponse(GunlukPlanInDB):
    etkinlik_detaylari: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="Seçilen etkinliklerin detaylı bilgileri"
    )

class GunlukPlanGenerateRequest(BaseModel):
    etkinlik_idleri: List[int] = Field(..., description="Kullanılacak etkinlik ID'leri")
    tarih: date = Field(..., description="Plan tarihi")
    yas_grubu: str = Field(..., description="Yaş grubu")
    custom_prompt: Optional[str] = Field(None, description="Özel AI promptu")

class GunlukPlanGenerateResponse(BaseModel):
    success: bool
    message: str
    plan_id: Optional[int] = None
    error: Optional[str] = None