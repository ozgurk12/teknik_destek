import os
import json
import asyncio
import threading
from typing import List, Dict, Optional
from datetime import datetime
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Thread-local storage for model instances
_thread_local = threading.local()

class VideoGenerationService:
    """Service for generating educational video scripts using Google Vertex AI"""

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

            logger.info("Vertex AI initialized successfully for video generation")

        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise

    def _get_model(self):
        """Get thread-local model instance for concurrent requests"""
        if not hasattr(_thread_local, 'model'):
            _thread_local.model = GenerativeModel(
                model_name=settings.VERTEX_AI_MODEL,
                generation_config=GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=32768,
                )
            )
        return _thread_local.model
    
    def create_video_script_prompt(self,
                                   ders: str,
                                   konu: str,
                                   yas_grubu: str,
                                   kazanimlar: List[Dict],
                                   video_yapisi: str = "2 bölüm",
                                   bolum_sonu_etkinligi: str = "",
                                   vurgu_noktalari: str = "",
                                   kacinilacaklar: str = "") -> str:
        """Create a detailed prompt for video script generation"""

        # Kazanımları formatla
        kazanim_text = ""
        for kazanim in kazanimlar:
            kazanim_text += f"- {kazanim.get('alan_becerileri', '')} - {kazanim.get('ogrenme_ciktilari', '')}\n"

        # Opsiyonel parametreleri ekle
        ozel_istekler = ""
        if video_yapisi:
            ozel_istekler += f"\nVideo Yapısı: {video_yapisi}"
        if bolum_sonu_etkinligi:
            ozel_istekler += f"\nBölüm Sonu Etkinliği: {bolum_sonu_etkinligi}"
        if vurgu_noktalari:
            ozel_istekler += f"\nVurgulanmasını İstediğiniz Özel Noktalar: {vurgu_noktalari}"
        if kacinilacaklar:
            ozel_istekler += f"\nKaçınılmasını İstediğiniz Noktalar: {kacinilacaklar}"

        prompt = f"""Merhabalar, senden dijital bir platform olan Edupage Kids için bir "Konu Anlatım Videosu" metni hazırlamanı istiyorum. Bu metin, okul öncesi eğitim programı kapsamında kullanılacak ve Atlas adında bir karakter tarafından seslendirilecektir.

BÖLÜM 1: TEMEL BİLGİLER
Ders: {ders}
Konu: {konu}
Hedef Yaş Grubu: {yas_grubu}

İlgili Kazanımlar:
{kazanim_text}

BÖLÜM 2: İÇERİK DETAYLARI VE ÖZEL İSTEKLER{ozel_istekler}

Senden beklentim, bu bilgilere dayanarak aşağıda detaylandırdığım format ve içerik felsefesine harfiyen uymandır.

1. GENEL FORMAT

Metin, aşağıdaki başlıkları ve yapıyı içermelidir:

[Video Başlığı]

Ders: {ders}

Hedef Yaş Grubu: {yas_grubu}

Video Süresi: (Yaklaşık olarak belirt)

Karakter: Atlas (Anlatıcı)

1. BÖLÜM: [Bölüm Başlığı]

1. Arka Plan (Görsel ve Müzik):

2. Seslendiren Karakter (Atlas):

3. Metin (Atlas'ın Anlatımı):

2. BÖLÜM: [Bölüm Başlığı]

1. Arka Plan (Görsel ve Müzik):

2. Seslendiren Karakter (Atlas):

3. Metin (Atlas'ın Anlatımı):

ÖNEMLİ FORMAT KURALI: Atlas'ın konuşmaları sırasında, arka planda o an ne olması gerektiğini belirtmek için lütfen **(Parantez içinde, kalın harflerle)** anlık görsel veya eylem yönlendirmeleri ekle. Bu, metnin akışını ve görselle senkronizasyonunu anlamam için kritik öneme sahiptir.

2. İÇERİK FELSEFESİ VE BEKLENTİLER

Yaş Grubuna Uygunluk (En Önemli Kural): Vereceğim yaş grubunun ({yas_grubu}) bilişsel, dil ve motor gelişim özelliklerini mutlaka göz önünde bulundur. Kullandığın kelimeler, cümlelerin uzunluğu, anlatılan kavramların derinliği ve etkinliklerin karmaşıklığı yaş grubuna göre belirgin şekilde farklılaşmalıdır.

Hikayeleştirme ve Benzetmeler: Soyut kavramları (sayılar, zıt kavramlar, bilimsel olgular vb.) somutlaştırmak için mutlaka hikayeler, masallar ve çocukların dünyasından basit benzetmeler (örneğin, 3 rakamını kelebek kanadına, ekinoksu tahterevalliye benzetmek gibi) kullan. Konuyu bir ders gibi değil, bir macera veya keşif gibi sun.

Etkileşim: Video pasif bir izleme deneyimi olmamalıdır. Mutlaka şu etkileşim türlerinden uygun olanları kullan:

Fiziksel Hareket: Çocukları bedenleriyle veya parmaklarıyla bir şeyler yapmaya teşvik et (havaya çizim yapma, bir hayvanı taklit etme, bedensel oyunlar).

Bilişsel Katılım: Bilmeceler, "Sizce ne olacak?" gibi tahmin soruları sor.

Yaratıcı Düşünme: Videonun sonunu mutlaka çocukları hayal kurmaya, kendi fikirlerini üretmeye veya bir problemi çözmeye yönlendiren açık uçlu bir soruyla bitir.

Bölüm Akışı:

1. Bölüm: Genellikle konunun tanıtıldığı, temel özelliklerinin verildiği ve basit, somut örneklerle açıklandığı bölümdür. Genellikle fiziksel bir oyun, bilmece veya interaktif bir etkinlikle biter.

2. Bölüm: Konunun daha derinleştirildiği, günlük yaşamla veya başka alanlarla (sanat, bilim, doğa) bağlantılarının kurulduğu bölümdür. Genellikle yaratıcı düşünmeye teşvik eden bir soruyla biter.

Atlas'ın Karakteri ve Tonu: Atlas, didaktik bir öğretmen değil; sıcak, sevecen, meraklı bir arkadaş ve keşif lideridir. Sesi her zaman pozitif, teşvik edici ve enerjiktir.

Dil Kullanımı:

Asla "Anladınız mı?" gibi sorgulayıcı ifadeler kullanma. Bunun yerine "Harikasınız!", "Bravo size!" gibi pozitif pekiştireçler kullan.

Doğa olaylarına veya nesnelere olumsuz insani özellikler yükleme (örneğin "yaramaz rüzgar" yerine "güçlü rüzgar" de).

KONU ANLATIM METNİ İSTERKEN YAPAY ZEKAYA VERİLECEK BİLGİLER

Konu Anlatım Metni İstek Şablonu:

Lütfen yukarıdaki tüm kurallara harfiyen uyarak, {konu} konusunda bir video metni hazırla.

ÖNEMLİ: Çıktını kesinlikle aşağıdaki JSON formatında ver. Başka hiçbir açıklama veya metin ekleme, sadece JSON döndür:

{{
  "title": "Video Başlığı",
  "subject": "{ders}",
  "age_group": "{yas_grubu}",
  "duration": "Video süresi dakika olarak (örn: 5)",
  "character": "Atlas",
  "sections": [
    {{
      "section_number": 1,
      "section_title": "1. Bölüm Başlığı",
      "background": {{
        "visual": "Arka plan görsel açıklaması",
        "music": "Arka plan müzik açıklaması"
      }},
      "character": "Atlas",
      "text": "Atlas'ın bu bölümdeki tüm anlatım metni. **(Parantez içinde görsel yönlendirmeler)** ile birlikte."
    }},
    {{
      "section_number": 2,
      "section_title": "2. Bölüm Başlığı",
      "background": {{
        "visual": "Arka plan görsel açıklaması",
        "music": "Arka plan müzik açıklaması"
      }},
      "character": "Atlas",
      "text": "Atlas'ın bu bölümdeki tüm anlatım metni. **(Parantez içinde görsel yönlendirmeler)** ile birlikte."
    }}
  ]
}}"""

        return prompt
    
    async def generate_video_script(self,
                                   ders: str,
                                   konu: str,
                                   yas_grubu: str,
                                   kazanimlar: List[Dict],
                                   video_yapisi: str = "2 bölüm",
                                   bolum_sonu_etkinligi: str = "",
                                   vurgu_noktalari: str = "",
                                   kacinilacaklar: str = "",
                                   custom_prompt: Optional[str] = None) -> str:
        """Generate a video script based on the given parameters"""
        try:
            # Create the prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self.create_video_script_prompt(
                    ders, konu, yas_grubu, kazanimlar,
                    video_yapisi, bolum_sonu_etkinligi,
                    vurgu_noktalari, kacinilacaklar
                )
            
            # Get thread-local model instance
            model = self._get_model()
            
            # Generate using the model
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: model.generate_content(prompt)
            )
            
            if response and response.text:
                return response.text
            else:
                logger.error("No text received from Vertex AI")
                return "Video metni oluşturulamadı."
                
        except Exception as e:
            logger.error(f"Error generating video script: {str(e)}")
            raise

# Singleton instance
video_generation_service = VideoGenerationService()