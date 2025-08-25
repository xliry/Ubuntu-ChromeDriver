"""
ChromeDriver Manager for Ubuntu Chrome Automation
Handles Chrome installation, driver setup, and browser configuration
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config import CHROME_CONFIG, PROFILES_DIR


class ChromeDriverManager:
    """Manages Chrome driver installation and configuration for Ubuntu"""
    
    def __init__(self):
        self.chrome_version: Optional[int] = None
        self.driver_path: Optional[str] = None
        self.ubuntu_chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/snap/bin/google-chrome",
            "/opt/google/chrome/chrome"
        ]
        
    def setup_chrome_driver(self, headless: bool = None) -> Optional[uc.Chrome]:
        """
        Setup and configure Chrome driver for Ubuntu
        
        Args:
            headless: Whether to run in headless mode
            
        Returns:
            Configured Chrome driver instance or None if failed
        """
        try:
            print("🔧 Chrome driver kurulumu başlatılıyor...")
            
            # Check if Chrome is installed
            if not self.is_chrome_installed():
                print("⚠️ Chrome kurulu değil, kurulum başlatılıyor...")
                if not self.install_chrome_if_needed():
                    print("❌ Chrome kurulumu başarısız!")
                    return None
            
            # Get Chrome version
            self.chrome_version = self.get_chrome_version()
            print(f"✅ Chrome versiyonu: {self.chrome_version}")
            
            # Setup Chrome options
            options = self._setup_chrome_options(headless or CHROME_CONFIG["headless"])
            
            # Create profile directory
            profile_path = PROFILES_DIR / f"chrome-profile-{os.getpid()}"
            profile_path.mkdir(exist_ok=True)
            
            # Launch undetected_chromedriver
            driver = uc.Chrome(
                version_main=self.chrome_version,
                options=options,
                headless=headless or CHROME_CONFIG["headless"],
                user_data_dir=str(profile_path)
            )
            
            print("✅ Chrome driver başarıyla kuruldu!")
            return driver
            
        except Exception as e:
            print(f"❌ Chrome driver kurulum hatası: {e}")
            return None
    
    def _setup_chrome_options(self, headless: bool) -> Options:
        """Setup Chrome options for Ubuntu"""
        options = Options()
        
        # Basic options
        if headless:
            options.add_argument("--headless")
        
        # Ubuntu-specific optimizations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        # Performance options
        if CHROME_CONFIG["disable_images"]:
            options.add_argument("--disable-images")
        
        if CHROME_CONFIG["disable_javascript"]:
            options.add_argument("--disable-javascript")
        
        # Security options
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        # User agent
        options.add_argument(f"--user-agent={CHROME_CONFIG['user_agent']}")
        
        # Additional arguments
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-save-password-bubble")
        options.add_argument("--disable-translate")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        
        # Experimental features
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        return options
    
    def get_chrome_version(self) -> int:
        """Get Chrome version from Ubuntu system"""
        for chrome_path in self.ubuntu_chrome_paths:
            if os.path.exists(chrome_path):
                try:
                    result = subprocess.run(
                        [chrome_path, "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        version_str = result.stdout.strip()
                        # Extract major version number
                        # "Google Chrome 120.0.6099.109" -> 120
                        version_parts = version_str.split()
                        if len(version_parts) >= 3:
                            version = version_parts[2].split('.')[0]
                            return int(version)
                            
                except (subprocess.TimeoutExpired, subprocess.SubprocessError, ValueError) as e:
                    print(f"⚠️ Chrome versiyon okuma hatası ({chrome_path}): {e}")
                    continue
        
        # Default to latest stable version if detection fails
        print("⚠️ Chrome versiyonu tespit edilemedi, varsayılan versiyon kullanılıyor")
        return 120
    
    def is_chrome_installed(self) -> bool:
        """Check if Chrome is installed on Ubuntu"""
        for chrome_path in self.ubuntu_chrome_paths:
            if os.path.exists(chrome_path):
                return True
        return False
    
    def install_chrome_if_needed(self) -> bool:
        """Install Chrome if not present"""
        try:
            print("📥 Chrome kurulumu başlatılıyor...")
            
            # Update package list
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            
            # Install dependencies
            subprocess.run([
                "sudo", "apt", "install", "-y", 
                "wget", "gnupg", "ca-certificates"
            ], check=True, capture_output=True)
            
            # Add Google signing key
            subprocess.run([
                "wget", "-q", "-O", "-", 
                "https://dl.google.com/linux/linux_signing_key.pub"
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Add Chrome repository
            repo_line = "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main"
            with open("/tmp/google-chrome.list", "w") as f:
                f.write(repo_line)
            
            subprocess.run([
                "sudo", "cp", "/tmp/google-chrome.list", 
                "/etc/apt/sources.list.d/"
            ], check=True, capture_output=True)
            
            # Install Chrome
            subprocess.run([
                "sudo", "apt", "update"
            ], check=True, capture_output=True)
            
            subprocess.run([
                "sudo", "apt", "install", "-y", "google-chrome-stable"
            ], check=True, capture_output=True)
            
            print("✅ Chrome başarıyla kuruldu!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Chrome kurulum hatası: {e}")
            return False
        except Exception as e:
            print(f"❌ Beklenmeyen kurulum hatası: {e}")
            return False
    
    def get_chrome_path(self) -> Optional[str]:
        """Get the path to installed Chrome binary"""
        for chrome_path in self.ubuntu_chrome_paths:
            if os.path.exists(chrome_path):
                return chrome_path
        return None
    
    def cleanup_profile(self, profile_path: str):
        """Clean up Chrome profile directory"""
        try:
            profile_dir = Path(profile_path)
            if profile_dir.exists():
                import shutil
                shutil.rmtree(profile_dir)
                print(f"✅ Profile temizlendi: {profile_path}")
        except Exception as e:
            print(f"⚠️ Profile temizleme hatası: {e}")


if __name__ == "__main__":
    # Test Chrome manager
    manager = ChromeDriverManager()
    
    if manager.is_chrome_installed():
        print("✅ Chrome kurulu")
        version = manager.get_chrome_version()
        print(f"Chrome versiyonu: {version}")
    else:
        print("❌ Chrome kurulu değil")
        if manager.install_chrome_if_needed():
            print("✅ Chrome kurulumu tamamlandı")
        else:
            print("❌ Chrome kurulumu başarısız")


