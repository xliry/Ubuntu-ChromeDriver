# Ubuntu ChromeDriver API Integration PRD

## Product Requirements Document

### 1. Proje Özeti (Project Overview)

**Proje Adı:** Ubuntu ChromeDriver API Entegrasyonu  
**Versiyon:** 1.0  
**Tarih:** 2025-01-23  
**Hedef:** Ubuntu sunucu ortamında ChromeDriver kullanarak web otomasyonu yapan agent için API entegrasyonu

---

### 2. Sistem Mimarisi (System Architecture)

#### 2.1 Genel Yapı

```
[Ubuntu Server] ←→ [ChromeDriver] ←→ [Chrome Browser] ←→ [Target Websites]
       ↑
[API Endpoints] ←→ [Agent/Client]
```

#### 2.2 Teknoloji Stack

- **Sunucu İşletim Sistemi:** Ubuntu 20.04 LTS / 22.04 LTS
- **Web Driver:** ChromeDriver (Linux x64)
- **Tarayıcı:** Google Chrome (Headless/Headful)
- **API Framework:** Node.js + Express.js / Python + FastAPI
- **Process Management:** PM2 / Systemd
- **Container:** Docker (Opsiyonel)

---

### 3. API Endpoint Yapısı (API Endpoint Structure)

#### 3.1 Ana Endpoint: `/api/v1/automation`

##### 3.1.1 POST `/api/v1/automation/google-flow`

**Açıklama:** Google Flow otomasyonu başlatır

**Request Body:**

```json
{
  "jobId": "unique_website_job_id_1755925204612_4uvbgrvys_1755925383232",
  "prompt": "Create a video about artificial intelligence",
  "model": "veo-3",
  "timestamp": "2025-01-23T10:30:00.000Z",
  "userId": "user_123",
  "action": "create_project",
  "timeout": 300,
  "callbackUrl": "https://balder-ai.vercel.app/api/jobs/callback"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Automation started successfully",
  "data": {
    "jobId": "unique_website_job_id_1755925204612_4uvbgrvys_1755925383232",
    "status": "processing",
    "estimatedDuration": "2-5 minutes",
    "sessionId": "chrome_session_abc123"
  }
}
```

##### 3.1.2 GET `/api/v1/automation/status/{jobId}`

**Açıklama:** Belirli bir job'ın durumunu sorgular

**Response:**

```json
{
  "jobId": "unique_website_job_id_1755925204612_4uvbgrvys_1755925383232",
  "status": "processing",
  "progress": 65,
  "currentStep": "Video generation in progress",
  "estimatedTimeRemaining": "1 minute",
  "sessionInfo": {
    "sessionId": "chrome_session_abc123",
    "browserVersion": "120.0.6099.109",
    "driverVersion": "120.0.6099.109"
  }
}
```

##### 3.1.3 DELETE `/api/v1/automation/cancel/{jobId}`

**Açıklama:** Çalışan bir job'ı iptal eder

**Response:**

```json
{
  "success": true,
  "message": "Job cancelled successfully",
  "data": {
    "jobId": "unique_website_job_id_1755925204612_4uvbgrvys_1755925383232",
    "status": "cancelled",
    "cancelledAt": "2025-01-23T10:35:00.000Z"
  }
}
```

#### 3.2 Sistem Yönetimi Endpoint'leri

##### 3.2.1 GET `/api/v1/system/health`

**Açıklama:** Sistem sağlık durumunu kontrol eder

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-23T10:30:00.000Z",
  "components": {
    "chromeDriver": {
      "status": "running",
      "version": "120.0.6099.109",
      "processId": 12345
    },
    "chromeBrowser": {
      "status": "available",
      "version": "120.0.6099.109",
      "instances": 2
    },
    "system": {
      "cpu": "15%",
      "memory": "2.1GB/8GB",
      "disk": "45GB/100GB"
    }
  }
}
```

##### 3.2.2 POST `/api/v1/system/restart`

**Açıklama:** ChromeDriver servisini yeniden başlatır

**Response:**

```json
{
  "success": true,
  "message": "ChromeDriver restarted successfully",
  "data": {
    "restartedAt": "2025-01-23T10:30:00.000Z",
    "newProcessId": 12346,
    "status": "running"
  }
}
```

---

### 4. ChromeDriver Konfigürasyonu (ChromeDriver Configuration)

#### 4.1 Temel Konfigürasyon

```bash
# ChromeDriver kurulumu
wget https://chromedriver.storage.googleapis.com/120.0.6099.109/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Chrome kurulumu
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

