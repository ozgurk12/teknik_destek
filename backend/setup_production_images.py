#!/usr/bin/env python3
"""
Production sunucusunda video-images klasörünü oluşturur
Bu scripti production sunucusunda çalıştırın
"""
import os
import subprocess
from pathlib import Path

def setup_video_images_directory():
    """Setup video-images directory on production server"""

    # Directory path
    base_dir = Path("/var/www/etkinlik.hautmedia.com")
    static_dir = base_dir / "static"
    video_images_dir = static_dir / "video-images"

    try:
        # Create directories if they don't exist
        print(f"Creating directory: {video_images_dir}")
        video_images_dir.mkdir(parents=True, exist_ok=True)

        # Set permissions (755 for directories, www-data ownership)
        print("Setting permissions...")
        subprocess.run(["sudo", "chmod", "755", str(static_dir)], check=True)
        subprocess.run(["sudo", "chmod", "755", str(video_images_dir)], check=True)

        # Set ownership to www-data (web server user)
        print("Setting ownership to www-data...")
        subprocess.run(["sudo", "chown", "-R", "www-data:www-data", str(video_images_dir)], check=True)

        # Create .htaccess to allow direct access to images
        htaccess_content = """# Allow direct access to images
Options -Indexes
<FilesMatch "\.(jpg|jpeg|png|gif|webp)$">
    Header set Access-Control-Allow-Origin "*"
    Header set Cache-Control "public, max-age=31536000"
</FilesMatch>
"""
        htaccess_path = video_images_dir / ".htaccess"
        with open(htaccess_path, 'w') as f:
            f.write(htaccess_content)

        print(f"✅ Directory created successfully: {video_images_dir}")
        print("✅ Permissions set to 755")
        print("✅ Ownership set to www-data")
        print("✅ .htaccess file created")

        # Test write access
        test_file = video_images_dir / "test.txt"
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("✅ Write test successful")
        except Exception as e:
            print(f"⚠️ Write test failed: {e}")
            print("You may need to adjust permissions")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease run this script with sudo:")
        print("sudo python3 setup_production_images.py")

if __name__ == "__main__":
    setup_video_images_directory()