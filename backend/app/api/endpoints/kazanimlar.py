from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional

from app.db.session import get_db
from app.models.kazanim import Kazanim
from app.schemas.kazanim import (
    KazanimResponse, 
    KazanimListResponse,
    KazanimFilter
)

router = APIRouter()

@router.get("/", response_model=KazanimListResponse)
async def list_kazanimlar(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    yas_grubu: Optional[str] = Query(None, description="Filter by age group"),
    ders: Optional[str] = Query(None, description="Filter by subject"),
    search: Optional[str] = Query(None, description="Search in learning outcomes"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all learning outcomes with pagination and filtering
    """
    # Build query
    query = select(Kazanim)
    count_query = select(func.count(Kazanim.id))
    
    # Apply filters
    if yas_grubu:
        query = query.where(Kazanim.yas_grubu == yas_grubu)
        count_query = count_query.where(Kazanim.yas_grubu == yas_grubu)
    
    if ders:
        query = query.where(Kazanim.ders == ders)
        count_query = count_query.where(Kazanim.ders == ders)
    
    if search:
        search_filter = or_(
            Kazanim.ogrenme_ciktilari.ilike(f"%{search}%"),
            Kazanim.alt_ogrenme_ciktilari.ilike(f"%{search}%"),
            Kazanim.alan_becerileri.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    kazanimlar = result.scalars().all()
    
    return KazanimListResponse(
        total=total,
        items=kazanimlar,
        page=page,
        page_size=page_size
    )

@router.get("/{kazanim_id}", response_model=KazanimResponse)
async def get_kazanim(
    kazanim_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific learning outcome by ID
    """
    query = select(Kazanim).where(Kazanim.id == kazanim_id)
    result = await db.execute(query)
    kazanim = result.scalar_one_or_none()
    
    if not kazanim:
        raise HTTPException(status_code=404, detail="Kazanım bulunamadı")
    
    return kazanim

@router.get("/stats/overview")
async def get_kazanim_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about learning outcomes
    """
    # Total count
    total_query = select(func.count(Kazanim.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar()
    
    # Count by age group
    age_group_query = select(
        Kazanim.yas_grubu,
        func.count(Kazanim.id).label('count')
    ).group_by(Kazanim.yas_grubu).order_by(Kazanim.yas_grubu)
    
    age_group_result = await db.execute(age_group_query)
    age_groups = [
        {"yas_grubu": row[0], "count": row[1]}
        for row in age_group_result
    ]
    
    # Count by subject
    subject_query = select(
        Kazanim.ders,
        func.count(Kazanim.id).label('count')
    ).group_by(Kazanim.ders).order_by(func.count(Kazanim.id).desc())
    
    subject_result = await db.execute(subject_query)
    subjects = [
        {"ders": row[0], "count": row[1]}
        for row in subject_result
    ]
    
    return {
        "total": total,
        "by_age_group": age_groups,
        "by_subject": subjects
    }

@router.get("/options/age-groups")
async def get_age_groups(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all unique age groups
    """
    query = select(Kazanim.yas_grubu).distinct().order_by(Kazanim.yas_grubu)
    result = await db.execute(query)
    age_groups = [row[0] for row in result if row[0]]
    
    return {"age_groups": age_groups}

@router.get("/options/subjects")
async def get_subjects(
    yas_grubu: Optional[str] = Query(None, description="Filter subjects by age group"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all unique subjects, optionally filtered by age group
    """
    query = select(Kazanim.ders).distinct()
    
    if yas_grubu:
        query = query.where(Kazanim.yas_grubu == yas_grubu)
    
    query = query.order_by(Kazanim.ders)
    result = await db.execute(query)
    subjects = [row[0] for row in result if row[0]]
    
    return {"subjects": subjects}