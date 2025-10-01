import os
import json
from typing import List, Dict, Optional
from google.oauth2 import service_account
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class VertexAIService:
    """Service for generating activities using Google Vertex AI"""
    
    def __init__(self):
        self._initialize_vertex_ai()
        
    def _initialize_vertex_ai(self):
        """Initialize Vertex AI with service account credentials"""
        try:
            # Get credentials path
            credentials_path = settings.GOOGLE_APPLICATION_CREDENTIALS
            if not credentials_path:
                credentials_path = "../credentials/google-service-account.json"
            
            # Resolve absolute path
            if not os.path.isabs(credentials_path):
                credentials_path = os.path.abspath(credentials_path)
            
            # Load service account credentials
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            # Initialize Vertex AI
            vertexai.init(
                project=settings.VERTEX_AI_PROJECT_ID,
                location=settings.VERTEX_AI_LOCATION,
                credentials=credentials
            )
            
            # Initialize the model
            self.model = GenerativeModel(
                model_name=settings.VERTEX_AI_MODEL,
                generation_config=GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=8192,
                )
            )
            
            logger.info("Vertex AI initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise
    
    def create_activity_prompt(self, kazanimlar: List[Dict]) -> str:
        """Create a detailed prompt for activity generation"""
        
        kazanim_listesi = "\n".join([
            f"- {k.get('yas_grubu', '')} yaş, {k.get('ders', '')}: {k.get('ogrenme_ciktilari', '')}"
            for k in kazanimlar
        ])
        
        prompt = f"""
        Okul öncesi öğretmeni olarak, aşağıdaki kazanımlara uygun detaylı bir etkinlik planı oluştur.
        ÇIKTI FORMATI JSON OLMALIDIR!
        
        KAZANIMLAR:
        {kazanim_listesi}
        
        ETKİNLİK PLANI JSON FORMATI (Tam olarak bu JSON yapısına uy):
        
        ```json
        {
        
          "etkinlik_adi": "Yaratıcı ve ilgi çekici bir isim",
          "alan_adi": "Fen ve Ekoloji/Matematik/Türkçe/Sanat/Müzik/Hareket ve Sağlık/Sosyal vb.",
          "yas_grubu": "36-48 ay veya 48-60 ay veya 60-72 ay",
          "sure": "30",
          "uygulama_yeri": "Sınıf içi/Bahçe/Spor salonu vb.",
        
          "amaclar": [
            "Çocukların kazanımla ilgili amaç 1",
            "Kazanımla ilgili amaç 2",
            "Gelişim alanıyla ilgili amaç 3",
            "Beceri geliştirmeye yönelik amaç 4"
          ],
        
          "materyaller": {
            "temel_malzemeler": "Kağıt, kalem, boya, makas, yapıştırıcı",
            "kategori_1": {
              "ana": ["Resimli kartlar", "fotoğraflar", "posterler"],
              "alternatif": ["Projeksiyon", "tablet görselleri", "dergi resimleri"]
            },
            "kategori_2": {
              "ana": ["Yapraklar", "taşlar", "dallar"],
              "alternatif": ["Kum", "toprak", "çiçekler"]
            },
            "kategori_3": {
              "ana": ["Plastik kaplar", "karton kutular"],
              "alternatif": ["Gazete kağıdı", "yumurta kolileri"]
            },
            "kategori_4": {
              "ana": ["Marakas", "davul", "zil"],
              "alternatif": ["Mutfak eşyaları", "el yapımı enstrümanlar"]
            },
            "kategori_5": {
              "ana": ["Islak mendil", "eldiven"],
              "alternatif": ["Önlük", "gazete"]
            }
          },
        
        UYGULAMA SÜRECİ:
        
        GİRİŞ (5-7 dakika):
        • Çocukları halı üzerinde yarım daire şeklinde oturtun
        • "Bugün sizlerle çok eğlenceli bir etkinlik yapacağız" diyerek dikkat çekin
        • Gizemli kutudan/torbadan ipucu materyali çıkarın
        • "Bu ne olabilir? Ne işe yarar?" sorularıyla merak uyandırın
        • Çocukların tahminlerini dinleyin ve değer verin
        • Kısa bir parmak oyunu veya tekerleme ile enerjiyi yükseltin
        
        GELİŞME (20 dakika):
        Aktivite 1 - Keşfetme (5 dakika):
        Öğretmen materyalleri tanıtır, çocuklar inceleme fırsatı bulur. Her çocuğun dokunmasına, koklamasına, gözlemlemesine izin verin.
        
        Aktivite 2 - Deneme (5 dakika):
        Çocuklar materyallerle serbest deneme yapar. Öğretmen gözlemler, gerektiğinde yönlendirir ama müdahale etmez.
        
        Aktivite 3 - Uygulama (5 dakika):
        Ana etkinlik uygulanır. Öğretmen model olur, çocuklar kendi çalışmalarını yapar. Bireysel farklılıklara saygı gösterilir.
        
        Aktivite 4 - Paylaşma (3 dakika):
        Çocuklar yaptıklarını arkadaşlarına gösterir, anlatır. Herkes alkışlanır ve teşvik edilir.
        
        Aktivite 5 - Genişletme (2 dakika):
        Etkinlik farklı bir boyuta taşınır, yeni bir meydan okuma sunulur.
        
        YANSIMA ÇEMBERİ (5-7 dakika):
        Düzenleme: Çocuklar yine yarım daire şeklinde otururlar, eller dizlerin üzerinde
        
        Yönlendirici Sorular:
        • "Bugün neler yaptık? En çok hangi bölümü sevdiniz?"
        • "Kendinizi nasıl hissettiniz? Mutlu, heyecanlı, meraklı?"
        • "Zorlandığınız bir yer oldu mu? Nasıl çözdünüz?"
        • "Evde ailenizle bunu nasıl yapabilirsiniz?"
        
        Öğretmen Özet Örnekleri:
        • "Bugün hep birlikte harika işler başardık"
        • "Herkes çok güzel fikirler üretti ve paylaştı"
        
        Kapanış Sorusu: "Yarın bu etkinliğe devam etsek ne eklemek isterdiniz?"
        
        Final: "Şimdi hep birlikte etkinlik alanımızı toparlayalım"
        
        SONUÇ (3 dakika):
        • Materyalleri toplama oyunu ("Kim daha hızlı toplar" yarışması)
        • Teşekkür şarkısı veya alkış yağmuru
        
        UYARLAMA:
        Görme Yetersizliği: Dokunsal materyaller kullanın, sesli betimlemeler yapın, arkadaş desteği sağlayın
        İşitme Yetersizliği: Görsel ipuçları, jest ve mimikler kullanın, göz teması kurun
        Fiziksel/Motor Sınırlılık: Materyalleri erişilebilir konumlandırın, uyarlanmış araçlar kullanın
        Dikkat Eksikliği/Hiperaktivite: Kısa ve net yönergeler, sık ara ve hareket molası, sorumluluk verin
        Dil ve Konuşma Güçlüğü: Basit cümleler, görsel kartlar, sabırlı dinleme
        
        FARKLILAŞTIRMA VE KAPSAYICILIK:
        
        Öğrenme Hızı Farkı:
        İleri düzey: Ek sorumluluklar verin, diğer arkadaşlarına yardım etmesini isteyin
        Ek destek: Birebir ilgilenin, basitleştirilmiş yönergeler, daha fazla tekrar
        
        Dil Desteği:
        Ana dili farklı olan çocuklar için görsel kartlar, vücut dili, arkadaş çevirmenliği
        
        Kültürel Kapsayıcılık:
        Farklı kültürlerden örnekler, evrensel temalar, ailelerden materyal desteği
        
        Sosyal-Duygusal Farklılaştırma:
        Çekingen çocukları cesaretlendirin, hiperaktif çocuklara hareket alanı tanıyın
        
        Çoklu Duyusal Yaklaşım:
        Görsel, işitsel ve dokunsal öğrenme stillerine hitap eden çeşitli aktiviteler
        
        DEĞERLENDİRME:
        
        Program Tarafından:
        • Etkinlik süresi yeterli miydi?
        • Materyaller amaca uygun muydu?
        • Akış düzgün müydü?
        
        Amaçlanan Beceriler Tarafından:
        • Kazanımlar gerçekleşti mi?
        • Hangi beceriler gelişti?
        • Eksik kalan yönler var mı?
        
        Öğrenciler Tarafından:
        • Tüm çocuklar katıldı mı?
        • Kim desteğe ihtiyaç duydu?
        • Bireysel gelişim notları alındı mı?
        """
        
        return prompt
    
    async def generate_activity(self, kazanimlar: List[Dict]) -> Optional[Dict]:
        """Generate an activity based on selected learning outcomes"""
        try:
            prompt = self.create_activity_prompt(kazanimlar)
            
            # Generate content using Vertex AI
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error("Empty response from Vertex AI")
                return None
            
            # Parse the generated text into structured data
            activity_data = self._parse_activity_text(response.text)
            
            # Add metadata
            activity_data['kazanim_idleri'] = [k.get('id') for k in kazanimlar if k.get('id')]
            activity_data['kazanim_metinleri'] = [
                f"{k.get('yas_grubu', '')} - {k.get('ders', '')}: {k.get('ogrenme_ciktilari', '')}"
                for k in kazanimlar
            ]
            activity_data['prompt_used'] = prompt[:1000]  # Store first 1000 chars
            activity_data['ai_generated'] = True
            activity_data['model_version'] = settings.VERTEX_AI_MODEL
            
            logger.info(f"Activity generated successfully: {activity_data.get('etkinlik_adi', 'Unknown')}")
            return activity_data
            
        except Exception as e:
            logger.error(f"Error generating activity: {str(e)}")
            return None
    
    def _parse_activity_text(self, text: str) -> Dict:
        """Parse the generated text into structured data"""
        
        activity = {}
        
        # Section mappings
        sections = {
            'ETKİNLİK ADI': 'etkinlik_adi',
            'ALAN ADI': 'alan_adi',
            'YAŞ GRUBU': 'yas_grubu',
            'SÜRE': 'sure',
            'UYGULAMA YERİ': 'uygulama_yeri',
            'ETKİNLİĞİN AMACI': 'etkinlik_amaci',
            'MATERYALLER': 'materyaller',
            'GİRİŞ': 'giris_bolumu',
            'GELİŞME': 'gelisme_bolumu',
            'YANSIMA ÇEMBERİ': 'yansima_cemberi',
            'SONUÇ': 'sonuc_bolumu',
            'UYARLAMA': 'uyarlama',
            'FARKLILAŞTIRMA VE KAPSAYICILIK': 'farklilastirma_kapsayicilik',
            'Program Değerlendirmesi': 'degerlendirme_program',
            'Kazanım Değerlendirmesi': 'degerlendirme_beceriler',
            'Bireysel Değerlendirme': 'degerlendirme_ogrenciler',
        }
        
        lines = text.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for new section
            section_found = False
            for key, field in sections.items():
                if key in line.upper():
                    # Save previous section
                    if current_section and current_content:
                        content = '\n'.join(current_content)
                        activity[current_section] = content.strip()
                    
                    current_section = field
                    current_content = []
                    
                    # Get content after colon if exists
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1 and parts[1].strip():
                            current_content.append(parts[1].strip())
                    
                    section_found = True
                    break
            
            if not section_found and current_section:
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            content = '\n'.join(current_content)
            activity[current_section] = content.strip()
        
        # Parse duration to integer - ensure it's always an integer
        if 'sure' in activity:
            try:
                import re
                # Try to extract number from string
                numbers = re.findall(r'\d+', str(activity['sure']))
                if numbers:
                    activity['sure'] = int(numbers[0])
                else:
                    activity['sure'] = 30  # Default duration
            except:
                activity['sure'] = 30  # Default duration
        else:
            activity['sure'] = 30  # Default if not provided
        
        # Combine process sections
        process_sections = []
        for key in ['giris_bolumu', 'gelisme_bolumu', 'yansima_cemberi', 'sonuc_bolumu']:
            if key in activity and activity[key]:
                process_sections.append(activity[key])
        
        if process_sections:
            activity['uygulama_sureci'] = '\n\n'.join(process_sections)
        
        return activity

# Singleton instance
vertex_ai_service = VertexAIService()