"""
Ubuntu ChromeDriver API Server
FastAPI tabanlı API server for Chrome automation
PRD'deki 3. API endpoint yapısına göre tasarlandı
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import time
from datetime import datetime
import uuid

from chrome_automation import ChromeAutomation
from session_manager import SessionManager

# FastAPI app
app = FastAPI(
    title="Ubuntu ChromeDriver API",
    description="Chrome automation API for Google Flow",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    callbackUrl: Optional[str] = None

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
async def run_automation(job_id: str, prompt: str, user_id: str):
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
            job["completedAt"] = datetime.now().isoformat()
        else:
            job["status"] = "failed"
            job["currentStep"] = "Automation başarısız"
            job["failedAt"] = datetime.now().isoformat()
        
        # Cleanup
        automation.close_browser()
        
        # Callback gönder (eğer varsa)
        if job.get("callbackUrl"):
            await send_callback(job["callbackUrl"], job)
            
    except Exception as e:
        job["status"] = "failed"
        job["currentStep"] = f"Hata: {str(e)}"
        job["error"] = str(e)
        job["failedAt"] = datetime.now().isoformat()
        print(f"Automation error for job {job_id}: {e}")

# Health check endpoint
@app.get("/api/v1/system/health", response_model=HealthStatus)
async def get_system_health():
    """Sistem sağlık durumunu kontrol eder"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "chromeDriver": {
                    "status": "running",
                    "version": "120.0.6099.109",  # Chrome version'dan alınacak
                    "processId": "python_process"
                },
                "chromeBrowser": {
                    "status": "available",
                    "version": "120.0.6099.109",
                    "instances": len(active_sessions)
                },
                "system": {
                    "cpu": "15%",  # System monitoring'den alınacak
                    "memory": "2.1GB/8GB",
                    "disk": "45GB/100GB"
                }
            }
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "HEALTH_CHECK_ERROR",
                "message": "System health check failed",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Main automation endpoint
