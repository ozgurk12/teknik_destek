from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
import logging
import json

from app.db.session import get_db
from app.api.deps import get_current_active_user, require_module_access
from app.models.user import User
from app.models.etkinlik import Etkinlik
from app.models.kazanim import Kazanim
from app.models.aylik_plan import AylikPlan
from app.schemas.etkinlik import (
    EtkinlikCreate,
    EtkinlikUpdate,
    EtkinlikResponse,
    EtkinlikGenerateRequest,
    EtkinlikGenerateResponse,
    PaginatedEtkinlikResponse
)
from app.services.vertex_ai_service import vertex_ai_service
from app.services.etkinlik_service import etkinlik_service
from app.services.docx_export import docx_export_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=EtkinlikGenerateResponse)
async def generate_activity(
    request: EtkinlikGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_module_access("etkinlik_olusturma"))
):
    """
    Generate a new activity using Vertex AI based on selected learning outcomes
    """
    try:
        # If aylik_plan_id is provided, fetch kazanim_ids and curriculum_ids from the plan
        if request.aylik_plan_id:
            plan_query = select(AylikPlan).where(AylikPlan.id == request.aylik_plan_id)
            plan_result = await db.execute(plan_query)
            aylik_plan = plan_result.scalar_one_or_none()

            if not aylik_plan:
                raise HTTPException(status_code=404, detail="Aylık plan bulunamadı")

            # Use kazanim_ids from the monthly plan if not provided
            if aylik_plan.kazanim_ids:
                request.kazanim_ids = aylik_plan.kazanim_ids
                logger.info(f"Using kazanim_ids from monthly plan: {request.kazanim_ids}")

            # TODO: Use curriculum_ids from monthly plan if needed
            # if aylik_plan.curriculum_ids:
            #     request.curriculum_ids = aylik_plan.curriculum_ids

        # Fetch selected kazanimlar
        query = select(Kazanim).where(Kazanim.id.in_(request.kazanim_ids))
        result = await db.execute(query)
        kazanimlar = result.scalars().all()

        if not kazanimlar:
            raise HTTPException(status_code=404, detail="Seçilen kazanımlar bulunamadı")
        
        # Convert to dict format for the service - include all fields
        kazanim_dicts = [
            {
                "id": k.id,
                "yas_grubu": k.yas_grubu,
                "ders": k.ders,
                "alan_becerileri": k.alan_becerileri,
                "butunlesik_beceriler": k.butunlesik_beceriler,
                "surec_bilesenleri": k.surec_bilesenleri,
                "ogrenme_ciktilari": k.ogrenme_ciktilari,
                "alt_ogrenme_ciktilari": k.alt_ogrenme_ciktilari
            }
            for k in kazanimlar
        ]
        
        # Generate activity using Vertex AI with optional custom prompt
        activity_data = await vertex_ai_service.generate_activity(
            kazanim_dicts, 
            custom_prompt=request.custom_prompt
        )
        
        if not activity_data:
            return EtkinlikGenerateResponse(
                success=False,
                message="Etkinlik oluşturulamadı",
                error="Vertex AI'dan yanıt alınamadı"
            )
        
        # Extract curriculum components from kazanims
        curriculum_data = await etkinlik_service.extract_curriculum_from_kazanims(db, request.kazanim_ids)

        # Create new activity record with kazanim info and curriculum
        new_activity = Etkinlik(**activity_data)

        # Determine activity area based on selected kazanims
        # If multiple areas, combine them
        selected_areas = list(set(k.ders for k in kazanimlar if k.ders))
        if len(selected_areas) == 1:
            # Single area
            area_mapping = {
                'MATEMATİK': 'Matematik',
                'TÜRKÇE': 'Türkçe',
                'FEN': 'Fen ve Ekoloji',
                'FEN VE EKOLOJİ': 'Fen ve Ekoloji',
                'SANAT': 'Sanat',
                'MÜZİK': 'Müzik',
                'HAREKET VE SAĞLIK': 'Hareket ve Sağlık',
                'SOSYAL': 'Sosyal'
            }
            new_activity.alan_adi = area_mapping.get(selected_areas[0], selected_areas[0])
        elif len(selected_areas) > 1:
            # Multiple areas - create combined name
            area_names = []
            for area in selected_areas:
                if area == 'MATEMATİK':
                    area_names.append('Matematik')
                elif area == 'TÜRKÇE':
                    area_names.append('Türkçe')
                elif area in ['FEN', 'FEN VE EKOLOJİ']:
                    area_names.append('Fen')
                elif area == 'HAREKET VE SAĞLIK':
                    area_names.append('Hareket')
                elif area == 'MÜZİK':
                    area_names.append('Müzik')
                elif area == 'SANAT':
                    area_names.append('Sanat')
                elif area == 'SOSYAL':
                    area_names.append('Sosyal')
            new_activity.alan_adi = ' + '.join(area_names[:3])  # Max 3 areas in name

        # Add kazanim information and custom prompt
        new_activity.kazanim_idleri = request.kazanim_ids
        new_activity.kazanim_metinleri = [
            f"{k.ogrenme_ciktilari} - {k.alt_ogrenme_ciktilari}" if k.alt_ogrenme_ciktilari
            else k.ogrenme_ciktilari
            for k in kazanimlar
        ]
        new_activity.prompt_used = request.custom_prompt
        new_activity.custom_instructions = request.custom_prompt  # Save custom instructions

        # Add user information
        new_activity.created_by_id = current_user.id
        new_activity.created_by_username = current_user.username
        new_activity.created_by_fullname = current_user.full_name

        # Log received curriculum data
        logger.info(f"Received curriculum data from frontend:")
        logger.info(f"  kavramsal_beceriler: {request.kavramsal_beceriler}")
        logger.info(f"  egilimler: {request.egilimler}")
        logger.info(f"  sosyal_duygusal: {request.sosyal_duygusal}")
        logger.info(f"  degerler: {request.degerler}")
        logger.info(f"  okuryazarlik: {request.okuryazarlik}")

        # Use curriculum from frontend if provided, otherwise use extracted
        if request.kavramsal_beceriler:
            curriculum_data['kavramsal_beceriler'] = request.kavramsal_beceriler
        if request.egilimler:
            curriculum_data['egilimler'] = request.egilimler
        if request.sosyal_duygusal:
            curriculum_data['sosyal_duygusal'] = request.sosyal_duygusal
        if request.degerler:
            curriculum_data['degerler'] = request.degerler
        if request.okuryazarlik:
            curriculum_data['okuryazarlik'] = request.okuryazarlik

        logger.info(f"Final curriculum_data: {curriculum_data}")

        # Add extracted curriculum components
        new_activity.curriculum_data = curriculum_data
        new_activity.alan_becerileri = curriculum_data.get('alan_becerileri')
        new_activity.ogrenme_ciktilari = curriculum_data.get('ogrenme_ciktilari')
        new_activity.kavramsal_beceriler = curriculum_data.get('kavramsal_beceriler')
        new_activity.egilimler = curriculum_data.get('egilimler')
        new_activity.sosyal_duygusal = curriculum_data.get('sosyal_duygusal')
        new_activity.degerler = curriculum_data.get('degerler')
        new_activity.okuryazarlik = curriculum_data.get('okuryazarlik')

        db.add(new_activity)
        await db.commit()
        await db.refresh(new_activity)
        
        return EtkinlikGenerateResponse(
            success=True,
            message="Etkinlik başarıyla oluşturuldu",
            etkinlik=new_activity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating activity: {str(e)}")
        return EtkinlikGenerateResponse(
            success=False,
            message="Etkinlik oluşturulurken hata oluştu",
            error=str(e)
        )

@router.get("/", response_model=PaginatedEtkinlikResponse)
async def list_activities(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    alan_adi: Optional[str] = Query(None),
    yas_grubu: Optional[str] = Query(None),
    ai_generated: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List all activities with pagination and filtering
    """
    # Build base query
    query = select(Etkinlik)
    count_query = select(func.count()).select_from(Etkinlik)

    # Apply filters
    if alan_adi:
        query = query.where(Etkinlik.alan_adi == alan_adi)
        count_query = count_query.where(Etkinlik.alan_adi == alan_adi)

    if yas_grubu:
        query = query.where(Etkinlik.yas_grubu == yas_grubu)
        count_query = count_query.where(Etkinlik.yas_grubu == yas_grubu)

    if ai_generated is not None:
        query = query.where(Etkinlik.ai_generated == ai_generated)
        count_query = count_query.where(Etkinlik.ai_generated == ai_generated)

    if search:
        search_filter = Etkinlik.etkinlik_adi.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Order by creation date (newest first)
    query = query.order_by(Etkinlik.created_at.desc())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    activities = result.scalars().all()

    # Calculate total pages
    import math
    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedEtkinlikResponse(
        items=activities,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{activity_id}", response_model=EtkinlikResponse)
async def get_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific activity by ID
    """
    query = select(Etkinlik).where(Etkinlik.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    
    return activity

@router.post("/", response_model=EtkinlikResponse)
async def create_activity(
    activity: EtkinlikCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new activity manually
    """
    new_activity = Etkinlik(**activity.model_dump())
    new_activity.ai_generated = False  # Manual creation
    
    db.add(new_activity)
    await db.commit()
    await db.refresh(new_activity)
    
    return new_activity

@router.put("/{activity_id}", response_model=EtkinlikResponse)
async def update_activity(
    activity_id: int,
    activity_update: EtkinlikUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing activity
    """
    query = select(Etkinlik).where(Etkinlik.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    
    # Update fields
    update_data = activity_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    await db.commit()
    await db.refresh(activity)
    
    return activity

@router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an activity
    """
    query = select(Etkinlik).where(Etkinlik.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    
    await db.delete(activity)
    await db.commit()
    
    return {"message": "Etkinlik başarıyla silindi"}

@router.get("/{activity_id}/export/docx")
async def export_activity_to_docx(
    activity_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Export a specific activity to DOCX format
    """
    query = select(Etkinlik).where(Etkinlik.id == activity_id)
    result = await db.execute(query)
    activity = result.scalar_one_or_none()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Etkinlik bulunamadı")
    
    # Prepare activity data for export - include ALL fields
    activity_data = {
        'etkinlik_adi': activity.etkinlik_adi,
        'alan_adi': activity.alan_adi,
        'yas_grubu': activity.yas_grubu,
        'sure': activity.sure,
        'uygulama_yeri': activity.uygulama_yeri,
        'etkinlik_amaci': activity.etkinlik_amaci,
        'materyaller': activity.materyaller,
        'uygulama_sureci': activity.uygulama_sureci,
        'giris_bolumu': activity.giris_bolumu,
        'gelisme_bolumu': activity.gelisme_bolumu,
        'yansima_cemberi': activity.yansima_cemberi,
        'sonuc_bolumu': activity.sonuc_bolumu,
        'uyarlama': activity.uyarlama,
        'farklilastirma_kapsayicilik': activity.farklilastirma_kapsayicilik,
        'degerlendirme_program': activity.degerlendirme_program,
        'degerlendirme_beceriler': activity.degerlendirme_beceriler,
        'degerlendirme_ogrenciler': activity.degerlendirme_ogrenciler,
        'json_data': activity.json_data if hasattr(activity, 'json_data') else None,
        'kazanim_metinleri': activity.kazanim_metinleri
    }
    
    # If no JSON data, create from existing fields
    if not activity_data['json_data']:
        json_structure = {
            'etkinlik_adi': activity.etkinlik_adi,
            'alan_adi': activity.alan_adi,
            'yas_grubu': activity.yas_grubu,
            'sure': str(activity.sure),
            'uygulama_yeri': activity.uygulama_yeri,
            'amaclar': activity.etkinlik_amaci.split('\n') if activity.etkinlik_amaci else [],
            'materyaller': {
                'temel_malzemeler': activity.materyaller if activity.materyaller else ''
            },
            'uygulama_sureci': {
                'giris': {'sure': '5-7 dakika', 'adimlar': []},
                'gelisme': {'sure': '20 dakika', 'aktiviteler': {}},
                'yansima_cemberi': {'sure': '5-7 dakika', 'sorular': []},
                'sonuc': {'sure': '3 dakika', 'aktiviteler': []}
            },
            'uyarlama': {},
            'farklilastirma_ve_kapsayicilik': {},
            'degerlendirme': {}
        }
        
        # Parse uygulama_sureci if exists
        if activity.uygulama_sureci:
            # Simple parsing - can be improved
            json_structure['uygulama_sureci'] = {
                'giris': {'sure': '5-7 dakika', 'adimlar': [activity.uygulama_sureci[:100]]},
                'gelisme': {'sure': '20 dakika', 'aktiviteler': {'aktivite_1': activity.uygulama_sureci[100:500]}},
                'yansima_cemberi': {'sure': '5-7 dakika', 'sorular': []},
                'sonuc': {'sure': '3 dakika', 'aktiviteler': []}
            }
        
        activity_data['json_data'] = json.dumps(json_structure, ensure_ascii=False)
    
    # Generate DOCX
    docx_file = docx_export_service.export_activity_to_docx(activity_data)
    
    # Return as downloadable file
    import urllib.parse
    safe_filename = urllib.parse.quote(activity.etkinlik_adi.replace(' ', '_')) + '.docx'
    
    return StreamingResponse(
        docx_file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}",
            "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document; charset=utf-8"
        }
    )

@router.get("/stats/overview")
async def get_activity_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about activities
    """
    # Total count
    total_query = select(func.count(Etkinlik.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # AI generated vs manual
    ai_query = select(
        Etkinlik.ai_generated,
        func.count(Etkinlik.id).label('count')
    ).group_by(Etkinlik.ai_generated)
    
    ai_result = await db.execute(ai_query)
    ai_stats = {
        "ai_generated": 0,
        "manual": 0
    }
    for row in ai_result:
        if row[0]:
            ai_stats["ai_generated"] = row[1]
        else:
            ai_stats["manual"] = row[1]
    
    # By field
    field_query = select(
        Etkinlik.alan_adi,
        func.count(Etkinlik.id).label('count')
    ).group_by(Etkinlik.alan_adi).order_by(func.count(Etkinlik.id).desc())
    
    field_result = await db.execute(field_query)
    fields = [
        {"alan_adi": row[0], "count": row[1]}
        for row in field_result if row[0]
    ]
    
    # By age group
    age_query = select(
        Etkinlik.yas_grubu,
        func.count(Etkinlik.id).label('count')
    ).group_by(Etkinlik.yas_grubu).order_by(Etkinlik.yas_grubu)
    
    age_result = await db.execute(age_query)
    age_groups = [
        {"yas_grubu": row[0], "count": row[1]}
        for row in age_result if row[0]
    ]
    
    return {
        "total": total,
        "generation_type": ai_stats,
        "by_field": fields,
        "by_age_group": age_groups
    }