#### 4.2 ChromeDriver Options

```javascript
const chromeOptions = {
  // Headless mod
  headless: true,

  // Güvenlik ayarları
  noSandbox: true,
  disableDevShmUsage: true,
  disableGpu: true,

  // Performans ayarları
  disableWebSecurity: true,
  allowRunningInsecureContent: true,

  // Bellek yönetimi
  memoryPressureLevel: "critical",

  // User agent
  userAgent: "BalderAI-Automation/1.0",

  // Ek argümanlar
  args: [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--disable-features=VizDisplayCompositor",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-features=TranslateUI",
    "--disable-ipc-flooding-protection"
  ]
};
```

---

### 5. Hata Yönetimi (Error Handling)

#### 5.1 HTTP Status Kodları

- **200:** Başarılı
- **201:** Oluşturuldu
- **400:** Geçersiz istek
- **401:** Yetkisiz erişim
- **404:** Bulunamadı
- **408:** Zaman aşımı
- **500:** Sunucu hatası
- **503:** Servis kullanılamıyor

#### 5.2 Hata Response Formatı

```json
{
  "error": {
    "code": "CHROME_DRIVER_ERROR",
    "message": "ChromeDriver başlatılamadı",
    "details": "Process failed to start: ENOENT: no such file or directory",
    "timestamp": "2025-01-23T10:30:00.000Z",
    "requestId": "req_abc123"
  }
}
```

#### 5.3 Yaygın Hata Kodları

- **CHROME_DRIVER_ERROR:** ChromeDriver çalıştırma hatası
- **BROWSER_LAUNCH_ERROR:** Tarayıcı başlatma hatası
- **SESSION_TIMEOUT:** Oturum zaman aşımı
- **ELEMENT_NOT_FOUND:** Web elementi bulunamadı
- **NETWORK_ERROR:** Ağ bağlantı hatası
- **MEMORY_ERROR:** Bellek yetersizliği

---

### 6. Güvenlik (Security)

#### 6.1 API Güvenliği

- **Rate Limiting:** IP başına dakikada maksimum 10 istek
- **Authentication:** API Key veya JWT token
- **CORS:** Sadece belirlenen domain'lerden erişim
- **Input Validation:** Tüm input'ların sanitize edilmesi

#### 6.2 ChromeDriver Güvenliği

- **Sandbox:** Disabled (Ubuntu sunucu ortamı için)
- **User Permissions:** Minimum gerekli izinler
- **Network Isolation:** Sadece gerekli domain'lere erişim
- **File System Access:** Sadece belirlenen dizinlere erişim

---

### 7. Monitoring ve Logging

#### 7.1 Log Formatı

```json
{
  "timestamp": "2025-01-23T10:30:00.000Z",
  "level": "INFO",
  "jobId": "unique_website_job_id_1755925204612_4uvbgrvys_1755925383232",
  "sessionId": "chrome_session_abc123",
  "action": "navigate_to_website",
  "message": "Navigating to https://example.com",
  "metadata": {
    "url": "https://example.com",
    "duration": 1500,
    "status": "success"
  }
}
```

#### 7.2 Monitoring Metrikleri

- **ChromeDriver Process Count:** Aktif ChromeDriver süreç sayısı
- **Memory Usage:** Bellek kullanımı
- **CPU Usage:** CPU kullanımı
- **Active Sessions:** Aktif oturum sayısı
- **Error Rate:** Hata oranı
- **Response Time:** Yanıt süresi

---

### 8. Deployment ve DevOps

#### 8.1 Ubuntu Sunucu Gereksinimleri

```bash
# Minimum sistem gereksinimleri
CPU: 2 vCPU
RAM: 4GB
Disk: 20GB SSD
OS: Ubuntu 20.04 LTS veya üzeri

# Önerilen sistem gereksinimleri
CPU: 4 vCPU
RAM: 8GB
Disk: 50GB SSD
OS: Ubuntu 22.04 LTS
```

#### 8.2 Kurulum Scripti

```bash
#!/bin/bash
# install_chromedriver.sh

echo "🚀 Ubuntu ChromeDriver API kurulumu başlatılıyor..."

# Sistem güncellemesi
sudo apt update && sudo apt upgrade -y

# Gerekli paketler
sudo apt install -y curl wget unzip software-properties-common

# Chrome kurulumu
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install -y google-chrome-stable

# ChromeDriver kurulumu
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Node.js kurulumu
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# PM2 kurulumu
sudo npm install -g pm2

echo "✅ Kurulum tamamlandı!"
echo "Chrome Version: $(google-chrome --version)"
echo "ChromeDriver Version: $(chromedriver --version)"
echo "Node.js Version: $(node --version)"
```

