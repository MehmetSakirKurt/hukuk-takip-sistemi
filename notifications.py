#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Bildirim yönetimi modülü
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from typing import List, Dict
import threading
import time
import os
import sys

# Sistem bildirimi için gerekli kütüphaneler
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

# Windows için
if sys.platform == "win32":
    try:
        import win32gui
        import win32con
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False

from database import DatabaseManager

class NotificationManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.notification_time = "09:00"  # Varsayılan bildirim saati
        self.days_ahead = 7  # Kaç gün öncesinden bildirim gönderilecek
        self.last_check_date = None
        
        # Bildirim pencereleri listesi
        self.notification_windows = []
    
    def set_notification_time(self, time_str: str):
        """Bildirim saatini ayarla (HH:MM formatında)"""
        try:
            datetime.strptime(time_str, "%H:%M")
            self.notification_time = time_str
        except ValueError:
            raise ValueError("Geçersiz saat formatı. HH:MM formatında giriniz.")
    
    def set_days_ahead(self, days: int):
        """Kaç gün öncesinden bildirim gönderileceğini ayarla"""
        if days < 1 or days > 30:
            raise ValueError("Gün sayısı 1-30 arasında olmalıdır.")
        self.days_ahead = days
    
    def check_and_send_notifications(self):
        """Yaklaşan tarihleri kontrol et ve bildirim gönder"""
        try:
            today = datetime.now().date()
            
            # Bugün zaten kontrol edilmiş mi?
            if self.last_check_date == today:
                return
            
            # Yaklaşan tarihleri al
            upcoming_dosyalar = self.db_manager.get_upcoming_deadlines(self.days_ahead)
            
            if not upcoming_dosyalar:
                self.last_check_date = today
                return
            
            # Bildirimleri grupla
            notifications = self.prepare_notifications(upcoming_dosyalar)
            
            # Bildirimleri gönder
            for notification_data in notifications:
                self.send_notification(notification_data)
            
            self.last_check_date = today
            
        except Exception as e:
            # Hata durumunda sessizce logla (debug için)
            self.log_error(f"Bildirim kontrolü hatası: {str(e)}")
    
    def prepare_notifications(self, dosyalar: List[Dict]) -> List[Dict]:
        """Bildirimleri hazırla ve grupla"""
        today = datetime.now().date()
        notifications = []
        
        # Tarihe göre grupla
        by_date = {}
        
        for dosya in dosyalar:
            if dosya['tamamlandi']:
                continue
            
            # Son teslim tarihi kontrolü
            try:
                son_teslim = datetime.strptime(dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d').date()
                kalan_gun = (son_teslim - today).days
                
                if kalan_gun <= self.days_ahead:
                    date_key = son_teslim.strftime('%Y-%m-%d')
                    if date_key not in by_date:
                        by_date[date_key] = {'date': son_teslim, 'type': 'son_teslim', 'dosyalar': []}
                    by_date[date_key]['dosyalar'].append({
                        'dosya_numarasi': dosya['dosya_numarasi'],
                        'kalan_gun': kalan_gun,
                        'tarih_str': son_teslim.strftime('%d.%m.%Y')
                    })
            except ValueError as e:
                print(f"Bildirim tarih formatı hatası: {e} - Dosya: {dosya.get('dosya_numarasi', 'N/A')}")
                pass
            
            # Ana avukata sunum tarihi kontrolü
            try:
                sunum_tarihi = datetime.strptime(dosya['ana_avukata_sunum_tarihi'], '%Y-%m-%d').date()
                kalan_gun = (sunum_tarihi - today).days
                
                if kalan_gun <= self.days_ahead:
                    date_key = sunum_tarihi.strftime('%Y-%m-%d') + '_sunum'
                    notifications.append({
                        'title': 'Ana Avukata Sunum Hatırlatması',
                        'type': 'sunum',
                        'dosya_numarasi': dosya['dosya_numarasi'],
                        'tarih': sunum_tarihi,
                        'kalan_gun': kalan_gun,
                        'tarih_str': sunum_tarihi.strftime('%d.%m.%Y')
                    })
            except ValueError as e:
                print(f"Bildirim tarih formatı hatası: {e} - Dosya: {dosya.get('dosya_numarasi', 'N/A')}")
                pass
        
        # Son teslim tarihlerini ekle
        for date_key, data in by_date.items():
            notifications.append({
                'title': 'Dilekçe Son Teslim Hatırlatması',
                'type': 'son_teslim',
                'date': data['date'],
                'dosyalar': data['dosyalar']
            })
        
        return notifications
    
    def send_notification(self, notification_data: Dict):
        """Bildirim gönder"""
        try:
            if notification_data['type'] == 'son_teslim':
                self.send_deadline_notification(notification_data)
            elif notification_data['type'] == 'sunum':
                self.send_presentation_notification(notification_data)
        except Exception as e:
            self.log_error(f"Bildirim gönderme hatası: {str(e)}")
    
    def send_deadline_notification(self, data: Dict):
        """Son teslim tarihi bildirimi gönder"""
        dosyalar = data['dosyalar']
        
        if len(dosyalar) == 1:
            dosya = dosyalar[0]
            title = "Dilekçe Son Teslim Hatırlatması"
            
            if dosya['kalan_gun'] == 0:
                message = f"'{dosya['dosya_numarasi']}' numaralı dosyanın son teslim tarihi bugün!"
            elif dosya['kalan_gun'] == 1:
                message = f"'{dosya['dosya_numarasi']}' numaralı dosyanın son teslim tarihine 1 gün kaldı!"
            else:
                message = f"'{dosya['dosya_numarasi']}' numaralı dosyanın son teslim tarihine {dosya['kalan_gun']} gün kaldı!"
        else:
            title = f"Dilekçe Son Teslim Hatırlatması ({len(dosyalar)} dosya)"
            tarih_str = dosyalar[0]['tarih_str']
            kalan_gun = dosyalar[0]['kalan_gun']
            
            if kalan_gun == 0:
                message = f"{tarih_str} tarihinde {len(dosyalar)} dosyanın son teslim tarihi var!"
            else:
                message = f"{tarih_str} tarihindeki son teslim tarihine {kalan_gun} gün kaldı! ({len(dosyalar)} dosya)"
            
            message += f"\nDosyalar: {', '.join([d['dosya_numarasi'] for d in dosyalar])}"
        
        self.show_notification(title, message, data)
    
    def send_presentation_notification(self, data: Dict):
        """Ana avukata sunum bildirimi gönder"""
        title = "Ana Avukata Sunum Hatırlatması"
        
        if data['kalan_gun'] == 0:
            message = f"'{data['dosya_numarasi']}' numaralı dosyanın ana avukata sunum tarihi bugün!"
        elif data['kalan_gun'] == 1:
            message = f"'{data['dosya_numarasi']}' numaralı dosyanın ana avukata sunum tarihine 1 gün kaldı!"
        else:
            message = f"'{data['dosya_numarasi']}' numaralı dosyanın ana avukata sunum tarihine {data['kalan_gun']} gün kaldı!"
        
        self.show_notification(title, message, data)
    
    def show_notification(self, title: str, message: str, data: Dict):
        """Bildirimi göster"""
        # Önce sistem bildirimi göndermeyi dene
        self.send_system_notification(title, message)
        
        # Sonra uygulama içi bildirim penceresi göster
        self.show_app_notification(title, message, data)
    
    def send_system_notification(self, title: str, message: str):
        """Sistem bildirimi gönder"""
        try:
            if PLYER_AVAILABLE:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Hukuk Takip Sistemi",
                    timeout=10
                )
            elif WIN32_AVAILABLE and sys.platform == "win32":
                # Windows için alternatif yöntem
                self.show_windows_notification(title, message)
            else:
                # Linux için notify-send dene
                if os.system("which notify-send > /dev/null 2>&1") == 0:
                    os.system(f'notify-send "{title}" "{message}"')
        except:
            pass  # Sistem bildirimi gösterilemezse sessizce devam et
    
    def show_windows_notification(self, title: str, message: str):
        """Windows sistem bildirimi göster"""
        try:
            import win32api
            import win32con
            
            win32api.MessageBox(0, message, title, win32con.MB_OK | win32con.MB_TOPMOST)
        except:
            pass
    
    def show_app_notification(self, title: str, message: str, data: Dict):
        """Uygulama içi bildirim penceresi göster"""
        try:
            # Ana thread'de çalıştır
            if hasattr(tk, '_default_root') and tk._default_root:
                tk._default_root.after(0, lambda: self._create_notification_window(title, message, data))
        except:
            pass
    
    def _create_notification_window(self, title: str, message: str, data: Dict):
        """Bildirim penceresi oluştur"""
        try:
            # Mevcut bildirim pencerelerini temizle
            self.cleanup_notification_windows()
            
            # Yeni bildirim penceresi oluştur
            notification_window = NotificationWindow(title, message, data)
            self.notification_windows.append(notification_window)
            
        except Exception as e:
            # Hata durumunda basit messagebox göster
            messagebox.showinfo(title, message)
    
    def cleanup_notification_windows(self):
        """Kapatılmış bildirim pencerelerini temizle"""
        self.notification_windows = [w for w in self.notification_windows if w.is_alive()]
    
    def manual_check(self):
        """Manuel bildirim kontrolü (test için)"""
        self.last_check_date = None  # Son kontrol tarihini sıfırla
        self.check_and_send_notifications()
    
    def log_error(self, error_message: str):
        """Hata logu (debug için)"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"{timestamp}: {error_message}\n"
            
            with open("hukuk_takip_errors.log", "a", encoding="utf-8") as f:
                f.write(log_message)
        except:
            pass  # Log yazılamıyorsa sessizce devam et


class NotificationWindow:
    def __init__(self, title: str, message: str, data: Dict):
        self.title = title
        self.message = message
        self.data = data
        self.window = None
        self.is_window_alive = True
        
        self.create_window()
    
    def create_window(self):
        """Bildirim penceresini oluştur"""
        try:
            self.window = tk.Toplevel()
            self.window.title(self.title)
            self.window.geometry("400x250")
            
            # Pencereyi her zaman üstte tut
            self.window.attributes('-topmost', True)
            
            # Pencereyi ekranın sağ alt köşesine yerleştir
            self.window.update_idletasks()
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = screen_width - self.window.winfo_width() - 50
            y = screen_height - self.window.winfo_height() - 100
            self.window.geometry(f"+{x}+{y}")
            
            # İçeriği oluştur
            self.create_content()
            
            # Pencere kapatılma olayını yakala
            self.window.protocol("WM_DELETE_WINDOW", self.close_window)
            
            # 10 saniye sonra otomatik kapat
            self.window.after(10000, self.auto_close)
            
            # Pencereyi göster
            self.window.focus_force()
            
        except Exception as e:
            self.is_window_alive = False
            # Pencere oluşturulamıyorsa basit messagebox göster
            messagebox.showinfo(self.title, self.message)
    
    def create_content(self):
        """Pencere içeriğini oluştur"""
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # İkon (emoji)
        icon_text = "⚠️" if "Son Teslim" in self.title else "📋"
        icon_label = tk.Label(main_frame, text=icon_text, font=('Arial', 24), bg='#f0f0f0')
        icon_label.pack(pady=(0, 10))
        
        # Başlık
        title_label = tk.Label(main_frame, text=self.title, 
                              font=('Arial', 12, 'bold'), bg='#f0f0f0')
        title_label.pack(pady=(0, 10))
        
        # Mesaj
        message_label = tk.Label(main_frame, text=self.message, 
                                font=('Arial', 10), bg='#f0f0f0', 
                                wraplength=350, justify='center')
        message_label.pack(pady=(0, 20))
        
        # Butonlar
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack()
        
        ok_button = tk.Button(button_frame, text="Tamam", 
                             command=self.close_window, 
                             bg='#4CAF50', fg='white', 
                             font=('Arial', 10, 'bold'),
                             padx=20)
        ok_button.pack(side=tk.LEFT, padx=5)
        
        snooze_button = tk.Button(button_frame, text="1 Saat Sonra Hatırlat", 
                                 command=self.snooze_notification, 
                                 bg='#FF9800', fg='white', 
                                 font=('Arial', 10),
                                 padx=20)
        snooze_button.pack(side=tk.LEFT, padx=5)
    
    def close_window(self):
        """Pencereyi kapat"""
        self.is_window_alive = False
        if self.window:
            self.window.destroy()
    
    def auto_close(self):
        """Otomatik kapatma"""
        if self.is_window_alive:
            self.close_window()
    
    def snooze_notification(self):
        """Bildirimi 1 saat sonraya ertele"""
        self.close_window()
        # Gerçek bir uygulamada burada ertele mantığı olurdu
        # Şimdilik sadece pencereyi kapat
    
    def is_alive(self):
        """Pencere hala açık mı?"""
        return self.is_window_alive and self.window and self.window.winfo_exists()


# Test fonksiyonu
def test_notification_system():
    """Bildirim sistemini test et"""
    from database import DatabaseManager
    
    db = DatabaseManager()
    notification_manager = NotificationManager(db)
    
    # Test bildirimi gönder
    test_data = {
        'title': 'Test Bildirimi',
        'type': 'son_teslim',
        'dosyalar': [{
            'dosya_numarasi': 'TEST-001',
            'kalan_gun': 1,
            'tarih_str': '01.01.2024'
        }]
    }
    
    notification_manager.send_deadline_notification(test_data)

if __name__ == "__main__":
    test_notification_system()