from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class VideoGeneration(Base):
    __tablename__ = "video_generations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    prompt = Column(Text, nullable=False)

    # Image URLs stored as JSON array
    image_urls = Column(JSON, default=list)

    # Video generation parameters
    duration = Column(Integer, default=30)  # seconds
    style = Column(String(100), default="cinematic")
    music_genre = Column(String(100), nullable=True)

    # Educational content fields
    ders = Column(String(100), nullable=True)
    konu = Column(String(200), nullable=True)
    yas_grubu = Column(String(50), nullable=True)
    kazanim_ids = Column(JSON, default=list)
    curriculum_ids = Column(JSON, default=list)
    video_yapisi = Column(String(100), nullable=True)
    bolum_sonu_etkinligi = Column(Text, nullable=True)
    vurgu_noktalari = Column(Text, nullable=True)
    kacinilacaklar = Column(Text, nullable=True)

    # Parsed script content (structured JSON)
    parsed_content = Column(JSON, nullable=True)

    # Kazanim details (full kazanim objects)
    kazanim_details = Column(JSON, nullable=True)

    # Curriculum details (full curriculum objects)
    curriculum_details = Column(JSON, nullable=True)

    # Status tracking
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    video_url = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)

    # Metadata
    external_job_id = Column(String(200), nullable=True)  # External API job ID
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)

    # User relationship
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())