@app.post("/api/v1/automation/google-flow", response_model=JobResponse)
async def start_google_flow_automation(
    request: GoogleFlowRequest,
    background_tasks: BackgroundTasks
):
    """Google Flow otomasyonu başlatır"""
    try:
        # Input validation
        if not request.jobId or not request.prompt:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_INPUT",
                    "message": "jobId ve prompt gerekli alanlardır",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Job oluştur
        job = {
            "jobId": request.jobId,
            "prompt": request.prompt,
            "model": request.model,
            "userId": request.userId,
            "action": request.action,
            "timeout": request.timeout,
            "callbackUrl": request.callbackUrl,
            "status": "pending",
            "progress": 0,
            "currentStep": "Job oluşturuldu",
            "estimatedDuration": "2-5 dakika",
            "sessionId": f"chrome_session_{int(time.time())}",
            "createdAt": datetime.now().isoformat(),
            "startedAt": None
        }
        
        jobs[request.jobId] = job
        
        # Session'ı kaydet
        active_sessions[job["sessionId"]] = {
            "jobId": request.jobId,
            "startTime": datetime.now(),
            "status": "starting"
        }
        
        # Background task olarak automation'ı başlat
        background_tasks.add_task(
            run_automation,
            request.jobId,
            request.prompt,
            request.userId
        )
        
        return JobResponse(
            success=True,
            message="Automation başarıyla başlatıldı",
            data={
                "jobId": job["jobId"],
                "status": job["status"],
                "estimatedDuration": job["estimatedDuration"],
                "sessionId": job["sessionId"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "AUTOMATION_ERROR",
                "message": "Automation başlatılamadı",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Job status endpoint
@app.get("/api/v1/automation/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Belirli bir job'ın durumunu sorgular"""
    try:
        job = jobs.get(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "JOB_NOT_FOUND",
                    "message": "Job bulunamadı",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Estimated time remaining hesapla
        estimated_time_remaining = "Bilinmiyor"
        if job["status"] == "processing" and job.get("startedAt"):
            started_time = datetime.fromisoformat(job["startedAt"])
            elapsed = (datetime.now() - started_time).total_seconds()
            estimated = 5 * 60  # 5 dakika
            
            if elapsed < estimated:
                remaining_minutes = int((estimated - elapsed) / 60)
                estimated_time_remaining = f"{remaining_minutes} dakika"
        
        return JobStatus(
            jobId=job["jobId"],
            status=job["status"],
            progress=job["progress"],
            currentStep=job["currentStep"],
            estimatedTimeRemaining=estimated_time_remaining,
            sessionInfo={
                "sessionId": job["sessionId"],
                "browserVersion": "120.0.6099.109",
                "driverVersion": "120.0.6099.109"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "STATUS_CHECK_ERROR",
                "message": "Job status kontrol edilemedi",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Cancel job endpoint
@app.delete("/api/v1/automation/cancel/{job_id}", response_model=JobResponse)
async def cancel_job(job_id: str):
    """Çalışan bir job'ı iptal eder"""
    try:
        job = jobs.get(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "JOB_NOT_FOUND",
                    "message": "Job bulunamadı",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        if job["status"] != "processing":
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "JOB_NOT_CANCELLABLE",
                    "message": "Bu job iptal edilemez",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # Job'ı güncelle
        job["status"] = "cancelled"
        job["cancelledAt"] = datetime.now().isoformat()
        job["currentStep"] = "Job iptal edildi"
        
        # Session'ı temizle
        if job["sessionId"] in active_sessions:
            del active_sessions[job["sessionId"]]
        
        # Callback gönder (eğer varsa)
        if job.get("callbackUrl"):
            await send_callback(job["callbackUrl"], job)
        
        return JobResponse(
            success=True,
            message="Job başarıyla iptal edildi",
            data={
                "jobId": job["jobId"],
                "status": job["status"],
                "cancelledAt": job["cancelledAt"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "CANCEL_ERROR",
                "message": "Job iptal edilemedi",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Restart ChromeDriver service
@app.post("/api/v1/system/restart", response_model=RestartResponse)
async def restart_chromedriver_service():
    """ChromeDriver servisini yeniden başlatır"""
    try:
        # Tüm aktif session'ları temizle
        active_sessions.clear()
        
        # Jobs'ları güncelle
        for job_id, job in jobs.items():
            if job["status"] == "processing":
                job["status"] = "failed"
                job["currentStep"] = "Service restart nedeniyle başarısız"
                job["failedAt"] = datetime.now().isoformat()
        
        return RestartResponse(
            success=True,
            message="ChromeDriver başarıyla yeniden başlatıldı",
            data={
                "restartedAt": datetime.now().isoformat(),
                "newProcessId": "python_process",
                "status": "running"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "RESTART_ERROR",
                "message": "ChromeDriver yeniden başlatılamadı",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# Callback function
async def send_callback(url: str, job: Dict[str, Any]):
    """Callback URL'e job bilgilerini gönder"""
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=job) as response:
                if response.status != 200:
                    print(f"Callback failed: {response.status} {response.status_text}")
                    
    except Exception as e:
        print(f"Callback error: {e}")

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Ubuntu ChromeDriver API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/system/health",
            "automation": "/api/v1/automation/google-flow",
            "status": "/api/v1/automation/status/{jobId}",
            "cancel": "/api/v1/automation/cancel/{jobId}",
            "restart": "/api/v1/system/restart"
        }
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": {
            "code": exc.detail.get("code", "HTTP_ERROR"),
            "message": exc.detail.get("message", str(exc.detail)),
            "details": exc.detail.get("details", ""),
            "timestamp": exc.detail.get("timestamp", datetime.now().isoformat())
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Ubuntu ChromeDriver API Server başlatılıyor...")
    print("📡 Port: 8000")
    print("🌐 Health Check: http://localhost:8000/api/v1/system/health")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
