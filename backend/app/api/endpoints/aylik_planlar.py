from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app import schemas
from app.api import deps
from app.models.user import User
from app.models.aylik_plan import AylikPlan
from app.schemas.aylik_plan import (
    AylikPlanCreate,
    AylikPlanUpdate,
    AylikPlanGenerateRequest,
    AylikPlanGenerateResponse,
    AylikPlan as AylikPlanSchema
)
from app.services.aylik_plan_ai_service import AylikPlanAIService
from app.services.docx_export_aylik import AylikPlanDocxExporter

router = APIRouter()

@router.post("/generate", response_model=AylikPlanGenerateResponse)
async def generate_aylik_plan(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request: AylikPlanGenerateRequest,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    AI kullanarak yeni aylık plan oluştur.
    """
    if not current_user.has_module_access("aylik_plan"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")

    ai_service = AylikPlanAIService()

    # Debug: Log incoming request
    print(f"Generate request - kazanim_ids: {request.kazanim_ids}")
    print(f"Generate request - curriculum_ids: {request.curriculum_ids}")

    try:
        # AI ile plan oluştur
        plan_data = await ai_service.generate_aylik_plan(
            db=db,
            yas_grubu=request.yas_grubu,
            ay=request.ay,
            kazanim_ids=request.kazanim_ids,
            curriculum_ids=request.curriculum_ids,
            custom_instructions=request.custom_instructions
        )

        # Veritabanına kaydet
        try:
            print(f"Plan data to save - keys: {plan_data.keys()}")
            print(f"Alan becerileri: {plan_data.get('alan_becerileri', 'NOT FOUND')}")
            print(f"Kavramsal beceriler: {plan_data.get('kavramsal_beceriler', 'NOT FOUND')}")

            db_plan = AylikPlan(
                **plan_data,
                created_by=current_user.id,
                kazanim_ids=request.kazanim_ids,
                curriculum_ids=request.curriculum_ids
            )
            db.add(db_plan)
            await db.commit()
            await db.refresh(db_plan)

            print(f"Saved plan ID: {db_plan.id}")
            print(f"Saved kazanim_ids: {db_plan.kazanim_ids}")
            print(f"Saved curriculum_ids: {db_plan.curriculum_ids}")
            print(f"Saved alan_becerileri: {db_plan.alan_becerileri}")
            print(f"Saved egilimler: {db_plan.egilimler}")
            print(f"Saved kavramsal_beceriler: {db_plan.kavramsal_beceriler}")

            return db_plan

        except Exception as db_error:
            await db.rollback()
            print(f"Database error while saving monthly plan: {db_error}")
            print(f"Plan data keys: {plan_data.keys()}")
            print(f"User ID type: {type(current_user.id)}, value: {current_user.id}")
            raise HTTPException(
                status_code=500,
                detail=f"Veritabanına kaydetme hatası: {str(db_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating monthly plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AylikPlanSchema])
async def read_aylik_planlar(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    yas_grubu: str = Query(None, description="Yaş grubu filtresi"),
    ay: str = Query(None, description="Ay filtresi"),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Aylık planları listele.
    """
    if not current_user.has_module_access("aylik_plan"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")

    query = select(AylikPlan)

    # Admin ve yöneticiler tüm planları görebilir
    if current_user.role not in ["admin", "yonetici"]:
        query = query.where(AylikPlan.created_by == current_user.id)

    # Filtreler
    if yas_grubu:
        query = query.where(AylikPlan.yas_grubu == yas_grubu)
    if ay:
        query = query.where(AylikPlan.ay == ay)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    plans = result.scalars().all()
    return plans

@router.get("/{id}", response_model=AylikPlanSchema)
async def read_aylik_plan(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    ID'ye göre aylık plan getir.
    """
    if not current_user.has_module_access("aylik_plan"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")

    query = select(AylikPlan).where(AylikPlan.id == id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Aylık plan bulunamadı")

    # Yetki kontrolü
    if current_user.role not in ["admin", "yonetici"] and plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Bu plana erişim yetkiniz yok")

    return plan

@router.put("/{id}", response_model=AylikPlanSchema)
async def update_aylik_plan(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    plan_in: AylikPlanUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Aylık planı güncelle.
    """
    if not current_user.has_module_access("aylik_plan"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")

    query = select(AylikPlan).where(AylikPlan.id == id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Aylık plan bulunamadı")

    # Yetki kontrolü
    if current_user.role not in ["admin", "yonetici"] and plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Bu planı güncelleme yetkiniz yok")

    # Güncelle
    for field, value in plan_in.dict(exclude_unset=True).items():
        setattr(plan, field, value)

    db.add(plan)
    await db.commit()
    await db.refresh(plan)

    return plan

@router.delete("/{id}")
async def delete_aylik_plan(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Aylık planı sil.
    """
    if not current_user.has_module_access("aylik_plan"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")

    query = select(AylikPlan).where(AylikPlan.id == id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Aylık plan bulunamadı")

    # Yetki kontrolü
    if current_user.role not in ["admin", "yonetici"] and plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Bu planı silme yetkiniz yok")

    await db.delete(plan)
    await db.commit()

    return {"msg": "Aylık plan başarıyla silindi"}

@router.get("/{id}/export-docx")
async def export_aylik_plan_docx(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Aylık planı DOCX formatında indir.
    """
    from fastapi.responses import FileResponse
    import os

    if not current_user.has_module_access("aylik_plan"):
        raise HTTPException(status_code=403, detail="Bu özelliğe erişim yetkiniz yok")

    query = select(AylikPlan).where(AylikPlan.id == id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Aylık plan bulunamadı")

    # Yetki kontrolü
    if current_user.role not in ["admin", "yonetici"] and plan.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Bu plana erişim yetkiniz yok")

    try:
        exporter = AylikPlanDocxExporter()
        file_path = exporter.export_aylik_plan(plan)

        # Türkçe karakterleri güvenli hale getir
        import unicodedata
        safe_filename = unicodedata.normalize('NFKD', plan.plan_adi)
        safe_filename = safe_filename.encode('ascii', 'ignore').decode('ascii')
        safe_filename = safe_filename.replace(' ', '_')
        if not safe_filename:
            safe_filename = f"aylik_plan_{plan.id}"

        return FileResponse(
            path=file_path,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=f"{safe_filename}.docx",
            headers={
                "Content-Disposition": f"attachment; filename={safe_filename}.docx"
            }
        )

    except Exception as e:
        import traceback
        error_detail = f"DOCX export hatası: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Backend loglarında görünsün
        raise HTTPException(status_code=500, detail=f"DOCX export hatası: {str(e)}")