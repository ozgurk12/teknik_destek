import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def create_activities_table():
    """Etkinlikler tablosunu oluşturur"""
    
    try:
        # PostgreSQL bağlantısı
        conn = psycopg2.connect(
            host=os.getenv('POSTGRE_HOST'),
            port=os.getenv('POSTGRE_PORT'),
            user=os.getenv('POSTGRE_USER'),
            password=os.getenv('POSTGRE_PASSWORD'),
            database=os.getenv('POSTGRE_DATABASE')
        )
        cursor = conn.cursor()
        
        # Etkinlikler tablosunu oluştur
        create_table_query = """
        CREATE TABLE IF NOT EXISTS etkinlikler (
            id SERIAL PRIMARY KEY,
            etkinlik_adi VARCHAR(255) NOT NULL,
            alan_adi VARCHAR(100),
            yas_grubu VARCHAR(20),
            sure INTEGER, -- dakika cinsinden
            uygulama_yeri VARCHAR(100),
            
            -- Etkinlik detayları
            etkinlik_amaci TEXT,
            materyaller TEXT,
            uygulama_sureci TEXT,
            giris_bolumu TEXT,
            gelisme_bolumu TEXT,
            yansima_cemberi TEXT,
            sonuc_bolumu TEXT,
            
            -- Uyarlama ve farklılaştırma
            uyarlama TEXT,
            farklilastirma_kapsayicilik TEXT,
            
            -- Değerlendirme
            degerlendirme_program TEXT,
            degerlendirme_beceriler TEXT,
            degerlendirme_ogrenciler TEXT,
            
            -- İlişkili kazanımlar (JSON array olarak)
            kazanim_idleri INTEGER[],
            kazanim_metinleri TEXT[],
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(100),
            ai_generated BOOLEAN DEFAULT TRUE,
            prompt_used TEXT,
            model_version VARCHAR(50) DEFAULT 'gemini-2.5-flash'
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✅ etkinlikler tablosu oluşturuldu")
        
        # İndeksler ekle
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_etkinlik_alan ON etkinlikler(alan_adi);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_etkinlik_yas ON etkinlikler(yas_grubu);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_etkinlik_kazanim ON etkinlikler USING GIN(kazanim_idleri);")
        conn.commit()
        print("✅ İndeksler oluşturuldu")
        
        # Tablo yapısını göster
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = 'etkinlikler'
            ORDER BY ordinal_position;
        """)
        
        print("\n📋 ETKİNLİKLER TABLOSU YAPISI:")
        print("-" * 60)
        for row in cursor.fetchall():
            col_name, data_type, max_length = row
            if max_length:
                print(f"  • {col_name}: {data_type}({max_length})")
            else:
                print(f"  • {col_name}: {data_type}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Etkinlikler tablosu başarıyla oluşturuldu!")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    create_activities_table()