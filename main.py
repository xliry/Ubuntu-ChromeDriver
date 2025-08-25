#!/usr/bin/env python3
"""
Main entry point for Ubuntu Chrome Automation
Combines API server functionality with Chrome automation
"""

import argparse
import sys
import asyncio
import time
from datetime import datetime
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

from chrome_automation import ChromeAutomation
from session_manager import SessionManager

# FastAPI app
app = FastAPI(
    title="Ubuntu ChromeDriver API",
    description="Chrome automation API for Google Flow",
    version="1.0.0"
)

# CORS middleware - Production BalderAI entegrasyonu
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://balder-ai.vercel.app",  # Production BalderAI
        "http://localhost:3000",         # Development
        "https://localhost:3000",        # Development HTTPS
        "*"                             # Geçici olarak tüm origin'lere izin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (production'da Redis kullanılmalı)
jobs = {}
active_sessions = {}

# Pydantic models
class GoogleFlowRequest(BaseModel):
    jobId: str
    prompt: str
    model: str = "veo-3"
    timestamp: Optional[str] = None
    userId: Optional[str] = None
    action: str = "create_project"
    timeout: int = 300
    callbackUrl: Optional[str] = "https://balder-ai.vercel.app/api/jobs/callback"  # Default production callback

class JobResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

class JobStatus(BaseModel):
    jobId: str
    status: str
    progress: int
    currentStep: str
    estimatedTimeRemaining: str
    sessionInfo: Dict[str, Any]

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    components: Dict[str, Any]

class RestartResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]

# Background task for automation
async def run_automation(job_id: str, prompt: str, user_id: str, callback_url: str = None):
    """Background'da automation çalıştır"""
    try:
        job = jobs[job_id]
        job["status"] = "processing"
        job["currentStep"] = "Automation başlatılıyor"
        job["progress"] = 0
        
        # Chrome automation başlat
        automation = ChromeAutomation()
        
        # Progress callback'leri için wrapper
        def progress_callback(step: str, progress: int):
            job["currentStep"] = step
            job["progress"] = progress
            print(f"Job {job_id}: {step} - Progress: {progress}%")
        
        # Automation'ı çalıştır
        success = automation.start_test(
            user_id=user_id or "api_user",
            prompt=prompt
        )
        
        if success:
            job["status"] = "completed"
            job["progress"] = 100
            job["currentStep"] = "Video başarıyla oluşturuldu"
            
            # Production callback gönder
            if callback_url:
                await send_production_callback(job_id, "completed", callback_url)
        else:
            job["status"] = "failed"
            job["currentStep"] = "Video oluşturma başarısız"
            
            # Error callback gönder
            if callback_url:
                await send_production_callback(job_id, "failed", callback_url, error="Video creation failed")
            
    except Exception as e:
        job["status"] = "error"
        job["currentStep"] = f"Hata: {str(e)}"
        print(f"Job {job_id} hatası: {e}")
        
        # Error callback gönder
        if callback_url:
            await send_production_callback(job_id, "error", callback_url, error=str(e))
    finally:
        if 'automation' in locals():
            automation.close_browser()

async def send_production_callback(job_id: str, status: str, callback_url: str, error: str = None, result_url: str = None):
    """Production BalderAI callback sistemi"""
    try:
        import requests
        
        # Localhost URL'lerini production'a çevir
        if "localhost:3000" in callback_url:
            callback_url = callback_url.replace("http://localhost:3000", "https://balder-ai.vercel.app")
            callback_url = callback_url.replace("https://localhost:3000", "https://balder-ai.vercel.app")
        
        # Default production callback URL
        if not callback_url or callback_url == "None":
            callback_url = "https://balder-ai.vercel.app/api/jobs/callback"
        
        payload = {
            "jobId": job_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "origin": "https://balder-ai.vercel.app"
        }
        
        if error:
            payload["error"] = error
        
        if result_url:
            payload["resultUrl"] = result_url
            payload["fileSize"] = "5.2MB"  # Default file size
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Appium-Agent/1.0",
            "Origin": "https://balder-ai.vercel.app"
        }
        
        print(f"📤 Sending callback to {callback_url}")
        print(f"📦 Payload: {payload}")
        
        response = requests.post(callback_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Callback sent successfully to {callback_url}")
        else:
            print(f"❌ Callback failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Callback error: {e}")

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ubuntu ChromeDriver API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        components={
            "api": "running",
            "chrome": "available",
            "session_manager": "available"
        }
    )

