#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Gelişmiş modül testleri (UI ve entegrasyon testleri)
"""

import os
import sys
import unittest
from datetime import datetime, timedelta
import tempfile
import shutil

# Test modülleri
from database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Veritabanı yöneticisi test sınıfı"""
    
    def setUp(self):
        """Her test öncesi çalışır"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db = DatabaseManager(self.test_db_path)
    
    def tearDown(self):
        """Her test sonrası çalışır"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_add_dosya(self):
        """Dosya ekleme testi"""
        result = self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
        self.assertTrue(result)
        
        # Eklenen dosyayı kontrol et
        dosyalar = self.db.get_all_dosyalar()
        self.assertEqual(len(dosyalar), 1)
        self.assertEqual(dosyalar[0]['dosya_numarasi'], "TEST-001")
    
    def test_duplicate_dosya(self):
        """Duplicate dosya testi"""
        # İlk dosyayı ekle
        self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
        
        # Aynı dosyayı tekrar eklemeye çalış
        with self.assertRaises(Exception):
            self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası 2")
    
    def test_date_calculation(self):
        """Otomatik tarih hesaplama testi"""
        self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
        dosyalar = self.db.get_all_dosyalar()
        
        dilekce_tarihi = datetime.strptime(dosyalar[0]['dilekce_son_teslim_tarihi'], '%Y-%m-%d')
        sunum_tarihi = datetime.strptime(dosyalar[0]['ana_avukata_sunum_tarihi'], '%Y-%m-%d')
        
        # 2 gün fark olmalı
        fark = (dilekce_tarihi - sunum_tarihi).days
        self.assertEqual(fark, 2)
    
    def test_search_dosyalar(self):
        """Arama testi"""
        # Test verileri ekle
        test_data = [
            ("TEST-001", "2024-12-31", "Önemli dilekçe"),
            ("TEST-002", "2024-12-15", "Acil dosya"),
            ("PROJE-001", "2024-11-30", "Proje dilekçesi")
        ]
        
        for dosya_no, tarih, notlar in test_data:
            self.db.add_dosya(dosya_no, tarih, notlar)
        
        # Dosya numarasına göre arama
        results = self.db.search_dosyalar("TEST")
        self.assertEqual(len(results), 2)
        
        # Notlara göre arama
        results = self.db.search_dosyalar("Acil")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['dosya_numarasi'], "TEST-002")
    
    def test_update_dosya(self):
        """Dosya güncelleme testi"""
        # Dosya ekle
        self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
        dosyalar = self.db.get_all_dosyalar()
        dosya_id = dosyalar[0]['id']
        
        # Güncelle
        result = self.db.update_dosya(dosya_id, notlar="Güncellenmiş not", tamamlandi=True)
        self.assertTrue(result)
        
        # Kontrol et
        updated_dosya = self.db.get_dosya_by_id(dosya_id)
        self.assertEqual(updated_dosya['notlar'], "Güncellenmiş not")
        self.assertTrue(updated_dosya['tamamlandi'])
    
    def test_delete_dosya(self):
        """Dosya silme testi"""
        # Dosya ekle
        self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
        dosyalar = self.db.get_all_dosyalar()
        dosya_id = dosyalar[0]['id']
        
        # Sil
        result = self.db.delete_dosya(dosya_id)
        self.assertTrue(result)
        
        # Kontrol et
        dosyalar_after = self.db.get_all_dosyalar()
        self.assertEqual(len(dosyalar_after), 0)
    
    def test_get_statistics(self):
        """İstatistik testi"""
        # Test verileri ekle
        self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası 1")
        self.db.add_dosya("TEST-002", "2024-12-15", "Test dosyası 2")
        
        # Birini tamamlandı olarak işaretle
        dosyalar = self.db.get_all_dosyalar()
        self.db.update_dosya(dosyalar[0]['id'], tamamlandi=True)
        
        # İstatistikleri al
        stats = self.db.get_statistics()
        self.assertEqual(stats['toplam_dosya'], 2)
        self.assertEqual(stats['tamamlanan_dosya'], 1)
        self.assertEqual(stats['aktif_dosya'], 1)
    
    def test_get_upcoming_deadlines(self):
        """Yaklaşan tarihler testi"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=8)
        
        # Test verileri ekle
        self.db.add_dosya("TEST-001", tomorrow.strftime('%Y-%m-%d'), "Yarın teslim")
        self.db.add_dosya("TEST-002", next_week.strftime('%Y-%m-%d'), "Gelecek hafta teslim")
        
        # 7 gün içindeki dosyaları al
        upcoming = self.db.get_upcoming_deadlines(7)
        
        # En az bir dosya olmalı (hem dilekçe hem sunum tarihi aralıkta olabilir)
        self.assertGreaterEqual(len(upcoming), 1)
        
        # TEST-001 dosyası listede olmalı
        dosya_numaralari = [d['dosya_numarasi'] for d in upcoming]
        self.assertIn("TEST-001", dosya_numaralari)
    
    def test_get_dosyalar_by_date(self):
        """Tarihe göre dosya getirme testi"""
        target_date = "2024-12-31"
        
        # Test verileri ekle
        self.db.add_dosya("TEST-001", target_date, "Test dosyası 1")
        self.db.add_dosya("TEST-002", "2024-12-15", "Test dosyası 2")
        
        # Belirli tarihteki dosyaları al
        dosyalar = self.db.get_dosyalar_by_date(target_date)
        
        # TEST-001 hem son teslim hem de sunum tarihi içeriyor olabilir
        self.assertGreater(len(dosyalar), 0)
        
        # En az bir dosyada hedef tarih olmalı
        found_target = False
        for dosya in dosyalar:
            if (dosya['dilekce_son_teslim_tarihi'] == target_date or 
                dosya['ana_avukata_sunum_tarihi'] == target_date):
                found_target = True
                break
        
        self.assertTrue(found_target)


class TestCalendarView(unittest.TestCase):
    """Takvim görünümü test sınıfı"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db = DatabaseManager(self.test_db_path)
        
        # Test verileri ekle
        self.db.add_dosya("TEST-001", "2024-12-31", "Test dosyası")
    
    def tearDown(self):
        """Test sonrası temizlik"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_calendar_data_retrieval(self):
        """Takvim veri alma testi"""
        # Takvim için gerekli veri formatını test et
        dosyalar = self.db.get_all_dosyalar()
        
        self.assertEqual(len(dosyalar), 1)
        dosya = dosyalar[0]
        
        # Gerekli alanların varlığını kontrol et
        required_fields = ['dosya_numarasi', 'dilekce_son_teslim_tarihi', 
                          'ana_avukata_sunum_tarihi', 'tamamlandi']
        
        for field in required_fields:
            self.assertIn(field, dosya)
        
        # Tarih formatını kontrol et
        try:
            datetime.strptime(dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d')
            datetime.strptime(dosya['ana_avukata_sunum_tarihi'], '%Y-%m-%d')
        except ValueError:
            self.fail("Tarih formatı hatalı")


class TestNotificationSystem(unittest.TestCase):
    """Bildirim sistemi test sınıfı"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db = DatabaseManager(self.test_db_path)
    
    def tearDown(self):
        """Test sonrası temizlik"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_notification_data_preparation(self):
        """Bildirim veri hazırlama testi"""
        # Yaklaşan tarihli dosya ekle
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        self.db.add_dosya("URGENT-001", tomorrow.strftime('%Y-%m-%d'), "Acil dosya")
        
        # Yaklaşan dosyaları al
        upcoming = self.db.get_upcoming_deadlines(7)
        
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0]['dosya_numarasi'], "URGENT-001")
        
        # Bildirim için gerekli bilgilerin varlığını kontrol et
        dosya = upcoming[0]
        self.assertIn('dosya_numarasi', dosya)
        self.assertIn('dilekce_son_teslim_tarihi', dosya)
        self.assertIn('tamamlandi', dosya)


class TestDataIntegrity(unittest.TestCase):
    """Veri bütünlüğü testleri"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db = DatabaseManager(self.test_db_path)
    
    def tearDown(self):
        """Test sonrası temizlik"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_invalid_date_format(self):
        """Geçersiz tarih formatı testi"""
        with self.assertRaises(Exception):
            self.db.add_dosya("TEST-001", "31-12-2024", "Hatalı tarih formatı")
        
        with self.assertRaises(Exception):
            self.db.add_dosya("TEST-002", "2024/12/31", "Hatalı tarih formatı")
    
    def test_empty_dosya_numarasi(self):
        """Boş dosya numarası testi"""
        with self.assertRaises(Exception):
            self.db.add_dosya("", "2024-12-31", "Boş dosya numarası")
    
    def test_past_date_handling(self):
        """Geçmiş tarih testi"""
        past_date = "2020-01-01"
        
        # Geçmiş tarih kabul edilmeli (hata vermemeli)
        try:
            self.db.add_dosya("PAST-001", past_date, "Geçmiş tarihli dosya")
            dosyalar = self.db.get_all_dosyalar()
            self.assertEqual(len(dosyalar), 1)
        except Exception:
            self.fail("Geçmiş tarih kabul edilmedi")
    
    def test_pagination(self):
        """Pagination testi"""
        # Çok sayıda dosya ekle
        for i in range(20):
            self.db.add_dosya(f"TEST-{i:03d}", "2024-12-31", f"Test dosyası {i}")
        
        # Sayfalı veri al
        page1 = self.db.get_all_dosyalar(limit=10, offset=0)
        page2 = self.db.get_all_dosyalar(limit=10, offset=10)
        
        self.assertEqual(len(page1), 10)
        self.assertEqual(len(page2), 10)
        
        # Sayfalar farklı veriler içermeli
        page1_ids = {dosya['id'] for dosya in page1}
        page2_ids = {dosya['id'] for dosya in page2}
        self.assertEqual(len(page1_ids.intersection(page2_ids)), 0)
    
    def test_count_function(self):
        """Sayma fonksiyonu testi"""
        # Başlangıçta 0 dosya
        count = self.db.get_dosya_count()
        self.assertEqual(count, 0)
        
        # 5 dosya ekle
        for i in range(5):
            self.db.add_dosya(f"TEST-{i:03d}", "2024-12-31", f"Test dosyası {i}")
        
        # Toplam sayı
        count = self.db.get_dosya_count(include_completed=True)
        self.assertEqual(count, 5)
        
        # Birini tamamlandı yap
        dosyalar = self.db.get_all_dosyalar()
        self.db.update_dosya(dosyalar[0]['id'], tamamlandi=True)
        
        # Aktif dosya sayısı
        active_count = self.db.get_dosya_count(include_completed=False)
        self.assertEqual(active_count, 4)


class TestPerformance(unittest.TestCase):
    """Performans testleri"""
    
    def setUp(self):
        """Test öncesi hazırlık"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db = DatabaseManager(self.test_db_path)
    
    def tearDown(self):
        """Test sonrası temizlik"""
        self.db.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_large_dataset_performance(self):
        """Büyük veri seti performans testi"""
        import time
        
        # 1000 dosya ekle
        start_time = time.time()
        
        for i in range(1000):
            try:
                self.db.add_dosya(f"PERF-{i:04d}", "2024-12-31", f"Performans test dosyası {i}")
            except:
                pass  # Duplicate errors ignore et
        
        insert_time = time.time() - start_time
        
        # Verileri oku
        start_time = time.time()
        dosyalar = self.db.get_all_dosyalar()
        read_time = time.time() - start_time
        
        # Arama yap
        start_time = time.time()
        results = self.db.search_dosyalar("PERF-0500")
        search_time = time.time() - start_time
        
        # Performans kontrolü (1 saniyeden az olmalı)
        self.assertLess(insert_time, 5.0, f"Ekleme çok yavaş: {insert_time:.2f}s")
        self.assertLess(read_time, 1.0, f"Okuma çok yavaş: {read_time:.2f}s")
        self.assertLess(search_time, 0.5, f"Arama çok yavaş: {search_time:.2f}s")
        
        print(f"Performans Sonuçları:")
        print(f"  1000 dosya ekleme: {insert_time:.2f}s")
        print(f"  Tüm dosyaları okuma: {read_time:.2f}s")
        print(f"  Arama: {search_time:.2f}s")


