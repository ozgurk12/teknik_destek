from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime
from uuid import UUID

class VideoGenerationBase(BaseModel):
    title: str
    prompt: str
    duration: Optional[int] = 30
    style: Optional[str] = "cinematic"
    music_genre: Optional[str] = None

class VideoGenerationCreate(VideoGenerationBase):
    image_urls: List[str] = []

class VideoGenerationUpdate(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    duration: Optional[int] = None
    style: Optional[str] = None
    music_genre: Optional[str] = None

class VideoGenerationInDBBase(VideoGenerationBase):
    id: int
    image_urls: List[str]
    status: str
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_by: Union[UUID, str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VideoGeneration(VideoGenerationInDBBase):
    pass

class VideoGenerationInDB(VideoGenerationInDBBase):
    external_job_id: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None

class ImageUploadResponse(BaseModel):
    url: str  # Base64 data URL for immediate display
    filename: str
    static_url: Optional[str] = None  # Static URL for permanent access

class VideoScriptGenerateRequest(BaseModel):
    ders: Optional[str] = None
    konu: Optional[str] = None
    yas_grubu: str
    kazanim_ids: Optional[List[int]] = None
    curriculum_ids: Optional[List[int]] = None
    video_yapisi: Optional[str] = "2 bölüm"
    bolum_sonu_etkinligi: Optional[str] = ""
    vurgu_noktalari: Optional[str] = ""
    kacinilacaklar: Optional[str] = ""
    custom_instructions: Optional[str] = None

class VideoScriptGenerateResponse(BaseModel):
    id: int
    script: str
    title: str
    ders: str
    konu: str
    yas_grubu: str