@app.post("/api/google-flow", response_model=JobResponse)
async def google_flow_endpoint(request: GoogleFlowRequest, background_tasks: BackgroundTasks):
    """Google Flow video generation endpoint - Production BalderAI entegrasyonu"""
    try:
        # Job oluştur
        job_id = request.jobId or str(uuid.uuid4())
        jobs[job_id] = {
            "id": job_id,
            "prompt": request.prompt,
            "model": request.model,
            "userId": request.userId,
            "status": "queued",
            "progress": 0,
            "currentStep": "Job kuyruğa alındı",
            "created_at": datetime.now().isoformat(),
            "timeout": request.timeout,
            "callbackUrl": request.callbackUrl
        }
        
        # Production callback URL'ini kontrol et
        callback_url = request.callbackUrl
        if not callback_url or callback_url == "None":
            callback_url = "https://balder-ai.vercel.app/api/jobs/callback"
        
        print(f"🚀 Starting automation for job {job_id}")
        print(f"📝 Prompt: {request.prompt}")
        print(f"👤 User ID: {request.userId}")
        print(f"📞 Callback URL: {callback_url}")
        
        # Background task olarak automation'ı başlat
        background_tasks.add_task(
            run_automation, 
            job_id, 
            request.prompt, 
            request.userId or "default_user",
            callback_url
        )
        
        return JobResponse(
            success=True,
            message="Job başarıyla başlatıldı - BalderAI Production",
            data={
                "jobId": job_id,
                "status": "queued",
                "estimatedTime": "5-10 dakika",
                "callbackUrl": callback_url,
                "origin": "https://balder-ai.vercel.app"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Job durumunu sorgula"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    
    job = jobs[job_id]
    
    # Session bilgilerini al
    session_info = {}
    try:
        session_manager = SessionManager()
        session_info = session_manager.get_session_info()
    except:
        session_info = {"status": "session_error"}
    
    return JobStatus(
        jobId=job_id,
        status=job["status"],
        progress=job["progress"],
        currentStep=job["currentStep"],
        estimatedTimeRemaining="Hesaplanıyor...",
        sessionInfo=session_info
    )

@app.post("/api/restart", response_model=RestartResponse)
async def restart_service():
    """Servisi yeniden başlat"""
    try:
        # Session'ları temizle
        session_manager = SessionManager()
        session_manager.clear_session()
        
        # Job'ları temizle
        jobs.clear()
        
        return RestartResponse(
            success=True,
            message="Servis başarıyla yeniden başlatıldı",
            data={"timestamp": datetime.now().isoformat()}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-callback")
async def test_callback():
    """Production callback sistemini test et"""
    try:
        test_job_id = f"test_{int(time.time())}"
        callback_url = "https://balder-ai.vercel.app/api/jobs/callback"
        
        await send_production_callback(
            job_id=test_job_id,
            status="test",
            callback_url=callback_url,
            result_url="https://immensely-ace-jaguar.ngrok-free.app/media/downloaded_videos/test.mp4"
        )
        
        return {
            "success": True,
            "message": "Test callback sent to BalderAI production",
            "jobId": test_job_id,
            "callbackUrl": callback_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Main function - API server'ı başlat"""
    parser = argparse.ArgumentParser(
        description="Ubuntu Chrome Automation - API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py                    # API server'ı başlat (varsayılan port 8000)
  python main.py --port 8080        # Farklı port'ta başlat
  python main.py --host 0.0.0.0     # Tüm IP'lerden erişime aç
  python main.py --test-session     # Session manager'ı test et
  python main.py --clear-session    # Session'ı temizle
  python main.py --session-info     # Session bilgilerini göster
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="API server port'u (varsayılan: 8000)"
    )
    
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1",
        help="API server host'u (varsayılan: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--test-session", 
        action="store_true",
        help="Session manager'ı test et"
    )
    
    parser.add_argument(
        "--clear-session", 
        action="store_true",
        help="Mevcut session'ı temizle"
    )
    
    parser.add_argument(
        "--session-info", 
        action="store_true",
        help="Mevcut session bilgilerini göster"
    )
    
    args = parser.parse_args()
    
    print("🚀 Ubuntu Chrome Automation API Server")
    print("=" * 50)
    
    # Check if running on Ubuntu/Linux
    if sys.platform not in ["linux", "linux2"]:
        print("⚠️ Bu script Ubuntu/Linux sistemler için tasarlanmıştır")
        print(f"   Mevcut platform: {sys.platform}")
        response = input("Devam etmek istiyor musunuz? (y/N): ")
        if response.lower() not in ["y", "yes"]:
            print("❌ Script durduruldu")
            sys.exit(1)
    
    # Handle session management commands
    if args.test_session:
        test_session_manager()
        return
    
    if args.clear_session:
        clear_session()
        return
    
    if args.session_info:
        show_session_info()
        return
    
    # Start API server
    print(f"🌐 API Server başlatılıyor...")
    print(f"📍 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"📖 API Docs: http://{args.host}:{args.port}/docs")
    print("=" * 50)
    
    uvicorn.run(app, host=args.host, port=args.port)


def test_session_manager():
    """Test session manager functionality"""
    print("🧪 Session Manager Test")
    print("-" * 30)
    
    try:
        manager = SessionManager()
        
        # Test session creation
        print("1. Test session oluşturuluyor...")
        if manager.create_session("test@example.com", "password123", 1000):
            print("   ✅ Test session oluşturuldu")
        else:
            print("   ❌ Test session oluşturulamadı")
            return
        
        # Test session status
        print("2. Session status kontrol ediliyor...")
        status = manager.check_session_status()
        print(f"   Session status: {status}")
        
        # Test credentials
        print("3. Credentials alınıyor...")
        creds = manager.get_current_credentials()
        if creds:
            print(f"   Email: {creds['email']}")
            print(f"   Password: {creds['password']}")
        else:
            print("   ❌ Credentials alınamadı")
        
        # Test session info
        print("4. Session bilgileri alınıyor...")
        info = manager.get_session_info()
        print(f"   Session info: {info}")
        
        # Cleanup
        print("5. Test session temizleniyor...")
        manager.clear_session()
        print("   ✅ Test session temizlendi")
        
        print("\n🎉 Session Manager test başarılı!")
        
    except Exception as e:
        print(f"❌ Session Manager test hatası: {e}")


def clear_session():
    """Clear current session"""
    print("🗑️ Session Temizleme")
    print("-" * 30)
    
    try:
        manager = SessionManager()
        manager.clear_session()
        print("✅ Session başarıyla temizlendi")
    except Exception as e:
        print(f"❌ Session temizleme hatası: {e}")


def show_session_info():
    """Show current session information"""
    print("ℹ️ Session Bilgileri")
    print("-" * 30)
    
    try:
        manager = SessionManager()
        info = manager.get_session_info()
        
        if info["status"] == "no_session":
            print("❌ Aktif session bulunamadı")
        else:
            print(f"📧 Email: {info['email']}")
            print(f"💳 Krediler: {info['credits']}")
            print(f"📊 Durum: {info['status']}")
            print(f"🎯 İlk Erişim: {info['first_access']}")
            print(f"✅ Onboarding: {info['onboarding']}")
            print(f"⏰ Bitiş: {info['expires']}")
            
    except Exception as e:
        print(f"❌ Session bilgisi alma hatası: {e}")


if __name__ == "__main__":
    main()


