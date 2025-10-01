# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.etkinlik import Etkinlik
from app.models.kazanim import Kazanim
import random

logger = logging.getLogger(__name__)

class EtkinlikService:
    """Service for managing activities and extracting curriculum components"""

    async def extract_curriculum_from_kazanims(
        self,
        db: AsyncSession,
        kazanim_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Extract all curriculum components from selected kazanims
        Returns structured curriculum data to be saved with activity
        """
        try:
            if not kazanim_ids:
                return {}

            # Fetch all selected kazanims
            query = select(Kazanim).where(Kazanim.id.in_(kazanim_ids))
            result = await db.execute(query)
            kazanims = result.scalars().all()

            if not kazanims:
                logger.warning(f"No kazanims found for IDs: {kazanim_ids}")
                return {}

            # Initialize collections
            alan_becerileri = {}
            ogrenme_ciktilari = {}
            kavramsal_beceriler = []
            egilimler = []
            sosyal_duygusal = []
            degerler = []
            okuryazarlik = []

            for kazanim in kazanims:
                # Process Alan Becerileri
                if kazanim.alan_becerileri:
                    if kazanim.ders not in alan_becerileri:
                        alan_becerileri[kazanim.ders] = []
                    if kazanim.alan_becerileri not in alan_becerileri[kazanim.ders]:
                        alan_becerileri[kazanim.ders].append(kazanim.alan_becerileri)

                # Process Öğrenme Çıktıları with codes
                if kazanim.ogrenme_ciktilari:
                    # Add the main learning outcome
                    if kazanim.ders not in ogrenme_ciktilari:
                        ogrenme_ciktilari[kazanim.ders] = []
                    if kazanim.ogrenme_ciktilari not in ogrenme_ciktilari[kazanim.ders]:
                        ogrenme_ciktilari[kazanim.ders].append(kazanim.ogrenme_ciktilari)

                # Add sub-learning outcomes if available
                if kazanim.alt_ogrenme_ciktilari and kazanim.surec_bilesenleri:
                    surec_code = kazanim.surec_bilesenleri
                    alan_key = self._get_alan_code(kazanim.ders)
                    # Check if it already starts with area code (like TAB1.1.SB2)
                    if surec_code.startswith(alan_key):
                        # Remove the duplicate area code prefix
                        surec_code = surec_code[len(alan_key):]
                        if surec_code.startswith('.'):
                            surec_code = surec_code[1:]

                    formatted_alt = f"{surec_code}. {kazanim.alt_ogrenme_ciktilari}"

                    if kazanim.ders not in ogrenme_ciktilari:
                        ogrenme_ciktilari[kazanim.ders] = []
                    if formatted_alt not in ogrenme_ciktilari[kazanim.ders]:
                        ogrenme_ciktilari[kazanim.ders].append(formatted_alt)

                # Process bütünleşik beceriler field to extract area codes
                if kazanim.butunlesik_beceriler:
                    # Extract area codes from butunlesik_beceriler
                    # Format is like "TAB1.1. Dinlemeyi/İzlemeyi Yönetme"
                    beceri_text = kazanim.butunlesik_beceriler

                    # Parse area codes from the text
                    if beceri_text:
                        # Extract the area code prefix (TAB, MAB, HSAB, etc.)
                        area_code = beceri_text.split('.')[0] if '.' in beceri_text else beceri_text.split()[0]

                        # Map area codes to bütünleşik beceri categories
                        # These should be enriched from actual curriculum tables
                        # For now, we'll use the area codes as indicators

            # Get areas from selected kazanims to determine which curriculum to include
            selected_areas = set(k.ders for k in kazanims if k.ders)

            # Sosyal duygusal beceriler - kazanımlardaki süreç bileşenlerinden SDB kodlu olanlar
            for kazanim in kazanims:
                if kazanim.surec_bilesenleri and 'SDB' in kazanim.surec_bilesenleri:
                    if kazanim.surec_bilesenleri not in sosyal_duygusal:
                        sosyal_duygusal.append(kazanim.surec_bilesenleri)

            # Don't randomly enrich - frontend will provide selected values
            # These will be overridden in the endpoint if frontend provides them

            # Return structured curriculum data
            curriculum_data = {
                'alan_becerileri': alan_becerileri,
                'ogrenme_ciktilari': ogrenme_ciktilari,
                'kavramsal_beceriler': kavramsal_beceriler,
                'egilimler': egilimler,
                'sosyal_duygusal': sosyal_duygusal,
                'degerler': degerler,
                'okuryazarlik': okuryazarlik
            }

            logger.info(f"Extracted curriculum data for {len(kazanims)} kazanims")
            return curriculum_data

        except Exception as e:
            logger.error(f"Error extracting curriculum from kazanims: {str(e)}")
            raise

    def _get_alan_code(self, ders: str) -> str:
        """Get standard code for subject area"""
        alan_codes = {
            'MATEMATİK': 'MAB',
            'TÜRKÇE': 'TAB',
            'HAREKET VE SAĞLIK': 'HSAB',
            'SANAT': 'SNAB',
            'FEN VE EKOLOJİ': 'FAB',
            'MÜZİK': 'MÜZAB',
            'SOSYAL': 'SOAB'
        }
        return alan_codes.get(ders.upper(), 'AB')

    async def create_activity_with_curriculum(
        self,
        db: AsyncSession,
        activity_data: Dict[str, Any],
        kazanim_ids: List[int]
    ) -> Etkinlik:
        """
        Create activity with extracted curriculum components
        """
        try:
            # Extract curriculum from kazanims
            curriculum = await self.extract_curriculum_from_kazanims(db, kazanim_ids)

            # Create activity with curriculum data
            activity = Etkinlik(
                **activity_data,
                kazanim_idleri=kazanim_ids,
                curriculum_data=curriculum,
                alan_becerileri=curriculum.get('alan_becerileri'),
                ogrenme_ciktilari=curriculum.get('ogrenme_ciktilari'),
                kavramsal_beceriler=curriculum.get('kavramsal_beceriler'),
                egilimler=curriculum.get('egilimler'),
                sosyal_duygusal=curriculum.get('sosyal_duygusal'),
                degerler=curriculum.get('degerler'),
                okuryazarlik=curriculum.get('okuryazarlik')
            )

            db.add(activity)
            await db.commit()
            await db.refresh(activity)

            logger.info(f"Created activity with curriculum: {activity.etkinlik_adi}")
            return activity

        except Exception as e:
            logger.error(f"Error creating activity with curriculum: {str(e)}")
            await db.rollback()
            raise

# Singleton instance
etkinlik_service = EtkinlikService()