#### 8.3 PM2 Konfigürasyonu

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "chromedriver-api",
      script: "server.js",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "production",
        PORT: 3000
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 3000
      }
    }
  ]
};
```

---

### 9. Test Senaryoları (Test Scenarios)

#### 9.1 Unit Tests

```javascript
describe("ChromeDriver API", () => {
  test("should start automation successfully", async () => {
    const response = await request(app)
      .post("/api/v1/automation/google-flow")
      .send({
        jobId: "test_job_123",
        prompt: "Test automation",
        model: "veo-3"
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
  });
});
```

#### 9.2 Integration Tests

```javascript
describe("ChromeDriver Integration", () => {
  test("should navigate to website and take screenshot", async () => {
    // Test implementation
  });

  test("should handle multiple concurrent sessions", async () => {
    // Test implementation
  });
});
```

---

### 10. Performans Optimizasyonu

#### 10.1 ChromeDriver Optimizasyonu

- **Process Pool:** Maksimum 5 eşzamanlı ChromeDriver süreci
- **Memory Management:** Her süreç için maksimum 1GB RAM
- **Session Reuse:** Kısa süreli oturumlar için oturum yeniden kullanımı
- **Resource Cleanup:** Kullanılmayan kaynakların otomatik temizlenmesi

#### 10.2 API Optimizasyonu

- **Connection Pooling:** Veritabanı bağlantı havuzu
- **Caching:** Sık kullanılan veriler için Redis cache
- **Async Processing:** Asenkron işlem kuyruğu
- **Load Balancing:** Yük dengeleme (birden fazla sunucu için)

---

### 11. Troubleshooting

#### 11.1 Yaygın Sorunlar ve Çözümleri

**ChromeDriver başlatılamıyor:**

```bash
# Çözüm 1: İzinleri kontrol et
sudo chmod +x /usr/local/bin/chromedriver

# Çözüm 2: Bağımlılıkları kontrol et
ldd /usr/local/bin/chromedriver

# Çözüm 3: Chrome versiyonunu kontrol et
google-chrome --version
chromedriver --version
```

**Bellek hatası:**

```bash
# Çözüm 1: Swap alanı ekle
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Çözüm 2: ChromeDriver süreç sayısını azalt
export CHROME_DRIVER_MAX_INSTANCES=3
```

**Chrome çökmesi:**

```bash
# Çözüm 1: Chrome'u yeniden başlat
sudo pkill -f chrome
sudo pkill -f chromedriver

# Çözüm 2: Sistem kaynaklarını kontrol et
htop
free -h
df -h
```

---

### 12. Gelecek Geliştirmeler (Future Enhancements)

#### 12.1 Kısa Vadeli (1-3 ay)

- [ ] Docker container desteği
- [ ] Kubernetes deployment
- [ ] Otomatik ChromeDriver güncelleme
- [ ] Gelişmiş monitoring dashboard

#### 12.2 Orta Vadeli (3-6 ay)

- [ ] Multi-browser desteği (Firefox, Safari)
- [ ] Distributed processing
- [ ] Machine learning tabanlı hata tahmini
- [ ] Otomatik scaling

#### 12.3 Uzun Vadeli (6+ ay)

- [ ] AI-powered automation
- [ ] Cross-platform compatibility
- [ ] Enterprise features
- [ ] Mobile automation support

---

### 13. Sonuç (Conclusion)

Bu PRD, Ubuntu sunucu ortamında ChromeDriver kullanarak web otomasyonu yapan agent için kapsamlı bir API entegrasyon planı sunmaktadır. Belirtilen gereksinimler ve özellikler, güvenilir, ölçeklenebilir ve sürdürülebilir bir sistem oluşturmayı hedeflemektedir.

**Önemli Noktalar:**

- ChromeDriver ve Chrome'un Ubuntu uyumluluğu
- Güvenlik ve performans optimizasyonu
- Kapsamlı hata yönetimi ve monitoring
- DevOps ve deployment otomasyonu
- Gelecek geliştirme planları

---

**Doküman Versiyonu:** 1.0  
**Son Güncelleme:** 2025-01-23  
**Hazırlayan:** AI Assistant  
**Onaylayan:** [Gerekli]  
**Durum:** Draft
