# Ubuntu Chrome Automation 🚀

Google Flow platformunda otomatik video üretimi için optimize edilmiş Ubuntu Chrome automation sistemi.

## ✨ Özellikler

- **🔧 Ubuntu Chrome Driver Yönetimi**: Otomatik Chrome kurulumu ve yapılandırması
- **🔐 Akıllı Session Yönetimi**: Şifrelenmiş session saklama ve yeniden kullanım
- **💳 Kredi Bazlı Hesap Değiştirme**: Düşük kredili hesaplardan otomatik geçiş
- **🎯 Flow Onboarding**: İlk giriş için otomatik onboarding handling
- **🤖 Bot Detection Bypass**: undetected_chromedriver ile güvenli automation
- **🖥️ Headless Mode**: Server environments için headless çalışma desteği
- **🌐 REST API**: FastAPI tabanlı modern API endpoints

## 🏗️ Sistem Mimarisi

```
ChromeAutomation (Ana Sınıf)
├── ChromeDriverManager (Chrome Driver Yönetimi)
├── SessionManager (Session & Kredi Yönetimi)
├── Flow Automation (Google Flow İşlemleri)
└── FastAPI Server (REST API Endpoints)
```

## 📋 Gereksinimler

### Sistem Gereksinimleri

- Ubuntu 20.04+ (veya Linux dağıtımı)
- Python 3.8+
- Minimum 2GB RAM
- Chrome browser

### Python Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Kurulum

### 1. Repository Clone

```bash
git clone <repository-url>
cd ubuntu-chromedriver-automation
```

### 2. Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Chrome Kurulumu (Otomatik)

```bash
python3 chrome_manager.py
```

## 💻 Kullanım

### Komut Satırı Kullanımı

```bash
# Basit video oluşturma
python3 main.py --prompt "A cute cat playing with a ball"

# Kullanıcı ID ile
python3 main.py --prompt "A dog running in the park" --user-id "user123"

# Headless mode (server için)
python3 main.py --headless --prompt "A bird flying in the sky"
```

### API Kullanımı

#### API Server'ı Başlat

```bash
python3 api_server.py
```

#### API Endpoints

**1. Health Check**

```bash
GET /api/v1/system/health
```

**2. Automation Başlat**

```bash
POST /api/v1/automation/google-flow
{
  "jobId": "unique_job_id",
  "prompt": "A cute cat playing with a ball",
  "model": "veo-3",
  "userId": "user123",
  "action": "create_project",
  "timeout": 300,
  "callbackUrl": "https://example.com/callback"
}
```

**3. Job Status Kontrol**

```bash
GET /api/v1/automation/status/{jobId}
```

**4. Job İptal Et**

```bash
DELETE /api/v1/automation/cancel/{jobId}
```

**5. Service Restart**

```bash
POST /api/v1/system/restart
```

#### API Test

```bash
python3 test_api.py
```

### Session Yönetimi

```bash
# Session bilgilerini göster
python3 main.py --session-info

# Session'ı temizle
python3 main.py --clear-session

# Session manager'ı test et
python3 main.py --test-session
```

## 🔧 Konfigürasyon

### Environment Variables

```bash
export GOOGLE_EMAIL="your-email@gmail.com"
export GOOGLE_PASSWORD="your-password"
export CHROME_HEADLESS="true"  # Server environments için
```

### Config Dosyası

`config.py` dosyasında aşağıdaki ayarları düzenleyebilirsiniz:

- **Chrome Options**: Browser yapılandırması
- **Session Timeout**: Session süre sınırları
- **Credit Threshold**: Hesap değiştirme kredi limiti
- **Flow URLs**: Google Flow endpoint'leri

## 📊 Akış Diyagramı

```
START → Chrome Setup → Session Check → Login (if needed) → Flow Navigation
  ↓
Onboarding Check → Project Creation → Video Generation → Success
```

## 🔐 Güvenlik

