#!/bin/bash
# Cloudflare Tunnel sorun giderme scripti

echo "Cloudflare Tunnel Sorun Giderme"
echo "================================"

# Tunnel durumunu kontrol et
echo "1. Mevcut tunnel'ları kontrol ediliyor..."
cloudflared tunnel list

echo ""
echo "2. Tunnel çalışıyor mu?"
ps aux | grep cloudflared

echo ""
echo "3. DNS kayıtlarını kontrol et:"
cloudflared tunnel route list

echo ""
echo "4. Config dosyası var mı?"
if [ -f ~/.cloudflared/config.yml ]; then
    echo "Config dosyası mevcut:"
    cat ~/.cloudflared/config.yml
else
    echo "Config dosyası bulunamadı!"
fi

echo ""
echo "5. Frontend çalışıyor mu?"
curl -I http://localhost:3001 2>/dev/null | head -n 1

echo ""
echo "Çözüm önerileri:"
echo "----------------"
echo "1. Tunnel'ı yeniden oluştur:"
echo "   cloudflared tunnel delete edupage"
echo "   cloudflared tunnel create edupage"
echo ""
echo "2. DNS kaydını yeniden ekle:"
echo "   cloudflared tunnel route dns edupage etkinlik.hautmedia.com"
echo ""
echo "3. Frontend'i başlat:"
echo "   cd ../frontend/edupage-kids-app"
echo "   npm run dev"
echo ""
echo "4. Tunnel'ı başlat:"
echo "   cloudflared tunnel run edupage"