# 🚀 BalderAI Production Integration Test Guide

## ✅ Tamamlanan Özellikler

### 1️⃣ Production Callback Sistemi
- **Default Callback URL:** `https://balder-ai.vercel.app/api/jobs/callback`
- **Automatic URL Conversion:** Localhost URL'leri otomatik olarak production'a çevriliyor
- **Headers:** `Appium-Agent/1.0` User-Agent ve production Origin

### 2️⃣ CORS Konfigürasyonu
- **Production Domain:** `https://balder-ai.vercel.app`
- **Development Domains:** `http://localhost:3000`, `https://localhost:3000`
- **Universal Access:** Geçici olarak tüm origin'lere izin

### 3️⃣ API Endpoints
- `POST /api/google-flow` - Video üretimi başlat
- `GET /api/job/{job_id}` - Job durumu sorgula
- `POST /api/test-callback` - Callback sistemi test et
- `GET /health` - Health check
- `POST /api/restart` - Servisi yeniden başlat

## 🧪 Test Senaryoları

### 1. API Server Başlatma
```bash
# Varsayılan port'ta başlat
python main.py

# Farklı port'ta başlat
python main.py --port 8080

# Tüm IP'lerden erişime aç
python main.py --host 0.0.0.0
```

### 2. Production Video Üretimi Test
```bash
curl -X POST http://localhost:8000/api/google-flow \
  -H "Content-Type: application/json" \
  -H "Origin: https://balder-ai.vercel.app" \
  -d '{
    "jobId": "test_production_job_001",
    "prompt": "A cute cat playing with a ball in the garden",
    "model": "veo-3",
    "action": "create_project",
    "userId": "test_user_123"
  }'
```

### 3. Callback Sistemi Test
```bash
curl -X POST http://localhost:8000/api/test-callback \
  -H "Content-Type: application/json"
```

### 4. Job Durumu Sorgulama
```bash
curl -X GET http://localhost:8000/api/job/test_production_job_001
```

### 5. Health Check
```bash
curl -X GET http://localhost:8000/health
```

## 📊 Beklenen Loglar

### Başarılı Video Üretimi
```
🚀 Starting automation for job test_production_job_001
📝 Prompt: A cute cat playing with a ball in the garden
👤 User ID: test_user_123
📞 Callback URL: https://balder-ai.vercel.app/api/jobs/callback
📤 Sending callback to https://balder-ai.vercel.app/api/jobs/callback
📦 Payload: {'jobId': 'test_production_job_001', 'status': 'completed', ...}
✅ Callback sent successfully to https://balder-ai.vercel.app/api/jobs/callback
```

### Callback Test
```
📤 Sending callback to https://balder-ai.vercel.app/api/jobs/callback
📦 Payload: {'jobId': 'test_1234567890', 'status': 'test', ...}
✅ Callback sent successfully to https://balder-ai.vercel.app/api/jobs/callback
```

## 🔧 Konfigürasyon

### Environment Variables
```bash
# Headless mode için
export CHROME_HEADLESS=true

# Custom callback URL için
export DEFAULT_CALLBACK_URL=https://balder-ai.vercel.app/api/jobs/callback
```

### API Response Format
```json
{
  "success": true,
  "message": "Job başarıyla başlatıldı - BalderAI Production",
  "data": {
    "jobId": "test_production_job_001",
    "status": "queued",
    "estimatedTime": "5-10 dakika",
    "callbackUrl": "https://balder-ai.vercel.app/api/jobs/callback",
    "origin": "https://balder-ai.vercel.app"
  }
}
```

## 🚨 Hata Durumları

### Callback Hatası
```
❌ Callback failed: 500 - Internal Server Error
❌ Callback error: Connection timeout
```

### Automation Hatası
```
Job test_production_job_001 hatası: Chrome driver not found
📤 Sending callback to https://balder-ai.vercel.app/api/jobs/callback
📦 Payload: {'jobId': 'test_production_job_001', 'status': 'error', 'error': 'Chrome driver not found'}
✅ Callback sent successfully to https://balder-ai.vercel.app/api/jobs/callback
```

## 📁 Dosya Yapısı

```
ubuntu-chromedriver-automation/
├── main.py                          # Ana API server
├── requirements.txt                  # Python bağımlılıkları
├── .gitignore                       # Git ignore kuralları
├── BALDERAI_PRODUCTION_TEST.md      # Bu test dokümantasyonu
├── chrome_automation.py             # Chrome automation logic
├── session_manager.py               # Session yönetimi
├── config.py                        # Konfigürasyon
└── logs/                            # Log dosyaları
```

## 🎯 Sonraki Adımlar

1. **Production Test:** Ubuntu server'da test et
2. **ngrok Tunnel:** Public URL için ngrok kur
3. **Monitoring:** Log monitoring sistemi ekle
4. **Error Handling:** Daha detaylı hata yönetimi
5. **Performance:** Redis cache ekle

---

**🎉 BalderAI Production Integration hazır!**
