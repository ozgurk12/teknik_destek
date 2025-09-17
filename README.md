# EduPage Kids Activity Generator

Maarif Model Okul Öncesi kazanımlarına uygun etkinlik planlama sistemi. Google Vertex AI kullanarak otomatik etkinlik oluşturur.

## 🚀 Özellikler

- ✅ Maarif Model kazanımları veritabanı
- 🤖 Vertex AI ile otomatik etkinlik oluşturma
- 🎨 Modern web arayüzü (Streamlit)
- 📊 FastAPI REST API
- 🐳 Docker desteği
- 📈 İstatistik ve raporlama

## 📋 Gereksinimler

- Python 3.11+
- PostgreSQL
- Google Cloud Project (Vertex AI için)
- Docker & Docker Compose (opsiyonel)

## 🛠️ Kurulum

### 1. Repository'yi klonlayın
```bash
git clone <repo-url>
cd "Etkinlik ve Günlük Plan"
```

### 2. Virtual environment oluşturun
```bash
python3 -m venv venv
source venv/bin/activate  # MacOS/Linux
```

### 3. Backend kurulumu
```bash
cd backend
pip install -r requirements.txt

# .env dosyasını düzenleyin
cp .env.example .env
# VERTEX_AI_PROJECT_ID'yi güncelleyin
```

### 4. Veritabanı kurulumu
```bash
# PostgreSQL'de edupage_kids veritabanını oluşturun
python ../setup_database.py
python ../import_csv_to_db.py
```

### 5. Backend'i başlatın
```bash
uvicorn app.main:app --reload
```

### 6. Frontend kurulumu (yeni terminal)
```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 🐳 Docker ile Çalıştırma

```bash
# .env dosyasını düzenleyin
docker-compose up --build
```

Servisler:
- Backend: http://localhost:8000
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/api/v1/docs

## 📁 Proje Yapısı

```
.
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Yapılandırma
│   │   ├── db/           # Veritabanı
│   │   ├── models/       # SQLAlchemy modeller
│   │   ├── schemas/      # Pydantic şemalar
│   │   └── services/     # Vertex AI servisi
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py  # Web arayüzü
│   └── requirements.txt
├── credentials/           # Google service account
└── docker-compose.yml
```

## 🔑 Vertex AI Yapılandırması

1. Google Cloud Console'dan yeni proje oluşturun
2. Vertex AI API'yi etkinleştirin
3. Service Account oluşturun ve JSON key'i indirin
4. JSON dosyasını `credentials/google-service-account.json` olarak kaydedin
5. `.env` dosyasında `VERTEX_AI_PROJECT_ID`'yi güncelleyin

## 📝 API Kullanımı

### Kazanımları Listele
```bash
GET /api/v1/kazanimlar?yas_grubu=36-48&ders=TÜRKÇE
```

### Etkinlik Oluştur
```bash
POST /api/v1/etkinlikler/generate
{
  "kazanim_ids": [1, 2, 3]
}
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'e push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.