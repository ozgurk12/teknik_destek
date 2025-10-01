from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

class EtkinlikBase(BaseModel):
    etkinlik_adi: str = Field(..., description="Activity name")
    alan_adi: Optional[str] = Field(None, description="Field/Subject area")
    yas_grubu: Optional[str] = Field(None, description="Age group")
    sure: Optional[int] = Field(None, description="Duration in minutes")
    uygulama_yeri: Optional[str] = Field(None, description="Application location")
    etkinlik_amaci: Optional[str] = Field(None, description="Activity objectives")
    materyaller: Optional[str] = Field(None, description="Materials needed")
    uygulama_sureci: Optional[str] = Field(None, description="Application process")
    giris_bolumu: Optional[str] = Field(None, description="Introduction section")
    gelisme_bolumu: Optional[str] = Field(None, description="Development section")
    yansima_cemberi: Optional[str] = Field(None, description="Reflection circle")
    sonuc_bolumu: Optional[str] = Field(None, description="Conclusion section")
    uyarlama: Optional[str] = Field(None, description="Adaptations")
    farklilastirma_kapsayicilik: Optional[str] = Field(None, description="Differentiation and inclusivity")
    degerlendirme_program: Optional[str] = Field(None, description="Program evaluation")
    degerlendirme_beceriler: Optional[str] = Field(None, description="Skills evaluation")
    degerlendirme_ogrenciler: Optional[str] = Field(None, description="Student evaluation")

class EtkinlikCreate(EtkinlikBase):
    kazanim_idleri: Optional[List[int]] = Field(None, description="Related learning outcome IDs")
    kazanim_metinleri: Optional[List[str]] = Field(None, description="Related learning outcome texts")
    custom_instructions: Optional[str] = Field(None, description="User's custom instructions")
    ai_generated: bool = Field(True, description="Whether AI generated")
    prompt_used: Optional[str] = Field(None, description="Prompt used for generation")
    model_version: Optional[str] = Field(None, description="AI model version")

class EtkinlikUpdate(BaseModel):
    etkinlik_adi: Optional[str] = None
    alan_adi: Optional[str] = None
    yas_grubu: Optional[str] = None
    sure: Optional[int] = None
    uygulama_yeri: Optional[str] = None
    etkinlik_amaci: Optional[str] = None
    materyaller: Optional[str] = None
    uygulama_sureci: Optional[str] = None
    giris_bolumu: Optional[str] = None
    gelisme_bolumu: Optional[str] = None
    yansima_cemberi: Optional[str] = None
    sonuc_bolumu: Optional[str] = None
    uyarlama: Optional[str] = None
    farklilastirma_kapsayicilik: Optional[str] = None
    degerlendirme_program: Optional[str] = None
    degerlendirme_beceriler: Optional[str] = None
    degerlendirme_ogrenciler: Optional[str] = None

class EtkinlikResponse(EtkinlikBase):
    id: int
    kazanim_idleri: Optional[List[int]] = None
    kazanim_metinleri: Optional[List[str]] = None
    custom_instructions: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: Optional[UUID] = None
    created_by_username: Optional[str] = None
    created_by_fullname: Optional[str] = None
    ai_generated: bool
    prompt_used: Optional[str] = None
    model_version: Optional[str] = None
    # Curriculum fields
    curriculum_data: Optional[Any] = None
    alan_becerileri: Optional[Any] = None
    ogrenme_ciktilari: Optional[Any] = None
    kavramsal_beceriler: Optional[List[str]] = None
    egilimler: Optional[List[str]] = None
    sosyal_duygusal: Optional[List[str]] = None
    degerler: Optional[List[str]] = None
    okuryazarlik: Optional[List[str]] = None

    class Config:
        from_attributes = True

class EtkinlikGenerateRequest(BaseModel):
    kazanim_ids: List[int] = Field(..., description="List of learning outcome IDs to generate activity for", min_items=1)
    custom_prompt: Optional[str] = Field(None, description="Custom instructions for activity generation")
    aylik_plan_id: Optional[int] = Field(None, description="Monthly plan ID to auto-fill kazanim and curriculum")
    # Bütünleşik beceriler - frontend'ten seçilenler
    kavramsal_beceriler: Optional[List[str]] = Field(None, description="Selected conceptual skills")
    egilimler: Optional[List[str]] = Field(None, description="Selected tendencies")
    sosyal_duygusal: Optional[List[str]] = Field(None, description="Selected social-emotional skills")
    degerler: Optional[List[str]] = Field(None, description="Selected values")
    okuryazarlik: Optional[List[str]] = Field(None, description="Selected literacy skills")

    class Config:
        json_schema_extra = {
            "example": {
                "kazanim_ids": [1, 2, 3],
                "custom_prompt": "Etkinlik dışarıda yapılsın ve müzik içersin",
                "kavramsal_beceriler": ["KB1.1. Saymak"],
                "egilimler": ["E1.1. Merak"],
                "degerler": ["D1. ADALET"]
            }
        }

class EtkinlikGenerateResponse(BaseModel):
    success: bool
    message: str
    etkinlik: Optional[EtkinlikResponse] = None
    error: Optional[str] = None

class PaginatedEtkinlikResponse(BaseModel):
    items: List[EtkinlikResponse]
    total: int
    page: int
    page_size: int
    total_pages: int