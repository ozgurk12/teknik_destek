# EduPage Kids - Deployment Kılavuzu

## 🚀 Hızlı Başlangıç

### 1. Backend Kurulumu

#### Gereksinimler
- Python 3.9+
- PostgreSQL 13+
- Vertex AI API erişimi (opsiyonel)

#### Adımlar

```bash
# 1. Backend dizinine gidin
cd backend

# 2. Virtual environment oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. .env dosyası oluşturun
cp .env.example .env

# 5. .env dosyasını düzenleyin
# Aşağıdaki değerleri doldurun:
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=edupage_kids

# 6. Veritabanı tablolarını oluşturun
python init_user_system.py

# 7. Backend'i başlatın
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Kurulumu

```bash
# 1. Frontend dizinine gidin
cd frontend/edupage-kids-app

# 2. Bağımlılıkları yükleyin
npm install

# 3. .env dosyasını düzenleyin
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env

# 4. Uygulamayı başlatın
npm start
```

## ☁️ Cloudflare Pages Deployment

### Frontend Deployment

#### Otomatik Deployment (GitHub Integration)

1. **GitHub'a Push**
```bash
git add .
git commit -m "Deploy to Cloudflare"
git push origin main
```

2. **Cloudflare Pages Kurulumu**
- [Cloudflare Dashboard](https://dash.cloudflare.com)'a gidin
- Pages > Create a project
- GitHub hesabınızı bağlayın
- Repo seçin: `edupage-kids-app`
- Build ayarları:
  - Build command: `npm run build`
  - Build output directory: `build`
  - Environment variables:
    - `REACT_APP_API_URL`: `https://your-api-domain.com/api/v1`

#### Manuel Deployment

```bash
# 1. Wrangler CLI yükleyin
npm install -g wrangler

# 2. Cloudflare'a login olun
wrangler login

# 3. Build ve deploy
cd frontend/edupage-kids-app
npm run deploy

# Veya preview için:
npm run preview
```

### Backend Deployment (VPS/Cloud)

#### Docker ile Deployment

```bash
# 1. Docker image oluşturun
cd backend
docker build -t edupage-backend .

# 2. Container'ı çalıştırın
docker run -d \
  --name edupage-backend \
  -p 8000:8000 \
  --env-file .env \
  edupage-backend
```

#### Systemd Service (Linux)

```bash
# 1. Service dosyası oluşturun
sudo nano /etc/systemd/system/edupage-backend.service
```

```ini
[Unit]
Description=EduPage Kids Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/edupage-backend
Environment="PATH=/opt/edupage-backend/venv/bin"
ExecStart=/opt/edupage-backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Service'i başlatın
sudo systemctl daemon-reload
sudo systemctl enable edupage-backend
sudo systemctl start edupage-backend
```

## 🔒 Güvenlik Ayarları

### HTTPS Kurulumu (Nginx + Certbot)

```nginx
# /etc/nginx/sites-available/edupage-backend
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment Variables

#### Production .env (Backend)
```env
# Database
POSTGRES_HOST=your-db-host
POSTGRES_PORT=5432
POSTGRES_USER=edupage_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=edupage_production

# Security
SECRET_KEY=generate-a-secure-random-key
DEBUG=False

# Google Cloud (opsiyonel)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=europe-west1
```

#### Production .env (Frontend)
```env
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
REACT_APP_ENV=production
```

## 📊 Monitoring & Logging

### Backend Logging

```python
# Backend'e Sentry ekleyin (opsiyonel)
pip install sentry-sdk[fastapi]

# main.py'de:
import sentry_sdk
sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production"
)
```

### Cloudflare Analytics

Frontend otomatik olarak Cloudflare Web Analytics kullanır.

## 🔄 CI/CD Pipeline (GitHub Actions)

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend/edupage-kids-app
          npm ci

      - name: Build
        run: |
          cd frontend/edupage-kids-app
          npm run build
        env:
          REACT_APP_API_URL: ${{ secrets.API_URL }}

      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: edupage-kids-app
          directory: frontend/edupage-kids-app/build
```

## 🐛 Troubleshooting

### Yaygın Hatalar ve Çözümleri

1. **CORS Hatası**
   - Backend'de `BACKEND_CORS_ORIGINS` ayarını kontrol edin
   - Frontend domain'ini eklediğinizden emin olun

2. **401 Unauthorized**
   - Token'ın expired olmadığını kontrol edin
   - Backend'in çalıştığından emin olun

3. **Database Connection Error**
   - PostgreSQL servisinin çalıştığını kontrol edin
   - .env dosyasındaki credentials'ları doğrulayın

4. **Cloudflare 522 Error**
   - Backend server'ın çalıştığını kontrol edin
   - Firewall ayarlarını gözden geçirin

## 📝 Deployment Checklist

- [ ] Backend .env dosyası production ayarlarıyla güncellendi
- [ ] Frontend .env dosyası production API URL'i ile güncellendi
- [ ] PostgreSQL veritabanı oluşturuldu
- [ ] User tabloları migrate edildi (`python init_user_system.py`)
- [ ] İlk admin kullanıcı şifresi değiştirildi
- [ ] HTTPS sertifikası kuruldu
- [ ] CORS ayarları production domain'leri içeriyor
- [ ] Firewall kuralları ayarlandı (port 443, 80)
- [ ] Backup stratejisi belirlendi
- [ ] Monitoring kuruldu

## 🆘 Destek

Sorun yaşarsanız:
1. Logs'ları kontrol edin: `sudo journalctl -u edupage-backend -f`
2. GitHub Issues'a bakın
3. Dokümantasyonu gözden geçirin