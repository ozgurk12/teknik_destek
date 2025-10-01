from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from uuid import UUID

class AylikPlanBase(BaseModel):
    plan_adi: str
    yas_grubu: str
    ay: str
    yil: int
    alan_becerileri: Dict[str, Any]
    kavramsal_beceriler: Dict[str, Any]
    egilimler: Dict[str, Any]
    sosyal_duygusal_beceriler: Dict[str, Any]
    degerler: Dict[str, Any]
    okuryazarlik_becerileri: Dict[str, Any]
    ogrenme_ciktilari: Dict[str, Any]
    anahtar_kavramlar: List[str]
    degerlendirme: Dict[str, Any]
    ogrenme_ogretme_yasantilari: str
    farklilastirma_zenginlestirme: Optional[str] = None
    destekleme: Optional[str] = None
    aile_toplum_katilimi: Optional[str] = None
    custom_instructions: Optional[str] = None
    kazanim_ids: Optional[List[int]] = None
    curriculum_ids: Optional[List[int]] = None

class AylikPlanCreate(BaseModel):
    yas_grubu: str
    ay: str
    kazanim_ids: List[int]
    curriculum_ids: Optional[List[int]] = None
    custom_instructions: Optional[str] = None

class AylikPlanUpdate(AylikPlanBase):
    pass

class AylikPlanInDBBase(AylikPlanBase):
    id: int
    ai_generated: bool
    ai_model: Optional[str] = None
    created_by: Union[UUID, str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AylikPlan(AylikPlanInDBBase):
    pass

class AylikPlanInDB(AylikPlanInDBBase):
    ai_prompt: Optional[str] = None

class AylikPlanGenerateRequest(BaseModel):
    yas_grubu: str
    ay: str
    kazanim_ids: List[int]
    curriculum_ids: Optional[List[int]] = None
    custom_instructions: Optional[str] = None

class AylikPlanGenerateResponse(BaseModel):
    id: int
    plan_adi: str
    yas_grubu: str
    ay: str
    yil: int
    alan_becerileri: Dict[str, Any]
    kavramsal_beceriler: Dict[str, Any]
    egilimler: Dict[str, Any]
    sosyal_duygusal_beceriler: Dict[str, Any]
    degerler: Dict[str, Any]
    okuryazarlik_becerileri: Dict[str, Any]
    ogrenme_ciktilari: Dict[str, Any]
    anahtar_kavramlar: List[str]
    degerlendirme: Dict[str, Any]
    ogrenme_ogretme_yasantilari: str
    farklilastirma_zenginlestirme: Optional[str] = None
    destekleme: Optional[str] = None
    aile_toplum_katilimi: Optional[str] = None
    created_at: datetime