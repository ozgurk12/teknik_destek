#!/bin/bash
# Backend için Cloudflare Tunnel kurulumu

set -e

echo "======================================"
echo "EduPage Kids Backend - Cloudflare Tunnel Setup"
echo "Domain: api-etkinlik.hautmedia.com"
echo "Port: 8000"
echo "======================================"

# cloudflared kontrolü
if ! command -v cloudflared &> /dev/null; then
    echo "cloudflared bulunamadı. Yükleniyor..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install cloudflared
    else
        wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
        sudo dpkg -i cloudflared-linux-amd64.deb
        rm cloudflared-linux-amd64.deb
    fi
fi

echo "1. Cloudflare hesabına giriş yapılıyor..."
cloudflared tunnel login

echo "2. Backend tunnel oluşturuluyor..."
cloudflared tunnel create edupage-backend || echo "Tunnel zaten var"

echo "3. DNS kaydı ekleniyor..."
cloudflared tunnel route dns edupage-backend api-etkinlik.hautmedia.com || echo "DNS kaydı zaten var"

echo "4. Config dosyası oluşturuluyor..."
TUNNEL_ID=$(cloudflared tunnel list | grep edupage-backend | awk '{print $1}')

cat > ~/.cloudflared/backend-config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: /Users/$USER/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: api-etkinlik.hautmedia.com
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      httpHostHeader: "api-etkinlik.hautmedia.com"
      originServerName: "api-etkinlik.hautmedia.com"

  - service: http_status:404

originRequest:
  connectTimeout: 30s
  tlsTimeout: 30s
  tcpKeepAlive: 30s
  keepAliveConnections: 4
  keepAliveTimeout: 90s

retries: 5
loglevel: info
EOF

echo ""
echo "✓ Backend tunnel kurulumu tamamlandı!"
echo ""
echo "Backend'i başlatmak için:"
echo "  cd backend"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Backend Tunnel'ı başlatmak için:"
echo "  cloudflared tunnel --config ~/.cloudflared/backend-config.yml run edupage-backend"
echo ""
echo "Backend API adresi: https://api-etkinlik.hautmedia.com"
echo ""
echo "ÖNEMLİ: Frontend .env dosyasını güncellemeyi unutmayın:"
echo "  REACT_APP_API_URL=https://api-etkinlik.hautmedia.com/api/v1"