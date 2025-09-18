#!/bin/bash
# Cloudflare Tunnel kurulum scripti

set -e

echo "Cloudflare Tunnel (cloudflared) kurulumu başlıyor..."

# İşletim sistemini kontrol et
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "macOS tespit edildi..."

    if command -v brew &> /dev/null; then
        echo "Homebrew ile cloudflared yükleniyor..."
        brew install cloudflared
    else
        echo "Homebrew bulunamadı. Manuel kurulum için:"
        echo "1. https://github.com/cloudflare/cloudflared/releases adresinden macOS versiyonunu indirin"
        echo "2. sudo mv cloudflared /usr/local/bin/"
        echo "3. sudo chmod +x /usr/local/bin/cloudflared"
        exit 1
    fi

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Linux tespit edildi..."

    # Architecture kontrolü
    ARCH=$(uname -m)

    if [ "$ARCH" == "x86_64" ]; then
        DOWNLOAD_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    elif [ "$ARCH" == "aarch64" ]; then
        DOWNLOAD_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb"
    else
        echo "Desteklenmeyen mimari: $ARCH"
        exit 1
    fi

    echo "cloudflared indiriliyor..."
    wget -q $DOWNLOAD_URL -O cloudflared.deb

    echo "cloudflared yükleniyor..."
    sudo dpkg -i cloudflared.deb
    rm cloudflared.deb

else
    echo "Desteklenmeyen işletim sistemi: $OSTYPE"
    exit 1
fi

# Kurulum kontrolü
if command -v cloudflared &> /dev/null; then
    echo "✓ cloudflared başarıyla yüklendi!"
    cloudflared --version
else
    echo "✗ cloudflared yüklenemedi!"
    exit 1
fi

echo ""
echo "Sonraki adımlar:"
echo "1. Cloudflare hesabınıza giriş yapın: cloudflared tunnel login"
echo "2. Yeni tünel oluşturun: cloudflared tunnel create edupage"
echo "3. DNS kaydı ekleyin: cloudflared tunnel route dns edupage app.yourdomain.com"
echo "4. config.yml dosyasını düzenleyin ve tüneli başlatın"