from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import aiofiles
import aiohttp
import os
import uuid
from pathlib import Path
import logging
import base64

from app import schemas
from app.api import deps
from app.models.user import User
from app.models.video_generation import VideoGeneration
from app.schemas.video_generation import (
    VideoGenerationCreate,
    VideoGenerationUpdate,
    VideoGeneration as VideoGenerationSchema,
    ImageUploadResponse,
    VideoScriptGenerateRequest,
    VideoScriptGenerateResponse
)
from app.services.video_generation_service import video_generation_service
from app.services.script_parser import VideoScriptParser
from app.models.kazanim import Kazanim
from app.models.curriculum import (
    ButunlesikBilesenler,
    Degerler,
    Egilimler,
    KavramsalBeceriler,
    SurecBilesenleri
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Image upload directory
import tempfile
import os

# Use local directory that will be served by FastAPI
# Create a directory inside the backend project
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "static" / "video-images"

# Always use resim.hautmedia.com for image URLs
# This domain should be configured to serve static files from the upload directory
UPLOAD_URL_BASE = "https://resim.hautmedia.com/video-images"

# Check if we're in production
IS_PRODUCTION = os.getenv('ENVIRONMENT') == 'production'

@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
    *,
    db: AsyncSession = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Upload an image for video generation
    """
    # Check module access
    if not current_user.has_module_access("video_generation"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")
    # Check file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )

    # Check file size (max 10MB)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max size is 10MB")

    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{current_user.id}_{uuid.uuid4()}.{file_extension}"

    # Save file locally first
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / unique_filename
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    # Always try to upload to production server for resim.hautmedia.com
    # This ensures images are available on the CDN
    try:
        # Upload to resim.hautmedia.com endpoint
        production_upload_url = "https://resim.hautmedia.com/upload"

        # Alternative: Upload to etkinlik.hautmedia.com first
        if not IS_PRODUCTION:
            production_api_url = "https://etkinlik.hautmedia.com/api/v1/video-generation/production-upload"

            async with aiohttp.ClientSession() as session:
                # Create form data
                form = aiohttp.FormData()
                form.add_field('file',
                            contents,
                            filename=unique_filename,
                            content_type=file.content_type)
                form.add_field('filename', unique_filename)

                # Send to production
                async with session.post(production_api_url, data=form) as resp:
                    if resp.status == 200:
                        logger.info(f"Image uploaded to production: {unique_filename}")
                    else:
                        logger.warning(f"Failed to upload to production: {await resp.text()}")
    except Exception as e:
        logger.error(f"Failed to upload to production server: {e}")
        # Continue anyway, we have local copy

    # Convert to base64 for immediate return
    with open(file_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

    # Log file save for debugging
    logger.info(f"Image saved to: {file_path}")
    logger.info(f"File exists: {file_path.exists()}")

    # Return both URL and base64 data
    # Return the actual URL that can be accessed via static serving
    actual_url = f"{UPLOAD_URL_BASE}/{unique_filename}"

    return ImageUploadResponse(
        url=f"data:image/{file_extension};base64,{image_base64}",  # For immediate display
        filename=unique_filename,
        static_url=actual_url  # For storage and future reference
    )

@router.post("/production-upload")
async def production_upload_image(
    *,
    file: UploadFile = File(...),
    filename: str = Form(...)
) -> Any:
    """
    Production-only endpoint to receive images from development environment
    This should only work on production server
    """
    if not IS_PRODUCTION:
        raise HTTPException(status_code=403, detail="This endpoint is only available in production")

    # Save file directly to production directory
    contents = await file.read()
    file_path = UPLOAD_DIR / filename

    # Create directory if it doesn't exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    return {"status": "success", "filename": filename}

@router.post("/", response_model=VideoGenerationSchema)
async def create_video_generation(
    *,
    db: AsyncSession = Depends(deps.get_db),
    video_in: VideoGenerationCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new video generation request
    """
    # Check module access
    if not current_user.has_module_access("video_generation"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")
    video_data = video_in.dict()
    image_urls_input = video_data.pop('image_urls', [])

    # Log the received image URLs for debugging
    logger.info(f"Received {len(image_urls_input)} image URLs for video generation")

    # Store actual URLs (not base64) in database
    stored_urls = []
    for url in image_urls_input:
        if url.startswith('data:'):
            # Extract base64 data and save to file
            try:
                # Parse data URL
                header, encoded = url.split(',', 1)
                # Decode base64
                image_data = base64.b64decode(encoded)

                # Generate filename
                filename = f"{current_user.id}_{uuid.uuid4()}.jpg"
                file_path = UPLOAD_DIR / filename

                # Ensure directory exists
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

                # Save file
                with open(file_path, 'wb') as f:
                    f.write(image_data)

                logger.info(f"Saved base64 image to: {file_path}")
                static_url = f"{UPLOAD_URL_BASE}/{filename}"
                stored_urls.append(static_url)
                logger.info(f"Image will be accessible at: {static_url}")
            except Exception as e:
                logger.error(f"Failed to save base64 image: {e}")
                # Store the base64 URL as fallback
                stored_urls.append(url)
        else:
            stored_urls.append(url)

    video_generation = VideoGeneration(
        **video_data,
        image_urls=stored_urls,
        created_by=current_user.id,
        status="pending"
    )

    db.add(video_generation)
    await db.commit()
    await db.refresh(video_generation)

    # Trigger webhook if configured
    webhook_url = os.environ.get('VIDEO_GENERATION_WEBHOOK_URL')
    if not webhook_url:
        # Default webhook URL for testing
        webhook_url = "http://localhost:5678/webhook-test/a471b215-246c-4cc4-bf2b-3bad4c6eeea9"

    # Read images and convert to base64 for webhook
    image_base64_list = []

    # For webhook, we need the actual base64 data from input
    # Since we're now storing base64 in image_urls_input, we'll use that
    for i, url in enumerate(image_urls_input):
        if url.startswith('data:'):
            # It's already base64
            image_base64_list.append({
                "filename": f"image_{i}.jpg",
                "data": url,
                "url": stored_urls[i] if i < len(stored_urls) else url
            })
        else:
            # Try to read from disk
            filename = url.split('/')[-1]
            file_path = UPLOAD_DIR / filename

            if file_path.exists():
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    image_base64_list.append({
                        "filename": filename,
                        "data": f"data:image/jpeg;base64,{image_base64}",
                        "url": url
                    })
            else:
                image_base64_list.append({
                    "filename": filename,
                    "url": url
                })

    # Prepare webhook payload
    webhook_payload = {
        "id": video_generation.id,
        "title": video_generation.title,
        "prompt": video_generation.prompt,
        "images": image_base64_list,  # Send base64 encoded images
        "image_urls": stored_urls,  # Also send URLs for reference
        "duration": video_generation.duration,
        "style": video_generation.style,
        "music_genre": video_generation.music_genre,
        "created_by": str(current_user.id),
        "user_email": current_user.email,
        "status": "pending"
    }

    # Send webhook asynchronously (using POST)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=webhook_payload) as response:
                if response.status == 200:
                    logger.info(f"Webhook sent successfully for video generation {video_generation.id}")
                    logger.info(f"Webhook payload: {webhook_payload}")
                else:
                    logger.error(f"Webhook failed with status {response.status}: {await response.text()}")
    except Exception as e:
        logger.error(f"Failed to send webhook: {str(e)}")
        # Don't fail the request if webhook fails

    return video_generation

@router.get("/", response_model=List[VideoGenerationSchema])
async def read_video_generations(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve all video generations (public endpoint)
    """
    query = select(VideoGeneration).order_by(VideoGeneration.created_at.desc())

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    video_generations = result.scalars().all()

    # Convert image URLs to base64 for display
    for video_gen in video_generations:
        if video_gen.image_urls:
            base64_urls = []
            for url in video_gen.image_urls:
                # Extract filename from URL
                if '/' in url:
                    filename = url.split('/')[-1]
                    file_path = UPLOAD_DIR / filename

                    # Check if file exists locally
                    if file_path.exists():
                        try:
                            with open(file_path, 'rb') as f:
                                image_data = f.read()
                                image_base64 = base64.b64encode(image_data).decode('utf-8')
                                # Determine file type from extension
                                ext = filename.split('.')[-1].lower()
                                mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                                base64_urls.append(f"data:{mime_type};base64,{image_base64}")
                        except Exception as e:
                            logger.warning(f"Could not read image file {file_path}: {e}")
                            base64_urls.append(url)  # Keep original URL as fallback
                    else:
                        base64_urls.append(url)  # Keep original URL if file not found
                else:
                    base64_urls.append(url)  # Keep original URL if no path

            # Replace URLs with base64 data for frontend display
            video_gen.image_urls = base64_urls

    return video_generations

@router.get("/{id}", response_model=VideoGenerationSchema)
async def read_video_generation(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get video generation by ID
    """
    # Check module access
    if not current_user.has_module_access("video_generation"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")
    query = select(VideoGeneration).where(VideoGeneration.id == id)
    result = await db.execute(query)
    video_generation = result.scalar_one_or_none()

    if not video_generation:
        raise HTTPException(status_code=404, detail="Video generation not found")

    # Check ownership
    if video_generation.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Convert image URLs to base64 for display
    if video_generation.image_urls:
        base64_urls = []
        for url in video_generation.image_urls:
            # Extract filename from URL
            if '/' in url:
                filename = url.split('/')[-1]
                file_path = UPLOAD_DIR / filename

                # Check if file exists locally
                if file_path.exists():
                    try:
                        with open(file_path, 'rb') as f:
                            image_data = f.read()
                            image_base64 = base64.b64encode(image_data).decode('utf-8')
                            # Determine file type from extension
                            ext = filename.split('.')[-1].lower()
                            mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
                            base64_urls.append(f"data:{mime_type};base64,{image_base64}")
                    except Exception as e:
                        logger.warning(f"Could not read image file {file_path}: {e}")
                        base64_urls.append(url)  # Keep original URL as fallback
                else:
                    base64_urls.append(url)  # Keep original URL if file not found
            else:
                base64_urls.append(url)  # Keep original URL if no path

        # Replace URLs with base64 data for frontend display
        video_generation.image_urls = base64_urls

    return video_generation

@router.post("/webhook-callback/{id}")
async def video_generation_webhook_callback(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    video_url: str = None,
    status: str = None,
    error_message: str = None,
    external_job_id: str = None
) -> Any:
    """
    Webhook callback to update video generation status
    """
    query = select(VideoGeneration).where(VideoGeneration.id == id)
    result = await db.execute(query)
    video_generation = result.scalar_one_or_none()

    if not video_generation:
        raise HTTPException(status_code=404, detail="Video generation not found")

    # Update status
    if status:
        video_generation.status = status
    if video_url:
        video_generation.video_url = video_url
    if error_message:
        video_generation.error_message = error_message
    if external_job_id:
        video_generation.external_job_id = external_job_id

    if status == "processing":
        from datetime import datetime
        video_generation.processing_started_at = datetime.utcnow()
    elif status in ["completed", "failed"]:
        from datetime import datetime
        video_generation.processing_completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(video_generation)

    logger.info(f"Video generation {id} updated via webhook: status={status}")

    return {"msg": "Video generation updated successfully"}

@router.post("/generate-script", response_model=VideoScriptGenerateResponse)
async def generate_video_script(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request: VideoScriptGenerateRequest,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Generate educational video script using AI
    """
    # Check module access
    if not current_user.has_module_access("video_generation"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")

    try:
        # Kazanımları getir - both for AI generation and for storing full details
        kazanimlar = []  # For AI generation (simplified)
        kazanim_details = []  # Full details for storage

        if request.kazanim_ids:
            # Get kazanims from kazanimlar table
            for kazanim_id in request.kazanim_ids:
                query = select(Kazanim).where(Kazanim.id == kazanim_id)
                result = await db.execute(query)
                kazanim = result.scalar_one_or_none()
                if kazanim:
                    # Simplified for AI
                    kazanimlar.append({
                        'alan_becerileri': kazanim.alan_becerileri,
                        'ogrenme_ciktilari': kazanim.ogrenme_ciktilari,
                        'alt_ogrenme_ciktilari': kazanim.alt_ogrenme_ciktilari
                    })
                    # Full details for storage
                    kazanim_details.append({
                        'id': kazanim.id,
                        'yas_grubu': kazanim.yas_grubu,
                        'ders': kazanim.ders,
                        'alan_becerileri': kazanim.alan_becerileri,
                        'butunlesik_beceriler': kazanim.butunlesik_beceriler,
                        'surec_bilesenleri': kazanim.surec_bilesenleri,
                        'ogrenme_ciktilari': kazanim.ogrenme_ciktilari,
                        'alt_ogrenme_ciktilari': kazanim.alt_ogrenme_ciktilari
                    })

        elif request.curriculum_ids:
            # Legacy support for curriculum_ids
            for curriculum_id in request.curriculum_ids:
                query = select(Kazanim).where(Kazanim.id == curriculum_id)
                result = await db.execute(query)
                kazanim = result.scalar_one_or_none()
                if kazanim:
                    kazanimlar.append({
                        'alan_becerileri': kazanim.alan_becerileri,
                        'ogrenme_ciktilari': kazanim.ogrenme_ciktilari,
                        'alt_ogrenme_ciktilari': kazanim.alt_ogrenme_ciktilari
                    })

        # Fetch curriculum details
        curriculum_details = {
            'butunlesik_bilesenler': [],
            'degerler': [],
            'egilimler': [],
            'kavramsal_beceriler': [],
            'surec_bilesenleri': []
        }

        if request.curriculum_ids:
            for curr_id in request.curriculum_ids:
                # Try each curriculum table
                # Check Butunlesik Bilesenler
                query = select(ButunlesikBilesenler).where(ButunlesikBilesenler.id == curr_id)
                result = await db.execute(query)
                item = result.scalar_one_or_none()
                if item:
                    curriculum_details['butunlesik_bilesenler'].append({
                        'id': item.id,
                        'butunlesik_bilesenler': item.butunlesik_bilesenler,
                        'alt_butunlesik_bilesenler': item.alt_butunlesik_bilesenler,
                        'surec_bilesenleri': item.surec_bilesenleri
                    })
                    continue

                # Check Degerler
                query = select(Degerler).where(Degerler.id == curr_id)
                result = await db.execute(query)
                item = result.scalar_one_or_none()
                if item:
                    curriculum_details['degerler'].append({
                        'id': item.id,
                        'ana_deger_kodu': item.ana_deger_kodu,
                        'ana_deger_adi': item.ana_deger_adi,
                        'alt_deger_kodu': item.alt_deger_kodu,
                        'alt_deger_adi': item.alt_deger_adi,
                        'davranis_gostergesi_kodu': item.davranis_gostergesi_kodu,
                        'davranis_gostergesi_aciklamasi': item.davranis_gostergesi_aciklamasi
                    })
                    continue

                # Check Egilimler
                query = select(Egilimler).where(Egilimler.id == curr_id)
                result = await db.execute(query)
                item = result.scalar_one_or_none()
                if item:
                    curriculum_details['egilimler'].append({
                        'id': item.id,
                        'ana_egilim': item.ana_egilim,
                        'alt_egilim': item.alt_egilim
                    })
                    continue

                # Check Kavramsal Beceriler
                query = select(KavramsalBeceriler).where(KavramsalBeceriler.id == curr_id)
                result = await db.execute(query)
                item = result.scalar_one_or_none()
                if item:
                    curriculum_details['kavramsal_beceriler'].append({
                        'id': item.id,
                        'ana_beceri_kodu': item.ana_beceri_kodu,
                        'ana_beceri_adi': item.ana_beceri_adi,
                        'alt_beceri_kodu': item.alt_beceri_kodu,
                        'alt_beceri_adi': item.alt_beceri_adi
                    })
                    continue

                # Check Surec Bilesenleri
                query = select(SurecBilesenleri).where(SurecBilesenleri.id == curr_id)
                result = await db.execute(query)
                item = result.scalar_one_or_none()
                if item:
                    curriculum_details['surec_bilesenleri'].append({
                        'id': item.id,
                        'surec_bileseni_kodu': item.surec_bileseni_kodu,
                        'surec_bileseni_adi': item.surec_bileseni_adi,
                        'gosterge_kodu': item.gosterge_kodu,
                        'gosterge_aciklamasi': item.gosterge_aciklamasi
                    })

        # Auto-generate ders and konu from selected kazanims if not provided
        ders = request.ders
        konu = request.konu

        if not ders:
            # Try to get ders from the actual kazanim objects
            if request.kazanim_ids:
                first_kazanim_id = request.kazanim_ids[0]
                query = select(Kazanim).where(Kazanim.id == first_kazanim_id)
                result = await db.execute(query)
                first_kazanim_obj = result.scalar_one_or_none()
                if first_kazanim_obj:
                    ders = first_kazanim_obj.ders

            if not ders:
                ders = 'Genel'

        if not konu and kazanimlar:
            # Generate topic from learning outcomes
            konu_parts = []
            for k in kazanimlar[:3]:  # Use first 3 kazanims for topic
                if isinstance(k, dict) and k.get('ogrenme_ciktilari'):
                    konu_parts.append(k['ogrenme_ciktilari'])
            konu = ', '.join(konu_parts)[:200] if konu_parts else 'Genel Konu'

        # Generate script using AI
        script = await video_generation_service.generate_video_script(
            ders=ders or 'Genel',
            konu=konu or 'Genel Konu',
            yas_grubu=request.yas_grubu,
            kazanimlar=kazanimlar,
            video_yapisi=request.video_yapisi or "2 bölüm",
            bolum_sonu_etkinligi=request.bolum_sonu_etkinligi or "",
            vurgu_noktalari=request.vurgu_noktalari or "",
            kacinilacaklar=request.kacinilacaklar or "",
            custom_prompt=request.custom_instructions
        )

        # Parse the generated script to extract structured data
        parsed_script = VideoScriptParser.parse_script(script)

        # Save to database with both raw text and parsed JSON
        video_script_data = {
            "title": parsed_script.get("title") or f"{ders} - {konu[:50]}..." if len(konu) > 50 else f"{ders} - {konu}",
            "prompt": script,
            "parsed_content": parsed_script,  # Store parsed JSON structure
            "ders": ders,
            "konu": konu,
            "yas_grubu": request.yas_grubu,
            "kazanim_ids": request.kazanim_ids,
            "kazanim_details": kazanim_details,  # Store full kazanim details
            "curriculum_ids": request.curriculum_ids,
            "curriculum_details": curriculum_details,  # Store full curriculum details
            "video_yapisi": request.video_yapisi,
            "bolum_sonu_etkinligi": request.bolum_sonu_etkinligi,
            "vurgu_noktalari": request.vurgu_noktalari,
            "kacinilacaklar": request.kacinilacaklar,
            "created_by": current_user.id,
            "status": "generated"
        }

        video_generation = VideoGeneration(**video_script_data)
        db.add(video_generation)
        await db.commit()
        await db.refresh(video_generation)

        return VideoScriptGenerateResponse(
            id=video_generation.id,
            script=script,
            title=video_generation.title,
            ders=ders,
            konu=konu,
            yas_grubu=request.yas_grubu
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating video script: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
async def delete_video_generation(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete video generation
    """
    # Check module access
    if not current_user.has_module_access("video_generation"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")
    query = select(VideoGeneration).where(VideoGeneration.id == id)
    result = await db.execute(query)
    video_generation = result.scalar_one_or_none()

    if not video_generation:
        raise HTTPException(status_code=404, detail="Video generation not found")

    # Check ownership
    if video_generation.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    await db.delete(video_generation)
    await db.commit()

    return {"msg": "Video generation deleted successfully"}