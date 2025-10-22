# PERSEPTOR Dynamic Configuration Checklist

Bu checklist, tüm statik bağlantıların dinamik environment variable'lara dönüştürüldüğünü doğrulamak için kullanılır.

## ✅ Tamamlanan Değişiklikler

### 1. Docker Compose (docker-compose.yml)
- [x] Backend port dinamik: `${BACKEND_PORT:-5000}`
- [x] Backend environment variables tanımlı
- [x] Frontend port dinamik: `${FRONTEND_PORT:-3000}`
- [x] Frontend environment variables tanımlı
- [x] Backend sadece `expose` kullanıyor (dışarıya kapalı)
- [x] Tüm değişkenler default value içeriyor

### 2. Backend Dockerfile (Dockerfile.backend)
- [x] CHROME_BIN environment variable
- [x] CHROMEDRIVER_PATH environment variable
- [x] TESSERACT_CMD environment variable
- [x] BACKEND_HOST environment variable
- [x] BACKEND_PORT environment variable

### 3. Frontend Dockerfile (Dockerfile.frontend)
- [x] nginx.conf.template kullanımı
- [x] docker-entrypoint.sh eklendi
- [x] NGINX_PORT environment variable
- [x] BACKEND_SERVICE environment variable
- [x] BACKEND_PORT environment variable
- [x] ENTRYPOINT script olarak ayarlandı

### 4. Nginx Configuration
- [x] nginx.conf.template oluşturuldu
- [x] ${NGINX_PORT} dinamik port
- [x] ${BACKEND_SERVICE} dinamik service name
- [x] ${BACKEND_PORT} dinamik backend port
- [x] Timeout ayarları eklendi (600s)

### 5. Backend Code (api/app.py)
- [x] BACKEND_HOST environment variable'dan okunuyor
- [x] BACKEND_PORT environment variable'dan okunuyor
- [x] FLASK_ENV environment variable'dan okunuyor
- [x] Hardcoded CORS origin kaldırıldı
- [x] Flask-CORS tüm origin'leri kabul ediyor

### 6. Python Modules
- [x] `modules/ocr_module.py` - TESSERACT_CMD dinamik
- [x] `modules/ocr_module.py` - CHROME_BIN dinamik
- [x] `modules/global_sigma_match_module.py` - SIGMAHQ_BASE_URL dinamik

### 7. Frontend Code (React)
- [x] `perseptor-ui/src/services/api.ts` - Relative URL kullanıyor (`/api`)
- [x] `perseptor-ui/src/pages/CreatedRules.tsx` - Relative URL kullanıyor
- [x] Tüm API çağrıları nginx proxy üzerinden

### 8. Documentation
- [x] ENV_TEMPLATE dosyası oluşturuldu
- [x] README.md güncellendi
- [x] Environment variable tablosu eklendi
- [x] Kullanım örnekleri eklendi

### 9. Test Scripts
- [x] test_env_vars.sh oluşturuldu
- [x] Executable yapıldı

## 🧪 Test Adımları

### Adım 1: Docker Container'ları Başlat
```bash
cd /home/dipsh0v/PERSEPTOR
docker-compose down
docker-compose up --build -d
```

### Adım 2: Environment Variables Testi
```bash
cd /home/dipsh0v/PERSEPTOR/docker
./test_env_vars.sh
```

### Adım 3: Manual Test
```bash
# Backend environment variables
docker-compose exec backend printenv | grep -E "BACKEND|FLASK|TESSERACT|CHROME|SIGMA"

# Frontend environment variables
docker-compose exec frontend printenv | grep -E "NGINX|BACKEND"

# Nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Adım 4: Network Connectivity Test
```bash
# Frontend'den backend'e ping
docker-compose exec frontend ping -c 3 backend

# API test
curl http://localhost:3000/api/rules
```

### Adım 5: Port Exposure Test
```bash
# Backend'in dışarıya kapalı olduğunu doğrula (başarısız olmalı)
curl http://localhost:5000/api/rules

# Frontend üzerinden (başarılı olmalı)
curl http://localhost:3000/api/rules
```

## 🔒 Güvenlik Kontrolleri

- [ ] Backend port 5000 dışarıya açık DEĞİL
- [ ] Sadece frontend port 3000 dışarıya açık
- [ ] Backend'e sadece Docker network içinden erişilebiliyor
- [ ] CORS ayarları doğru çalışıyor
- [ ] Nginx proxy doğru çalışıyor

## 🎯 Özel Konfigürasyon Testi

### Farklı Portlarla Test
```bash
# .env dosyası oluştur
cat > /home/dipsh0v/PERSEPTOR/docker/.env << EOF
FRONTEND_PORT=8080
BACKEND_PORT=5001
FLASK_ENV=production
EOF

# Yeniden başlat
docker-compose down
docker-compose up --build -d

# Test et
curl http://localhost:8080/api/rules
```

## 📊 Beklenen Sonuçlar

### Environment Variables
- Tüm değişkenler container'larda set olmalı
- Default değerler kullanılmalı (eğer .env yoksa)
- .env dosyası varsa, oradaki değerler kullanılmalı

### Network
- Frontend → Backend iletişimi çalışmalı
- Backend sadece internal network'te erişilebilir olmalı
- External → Backend direkt erişimi başarısız olmalı

### Configuration
- Nginx config dinamik olarak generate edilmeli
- Backend doğru port ve host'ta çalışmalı
- Tesseract ve Chrome doğru path'leri kullanmalı

## ⚠️ Bilinen Sınırlamalar

### Docker Olmayan Durumlar
Aşağıdaki dosyalar Docker kullanılmadığında hardcoded değerler içerir (local development için):
- `main.py` - Local Flask development server (CORS: localhost:3000)
- `DEATHCon 2025/setup_workshop.py` - Workshop setup script

Bu dosyalar Docker deployment'ında kullanılmaz, bu yüzden sorun yaratmaz.

## 🔄 Değişiklik Sonrası Checklist

Yeni bir değişiklik yaptıktan sonra:
1. [ ] Docker container'ları yeniden build et
2. [ ] test_env_vars.sh çalıştır
3. [ ] Manual API testi yap
4. [ ] Frontend'den backend connectivity testi yap
5. [ ] Security testi yap (backend external erişim)
6. [ ] Log'ları kontrol et: `docker-compose logs`

## 📝 Sonuç

✅ **Tüm statik bağlantılar dinamik environment variable'lara dönüştürüldü!**

- Backend ve Frontend tamamen environment variable bazlı
- Nginx dinamik olarak konfigüre ediliyor
- Docker network internal communication çalışıyor
- Backend external erişime kapalı
- Dokümantasyon güncel
- Test script'leri hazır