- **Şifrelenmiş Session**: Fernet encryption ile güvenli saklama
- **Credential Protection**: Şifreler memory'de şifrelenmiş olarak tutulur
- **Profile Isolation**: Her session için ayrı Chrome profile
- **Bot Detection Bypass**: undetected_chromedriver ile güvenli automation
- **API Rate Limiting**: IP başına dakikada maksimum 10 istek

## 🧪 Test

### Session Manager Test

```bash
python3 main.py --test-session
```

### Chrome Manager Test

```bash
python3 chrome_manager.py
```

### Manuel Test

```bash
python3 chrome_automation.py
```

### API Test

```bash
python3 test_api.py
```

## 📁 Proje Yapısı

```
ubuntu-chromedriver-automation/
├── main.py                 # Ana çalıştırma dosyası
├── api_server.py           # FastAPI server
├── test_api.py             # API test script'i
├── chrome_automation.py    # Ana automation sınıfı
├── chrome_manager.py       # Chrome driver yönetimi
├── session_manager.py      # Session ve kredi yönetimi
├── config.py              # Konfigürasyon ayarları
├── requirements.txt       # Python dependencies
├── README.md             # Bu dosya
├── data/                 # Session ve veri dosyaları
├── logs/                 # Log dosyaları
├── profiles/             # Chrome profile'ları
└── downloads/            # İndirilen dosyalar
```

## 🚨 Hata Giderme

### Chrome Kurulum Sorunları

```bash
# Chrome versiyonunu kontrol et
google-chrome --version

# Chrome'u yeniden kur
sudo apt remove google-chrome-stable
sudo apt install google-chrome-stable
```

### Session Sorunları

```bash
# Session'ı temizle
python3 main.py --clear-session

# Session bilgilerini kontrol et
python3 main.py --session-info
```

### API Sorunları

```bash
# API server'ı yeniden başlat
python3 api_server.py

# Health check yap
curl http://localhost:8000/api/v1/system/health
```

### Permission Sorunları

```bash
# Chrome profile dizinini temizle
rm -rf profiles/*

# Encryption key'i yenile
rm .encryption_key
```

## 📈 Performance Metrikleri

| Metrik                   | Android/Appium | Ubuntu/Chrome | İyileştirme |
| ------------------------ | -------------- | ------------- | ----------- |
| Login Süresi             | ~45 saniye     | ~15 saniye    | %67 azalma  |
| Toplam Test Süresi       | ~3 dakika      | ~2 dakika     | %33 azalma  |
| Session Yeniden Kullanım | %0             | %80           | %80 artış   |

## 🔄 Geliştirme

### Yeni Özellik Ekleme

1. İlgili sınıfa yeni method ekle
2. Config dosyasına gerekli ayarları ekle
3. Test senaryolarını güncelle
4. README'yi güncelle

### Debug Mode

```bash
# Verbose logging için
export PYTHONPATH=.
python3 -u main.py --prompt "test" 2>&1 | tee automation.log
```

## 📞 Destek

### Log Dosyaları

- **Automation Logs**: `logs/automation.log`
- **Chrome Logs**: `profiles/chrome-profile-*/chrome_debug.log`
- **API Logs**: Uvicorn console output

### Hata Raporlama

1. Log dosyalarını kontrol et
2. Session bilgilerini kontrol et
3. Chrome versiyonunu kontrol et
4. API health check yap
5. Issue aç ve log'ları ekle

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yap
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Commit yap (`git commit -m 'Add amazing feature'`)
4. Push yap (`git push origin feature/amazing-feature`)
5. Pull Request aç

## 🎯 Roadmap

- [x] Video oluşturma otomasyonu
- [x] REST API endpoints
- [ ] Batch processing desteği
- [ ] Web UI dashboard
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Performance monitoring

---

**Not**: Bu proje Google Flow platformu ile otomatik etkileşim için tasarlanmıştır. Platform'un kullanım şartlarına uygun olarak kullanın.
