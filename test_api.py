"""
API Test Script
Ubuntu ChromeDriver API'yi test etmek için
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Health check endpoint'ini test et"""
    print("🏥 Health Check Test")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/system/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check başarılı")
            print(f"   Status: {data['status']}")
            print(f"   Chrome Driver: {data['components']['chromeDriver']['status']}")
            print(f"   Chrome Browser: {data['components']['chromeBrowser']['status']}")
            print(f"   Active Sessions: {data['components']['chromeBrowser']['instances']}")
        else:
            print(f"❌ Health check başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API server'a bağlanılamadı. Server çalışıyor mu?")
    except Exception as e:
        print(f"❌ Health check hatası: {e}")

def test_automation_start():
    """Automation başlatma endpoint'ini test et"""
    print("\n🚀 Automation Start Test")
    print("-" * 30)
    
    try:
        # Test request data
        request_data = {
            "jobId": f"test_job_{int(time.time())}",
            "prompt": "A cute cat playing with a ball",
            "model": "veo-3",
            "userId": "test_user_123",
            "action": "create_project",
            "timeout": 300,
            "callbackUrl": "https://example.com/callback"
        }
        
        print(f"📝 Request: {json.dumps(request_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/automation/google-flow",
            json=request_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Automation başlatma başarılı")
            print(f"   Job ID: {data['data']['jobId']}")
            print(f"   Status: {data['data']['status']}")
            print(f"   Session ID: {data['data']['sessionId']}")
            print(f"   Estimated Duration: {data['data']['estimatedDuration']}")
            
            return data['data']['jobId']
        else:
            print(f"❌ Automation başlatma başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ API server'a bağlanılamadı. Server çalışıyor mu?")
        return None
    except Exception as e:
        print(f"❌ Automation start hatası: {e}")
        return None

def test_job_status(job_id):
    """Job status endpoint'ini test et"""
    if not job_id:
        return
        
    print(f"\n📊 Job Status Test (Job ID: {job_id})")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/automation/status/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Job status başarılı")
            print(f"   Status: {data['status']}")
            print(f"   Progress: {data['progress']}%")
            print(f"   Current Step: {data['currentStep']}")
            print(f"   Estimated Time: {data['estimatedTimeRemaining']}")
            print(f"   Session Info: {data['sessionInfo']}")
        else:
            print(f"❌ Job status başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API server'a bağlanılamadı. Server çalışıyor mu?")
    except Exception as e:
        print(f"❌ Job status hatası: {e}")

def test_job_cancel(job_id):
    """Job cancel endpoint'ini test et"""
    if not job_id:
        return
        
    print(f"\n❌ Job Cancel Test (Job ID: {job_id})")
    print("-" * 50)
    
    try:
        response = requests.delete(f"{BASE_URL}/api/v1/automation/cancel/{job_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Job cancel başarılı")
            print(f"   Status: {data['data']['status']}")
            print(f"   Cancelled At: {data['data']['cancelledAt']}")
        else:
            print(f"❌ Job cancel başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API server'a bağlanılamadı. Server çalışıyor mu?")
    except Exception as e:
        print(f"❌ Job cancel hatası: {e}")

def test_restart_service():
    """Service restart endpoint'ini test et"""
    print("\n🔄 Service Restart Test")
    print("-" * 30)
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/system/restart")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Service restart başarılı")
            print(f"   Restarted At: {data['data']['restartedAt']}")
            print(f"   New Process ID: {data['data']['newProcessId']}")
            print(f"   Status: {data['data']['status']}")
        else:
            print(f"❌ Service restart başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API server'a bağlanılamadı. Server çalışıyor mu?")
    except Exception as e:
        print(f"❌ Service restart hatası: {e}")

def test_root_endpoint():
    """Root endpoint'ini test et"""
    print("\n🏠 Root Endpoint Test")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint başarılı")
            print(f"   Message: {data['message']}")
            print(f"   Version: {data['version']}")
            print("   Available Endpoints:")
            for name, path in data['endpoints'].items():
                print(f"     {name}: {path}")
        else:
            print(f"❌ Root endpoint başarısız: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ API server'a bağlanılamadı. Server çalışıyor mu?")
    except Exception as e:
        print(f"❌ Root endpoint hatası: {e}")

def main():
    """Ana test fonksiyonu"""
    print("🧪 Ubuntu ChromeDriver API Test Suite")
    print("=" * 50)
    print(f"🌐 API Base URL: {BASE_URL}")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Health Check
    test_health_check()
    
    # Test 2: Root Endpoint
    test_root_endpoint()
    
    # Test 3: Automation Start
    job_id = test_automation_start()
    
    # Test 4: Job Status (birkaç kez)
    if job_id:
        for i in range(3):
            test_job_status(job_id)
            if i < 2:  # Son iterasyonda bekleme yok
                time.sleep(2)
    
    # Test 5: Job Cancel
    if job_id:
        test_job_cancel(job_id)
    
    # Test 6: Service Restart
    test_restart_service()
    
    print("\n🎉 Test Suite tamamlandı!")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Swagger UI: http://localhost:8000/docs")

if __name__ == "__main__":
    main()


