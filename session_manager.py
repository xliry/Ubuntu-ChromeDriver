"""
Session Manager for Ubuntu Chrome Automation
Handles user sessions, credits, and account switching
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List

from cryptography.fernet import Fernet

from config import SESSION_CONFIG, DATA_DIR


class SessionManager:
    """Manages user sessions, credits, and account switching"""
    
    def __init__(self):
        self.session_file = DATA_DIR / SESSION_CONFIG["session_file"]
        self.credit_threshold = SESSION_CONFIG["credit_threshold"]
        self.session_timeout_hours = SESSION_CONFIG["session_timeout_hours"]
        self.encryption_key_file = Path(SESSION_CONFIG["encryption_key_file"])
        self.cipher = self._get_or_create_cipher()
        
    def _get_or_create_cipher(self) -> Fernet:
        """Get existing encryption key or create new one"""
        if self.encryption_key_file.exists():
            with open(self.encryption_key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.encryption_key_file, "wb") as f:
                f.write(key)
        return Fernet(key)
    
    def check_session_status(self) -> str:
        """
        Check current session status
        
        Returns:
            "valid_with_credits" - Valid session with sufficient credits
            "valid_low_credits" - Valid session but low credits
            "invalid_or_none" - No session or expired
        """
        session = self.get_current_session()
        
        if not session:
            return "invalid_or_none"
        
        # Check if session is expired
        if self.is_session_expired(session):
            return "invalid_or_none"
        
        # Check credits
        credits = session.get("credits_remaining", 0)
        if credits > self.credit_threshold:
            return "valid_with_credits"
        else:
            return "valid_low_credits"
    
    def needs_login(self) -> bool:
        """Check if login is required"""
        return self.check_session_status() != "valid_with_credits"
    
    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Get current session data"""
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, "rb") as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
            
        except Exception as e:
            print(f"⚠️ Session okuma hatası: {e}")
            return None
    
    def is_session_expired(self, session: Dict[str, Any]) -> bool:
        """Check if session is expired"""
        try:
            expires_at = session.get("session_expires")
            if not expires_at:
                return True
            
            expires_datetime = datetime.fromisoformat(expires_at)
            return datetime.now() > expires_datetime
            
        except Exception as e:
            print(f"⚠️ Session süre kontrolü hatası: {e}")
            return True
    
    def create_session(self, email: str, password: str, credits: int = 1000) -> bool:
        """Create new session"""
        try:
            session_data = {
                "email": email,
                "password": self.encrypt_password(password),
                "credits_remaining": credits,
                "last_login": datetime.now().isoformat(),
                "session_expires": (datetime.now() + timedelta(hours=self.session_timeout_hours)).isoformat(),
                "status": "active",
                "first_flow_access": False,
                "onboarding_completed": False,
                "browser_profile": None
            }
            
            self.save_session(session_data)
            print(f"✅ Yeni session oluşturuldu: {email}")
            return True
            
        except Exception as e:
            print(f"❌ Session oluşturma hatası: {e}")
            return False
    
    def update_session(self, updates: Dict[str, Any]) -> bool:
        """Update current session with new data"""
        try:
            session = self.get_current_session()
            if not session:
                return False
            
            session.update(updates)
            self.save_session(session)
            return True
            
        except Exception as e:
            print(f"❌ Session güncelleme hatası: {e}")
            return False
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """Save encrypted session data"""
        try:
            encrypted_data = self.cipher.encrypt(json.dumps(session_data).encode())
            
            with open(self.session_file, "wb") as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Session kaydetme hatası: {e}")
            return False
    
    def encrypt_password(self, password: str) -> str:
        """Encrypt password"""
        return self.cipher.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt password"""
        return self.cipher.decrypt(encrypted_password.encode()).decode()
    
    def get_current_credentials(self) -> Optional[Dict[str, str]]:
        """Get current email and decrypted password"""
        session = self.get_current_session()
        if not session:
            return None
        
        try:
            return {
                "email": session["email"],
                "password": self.decrypt_password(session["password"])
            }
        except Exception as e:
            print(f"❌ Credential çözme hatası: {e}")
            return None
    
    def check_credits_and_switch_if_needed(self) -> bool:
        """Check credits and switch account if needed"""
        session = self.get_current_session()
        
        if session and session.get("credits_remaining", 0) <= self.credit_threshold:
            print(f"⚠️ Düşük kredi: {session.get('credits_remaining', 0)}")
            return self.switch_to_next_account()
        
        return False
    
    def switch_to_next_account(self) -> bool:
        """Switch to next available account"""
        try:
            print("🔄 Hesap değiştirme başlatılıyor...")
            
            # Get next available account
            next_account = self.get_next_available_account()
            
            if next_account:
                # Create new session with new account
                if self.create_session(
                    next_account["email"], 
                    next_account["password"], 
                    next_account["credits"]
                ):
                    print(f"✅ Yeni hesaba geçildi: {next_account['email']}")
                    return True
                else:
                    print("❌ Yeni session oluşturulamadı")
                    return False
            else:
                print("❌ Kullanılabilir hesap bulunamadı")
                return False
                
        except Exception as e:
            print(f"❌ Hesap değiştirme hatası: {e}")
            return False
    
    def get_next_available_account(self) -> Optional[Dict[str, Any]]:
        """Get next available account from pool"""
        accounts = self.load_account_pool()
        
        # Sort by last used time (oldest first)
        accounts.sort(key=lambda x: x.get("last_used", "1970-01-01"))
        
        for account in accounts:
            if account.get("credits", 0) > self.credit_threshold:
                return account
        
        return None
    
    def load_account_pool(self) -> List[Dict[str, Any]]:
        """Load account pool from file"""
        account_file = DATA_DIR / "account_pool.json"
        
        if not account_file.exists():
            # Create default account pool
            default_accounts = [
                {
                    "email": "test1@gmail.com",
                    "password": "password1",
                    "credits": 1000,
                    "last_used": "1970-01-01T00:00:00"
                },
                {
                    "email": "test2@gmail.com", 
                    "password": "password2",
                    "credits": 950,
                    "last_used": "1970-01-01T00:00:00"
                }
            ]
            
            with open(account_file, "w") as f:
                json.dump(default_accounts, f, indent=2)
            
            return default_accounts
        
        try:
            with open(account_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Account pool okuma hatası: {e}")
            return []
    
    def update_account_usage(self, email: str, credits_used: int = 0):
        """Update account usage and credits"""
        try:
            accounts = self.load_account_pool()
            
            for account in accounts:
                if account["email"] == email:
                    account["credits"] = max(0, account["credits"] - credits_used)
                    account["last_used"] = datetime.now().isoformat()
                    break
            
            # Save updated accounts
            account_file = DATA_DIR / "account_pool.json"
            with open(account_file, "w") as f:
                json.dump(accounts, f, indent=2)
            
            # Update current session
            if credits_used > 0:
                self.update_session({"credits_remaining": max(0, self.get_current_session().get("credits_remaining", 0) - credits_used)})
                
        except Exception as e:
            print(f"⚠️ Account usage güncelleme hatası: {e}")
    
    def is_first_flow_access(self) -> bool:
        """Check if this is first time accessing Flow"""
        session = self.get_current_session()
        if not session:
            return True
        
        return not session.get("first_flow_access", False)
    
    def mark_flow_onboarding_completed(self):
        """Mark Flow onboarding as completed"""
        self.update_session({
            "first_flow_access": True,
            "onboarding_completed": True
        })
    
    def clear_session(self):
        """Clear current session"""
        try:
            if self.session_file.exists():
                os.remove(self.session_file)
                print("✅ Session temizlendi")
        except Exception as e:
            print(f"⚠️ Session temizleme hatası: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information for debugging"""
        session = self.get_current_session()
        if not session:
            return {"status": "no_session"}
        
        return {
            "email": session.get("email"),
            "credits": session.get("credits_remaining"),
            "status": session.get("status"),
            "first_access": session.get("first_flow_access"),
            "onboarding": session.get("onboarding_completed"),
            "expires": session.get("session_expires")
        }


if __name__ == "__main__":
    # Test session manager
    manager = SessionManager()
    
    print("=== Session Manager Test ===")
    
    # Create test session
    if manager.create_session("test@example.com", "password123", 1000):
        print("✅ Test session oluşturuldu")
        
        # Check status
        status = manager.check_session_status()
        print(f"Session status: {status}")
        
        # Get credentials
        creds = manager.get_current_credentials()
        if creds:
            print(f"Email: {creds['email']}")
            print(f"Password: {creds['password']}")
        
        # Get session info
        info = manager.get_session_info()
        print(f"Session info: {info}")
        
        # Cleanup
        manager.clear_session()
    else:
        print("❌ Test session oluşturulamadı")


