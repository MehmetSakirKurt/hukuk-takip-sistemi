#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Kurulum yardımcısı
"""

import sys
import os
import subprocess
import importlib.util

def check_python_version():
    """Python sürümünü kontrol et"""
    if sys.version_info < (3, 7):
        print("❌ Hata: Python 3.7 veya üzeri gerekli!")
        print(f"   Mevcut sürüm: {sys.version}")
        print("   Lütfen Python'u güncelleyin: https://python.org")
        return False
    else:
        print(f"✅ Python sürümü uygun: {sys.version}")
        return True

def check_pip():
    """pip kurulu mu kontrol et"""
    try:
        import pip
        print("✅ pip kurulu")
        return True
    except ImportError:
        print("❌ pip bulunamadı!")
        print("   pip kurulumu için: https://pip.pypa.io/en/stable/installation/")
        return False

def install_package(package_name, optional=False):
    """Paket kurulumu"""
    try:
        print(f"📦 {package_name} kuruluyor...")
        
        # Paket zaten kurulu mu kontrol et
        if package_name == "tkcalendar":
            try:
                import tkcalendar
                print(f"✅ {package_name} zaten kurulu")
                return True
            except ImportError:
                pass
        elif package_name == "plyer":
            try:
                import plyer
                print(f"✅ {package_name} zaten kurulu")
                return True
            except ImportError:
                pass
        
        # Kurulum
        result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package_name} başarıyla kuruldu")
            return True
        else:
            if optional:
                print(f"⚠️  {package_name} kurulamadı (isteğe bağlı)")
                print(f"   Hata: {result.stderr}")
                return True  # İsteğe bağlı paketler için True döndür
            else:
                print(f"❌ {package_name} kurulumu başarısız!")
                print(f"   Hata: {result.stderr}")
                return False
                
    except Exception as e:
        if optional:
            print(f"⚠️  {package_name} kurulumu başarısız (isteğe bağlı): {str(e)}")
            return True
        else:
            print(f"❌ {package_name} kurulumu başarısız: {str(e)}")
            return False

def check_tkinter():
    """tkinter kurulu mu kontrol et"""
    try:
        import tkinter
        print("✅ tkinter kurulu")
        return True
    except ImportError:
        print("❌ tkinter bulunamadı!")
        print("   Linux için: sudo apt-get install python3-tk")
        print("   macOS için: brew install python-tk")
        return False

def check_required_files():
    """Gerekli dosyalar mevcut mu kontrol et"""
    required_files = [
        "main.py",
        "database.py", 
        "gui.py",
        "calendar_view.py",
        "notifications.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Eksik dosyalar:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Tüm gerekli dosyalar mevcut")
        return True

def create_desktop_shortcut():
    """Masaüstü kısayolu oluştur (Windows için)"""
    if sys.platform == "win32":
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Hukuk Takip Sistemi.lnk")
            target = os.path.join(os.getcwd(), "main.py")
            wDir = os.getcwd()
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("✅ Masaüstü kısayolu oluşturuldu")
            return True
            
        except Exception as e:
            print(f"⚠️  Masaüstü kısayolu oluşturulamadı: {str(e)}")
            return False
    else:
        print("ℹ️  Masaüstü kısayolu sadece Windows'ta desteklenir")
        return True

def run_test():
    """Basit test çalıştır"""
    try:
        print("🧪 Sistem testi çalıştırılıyor...")
        
        # Database modülünü test et
        from database import DatabaseManager
        db = DatabaseManager("test.db")
        
        # Test verisi ekle
        db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
        
        # Veriyi oku
        dosyalar = db.get_all_dosyalar()
        if len(dosyalar) == 1:
            print("✅ Veritabanı testi başarılı")
        else:
            print("❌ Veritabanı testi başarısız")
            return False
        
        # Test dosyasını temizle
        db.close()
        if os.path.exists("test.db"):
            os.remove("test.db")
        
        # GUI modülünü import et
        from gui import MainGUI
        print("✅ GUI modülü import edildi")
        
        # Bildirim modülünü import et
        from notifications import NotificationManager
        print("✅ Bildirim modülü import edildi")
        
        print("✅ Tüm testler başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Test başarısız: {str(e)}")
        return False

def main():
    """Ana kurulum fonksiyonu"""
    print("🚀 Hukuk Bürosu Dilekçe Takip Sistemi Kurulum Yardımcısı")
    print("=" * 60)
    
    # Sistem kontrolü
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    if not check_tkinter():
        return False
    
    if not check_required_files():
        return False
    
    # Paket kurulumları
    print("\n📦 Paket kurulumları başlıyor...")
    
    # Temel paketler
    success = True
    
    # İsteğe bağlı paketler
    install_package("tkcalendar", optional=True)
    install_package("plyer", optional=True)
    
    # Windows için ek paket
    if sys.platform == "win32":
        install_package("pywin32", optional=True)
    
    # Test çalıştır
    print("\n🧪 Sistem testi...")
    if not run_test():
        print("⚠️  Bazı testler başarısız oldu, ancak uygulama çalışabilir")
    
    # Masaüstü kısayolu
    print("\n🔗 Kısayol oluşturma...")
    create_desktop_shortcut()
    
    # Sonuç
    print("\n" + "=" * 60)
    print("🎉 Kurulum tamamlandı!")
    print("\nUygulamayı çalıştırmak için:")
    print("   python main.py")
    print("\nveya Windows'ta:")
    print("   main.py dosyasına çift tıklayın")
    
    if sys.platform == "win32":
        print("\nMasaüstündaki kısayolu da kullanabilirsiniz.")
    
    print("\nSorun yaşarsanız README.md dosyasını inceleyin.")
    print("İyi kullanımlar! 🙂")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Kurulum iptal edildi")
    except Exception as e:
        print(f"\n\n❌ Kurulum hatası: {str(e)}")
        print("Lütfen README.md dosyasını kontrol edin")