cl# Kullanıcı Yönetim Sistemi Kılavuzu

## Genel Bakış

EduPage Kids uygulaması için 3 seviyeli rol tabanlı kullanıcı yönetim sistemi:

### Roller

1. **Admin (Süper Yönetici)**
   - Tüm sisteme tam erişim
   - Yönetici hesapları oluşturma/silme
   - Yöneticilerin modül erişimlerini belirleme
   - Sistem ayarlarını yönetme

2. **Yönetici (Manager)**
   - Admin tarafından belirlenen modüllere erişim
   - Öğretmen hesapları oluşturma/düzenleme
   - Öğretmenlerin modül erişimlerini belirleme
   - Kendi profilini yönetme

3. **Kullanıcı (Öğretmen)**
   - Yönetici tarafından belirlenen modüllere erişim
   - İzin verilen modüllerde içerik oluşturma
   - Kendi profilini düzenleme

### Modüller

- **Etkinlik Oluşturma**: Etkinlik oluşturma ve düzenleme
- **Günlük Plan**: Günlük plan hazırlama
- **Kazanım Yönetimi**: Kazanım görüntüleme ve yönetim
- **Şablon Yönetimi**: Şablon oluşturma ve düzenleme
- **Raporlama**: Rapor görüntüleme ve oluşturma
- **Kullanıcı Yönetimi**: Kullanıcı yönetimi (sadece yönetici)

## Kurulum

### 1. Bağımlılıkları Yükleyin

```bash
cd backend
pip install -r requirements.txt
```

### 2. Veritabanı Tablolarını Oluşturun

```bash
python init_user_system.py
```

Bu komut:
- User ve Module tablolarını oluşturur
- Varsayılan modülleri ekler
- İlk admin kullanıcısını oluşturur

**Varsayılan Admin Bilgileri:**
- Kullanıcı Adı: `admin`
- Şifre: `Admin123!`
- ⚠️ İlk girişten sonra şifreyi değiştirin!

## API Endpoint'leri

### Kimlik Doğrulama

#### Giriş Yap
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=Admin123!
```

Yanıt:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Token Yenile
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

### Kullanıcı İşlemleri

#### Mevcut Kullanıcı Bilgileri
```http
GET /api/v1/users/me
Authorization: Bearer {access_token}
```

#### Kullanıcı Listele (Yönetici)
```http
GET /api/v1/users
Authorization: Bearer {access_token}
```

#### Yeni Kullanıcı Oluştur (Yönetici)
```http
POST /api/v1/users
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "ogretmen@okul.com",
  "username": "ogretmen1",
  "full_name": "Ayşe Öğretmen",
  "password": "Sifre123!",
  "role": "kullanici",
  "module_ids": ["module-uuid-1", "module-uuid-2"]
}
```

#### Kullanıcı Güncelle (Yönetici)
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Yeni İsim",
  "module_ids": ["module-uuid-1", "module-uuid-3"]
}
```

### Modül İşlemleri

#### Modül Listele (Admin)
```http
GET /api/v1/modules
Authorization: Bearer {access_token}
```

## Kullanım Senaryoları

### 1. İlk Kurulum

1. `init_user_system.py` scripti çalıştırın
2. Admin hesabıyla giriş yapın
3. Admin panelden yönetici hesapları oluşturun
4. Yöneticilere gerekli modül erişimlerini verin

### 2. Yönetici Oluşturma (Admin)

```python
# POST /api/v1/users
{
  "email": "yonetici@okul.com",
  "username": "yonetici1",
  "full_name": "Mehmet Yönetici",
  "password": "Yonetici123!",
  "role": "yonetici",
  "module_ids": [
    "etkinlik_olusturma_module_id",
    "kullanici_yonetimi_module_id"
  ]
}
```

### 3. Öğretmen Oluşturma (Yönetici)

```python
# POST /api/v1/users
{
  "email": "ogretmen@okul.com",
  "username": "ogretmen1",
  "full_name": "Zeynep Öğretmen",
  "password": "Ogretmen123!",
  "role": "kullanici",
  "module_ids": [
    "etkinlik_olusturma_module_id",
    "gunluk_plan_module_id"
  ]
}
```

## Güvenlik

### Şifre Politikası

Şifreler şu kriterleri karşılamalı:
- En az 8 karakter
- En az 1 büyük harf
- En az 1 küçük harf
- En az 1 rakam

### Token Yönetimi

- Access Token: 30 dakika geçerli
- Refresh Token: 7 gün geçerli
- Her istekte `Authorization: Bearer {token}` header'ı gerekli

### Modül Bazlı Erişim Kontrolü

Endpoint'lerde modül kontrolü:

```python
from app.api.deps import require_module_access

@router.post("/etkinlik")
async def create_activity(
    current_user = Depends(require_module_access("etkinlik_olusturma"))
):
    # Sadece etkinlik_olusturma modülüne sahip kullanıcılar erişebilir
    pass
```

## Sorun Giderme

### Yaygın Hatalar

1. **"User not found"**: Token süresi dolmuş olabilir, yeniden giriş yapın
2. **"Not enough permissions"**: Kullanıcının rolü yetersiz
3. **"No access to module"**: Kullanıcıya modül atanmamış
4. **"Password too weak"**: Şifre politikasına uygun değil

### Veritabanı Sıfırlama

Eğer baştan başlamak isterseniz:

```sql
-- PostgreSQL'de
DROP TABLE IF EXISTS user_modules CASCADE;
DROP TABLE IF EXISTS modules CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TYPE IF EXISTS userrole;
```

Sonra `init_user_system.py` scriptini yeniden çalıştırın.

## Geliştirme Notları

### Yeni Modül Ekleme

1. `init_user_system.py` dosyasında `modules_data` listesine ekleyin
2. Veya API üzerinden POST `/api/v1/modules` endpoint'ini kullanın

### Rol Kontrolü Ekleme

```python
from app.api.deps import get_admin_user, get_manager_user

# Sadece admin
@router.get("/admin-only")
async def admin_endpoint(current_user = Depends(get_admin_user)):
    pass

# Admin veya yönetici
@router.get("/manager-plus")
async def manager_endpoint(current_user = Depends(get_manager_user)):
    pass
```

## Destek

Sorularınız için sistem yöneticisi ile iletişime geçin.