#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Ana uygulama dosyası
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime, timedelta
import threading
import time

# Yerel modülleri import et
from database import DatabaseManager
from gui import MainGUI
from notifications import NotificationManager

class HukukTakipSistemi:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hukuk Bürosu Dilekçe Takip Sistemi")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Veritabanı yöneticisini başlat
        self.db_manager = DatabaseManager()
        
        # Bildirim yöneticisini başlat
        self.notification_manager = NotificationManager(self.db_manager)
        
        # Ana GUI'yi başlat
        self.main_gui = MainGUI(self.root, self.db_manager, self.notification_manager)
        
        # Bildirim thread'ini başlat
        self.start_notification_thread()
        
    def start_notification_thread(self):
        """Günlük bildirimleri başlat"""
        def notification_loop():
            while True:
                current_time = datetime.now()
                # Her gün saat 09:00'da bildirimleri kontrol et
                if current_time.hour == 9 and current_time.minute == 0:
                    self.notification_manager.check_and_send_notifications()
                    time.sleep(60)  # 1 dakika bekle
                else:
                    time.sleep(30)  # 30 saniye bekle
        
        # Daemon thread olarak çalıştır (ana program kapandığında otomatik kapansın)
        notification_thread = threading.Thread(target=notification_loop, daemon=True)
        notification_thread.start()
    
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Temiz kapatma"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        self.root.quit()

def main():
    """Ana fonksiyon"""
    try:
        app = HukukTakipSistemi()
        app.run()
    except Exception as e:
        messagebox.showerror("Hata", f"Uygulama başlatılırken hata oluştu: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()