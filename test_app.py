#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Test betiği
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

# Proje modüllerini import et
try:
    from database import DatabaseManager
    from notifications import NotificationManager
    import main
    print("✅ Tüm modüller başarıyla import edildi")
except ImportError as e:
    print(f"❌ Modül import hatası: {e}")
    sys.exit(1)

class TestDatabaseManager(unittest.TestCase):
    """Veritabanı yöneticisi testleri"""
    
    def setUp(self):
        """Test öncesi kurulum"""
        self.db = DatabaseManager("test_db.db")
        
    def tearDown(self):
        """Test sonrası temizlik"""
        self.db.close()
        if os.path.exists("test_db.db"):
            os.remove("test_db.db")
    
    def test_add_dosya(self):
        """Dosya ekleme testi"""
        result = self.db.add_dosya("TEST-001", "2024-12-31", "Test notları")
        self.assertTrue(result)
        
        dosyalar = self.db.get_all_dosyalar()
        self.assertEqual(len(dosyalar), 1)
        self.assertEqual(dosyalar[0]['dosya_numarasi'], "TEST-001")
    
    def test_duplicate_dosya(self):
        """Aynı dosya numarası ekleme testi"""
        self.db.add_dosya("TEST-001", "2024-12-31", "Test notları")
        
        with self.assertRaises(Exception):  # Duplicate key hatası bekleniyor
            self.db.add_dosya("TEST-001", "2024-12-30", "Başka notlar")
    
    def test_update_dosya(self):
        """Dosya güncelleme testi"""
        self.db.add_dosya("TEST-001", "2024-12-31", "Test notları")
        dosyalar = self.db.get_all_dosyalar()
        dosya_id = dosyalar[0]['id']
        
        result = self.db.update_dosya(dosya_id, dosya_numarasi="TEST-002")
        self.assertTrue(result)
        
        updated_dosya = self.db.get_dosya_by_id(dosya_id)
        self.assertEqual(updated_dosya['dosya_numarasi'], "TEST-002")
    
    def test_delete_dosya(self):
        """Dosya silme testi"""
        self.db.add_dosya("TEST-001", "2024-12-31", "Test notları")
        dosyalar = self.db.get_all_dosyalar()
        dosya_id = dosyalar[0]['id']
        
        result = self.db.delete_dosya(dosya_id)
        self.assertTrue(result)
        
        dosyalar_after = self.db.get_all_dosyalar()
        self.assertEqual(len(dosyalar_after), 0)
    
    def test_search_dosyalar(self):
        """Dosya arama testi"""
        self.db.add_dosya("TEST-001", "2024-12-31", "Önemli dosya")
        self.db.add_dosya("TEST-002", "2024-12-30", "Normal dosya")
        
        results = self.db.search_dosyalar("TEST-001")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['dosya_numarasi'], "TEST-001")
        
        results = self.db.search_dosyalar("Önemli")
        self.assertEqual(len(results), 1)
    
    def test_date_calculation(self):
        """Tarih hesaplama testi"""
        self.db.add_dosya("TEST-001", "2024-12-31", "Test")
        dosyalar = self.db.get_all_dosyalar()
        
        # Ana avukata sunum tarihi 2 gün öncesi olmalı
        dilekce_tarihi = datetime.strptime(dosyalar[0]['dilekce_son_teslim_tarihi'], '%Y-%m-%d')
        sunum_tarihi = datetime.strptime(dosyalar[0]['ana_avukata_sunum_tarihi'], '%Y-%m-%d')
        
        fark = (dilekce_tarihi - sunum_tarihi).days
        self.assertEqual(fark, 2)

