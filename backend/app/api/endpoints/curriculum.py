from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from app.db.session import get_db
from app.models.curriculum import (
    ButunlesikBilesenler,
    Degerler,
    Egilimler,
    KavramsalBeceriler,
    SurecBilesenleri
)
from app.models.kazanim import Kazanim

router = APIRouter()


@router.get("/")
async def get_curriculum(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(1000, description="Limit number of results"),
    yas: Optional[str] = Query(None, description="Filter by age group"),
    ders: Optional[str] = Query(None, description="Filter by subject")
) -> List[Dict[str, Any]]:
    """Get all curriculum items (kazanımlar) - for compatibility with frontend"""
    query = select(Kazanim)

    # Apply filters
    if yas:
        # Convert the age format if needed (e.g., "36-48 Ay" to "36-48 ay")
        query = query.where(Kazanim.yas_grubu.ilike(f"%{yas}%"))

    if ders:
        query = query.where(Kazanim.ders.ilike(f"%{ders}%"))

    # Apply limit
    query = query.limit(limit)

    # Execute query
    result = await db.execute(query)
    kazanimlar = result.scalars().all()

    # Convert to dict format expected by frontend
    return [
        {
            "id": k.id,
            "yas": k.yas_grubu,
            "ders": k.ders,
            "alan_becerileri": k.alan_becerileri,
            "butunlesik_beceriler": k.butunlesik_beceriler,
            "surec_bileşenleri": k.surec_bilesenleri,
            "ogrenme_ciktilari": k.ogrenme_ciktilari,
            "alt_ogrenme_ciktilari": k.alt_ogrenme_ciktilari
        }
        for k in kazanimlar
    ]


@router.get("/butunlesik-bilesenler")
async def get_butunlesik_bilesenler(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all Bütünleşik Bileşenler"""
    result = await db.execute(select(ButunlesikBilesenler))
    records = result.scalars().all()
    return [record.to_dict() for record in records]


@router.get("/degerler")
async def get_degerler(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all Değerler"""
    result = await db.execute(select(Degerler))
    records = result.scalars().all()
    return [record.to_dict() for record in records]


@router.get("/degerler/grouped")
async def get_degerler_grouped(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get Değerler grouped by Ana Değer"""
    result = await db.execute(select(Degerler))
    records = result.scalars().all()
    grouped = {}
    
    for record in records:
        ana_deger = record.ana_deger_adi
        if ana_deger not in grouped:
            grouped[ana_deger] = {
                "kod": record.ana_deger_kodu,
                "aciklama": record.ana_deger_aciklamasi,
                "alt_degerler": []
            }
        
        if record.alt_deger_adi:
            alt_deger = {
                "kod": record.alt_deger_kodu,
                "adi": record.alt_deger_adi,
                "davranis_gostergeleri": []
            }
            
            # Check if this alt_deger already exists
            existing = next((ad for ad in grouped[ana_deger]["alt_degerler"] 
                           if ad["kod"] == record.alt_deger_kodu), None)
            
            if existing:
                if record.davranis_gostergesi_kodu:
                    existing["davranis_gostergeleri"].append({
                        "kod": record.davranis_gostergesi_kodu,
                        "aciklama": record.davranis_gostergesi_aciklamasi,
                        "ogretim_yontemleri": record.ogretim_yontemleri
                    })
            else:
                if record.davranis_gostergesi_kodu:
                    alt_deger["davranis_gostergeleri"].append({
                        "kod": record.davranis_gostergesi_kodu,
                        "aciklama": record.davranis_gostergesi_aciklamasi,
                        "ogretim_yontemleri": record.ogretim_yontemleri
                    })
                grouped[ana_deger]["alt_degerler"].append(alt_deger)
    
    return grouped


@router.get("/egilimler")
async def get_egilimler(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all Eğilimler"""
    result = await db.execute(select(Egilimler))
    records = result.scalars().all()
    return [record.to_dict() for record in records]


@router.get("/egilimler/grouped")
async def get_egilimler_grouped(db: AsyncSession = Depends(get_db)) -> Dict[str, List[str]]:
    """Get Eğilimler grouped by Ana Eğilim"""
    result = await db.execute(select(Egilimler))
    records = result.scalars().all()
    grouped = {}
    
    for record in records:
        if record.ana_egilim not in grouped:
            grouped[record.ana_egilim] = []
        grouped[record.ana_egilim].append(record.alt_egilim)
    
    return grouped


@router.get("/kavramsal-beceriler")
async def get_kavramsal_beceriler(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all Kavramsal Beceriler"""
    result = await db.execute(select(KavramsalBeceriler))
    records = result.scalars().all()
    return [record.to_dict() for record in records]


@router.get("/kavramsal-beceriler/grouped")
async def get_kavramsal_beceriler_grouped(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get Kavramsal Beceriler grouped by category"""
    result = await db.execute(select(KavramsalBeceriler))
    records = result.scalars().all()
    grouped = {}
    
    for record in records:
        kategori = record.ana_beceri_kategorisi
        if kategori not in grouped:
            grouped[kategori] = []
        
        beceri = {
            "kod": record.ana_beceri_kodu,
            "adi": record.ana_beceri_adi,
            "alt_beceri_kodu": record.alt_beceri_kodu,
            "alt_beceri_adi": record.alt_beceri_adi,
            "surec_bileseni_kodu": record.surec_bileseni_kodu,
            "aciklama": record.aciklama
        }
        grouped[kategori].append(beceri)
    
    return grouped


@router.get("/surec-bilesenleri")
async def get_surec_bilesenleri(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all Süreç Bileşenleri"""
    result = await db.execute(select(SurecBilesenleri))
    records = result.scalars().all()
    return [record.to_dict() for record in records]


@router.get("/surec-bilesenleri/grouped")
async def get_surec_bilesenleri_grouped(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get Süreç Bileşenleri grouped by component"""
    result = await db.execute(select(SurecBilesenleri))
    records = result.scalars().all()
    grouped = {}
    
    for record in records:
        bilesen_kodu = record.surec_bileseni_kodu
        if bilesen_kodu not in grouped:
            grouped[bilesen_kodu] = {
                "adi": record.surec_bileseni_adi,
                "gostergeler": []
            }
        
        if record.gosterge_kodu:
            grouped[bilesen_kodu]["gostergeler"].append({
                "kod": record.gosterge_kodu,
                "aciklama": record.gosterge_aciklamasi
            })
    
    return grouped