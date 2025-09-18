#!/bin/bash
# Hızlı Cloudflare Tunnel kurulumu - hautmedia.com için

set -e

echo "======================================"
echo "EduPage Kids - Cloudflare Tunnel Setup"
echo "Domain: etkinlik.hautmedia.com"
echo "Port: 3001"
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

echo "2. Tunnel oluşturuluyor..."
cloudflared tunnel create edupage || echo "Tunnel zaten var"

echo "3. DNS kaydı ekleniyor..."
cloudflared tunnel route dns edupage etkinlik.hautmedia.com || echo "DNS kaydı zaten var"

echo "4. Config dosyası oluşturuluyor..."
TUNNEL_ID=$(cloudflared tunnel list | grep edupage | awk '{print $1}')

cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: /Users/$USER/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: etkinlik.hautmedia.com
    service: http://localhost:3001
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      httpHostHeader: "etkinlik.hautmedia.com"
      originServerName: "etkinlik.hautmedia.com"

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
echo "✓ Kurulum tamamlandı!"
echo ""
echo "Frontend'i başlatmak için:"
echo "  cd frontend/edupage-kids-app"
echo "  npm install  # İlk kurulumda"
echo "  npm run dev  # Port 3001'de başlayacak"
echo ""
echo "Tunnel'ı başlatmak için:"
echo "  cloudflared tunnel run edupage"
echo ""
echo "Erişim adresi: https://etkinlik.hautmedia.com"