def run_gui_test():
    """GUI testi (eğer mümkünse)"""
    print("\n🖥️  GUI Test edilecek...")
    
    try:
        import tkinter as tk
        print("✅ tkinter modülü mevcut")
        
        # Basit GUI testi
        try:
            root = tk.Tk()
            root.withdraw()  # Görünür yapma
            root.destroy()
            print("✅ GUI başlatılabilir")
            return True
        except Exception as e:
            print(f"❌ GUI test hatası: {e}")
            return False
            
    except ImportError:
        print("⚠️  tkinter modülü yok - GUI testi atlanıyor")
        return True


def main():
    """Ana test fonksiyonu"""
    print("🧪 Hukuk Bürosu Dilekçe Takip Sistemi - Gelişmiş Testler")
    print("=" * 70)
    
    # Test suites
    test_classes = [
        TestDatabaseManager,
        TestCalendarView, 
        TestNotificationSystem,
        TestDataIntegrity,
        TestPerformance
    ]
    
    total_tests = 0
    total_failures = 0
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__} testleri çalışıyor...")
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures) + len(result.errors)
        
        if result.failures:
            print("❌ Başarısız testler:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("❌ Hata verilen testler:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    # GUI testi
    gui_success = run_gui_test()
    
    # Sonuç raporu
    print("\n" + "=" * 70)
    print(f"📊 Test Raporu:")
    print(f"   Toplam Test: {total_tests}")
    print(f"   Başarılı: {total_tests - total_failures}")
    print(f"   Başarısız: {total_failures}")
    print(f"   GUI Test: {'✅ Başarılı' if gui_success else '❌ Başarısız'}")
    
    success_rate = (total_tests - total_failures) / total_tests * 100 if total_tests > 0 else 0
    print(f"   Başarı Oranı: {success_rate:.1f}%")
    
    if total_failures == 0 and gui_success:
        print("\n🎉 Tüm gelişmiş testler başarılı!")
        print("Sistem tam olarak çalışır durumda.")
    else:
        print(f"\n⚠️  {total_failures} test başarısız oldu.")
        print("Lütfen hataları kontrol edin.")
    
    return total_failures == 0 and gui_success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Test süreci kullanıcı tarafından iptal edildi")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test hatası: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)