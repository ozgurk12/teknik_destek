#!/bin/bash
# Frontend ve Backend Cloudflare Tunnel'larını başlatma scripti

echo "======================================"
echo "EduPage Kids - Cloudflare Tunnels"
echo "======================================"

# Backend'i başlat
echo "1. Backend başlatılıyor (Port 8000)..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Frontend'i başlat
echo "2. Frontend başlatılıyor (Port 3001)..."
cd ../frontend/edupage-kids-app
npm run dev &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

# Biraz bekle servislerin başlaması için
sleep 5

# Backend Tunnel'ı başlat
echo "3. Backend Cloudflare Tunnel başlatılıyor..."
cloudflared tunnel --config ~/.cloudflared/backend-config.yml run edupage-backend &
BACKEND_TUNNEL_PID=$!
echo "   Backend Tunnel PID: $BACKEND_TUNNEL_PID"

# Frontend Tunnel'ı başlat
echo "4. Frontend Cloudflare Tunnel başlatılıyor..."
cloudflared tunnel run edupage &
FRONTEND_TUNNEL_PID=$!
echo "   Frontend Tunnel PID: $FRONTEND_TUNNEL_PID"

echo ""
echo "✓ Tüm servisler başlatıldı!"
echo ""
echo "Erişim adresleri:"
echo "  Frontend: https://etkinlik.hautmedia.com"
echo "  Backend API: https://api-etkinlik.hautmedia.com"
echo ""
echo "Servisleri durdurmak için: Ctrl+C"
echo ""

# Ctrl+C ile durdurmak için bekle
trap "echo 'Servisler durduruluyor...'; kill $BACKEND_PID $FRONTEND_PID $BACKEND_TUNNEL_PID $FRONTEND_TUNNEL_PID 2>/dev/null; exit" INT

# Sürekli çalışır durumda tut
wait