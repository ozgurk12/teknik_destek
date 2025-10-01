# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.etkinlik import Etkinlik
from app.models.kazanim import Kazanim

logger = logging.getLogger(__name__)

class GunlukPlanService:
    """Service for processing daily plans and extracting curriculum data"""

    async def process_activities_for_plan(
        self,
        db: AsyncSession,
        activity_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Process selected activities and extract all curriculum components
        Returns structured data for daily plan
        """
        try:
            # Fetch all selected activities
            query = select(Etkinlik).where(Etkinlik.id.in_(activity_ids))
            result = await db.execute(query)
            activities = result.scalars().all()

            if not activities:
                logger.warning(f"No activities found for IDs: {activity_ids}")
                return {}

            # Initialize collections
            alan_becerileri = {}
            kavramsal_beceriler = {}
            egilimler = {}
            sosyal_duygusal = {}
            degerler = {}
            okuryazarlik = {}
            ogrenme_ciktilari = {}
            all_materials = []
            all_concepts = []
            all_words = []

            # Collect unique activity areas to filter kazanims
            selected_activity_areas = set()
            for activity in activities:
                if activity.alan_adi:
                    selected_activity_areas.add(activity.alan_adi)
                    logger.info(f"Added activity area: {activity.alan_adi}")

            logger.info(f"Total selected activity areas: {selected_activity_areas}")

            # Process each activity
            for activity in activities:
                # Get kazanims for this activity
                if activity.kazanim_idleri:
                    kazanim_query = select(Kazanim).where(
                        Kazanim.id.in_(activity.kazanim_idleri)
                    )
                    kazanim_result = await db.execute(kazanim_query)
                    kazanims = kazanim_result.scalars().all()

                    for kazanim in kazanims:
                        # ONLY include kazanims that match the selected activities' areas
                        # Map between activity area names and kazanim ders names
                        area_mapping = {
                            'Matematik': 'MATEMATİK',
                            'Türkçe': 'TÜRKÇE',
                            'Fen': 'FEN VE EKOLOJİ',
                            'Fen ve Ekoloji': 'FEN VE EKOLOJİ',
                            'Sanat': 'SANAT',
                            'Müzik': 'MÜZİK',
                            'Hareket': 'HAREKET VE SAĞLIK',
                            'Hareket ve Sağlık': 'HAREKET VE SAĞLIK'
                        }

                        # Don't filter by area name - we should include all kazanims from selected activities
                        # The area matching was causing issues with combined areas like "Türkçe + Müzik"
                        should_include = True
                        logger.info(f"Including kazanim from {kazanim.ders}")

                        # Process Alan Becerileri
                        if kazanim.alan_becerileri:
                            self._add_to_dict(alan_becerileri, kazanim.ders, kazanim.alan_becerileri)

                        # Process Öğrenme Çıktıları with codes
                        if kazanim.ogrenme_ciktilari:
                            # Add the main learning outcome
                            self._add_to_dict(
                                ogrenme_ciktilari,
                                kazanim.ders,
                                kazanim.ogrenme_ciktilari
                            )

                            # Add sub-learning outcomes if available
                            if kazanim.alt_ogrenme_ciktilari:
                                # Process süreç bileşenleri - remove duplicate prefix if exists
                                if kazanim.surec_bilesenleri:
                                    surec_code = kazanim.surec_bilesenleri
                                    # Check if it already starts with area code (like TAB1.1.SB2)
                                    alan_key = self._get_alan_code(kazanim.ders)
                                    if surec_code.startswith(alan_key):
                                        # Remove the duplicate area code prefix
                                        surec_code = surec_code[len(alan_key):]
                                        if surec_code.startswith('.'):
                                            surec_code = surec_code[1:]

                                    formatted_alt = f"{surec_code}. {kazanim.alt_ogrenme_ciktilari}"
                                else:
                                    formatted_alt = kazanim.alt_ogrenme_ciktilari

                                self._add_to_dict(
                                    ogrenme_ciktilari,
                                    kazanim.ders,
                                    formatted_alt
                                )

                        # Process Bütünleşik Beceriler (Kavramsal, Eğilimler, etc.)
                        if kazanim.butunlesik_beceriler:
                            self._process_butunlesik_beceriler(
                                kazanim.butunlesik_beceriler,
                                kavramsal_beceriler,
                                egilimler,
                                sosyal_duygusal,
                                degerler,
                                okuryazarlik
                            )

                # Collect materials and concepts from activity
                if activity.materyaller:
                    all_materials.append(activity.materyaller)

                # Extract concepts and words from activity (if stored)
                # This could be enhanced with AI extraction

            # Format collected data
            plan_data = {
                'alan_becerileri': self._format_curriculum_section(alan_becerileri),
                'kavramsal_beceriler': self._format_curriculum_section(kavramsal_beceriler),
                'egilimler': self._format_curriculum_section(egilimler),
                'sosyal_duygusal_beceriler': self._format_curriculum_section(sosyal_duygusal),
                'degerler': self._format_curriculum_section(degerler),
                'okuryazarlik_becerileri': self._format_curriculum_section(okuryazarlik),
                'ogrenme_ciktilari': self._format_curriculum_section(ogrenme_ciktilari),
                'materyaller': self._merge_materials(all_materials),
                'etkinlikler': self._format_activities(activities)
            }

            return plan_data

        except Exception as e:
            logger.error(f"Error processing activities for plan: {str(e)}")
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

    def _add_to_dict(self, target_dict: Dict, key: str, value: str):
        """Add value to dictionary with proper formatting"""
        if key not in target_dict:
            target_dict[key] = []
        if value and value not in target_dict[key]:
            target_dict[key].append(value)

    def _process_butunlesik_beceriler(
        self,
        beceriler: str,
        kavramsal: Dict,
        egilimler: Dict,
        sosyal_duygusal: Dict,
        degerler: Dict,
        okuryazarlik: Dict
    ):
        """Process and categorize integrated skills"""
        beceri_list = beceriler.split(',') if beceriler else []

        for beceri in beceri_list:
            beceri = beceri.strip()

            # Categorize based on prefixes
            if beceri.startswith('KB'):
                self._add_to_dict(kavramsal, 'Kavramsal Beceriler', beceri)
            elif beceri.startswith('E'):
                self._add_to_dict(egilimler, 'Eğilimler', beceri)
            elif beceri.startswith('SDB'):
                self._add_to_dict(sosyal_duygusal, 'Sosyal-Duygusal Öğrenme', beceri)
            elif beceri.startswith('D'):
                self._add_to_dict(degerler, 'Değerler', beceri)
            elif beceri.startswith('OB'):
                self._add_to_dict(okuryazarlik, 'Okuryazarlık Becerileri', beceri)

    def _format_curriculum_section(self, data: Dict) -> Dict:
        """Format curriculum section for output"""
        formatted = {}
        for key, values in data.items():
            if values:
                formatted[key] = values
        return formatted

    def _merge_materials(self, materials_list: List[str]) -> str:
        """Merge and deduplicate materials from multiple activities"""
        all_items = []
        for materials in materials_list:
            if materials:
                items = materials.split('\n')
                for item in items:
                    item = item.strip()
                    if item and item not in all_items:
                        all_items.append(item)
        return '\n'.join(all_items)

    def _format_activities(self, activities: List[Etkinlik]) -> str:
        """Format activities for daily plan"""
        formatted_activities = []

        for i, activity in enumerate(activities, 1):
            activity_text = f"ETKİNLİK {i}: {activity.etkinlik_adi}\n"
            activity_text += f"Alan: {activity.alan_adi}\n"
            activity_text += f"Süre: {activity.sure} dakika\n\n"

            if activity.uygulama_sureci:
                activity_text += activity.uygulama_sureci

            formatted_activities.append(activity_text)

        return '\n\n'.join(formatted_activities)

# Singleton instance
gunluk_plan_service = GunlukPlanService()