from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class KazanimBase(BaseModel):
    yas_grubu: str = Field(..., description="Age group (e.g., 36-48, 48-60, 60-72)")
    ders: str = Field(..., description="Subject/Course name")
    alan_becerileri: Optional[str] = Field(None, description="Field skills")
    butunlesik_beceriler: Optional[str] = Field(None, description="Integrated skills")
    surec_bilesenleri: Optional[str] = Field(None, description="Process components")
    ogrenme_ciktilari: Optional[str] = Field(None, description="Learning outcomes")
    alt_ogrenme_ciktilari: Optional[str] = Field(None, description="Sub-learning outcomes")

class KazanimCreate(KazanimBase):
    pass

class KazanimUpdate(BaseModel):
    yas_grubu: Optional[str] = None
    ders: Optional[str] = None
    alan_becerileri: Optional[str] = None
    butunlesik_beceriler: Optional[str] = None
    surec_bilesenleri: Optional[str] = None
    ogrenme_ciktilari: Optional[str] = None
    alt_ogrenme_ciktilari: Optional[str] = None

class KazanimResponse(KazanimBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class KazanimListResponse(BaseModel):
    total: int
    items: List[KazanimResponse]
    page: int
    page_size: int
    
class KazanimFilter(BaseModel):
    yas_grubu: Optional[str] = None
    ders: Optional[str] = None
    search: Optional[str] = None