#!/usr/bin/env python3
"""
Main entry point for Ubuntu Chrome Automation
Combines API server functionality with Chrome automation
"""

import argparse
import sys
import asyncio
import time
from datetime import datetime, timedelta
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

# Pydantic models - Android Agent Ubuntu Migration Guide uyumlu
class CreateProjectRequest(BaseModel):
    prompt: str
    model: str = "veo-3"
    user_id: str
    callback_url: Optional[str] = "https://balder-ai.vercel.app/api/jobs/callback"

class JobResponse(BaseModel):
    success: bool
    job_id: str
    project_url: Optional[str] = None
    project_id: Optional[str] = None
    user_id: str
    status: str
    message: str
    total_videos: int = 0
    is_new_project: bool = True

class JobStatus(BaseModel):
    job_id: str
    status: str
    project_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class UserStats(BaseModel):
    status: str
    user_id: str
    data: Dict[str, Any]
    timestamp: str

class AllUsersStats(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: str

class CleanupRequest(BaseModel):
    days_threshold: int = 30

class CleanupResponse(BaseModel):
    status: str
    message: str
    days_threshold: int
    timestamp: str

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"

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
    """Health check endpoint - Android Agent Ubuntu Migration Guide uyumlu"""
    return HealthStatus(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.post("/api/v1/create-project", response_model=JobResponse)
async def create_project_endpoint(request: CreateProjectRequest, background_tasks: BackgroundTasks):
    """Create video project endpoint - Android Agent Ubuntu Migration Guide uyumlu"""
    try:
        # Job oluştur
        job_id = str(uuid.uuid4())
        project_id = f"project_{int(time.time())}"
        project_url = f"https://labs.google/fx/tools/flow/project/{project_id}"
        
        jobs[job_id] = {
            "id": job_id,
            "prompt": request.prompt,
            "model": request.model,
            "user_id": request.user_id,
            "project_id": project_id,
            "project_url": project_url,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "callback_url": request.callback_url
        }
        
        # Production callback URL'ini kontrol et
        callback_url = request.callback_url
        if not callback_url or callback_url == "None":
            callback_url = "https://balder-ai.vercel.app/api/jobs/callback"
        
        print(f"🚀 Creating project for job {job_id}")
        print(f"📝 Prompt: {request.prompt}")
        print(f"👤 User ID: {request.user_id}")
        print(f"🔗 Project URL: {project_url}")
        print(f"📞 Callback URL: {callback_url}")
        
        # Background task olarak automation'ı başlat
        background_tasks.add_task(
            run_automation, 
            job_id, 
            request.prompt, 
            request.user_id,
            callback_url
        )
        
        return JobResponse(
            success=True,
            job_id=job_id,
            project_url=project_url,
            project_id=project_id,
            user_id=request.user_id,
            status="pending",
            message="Video generation started. Will be ready in ~3 minutes.",
            total_videos=1,
            is_new_project=True
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status - Android Agent Ubuntu Migration Guide uyumlu"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job bulunamadı")
    
    job = jobs[job_id]
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        project_url=job.get("project_url"),
        video_url=job.get("video_url"),
        created_at=job["created_at"],
        completed_at=job.get("completed_at")
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

@app.get("/api/v1/users/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: str):
    """Get user project statistics - Android Agent Ubuntu Migration Guide uyumlu"""
    try:
        # User stats hesapla
        user_jobs = [job for job in jobs.values() if job.get("user_id") == user_id]
        total_videos = len(user_jobs)
        last_activity = max([job["created_at"] for job in user_jobs]) if user_jobs else None
        project_url = user_jobs[-1]["project_url"] if user_jobs else None
        
        return UserStats(
            status="success",
            user_id=user_id,
            data={
                "total_projects": len(set([job.get("project_id") for job in user_jobs])),
                "total_videos": total_videos,
                "last_activity": last_activity,
                "project_url": project_url
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/users/stats/all", response_model=AllUsersStats)
async def get_all_users_stats():
    """Get all users statistics - Android Agent Ubuntu Migration Guide uyumlu"""
    try:
        # Tüm user'ları analiz et
        user_stats = {}
        total_projects = len(set([job.get("project_id") for job in jobs.values() if job.get("project_id")]))
        total_videos = len(jobs)
        
        for job in jobs.values():
            user_id = job.get("user_id")
            if user_id:
                if user_id not in user_stats:
                    user_stats[user_id] = {"total_videos": 0, "last_activity": None}
                user_stats[user_id]["total_videos"] += 1
                if not user_stats[user_id]["last_activity"] or job["created_at"] > user_stats[user_id]["last_activity"]:
                    user_stats[user_id]["last_activity"] = job["created_at"]
        
        return AllUsersStats(
            status="success",
            data={
                "total_users": len(user_stats),
                "total_projects": total_projects,
                "total_videos": total_videos,
                "users": user_stats
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/users/projects/cleanup", response_model=CleanupResponse)
async def cleanup_old_projects(request: CleanupRequest):
    """Cleanup old projects - Android Agent Ubuntu Migration Guide uyumlu"""
    try:
        # Eski job'ları temizle
        cutoff_time = datetime.now() - timedelta(days=request.days_threshold)
        old_jobs = [job_id for job_id, job in jobs.items() 
                   if datetime.fromisoformat(job["created_at"]) < cutoff_time]
        
        for job_id in old_jobs:
            del jobs[job_id]
        
        return CleanupResponse(
            status="success",
            message=f"Cleaned up {len(old_jobs)} old projects",
            days_threshold=request.days_threshold,
            timestamp=datetime.now().isoformat()
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
  python main.py                    # API server'ı başlat (varsayılan port 8080)
  python main.py --port 8000        # Farklı port'ta başlat
  python main.py --host 0.0.0.0     # Tüm IP'lerden erişime aç
  python main.py --test-session     # Session manager'ı test et
  python main.py --clear-session    # Session'ı temizle
  python main.py --session-info     # Session bilgilerini göster
        """
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8080,
        help="API server port'u (varsayılan: 8080)"
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


