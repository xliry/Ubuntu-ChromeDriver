#!/usr/bin/env python3
"""
Main entry point for Ubuntu Chrome Automation
Handles user input and starts the automation process
"""

import argparse
import sys
from pathlib import Path

from chrome_automation import ChromeAutomation
from session_manager import SessionManager


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Ubuntu Chrome Automation - Google Flow Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py --prompt "A cute cat playing with a ball"
  python main.py --prompt "A dog running in the park" --user-id "user123"
  python main.py --headless --prompt "A bird flying in the sky"
        """
    )
    
    parser.add_argument(
        "--prompt", 
        type=str, 
        default="A cat",
        help="Video oluşturma prompt'u (varsayılan: 'A cat')"
    )
    
    parser.add_argument(
        "--user-id", 
        type=str, 
        default="default_user",
        help="Kullanıcı ID'si (varsayılan: 'default_user')"
    )
    
    parser.add_argument(
        "--headless", 
        action="store_true",
        help="Headless mode'da çalıştır (server environments için)"
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
    
    print("🚀 Ubuntu Chrome Automation")
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
    
    # Set headless mode if requested
    if args.headless:
        import os
        os.environ["CHROME_HEADLESS"] = "true"
        print("🔒 Headless mode aktif")
    
    # Start automation
    start_automation(args.prompt, args.user_id)


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


def start_automation(prompt: str, user_id: str):
    """Start the main automation process"""
    print(f"🎬 Video oluşturma başlatılıyor...")
    print(f"📝 Prompt: {prompt}")
    print(f"👤 User ID: {user_id}")
    print("-" * 50)
    
    automation = ChromeAutomation()
    
    try:
        # Start automation
        success = automation.start_test(
            user_id=user_id,
            prompt=prompt
        )
        
        if success:
            print("\n🎉 Video oluşturma başarıyla tamamlandı!")
            print("📁 Proje detayları session'da saklandı")
        else:
            print("\n❌ Video oluşturma başarısız!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ İşlem kullanıcı tarafından durduruldu")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        automation.close_browser()


if __name__ == "__main__":
    main()


