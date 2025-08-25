"""
Main Chrome Automation Class for Ubuntu Chrome Automation
Handles Google login, Flow navigation, and project creation
"""

import time
from typing import Optional, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from chrome_manager import ChromeDriverManager
from session_manager import SessionManager
from config import FLOW_CONFIG


class ChromeAutomation:
    """Main automation class for Google Flow operations"""
    
    def __init__(self):
        self.chrome_manager = ChromeDriverManager()
        self.session_manager = SessionManager()
        self.driver = None
        self.wait = None
        
    def start_test(self, user_id: str = None, prompt: str = "A cat") -> bool:
        """
        Start the main automation test
        
        Args:
            user_id: User identifier
            prompt: Project creation prompt
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("=== Ubuntu Chrome Automation Başlatılıyor ===")
            
            # Setup Chrome driver
            self.driver = self.chrome_manager.setup_chrome_driver()
            if not self.driver:
                print("❌ Chrome driver kurulamadı!")
                return False
            
            self.wait = WebDriverWait(self.driver, FLOW_CONFIG["wait_timeout"])
            
            # Check session status (main decision point)
            session_status = self.session_manager.check_session_status()
            
            if session_status == "valid_with_credits":
                print("✅ Geçerli session ve yeterli kredi - direkt Flow'a git")
                return self.navigate_to_flow_directly(prompt, user_id)
                
            elif session_status == "valid_low_credits":
                print("⚠️ Geçerli session ama düşük kredi - hesap değiştir")
                if not self.session_manager.switch_to_next_account():
                    print("❌ Yeni hesaba geçilemedi!")
                    return False
                # Continue with new account
                
            elif session_status == "invalid_or_none":
                print("🔑 Session geçersiz veya yok - login gerekli")
            
            # Perform login flow (only when needed)
            if not self.perform_login_flow():
                return False
            
            # Check credits after login
            if not self.session_manager.check_credits_and_switch_if_needed():
                # Continue to Flow
                return self.navigate_to_flow_with_onboarding_check(prompt, user_id)
            else:
                # Account switched, need to login again
                return self.perform_login_flow()
                
        except Exception as e:
            print(f"❌ Test sırasında hata: {e}")
            return False
    
    def perform_login_flow(self) -> bool:
        """Perform Google login flow"""
        try:
            print("🔑 Google login başlatılıyor...")
            
            # Navigate to Google login
            self.driver.get(FLOW_CONFIG["login_url"])
            time.sleep(2)
            
            # Get credentials
            credentials = self.session_manager.get_current_credentials()
            if not credentials:
                print("❌ Credentials bulunamadı!")
                return False
            
            # Enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "identifier"))
            )
            email_input.clear()
            email_input.send_keys(credentials["email"])
            time.sleep(1)
            
            # Click next button
            next_button = self.driver.find_element(By.ID, "identifierNext")
            next_button.click()
            time.sleep(2)
            
            # Enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.clear()
            password_input.send_keys(credentials["password"])
            time.sleep(1)
            
            # Click next button
            password_next = self.driver.find_element(By.ID, "passwordNext")
            password_next.click()
            time.sleep(3)
            
            # Check for 2FA
            if self.check_2fa_required():
                if not self.handle_2fa():
                    return False
            
            # Verify login success
            if self.is_login_successful():
                print("✅ Login başarılı")
                return True
            else:
                print("❌ Login başarısız")
                return False
                
        except Exception as e:
            print(f"❌ Login hatası: {e}")
            return False
    
    def check_2fa_required(self) -> bool:
        """Check if 2FA is required"""
        try:
            # Look for 2FA input field
            self.driver.find_element(By.NAME, "totpPin")
            return True
        except NoSuchElementException:
            return False
    
    def handle_2fa(self) -> bool:
        """Handle 2FA authentication"""
        try:
            print("⚠️ 2FA kodu gerekli! Lütfen kodu girin...")
            print("⏰ 30 saniye bekleniyor...")
            time.sleep(30)  # Give user time to enter 2FA code
            
            return True
        except Exception as e:
            print(f"❌ 2FA hatası: {e}")
            return False
    
    def is_login_successful(self) -> bool:
        """Check if login was successful"""
        try:
            # Check if we're on Google main page
            current_url = self.driver.current_url
            return ("myaccount.google.com" in current_url or 
                    "accounts.google.com" not in current_url)
        except:
            return False
    
    def navigate_to_flow_with_onboarding_check(self, prompt: str, user_id: str) -> bool:
        """Navigate to Flow and handle onboarding if needed"""
        # Navigate to Flow
        if not self.navigate_to_flow():
            return False
        
        # Check if first time access
        if self.session_manager.is_first_flow_access():
            print("🎯 İlk Flow girişi - onboarding başlatılıyor")
            if not self.handle_flow_onboarding():
                print("⚠️ Onboarding tamamlanamadı")
                return False
            # Mark onboarding as completed
            self.session_manager.mark_flow_onboarding_completed()
        else:
            print("✅ Onboarding daha önce tamamlanmış - direkt proje oluşturmaya geç")
        
        # Continue with project creation
        return self.create_new_project_with_prompt(prompt, user_id)
    
    def navigate_to_flow_directly(self, prompt: str, user_id: str) -> bool:
        """Navigate directly to Flow (bypassing onboarding)"""
        if not self.navigate_to_flow():
            return False
        
        return self.create_new_project_with_prompt(prompt, user_id)
    
    def navigate_to_flow(self) -> bool:
        """Navigate to Google Flow page"""
        try:
            print("🌐 Flow sayfasına gidiliyor...")
            self.driver.get(FLOW_CONFIG["base_url"])
            time.sleep(3)
            
            # Check if we're on Flow page
            if "flow" in self.driver.current_url.lower():
                print("✅ Flow sayfasına başarıyla gidildi")
                return True
            else:
                print("❌ Flow sayfasına gidilemedi")
                return False
                
        except Exception as e:
            print(f"❌ Flow navigasyon hatası: {e}")
            return False
    
    def handle_flow_onboarding(self) -> bool:
        """Handle Flow onboarding steps"""
        try:
            print("🚀 Flow onboarding başlatılıyor...")
            
            # Skip welcome screen
            if not self.skip_welcome_screen():
                print("⚠️ Welcome screen atlanamadı")
            
            # Skip tutorial/guide
            if not self.skip_tutorial_guide():
                print("⚠️ Tutorial guide atlanamadı")
            
            # Handle permissions
            if not self.handle_flow_permissions():
                print("⚠️ Permissions handle edilemedi")
            
            # Complete initial setup
            if not self.complete_initial_setup():
                print("⚠️ Initial setup tamamlanamadı")
            
            print("✅ Flow onboarding tamamlandı")
            return True
            
        except Exception as e:
            print(f"❌ Flow onboarding hatası: {e}")
            return False
    
    def skip_welcome_screen(self) -> bool:
        """Skip Flow welcome screen"""
        try:
            # Look for skip or continue buttons
            skip_selectors = [
                "//button[contains(text(), 'Skip')]",
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'Get Started')]",
                "//button[contains(text(), 'Next')]"
            ]
            
            for selector in skip_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(1)
                    print("✅ Welcome screen atlandı")
                    return True
                except NoSuchElementException:
                    continue
            
            print("⚠️ Welcome screen skip butonu bulunamadı")
            return False
            
        except Exception as e:
            print(f"⚠️ Welcome screen skip hatası: {e}")
            return False
    
    def skip_tutorial_guide(self) -> bool:
        """Skip Flow tutorial/guide"""
        try:
            # Look for tutorial skip options
            tutorial_selectors = [
                "//button[contains(text(), 'Skip Tutorial')]",
                "//button[contains(text(), 'Skip Guide')]",
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Maybe Later')]"
            ]
            
            for selector in tutorial_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(1)
                    print("✅ Tutorial guide atlandı")
                    return True
                except NoSuchElementException:
                    continue
            
            print("⚠️ Tutorial guide skip butonu bulunamadı")
            return False
            
        except Exception as e:
            print(f"⚠️ Tutorial guide skip hatası: {e}")
            return False
    
    def handle_flow_permissions(self) -> bool:
        """Handle Flow permissions requests"""
        try:
            # Look for permission dialogs
            permission_selectors = [
                "//button[contains(text(), 'Allow')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Yes')]",
                "//button[contains(text(), 'OK')]"
            ]
            
            for selector in permission_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(1)
                    print("✅ Permission verildi")
                except NoSuchElementException:
                    continue
            
            return True
            
        except Exception as e:
            print(f"⚠️ Permission handling hatası: {e}")
            return False
    
    def complete_initial_setup(self) -> bool:
        """Complete initial Flow setup"""
        try:
            # Look for setup completion buttons
            setup_selectors = [
                "//button[contains(text(), 'Finish')]",
                "//button[contains(text(), 'Complete')]",
                "//button[contains(text(), 'Done')]",
                "//button[contains(text(), 'Start Creating')]"
            ]
            
            for selector in setup_selectors:
                try:
                    button = self.driver.find_element(By.XPATH, selector)
                    button.click()
                    time.sleep(2)
                    print("✅ Initial setup tamamlandı")
                    return True
                except NoSuchElementException:
                    continue
            
            print("⚠️ Setup completion butonu bulunamadı")
            return False
            
        except Exception as e:
            print(f"⚠️ Setup completion hatası: {e}")
            return False
    
    def create_new_project_with_prompt(self, prompt: str, user_id: str) -> bool:
        """Create new project with given prompt"""
        try:
            print(f"🎬 Yeni proje oluşturuluyor: {prompt}")
            
            # Look for create project button
            create_selectors = [
                "//button[contains(text(), 'Create')]",
                "//button[contains(text(), 'New Project')]",
                "//button[contains(text(), 'Start')]"
            ]
            
            create_button = None
            for selector in create_selectors:
                try:
                    create_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not create_button:
                print("❌ Create project butonu bulunamadı")
                return False
            
            create_button.click()
            time.sleep(2)
            
            # Find prompt input field
            prompt_selectors = [
                "//textarea[@placeholder*='prompt']",
                "//textarea[@placeholder*='description']",
                "//input[@placeholder*='prompt']",
                "//input[@placeholder*='description']"
            ]
            
            prompt_input = None
            for selector in prompt_selectors:
                try:
                    prompt_input = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not prompt_input:
                print("❌ Prompt input alanı bulunamadı")
                return False
            
            # Fill prompt
            prompt_input.clear()
            prompt_input.send_keys(prompt)
            time.sleep(1)
            
            # Submit project creation
            submit_selectors = [
                "//button[contains(text(), 'Create')]",
                "//button[contains(text(), 'Submit')]",
                "//button[contains(text(), 'Generate')]"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.XPATH, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not submit_button:
                print("❌ Submit butonu bulunamadı")
                return False
            
            submit_button.click()
            time.sleep(FLOW_CONFIG["project_creation_delay"])
            
            # Capture project URL
            project_url = self.driver.current_url
            print(f"✅ Proje oluşturuldu: {project_url}")
            
            # Save to session
            self.save_project_to_session(project_url, user_id)
            
            return True
            
        except Exception as e:
            print(f"❌ Proje oluşturma hatası: {e}")
            return False
    
    def save_project_to_session(self, project_url: str, user_id: str):
        """Save project to session"""
        try:
            from datetime import datetime
            
            project_data = {
                "url": project_url,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Update session with project
            self.session_manager.update_session({
                "current_project": project_data
            })
            
            print("✅ Proje session'a kaydedildi")
            
        except Exception as e:
            print(f"⚠️ Proje kaydetme hatası: {e}")
    
    def close_browser(self):
        """Close browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ Browser kapatıldı")
        except Exception as e:
            print(f"⚠️ Browser kapatma hatası: {e}")


if __name__ == "__main__":
    # Test automation
    automation = ChromeAutomation()
    
    try:
        # Start test
        success = automation.start_test(
            user_id="test_user",
            prompt="A cute cat playing with a ball"
        )
        
        if success:
            print("✅ Test başarıyla tamamlandı!")
        else:
            print("❌ Test başarısız!")
            
    except KeyboardInterrupt:
        print("\n⚠️ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Test hatası: {e}")
    finally:
        # Cleanup
        automation.close_browser()