class TestNotificationManager(unittest.TestCase):
    """Bildirim yöneticisi testleri"""
    
    def setUp(self):
        """Test öncesi kurulum"""
        self.db = DatabaseManager("test_notification_db.db")
        self.notification_manager = NotificationManager(self.db)
        
    def tearDown(self):
        """Test sonrası temizlik"""
        self.db.close()
        if os.path.exists("test_notification_db.db"):
            os.remove("test_notification_db.db")
    
    def test_upcoming_deadlines(self):
        """Yaklaşan tarihler testi"""
        # Yarın için bir dosya ekle
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.db.add_dosya("TEST-001", tomorrow, "Yarınki dosya")
        
        # Gelecek hafta için bir dosya ekle
        next_week = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
        self.db.add_dosya("TEST-002", next_week, "Gelecek haftaki dosya")
        
        upcoming = self.db.get_upcoming_deadlines(7)
        self.assertEqual(len(upcoming), 1)  # Sadece yarınki dosya 7 gün içinde
        self.assertEqual(upcoming[0]['dosya_numarasi'], "TEST-001")

def run_integration_test():
    """Entegrasyon testi"""
    print("\n🔄 Entegrasyon testi başlıyor...")
    
    try:
        # Veritabanı oluştur
        db = DatabaseManager("integration_test.db")
        
        # Test verileri ekle
        test_data = [
            ("DOSYA-001", "2024-12-31", "Yıl sonu dosyası"),
            ("DOSYA-002", "2024-12-15", "Önemli dilekçe"),
            ("DOSYA-003", "2024-11-30", "Acil dosya"),
        ]
        
        for dosya_no, tarih, not_metni in test_data:
            db.add_dosya(dosya_no, tarih, not_metni)
        
        # Verileri kontrol et
        dosyalar = db.get_all_dosyalar()
        assert len(dosyalar) == 3, f"Beklenen 3 dosya, bulunan: {len(dosyalar)}"
        
        # Arama testi
        search_results = db.search_dosyalar("DOSYA-001")
        assert len(search_results) == 1, "Arama sonucu hatalı"
        
        # İstatistik testi
        stats = db.get_statistics()
        assert stats['toplam_dosya'] == 3, "İstatistik hatalı"
        
        # Bildirim yöneticisi testi
        notification_manager = NotificationManager(db)
        
        print("✅ Entegrasyon testi başarılı!")
        
        # Temizlik
        db.close()
        if os.path.exists("integration_test.db"):
            os.remove("integration_test.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Entegrasyon testi başarısız: {str(e)}")
        return False

def check_gui_dependencies():
    """GUI bağımlılıklarını kontrol et"""
    print("\n📋 GUI bağımlılıkları kontrol ediliyor...")
    
    try:
        import tkinter
        print("✅ tkinter mevcut")
    except ImportError:
        print("❌ tkinter bulunamadı!")
        return False
    
    try:
        import tkcalendar
        print("✅ tkcalendar mevcut")
    except ImportError:
        print("⚠️  tkcalendar bulunamadı (isteğe bağlı)")
    
    try:
        import plyer
        print("✅ plyer mevcut")
    except ImportError:
        print("⚠️  plyer bulunamadı (isteğe bağlı)")
    
    return True

def main():
    """Ana test fonksiyonu"""
    print("🧪 Hukuk Bürosu Dilekçe Takip Sistemi - Test Süreci")
    print("=" * 60)
    
    # GUI bağımlılıkları kontrolü
    if not check_gui_dependencies():
        print("❌ Kritik bağımlılıklar eksik!")
        return False
    
    # Unit testleri çalıştır
    print("\n🔬 Unit testleri çalıştırılıyor...")
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestNotificationManager))
    
    # Testleri çalıştır
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        print("❌ Bazı unit testler başarısız!")
        return False
    
    # Entegrasyon testi
    if not run_integration_test():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Tüm testler başarılı!")
    print("\nUygulamanız kullanıma hazır.")
    print("Çalıştırmak için: python main.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Testler başarısız. Lütfen hataları düzeltin.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n❌ Test süreci iptal edildi")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test hatası: {str(e)}")
        sys.exit(1)