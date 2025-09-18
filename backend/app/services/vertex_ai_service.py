import os
import json
import asyncio
import threading
from typing import List, Dict, Optional
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Thread-local storage for model instances
_thread_local = threading.local()

class VertexAIService:
    """Service for generating activities using Google Vertex AI"""

    # Class-level cache for credentials to avoid re-loading
    _credentials = None
    _credentials_lock = threading.Lock()

    def __init__(self):
        self._initialize_vertex_ai()
        
    @classmethod
    def _get_credentials(cls):
        """Get or create cached credentials (thread-safe)"""
        if cls._credentials is None:
            with cls._credentials_lock:
                if cls._credentials is None:  # Double-check pattern
                    credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
                    if not credentials_path:
                        credentials_path = "../credentials/google-service-account.json"

                    if not os.path.isabs(credentials_path):
                        credentials_path = os.path.abspath(credentials_path)

                    cls._credentials = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=["https://www.googleapis.com/auth/cloud-platform"]
                    )
        return cls._credentials

    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with service account credentials"""
        try:
            # Get cached credentials
            credentials = self._get_credentials()

            # Initialize Vertex AI
            vertexai.init(
                project=settings.VERTEX_AI_PROJECT_ID,
                location=settings.VERTEX_AI_LOCATION,
                credentials=credentials
            )

            # Model will be initialized on-demand in _get_model()

            logger.info("Vertex AI initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise

    def _get_model(self, use_json_output=False):
        """Get thread-local model instance for concurrent requests

        Args:
            use_json_output: If True, configure model for structured JSON output
        """
        model_key = 'json_model' if use_json_output else 'model'

        if not hasattr(_thread_local, model_key):
            if use_json_output:
                # Create model with JSON output configuration
                setattr(_thread_local, model_key, GenerativeModel(
                    model_name=settings.VERTEX_AI_MODEL,
                    generation_config=GenerationConfig(
                        temperature=0.7,
                        top_p=0.9,
                        max_output_tokens=32768,
                        response_mime_type="application/json",
                    )
                ))
            else:
                # Standard model for text generation
                setattr(_thread_local, model_key, GenerativeModel(
                    model_name=settings.VERTEX_AI_MODEL,
                    generation_config=GenerationConfig(
                        temperature=0.7,
                        top_p=0.9,
                        max_output_tokens=32768,
                    )
                ))
        return getattr(_thread_local, model_key)
    
    def create_activity_prompt(self, kazanimlar: List[Dict], custom_prompt: Optional[str] = None) -> str:
        """Create a detailed prompt for activity generation"""

        # Detaylı kazanım listesi oluştur
        kazanim_listesi = []
        for k in kazanimlar:
            kazanim_text = f"- Yaş: {k.get('yas_grubu', '')}\n"
            kazanim_text += f"  Ders: {k.get('ders', '')}\n"
            if k.get('alan_becerileri'):
                kazanim_text += f"  Alan Becerileri: {k.get('alan_becerileri')}\n"
            if k.get('butunlesik_beceriler'):
                kazanim_text += f"  Bütünleşik Beceriler: {k.get('butunlesik_beceriler')}\n"
            if k.get('surec_bilesenleri'):
                kazanim_text += f"  Süreç Bileşenleri: {k.get('surec_bilesenleri')}\n"
            kazanim_text += f"  Öğrenme Çıktıları: {k.get('ogrenme_ciktilari', '')}\n"
            if k.get('alt_ogrenme_ciktilari'):
                kazanim_text += f"  Alt Öğrenme Çıktıları: {k.get('alt_ogrenme_ciktilari')}\n"
            kazanim_listesi.append(kazanim_text)

        kazanimlar_str = "\n".join(kazanim_listesi)

        # Add custom instructions if provided (müfredat seçimleri dahil)
        custom_instructions = ""
        duration = 30  # Default duration

        if custom_prompt:
            # Extract duration if specified in custom prompt
            import re
            duration_match = re.search(r'(\d+)\s*dakika', custom_prompt)
            if duration_match:
                duration = int(duration_match.group(1))

            custom_instructions = f"\n\nÖZEL TALİMATLAR VE MÜFREDAT SEÇİMLERİ:\n{custom_prompt}\n\nBu özel talimatları ve müfredat bileşenlerini etkinlik planına dahil et. Seçilen değerler, eğilimler, beceriler ve bileşenleri etkinlik içinde kullan.\n"
        
        prompt = f"""
        Sen deneyimli bir okul öncesi öğretmenisin. 15 yıllık tecrüben var ve çocuk gelişimi ile erken çocukluk eğitimi alanında uzmansın.
        Maarif Modeli'ne hakim, gelişimsel uygunluk ilkelerini bilen, çocuk merkezli ve oyun temelli öğrenme yaklaşımını benimseyen bir eğitimcisin.

        GÖREV: Aşağıdaki kazanımlar ve müfredat bileşenleri için pedagojik olarak doğru, gelişime uygun, yaratıcı bir etkinlik planı hazırla.

        PEDAGOJİK İLKELERİN:
        1. **Gelişimsel Uygunluk**: Her yaş grubunun fiziksel, bilişsel, sosyal-duygusal gelişim özelliklerini dikkate al
        2. **Bütünsel Yaklaşım**: Tek bir gelişim alanına değil, tüm gelişim alanlarına hitap et
        3. **Oyun Temelli Öğrenme**: Çocukların en iyi oyun yoluyla öğrendiğini unutma
        4. **Aktif Katılım**: Çocukları pasif dinleyici değil, aktif katılımcı yap
        5. **Bireysel Farklılıklar**: Her çocuğun farklı öğrenme hızı ve stili olduğunu göz önünde bulundur
        6. **Somuttan Soyuta**: Önce yaşantı ve deneyim, sonra kavram öğretimi
        7. **Yakından Uzağa**: Çocuğun kendi dünyasından başla, genişlet
        8. **21. Yüzyıl Becerileri**: Yaratıcılık, eleştirel düşünme, işbirliği, iletişim becerilerini geliştir

        ETKİNLİK TASARIM KRİTERLERİN:
        • Çocukların merak ve ilgisini uyandıracak gizemli/sürprizli bir başlangıç
        • Tüm duyuların aktif kullanımı (görme, işitme, dokunma, hareket)
        • Küçük grup, büyük grup ve bireysel çalışma dengesi
        • Öğrenme merkezleri arası geçişler ve bütünleşik etkinlikler
        • Çocukların seçim yapabildiği, karar verebildiği anlar
        • Süreç odaklı (ürün değil süreç önemli)
        • Hata yapmanın öğrenmenin parçası olduğu güvenli ortam
        • Akran öğrenmesi fırsatları

        YARATICILIK VE ÖZGÜNLÜK:
        • Sıradan materyalleri yaratıcı şekilde kullan
        • Çocukların hayal gücünü harekete geçir
        • Açık uçlu sorular ve keşif fırsatları sun
        • Problem çözme durumları yarat
        • Farklı sanat teknikleri ve ifade biçimlerini birleştir

        KAZANIMLAR (Detaylı):
        {kazanimlar_str}{custom_instructions}

        ÖNEMLİ HATIRLATMALAR:
        - ETKİNLİK SÜRESİ TAM OLARAK {duration} DAKİKA OLMALIDIR! Bölümlerin toplamı bu süreye uygun olmalı.
        - TÜM ADIMLARI GENİŞ ZAMAN KİPİNDE YAZ (yapılır, edilir, sorulur, dinlenir vb.)
        - Emir kipi kullanma (yapın, edin, sorun yerine yapılır, edilir, sorulur kullan)
        - Her etkinlik aşaması için çocukların ne yapacağını, öğretmenin nasıl yönlendireceğini net olarak belirt
        - Geçiş anlarını (transition) dikkatli planla - çocuklar bir aktiviteden diğerine nasıl geçecek?
        - Yansıma çemberinde çocukların metacognitive (üst biliş) becerilerini geliştir
        - Uyarlama önerilerinde kapsayıcı eğitim ilkelerini göz önünde bulundur
        - Değerlendirme bölümünü MUTLAKA DOLDUR - boş bırakma
        - ASLA PARANTEZ İÇİNDE KAZANIM KODU YAZMA! Kodlar veritabanında saklanacak ama metinde görünmeyecek

        ÇOK ÖNEMLİ - ETKİNLİK ÇEŞİTLİLİĞİ:
        - HER ETKİNLİK FARKLI BİR TEMADA OLMALI (duyular değil, kazanımlara özgü temalar)
        - Seçilen kazanımların GERÇEKTEKİ İÇERİĞİNE UYGUN etkinlikler tasarla
        - Matematik için: sayılar, şekiller, örüntüler, ölçme, grafik vb.
        - Türkçe için: hikaye, şiir, drama, konuşma, dinleme vb.
        - Fen için: deneyler, gözlem, doğa, canlılar, mevsimler vb.
        - Sanat için: resim, heykel, kolaj, baskı, üç boyutlu çalışmalar vb.
        - Her etkinlik kendine özgü materyaller ve yöntemler içermeli
        - DUYU ETKİNLİĞİ YAPMA, kazanıma özgü içerik üret

        ÇIKTI FORMATI: Aşağıdaki JSON formatında döndür (SADECE JSON, başka açıklama ekleme):

        {{
          "etkinlik_adi": "Kazanıma uygun, özgün ve içeriği yansıtan bir isim",
          "alan_adi": "Ana gelişim alanı (Fen ve Ekoloji/Matematik/Türkçe/Sanat/Müzik/Hareket ve Sağlık/Sosyal)",
          "yas_grubu": "Gelişimsel özelliklere uygun yaş aralığı (36-48 ay/48-60 ay/60-72 ay)",
          "sure": {duration},
          "uygulama_yeri": "En uygun öğrenme ortamı (Sınıf içi/Bahçe/Spor salonu/Sanat atölyesi)",
          "amaclar": [
            "Çocukların etkinlik konusundaki temel kavramları öğrenmesi ve anlaması",
            "Çevresindeki nesneleri ve olayları gözlem yoluyla tanıması ve ayırt etmesi",
            "Problem çözme ve eleştirel düşünme becerilerini geliştirmesi",
            "Yaratıcılık ve hayal gücünü kullanarak kendini ifade etmesi",
            "Akranlarıyla işbirliği yaparak sosyal becerilerini güçlendirmesi"
          ],
          "materyaller": [
            "Kazanımlara ve etkinlik içeriğine uygun materyaller listesi",
            "Ana materyaller detaylı olarak belirtilir",
            "Alternatif materyaller parantez içinde verilir",
            "Kolay bulunabilir, güvenli ve yaş grubuna uygun malzemeler",
            "Doğal, geri dönüşüm ve açık uçlu materyaller tercih edilir",
            "Her çocuk için yeterli sayıda materyal planlanır"
          ],
          "uygulama_sureci": {{
            "giris": {{
              "sure": "{round(duration * 0.2)}-{round(duration * 0.25)} dakika",
              "adimlar": [
                "Çocuklar rahat hissedecekleri şekilde organize edilir (yarım daire, U düzeni, minderler üzerinde)",
                "Dikkat çekici ve ilgi uyandıran bir başlangıç yapılır (örneğin: ilginç bir nesne, ses, görsel veya kukla kullanılır)",
                "Önceki öğrenmelerle bağlantı kurulur: 'Dün yaptığımız etkinliği hatırlayan var mı?'",
                "Merak uyandıran açık uçlu sorular sorulur: 'Sizce bu kutunun içinde ne olabilir?'",
                "Çocukların tahmin ve fikirleri dinlenir, her fikre değer verilir",
                "Parmak oyunu, şarkı veya hareket ile enerji yükseltilir ve odaklanma sağlanır"
              ]
            }},
            "gelisme": {{
              "sure": "{round(duration * 0.5)}-{round(duration * 0.6)} dakika",
              "aktiviteler": {{
                "kesfetme": "KEŞFETME (5 dk): Çocukların materyallerle serbest keşif yapması, dokunması, incelemesi. Öğretmen gözlemler, sorular sorar: 'Ne fark ediyorsun? Nasıl hissettiriyor?'",
                "deneyimleme": "DENEYİMLEME (5 dk): Rehberli aktivite - öğretmen model olur, çocuklar dener. Problem durumu sunulur, çocuklar çözüm üretir. 'Bunu başka nasıl yapabiliriz?'",
                "uygulama": "UYGULAMA (5 dk): Çocuklar öğrendiklerini kendi yaratıcılıklarıyla uygular. Bireysel, ikili veya küçük grup çalışması. Her çocuk kendi hızında ilerler.",
                "paylasma": "PAYLAŞMA (3 dk): Çocuklar yaptıklarını arkadaşlarıyla paylaşır. 'Kim göstermek ister? Arkadaşınızın çalışması hakkında ne düşünüyorsunuz?'",
                "genisletme": "GENİŞLETME (2 dk): Öğrenme merkezi bağlantıları, evde aileyle yapılabilecek aktiviteler, gelecek etkinliğe köprü kurma."
              }}
            }},
            "yansima_cemberi": {{
              "sure": "{round(duration * 0.15)}-{round(duration * 0.2)} dakika",
              "duzenleme": "Rahat bir oturma düzeni - çember, yarım ay veya minderler üzerinde",
              "sorular": [
                "Bugün hangi materyalleri kullandık? Neler yaptık?",
                "Bu etkinlikte kendinizi nasıl hissettiniz? En çok neyi yaparken mutlu oldunuz?",
                "En zor/kolay kısmı neydi? Neden? Başka nasıl yapabilirdik?",
                "Öğrendiklerimizi başka nerede kullanabiliriz? Evde/parkta benzer neler yapabiliriz?",
                "Bu etkinliği tekrar yapsak neyi farklı yapardınız?"
              ],
              "temizlik": "Materyalleri toplama oyunu - 'Kim en hızlı toplayacak? Renklere göre ayıralım!'"
            }},
            "sonuc": {{
              "sure": "{round(duration * 0.1)} dakika",
              "aktiviteler": [
                "Materyalleri toplama oyunu",
                "Teşekkür şarkısı veya alkış yağmuru"
              ]
            }}
          }},
          "uyarlama": {{
            "Görme Yetersizliği": "Dokunsal materyaller kullanma, ses ve koku ipuçları ekleme, açık ve net betimlemeler yapma, güvenli hareket alanı oluşturma, akran desteği sağlama",
            "İşitme Yetersizliği": "Görsel ipuçları ve işaret dili kullanma, yüz yüze iletişim kurma, ışıklı/titreşimli uyarılar ekleme, dudak okuma için uygun pozisyon alma",
            "Fiziksel/Motor Sınırlılık": "Erişilebilir materyaller sağlama, adaptif araçlar kullanma, pozisyonlama desteği verme, aktiviteleri çocuğun yapabilecekleri doğrultusunda uyarlama",
            "Dikkat Eksikliği / Hiperaktivite": "Kısa ve net yönergeler verme, göz teması kurma, etkinliği küçük adımlara bölme, sık sık olumlu pekiştireç verme, hareket fırsatları sunma",
            "Dil ve Konuşma Güçlüğü": "Basit ve kısa cümleler kullanma, beden dili ve jestlerle destekleme, görsel kartlar kullanma, sabırlı bekleme, cesaretlendirme"
          }},
          "farklilastirma_ve_kapsayicilik": {{
            "Öğrenme Hızı Farkı": {{
              "İleri Düzey": "Liderlik rolleri, akran öğretimi, araştırma projeleri, karmaşık problem çözme görevleri, seçmeli ek aktiviteler",
              "Temel Düzey": "Görsel destekler, parçalara ayırma, somut materyaller, tekrar fırsatları, akran desteği, başarı basamakları"
            }},
            "Dil Desteği": "Görsel sözlük, resimli yönergeler, vücut dili, akran tercümanlığı, anadilde anahtar kelimeler, çok dilli materyaller",
            "Kültürel Kapsayıcılık": "Farklı kültürlerden hikayeler/oyunlar, ailelerden kültürel paylaşımlar, evrensel değerler üzerinden bağlantılar, çeşitliliği kutlama",
            "Sosyal Duygusal Farklılaştırma": {{
              "Çekingen Çocuklar": "Küçük grup çalışmaları, güvenli alan, sözsüz katılım seçenekleri, kademeli katılım",
              "Dış Dönük Çocuklar": "Liderlik fırsatları, hareket içeren görevler, aktif roller",
              "Duygusal Destek": "Duygu kartları, sakinleşme köşesi, duygu termometresi, özel ilgi anları"
            }},
            "Çoklu Duyusal Yaklaşım": "Görsel (resimler, videolar), İşitsel (müzik, sesler), Dokunsal (dokular, hamur), Kinestetik (hareket, dans), Tat ve koku deneyimleri"
          }},
          "degerlendirme": {{
            "program_tarafindan": [
              "Etkinliği uygularken hangi aşamalar kolaylaştırıcı oldu?",
              "Çocukların ilgisi en çok hangi bölümde yoğunlaştı?",
              "Etkinlik süresi yeterli oldu mu? Hangi bölümler planlanandan farklı sürdü?",
              "Kullanılan materyaller amaca uygun muydu?",
              "Etkinlik planlandığı gibi uygulanabildi mi?"
            ],
            "amaclanan_beceriler_tarafindan": [
              "Çocuklar hedeflenen kavramları anlayabildi mi?",
              "Problem çözme becerileri gelişim gösterdi mi?",
              "İşbirliği ve paylaşma davranışları gözlemlendi mi?",
              "Yaratıcı düşünme ve kendini ifade etme becerileri gelişti mi?",
              "Motor beceri gelişimi için yeterli fırsat sunuldu mu?"
            ],
            "ogrenciler_tarafindan": [
              "Etkinlikte daha fazla desteğe ihtiyaç duyan çocuklar oldu mu?",
              "Öğrenme gerçekleşti mi yoksa tekrara ihtiyaç var mı?",
              "Çocuklar öğrendiklerini günlük yaşamla ilişkilendirebildi mi?",
              "Her çocuk kendi hızında ilerleyebildi mi?",
              "Farklı öğrenme stillerine sahip çocukların ihtiyaçları karşılandı mı?"
            ]
          }}
        }}
        
        SADECE JSON DÖNDÜR, BAŞKA AÇIKLAMA EKLEME!

        ÖNEMLİ KURALLAR:
        1. "sure" alanı sadece sayı olmalı (örn: 30), "30 dakika" şeklinde yazma!
        2. TÜM ALANLARI DOLDUR - özellikle "degerlendirme" bölümü boş kalmamalı
        3. Tüm metinlerde Türkçe karakterleri doğru kullan (ı, ğ, ü, ş, ö, ç)
        4. Geniş zaman kipi kullan (yapılır, edilir, sorulur)
        5. JSON formatı GEÇERLİ olmalı:
           - Her string değer tırnak içinde olmalı ve tırnak kapatılmalı
           - Array'ler [] ile başlayıp bitmelidir
           - Object'ler {{}} ile başlayıp bitmelidir
           - Son elemandan sonra virgül OLMAMALI
           - Tüm açılan parantezler kapatılmalı
        6. Metinlerde kesme işareti kullanma, tek tırnak yerine çift tırnak kullan
        7. JSON içinde newline karakteri kullanma, uzun metinleri tek satırda yaz
        """
        
        return prompt
    
    async def generate_activity_async(self, kazanimlar: List[Dict], custom_prompt: Optional[str] = None) -> Optional[Dict]:
        """Generate activity asynchronously for concurrent requests"""
        # Create prompt
        prompt = self.create_activity_prompt(kazanimlar, custom_prompt)

        # Run generation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,  # Uses default ThreadPoolExecutor
            self._generate_content_sync,
            prompt,
            kazanimlar
        )

        return result

    def _generate_content_sync(self, prompt: str, kazanimlar: List[Dict]) -> Optional[Dict]:
        """Synchronous content generation (runs in thread pool)"""
        try:
            # Get thread-local model instance
            model = self._get_model()

            # Generate content using Vertex AI
            response = model.generate_content(prompt)

            if not response or not response.text:
                logger.error("Empty response from Vertex AI")
                return None
            
            # Parse JSON from response
            activity_data = self._parse_json_response(response.text)

            if not activity_data:
                # If JSON parsing fails, try old parsing method
                logger.warning("JSON parsing failed, trying fallback parser")
                activity_data = self._parse_activity_text(response.text)

            # Ensure activity_data is a dictionary
            if not isinstance(activity_data, dict):
                logger.error(f"Activity data is not a dictionary: {type(activity_data)}")
                return None

            # Add metadata
            activity_data['kazanim_idleri'] = [k.get('id') for k in kazanimlar if k.get('id')]
            activity_data['kazanim_metinleri'] = [
                f"{k.get('yas_grubu', '')} - {k.get('ders', '')}: {k.get('ogrenme_ciktilari', '')}"
                for k in kazanimlar
            ]
            activity_data['prompt_used'] = prompt[:1000]  # Store first 1000 chars
            activity_data['ai_generated'] = True
            activity_data['model_version'] = settings.VERTEX_AI_MODEL

            # Convert nested JSON structure to flat structure for database
            activity_data = self._flatten_activity_data(activity_data)

            logger.info(f"Activity generated successfully: {activity_data.get('etkinlik_adi', 'Unknown')}")
            return activity_data

        except Exception as e:
            logger.error(f"Error generating activity: {str(e)}")
            return None

    async def generate_activity(self, kazanimlar: List[Dict], custom_prompt: Optional[str] = None) -> Optional[Dict]:
        """Generate an activity based on selected learning outcomes (backward compatible)"""
        # Use async version internally
        return await self.generate_activity_async(kazanimlar, custom_prompt)
    
    def _parse_json_response(self, text: str) -> Optional[Dict]:
        """Parse JSON from AI response with better error handling"""
        try:
            # Log the raw response for debugging
            logger.info(f"Raw AI response length: {len(text)} chars")
            logger.debug(f"Raw AI response (first 1000 chars): {text[:1000]}")
            logger.debug(f"Raw AI response (last 500 chars): {text[-500:] if len(text) > 500 else text}")

            # Remove markdown code blocks if present
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly - be more flexible
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = text.strip()

            # Clean up common JSON issues
            json_str = json_str.strip()

            # Fix incomplete strings - add closing quote if missing
            lines = json_str.split('\n')
            fixed_lines = []
            for i, line in enumerate(lines):
                # Count quotes in the line
                quote_count = line.count('"') - line.count('\\"')
                if quote_count % 2 == 1:  # Odd number of quotes
                    # Check if line ends with incomplete string
                    if not line.rstrip().endswith('"') and not line.rstrip().endswith(','):
                        line = line.rstrip() + '",'
                    elif not line.rstrip().endswith('"'):
                        line = line.rstrip() + '"'
                fixed_lines.append(line)
            json_str = '\n'.join(fixed_lines)

            # Remove any trailing commas before closing braces/brackets
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            # Fix double commas
            json_str = re.sub(r',\s*,', ',', json_str)
            # Remove any BOM or invisible characters
            json_str = json_str.replace('\ufeff', '').replace('\u200b', '')

            # Handle truncated JSON by trying to close it properly
            open_braces = json_str.count('{') - json_str.count('}')
            open_brackets = json_str.count('[') - json_str.count(']')

            if open_brackets > 0:
                json_str += ']' * open_brackets
            if open_braces > 0:
                json_str += '}' * open_braces

            # Try to parse JSON
            data = json.loads(json_str)

            # Validate required fields
            required_fields = ['etkinlik_adi', 'alan_adi', 'yas_grubu', 'sure', 'uygulama_yeri']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing required field: {field}")
                    data[field] = self._get_default_value(field)

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Problematic JSON string (first 1000 chars): {json_str[:1000] if 'json_str' in locals() else 'Not available'}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in JSON parsing: {e}")
            return None

    def _get_default_value(self, field: str):
        """Get default value for missing field"""
        defaults = {
            'etkinlik_adi': 'Etkinlik',
            'alan_adi': 'Genel',
            'yas_grubu': '48-60 ay',
            'sure': 30,
            'uygulama_yeri': 'Sınıf içi'
        }
        return defaults.get(field, '')
    
    def _flatten_activity_data(self, data: Dict) -> Dict:
        """Convert nested JSON structure to flat structure for database"""
        flat = {}
        
        # Basic fields
        flat['etkinlik_adi'] = data.get('etkinlik_adi', '')
        flat['alan_adi'] = data.get('alan_adi', '')
        flat['yas_grubu'] = data.get('yas_grubu', '')
        
        # Parse duration - handle "35 dakika" or just "35"
        sure_str = str(data.get('sure', '30'))
        import re
        numbers = re.findall(r'\d+', sure_str)
        flat['sure'] = int(numbers[0]) if numbers else 30
        
        flat['uygulama_yeri'] = data.get('uygulama_yeri', '')
        
        # Amaçlar
        amaclar = data.get('amaclar', [])
        flat['etkinlik_amaci'] = '\n'.join([f"• {amac}" for amac in amaclar])
        
        # Materyaller
        materyaller = data.get('materyaller', [])
        if isinstance(materyaller, list):
            # Eğer liste ise madde madde yazdır
            mat_text = []
            for item in materyaller:
                mat_text.append(f"• {item}")
            flat['materyaller'] = '\n'.join(mat_text)
        else:
            # Eski format (dict) ise string'e çevir
            flat['materyaller'] = str(materyaller)
        
        # Uygulama Süreci
        surec = data.get('uygulama_sureci', {})
        surec_text = []
        
        # Giriş
        giris = surec.get('giris', {})
        if giris:
            surec_text.append(f"GİRİŞ ({giris.get('sure', '5-7 dakika')}):")
            for adim in giris.get('adimlar', []):
                surec_text.append(f"• {adim}")
        
        # Gelişme
        gelisme = surec.get('gelisme', {})
        if gelisme:
            surec_text.append(f"\nGELİŞME ({gelisme.get('sure', '20 dakika')}):")
            for key, value in gelisme.get('aktiviteler', {}).items():
                surec_text.append(f"• {value}")
        
        # Yansıma
        yansima = surec.get('yansima_cemberi', {})
        if yansima:
            surec_text.append(f"\nYANSIMA ÇEMBERİ ({yansima.get('sure', '5-7 dakika')}):")
            surec_text.append(f"Düzenleme: {yansima.get('duzenleme', '')}")
            surec_text.append("\nYönlendirici Sorular:")
            for soru in yansima.get('sorular', []):
                surec_text.append(f"• {soru}")

            # Yeni format için öğretmen yönlendirmeleri
            if yansima.get('ogretmen_yonlendirmeleri'):
                surec_text.append("\nÖğretmen Yönlendirmeleri:")
                for yonlendirme in yansima['ogretmen_yonlendirmeleri']:
                    surec_text.append(f"• {yonlendirme}")
            # Eski format desteği
            elif yansima.get('ogretmen_ozet_ornekleri'):
                surec_text.append("\nÖğretmen Özet Örnekleri:")
                for ornek in yansima['ogretmen_ozet_ornekleri']:
                    surec_text.append(f"• {ornek}")

            if yansima.get('kapaniş'):
                surec_text.append(f"\nKapanış: {yansima['kapaniş']}")
            elif yansima.get('kapaniş_sorusu'):
                surec_text.append(f"\nKapanış Sorusu: {yansima['kapaniş_sorusu']}")

            if yansima.get('temizlik'):
                surec_text.append(f"Temizlik: {yansima['temizlik']}")
            elif yansima.get('final'):
                surec_text.append(f"Final: {yansima['final']}")
        
        # Sonuç
        sonuc = surec.get('sonuc', {})
        if sonuc:
            surec_text.append(f"\nSONUÇ ({sonuc.get('sure', '3 dakika')}):")
            for aktivite in sonuc.get('aktiviteler', []):
                surec_text.append(f"• {aktivite}")
        
        flat['uygulama_sureci'] = '\n'.join(surec_text)
        
        # Uyarlama
        uyarlama = data.get('uyarlama', {})
        uyarlama_text = []

        # Turkish field name mappings for uyarlama (handle both formats)
        uyarlama_field_map = {
            'gorme_yetersizligi': 'Görme Yetersizliği',
            'isitme_yetersizligi': 'İşitme Yetersizliği',
            'fiziksel_motor_sinirlilik': 'Fiziksel Motor Sınırlılık',
            'dikkat_eksikligi_hiperaktivite': 'Dikkat Eksikliği ve Hiperaktivite',
            'otizm_spektrum_bozuklugu': 'Otizm Spektrum Bozukluğu',
            'dil_ve_konusma_guclugu': 'Dil ve Konuşma Güçlüğü',
            'zihinsel_yetersizlik': 'Zihinsel Yetersizlik',
            'ogrenme_guclugu': 'Öğrenme Güçlüğü'
        }

        for key, value in uyarlama.items():
            if value:
                # If key already has Turkish characters, use it as is
                if any(char in key for char in 'ÇĞÖŞÜçğöşüıİ'):
                    baslik = key
                else:
                    baslik = uyarlama_field_map.get(key, key.replace('_', ' ').title())
                uyarlama_text.append(f"{baslik}: {value}")
        flat['uyarlama'] = '\n'.join(uyarlama_text) if uyarlama_text else 'Farklı Yaş Grupları:\n• 36-48 ay: Etkinlik basitleştirilerek uygulanır, daha kısa süreli tutulur\n• 48-60 ay: Mevcut plan uygulanır\n• 60-72 ay: Etkinlik zenginleştirilerek, ek görevlerle desteklenir\n\nFarklı Ortamlar:\n• İç mekan: Sınıf ortamında masa başı veya halı alanında uygulanır\n• Dış mekan: Bahçede veya açık alanda hareket alanı genişletilerek uygulanır\n• Ev ortamı: Aile katılımı ile evde tekrar edilebilir'
        
        # Farklılaştırma
        farklilastirma = data.get('farklilastirma_ve_kapsayicilik', {})
        fark_text = []

        # Turkish field name mappings for farklılaştırma (handle both formats)
        fark_field_map = {
            'ogrenme_hizi_farki': 'Öğrenme Hızı Farkı',
            'ileri_duzey': 'İleri Düzey',
            'temel_duzey': 'Temel Düzey',
            'dil_destegi': 'Dil Desteği',
            'kulturel_kapsayicilik': 'Kültürel Kapsayıcılık',
            'sosyal_duygusal_farklilastirma': 'Sosyal Duygusal Farklılaştırma',
            'cekingen_cocuklar': 'Çekingen Çocuklar',
            'dis_donuk_cocuklar': 'Dış Dönük Çocuklar',
            'duygusal_destek': 'Duygusal Destek',
            'coklu_duyusal_yaklasim': 'Çoklu Duyusal Yaklaşım'
        }

        for key, value in farklilastirma.items():
            if isinstance(value, dict):
                # If key already has Turkish characters, use it as is
                if any(char in key for char in 'ÇĞÖŞÜçğöşüıİ'):
                    baslik = key
                else:
                    baslik = fark_field_map.get(key, key.replace('_', ' ').title())
                fark_text.append(f"\n{baslik}:")
                for sub_key, sub_value in value.items():
                    if any(char in sub_key for char in 'ÇĞÖŞÜçğöşüıİ'):
                        sub_baslik = sub_key
                    else:
                        sub_baslik = fark_field_map.get(sub_key, sub_key.replace('_', ' ').title())
                    fark_text.append(f"• {sub_baslik}: {sub_value}")
            else:
                # If key already has Turkish characters, use it as is
                if any(char in key for char in 'ÇĞÖŞÜçğöşüıİ'):
                    baslik = key
                else:
                    baslik = fark_field_map.get(key, key.replace('_', ' ').title())
                fark_text.append(f"{baslik}: {value}")
        flat['farklilastirma_kapsayicilik'] = '\n'.join(fark_text) if fark_text else 'Özel Gereksinimli Çocuklar:\n• Görme yetersizliği: Sesli betimlemeler, dokunsal materyaller, kabartmalı şekiller kullanılır\n• İşitme yetersizliği: Görsel ipuçları, işaret dili desteği, yazılı yönergeler verilir\n• Fiziksel yetersizlik: Erişilebilir materyaller, uyarlanmış araç-gereçler kullanılır\n• Zihinsel yetersizlik: Basitleştirilmiş yönergeler, tekrarlar, somut materyaller kullanılır\n• Otizm spektrum bozukluğu: Görsel programlar, yapılandırılmış ortam, rutinler oluşturulur\n• Dikkat eksikliği ve hiperaktivite: Kısa süreli etkinlikler, hareket araları, odaklanma destekleri sağlanır\n• Öğrenme güçlüğü: Çoklu duyusal yaklaşımlar, bireyselleştirilmiş destek verilir\n• Dil ve konuşma bozukluğu: Alternatif iletişim yöntemleri, görsel kartlar kullanılır\n\nÜstün Yetenekli Çocuklar:\n• Zenginleştirilmiş içerik ve ek görevler verilir\n• Yaratıcı düşünmeyi teşvik eden sorular sorulur\n• Liderlik rolleri ve akran öğretimi fırsatları sunulur'
        
        # Değerlendirme
        degerlendirme = data.get('degerlendirme', {})

        # Yeni format için gözlem formu
        if degerlendirme.get('gozlem_formu'):
            prog_text = ["Gözlem Formu:"]
            for item in degerlendirme['gozlem_formu']:
                prog_text.append(f"• {item}")
            flat['degerlendirme_program'] = '\n'.join(prog_text)
        # Eski format desteği
        elif degerlendirme.get('program_tarafindan'):
            prog_text = ["Program Değerlendirmesi:"]
            for item in degerlendirme['program_tarafindan']:
                prog_text.append(f"• {item}")
            flat['degerlendirme_program'] = '\n'.join(prog_text)
        else:
            flat['degerlendirme_program'] = 'Gözlem Formu:\n• Etkinlik süresi ve akışı değerlendirilir\n• Materyallerin uygunluğu kontrol edilir\n• Çocukların ilgi düzeyi gözlemlenir'

        # Yeni format için öğretmen öz değerlendirme
        if degerlendirme.get('ogretmen_oz_degerlendirme'):
            beceri_text = ["Öğretmen Öz Değerlendirme:"]
            for item in degerlendirme['ogretmen_oz_degerlendirme']:
                beceri_text.append(f"• {item}")
            flat['degerlendirme_beceriler'] = '\n'.join(beceri_text)
        # Eski format desteği
        elif degerlendirme.get('amaclanan_beceriler_tarafindan'):
            beceri_text = ["Beceri Değerlendirmesi:"]
            for item in degerlendirme['amaclanan_beceriler_tarafindan']:
                beceri_text.append(f"• {item}")
            flat['degerlendirme_beceriler'] = '\n'.join(beceri_text)
        else:
            flat['degerlendirme_beceriler'] = 'Gelişim Alanları:\n• Bilişsel gelişim: Problem çözme ve analitik düşünme becerileri\n• Dil gelişimi: Kelime hazinesi ve iletişim becerileri\n• Sosyal-duygusal gelişim: İşbirliği ve empati kurma\n• Motor gelişim: İnce ve kaba motor beceriler'

        # Yeni format için çocuk değerlendirmesi
        if degerlendirme.get('cocuk_degerlendirmesi'):
            ogrenci_text = ["Çocuk Değerlendirmesi:"]
            for item in degerlendirme['cocuk_degerlendirmesi']:
                ogrenci_text.append(f"• {item}")
            flat['degerlendirme_ogrenciler'] = '\n'.join(ogrenci_text)
        # Eski format desteği
        elif degerlendirme.get('ogrenciler_tarafindan'):
            ogrenci_text = ["Öğrenci Değerlendirmesi:"]
            for item in degerlendirme['ogrenciler_tarafindan']:
                ogrenci_text.append(f"• {item}")
            flat['degerlendirme_ogrenciler'] = '\n'.join(ogrenci_text)
        else:
            flat['degerlendirme_ogrenciler'] = 'Bireysel Gözlem:\n• Her çocuğun etkinliğe katılım düzeyi\n• Bireysel güçlü yönler ve gelişim alanları\n• Öğrenme stilleri ve tercihler\n• İlerleme durumu ve kazanımlara ulaşma düzeyi'

        # Yeni format için aile geri bildirimi
        if degerlendirme.get('aile_geri_bildirimi'):
            aile_text = ["Aile Geri Bildirimi:"]
            for item in degerlendirme['aile_geri_bildirimi']:
                aile_text.append(f"• {item}")
            # Aile geri bildirimini öğrenci değerlendirmesine ekle
            if flat['degerlendirme_ogrenciler']:
                flat['degerlendirme_ogrenciler'] += '\n\n' + '\n'.join(aile_text)
            else:
                flat['degerlendirme_ogrenciler'] = '\n'.join(aile_text)
        
        # Store original JSON for later use
        flat['json_data'] = json.dumps(data, ensure_ascii=False)
        
        return flat
    
    def _parse_activity_text(self, text: str) -> Dict:
        """Fallback parser for non-JSON responses"""
        logger.info("Using fallback parser for activity generation")

        # Try to extract title from the text if possible
        title = 'Keşif ve Öğrenme Etkinliği'
        if text and 'etkinlik_adi' in text.lower():
            try:
                import re
                title_match = re.search(r'"etkinlik_adi"\s*:\s*"([^"]+)"', text)
                if title_match:
                    title = title_match.group(1)
            except:
                pass

        # Create a comprehensive activity structure with all fields filled
        activity = {
            'etkinlik_adi': title,
            'alan_adi': 'Bütünleşik',
            'yas_grubu': '48-60 ay',
            'sure': 30,
            'uygulama_yeri': 'Sınıf içi',
            'amaclar': [
                'Kazanımlara uygun öğrenme hedefleri',
                'Gelişim alanlarını destekleme'
            ],
            'materyaller': ['Temel eğitim materyalleri'],
            'uygulama_sureci': {
                'giris': {
                    'sure': '5-7 dakika',
                    'adimlar': ['Dikkat çekici başlangıç', 'Konu tanıtımı']
                },
                'gelisme': {
                    'sure': '20 dakika',
                    'aktiviteler': {
                        'aktivite_1': 'Ana etkinlik uygulaması'
                    }
                },
                'yansima_cemberi': {
                    'sure': '5-7 dakika',
                    'sorular': ['Neler öğrendik?', 'Nasıl hissettiniz?']
                },
                'sonuc': {
                    'sure': '3 dakika',
                    'aktiviteler': ['Toparlama ve kapanış']
                }
            },
            'uyarlama': {
                'gorme_yetersizligi': 'Sesli betimlemeler, dokunsal materyaller, akran desteği sağlanır',
                'isitme_yetersizligi': 'Görsel ipuçları, işaret dili desteği, yüz yüze iletişim kurulur',
                'fiziksel_motor_sinirlilik': 'Erişilebilir materyaller, uyarlanmış araç-gereçler kullanılır',
                'dikkat_eksikligi_hiperaktivite': 'Kısa ve net yönergeler verilir, hareket molaları eklenir',
                'otizm_spektrum_bozuklugu': 'Görsel programlar, yapılandırılmış ortam, rutinler oluşturulur',
                'dil_ve_konusma_guclugu': 'Görsel kartlar, sabırlı dinleme, alternatif iletişim yöntemleri kullanılır'
            },
            'farklilastirma_ve_kapsayicilik': {
                'ogrenme_hizi_farki': {
                    'ileri_duzey': 'Ek sorumluluklar verilir, liderlik rolleri, akran öğretimi yapılır',
                    'temel_duzey': 'Somut materyaller, tekrar fırsatları, bireysel destek sağlanır'
                },
                'dil_destegi': 'Görsel sözlük, resimli yönergeler, çok dilli materyaller kullanılır',
                'kulturel_kapsayicilik': 'Farklı kültürlerden örnekler, evrensel değerler vurgulanır',
                'sosyal_duygusal_farklilastirma': {
                    'cekingen_cocuklar': 'Küçük grup çalışmaları, güvenli alan, kademeli katılım sağlanır',
                    'dis_donuk_cocuklar': 'Liderlik fırsatları, hareket içeren görevler verilir',
                    'duygusal_destek': 'Duygu kartları, sakinleşme köşesi, bireysel ilgi gösterilir'
                },
                'coklu_duyusal_yaklasim': 'Görsel, işitsel, dokunsal, kinestetik öğrenme fırsatları sunulur'
            },
            'degerlendirme': {
                'gozlem_formu': [
                    'Çocukların etkinliğe ilgi ve katılım düzeyi gözlemlenir',
                    'Kazanımlara ulaşma durumu değerlendirilir',
                    'Bireysel gelişim farklılıkları not edilir',
                    'Sosyal etkileşim kalitesi gözlemlenir',
                    'Problem çözme becerileri değerlendirilir'
                ],
                'ogretmen_oz_degerlendirme': [
                    'Etkinlik planının uygulanabilirliği değerlendirilir',
                    'Zaman yönetimi ve geçişlerin akıcılığı kontrol edilir',
                    'Materyallerin yeterliliği değerlendirilir',
                    'Çocukların bireysel ihtiyaçlarına yanıt verilme durumu gözden geçirilir',
                    'Etkinliğin geliştirilmesi gereken yönleri belirlenir'
                ],
                'cocuk_degerlendirmesi': [
                    'Çocukların etkinlikle ilgili duyguları sorulur',
                    'En sevdikleri bölüm öğrenilir',
                    'Zorlandıkları noktalar belirlenir',
                    'Öğrendiklerini ifade etmeleri istenir',
                    'Tekrar yapmak istedikleri aktiviteler öğrenilir'
                ],
                'aile_geri_bildirimi': [
                    'Evde etkinlikle ilgili paylaşımlar yapılır',
                    'Çocuğun eve yansıyan öğrenmeleri takip edilir',
                    'Ailelerin etkinlik önerileri alınır'
                ]
            }
        }

        # Try to extract some meaningful content from the text
        if text and len(text) > 100:
            # Try to use first line as title if possible
            lines = text.split('\n')
            if lines and len(lines[0]) < 100:
                activity['etkinlik_adi'] = lines[0].strip()[:100]

        return activity

    async def generate_content(self, prompt: str, use_json_output: bool = True) -> str:
        """Generate content using Vertex AI for daily plans

        Args:
            prompt: The prompt to send to Vertex AI
            use_json_output: If True, use structured JSON output (default: True)
        """
        try:
            logger.info(f"=== VERTEX AI: Generating content with prompt length: {len(prompt)} ===")
            logger.info(f"=== Using JSON output mode: {use_json_output} ===")

            # Get the appropriate model (with or without JSON output)
            model = self._get_model(use_json_output=use_json_output)

            # Generate content using Vertex AI
            response = model.generate_content(prompt)

            if not response or not response.text:
                logger.error("Empty response from Vertex AI")
                return "{}"

            logger.info(f"=== VERTEX AI: Response received, length: {len(response.text)} ===")

            # If using JSON output, validate it's proper JSON
            if use_json_output:
                try:
                    # Try to parse to validate it's valid JSON
                    json.loads(response.text)
                    logger.info("=== Response is valid JSON ===")
                except json.JSONDecodeError as e:
                    logger.error(f"Response is not valid JSON: {str(e)}")
                    logger.error(f"First 500 chars of response: {response.text[:500]}")

            return response.text

        except Exception as e:
            logger.error(f"Error generating content from Vertex AI: {str(e)}")
            # Return a basic structure if AI fails
            return json.dumps({
                "alan_becerileri": {},
                "kavramsal_beceriler": {},
                "egilimler": {},
                "sosyal_duygusal_beceriler": {},
                "degerler": {},
                "okuryazarlik_becerileri": {},
                "ogrenme_ciktilari": {},
                "kavramlar": "",
                "sozcukler": "",
                "materyaller": "",
                "egitim_ortamlari": "Sınıf, oyun alanı",
                "gune_baslama": "Çocuklar sınıfa geldiklerinde karşılanır.",
                "ogrenme_merkezleri": "Öğrenme merkezlerinde serbest oyun zamanı.",
                "beslenme_toplanma": "Beslenme saati rutini uygulanır.",
                "etkinlikler": "Seçilen etkinlikler uygulanır.",
                "degerlendirme": "Günün değerlendirmesi yapılır.",
                "zenginlestirme": "",
                "destekleme": "",
                "aile_katilimi": "",
                "toplum_katilimi": "",
                "notlar": ""
            }, ensure_ascii=False)

# Singleton instance
vertex_ai_service = VertexAIService()