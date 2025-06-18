#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Temel modül testleri (GUI olmadan)
"""

import os
import sys
from datetime import datetime, timedelta

# Sadace temel modülleri test et
try:
    from database import DatabaseManager
    print("✅ Database modülü import edildi")
except ImportError as e:
    print(f"❌ Database modül hatası: {e}")
    sys.exit(1)

def test_database():
    """Veritabanı temel testleri"""
    print("\n🔬 Veritabanı testleri başlıyor...")
    
    try:
        # Test veritabanı oluştur
        db = DatabaseManager("test_core.db")
        print("✅ Veritabanı oluşturuldu")
        
        # Dosya ekleme testi
        result = db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
        print("✅ Dosya ekleme testi başarılı")
        
        # Verileri okuma testi
        dosyalar = db.get_all_dosyalar()
        assert len(dosyalar) == 1, "Dosya sayısı yanlış"
        assert dosyalar[0]['dosya_numarasi'] == "TEST-001", "Dosya numarası yanlış"
        print("✅ Veri okuma testi başarılı")
        
        # Tarih hesaplama kontrolü
        dilekce_tarihi = datetime.strptime(dosyalar[0]['dilekce_son_teslim_tarihi'], '%Y-%m-%d')
        sunum_tarihi = datetime.strptime(dosyalar[0]['ana_avukata_sunum_tarihi'], '%Y-%m-%d')
        fark = (dilekce_tarihi - sunum_tarihi).days
        assert fark == 2, f"Tarih farkı yanlış: {fark}"
        print("✅ Otomatik tarih hesaplama testi başarılı")
        
        # Arama testi
        search_results = db.search_dosyalar("TEST-001")
        assert len(search_results) == 1, "Arama sonucu hatalı"
        print("✅ Arama testi başarılı")
        
        # Güncelleme testi
        dosya_id = dosyalar[0]['id']
        update_result = db.update_dosya(dosya_id, notlar="Güncellenmiş not")
        assert update_result, "Güncelleme başarısız"
        
        updated_dosya = db.get_dosya_by_id(dosya_id)
        assert updated_dosya['notlar'] == "Güncellenmiş not", "Not güncellenmedi"
        print("✅ Güncelleme testi başarılı")
        
        # İstatistik testi
        stats = db.get_statistics()
        assert stats['toplam_dosya'] == 1, "İstatistik hatalı"
        print("✅ İstatistik testi başarılı")
        
        # Temizlik
        db.close()
        if os.path.exists("test_core.db"):
            os.remove("test_core.db")
        
        print("✅ Tüm veritabanı testleri başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Veritabanı testi başarısız: {str(e)}")
        return False

def test_file_structure():
    """Dosya yapısı kontrolü"""
    print("\n📁 Dosya yapısı kontrol ediliyor...")
    
    required_files = [
        "main.py",
        "database.py", 
        "gui.py",
        "calendar_view.py",
        "notifications.py",
        "requirements.txt",
        "README.md",
        "install.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}")
    
    if missing_files:
        print("❌ Eksik dosyalar:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Tüm gerekli dosyalar mevcut")
        return True

def test_python_version():
    """Python sürüm kontrolü"""
    print(f"\n🐍 Python sürümü: {sys.version}")
    
    if sys.version_info >= (3, 7):
        print("✅ Python sürümü uygun")
        return True
    else:
        print("❌ Python 3.7+ gerekli")
        return False

def test_imports():
    """Modül import testleri"""
    print("\n📦 Modül import testleri...")
    
    modules = [
        "sqlite3",
        "datetime", 
        "threading",
        "time",
        "os",
        "sys",
        "calendar"
    ]
    
    failed_imports = []
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    # İsteğe bağlı modüller
    optional_modules = ["tkcalendar", "plyer"]
    
    print("\nİsteğe bağlı modüller:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ {module} (isteğe bağlı)")
        except ImportError:
            print(f"⚠️  {module} (isteğe bağlı - eksik)")
    
    if failed_imports:
        print(f"❌ Kritik modüller eksik: {failed_imports}")
        return False
    else:
        print("✅ Tüm kritik modüller mevcut")
        return True

def create_sample_data():
    """Örnek veri oluştur"""
    print("\n📊 Örnek veri oluşturuluyor...")
    
    try:
        db = DatabaseManager("hukuk_takip.db")
        
        # Örnek dosyalar
        sample_files = [
            ("2024-DILEKCE-001", "2024-12-31", "Yıl sonu dilekçesi - önemli"),
            ("2024-DILEKCE-002", "2024-12-15", "Acil dilekçe - müvekkil A"),
            ("2024-DILEKCE-003", "2024-11-30", "İcra takibi dilekçesi"),
            ("2024-DILEKCE-004", "2024-12-20", "Temyiz dilekçesi - Dosya B"),
            ("2024-DILEKCE-005", "2024-11-25", "Tazminat davası dilekçesi"),
        ]
        
        added_count = 0
        for dosya_no, tarih, notlar in sample_files:
            try:
                db.add_dosya(dosya_no, tarih, notlar)
                added_count += 1
                print(f"✅ Eklendi: {dosya_no}")
            except Exception as e:
                print(f"⚠️  Zaten mevcut: {dosya_no}")
        
        # İstatistikleri göster
        stats = db.get_statistics()
        print(f"\n📈 Toplam dosya sayısı: {stats['toplam_dosya']}")
        print(f"📈 Yeni eklenen: {added_count}")
        
        db.close()
        
        if added_count > 0:
            print("✅ Örnek veriler oluşturuldu!")
        else:
            print("ℹ️  Örnek veriler zaten mevcut")
        
        return True
        
    except Exception as e:
        print(f"❌ Örnek veri oluşturma hatası: {str(e)}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 Hukuk Bürosu Dilekçe Takip Sistemi - Temel Testler")
    print("=" * 60)
    
    all_passed = True
    
    # Python sürüm kontrolü
    if not test_python_version():
        all_passed = False
    
    # Dosya yapısı kontrolü
    if not test_file_structure():
        all_passed = False
    
    # Modül import testleri
    if not test_imports():
        all_passed = False
    
    # Veritabanı testleri
    if not test_database():
        all_passed = False
    
    # Örnek veri oluştur
    create_sample_data()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Tüm temel testler başarılı!")
        print("\nUygulama temel fonksiyonları çalışır durumda.")
        print("\nGUI testi için (eğer tkinter kuruluysa):")
        print("   python3 main.py")
        print("\nKurulum için:")
        print("   python3 install.py")
    else:
        print("❌ Bazı testler başarısız!")
        print("Lütfen eksik modülleri kurun ve tekrar deneyin.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Test süreci iptal edildi")
        sys.exit(1) 
    except Exception as e:
        print(f"\n\n❌ Test hatası: {str(e)}")
        sys.exit(1)