import json
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings

from app.models.kazanim import Kazanim
from app.models.curriculum import (
    ButunlesikBilesenler,
    Degerler,
    Egilimler,
    KavramsalBeceriler,
    SurecBilesenleri
)

logger = logging.getLogger(__name__)

class AylikPlanAIService:
    def __init__(self):
        # Get credentials path from settings
        credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
        if not credentials_path:
            credentials_path = "../credentials/google-service-account.json"

        if not os.path.isabs(credentials_path):
            credentials_path = os.path.abspath(credentials_path)

        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # Get configuration from settings/env
        project_id = settings.VERTEX_AI_PROJECT_ID or "kocai-451112"
        location = settings.VERTEX_AI_LOCATION or "europe-west1"
        model_name = settings.VERTEX_AI_MODEL or "gemini-2.5-pro"

        # Initialize Vertex AI with credentials
        vertexai.init(
            project=project_id,
            location=location,
            credentials=credentials
        )

        # Use the model specified in environment
        self.model = GenerativeModel(model_name)
        self.model_name = model_name
        logger.info(f"Initialized AylikPlanAIService with model: {model_name} in location: {location}")

    async def generate_aylik_plan(
        self,
        db: AsyncSession,
        yas_grubu: str,
        ay: str,
        kazanim_ids: List[int],
        curriculum_ids: Optional[List[int]] = None,
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Yapay zeka kullanarak aylık plan üretir.
        """
        try:
            # Kazanımları getir
            query = select(Kazanim).where(Kazanim.id.in_(kazanim_ids))
            result = await db.execute(query)
            kazanimlar = result.scalars().all()

            # Curriculum'ları getir
            curriculums = {
                'butunlesik_bilesenler': [],
                'degerler': [],
                'egilimler': [],
                'kavramsal_beceriler': [],
                'surec_bilesenleri': []
            }

            # Store formatted curriculum items for direct use
            formatted_curriculums = {
                'kavramsal_beceriler': [],
                'egilimler': [],
                'sosyal_duygusal': [],
                'degerler': [],
                'okuryazarlik': []
            }

            if curriculum_ids:
                # Her curriculum tablosundan ilgili verileri getir
                # ID'ler frontend'den hangi tipte geldiğini belirtecek şekilde gelebilir
                # Şimdilik tüm tabloları kontrol ediyoruz

                # Bütünleşik Bileşenler
                query = select(ButunlesikBilesenler).where(
                    ButunlesikBilesenler.id.in_(curriculum_ids)
                )
                result = await db.execute(query)
                bb_items = result.scalars().all()
                curriculums['butunlesik_bilesenler'] = bb_items
                # Format for direct display - these include Okuryazarlık Becerileri
                for item in bb_items:
                    bb_text = item.butunlesik_bilesenler or ''
                    alt_bb = item.alt_butunlesik_bilesenler or item.surec_bilesenleri or ''
                    # Check if it's literacy related
                    if 'Okuryazarlık' in bb_text or 'OB' in bb_text:
                        formatted_curriculums['okuryazarlik'].append(f"{bb_text[:50]}")
                    # Also add to sosyal-duygusal if it's SDB related
                    elif 'Sosyal' in bb_text or 'Duygusal' in bb_text or 'SDB' in bb_text:
                        formatted_curriculums['sosyal_duygusal'].append(f"{bb_text[:50]}")

                # Değerler
                query = select(Degerler).where(
                    Degerler.id.in_(curriculum_ids)
                )
                result = await db.execute(query)
                d_items = result.scalars().all()
                curriculums['degerler'] = d_items
                # Format for direct display
                for item in d_items:
                    code = f"{item.ana_deger_kodu}"
                    desc = item.ana_deger_adi or item.alt_deger_adi or ''
                    formatted_curriculums['degerler'].append(f"{code} {desc[:30]}")

                # Eğilimler
                query = select(Egilimler).where(
                    Egilimler.id.in_(curriculum_ids)
                )
                result = await db.execute(query)
                eg_items = result.scalars().all()
                curriculums['egilimler'] = eg_items
                # Format for direct display
                for item in eg_items:
                    formatted_curriculums['egilimler'].append(f"{item.ana_egilim} - {item.alt_egilim}"[:50])

                # Kavramsal Beceriler
                query = select(KavramsalBeceriler).where(
                    KavramsalBeceriler.id.in_(curriculum_ids)
                )
                result = await db.execute(query)
                kb_items = result.scalars().all()
                curriculums['kavramsal_beceriler'] = kb_items
                # Format for direct display
                for item in kb_items:
                    code = f"{item.ana_beceri_kodu}"
                    desc = item.ana_beceri_adi or item.alt_beceri_adi or item.aciklama or ''
                    formatted_curriculums['kavramsal_beceriler'].append(f"{code} {desc[:30]}")

                # Süreç Bileşenleri
                query = select(SurecBilesenleri).where(
                    SurecBilesenleri.id.in_(curriculum_ids)
                )
                result = await db.execute(query)
                sb_items = result.scalars().all()
                curriculums['surec_bilesenleri'] = sb_items
                # Format for direct display
                for item in sb_items:
                    code = item.surec_bileseni_kodu or ''
                    desc = item.surec_bileseni_adi or item.gosterge_aciklamasi or ''
                    # Check what type of skill this is and add to appropriate category
                    if 'OB' in code:
                        formatted_curriculums['okuryazarlik'].append(f"{code} {desc[:30]}")
                    elif 'SDB' in code:
                        formatted_curriculums['sosyal_duygusal'].append(f"{code} {desc[:30]}")

            # Prompt oluştur - pass formatted_curriculums to include in prompt
            prompt = self._create_prompt(yas_grubu, ay, kazanimlar, curriculums, formatted_curriculums, custom_instructions)

            # Store formatted curriculums for later use
            self.formatted_curriculums = formatted_curriculums

            # AI'dan yanıt al
            generation_config = GenerationConfig(
                temperature=0.8,
                max_output_tokens=8192,
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )

            # Yanıtı parse et
            logger.info(f"AI Response length: {len(response.text)}")
            logger.info(f"AI Response (first 1000 chars): {response.text[:1000]}")

            plan_data = self._parse_response(response.text, yas_grubu, ay)
            plan_data["ai_prompt"] = prompt

            # IMPORTANT: If curriculum items were selected by user, ALWAYS use them instead of AI-generated content
            if formatted_curriculums['kavramsal_beceriler']:
                # Always prioritize user-selected curriculum over AI-generated content
                plan_data['kavramsal_beceriler'] = {'Kavramsal Beceriler': formatted_curriculums['kavramsal_beceriler']}
                logger.info(f"Using user-selected kavramsal_beceriler: {len(formatted_curriculums['kavramsal_beceriler'])} items")

            if formatted_curriculums['egilimler']:
                # Always prioritize user-selected curriculum over AI-generated content
                plan_data['egilimler'] = {'Eğilimler': formatted_curriculums['egilimler']}
                logger.info(f"Using user-selected egilimler: {len(formatted_curriculums['egilimler'])} items")

            if formatted_curriculums['degerler']:
                # Always prioritize user-selected curriculum over AI-generated content
                plan_data['degerler'] = {'Değerler': formatted_curriculums['degerler']}
                logger.info(f"Using user-selected degerler: {len(formatted_curriculums['degerler'])} items")

            if formatted_curriculums['okuryazarlik']:
                # Always prioritize user-selected curriculum over AI-generated content
                plan_data['okuryazarlik_becerileri'] = {'Okuryazarlık Becerileri': formatted_curriculums['okuryazarlik']}
                logger.info(f"Using user-selected okuryazarlik: {len(formatted_curriculums['okuryazarlik'])} items")

            if formatted_curriculums['sosyal_duygusal']:
                # Always prioritize user-selected curriculum over AI-generated content
                plan_data['sosyal_duygusal_beceriler'] = {'Sosyal-Duygusal Beceriler': formatted_curriculums['sosyal_duygusal']}
                logger.info(f"Using user-selected sosyal_duygusal: {len(formatted_curriculums['sosyal_duygusal'])} items")

            # Debug: Log parsed data in detail
            logger.info(f"Parsed plan_data keys: {plan_data.keys()}")
            for key in ['alan_becerileri', 'kavramsal_beceriler', 'egilimler', 'sosyal_duygusal_beceriler', 'degerler', 'okuryazarlik_becerileri']:
                if key in plan_data:
                    value = plan_data[key]
                    if isinstance(value, dict):
                        logger.info(f"{key}: {len(value)} categories, {sum(len(v) if isinstance(v, list) else 1 for v in value.values())} total items")
                    elif isinstance(value, list):
                        logger.info(f"{key}: {len(value)} items")
                    else:
                        logger.info(f"{key}: {str(value)[:200]}")

            # Check if critical sections are empty and log warning
            if not plan_data.get('alan_becerileri') or plan_data.get('alan_becerileri') == {}:
                logger.warning("Alan becerileri is empty!")
            if not plan_data.get('kavramsal_beceriler') or plan_data.get('kavramsal_beceriler') == {}:
                logger.warning("Kavramsal beceriler is empty!")

            return plan_data

        except Exception as e:
            logger.error(f"Aylık plan oluşturma hatası: {str(e)}")
            raise Exception(f"Aylık plan oluşturulamadı: {str(e)}")

    def _create_prompt(
        self,
        yas_grubu: str,
        ay: str,
        kazanimlar: List[Kazanim],
        curriculums: Dict[str, Any],
        formatted_curriculums: Dict[str, List[str]],
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        AI için prompt oluşturur.
        """
        logger.info(f"Creating prompt for {len(kazanimlar)} kazanims")

        # Daha detaylı kazanım bilgisi ve hangi alanların dahil edildiği
        included_areas = set()
        kazanim_texts = []
        kazanim_details_for_ai = []  # AI'ya verilecek tam kazanım metinleri

        for k in kazanimlar:
            included_areas.add(k.ders)

            # AI için detaylı kazanım bilgisi
            kazanim_detail = f"""
KAZANIM ID {k.id} - {k.ders} DERSİ:
  Alan Becerisi: {k.alan_becerileri}
  Öğrenme Çıktısı: {k.ogrenme_ciktilari}
  Alt Öğrenme Çıktıları: {k.alt_ogrenme_ciktilari if k.alt_ogrenme_ciktilari else 'Yok'}
  Bütünleşik Beceriler: {k.butunlesik_beceriler if k.butunlesik_beceriler else 'Yok'}
  Süreç Bileşenleri: {k.surec_bilesenleri if k.surec_bilesenleri else 'Yok'}"""
            kazanim_texts.append(kazanim_detail)

            # Sadece kazanım metinlerini topla
            kazanim_details_for_ai.append({
                'ders': k.ders,
                'alan_becerisi': k.alan_becerileri,
                'ogrenme_ciktisi': k.ogrenme_ciktilari
            })

        # Dahil edilecek alanları açıkça belirt
        included_areas_text = f"\nSADECE ŞU ALANLAR PLANLANACAK: {', '.join(sorted(included_areas))}\n"

        kazanim_text = "\n".join(kazanim_texts)
        logger.info(f"Kazanim text length: {len(kazanim_text)}")

        curriculum_text = ""
        curriculum_sections = []

        # Bütünleşik Bileşenler
        if curriculums.get('butunlesik_bilesenler'):
            items = [f"- {b.butunlesik_bilesenler}: {b.alt_butunlesik_bilesenler or b.surec_bilesenleri}"
                    for b in curriculums['butunlesik_bilesenler']]
            if items:
                curriculum_sections.append(f"BÜTÜNLEŞIK BILEŞENLER:\n" + "\n".join(items))

        # Değerler
        if curriculums.get('degerler'):
            items = [f"- {d.ana_deger_kodu} {d.ana_deger_adi}: {d.alt_deger_adi or d.ana_deger_aciklamasi}"
                    for d in curriculums['degerler']]
            if items:
                curriculum_sections.append(f"DEĞERLER:\n" + "\n".join(items))

        # Eğilimler
        if curriculums.get('egilimler'):
            items = [f"- {e.ana_egilim}: {e.alt_egilim}"
                    for e in curriculums['egilimler']]
            if items:
                curriculum_sections.append(f"EĞİLİMLER:\n" + "\n".join(items))

        # Kavramsal Beceriler
        if curriculums.get('kavramsal_beceriler'):
            items = [f"- {k.ana_beceri_kodu} {k.ana_beceri_adi}: {k.alt_beceri_adi or k.aciklama or ''}"
                    for k in curriculums['kavramsal_beceriler']]
            if items:
                curriculum_sections.append(f"KAVRAMSAL BECERİLER:\n" + "\n".join(items))

        # Süreç Bileşenleri
        if curriculums.get('surec_bilesenleri'):
            items = [f"- {s.surec_bileseni_kodu}: {s.surec_bileseni_adi or s.gosterge_aciklamasi or ''}"
                    for s in curriculums['surec_bilesenleri']]
            if items:
                curriculum_sections.append(f"SÜREÇ BİLEŞENLERİ:\n" + "\n".join(items))

        if curriculum_sections:
            curriculum_text = "\n\n".join(curriculum_sections)

        logger.info(f"Curriculum text length: {len(curriculum_text)}")
        logger.info(f"Total prompt will include {len(kazanimlar)} kazanims and curriculum data")

        # Add selected curriculum items to instructions if they exist
        selected_curriculum_warning = ""
        if any(formatted_curriculums.values()):
            selected_curriculum_warning = """
🔴 ÇOK ÖNEMLİ: Kullanıcı aşağıdaki curriculum öğelerini seçti. BUNLARI AYNEN KULLANMAK ZORUNDASIN:
"""
            if formatted_curriculums.get('kavramsal_beceriler'):
                selected_curriculum_warning += f"KAVRAMSAL BECERİLER: {', '.join(formatted_curriculums['kavramsal_beceriler'][:5])}\n"
            if formatted_curriculums.get('egilimler'):
                selected_curriculum_warning += f"EĞİLİMLER: {', '.join(formatted_curriculums['egilimler'][:5])}\n"
            if formatted_curriculums.get('degerler'):
                selected_curriculum_warning += f"DEĞERLER: {', '.join(formatted_curriculums['degerler'][:5])}\n"
            if formatted_curriculums.get('sosyal_duygusal'):
                selected_curriculum_warning += f"SOSYAL-DUYGUSAL: {', '.join(formatted_curriculums['sosyal_duygusal'][:5])}\n"
            if formatted_curriculums.get('okuryazarlik'):
                selected_curriculum_warning += f"OKURYAZARLIK: {', '.join(formatted_curriculums['okuryazarlik'][:5])}\n"

        prompt = f"""
Sen Türkiye Maarif Modeli'ne göre okul öncesi eğitim için aylık plan hazırlayan bir eğitim uzmanısın.

Aşağıdaki bilgilere göre {yas_grubu} yaş grubu için {ay} ayı aylık planı oluştur.

🚨 KRİTİK KURALLAR - BUNLARA MUTLAKA UY:
1. SADECE aşağıda verilen kazanımları kullan. Başka kazanım ekleme!
2. SADECE kazanımlarda belirtilen derslerin/alanların planını yap.
3. Kazanımda olmayan hiçbir alan için plan yapma (örn: kazanımda Müzik yoksa Müzik alanı ekleme).
4. Her kazanımı olduğu gibi kullan, değiştirme veya genişletme.
5. Alan Becerilerinde SADECE {', '.join(sorted(included_areas))} alanlarını ekle, başka alan ekleme.
6. ⚠️ ÇOK ÖNEMLİ: TÜM METİNLERİ TAMAMEN YAZ! Hiçbir metni kısaltma, kesme veya "..." ile bitirme!
7. ⚠️ ÇOK ÖNEMLİ: Her madde/cümle TAMAMEN yazılmalı, yarıda bırakılmamalı!
{selected_curriculum_warning}

{included_areas_text}
Toplam {len(kazanimlar)} kazanım verildi. SADECE bunları kullan:

VERİLEN KAZANIMLAR (DEĞİŞTİRMEDEN KULLAN):
{kazanim_text}

{f"CURRICULUM KONULARI:\n{curriculum_text}" if curriculum_text else ""}

{f"ÖZEL TALİMATLAR: {custom_instructions}" if custom_instructions else ""}

AYLIK PLAN FORMATI (TAM OLARAK BU FORMATI KULLAN):

## 1. ALAN BECERİLERİ

⚠️ UYARI: SADECE verilen kazanımlardaki alanları ve kodları kullan!
FORMAT: Her alan için sadece KOD ve KISA AÇIKLAMA yaz.

Örnek format:
### Türkçe Alanı:
TADB. Dinleme/İzleme
TAOB. Okuma
TAKB. Konuşma

### Matematik Alanı:
MAB1. Sayma
MAB2. Geometri

SADECE verilen kazanımdaki alan kodlarını yaz, fazla detay ekleme!

## 2. KAVRAMSAL BECERİLER

⚠️ HER SATIRI TAM OLARAK YAZ! Cümleleri yarıda KESME!
{f"ZORUNLU - AYNEN KULLAN:{chr(10)}" + chr(10).join([f"- {item}" for item in formatted_curriculums.get('kavramsal_beceriler', [])]) if curriculum_text and formatted_curriculums.get('kavramsal_beceriler') else ""}
Sadece kod ve TAM açıklama:
KB1.1 Saymak
KB1.5 Bulmak
KB1.6 Seçmek
[Seçilen curriculum'lara uygun diğer beceriler - TAM YAZILACAK]

## 3. EĞİLİMLER

⚠️ HER SATIRI TAM OLARAK YAZ! Parantez içindeki metinleri TAMAMLA!
{f"ZORUNLU - AYNEN KULLAN:{chr(10)}" + chr(10).join([f"- {item}" for item in formatted_curriculums.get('egilimler', [])]) if curriculum_text and formatted_curriculums.get('egilimler') else ""}
E1. Benlik Eğilimleri - E1.1. Merak
E2. Sosyal Eğilimler - E2.5. Oyunseverlik
[Seçilen curriculum'lara uygun diğer eğilimler - HER SATIR TAM YAZILACAK]

## 4. SOSYAL-DUYGUSAL ÖĞRENME BECERİLERİ

⚠️ HER SATIRI TAM OLARAK YAZ! Cümleleri yarıda KESME!
{f"ZORUNLU - AYNEN KULLAN:{chr(10)}" + chr(10).join([f"- {item}" for item in formatted_curriculums.get('sosyal_duygusal', [])]) if curriculum_text and formatted_curriculums.get('sosyal_duygusal') else ""}
SDB2.1. İletişim Becerisi
SDB2.1.SB1 Başkalarını etkin bir şekilde dinlemek
[Seçilen curriculum'lara uygun diğer beceriler - HER CÜMLE TAMAMEN YAZILACAK]

## 5. DEĞERLER

{f"ZORUNLU - AYNEN KULLAN:{chr(10)}" + chr(10).join([f"- {item}" for item in formatted_curriculums.get('degerler', [])]) if curriculum_text and formatted_curriculums.get('degerler') else ""}
D2. Aile Bütünlüğü
D3. Çalışkanlık
[Seçilen curriculum'lara uygun değerler]

## 6. OKURYAZARLIK BECERİLERİ

{f"ZORUNLU - AYNEN KULLAN:{chr(10)}" + chr(10).join([f"- {item}" for item in formatted_curriculums.get('okuryazarlik', [])]) if curriculum_text and formatted_curriculums.get('okuryazarlik') else ""}
OB4. Görsel Okuryazarlık
OB4.1. Görseli Anlama
[Seçilen curriculum'lara uygun beceriler]

## 7. ÖĞRENME ÇIKTILARI VE SÜREÇ BİLEŞENLERİ

⚠️ HER KAZANIMI AYRI SATIRA YAZ! Format:

DERS ADI Öğrenme Çıktısı:
KAZANIM ID X - Alan Becerisi: [KOD]
Öğrenme Çıktısı: [TAM AÇIKLAMA]
Alt Öğrenme Çıktıları: [TAM AÇIKLAMA]
Bütünleşik Beceriler: [TAM AÇIKLAMA]
Süreç Bileşenleri: [TAM AÇIKLAMA]

KAZANIM ID Y - Alan Becerisi: [KOD]
[...benzeri devam et...]

[SADECE verilen kazanımlardaki alanlar için öğrenme çıktıları yaz. HER KAZANIM AYRI SATIRDA!]

## 8. ANAHTAR KAVRAMLAR

[Örnek: Sesli-Sessiz, Gece-Gündüz, Az-Çok, Sert-Yumuşak]

## 9. ÖĞRENME KANITLARI (ÖLÇME VE DEĞERLENDİRME)

### Çocuklar Yönünden Değerlendirme
[Detaylı değerlendirme kriterleri]

### Program Yönünden Değerlendirme
[Program değerlendirme kriterleri]

### Öğretmen Yönünden Değerlendirme
[Öğretmen öz değerlendirme kriterleri]

## 10. ÖĞRENME-ÖĞRETME YAŞANTILARI

⚠️ ETKİNLİK SONLARINDA KODLARI PARANTEZ İÇİNDE YAZ!
Format: (E1.2, KB1.1, TADB.1.a, D1)

Örnek:
"Hikâye Seçimi": Çocuklara 3 farklı hikâye sunulur. Seçim yapmaları istenir ve seçilen hikâye okunur. (KB1.2, TADB.1.a, E1.2, D1)

[SADECE verilen kazanımlardaki alanlar için etkinlikler planla. Her etkinliğin sonunda ilgili kodları parantez içinde yaz!]

## 11. FARKLILAŞTIRMA VE ZENGİNLEŞTİRME

[Bireysel farklılıkları gözeten yaklaşımlar]

## 12. DESTEKLEME

[Özel gereksinimli çocuklar için düzenlemeler]

## 13. AİLE/TOPLUM KATILIMI

[Aile katılımı etkinlikleri ve toplum iş birlikleri]

NOT: Plan {yas_grubu} yaş grubuna uygun, gelişimsel özellikleri dikkate alan, sarmal bir yaklaşımla hazırlanmalıdır.
"""
        return prompt

    def _parse_response(self, response_text: str, yas_grubu: str, ay: str) -> Dict[str, Any]:
        """
        AI yanıtını parse eder ve uygun formata dönüştürür.
        """
        # Debug: Log first 2000 chars of response
        logger.info(f"AI Response (first 2000 chars): {response_text[:2000]}")
        logger.info(f"AI Response total length: {len(response_text)}")

        # Find sections by looking for numbered headers
        import re

        # Extract content for each main section
        def extract_section(pattern, text):
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                start = match.start()
                # Find next numbered section or end
                next_section = re.search(r'\n\s*\#{1,3}\s*\*{0,2}\s*\d+\.\s+', text[start + 1:], re.IGNORECASE)
                if next_section:
                    end = start + 1 + next_section.start()
                else:
                    end = len(text)
                return text[start:end].strip()
            return ""

        alan_section = extract_section(r'\#{1,3}\s*\*{0,2}\s*1\.\s*ALAN\s*BECER', response_text)
        kavramsal_section = extract_section(r'\#{1,3}\s*\*{0,2}\s*2\.\s*KAVRAMSAL\s*BECER', response_text)
        egilimler_section = extract_section(r'\#{1,3}\s*\*{0,2}\s*3\.\s*EĞİLİM', response_text)
        sosyal_section = extract_section(r'\#{1,3}\s*\*{0,2}\s*4\.\s*SOSYAL', response_text)
        degerler_section = extract_section(r'\#{1,3}\s*\*{0,2}\s*5\.\s*DEĞER', response_text)
        okuryazar_section = extract_section(r'\#{1,3}\s*\*{0,2}\s*6\.\s*OKURYAZAR', response_text)
        ogrenme_ciktilari_section = extract_section(r'\#{1,3}\s*\*{0,2}\s*7\.\s*ÖĞRENME\s*ÇIKT', response_text)

        logger.info(f"Extracted sections - Alan: {len(alan_section)}, Kavramsal: {len(kavramsal_section)}, Eğilimler: {len(egilimler_section)}")

        plan_data = {
            "plan_adi": f"{yas_grubu} Yaş {ay} Ayı Planı",
            "yas_grubu": yas_grubu,
            "ay": ay,
            "yil": datetime.now().year,
            "alan_becerileri": {},
            "kavramsal_beceriler": {},
            "egilimler": {},
            "sosyal_duygusal_beceriler": {},
            "degerler": {},
            "okuryazarlik_becerileri": {},
            "ogrenme_ciktilari": {},
            "anahtar_kavramlar": [],
            "degerlendirme": {},
            "ogrenme_ogretme_yasantilari": "",
            "farklilastirma_zenginlestirme": "",
            "destekleme": "",
            "aile_toplum_katilimi": "",
            "ai_generated": True,
            "ai_model": self.model_name
        }

        # Parse extracted sections with the content
        if alan_section:
            # Clean the section header and parse content
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*1\.\s*ALAN\s*BECER[^\n]*\n', '', alan_section, 1)
            plan_data["alan_becerileri"] = self._parse_alan_becerileri_flexible(clean_content)

        if kavramsal_section:
            clean_content = self._clean_markdown(kavramsal_section)
            clean_content = re.sub(r'^2\.\s*KAVRAMSAL\s*BECER[^\n]*\n', '', clean_content, 1)
            kb_lines = []
            for line in clean_content.split('\n'):
                line = line.strip()
                if line and re.match(r'KB[0-9]', line):
                    # Keep full line without truncation
                    kb_lines.append(line)
            # Only add if we found actual items, not default text
            if kb_lines:
                plan_data["kavramsal_beceriler"] = {"Kavramsal Beceriler": kb_lines[:10]}
            else:
                plan_data["kavramsal_beceriler"] = {}

        if egilimler_section:
            clean_content = self._clean_markdown(egilimler_section)
            clean_content = re.sub(r'^3\.\s*EĞİLİM[^\n]*\n', '', clean_content, 1)
            e_lines = []
            for line in clean_content.split('\n'):
                line = line.strip()
                if line and re.match(r'E[0-9]', line):
                    # Keep full line without truncation
                    e_lines.append(line)
            # Only add if we found actual items
            if e_lines:
                plan_data["egilimler"] = {"Eğilimler": e_lines[:10]}
            else:
                plan_data["egilimler"] = {}

        if sosyal_section:
            clean_content = self._clean_markdown(sosyal_section)
            clean_content = re.sub(r'^4\.\s*SOSYAL[^\n]*\n', '', clean_content, 1)
            sdb_lines = []
            for line in clean_content.split('\n'):
                line = line.strip()
                if line and re.match(r'SDB[0-9]', line):
                    # Keep full line without truncation
                    sdb_lines.append(line)
            # Only add if we found actual items
            if sdb_lines:
                plan_data["sosyal_duygusal_beceriler"] = {"Sosyal-Duygusal Beceriler": sdb_lines[:10]}
            else:
                plan_data["sosyal_duygusal_beceriler"] = {}

        if degerler_section:
            clean_content = self._clean_markdown(degerler_section)
            clean_content = re.sub(r'^5\.\s*DEĞER[^\n]*\n', '', clean_content, 1)
            d_lines = []
            seen_codes = set()  # Track unique codes to prevent duplicates
            for line in clean_content.split('\n'):
                line = line.strip()
                if line and re.match(r'D[0-9]', line):
                    # Extract code to check for duplicates
                    code_match = re.match(r'^(D[0-9]+)', line)
                    if code_match:
                        code = code_match.group(1)
                        if code not in seen_codes:
                            seen_codes.add(code)
                            # Keep full line without truncation
                            d_lines.append(line)
            # Only add if we found actual items
            if d_lines:
                plan_data["degerler"] = {"Değerler": d_lines[:10]}
            else:
                plan_data["degerler"] = {}

        if okuryazar_section:
            clean_content = self._clean_markdown(okuryazar_section)
            clean_content = re.sub(r'^6\.\s*OKURYAZAR[^\n]*\n', '', clean_content, 1)
            ob_lines = []
            for line in clean_content.split('\n'):
                line = line.strip()
                if line and re.match(r'OB[0-9]', line):
                    # Keep full line without truncation
                    ob_lines.append(line)
            # Only add if we found actual items
            if ob_lines:
                plan_data["okuryazarlik_becerileri"] = {"Okuryazarlık Becerileri": ob_lines[:10]}
            else:
                plan_data["okuryazarlik_becerileri"] = {}

        if ogrenme_ciktilari_section:
            # Remove section header before cleaning
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*7\.\s*ÖĞRENME\s*ÇIKT[^\n]*\n', '', ogrenme_ciktilari_section, 1)
            clean_content = self._clean_markdown(clean_content)
            lines = []
            for line in clean_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('7.'):
                    # Keep full line without truncation
                    lines.append(line)
            plan_data["ogrenme_ciktilari"] = {"Öğrenme Çıktıları": lines[:15] if lines else []}

        # Extract other sections
        anahtar_kavramlar = extract_section(r'\#{1,3}\s*\*{0,2}\s*8\.\s*ANAHTAR\s*KAVRAM', response_text)
        if anahtar_kavramlar:
            # Remove the section header completely
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*8\.\s*ANAHTAR\s*KAVRAM[^\n]*\n', '', anahtar_kavramlar, 1)
            clean_content = self._clean_markdown(clean_content)
            plan_data["anahtar_kavramlar"] = self._parse_anahtar_kavramlar(clean_content)

        degerlendirme = extract_section(r'\#{1,3}\s*\*{0,2}\s*9\.\s*ÖĞRENME\s*KANIT', response_text)
        if degerlendirme:
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*9\.\s*ÖĞRENME\s*KANIT[^\n]*\n', '', degerlendirme, 1)
            plan_data["degerlendirme"] = self._parse_degerlendirme(clean_content)

        ogrenme_ogretme = extract_section(r'\#{1,3}\s*\*{0,2}\s*10\.\s*ÖĞRENME[\-\s]*ÖĞRETME', response_text)
        if ogrenme_ogretme:
            # Remove the section header completely before cleaning markdown
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*10\.\s*ÖĞRENME[\-\s]*ÖĞRETME[^\n]*\n', '', ogrenme_ogretme, 1)
            # Preserve structure for long text sections
            clean_content = self._clean_markdown(clean_content, preserve_structure=True)
            plan_data["ogrenme_ogretme_yasantilari"] = clean_content.strip()

        farklilastirma = extract_section(r'\#{1,3}\s*\*{0,2}\s*11\.\s*FARKLILAŞTIRMA', response_text)
        if farklilastirma:
            # Remove the section header completely before cleaning markdown
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*11\.\s*FARKLILAŞTIRMA[^\n]*\n', '', farklilastirma, 1)
            # Preserve structure for long text sections
            clean_content = self._clean_markdown(clean_content, preserve_structure=True)
            plan_data["farklilastirma_zenginlestirme"] = clean_content.strip()

        destekleme = extract_section(r'\#{1,3}\s*\*{0,2}\s*12\.\s*DESTEKLE', response_text)
        if destekleme:
            # Remove the section header completely before cleaning markdown
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*12\.\s*DESTEKLE[^\n]*\n', '', destekleme, 1)
            # Preserve structure for long text sections
            clean_content = self._clean_markdown(clean_content, preserve_structure=True)
            plan_data["destekleme"] = clean_content.strip()

        aile_toplum = extract_section(r'\#{1,3}\s*\*{0,2}\s*13\.\s*AİLE', response_text)
        if aile_toplum:
            # Remove the section header completely before cleaning markdown
            clean_content = re.sub(r'^\#{1,3}\s*\*{0,2}\s*13\.\s*AİLE[^\n]*\n', '', aile_toplum, 1)
            # Preserve structure for long text sections
            clean_content = self._clean_markdown(clean_content, preserve_structure=True)
            plan_data["aile_toplum_katilimi"] = clean_content.strip()

        return plan_data

    def _clean_markdown(self, text: str, preserve_structure: bool = False) -> str:
        """Markdown formatlarını temizler"""
        import re
        # Bold text **text** -> text (kalın metni normal yap)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        # Italic text *text* -> text
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)
        # Headers ### -> boş
        text = re.sub(r'^\#{1,6}\s*', '', text, flags=re.MULTILINE)
        # Bullet points - keep them if preserving structure
        if not preserve_structure:
            text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
            text = re.sub(r'^\s*\•\s+', '', text, flags=re.MULTILINE)

        if preserve_structure:
            # For structured text, only collapse multiple spaces on same line
            # but preserve line breaks
            text = re.sub(r'[ \t]+', ' ', text)
            # Remove excessive blank lines (more than 2)
            text = re.sub(r'\n{3,}', '\n\n', text)
        else:
            # For simple text, collapse all whitespace
            text = re.sub(r'\s+', ' ', text)

        # Clean extra whitespace
        text = text.strip()
        return text

    def _parse_alan_becerileri_flexible(self, content: str) -> Dict[str, List[str]]:
        """Alan becerilerini daha esnek parse eder ve temizler"""
        import re
        result = {}

        # Clean all markdown first
        content = self._clean_markdown(content)

        # Look for area headers like "Türkçe Alanı" or similar
        areas = re.findall(r'([\wçğıöşüÇĞİÖŞÜ\s]+\s+Alanı):?', content, re.IGNORECASE)

        for area in areas:
            area_name = area.strip().replace(':', '')
            # Find content after this area until next area or end
            pattern = re.escape(area) + r'.*?(?=[\wçğıöşüÇĞİÖŞÜ\s]+\s+Alanı:|$)'
            area_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if area_match:
                area_content = area_match.group(0)
                # Extract only codes without duplicating descriptions
                lines = []
                code_pattern = r'([A-Z]+[0-9]*\.?[A-Z]*[0-9]*\.?[A-Z]*[0-9]*)'

                for line in area_content.split('\n'):
                    line = line.strip()
                    # Look for lines with codes
                    if re.match(code_pattern, line):
                        # Extract just the code part
                        code_match = re.match(r'^([A-Z]+[0-9]*(?:\.[A-Z]*[0-9]*)*)', line)
                        if code_match:
                            code = code_match.group(1)
                            # Get full description
                            rest = line[len(code):].strip()
                            if rest.startswith('.') or rest.startswith(':'):
                                rest = rest[1:].strip()
                            # Keep full description, don't truncate
                            if rest:
                                lines.append(f"{code}. {rest}")
                            else:
                                lines.append(code)

                if lines:
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_lines = []
                    for line in lines:
                        clean_line = line.strip()
                        if clean_line and clean_line not in seen:
                            seen.add(clean_line)
                            unique_lines.append(clean_line)
                    result[area_name] = unique_lines[:5]  # Limit to 5 items per area

        # If no areas found, try to parse as simple list
        if not result and content:
            lines = []
            code_pattern = r'^([A-Z]+[0-9]*(?:\.[A-Z]*[0-9]*)*)'
            for line in content.split('\n'):
                line = line.strip()
                if re.match(code_pattern, line):
                    lines.append(line.split()[0] if ' ' in line else line)
            if lines:
                result["Alan Becerileri"] = lines[:10]  # Limit total

        return result

    def _parse_alan_becerileri(self, content: str) -> Dict[str, List[str]]:
        """Alan becerilerini parse eder"""
        result = {}
        current_alan = None

        logger.info(f"Parsing alan becerileri, content length: {len(content)}")

        for line in content.split("\n"):
            if "###" in line:
                alan_name = line.replace("###", "").replace(":", "").strip()
                current_alan = alan_name
                result[current_alan] = []
                logger.debug(f"Found alan: {alan_name}")
            elif current_alan and line.strip():
                result[current_alan].append(line.strip())

        logger.info(f"Parsed alan becerileri result: {list(result.keys())}, total items: {sum(len(v) for v in result.values())}")
        return result

    def _parse_kavramsal_beceriler(self, content: str) -> Dict[str, List[str]]:
        """Kavramsal becerileri parse eder"""
        result = {}
        current_category = None

        for line in content.split("\n"):
            if "###" in line or line.startswith("KB"):
                category = line.replace("###", "").strip()
                current_category = category
                result[current_category] = []
            elif current_category and line.strip() and not line.startswith("#"):
                result[current_category].append(line.strip())

        return result

    def _parse_egilimler(self, content: str) -> Dict[str, List[str]]:
        """Eğilimleri parse eder"""
        result = {}
        current_category = None

        for line in content.split("\n"):
            if "###" in line or line.startswith("E"):
                category = line.replace("###", "").strip()
                current_category = category
                result[current_category] = []
            elif current_category and line.strip() and not line.startswith("#"):
                result[current_category].append(line.strip())

        return result

    def _parse_sosyal_duygusal(self, content: str) -> Dict[str, List[str]]:
        """Sosyal-duygusal becerileri parse eder"""
        result = {}
        current_skill = None

        for line in content.split("\n"):
            if "###" in line or line.startswith("SDB"):
                skill = line.replace("###", "").strip()
                current_skill = skill
                result[current_skill] = []
            elif current_skill and line.strip() and not line.startswith("#"):
                result[current_skill].append(line.strip())

        return result

    def _parse_degerler(self, content: str) -> Dict[str, List[str]]:
        """Değerleri parse eder"""
        result = {}
        current_value = None

        for line in content.split("\n"):
            if line.startswith("D") and "." in line:
                value = line.strip()
                current_value = value.split(".")[0] + "."
                result[current_value] = [value]
            elif current_value and line.strip() and not line.startswith("#"):
                result[current_value].append(line.strip())

        return result

    def _parse_okuryazarlik(self, content: str) -> Dict[str, List[str]]:
        """Okuryazarlık becerilerini parse eder"""
        result = {}
        current_skill = None

        for line in content.split("\n"):
            if "###" in line or line.startswith("OB"):
                skill = line.replace("###", "").strip()
                current_skill = skill
                result[current_skill] = []
            elif current_skill and line.strip() and not line.startswith("#"):
                result[current_skill].append(line.strip())

        return result

    def _parse_ogrenme_ciktilari(self, content: str) -> Dict[str, List[str]]:
        """Öğrenme çıktılarını parse eder"""
        result = {}
        current_alan = None

        for line in content.split("\n"):
            if any(alan in line.upper() for alan in ["TÜRKÇE", "MATEMATİK", "FEN", "SOSYAL", "HAREKET", "SANAT", "MÜZİK"]):
                current_alan = line.strip()
                result[current_alan] = []
            elif current_alan and line.strip():
                result[current_alan].append(line.strip())

        return result

    def _parse_anahtar_kavramlar(self, content: str) -> List[str]:
        """Anahtar kavramları parse eder"""
        kavramlar = []
        # First clean any markdown or special characters
        content = content.replace('*', '').replace('#', '').replace('[', '').replace(']', '')

        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                # Handle comma-separated values
                if "," in line:
                    items = [k.strip() for k in line.split(",") if k.strip()]
                    kavramlar.extend(items[:20])  # Limit number of items
                # Handle dash-separated values (but not list markers)
                elif "-" in line and not line.startswith("-"):
                    parts = line.split("-")
                    if len(parts) == 2 and len(parts[0]) < 20 and len(parts[1]) < 20:
                        # This looks like a concept pair (e.g., "Az-Çok")
                        kavramlar.append(line.strip())
                    else:
                        # Treat as separate items
                        kavramlar.extend([p.strip() for p in parts if p.strip()][:10])
                # Handle list markers
                elif line.startswith("-") or line.startswith("•"):
                    item = line.lstrip("-•").strip()
                    if item:
                        kavramlar.append(item)
                else:
                    # Single line item
                    kavramlar.append(line)

        # Remove duplicates while preserving order
        seen = set()
        unique_kavramlar = []
        for k in kavramlar[:30]:  # Limit total to 30 items
            if k not in seen and len(k) < 50:  # Skip very long items
                seen.add(k)
                unique_kavramlar.append(k)

        return unique_kavramlar

    def _parse_degerlendirme(self, content: str) -> Dict[str, str]:
        """Değerlendirme kriterlerini parse eder"""
        result = {}

        # Clean markdown first
        content = self._clean_markdown(content)

        # Look for standard evaluation sections
        sections = [
            ("Çocuklar Yönünden Değerlendirme", r"[Çç]ocuk.*[Yy]önünden.*[Dd]eğerlendirme"),
            ("Program Yönünden Değerlendirme", r"[Pp]rogram.*[Yy]önünden.*[Dd]eğerlendirme"),
            ("Öğretmen Yönünden Değerlendirme", r"[Öö]ğretmen.*[Yy]önünden.*[Dd]eğerlendirme")
        ]

        import re
        for section_name, pattern in sections:
            match = re.search(pattern + r'(.*?)(?=' + '|'.join([s[1] for s in sections if s[0] != section_name]) + r'|$)',
                            content, re.DOTALL | re.IGNORECASE)
            if match:
                section_content = match.group(1).strip()
                # Clean up the content
                lines = []
                for line in section_content.split('\n'):
                    line = line.strip()
                    if line and not re.match(pattern, line, re.IGNORECASE):
                        lines.append(line)
                result[section_name] = '\n'.join(lines[:5])  # Limit to 5 lines per section

        # If no sections found, try simpler parsing
        if not result:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'Çocuk' in line and 'Değerlendirme' in line:
                    result["Çocuklar Yönünden Değerlendirme"] = '\n'.join(lines[i+1:i+4])
                elif 'Program' in line and 'Değerlendirme' in line:
                    result["Program Yönünden Değerlendirme"] = '\n'.join(lines[i+1:i+4])
                elif 'Öğretmen' in line and 'Değerlendirme' in line:
                    result["Öğretmen Yönünden Değerlendirme"] = '\n'.join(lines[i+1:i+4])

        return result