# Cloudflare Tunnel ile Localhost'tan Yayın

Bu kılavuz, EduPage Kids frontend uygulamasını localhost'tan Cloudflare Tunnel ile güvenli şekilde internete açmayı anlatır.

## 🎯 Neden Cloudflare Tunnel?

- **Port açmaya gerek yok**: Router/firewall ayarı gerekmez
- **Otomatik HTTPS**: SSL sertifikası otomatik
- **DDoS koruması**: Cloudflare altyapısı
- **Ücretsiz**: Free plan yeterli
- **Kolay kurulum**: 5 dakikada hazır

## 📋 Gereksinimler

- Cloudflare hesabı (ücretsiz)
- Domain (Cloudflare'da yönetilen)
- macOS veya Linux
- Backend localhost:8000'de çalışıyor
- Frontend localhost:8501'de çalışacak

## 🚀 Hızlı Kurulum

### 1. Cloudflared Kurulumu

```bash
cd cloudflare
chmod +x install-cloudflared.sh
./install-cloudflared.sh
```

### 2. Tunnel Oluşturma

```bash
chmod +x setup-tunnel.sh
./setup-tunnel.sh
```

Script sizden domain adınızı isteyecek ve otomatik olarak:
- Cloudflare'a giriş yapacak
- Tunnel oluşturacak
- DNS kaydı ekleyecek
- Config dosyasını oluşturacak

### 3. Frontend'i Başlatma

```bash
chmod +x run-frontend-tunnel.sh
./run-frontend-tunnel.sh
```

Bu script:
- Backend kontrolü yapar
- Frontend'i başlatır (Streamlit)
- Cloudflare Tunnel'ı başlatır
- Her iki servisi de izler

## 📖 Manuel Kurulum

### Adım 1: Cloudflared Kurulumu

**macOS:**
```bash
brew install cloudflared
```

**Linux:**
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

### Adım 2: Cloudflare Giriş
```bash
cloudflared tunnel login
```
Browser açılacak, Cloudflare hesabınıza giriş yapın.

### Adım 3: Tunnel Oluşturma
```bash
cloudflared tunnel create edupage
```

### Adım 4: DNS Kaydı
```bash
cloudflared tunnel route dns edupage edupage.yourdomain.com
```

### Adım 5: Config Dosyası

`~/.cloudflared/config.yml` dosyasını oluşturun:

```yaml
tunnel: <TUNNEL-ID>
credentials-file: /Users/<USER>/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: edupage.yourdomain.com
    service: http://localhost:8501
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s

  - service: http_status:404
```

### Adım 6: Tunnel'ı Başlatma
```bash
cloudflared tunnel run edupage
```

## 🔧 VPN Split-Tunnel Ayarları

Backend'in VPN üzerinden veritabanına erişmesi için:

### WireGuard
```conf
[Interface]
PrivateKey = <your-key>
Address = 10.0.0.2/32

[Peer]
PublicKey = <server-key>
Endpoint = vpn.company.com:51820
AllowedIPs = 10.0.0.0/24  # Sadece DB subnet
```

### OpenVPN
```bash
# .ovpn dosyasına ekle:
pull-filter ignore "redirect-gateway"
route 10.0.0.0 255.255.255.0
```

## 🖥️ Sistemd Service (Linux)

Kalıcı servis için:

```bash
sudo cloudflared service install
sudo systemctl start cloudflared
sudo systemctl enable cloudflared
```

## 🔍 Test ve Debug

### Tunnel Durumu
```bash
cloudflared tunnel list
cloudflared tunnel info edupage
```

### Log İzleme
```bash
cloudflared tunnel run edupage --loglevel debug
```

### DNS Kontrolü
```bash
dig edupage.yourdomain.com
nslookup edupage.yourdomain.com
```

## 🛡️ Güvenlik

### Cloudflare Access (Opsiyonel)
Dashboard'dan Access politikası ekleyerek kimlik doğrulama ekleyebilirsiniz:
1. Zero Trust → Access → Applications
2. Add an application
3. Self-hosted
4. Application domain: edupage.yourdomain.com
5. Policy ekle (email, IP range, vs.)

### Rate Limiting
Dashboard'dan rate limiting ekleyin:
1. Security → WAF → Rate limiting rules
2. Create rule
3. Path: /*
4. Requests: 100 per minute

## 🔄 Güncelleme

Frontend güncellemesi için:
```bash
# Frontend'i durdur
pkill -f streamlit

# Kodu güncelle
git pull

# Yeniden başlat
./run-frontend-tunnel.sh
```

## ❌ Sorun Giderme

### "Tunnel already exists"
```bash
cloudflared tunnel delete edupage
cloudflared tunnel create edupage
```

### "DNS record already exists"
Cloudflare Dashboard → DNS → İlgili kaydı sil

### "Connection refused"
- Frontend'in çalıştığını kontrol et: `curl http://localhost:8501`
- Backend'in çalıştığını kontrol et: `curl http://localhost:8000/health`

### WebSocket Hatası
Config'de `originRequest` altına ekle:
```yaml
httpHostHeader: "edupage.yourdomain.com"
originServerName: "edupage.yourdomain.com"
```

## 📊 Monitoring

### Cloudflare Analytics
Dashboard → Analytics → Web Analytics'ten trafik izleyin

### Tunnel Metrics
```bash
cloudflared tunnel metrics edupage
```

## 🎯 Özet Komutlar

```bash
# Kurulum
cd cloudflare
./setup-tunnel.sh

# Başlatma
./run-frontend-tunnel.sh

# Durdurma
pkill -f cloudflared
pkill -f streamlit

# Status
ps aux | grep -E "cloudflared|streamlit"

# Logs
tail -f ~/.cloudflared/logs/*
```

## 📝 Notlar

- Tunnel ID'yi kaydedin (backup için)
- Credentials dosyasını yedekleyin: `~/.cloudflared/*.json`
- Free plan'da 100k request/day limiti var (yeterli)
- Laptop kapanırsa servis durur (production için VPS önerilir)