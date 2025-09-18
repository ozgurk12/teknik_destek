#!/bin/bash
# Frontend ve Cloudflare Tunnel'ı birlikte başlat

set -e

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}EduPage Kids - Frontend Başlatılıyor${NC}"
echo "======================================"

# Backend'in çalışıp çalışmadığını kontrol et
if curl -f http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✓ Backend zaten çalışıyor${NC}"
else
    echo -e "${YELLOW}⚠ Backend çalışmıyor. Backend'i başlatın:${NC}"
    echo "  cd backend"
    echo "  uvicorn app.main:app --reload"
    echo ""
    read -p "Backend başlatıldıysa devam etmek için Enter'a basın..."
fi

# Frontend'i başlat
echo -e "${GREEN}Frontend başlatılıyor (port 3001)...${NC}"
cd ../frontend

# Frontend'i port 3001'de başlat (Next.js, React vb. için)
# Eğer Streamlit kullanıyorsanız: streamlit run streamlit_app.py --server.port 3001 &
# React/Next.js için: npm start veya npm run dev (package.json'da port 3001 olarak ayarlanmalı)

# Next.js/React için (edupage-kids-app dizininde)
if [ -d "edupage-kids-app" ]; then
    cd edupage-kids-app
    npm run dev &  # Port 3001'de başlayacak şekilde ayarlanmış olmalı
    FRONTEND_PID=$!
else
    # Streamlit için
    streamlit run streamlit_app.py --server.port 3001 &
    FRONTEND_PID=$!
fi

# Frontend'in başlamasını bekle
echo "Frontend başlatılıyor..."
sleep 8

# Frontend kontrolü
if curl -f http://localhost:3001 &> /dev/null; then
    echo -e "${GREEN}✓ Frontend başarıyla başlatıldı port 3001'de (PID: $FRONTEND_PID)${NC}"
else
    echo -e "${RED}✗ Frontend başlatılamadı${NC}"
    exit 1
fi

# Cloudflare Tunnel'ı başlat
echo -e "${GREEN}Cloudflare Tunnel başlatılıyor...${NC}"
cd ../cloudflare

if [ -f ~/.cloudflared/config.yml ]; then
    cloudflared tunnel run edupage &
    TUNNEL_PID=$!

    echo -e "${GREEN}✓ Tunnel başlatıldı (PID: $TUNNEL_PID)${NC}"
else
    echo -e "${RED}Config dosyası bulunamadı! Önce setup-tunnel.sh çalıştırın.${NC}"
    kill $FRONTEND_PID
    exit 1
fi

echo ""
echo -e "${GREEN}=== Servisler Başlatıldı ===${NC}"
echo ""
echo "Frontend PID: $FRONTEND_PID"
echo "Tunnel PID: $TUNNEL_PID"
echo ""
echo "Durdurmak için:"
echo "  kill $FRONTEND_PID $TUNNEL_PID"
echo ""
echo "veya Ctrl+C basın"
echo ""

# Servisleri izle
trap "echo 'Durduruluyor...'; kill $FRONTEND_PID $TUNNEL_PID; exit" INT TERM

# Servisleri canlı tut
while true; do
    if ! ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${RED}Frontend durdu!${NC}"
        kill $TUNNEL_PID
        exit 1
    fi

    if ! ps -p $TUNNEL_PID > /dev/null; then
        echo -e "${RED}Tunnel durdu!${NC}"
        kill $FRONTEND_PID
        exit 1
    fi

    sleep 5
done