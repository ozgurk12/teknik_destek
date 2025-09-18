#!/bin/bash
# Cloudflare Tunnel kurulum ve yapılandırma

set -e

echo "==================================="
echo "EduPage Kids - Cloudflare Tunnel Setup"
echo "==================================="

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Domain sabit olarak hautmedia.com
DOMAIN="hautmedia.com"
echo "Domain: $DOMAIN"

# cloudflared kontrolü
if ! command -v cloudflared &> /dev/null; then
    echo -e "${YELLOW}cloudflared bulunamadı. Yükleniyor...${NC}"
    chmod +x install-cloudflared.sh
    ./install-cloudflared.sh
fi

echo -e "${GREEN}1. Cloudflare hesabına giriş yapılıyor...${NC}"
cloudflared tunnel login

echo -e "${GREEN}2. Tunnel oluşturuluyor...${NC}"
cloudflared tunnel create edupage

echo -e "${GREEN}3. DNS kaydı ekleniyor...${NC}"
cloudflared tunnel route dns edupage etkinlik.$DOMAIN

echo -e "${GREEN}4. Tunnel ID alınıyor...${NC}"
TUNNEL_ID=$(cloudflared tunnel list | grep edupage | awk '{print $1}')

if [ -z "$TUNNEL_ID" ]; then
    echo -e "${RED}Tunnel ID bulunamadı!${NC}"
    exit 1
fi

echo "Tunnel ID: $TUNNEL_ID"

echo -e "${GREEN}5. Config dosyası oluşturuluyor...${NC}"

# Config dosyasını güncelle
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: /Users/$USER/.cloudflared/$TUNNEL_ID.json

ingress:
  # Frontend Application
  - hostname: etkinlik.$DOMAIN
    service: http://localhost:3001
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      httpHostHeader: "etkinlik.$DOMAIN"
      # WebSocket support
      originServerName: "etkinlik.$DOMAIN"

  # 404 catch-all
  - service: http_status:404

# Tunnel settings
originRequest:
  connectTimeout: 30s
  tlsTimeout: 30s
  tcpKeepAlive: 30s
  keepAliveConnections: 4
  keepAliveTimeout: 90s

retries: 5
grace-period: 30s
loglevel: info
EOF

echo -e "${GREEN}6. Tunnel test ediliyor...${NC}"
cloudflared tunnel run edupage &
TUNNEL_PID=$!

sleep 5

if ps -p $TUNNEL_PID > /dev/null; then
    echo -e "${GREEN}✓ Tunnel başarıyla çalışıyor!${NC}"
    kill $TUNNEL_PID
else
    echo -e "${RED}✗ Tunnel başlatılamadı!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Kurulum Tamamlandı ===${NC}"
echo ""
echo "Frontend'i başlatmak için:"
echo "  cd frontend"
echo "  streamlit run streamlit_app.py"
echo ""
echo "Tunnel'ı başlatmak için:"
echo "  cloudflared tunnel run edupage"
echo ""
echo "Erişim adresi:"
echo "  https://etkinlik.$DOMAIN"
echo ""
echo "Kalıcı servis için (systemd):"
echo "  sudo cloudflared service install"
echo "  sudo systemctl start cloudflared"
echo "  sudo systemctl enable cloudflared"