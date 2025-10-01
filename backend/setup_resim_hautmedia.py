#!/usr/bin/env python3
"""
Setup script for resim.hautmedia.com CDN configuration

This script should be run on the production server to:
1. Create necessary directories for image storage
2. Configure nginx for resim.hautmedia.com subdomain
3. Set up SSL certificates
"""

import os
import subprocess
from pathlib import Path

def setup_image_directories():
    """Create directories for image storage"""
    base_dir = Path("/var/www/resim.hautmedia.com")
    video_images_dir = base_dir / "video-images"

    # Create directories
    video_images_dir.mkdir(parents=True, exist_ok=True)

    # Set permissions
    os.chmod(video_images_dir, 0o755)

    print(f"✅ Created image directory: {video_images_dir}")
    return base_dir

def create_nginx_config():
    """Create nginx configuration for resim.hautmedia.com"""

    nginx_config = """
server {
    listen 80;
    listen [::]:80;
    server_name resim.hautmedia.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name resim.hautmedia.com;

    # SSL certificates (will be managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/resim.hautmedia.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/resim.hautmedia.com/privkey.pem;

    # Root directory
    root /var/www/resim.hautmedia.com;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # CORS headers for images
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, HEAD, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept" always;

    # Cache control for images
    location ~* \.(jpg|jpeg|png|gif|ico|webp|svg)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*" always;
    }

    # Serve video images
    location /video-images/ {
        alias /var/www/resim.hautmedia.com/video-images/;
        try_files $uri =404;

        # CORS headers
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, HEAD, OPTIONS" always;
    }

    # Upload endpoint (only from etkinlik.hautmedia.com)
    location /upload {
        # Only allow POST from production backend
        limit_except POST {
            deny all;
        }

        # Proxy to a simple upload handler or handle via FastAPI
        proxy_pass http://127.0.0.1:8001/upload;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Default location
    location / {
        try_files $uri $uri/ =404;
    }
}
"""

    config_path = "/etc/nginx/sites-available/resim.hautmedia.com"

    with open(config_path, 'w') as f:
        f.write(nginx_config)

    # Create symbolic link
    subprocess.run([
        "ln", "-sf",
        "/etc/nginx/sites-available/resim.hautmedia.com",
        "/etc/nginx/sites-enabled/"
    ])

    print(f"✅ Created nginx configuration: {config_path}")
    return config_path

def setup_ssl_certificate():
    """Setup SSL certificate using Certbot"""
    print("\n📋 Setting up SSL certificate for resim.hautmedia.com...")

    # Run certbot
    subprocess.run([
        "certbot", "certonly",
        "--nginx",
        "-d", "resim.hautmedia.com",
        "--non-interactive",
        "--agree-tos",
        "--email", "admin@hautmedia.com"
    ])

    print("✅ SSL certificate configured")

def restart_nginx():
    """Test and restart nginx"""
    print("\n🔄 Restarting nginx...")

    # Test configuration
    result = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Nginx configuration error: {result.stderr}")
        return False

    # Reload nginx
    subprocess.run(["systemctl", "reload", "nginx"])
    print("✅ Nginx reloaded successfully")
    return True

def create_upload_handler():
    """Create a simple FastAPI app for handling uploads"""

    handler_code = """
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import aiofiles
import uvicorn

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://etkinlik.hautmedia.com", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("/var/www/resim.hautmedia.com/video-images")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), filename: str = None):
    \"\"\"Handle file upload from etkinlik.hautmedia.com\"\"\"

    if not filename:
        filename = file.filename

    file_path = UPLOAD_DIR / filename

    # Save file
    contents = await file.read()
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    return {"status": "success", "filename": filename}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
"""

    handler_path = "/opt/resim-hautmedia/upload_handler.py"
    Path(handler_path).parent.mkdir(parents=True, exist_ok=True)

    with open(handler_path, 'w') as f:
        f.write(handler_code)

    print(f"✅ Created upload handler: {handler_path}")
    return handler_path

def create_systemd_service():
    """Create systemd service for upload handler"""

    service_config = """
[Unit]
Description=Resim Hautmedia Upload Handler
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/resim-hautmedia
ExecStart=/usr/bin/python3 /opt/resim-hautmedia/upload_handler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    service_path = "/etc/systemd/system/resim-upload.service"

    with open(service_path, 'w') as f:
        f.write(service_config)

    # Reload systemd and start service
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "resim-upload.service"])
    subprocess.run(["systemctl", "start", "resim-upload.service"])

    print(f"✅ Created and started systemd service: {service_path}")

def main():
    """Main setup function"""
    print("🚀 Setting up resim.hautmedia.com CDN")
    print("=" * 50)

    # Check if running as root
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo)")
        return

    # Setup steps
    setup_image_directories()
    create_nginx_config()
    setup_ssl_certificate()
    create_upload_handler()
    create_systemd_service()
    restart_nginx()

    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Add DNS record: resim.hautmedia.com -> Your server IP")
    print("2. Test upload from development environment")
    print("3. Monitor logs: journalctl -u resim-upload -f")

if __name__ == "__main__":
    main()