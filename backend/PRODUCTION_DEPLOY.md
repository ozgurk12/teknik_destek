# Production Deployment - Video Generation Module

## 1. SSH ile Production Sunucusuna Bağlanın

```bash
ssh your-user@etkinlik.hautmedia.com
```

## 2. Video Images Klasörünü Oluşturun

```bash
# Static klasörüne gidin
cd /var/www/etkinlik.hautmedia.com

# Video images klasörünü oluşturun
sudo mkdir -p static/video-images

# İzinleri ayarlayın (web sunucusu yazabilmeli)
sudo chmod 755 static/video-images

# Sahipliği web sunucu kullanıcısına verin (genellikle www-data veya nginx)
sudo chown -R www-data:www-data static/video-images

# Alternatif: Eğer nginx kullanıyorsanız
# sudo chown -R nginx:nginx static/video-images
```

## 3. Backend'i Production Modunda Çalıştırın

Production sunucusunda backend'i başlatırken environment variable ekleyin:

```bash
# Environment variable ile production modunu aktifleştirin
export ENV=production
# veya
export PRODUCTION=true

# Backend'i başlatın
cd /path/to/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 4. Nginx Konfigürasyonu (Eğer kullanıyorsanız)

`/etc/nginx/sites-available/etkinlik.hautmedia.com` dosyasına ekleyin:

```nginx
# Static files for video images
location /static/video-images/ {
    alias /var/www/etkinlik.hautmedia.com/static/video-images/;
    expires 30d;
    add_header Cache-Control "public, immutable";
    add_header Access-Control-Allow-Origin "*";
}
```

Sonra nginx'i yeniden yükleyin:
```bash
sudo nginx -t  # Konfigürasyonu test et
sudo systemctl reload nginx  # Yeniden yükle
```

## 5. Test Edin

```bash
# Klasörün var olduğunu kontrol edin
ls -la /var/www/etkinlik.hautmedia.com/static/video-images/

# Test dosyası oluşturun
echo "test" | sudo tee /var/www/etkinlik.hautmedia.com/static/video-images/test.txt

# Browser'dan test edin
# https://etkinlik.hautmedia.com/static/video-images/test.txt
```

## 6. Webhook URL'ini Ayarlayın

Production'da webhook URL'ini environment variable olarak ayarlayın:

```bash
export VIDEO_GENERATION_WEBHOOK_URL="http://your-webhook-url"
```

## Notlar

- Görseller hem local'de base64 olarak hem de production URL'i olarak webhook'a gönderilir
- Production'da `ENV=production` ayarlandığında görseller direkt `/var/www/etkinlik.hautmedia.com/static/video-images/` klasörüne kaydedilir
- Development'ta görseller temp klasöre kaydedilir ama URL'ler production'ı gösterir