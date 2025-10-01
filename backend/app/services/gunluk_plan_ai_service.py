# -*- coding: utf-8 -*-
import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.etkinlik import Etkinlik
from app.models.kazanim import Kazanim
from app.services.vertex_ai_service import vertex_ai_service as ai_service
import json

logger = logging.getLogger(__name__)

class GunlukPlanAIService:
    """Service for generating daily plan content using AI"""

    async def generate_plan_content(
        self,
        db: AsyncSession,
        activity_ids: List[int],
        yas_grubu: str,
        plan_adi: str
    ) -> Dict[str, Any]:
        """
        Generate complete daily plan content using AI based on selected activities
        """
        try:
            print(f"=== AI SERVICE: generate_plan_content called ===")
            print(f"Activity IDs: {activity_ids}")
            print(f"Age group: {yas_grubu}, Plan name: {plan_adi}")
            logger.info(f"=== AI SERVICE: generate_plan_content called ===")
            logger.info(f"Activity IDs: {activity_ids}")
            logger.info(f"Age group: {yas_grubu}, Plan name: {plan_adi}")
            # Fetch all selected activities
            query = select(Etkinlik).where(Etkinlik.id.in_(activity_ids))
            result = await db.execute(query)
            activities = result.scalars().all()

            if not activities:
                logger.warning(f"No activities found for IDs: {activity_ids}")
                return {}

            # Collect all information from activities
            activities_data = []
            all_materials = []

            # Aggregate curriculum data from all selected activities
            aggregated_alan_becerileri = {}
            aggregated_ogrenme_ciktilari = {}
            aggregated_kavramsal = []
            aggregated_egilimler = []
            aggregated_sosyal = []
            aggregated_degerler = []
            aggregated_okuryazarlik = []

            for activity in activities:

                activity_info = {
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
                    'kazanim_idleri': activity.kazanim_idleri,
                    'kazanim_metinleri': activity.kazanim_metinleri
                }
                activities_data.append(activity_info)

                if activity.materyaller:
                    all_materials.append(activity.materyaller)

                # Use saved curriculum data from activity if available
                if activity.curriculum_data:
                    logger.info(f"Using saved curriculum data for activity: {activity.etkinlik_adi}")

                    # Merge alan becerileri
                    if activity.alan_becerileri:
                        for alan, beceriler in activity.alan_becerileri.items():
                            if alan not in aggregated_alan_becerileri:
                                aggregated_alan_becerileri[alan] = []
                            for beceri in beceriler:
                                if beceri not in aggregated_alan_becerileri[alan]:
                                    aggregated_alan_becerileri[alan].append(beceri)

                    # Merge öğrenme çıktıları
                    if activity.ogrenme_ciktilari:
                        for alan, ciktilar in activity.ogrenme_ciktilari.items():
                            if alan not in aggregated_ogrenme_ciktilari:
                                aggregated_ogrenme_ciktilari[alan] = []
                            for cikti in ciktilar:
                                if cikti not in aggregated_ogrenme_ciktilari[alan]:
                                    aggregated_ogrenme_ciktilari[alan].append(cikti)

                    # Merge kavramsal beceriler
                    if activity.kavramsal_beceriler:
                        for beceri in activity.kavramsal_beceriler:
                            if beceri not in aggregated_kavramsal:
                                aggregated_kavramsal.append(beceri)

                    # Merge eğilimler
                    if activity.egilimler:
                        for egilim in activity.egilimler:
                            if egilim not in aggregated_egilimler:
                                aggregated_egilimler.append(egilim)

                    # Merge sosyal-duygusal
                    if activity.sosyal_duygusal:
                        for sd in activity.sosyal_duygusal:
                            if sd not in aggregated_sosyal:
                                aggregated_sosyal.append(sd)

                    # Merge değerler
                    if activity.degerler:
                        for deger in activity.degerler:
                            if deger not in aggregated_degerler:
                                aggregated_degerler.append(deger)

                    # Merge okuryazarlık
                    if activity.okuryazarlik:
                        for ok in activity.okuryazarlik:
                            if ok not in aggregated_okuryazarlik:
                                aggregated_okuryazarlik.append(ok)

                # Fallback to extracting from kazanims if no saved curriculum data
                elif activity.kazanim_idleri:
                    logger.info(f"No saved curriculum data for {activity.etkinlik_adi}, extracting from kazanims")
                    kazanim_query = select(Kazanim).where(
                        Kazanim.id.in_(activity.kazanim_idleri)
                    )
                    kazanim_result = await db.execute(kazanim_query)
                    kazanims = kazanim_result.scalars().all()

                    for kazanim in kazanims:
                        # ONLY include kazanims that match the selected activities' areas
                        # Check if kazanim's subject (ders) matches any selected activity area
                        kazanim_area = kazanim.ders  # This might be 'MATEMATİK', 'TÜRKÇE', etc.

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

                        # Process Alan Becerileri
                        if kazanim.alan_becerileri:
                            if kazanim.ders not in aggregated_alan_becerileri:
                                aggregated_alan_becerileri[kazanim.ders] = []
                            if kazanim.alan_becerileri not in aggregated_alan_becerileri[kazanim.ders]:
                                aggregated_alan_becerileri[kazanim.ders].append(kazanim.alan_becerileri)

                        # Process Öğrenme Çıktıları with proper codes
                        if kazanim.ogrenme_ciktilari:
                            # Add the main learning outcome
                            if kazanim.ders not in aggregated_ogrenme_ciktilari:
                                aggregated_ogrenme_ciktilari[kazanim.ders] = []
                            if kazanim.ogrenme_ciktilari not in aggregated_ogrenme_ciktilari[kazanim.ders]:
                                aggregated_ogrenme_ciktilari[kazanim.ders].append(kazanim.ogrenme_ciktilari)

                            # Add sub-learning outcomes if available
                            if kazanim.alt_ogrenme_ciktilari:
                                if kazanim.surec_bilesenleri:
                                    surec_code = kazanim.surec_bilesenleri
                                    alan_key = self._get_alan_code(kazanim.ders)
                                    # Check if it already starts with area code (like TAB1.1.SB2)
                                    if surec_code.startswith(alan_key):
                                        # Remove the duplicate area code prefix
                                        surec_code = surec_code[len(alan_key):]
                                        if surec_code.startswith('.'):
                                            surec_code = surec_code[1:]

                                    formatted_alt = f"{surec_code}. {kazanim.alt_ogrenme_ciktilari}"
                                else:
                                    formatted_alt = kazanim.alt_ogrenme_ciktilari

                                if formatted_alt not in aggregated_ogrenme_ciktilari[kazanim.ders]:
                                    aggregated_ogrenme_ciktilari[kazanim.ders].append(formatted_alt)

                        # Process Bütünleşik Beceriler
                        if kazanim.butunlesik_beceriler:
                            beceri_parts = kazanim.butunlesik_beceriler.split(',')
                            for beceri in beceri_parts:
                                beceri = beceri.strip()
                                if beceri.startswith('KB') and beceri not in aggregated_kavramsal:
                                    aggregated_kavramsal.append(beceri)
                                elif beceri.startswith('E') and beceri not in aggregated_egilimler:
                                    aggregated_egilimler.append(beceri)
                                elif beceri.startswith('SDB') and beceri not in aggregated_sosyal:
                                    aggregated_sosyal.append(beceri)
                                elif beceri.startswith('D') and not beceri.startswith('DB') and beceri not in aggregated_degerler:
                                    aggregated_degerler.append(beceri)
                                elif beceri.startswith('OB') and beceri not in aggregated_okuryazarlik:
                                    aggregated_okuryazarlik.append(beceri)

            # Read template JSON
            import os
            template_path = os.path.join(os.path.dirname(__file__), 'gunluk_plan_template.json')
            logger.info(f"Attempting to load template from: {template_path}")
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template = f.read()
                logger.info("Successfully loaded template from file")
            except Exception as template_error:
                logger.error(f"Failed to load template: {str(template_error)}")
                # If template doesn't exist, use inline template
                template = """{
  "alan_becerileri": {},
  "kavramsal_beceriler": [],
  "egilimler": [],
  "programlar_arasi_bilesenler": {
    "sosyal_duygusal_ogrenme_becerileri": [],
    "degerler": [],
    "okuryazarlik_becerileri": []
  },
  "ogrenme_ciktilari_ve_surec_bilesenleri": {},
  "icerik_cercevesi": {
    "kavramlar": "",
    "sozcukler": "",
    "materyaller": "",
    "egitim_ogrenme_ortamlari": ""
  },
  "ogrenme_ogretme_yasantilari": {
    "gune_baslama_zamani": "",
    "ogrenme_merkezlerinde_oyun": "",
    "beslenme_toplanma_temizlik": "",
    "etkinlikler": ""
  },
  "degerlendirme": "",
  "farklilastirma": {
    "zenginlestirme": "",
    "destekleme": ""
  },
  "aile_toplum_katilimi": {
    "aile_katilimi": "",
    "toplum_katilimi": ""
  }
}"""

            # Create AI prompt with detailed curriculum structure
            total_duration = sum(act.get('sure', 0) for act in activities_data)

            # Check if single or multiple activities
            activity_count = len(activities_data)

            # Get selected activity areas for prompt
            selected_activity_areas = set()
            for activity in activities:
                if activity.alan_adi:
                    selected_activity_areas.add(activity.alan_adi)

            # Log selected areas for debugging
            logger.info(f"Selected activity areas for prompt: {selected_activity_areas}")

            if activity_count == 1:
                activity_format_instruction = """ETKİNLİKLER BÖLÜMÜ İÇİN ÖZEL TALİMAT:
- TEK ETKİNLİK olduğu için numara kullanma
- Direkt etkinlik başlığıyla başla: "(Alan Adı - Etkinlik Adı)" şeklinde, parantez içinde
- Etkinlik EN AZ 10-15 cümle uzunluğunda, DETAYLI ve ADIM ADIM açıklanmalı
- Öğretmenin ne yapacağı, çocukların ne yapacağı, kullanılacak materyaller net belirtilmeli
- Kazanım kodlarını parantez içinde belirt ama çok fazla kullanma"""

                # Example for single activity
                etkinlikler_example = """(Türkçe - Duyuların Keşif Sandığı ve Hikaye Seçimi): "Öğretmen, merak uyandırıcı bir 'keşif sandığı'nı ortaya çıkarır ve çocuklara içinde neler olabileceğini sorar. Çocuklar sırayla sandığa dokunarak, koklayarak veya sallayarak içindeki nesneleri tahmin etmeye çalışır, böylece duyusal keşif başlar. Her çocuk sandıktan bir nesne seçer ve nesnenin özelliklerini (yumuşak, sert, kokulu vb.) betimler. Ardından, öğretmen farklı hikaye kitapları veya resimli kartlar sunarak çocuklardan sandıktan çıkan nesnelerle ilgili bir hikaye seçmelerini veya kendi hikayelerini oluşturmalarını ister (TAB.TAB1.1.SB1. Seçim yapmak). Seçilen hikaye hep birlikte dinlenir veya izlenir (TAB8.1. Dinleyecekleri/izleyecekleri şiir, hikaye gibi materyalleri yönetebilme). Bu etkinlik, çocukların duyusal algılarını geliştirirken aynı zamanda dinleme ve seçim yapma becerilerini pekiştirir."""
            else:
                activity_format_instruction = f"""ETKİNLİKLER BÖLÜMÜ İÇİN ÖZEL TALİMAT:
- {activity_count} ETKİNLİK var, hepsini açık ve net yaz
- Her etkinlik AYRI PARAGRAF olmalı ve aralarında BOŞ SATIR bırak
- Her etkinliği şu formatta başlat: "(Alan Adı - Etkinlik Adı):" şeklinde, parantez içinde
- Her etkinlik EN AZ 10-15 cümle uzunluğunda, DETAYLI ve ADIM ADIM açıklanmalı
- Öğretmenin ne yapacağı, çocukların ne yapacağı, kullanılacak materyaller net belirtilmeli
- Kazanım kodlarını parantez içinde belirt ama çok fazla kullanma"""

                # Example for multiple activities
                etkinlikler_example = """(Matematik - Geometrik Şekiller ve Örüntü Oluşturma): Öğretmen çocuklara daire, kare, üçgen ve dikdörtgen şekillerini tanıtır. Her şeklin özelliklerini (köşe sayısı, kenar sayısı) birlikte incelerler. Çocuklar sınıftaki nesnelerden bu şekillere örnekler bulurlar. Ardından renkli geometrik şekil blokları kullanılarak basit örüntüler oluşturulur. Önce öğretmen kırmızı daire - mavi kare - kırmızı daire şeklinde bir örüntü başlatır ve çocuklardan devamını getirmeleri istenir. Çocuklar kendi örüntülerini oluşturur ve arkadaşlarıyla paylaşırlar. Etkinlik sonunda her çocuk oluşturduğu örüntüyü çizim kağıdına aktarır. Bu süreçte şekillerin özellikleri pekiştirilir ve mantıksal düşünme becerileri geliştirilir (MAB2.3. Geometrik şekilleri tanıma).

(Sanat - Doğal Materyallerle Kolaj Çalışması): Öğretmen çocuklarla birlikte bahçeden yaprak, dal, çiçek, taş gibi doğal materyaller toplar. Toplanan materyaller masaya yerleştirilir ve çocuklar bunları inceler, dokularını hisseder, renklerini karşılaştırır. Her çocuğa büyük bir karton verilir ve yapıştırıcı kullanarak kendi doğa kolajlarını oluşturmaları istenir. Çocuklar materyalleri istedikleri gibi düzenler, yapıştırır ve gerekirse pastel boyalarla tamamlarlar. Çalışma sırasında öğretmen çocuklarla doğadaki renkler, mevsimler ve doğanın güzellikleri hakkında sohbet eder. Her çocuk tamamladığı kolajını arkadaşlarına sunar ve hangi materyalleri neden seçtiğini açıklar. Eserler sınıfın sanat köşesinde sergilenir. Bu etkinlik yaratıcılığı, el-göz koordinasyonunu ve doğa sevgisini geliştirir (SNAB4. Özgün ürünler oluşturma)."""

            # Log aggregated curriculum data
            logger.info(f"Aggregated alan_becerileri: {aggregated_alan_becerileri}")
            logger.info(f"Aggregated kavramsal: {len(aggregated_kavramsal)} items")
            logger.info(f"Aggregated eğilimler: {len(aggregated_egilimler)} items")

            prompt = f"""
MEB MAARİF MODELİ OKUL ÖNCESİ GÜNLÜK PLANI OLUŞTUR

Plan Bilgileri:
- Plan Adı: {plan_adi}
- Yaş Grubu: {yas_grubu}
- Toplam Süre: {total_duration} dakika

Seçilen Etkinlikler:
{json.dumps([{'adi': act['etkinlik_adi'], 'alan': act['alan_adi'], 'sure': act['sure']} for act in activities_data], ensure_ascii=False, indent=2)}

ETKİNLİKLERDEN ÇIKARILAN MÜFREDAT BİLEŞENLERİ (BUNLARI AYNEN KULLAN):

Alan Becerileri:
{json.dumps(aggregated_alan_becerileri, ensure_ascii=False, indent=2)}

Öğrenme Çıktıları:
{json.dumps(aggregated_ogrenme_ciktilari, ensure_ascii=False, indent=2)}

Kavramsal Beceriler:
{json.dumps(aggregated_kavramsal, ensure_ascii=False)}

Eğilimler:
{json.dumps(aggregated_egilimler, ensure_ascii=False)}

Sosyal-Duygusal Beceriler:
{json.dumps(aggregated_sosyal, ensure_ascii=False)}

Değerler:
{json.dumps(aggregated_degerler, ensure_ascii=False)}

Okuryazarlık Becerileri:
{json.dumps(aggregated_okuryazarlik, ensure_ascii=False)}

ÇOK ÖNEMLİ:
1. YUKARIDAKİ MÜFREDAT BİLEŞENLERİNİ AYNEN KULLAN
2. Her bölümü DETAYLI ve UZUN yaz
3. SADECE SEÇİLEN ETKİNLİKLERİN ALANLARINI KULLAN

{activity_format_instruction}

JSON ŞABLONU (TÜM ALANLARI DOLDUR):
{{
  "alan_becerileri": {json.dumps(aggregated_alan_becerileri, ensure_ascii=False)},
  "kavramsal_beceriler": {json.dumps(aggregated_kavramsal if aggregated_kavramsal else [], ensure_ascii=False)},
  "egilimler": {json.dumps(aggregated_egilimler if aggregated_egilimler else [], ensure_ascii=False)},
  "programlar_arasi_bilesenler": {{
    "sosyal_duygusal_ogrenme_becerileri": {json.dumps(aggregated_sosyal if aggregated_sosyal else [], ensure_ascii=False)},
    "degerler": {json.dumps(aggregated_degerler if aggregated_degerler else [], ensure_ascii=False)},
    "okuryazarlik_becerileri": {json.dumps(aggregated_okuryazarlik if aggregated_okuryazarlik else [], ensure_ascii=False)}
  }},
  "ogrenme_ciktilari_ve_surec_bilesenleri": {json.dumps(aggregated_ogrenme_ciktilari, ensure_ascii=False)},
  "icerik_cercevesi": {{
    "kavramlar": "İlişkili-İlişkisiz, Parça-Bütün, Büyük-Küçük, Az-Çok, İçinde-Dışında, Uzun-Kısa, Yakın-Uzak",
    "sozcukler": "Ressam, atölye, boya, fırça, tuval, sanat, eser, müze, sergi, yaratıcılık",
    "materyaller": "Pastel boyalar, sulu boyalar, A4 kağıtları, resim kağıtları, makas, yapıştırıcı, renkli kalemler, keçeli kalemler, pamuk, yapıştırıcı, sim, pul, doğal materyaller (yaprak, dal, taş), geri dönüşüm materyalleri, oyun hamuru, boya önlükleri",
    "egitim_ogrenme_ortamlari": "Sınıf, Sanat merkezi, Bahçe, Oyun alanı"
  }},
  "ogrenme_ogretme_yasantilari": {{
    "gune_baslama_zamani": "Çocuklar sınıfa geldiklerinde öğretmen her birini kapıda güler yüzle karşılar ve ismiyle selamlar. Çocukların o gün nasıl hissettiklerini paylaşmaları için duygu panosu kullanılır. Herkes çember şeklinde oturur ve öğretmen günün etkinliklerini kısaca tanıtır. Çocukların merak duygularını uyandırmak için 'Bugün sizce hangi malzemeleri kullanarak resim yapacağız?' gibi sorular sorulur (E1.1.). Çocukların tahminleri dinlenir ve değer verilir (SDB2.1.SB1.). Günün şarkısı hep birlikte söylenir ve el hareketleriyle eşlik edilir. Yoklama alınırken her çocuk kendi ismini söyler ve arkadaşlarını sayarak kaç kişi oldukları belirlenir (MAB6).",
    "ogrenme_merkezlerinde_oyun": "Çocuklar ilgi ve tercihlerine göre öğrenme merkezlerine dağılırlar. Sanat merkezinde çeşitli boyama materyalleri ve kağıtlar hazır bulundurulur. Çocuklar istedikleri materyalleri seçerek özgün çalışmalar yaparlar (SNAB4). Matematik merkezinde parça-bütün yapbozları ve sayma materyalleri bulunur. Çocuklar yapbozları tamamlarken parçalar arasındaki ilişkileri keşfederler (MAB2). Dramatik oyun merkezinde ressam atölyesi kurulur. Çocuklar ressam rolüne girerek birbirlerinin portrelerini çizerler. Blok merkezinde çocuklar işbirliği yaparak büyük yapılar inşa ederler (SDB2.2.SB1). Öğretmen merkezleri dolaşarak çocukların çalışmalarını gözlemler, sorular sorar ve gerektiğinde rehberlik eder.",
    "beslenme_toplanma_temizlik": "Beslenme zamanı öncesinde çocuklar ellerini yıkarken temizliğin önemi hakkında konuşulur (D18). Sofralar birlikte hazırlanır ve herkes görev alır. Yemekler paylaşılırken 'teşekkür ederim', 'afiyet olsun' gibi nezaket sözcükleri kullanılır. Beslenme sonrası masalar temizlenir, çöpler ayrıştırılarak atılır. Çocuklar kendi alanlarını toplarken düzen ve temizlik alışkanlığı kazanırlar (D18.2.3). Dişler fırçalanır ve kişisel temizlik rutini tamamlanır. Dinlenme zamanında sakin müzik eşliğinde çocuklar uzanarak gevşeme egzersizleri yaparlar.",
    "etkinlikler": "{etkinlikler_example}"
  }},
  "degerlendirme": "• Bugün hangi materyalleri kullanarak resim yaptınız? En çok hangisini kullanmayı sevdiniz?\n• Parçaları birleştirirken nelere dikkat ettiniz? Hangi parçanın nereye ait olduğunu nasıl anladınız?\n• Arkadaşlarınızla birlikte çalışırken neler hissettiniz? İşbirliği yapmak işinizi kolaylaştırdı mı?\n• Ressam hikayesinde en çok hangi bölümü beğendiniz? Siz ressam olsaydınız ne çizerdiniz?\n• Heykel oyununda dengenizi korumak zor oldu mu? Hangi pozisyonda durmak daha kolaydı?\n• Bugün öğrendiğiniz yeni sözcükler nelerdi? Bu sözcükleri başka nerelerde kullanabilirsiniz?\n• Sanat eserlerinizi ailenize nasıl anlatacaksınız?",
  "farklilastirma": {{
    "zenginlestirme": "Web2 araçları kullanılarak sanal müze gezisi düzenlenir. Çocuklar farklı ülkelerden sanat eserlerini inceler. Dijital çizim uygulamalarıyla tablet üzerinde resim yapma deneyimi yaşarlar. İleri düzey çocuklar için karmaşık yapbozlar ve üç boyutlu modelleme çalışmaları sunulur. Sanat tarihi ile ilgili basit bilgiler verilerek farklı dönemlerin sanat anlayışları tanıtılır. Atık materyallerle heykel yapımı gibi yaratıcı projeler planlanır.",
    "destekleme": "Çember zamanı öncesinde bireysel olarak hazırlanması gereken çocuklarla özel ilgilenilir. Motor becerileri gelişmekte olan çocuklar için kalın fırçalar ve büyük kağıtlar kullanılır. Makas kullanımında zorlanan çocuklar için önceden kesilmiş şekiller hazırlanır. Görsel ipuçları ve model alma yöntemi kullanılarak çocukların katılımı desteklenir. Basit ve kısa yönergeler verilerek anlama kolaylaştırılır. Akran desteği sağlanarak işbirlikli öğrenme teşvik edilir."
  }},
  "aile_toplum_katilimi": {{
    "aile_katilimi": "Aile Katılımı: Ailelere etkinlikte yapılan çalışmalar hakkında bilgi verilir ve evde benzer sanat aktiviteleri yapmaları önerilir. Hafta sonu aileleriyle birlikte müze veya sergi gezisi yapmaları teşvik edilir. Evde bulunan atık materyallerle sanat çalışmaları yapılması için öneriler sunulur. Ailelerin çocuklarıyla birlikte resim yaparak bu çalışmaları okula göndermeleri istenir. Veliler sınıfa davet edilerek kendi meslekleri veya hobileri hakkında sunum yapmaları sağlanır.",
    "toplum_katilimi": "Toplum Katılımı: Yerel sanatçılar okula davet edilerek çocuklarla atölye çalışması yapmaları sağlanır. Mahalle kütüphanesine gidilerek sanat kitapları incelenir. Yakın çevredeki sanat galerileri veya müzeler ziyaret edilir. Belediyenin düzenlediği çocuk sanat etkinliklerine katılım sağlanır. Okulun sergi alanında çocukların eserlerinden oluşan bir sergi düzenlenerek mahalle halkı davet edilir. Huzurevine gidilerek yaşlılarla birlikte resim yapma etkinliği gerçekleştirilir."
  }}
}}

HATIRLATMALAR:
1. JSON ŞABLONUNDA VERİLEN DEĞERLERİ AYNEN KULLAN - Yeni değer ekleme, var olanları değiştirme
2. KAVRAMSAL BECERİLER, EĞİLİMLER, SOSYAL DUYGUSAL, DEĞERLER, OKURYAZARLIK: Şablonda verilenlerden başka ekleme yapma
3. ETKİNLİKLER BÖLÜMÜ ÇOK ÖNEMLİ: Her etkinlik EN AZ 10-15 cümle olmalı, detaylı ve adım adım açıklanmalı
4. Etkinlikler parantez içinde başlık formatında yazılmalı: (Alan Adı - Etkinlik Adı)
5. Kazanım kodlarını minimum kullan ve parantez içinde yaz
6. SADECE SEÇİLEN ETKİNLİKLERİN ALANLARINI KULLAN - Başka alan ekleme
7. Öğrenme-Öğretme Yaşantıları'nın her bölümü en az 5-6 cümle olmalı
8. ÖĞRENME ÇIKTILARI: Şablonda verilen formatta kullan
7. Değerlendirme en az 7-8 soru içermeli
8. İçerik çerçevesi alanlarını etkinliklere uygun doldur
9. Mutlaka geçerli JSON formatında yanıt ver, başka açıklama veya metin ekleme
            """

            # Call AI service
            logger.info(f"Calling Vertex AI with prompt length: {len(prompt)} characters")
            print(f"=== CALLING VERTEX AI ===")
            print(f"Prompt length: {len(prompt)} characters")

            try:
                # Use structured JSON output
                response = await ai_service.generate_content(prompt, use_json_output=True)
                logger.info(f"Received JSON response from Vertex AI: {len(response) if response else 0} characters")
                print(f"=== VERTEX AI JSON RESPONSE RECEIVED ===")
                print(f"Response length: {len(response) if response else 0} characters")

                # Log the actual response for debugging
                if response:
                    logger.info(f"AI Response preview (first 500 chars): {response[:500]}")
                    print(f"Response preview: {response[:500]}")
            except Exception as vertex_error:
                logger.error(f"Vertex AI call failed: {str(vertex_error)}")
                print(f"=== VERTEX AI CALL FAILED ===")
                print(f"Error: {str(vertex_error)}")
                response = None

            # Parse AI response
            if response:
                try:
                    # Clean potential markdown wrappers even with JSON output mode
                    cleaned_response = response.strip()
                    if cleaned_response.startswith('```json'):
                        cleaned_response = cleaned_response[7:]
                    elif cleaned_response.startswith('```'):
                        cleaned_response = cleaned_response[3:]
                    if cleaned_response.endswith('```'):
                        cleaned_response = cleaned_response[:-3]
                    cleaned_response = cleaned_response.strip()

                    # Remove invalid control characters that break JSON parsing
                    import re
                    # Replace actual newlines, tabs, and other control characters within strings
                    # This regex finds strings and replaces control chars inside them
                    def clean_json_string(match):
                        string_content = match.group(1)
                        # Replace control characters with escaped versions
                        string_content = string_content.replace('\n', '\\n')
                        string_content = string_content.replace('\r', '\\r')
                        string_content = string_content.replace('\t', '\\t')
                        # Remove other control characters
                        string_content = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', string_content)
                        return f'"{string_content}"'

                    # Apply cleaning to all JSON strings
                    cleaned_response = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', clean_json_string, cleaned_response)

                    # Since we're using JSON output mode, response should be valid JSON
                    ai_content = json.loads(cleaned_response)
                    logger.info(f"Successfully parsed JSON response with keys: {list(ai_content.keys())}")
                    print(f"=== AI CONTENT PARSED SUCCESSFULLY ===")
                    print(f"Keys in response: {list(ai_content.keys())}")
                except json.JSONDecodeError as json_error:
                    logger.error(f"Failed to parse JSON response: {str(json_error)}")
                    logger.error(f"JSON Error at position {json_error.pos if hasattr(json_error, 'pos') else 'unknown'}: {json_error.msg}")
                    logger.info("Response should be valid JSON when using JSON output mode")
                    print(f"=== UNEXPECTED: JSON PARSE FAILED WITH JSON OUTPUT MODE ===")
                    print(f"Error: {str(json_error)}")
                    print(f"Response preview (first 500 chars): {response[:500] if response else 'None'}")

                    # Fallback to default content
                    ai_content = self._get_default_content()
                    logger.info(f"Using default content with keys: {list(ai_content.keys())}")
            else:
                logger.warning("No response from AI, using default content")
                print(f"=== NO AI RESPONSE, USING DEFAULT ===")
                ai_content = self._get_default_content()

            # Merge with existing materials
            if all_materials:
                materials_text = '\n'.join(all_materials)
                if 'materyaller' not in ai_content or not ai_content['materyaller']:
                    ai_content['materyaller'] = materials_text
                else:
                    ai_content['materyaller'] = f"{ai_content['materyaller']}\n{materials_text}"

            # Ensure all required fields are present
            ai_content = self._ensure_complete_structure(ai_content)
            return ai_content

        except Exception as e:
            logger.error(f"Error generating AI content for daily plan: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return self._get_default_content()

    def _ensure_complete_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the content has all required fields with proper structure"""
        default = self._get_default_content()

        # Merge with default to ensure all fields exist
        result = {
            'alan_becerileri': content.get('alan_becerileri', default['alan_becerileri']),
            'kavramsal_beceriler': content.get('kavramsal_beceriler', default['kavramsal_beceriler']),
            'egilimler': content.get('egilimler', default['egilimler']),
            'programlar_arasi_bilesenler': content.get('programlar_arasi_bilesenler', default['programlar_arasi_bilesenler']),
            'ogrenme_ciktilari_ve_surec_bilesenleri': content.get('ogrenme_ciktilari_ve_surec_bilesenleri', default['ogrenme_ciktilari_ve_surec_bilesenleri']),
            'icerik_cercevesi': content.get('icerik_cercevesi', default['icerik_cercevesi']),
            'ogrenme_ogretme_yasantilari': content.get('ogrenme_ogretme_yasantilari', default['ogrenme_ogretme_yasantilari']),
            'degerlendirme': content.get('degerlendirme', default['degerlendirme']),
            'farklilastirma': content.get('farklilastirma', default['farklilastirma']),
            'aile_toplum_katilimi': content.get('aile_toplum_katilimi', default['aile_toplum_katilimi'])
        }

        # Also include any fields that might be at root level
        for key in ['kavramlar', 'sozcukler', 'materyaller', 'egitim_ortamlari',
                    'gune_baslama', 'ogrenme_merkezleri', 'beslenme_toplanma',
                    'etkinlikler', 'zenginlestirme', 'destekleme',
                    'aile_katilimi', 'toplum_katilimi', 'notlar']:
            if key in content:
                result[key] = content[key]

        return result

    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response if not in JSON format"""
        content = {}

        # Try to extract sections from text
        sections = {
            'KAVRAMLAR': 'kavramlar',
            'SÖZCÜKLER': 'sozcukler',
            'EĞİTİM ORTAMLARI': 'egitim_ortamlari',
            'GÜNE BAŞLAMA': 'gune_baslama',
            'ÖĞRENME MERKEZLERİ': 'ogrenme_merkezleri',
            'BESLENME': 'beslenme_toplanma',
            'DEĞERLENDİRME': 'degerlendirme',
            'ZENGİNLEŞTİRME': 'zenginlestirme',
            'DESTEKLEME': 'destekleme',
            'AİLE KATILIMI': 'aile_katilimi',
            'TOPLUM KATILIMI': 'toplum_katilimi'
        }

        for marker, field in sections.items():
            if marker in response:
                start_idx = response.find(marker)
                end_idx = len(response)

                # Find next section
                for next_marker in sections.keys():
                    if next_marker != marker:
                        next_idx = response.find(next_marker, start_idx + len(marker))
                        if next_idx > 0 and next_idx < end_idx:
                            end_idx = next_idx

                # Extract content
                section_content = response[start_idx + len(marker):end_idx].strip()
                section_content = section_content.strip(':').strip()
                content[field] = section_content

        return content

    def _extract_partial_content(self, response: str) -> Dict[str, Any]:
        """Try to extract as much content as possible from a partial/broken JSON response"""
        try:
            content = {}

            # Try to fix common JSON issues
            # Add missing closing brackets/braces at the end
            open_braces = response.count('{') - response.count('}')
            open_brackets = response.count('[') - response.count(']')

            fixed_response = response
            fixed_response += ']' * open_brackets
            fixed_response += '}' * open_braces

            # Try to parse the fixed response
            try:
                content = json.loads(fixed_response)
                logger.info("Successfully extracted partial content after fixing brackets")
                return content
            except:
                pass

            # If that fails, try to extract specific sections using regex
            import re

            # Extract kavramsal_beceriler if present
            kavramsal_match = re.search(r'"kavramsal_beceriler"\s*:\s*\[(.*?)\]', response, re.DOTALL)
            if kavramsal_match:
                try:
                    content['kavramsal_beceriler'] = json.loads('[' + kavramsal_match.group(1) + ']')
                except:
                    content['kavramsal_beceriler'] = []

            # Extract egilimler if present
            egilimler_match = re.search(r'"egilimler"\s*:\s*\[(.*?)\]', response, re.DOTALL)
            if egilimler_match:
                try:
                    content['egilimler'] = json.loads('[' + egilimler_match.group(1) + ']')
                except:
                    content['egilimler'] = []

            # Extract alan_becerileri if present
            alan_match = re.search(r'"alan_becerileri"\s*:\s*\{(.*?)\}', response, re.DOTALL)
            if alan_match:
                try:
                    content['alan_becerileri'] = json.loads('{' + alan_match.group(1) + '}')
                except:
                    content['alan_becerileri'] = {}

            # Extract programlar_arasi_bilesenler if present
            prog_match = re.search(r'"programlar_arasi_bilesenler"\s*:\s*\{(.*?)\}', response, re.DOTALL)
            if prog_match:
                try:
                    content['programlar_arasi_bilesenler'] = json.loads('{' + prog_match.group(1) + '}')
                except:
                    content['programlar_arasi_bilesenler'] = {}

            if content:
                logger.info(f"Extracted partial content with fields: {list(content.keys())}")
                # Fill in missing fields with defaults
                default = self._get_default_content()
                for key in default:
                    if key not in content:
                        content[key] = default[key]
                return content

        except Exception as e:
            logger.error(f"Failed to extract partial content: {str(e)}")

        return {}

    def _get_default_content(self) -> Dict[str, Any]:
        """Return minimal default content when AI fails"""
        logger.warning("Using minimal default content due to AI failure")
        return {
            'alan_becerileri': {
                'Matematik Alanı': ['MAB1. Matematiksel Muhakeme'],
                'Türkçe Alanı': ['TAB1. Dinleme', 'TAB2. Konuşma']
            },
            'kavramsal_beceriler': [
                'KB1.Temel Beceriler',
                'KB1.5.Bulmak',
                'KB1.6.Seçmek'
            ],
            'egilimler': [
                'E.1. Benlik Eğilimleri',
                'E1.1. Merak',
                'E.3. Entelektüel Eğilimler'
            ],
            'programlar_arasi_bilesenler': {
                'sosyal_duygusal_ogrenme_becerileri': [
                    'SDB2.1. İletişim Becerisi',
                    'SDB2.1.SB1. Başkalarını etkin şekilde dinlemek'
                ],
                'degerler': [
                    'D18. Temizlik',
                    'D18.2.Yaşadığı ortamın temizliğine dikkat etmek'
                ],
                'okuryazarlik_becerileri': [
                    'OB4. Görsel Okuryazarlık Becerileri',
                    'OB4.1. Görseli Anlama'
                ]
            },
            'sosyal_duygusal_beceriler': [],
            'degerler': [],
            'okuryazarlik_becerileri': [],
            'ogrenme_ciktilari_ve_surec_bilesenleri': {},
            'icerik_cercevesi': {
                'kavramlar': '',
                'sozcukler': '',
                'materyaller': '',
                'egitim_ogrenme_ortamlari': ''
            },
            'ogrenme_ogretme_yasantilari': {
                'gune_baslama_zamani': 'AI tarafından detaylı içerik oluşturulamadı',
                'ogrenme_merkezlerinde_oyun': 'AI tarafından detaylı içerik oluşturulamadı',
                'beslenme_toplanma_temizlik': 'AI tarafından detaylı içerik oluşturulamadı',
                'etkinlikler': 'AI tarafından detaylı içerik oluşturulamadı'
            },
            'degerlendirme': 'AI tarafından değerlendirme soruları oluşturulamadı',
            'farklilastirma': {
                'zenginlestirme': 'AI tarafından zenginleştirme önerileri oluşturulamadı',
                'destekleme': 'AI tarafından destekleme önerileri oluşturulamadı'
            },
            'aile_toplum_katilimi': {
                'aile_katilimi': 'AI tarafından aile katılımı önerileri oluşturulamadı',
                'toplum_katilimi': 'AI tarafından toplum katılımı önerileri oluşturulamadı'
            }
        }

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

# Singleton instance
gunluk_plan_ai_service = GunlukPlanAIService()