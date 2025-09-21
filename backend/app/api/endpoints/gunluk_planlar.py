# -*- coding: utf-8 -*-
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import date
import logging

from app.api.deps import get_db, get_current_active_user, require_module_access
from app.models.user import User
from app.models.gunluk_plan import GunlukPlan
from app.models.etkinlik import Etkinlik
from app.schemas.gunluk_plan import (
    GunlukPlanCreate,
    GunlukPlanUpdate,
    GunlukPlanResponse,
    GunlukPlanGenerateRequest,
    GunlukPlanGenerateResponse
)
from app.services.gunluk_plan_service import gunluk_plan_service
from app.services.docx_export_gunluk import docx_gunluk_export_service
from app.services.gunluk_plan_ai_service import gunluk_plan_ai_service
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gunluk-planlar", tags=["Günlük Planlar"])

@router.get("/", response_model=List[GunlukPlanResponse])
async def list_gunluk_planlar(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    yas_grubu: Optional[str] = Query(None, description="Filter by age group"),
    tarih_from: Optional[date] = Query(None, description="Filter by date from"),
    tarih_to: Optional[date] = Query(None, description="Filter by date to"),
    search: Optional[str] = Query(None, description="Search in plan name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all daily plans with pagination and filtering
    """
    query = select(GunlukPlan)

    # Apply filters
    filters = []
    if yas_grubu:
        filters.append(GunlukPlan.yas_grubu == yas_grubu)
    if tarih_from:
        filters.append(GunlukPlan.tarih >= tarih_from)
    if tarih_to:
        filters.append(GunlukPlan.tarih <= tarih_to)
    if search:
        filters.append(
            or_(
                GunlukPlan.plan_adi.ilike(f"%{search}%"),
                GunlukPlan.ogretmen.ilike(f"%{search}%")
            )
        )

    if filters:
        query = query.where(and_(*filters))

    # Apply pagination
    query = query.order_by(GunlukPlan.tarih.desc(), GunlukPlan.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    plans = result.scalars().all()

    # Enrich with activity details
    enriched_plans = []
    for plan in plans:
        plan_dict = plan.__dict__.copy()

        # Get activity details if IDs exist
        if plan.etkinlik_idleri:
            activity_query = select(Etkinlik).where(Etkinlik.id.in_(plan.etkinlik_idleri))
            activity_result = await db.execute(activity_query)
            activities = activity_result.scalars().all()

            plan_dict['etkinlik_detaylari'] = [
                {
                    'id': act.id,
                    'etkinlik_adi': act.etkinlik_adi,
                    'alan_adi': act.alan_adi,
                    'sure': act.sure,
                    'yas_grubu': act.yas_grubu
                }
                for act in activities
            ]
        else:
            plan_dict['etkinlik_detaylari'] = []

        enriched_plans.append(GunlukPlanResponse(**plan_dict))

    return enriched_plans

@router.get("/{plan_id}", response_model=GunlukPlanResponse)
async def get_gunluk_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific daily plan by ID
    """
    query = select(GunlukPlan).where(GunlukPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Günlük plan bulunamadı")

    plan_dict = plan.__dict__.copy()

    # Get activity details
    if plan.etkinlik_idleri:
        activity_query = select(Etkinlik).where(Etkinlik.id.in_(plan.etkinlik_idleri))
        activity_result = await db.execute(activity_query)
        activities = activity_result.scalars().all()

        plan_dict['etkinlik_detaylari'] = [
            {
                'id': act.id,
                'etkinlik_adi': act.etkinlik_adi,
                'alan_adi': act.alan_adi,
                'sure': act.sure,
                'yas_grubu': act.yas_grubu,
                'etkinlik_amaci': act.etkinlik_amaci,
                'materyaller': act.materyaller,
                'uygulama_sureci': act.uygulama_sureci
            }
            for act in activities
        ]
    else:
        plan_dict['etkinlik_detaylari'] = []

    return GunlukPlanResponse(**plan_dict)

@router.post("/generate-with-ai", response_model=GunlukPlanResponse)
async def generate_gunluk_plan_with_ai(
    plan: GunlukPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a daily plan using AI based on selected activities
    """
    print(f"=== GENERATE-WITH-AI ENDPOINT CALLED ===")
    print(f"Plan data received: {plan.dict()}")
    logger.info(f"=== GENERATE-WITH-AI ENDPOINT CALLED ===")
    logger.info(f"Plan data received: {plan.dict()}")

    if not plan.etkinlik_idleri:
        raise HTTPException(status_code=400, detail="En az bir etkinlik seçmelisiniz")

    logger.info(f"Calling AI service with {len(plan.etkinlik_idleri)} activities...")
    print(f"About to call AI service with activities: {plan.etkinlik_idleri}")

    # Generate AI content
    try:
        ai_content = await gunluk_plan_ai_service.generate_plan_content(
            db=db,
            activity_ids=plan.etkinlik_idleri,
            plan_adi=plan.plan_adi,
            yas_grubu=plan.yas_grubu
        )
        print(f"AI service returned content with keys: {list(ai_content.keys()) if ai_content else 'None'}")
    except Exception as e:
        print(f"ERROR calling AI service: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

    logger.info(f"AI content generated: {bool(ai_content)}")

    # Process activities to extract curriculum data
    plan_data = await gunluk_plan_service.process_activities_for_plan(
        db,
        plan.etkinlik_idleri
    )

    # Extract nested fields from AI response
    programlar_arasi = ai_content.get('programlar_arasi_bilesenler', {})
    icerik_cercevesi = ai_content.get('icerik_cercevesi', {})
    ogrenme_ogretme = ai_content.get('ogrenme_ogretme_yasantilari', {})
    farklilastirma = ai_content.get('farklilastirma', {})
    aile_toplum = ai_content.get('aile_toplum_katilimi', {})

    # Handle both direct and nested fields
    kavramsal_beceriler = ai_content.get('kavramsal_beceriler', [])
    egilimler = ai_content.get('egilimler', [])

    # Check if programlar_arasi has the fields, otherwise check root level
    sosyal_duygusal = programlar_arasi.get('sosyal_duygusal_ogrenme_becerileri',
                      ai_content.get('sosyal_duygusal_beceriler', []))
    degerler = programlar_arasi.get('degerler',
               ai_content.get('degerler', []))
    okuryazarlik = programlar_arasi.get('okuryazarlik_becerileri',
                   ai_content.get('okuryazarlik_becerileri', []))

    # Create plan instance with AI generated content
    db_plan = GunlukPlan(
        plan_adi=plan.plan_adi,
        tarih=plan.tarih,
        yas_grubu=plan.yas_grubu,
        sinif=plan.sinif,
        ogretmen=plan.ogretmen,
        etkinlik_idleri=plan.etkinlik_idleri,
        # Use AI generated curriculum components if available
        alan_becerileri=ai_content.get('alan_becerileri', plan_data.get('alan_becerileri', {})),
        kavramsal_beceriler=kavramsal_beceriler if kavramsal_beceriler else plan_data.get('kavramsal_beceriler', []),
        egilimler=egilimler if egilimler else plan_data.get('egilimler', []),
        programlar_arasi_bilesenler=programlar_arasi if programlar_arasi else {},  # Combined field for frontend
        sosyal_duygusal_beceriler=sosyal_duygusal if sosyal_duygusal else plan_data.get('sosyal_duygusal_beceriler', []),
        degerler=degerler if degerler else plan_data.get('degerler', []),
        okuryazarlik_becerileri=okuryazarlik if okuryazarlik else plan_data.get('okuryazarlik_becerileri', []),
        farklilastirma=farklilastirma if farklilastirma else {},  # Combined field for frontend
        aile_toplum_katilimi=aile_toplum if aile_toplum else {},  # Combined field for frontend
        ogrenme_ciktilari=ai_content.get('ogrenme_ciktilari_ve_surec_bilesenleri', ai_content.get('ogrenme_ciktilari', plan_data.get('ogrenme_ciktilari', {}))),
        # Content framework fields
        kavramlar=icerik_cercevesi.get('kavramlar', plan.kavramlar or ''),
        sozcukler=icerik_cercevesi.get('sozcukler', plan.sozcukler or ''),
        materyaller=icerik_cercevesi.get('materyaller', plan_data.get('materyaller', '')),
        egitim_ortamlari=icerik_cercevesi.get('egitim_ogrenme_ortamlari', plan.egitim_ortamlari or ''),
        # Learning-teaching experiences
        gune_baslama=ogrenme_ogretme.get('gune_baslama_zamani', plan.gune_baslama or ''),
        ogrenme_merkezleri=ogrenme_ogretme.get('ogrenme_merkezlerinde_oyun', plan.ogrenme_merkezleri or ''),
        beslenme_toplanma=ogrenme_ogretme.get('beslenme_toplanma_temizlik', plan.beslenme_toplanma or ''),
        etkinlikler=json.dumps(ogrenme_ogretme.get('etkinlikler', ''), ensure_ascii=False) if isinstance(ogrenme_ogretme.get('etkinlikler'), dict) else ogrenme_ogretme.get('etkinlikler', plan_data.get('etkinlikler', '')),
        # Evaluation and differentiation
        degerlendirme='\n'.join(ai_content.get('degerlendirme', [])) if isinstance(ai_content.get('degerlendirme'), list) else ai_content.get('degerlendirme', plan.degerlendirme or ''),
        zenginlestirme=farklilastirma.get('zenginlestirme', plan.zenginlestirme or ''),
        destekleme=farklilastirma.get('destekleme', plan.destekleme or ''),
        # Family and community participation
        aile_katilimi=aile_toplum.get('aile_katilimi', plan.aile_katilimi or ''),
        toplum_katilimi=aile_toplum.get('toplum_katilimi', plan.toplum_katilimi or ''),
        notlar=ai_content.get('notlar', plan.notlar or ''),
        # User information
        created_by_id=current_user.id,
        created_by_username=current_user.username,
        created_by_fullname=current_user.full_name,
        ai_generated=True,
        ai_prompt=f"Generated daily plan for {plan.yas_grubu} with {len(plan.etkinlik_idleri)} activities"
    )

    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)

    # Get activity details for response
    plan_dict = db_plan.__dict__.copy()
    if db_plan.etkinlik_idleri:
        activity_query = select(Etkinlik).where(Etkinlik.id.in_(db_plan.etkinlik_idleri))
        activity_result = await db.execute(activity_query)
        activities = activity_result.scalars().all()

        plan_dict['etkinlik_detaylari'] = [
            {
                'id': act.id,
                'etkinlik_adi': act.etkinlik_adi,
                'alan_adi': act.alan_adi,
                'sure': act.sure,
                'yas_grubu': act.yas_grubu
            }
            for act in activities
        ]
    else:
        plan_dict['etkinlik_detaylari'] = []

    return GunlukPlanResponse(**plan_dict)

@router.post("/", response_model=GunlukPlanResponse)
async def create_gunluk_plan(
    plan: GunlukPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new daily plan
    """
    # Process activities to extract curriculum data
    if plan.etkinlik_idleri:
        plan_data = await gunluk_plan_service.process_activities_for_plan(
            db,
            plan.etkinlik_idleri
        )
    else:
        plan_data = {}

    # Create plan instance
    db_plan = GunlukPlan(
        **plan.model_dump(),
        alan_becerileri=plan_data.get('alan_becerileri', {}),
        kavramsal_beceriler=plan_data.get('kavramsal_beceriler', {}),
        egilimler=plan_data.get('egilimler', {}),
        sosyal_duygusal_beceriler=plan_data.get('sosyal_duygusal_beceriler', {}),
        degerler=plan_data.get('degerler', {}),
        okuryazarlik_becerileri=plan_data.get('okuryazarlik_becerileri', {}),
        ogrenme_ciktilari=plan_data.get('ogrenme_ciktilari', {}),
        etkinlikler=plan_data.get('etkinlikler', ''),
        # User information
        created_by_id=current_user.id,
        created_by_username=current_user.username,
        created_by_fullname=current_user.full_name
    )

    # If materials not provided, use from activities
    if not db_plan.materyaller and plan_data.get('materyaller'):
        db_plan.materyaller = plan_data['materyaller']

    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)

    # Get activity details for response
    plan_dict = db_plan.__dict__.copy()
    if db_plan.etkinlik_idleri:
        activity_query = select(Etkinlik).where(Etkinlik.id.in_(db_plan.etkinlik_idleri))
        activity_result = await db.execute(activity_query)
        activities = activity_result.scalars().all()

        plan_dict['etkinlik_detaylari'] = [
            {
                'id': act.id,
                'etkinlik_adi': act.etkinlik_adi,
                'alan_adi': act.alan_adi,
                'sure': act.sure,
                'yas_grubu': act.yas_grubu
            }
            for act in activities
        ]
    else:
        plan_dict['etkinlik_detaylari'] = []

    return GunlukPlanResponse(**plan_dict)

@router.put("/{plan_id}", response_model=GunlukPlanResponse)
async def update_gunluk_plan(
    plan_id: int,
    plan_update: GunlukPlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update an existing daily plan
    """
    query = select(GunlukPlan).where(GunlukPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Günlük plan bulunamadı")

    # Update fields
    update_data = plan_update.model_dump(exclude_unset=True)

    # If activities changed, reprocess curriculum data
    if 'etkinlik_idleri' in update_data and update_data['etkinlik_idleri']:
        plan_data = await gunluk_plan_service.process_activities_for_plan(
            db,
            update_data['etkinlik_idleri']
        )

        plan.alan_becerileri = plan_data.get('alan_becerileri', {})
        plan.kavramsal_beceriler = plan_data.get('kavramsal_beceriler', {})
        plan.egilimler = plan_data.get('egilimler', {})
        plan.sosyal_duygusal_beceriler = plan_data.get('sosyal_duygusal_beceriler', {})
        plan.degerler = plan_data.get('degerler', {})
        plan.okuryazarlik_becerileri = plan_data.get('okuryazarlik_becerileri', {})
        plan.ogrenme_ciktilari = plan_data.get('ogrenme_ciktilari', {})
        plan.etkinlikler = plan_data.get('etkinlikler', '')

        # Update materials if not manually set
        if not update_data.get('materyaller'):
            plan.materyaller = plan_data.get('materyaller', '')

    # Apply other updates
    for field, value in update_data.items():
        setattr(plan, field, value)

    await db.commit()
    await db.refresh(plan)

    # Get activity details for response
    plan_dict = plan.__dict__.copy()
    if plan.etkinlik_idleri:
        activity_query = select(Etkinlik).where(Etkinlik.id.in_(plan.etkinlik_idleri))
        activity_result = await db.execute(activity_query)
        activities = activity_result.scalars().all()

        plan_dict['etkinlik_detaylari'] = [
            {
                'id': act.id,
                'etkinlik_adi': act.etkinlik_adi,
                'alan_adi': act.alan_adi,
                'sure': act.sure,
                'yas_grubu': act.yas_grubu
            }
            for act in activities
        ]
    else:
        plan_dict['etkinlik_detaylari'] = []

    return GunlukPlanResponse(**plan_dict)

@router.delete("/{plan_id}")
async def delete_gunluk_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a daily plan
    """
    query = select(GunlukPlan).where(GunlukPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Günlük plan bulunamadı")

    await db.delete(plan)
    await db.commit()

    return {"message": "Günlük plan başarıyla silindi"}

@router.get("/{plan_id}/export/docx")
async def export_gunluk_plan_to_docx(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Export a daily plan to DOCX format
    """
    query = select(GunlukPlan).where(GunlukPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Günlük plan bulunamadı")

    # Get activity details
    activities = []
    if plan.etkinlik_idleri:
        activity_query = select(Etkinlik).where(Etkinlik.id.in_(plan.etkinlik_idleri))
        activity_result = await db.execute(activity_query)
        activities = activity_result.scalars().all()

    # Prepare data for DOCX export
    plan_data = {
        'plan_adi': plan.plan_adi,
        'tarih': plan.tarih,
        'yas_grubu': plan.yas_grubu,
        'sinif': plan.sinif,
        'ogretmen': plan.ogretmen,
        'alan_becerileri': plan.alan_becerileri,
        'kavramsal_beceriler': plan.kavramsal_beceriler,
        'egilimler': plan.egilimler,
        'sosyal_duygusal_beceriler': plan.sosyal_duygusal_beceriler,
        'degerler': plan.degerler,
        'okuryazarlik_becerileri': plan.okuryazarlik_becerileri,
        'ogrenme_ciktilari': plan.ogrenme_ciktilari,
        'kavramlar': plan.kavramlar,
        'sozcukler': plan.sozcukler,
        'materyaller': plan.materyaller,
        'egitim_ortamlari': plan.egitim_ortamlari,
        'gune_baslama': plan.gune_baslama,
        'ogrenme_merkezleri': plan.ogrenme_merkezleri,
        'beslenme_toplanma': plan.beslenme_toplanma,
        'etkinlikler': plan.etkinlikler,
        'degerlendirme': plan.degerlendirme,
        'zenginlestirme': plan.zenginlestirme,
        'destekleme': plan.destekleme,
        'aile_katilimi': plan.aile_katilimi,
        'toplum_katilimi': plan.toplum_katilimi,
        'activities': activities
    }

    # Generate DOCX
    docx_file = docx_gunluk_export_service.export_gunluk_plan_to_docx(plan_data)

    # Return as downloadable file
    import urllib.parse
    safe_filename = urllib.parse.quote(plan.plan_adi.replace(' ', '_')) + '_gunluk_plan.docx'

    return StreamingResponse(
        docx_file,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}",
            "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document; charset=utf-8"
        }
    )