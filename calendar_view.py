#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Takvim görünümü modülü
"""

import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import datetime, timedelta, date
from typing import Dict, List
from database import DatabaseManager

class CalendarView:
    def __init__(self, parent, db_manager: DatabaseManager):
        self.parent = parent
        self.db_manager = db_manager
        self.current_date = datetime.now()
        
        # Ana frame
        self.main_frame = ttk.Frame(parent, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Kontrol paneli oluştur
        self.create_control_panel()
        
        # Takvim oluştur
        self.create_calendar()
        
        # Detay paneli oluştur
        self.create_detail_panel()
        
        # Takvimi güncelle
        self.update_calendar()
    
    def create_control_panel(self):
        """Kontrol panelini oluştur"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ay/Yıl navigasyonu
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(side=tk.LEFT)
        
        ttk.Button(nav_frame, text="◀", command=self.prev_month, width=3).pack(side=tk.LEFT)
        
        self.month_year_var = tk.StringVar()
        month_label = ttk.Label(nav_frame, textvariable=self.month_year_var, 
                               font=('Arial', 12, 'bold'), width=20)
        month_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(nav_frame, text="▶", command=self.next_month, width=3).pack(side=tk.LEFT)
        
        ttk.Button(nav_frame, text="Bugün", command=self.go_to_today).pack(side=tk.LEFT, padx=(10, 0))
        
        # Renk kodları açıklaması
        legend_frame = ttk.LabelFrame(control_frame, text="Renk Kodları", padding="5")
        legend_frame.pack(side=tk.RIGHT)
        
        legend_items = [
            ("Son Teslim", "#ffcccc"),
            ("Ana Avukata Sunum", "#ccccff"),
            ("Geçmiş Tarih", "#ff9999"),
            ("Bugün", "#ffff99")
        ]
        
        for i, (text, color) in enumerate(legend_items):
            legend_label = tk.Label(legend_frame, text=f"■ {text}", 
                                  background=color, padx=5, pady=2)
            legend_label.grid(row=0, column=i, padx=2)
    
    def create_calendar(self):
        """Takvim oluştur"""
        # Takvim frame'i
        self.calendar_frame = ttk.Frame(self.main_frame)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True)
        
        # Haftanın günleri başlıkları
        days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        
        for i, day in enumerate(days):
            day_label = ttk.Label(self.calendar_frame, text=day, 
                                 font=('Arial', 10, 'bold'), anchor='center')
            day_label.grid(row=0, column=i, sticky='ew', padx=1, pady=1)
        
        # Grid konfigürasyonu
        for i in range(7):
            self.calendar_frame.columnconfigure(i, weight=1)
        
        # Takvim günleri için liste
        self.day_buttons = []
        
        # 6 satır x 7 sütun = 42 gün
        for week in range(6):
            week_buttons = []
            for day in range(7):
                row = week + 1  # 0. satır başlıklar için
                
                # Gün butonu frame'i
                day_frame = tk.Frame(self.calendar_frame, relief='raised', borderwidth=1,
                                   width=100, height=80)
                day_frame.grid(row=row, column=day, sticky='nsew', padx=1, pady=1)
                day_frame.grid_propagate(False)
                
                # Gün numarası etiketi
                day_label = tk.Label(day_frame, text="", font=('Arial', 12, 'bold'),
                                   background='white', anchor='nw')
                day_label.place(x=5, y=5)
                
                # Dosya bilgileri etiketi
                info_label = tk.Label(day_frame, text="", font=('Arial', 8),
                                    background='white', anchor='nw', justify='left',
                                    wraplength=90)
                info_label.place(x=5, y=25)
                
                # Tıklama olayı
                day_frame.bind('<Button-1>', lambda e, d=(week, day): self.on_day_click(d))
                day_label.bind('<Button-1>', lambda e, d=(week, day): self.on_day_click(d))
                info_label.bind('<Button-1>', lambda e, d=(week, day): self.on_day_click(d))
                
                week_buttons.append({
                    'frame': day_frame,
                    'day_label': day_label,
                    'info_label': info_label,
                    'date': None
                })
                
            self.day_buttons.append(week_buttons)
        
        # Grid satırlarını genişletilebilir yap
        for i in range(7):
            self.calendar_frame.rowconfigure(i, weight=1)
    
    def create_detail_panel(self):
        """Detay panelini oluştur"""
        detail_frame = ttk.LabelFrame(self.main_frame, text="Seçili Günün Detayları", padding="10")
        detail_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.detail_text = tk.Text(detail_frame, height=6, wrap=tk.WORD)
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, 
                                       command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Başlangıçta bugünü seç
        today = datetime.now().date()
        self.show_day_details(today)
    
    def prev_month(self):
        """Önceki aya git"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """Sonraki aya git"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def go_to_today(self):
        """Bugüne git"""
        self.current_date = datetime.now()
        self.update_calendar()
    
    def update_calendar(self):
        """Takvimi güncelle"""
        # Ay/yıl başlığını güncelle
        month_names = [
            '', 'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
            'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
        ]
        month_year_text = f"{month_names[self.current_date.month]} {self.current_date.year}"
        self.month_year_var.set(month_year_text)
        
        # Ayın ilk günü ve gün sayısı
        first_day = self.current_date.replace(day=1)
        days_in_month = calendar.monthrange(self.current_date.year, self.current_date.month)[1]
        
        # İlk günün hafta içindeki pozisyonu (Pazartesi = 0)
        first_weekday = first_day.weekday()
        
        # Bugünün tarihi
        today = datetime.now().date()
        
        # Dosya verilerini al
        dosyalar_by_date = self.get_dosyalar_by_month()
        
        # Takvim günlerini doldur
        current_day = 1
        
        for week in range(6):
            for day in range(7):
                button_info = self.day_buttons[week][day]
                
                # Bu pozisyonda gösterilecek tarih
                if week == 0 and day < first_weekday:
                    # Önceki ayın sonları
                    prev_month_date = first_day - timedelta(days=first_weekday - day)
                    self.setup_day_button(button_info, prev_month_date, dosyalar_by_date, 
                                         is_current_month=False)
                elif current_day <= days_in_month:
                    # Bu ayın günleri
                    current_date = first_day.replace(day=current_day)
                    self.setup_day_button(button_info, current_date, dosyalar_by_date, 
                                         is_current_month=True, is_today=(current_date == today))
                    current_day += 1
                else:
                    # Sonraki ayın başları
                    next_month_start = first_day.replace(month=first_day.month + 1 if first_day.month < 12 else 1,
                                                       year=first_day.year if first_day.month < 12 else first_day.year + 1,
                                                       day=1)
                    next_month_date = next_month_start + timedelta(days=current_day - days_in_month - 1)
                    self.setup_day_button(button_info, next_month_date, dosyalar_by_date, 
                                         is_current_month=False)
                    current_day += 1
    
    def setup_day_button(self, button_info: Dict, date_obj: date, dosyalar_by_date: Dict, 
                        is_current_month: bool = True, is_today: bool = False):
        """Günlük butonu ayarla"""
        button_info['date'] = date_obj
        date_str = date_obj.strftime('%Y-%m-%d')
        
        # Gün numarasını ayarla
        day_text = str(date_obj.day)
        button_info['day_label'].config(text=day_text)
        
        # Renk ve metin ayarları
        bg_color = 'white'
        text_color = 'black'
        info_text = ''
        
        # Bugün mü?
        if is_today:
            bg_color = '#ffff99'
        
        # Bu ay mı?
        if not is_current_month:
            text_color = '#cccccc'
        
        # Bu tarihteki dosyalar var mı?
        if date_str in dosyalar_by_date:
            dosyalar = dosyalar_by_date[date_str]
            
            # Dosya türlerine göre renk belirle
            has_dilekce = any(d['type'] == 'dilekce' for d in dosyalar)
            has_sunum = any(d['type'] == 'sunum' for d in dosyalar)
            
            if has_dilekce and has_sunum:
                bg_color = '#ffddff'  # Mor
            elif has_dilekce:
                if date_obj < datetime.now().date():
                    bg_color = '#ff9999'  # Kırmızı (geçmiş)
                else:
                    bg_color = '#ffcccc'  # Açık kırmızı
            elif has_sunum:
                if date_obj < datetime.now().date():
                    bg_color = '#9999ff'  # Koyu mavi (geçmiş)
                else:
                    bg_color = '#ccccff'  # Açık mavi
            
            # Bilgi metnini oluştur
            dilekce_count = len([d for d in dosyalar if d['type'] == 'dilekce'])
            sunum_count = len([d for d in dosyalar if d['type'] == 'sunum'])
            
            info_parts = []
            if dilekce_count > 0:
                info_parts.append(f"ST: {dilekce_count}")  # Son Teslim
            if sunum_count > 0:
                info_parts.append(f"AS: {sunum_count}")   # Ana avukata Sunum
            
            info_text = '\n'.join(info_parts)
        
        # Bugün ise rengi koru ama kenarlık ekle
        if is_today and bg_color == 'white':
            bg_color = '#ffffcc'
        
        # Widget'ları güncelle
        button_info['frame'].config(background=bg_color)
        button_info['day_label'].config(foreground=text_color, background=bg_color)
        button_info['info_label'].config(text=info_text, foreground=text_color, background=bg_color)
    
    def get_dosyalar_by_month(self) -> Dict:
        """Bu aydaki dosyaları al"""
        try:
            # Ayın ilk ve son günü
            first_day = self.current_date.replace(day=1)
            if self.current_date.month == 12:
                last_day = first_day.replace(year=first_day.year + 1, month=1) - timedelta(days=1)
            else:
                last_day = first_day.replace(month=first_day.month + 1) - timedelta(days=1)
            
            # Tüm dosyaları al
            all_dosyalar = self.db_manager.get_all_dosyalar(include_completed=True)
            
            # Tarihe göre grupla
            dosyalar_by_date = {}
            
            for dosya in all_dosyalar:
                # Son teslim tarihi
                try:
                    dilekce_date = datetime.strptime(dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d').date()
                    if first_day.date() <= dilekce_date <= last_day.date():
                        date_str = dilekce_date.strftime('%Y-%m-%d')
                        if date_str not in dosyalar_by_date:
                            dosyalar_by_date[date_str] = []
                        dosyalar_by_date[date_str].append({
                            'dosya': dosya,
                            'type': 'dilekce'
                        })
                except:
                    pass
                
                # Ana avukata sunum tarihi
                try:
                    sunum_date = datetime.strptime(dosya['ana_avukata_sunum_tarihi'], '%Y-%m-%d').date()
                    if first_day.date() <= sunum_date <= last_day.date():
                        date_str = sunum_date.strftime('%Y-%m-%d')
                        if date_str not in dosyalar_by_date:
                            dosyalar_by_date[date_str] = []
                        dosyalar_by_date[date_str].append({
                            'dosya': dosya,
                            'type': 'sunum'
                        })
                except:
                    pass
            
            return dosyalar_by_date
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya verileri alınırken hata oluştu: {str(e)}")
            return {}
    
    def on_day_click(self, day_coords):
        """Güne tıklandığında"""
        week, day = day_coords
        button_info = self.day_buttons[week][day]
        
        if button_info['date']:
            self.show_day_details(button_info['date'])
    
    def show_day_details(self, date_obj: date):
        """Günün detaylarını göster"""
        try:
            # Bu tarihteki dosyaları al
            date_str = date_obj.strftime('%Y-%m-%d')
            dosyalar = self.db_manager.get_dosyalar_by_date(date_str)
            
            # Detay metnini oluştur
            detail_text = f"Tarih: {date_obj.strftime('%d.%m.%Y (%A)')}\n"
            detail_text += "=" * 40 + "\n\n"
            
            if dosyalar:
                for dosya in dosyalar:
                    detail_text += f"📁 Dosya: {dosya['dosya_numarasi']}\n"
                    
                    # Bu dosya için hangi tarih türü
                    if dosya['dilekce_son_teslim_tarihi'] == date_str:
                        detail_text += "   🔴 Son Teslim Tarihi\n"
                    
                    if dosya['ana_avukata_sunum_tarihi'] == date_str:
                        detail_text += "   🔵 Ana Avukata Sunum Tarihi\n"
                    
                    # Durum
                    durum = "✅ Tamamlandı" if dosya['tamamlandi'] else "⏳ Aktif"
                    detail_text += f"   Durum: {durum}\n"
                    
                    # Notlar
                    if dosya.get('notlar'):
                        detail_text += f"   Not: {dosya['notlar'][:50]}{'...' if len(dosya['notlar']) > 50 else ''}\n"
                    
                    detail_text += "\n"
            else:
                detail_text += "Bu tarihte dosya bulunmamaktadır.\n"
            
            # Metin widget'ını güncelle
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete('1.0', tk.END)
            self.detail_text.insert('1.0', detail_text)
            self.detail_text.config(state=tk.DISABLED)
            
        except Exception as e:
            error_text = f"Detay gösterilirken hata oluştu: {str(e)}"
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete('1.0', tk.END)
            self.detail_text.insert('1.0', error_text)
            self.detail_text.config(state=tk.DISABLED)