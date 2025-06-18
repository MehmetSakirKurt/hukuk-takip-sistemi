#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Ana GUI arayüzü
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import calendar
from typing import Dict, List, Optional

try:
    from tkcalendar import DateEntry
    TKCALENDAR_AVAILABLE = True
except ImportError:
    TKCALENDAR_AVAILABLE = False

from database import DatabaseManager
from calendar_view import CalendarView

class MainGUI:
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager, notification_manager):
        self.root = root
        self.db_manager = db_manager
        self.notification_manager = notification_manager
        
        # Stil ayarları
        self.setup_styles()
        
        # Ana pencere ayarları
        self.setup_main_window()
        
        # Ana widget'ları oluştur
        self.create_widgets()
        
        # Verileri yükle
        self.refresh_data()
        
    def setup_styles(self):
        """Stil ayarlarını yap"""
        style = ttk.Style()
        
        # Tema seç
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Özel stiller
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        
    def setup_main_window(self):
        """Ana pencere ayarlarını yap"""
        # Icon ayarla (varsa)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        # Pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Menü oluştur
        self.create_menu()
        
    def create_menu(self):
        """Ana menüyü oluştur"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Yeni Dosya Ekle", command=self.show_add_dialog, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Veritabanını Yedekle", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Düzenle menüsü
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Düzenle", menu=edit_menu)
        edit_menu.add_command(label="Seçili Dosyayı Düzenle", command=self.edit_selected_dosya, accelerator="F2")
        edit_menu.add_command(label="Seçili Dosyayı Sil", command=self.delete_selected_dosya, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Tümünü Yenile", command=self.refresh_data, accelerator="F5")
        
        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Görünüm", menu=view_menu)
        view_menu.add_command(label="Takvim Görünümü", command=self.show_calendar_view)
        view_menu.add_command(label="İstatistikler", command=self.show_statistics)
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Tamamlananları Göster", variable=tk.BooleanVar(value=True), 
                                command=self.toggle_completed_visibility)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        
        # Klavye kısayolları
        self.root.bind('<Control-n>', lambda e: self.show_add_dialog())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F2>', lambda e: self.edit_selected_dosya())
        self.root.bind('<Delete>', lambda e: self.delete_selected_dosya())
        self.root.bind('<F5>', lambda e: self.refresh_data())
        
    def create_widgets(self):
        """Ana widget'ları oluştur"""
        # Ana container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid yapılandırması
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="Hukuk Bürosu Dilekçe Takip Sistemi", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Sol panel - Kontroller
        self.create_control_panel(main_frame)
        
        # Orta panel - Dosya listesi
        self.create_file_list_panel(main_frame)
        
        # Alt panel - Durum çubuğu
        self.create_status_panel(main_frame)
        
    def create_control_panel(self, parent):
        """Kontrol panelini oluştur"""
        control_frame = ttk.LabelFrame(parent, text="Kontroller", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Yeni dosya ekleme butonu
        add_btn = ttk.Button(control_frame, text="Yeni Dosya Ekle", 
                            command=self.show_add_dialog, width=20)
        add_btn.grid(row=0, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Düzenleme butonları
        edit_btn = ttk.Button(control_frame, text="Düzenle", 
                             command=self.edit_selected_dosya, width=20)
        edit_btn.grid(row=1, column=0, pady=5, sticky=tk.W+tk.E)
        
        delete_btn = ttk.Button(control_frame, text="Sil", 
                               command=self.delete_selected_dosya, width=20)
        delete_btn.grid(row=2, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Ayırıcı
        ttk.Separator(control_frame, orient='horizontal').grid(row=3, column=0, 
                                                              sticky=tk.W+tk.E, pady=10)
        
        # Arama
        ttk.Label(control_frame, text="Arama:").grid(row=4, column=0, sticky=tk.W)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=20)
        search_entry.grid(row=5, column=0, pady=5, sticky=tk.W+tk.E)
        search_entry.bind('<KeyRelease>', self.on_search_change)
        
        search_btn = ttk.Button(control_frame, text="Ara", 
                               command=self.search_files, width=20)
        search_btn.grid(row=6, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Ayırıcı
        ttk.Separator(control_frame, orient='horizontal').grid(row=7, column=0, 
                                                              sticky=tk.W+tk.E, pady=10)
        
        # Görünüm seçenekleri
        self.show_completed_var = tk.BooleanVar(value=True)
        completed_check = ttk.Checkbutton(control_frame, text="Tamamlananları Göster",
                                         variable=self.show_completed_var,
                                         command=self.refresh_data)
        completed_check.grid(row=8, column=0, sticky=tk.W, pady=5)
        
        # Takvim görünümü butonu
        calendar_btn = ttk.Button(control_frame, text="Takvim Görünümü", 
                                 command=self.show_calendar_view, width=20)
        calendar_btn.grid(row=9, column=0, pady=5, sticky=tk.W+tk.E)
        
        # İstatistikler butonu
        stats_btn = ttk.Button(control_frame, text="İstatistikler", 
                              command=self.show_statistics, width=20)
        stats_btn.grid(row=10, column=0, pady=5, sticky=tk.W+tk.E)
        
    def create_file_list_panel(self, parent):
        """Dosya listesi panelini oluştur"""
        list_frame = ttk.LabelFrame(parent, text="Dosya Listesi", padding="10")
        list_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview oluştur
        columns = ('dosya_no', 'son_teslim', 'sunum_tarihi', 'kalan_gun', 'durum')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Sütun başlıkları ve genişlikleri
        self.tree.heading('dosya_no', text='Dosya No')
        self.tree.heading('son_teslim', text='Son Teslim Tarihi')
        self.tree.heading('sunum_tarihi', text='Ana Avukata Sunum')
        self.tree.heading('kalan_gun', text='Kalan Gün')
        self.tree.heading('durum', text='Durum')
        
        self.tree.column('dosya_no', width=120, minwidth=100)
        self.tree.column('son_teslim', width=120, minwidth=100)
        self.tree.column('sunum_tarihi', width=120, minwidth=100)
        self.tree.column('kalan_gun', width=80, minwidth=70)
        self.tree.column('durum', width=100, minwidth=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid yerleştirme
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Çift tıklama olayı
        self.tree.bind('<Double-1>', lambda e: self.edit_selected_dosya())
        
        # Sağ tık menüsü
        self.create_context_menu()
        
    def create_context_menu(self):
        """Sağ tık menüsünü oluştur"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Düzenle", command=self.edit_selected_dosya)
        self.context_menu.add_command(label="Tamamlandı Olarak İşaretle", command=self.mark_as_completed)
        self.context_menu.add_command(label="Sil", command=self.delete_selected_dosya)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Detayları Göster", command=self.show_details)
        
        # Sağ tık olayını bağla
        self.tree.bind('<Button-3>', self.show_context_menu)
        
    def create_status_panel(self, parent):
        """Durum panelini oluştur"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        status_frame.columnconfigure(1, weight=1)
        
        # Durum etiketi
        self.status_var = tk.StringVar(value="Hazır")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel')
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # İstatistik bilgileri
        self.stats_var = tk.StringVar()\n        stats_label = ttk.Label(status_frame, textvariable=self.stats_var, style='Status.TLabel')
        stats_label.grid(row=0, column=1, sticky=tk.E)
        
    def show_add_dialog(self):
        """Yeni dosya ekleme diyaloğunu göster"""
        dialog = DosyaDialog(self.root, self.db_manager, title="Yeni Dosya Ekle")
        if dialog.result:
            self.refresh_data()
            self.update_status("Yeni dosya eklendi.")
            
    def edit_selected_dosya(self):
        """Seçili dosyayı düzenle"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek istediğiniz dosyayı seçin.")
            return
        
        # Seçili öğenin ID'sini al
        item_id = self.tree.item(selected[0])['values'][0]
        
        # Veritabanından dosya bilgilerini al
        try:
            # Dosya numarasına göre arama yap
            dosyalar = self.db_manager.search_dosyalar(item_id)
            if dosyalar:
                dosya = dosyalar[0]
                dialog = DosyaDialog(self.root, self.db_manager, dosya=dosya, 
                                   title="Dosya Düzenle")
                if dialog.result:
                    self.refresh_data()
                    self.update_status("Dosya güncellendi.")
            else:
                messagebox.showerror("Hata", "Dosya bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya düzenleme hatası: {str(e)}")
            
    def delete_selected_dosya(self):
        """Seçili dosyayı sil"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz dosyayı seçin.")
            return
        
        # Onay al
        if not messagebox.askyesno("Onay", "Seçili dosyayı silmek istediğinizden emin misiniz?"):
            return
        
        # Seçili öğenin ID'sini al
        item_id = self.tree.item(selected[0])['values'][0]
        
        try:
            # Dosya numarasına göre dosyayı bul ve sil
            dosyalar = self.db_manager.search_dosyalar(item_id)
            if dosyalar:
                dosya = dosyalar[0]
                self.db_manager.delete_dosya(dosya['id'])
                self.refresh_data()
                self.update_status("Dosya silindi.")
            else:
                messagebox.showerror("Hata", "Dosya bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya silme hatası: {str(e)}")
            
    def mark_as_completed(self):
        """Seçili dosyayı tamamlandı olarak işaretle"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen işaretlemek istediğiniz dosyayı seçin.")
            return
        
        item_id = self.tree.item(selected[0])['values'][0]
        
        try:
            dosyalar = self.db_manager.search_dosyalar(item_id)
            if dosyalar:
                dosya = dosyalar[0]
                new_status = not dosya['tamamlandi']
                self.db_manager.update_dosya(dosya['id'], tamamlandi=new_status)
                self.refresh_data()
                status_text = "tamamlandı" if new_status else "aktif"
                self.update_status(f"Dosya {status_text} olarak işaretlendi.")
            else:
                messagebox.showerror("Hata", "Dosya bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Durum güncelleme hatası: {str(e)}")
            
    def show_details(self):
        """Seçili dosyanın detaylarını göster"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item_id = self.tree.item(selected[0])['values'][0]
        
        try:
            dosyalar = self.db_manager.search_dosyalar(item_id)
            if dosyalar:
                dosya = dosyalar[0]
                details_window = DosyaDetayWindow(self.root, dosya)
            else:
                messagebox.showerror("Hata", "Dosya bulunamadı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Detay gösterme hatası: {str(e)}")
    
    def show_context_menu(self, event):
        """Sağ tık menüsünü göster"""
        # Tıklanan öğeyi seç
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_search_change(self, event):
        """Arama metni değiştiğinde"""
        # Kısa bir gecikme ile otomatik arama
        self.root.after(500, self.search_files)
    
    def search_files(self):
        """Dosya arama"""
        search_term = self.search_var.get().strip()
        
        try:
            if search_term:
                dosyalar = self.db_manager.search_dosyalar(search_term)
                self.update_status(f"'{search_term}' için {len(dosyalar)} sonuç bulundu.")
            else:
                dosyalar = self.db_manager.get_all_dosyalar(
                    include_completed=self.show_completed_var.get()
                )
                self.update_status("Tüm dosyalar gösteriliyor.")
            
            self.populate_tree(dosyalar)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Arama hatası: {str(e)}")
    
    def show_calendar_view(self):
        """Takvim görünümünü göster"""
        try:
            calendar_window = CalendarWindow(self.root, self.db_manager)
        except Exception as e:
            messagebox.showerror("Hata", f"Takvim görünümü hatası: {str(e)}")
    
    def show_statistics(self):
        """İstatistikleri göster"""
        try:
            stats = self.db_manager.get_statistics()
            stats_window = StatisticsWindow(self.root, stats)
        except Exception as e:
            messagebox.showerror("Hata", f"İstatistik hatası: {str(e)}")
    
    def toggle_completed_visibility(self):
        """Tamamlanan dosyaların görünürlüğünü değiştir"""
        self.refresh_data()
    
    def backup_database(self):
        """Veritabanını yedekle"""
        try:
            import shutil
            from tkinter import filedialog
            
            backup_file = filedialog.asksaveasfilename(
                title="Veritabanı Yedeği Kaydet",
                defaultextension=".db",
                filetypes=[("SQLite Veritabanı", "*.db"), ("Tüm Dosyalar", "*.*")]
            )
            
            if backup_file:
                shutil.copy2("hukuk_takip.db", backup_file)
                messagebox.showinfo("Başarılı", f"Veritabanı yedeklendi:\n{backup_file}")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Yedekleme hatası: {str(e)}")
    
    def show_about(self):
        """Hakkında diyaloğunu göster"""
        about_text = """
Hukuk Bürosu Dilekçe Takip Sistemi
Versiyon: 1.0

Bu uygulama, hukuk bürolarında dilekçe son teslim 
tarihlerinin takibi için geliştirilmiştir.

Özellikler:
• Dosya ekleme, düzenleme, silme
• Otomatik tarih hesaplama
• Takvim görünümü
• Günlük bildirimler
• Arama ve filtreleme
• İstatistikler

© 2024 - Python ile geliştirilmiştir
"""
        messagebox.showinfo("Hakkında", about_text)
    
    def refresh_data(self):
        """Verileri yenile"""
        try:
            dosyalar = self.db_manager.get_all_dosyalar(
                include_completed=self.show_completed_var.get()
            )
            self.populate_tree(dosyalar)
            self.update_statistics()
            self.update_status("Veriler yenilendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Veri yenileme hatası: {str(e)}")
    
    def populate_tree(self, dosyalar: List[Dict]):
        """Ağaç görünümünü doldur"""
        # Mevcut öğeleri temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        today = datetime.now().date()
        
        for dosya in dosyalar:
            # Kalan gün hesapla
            try:
                son_teslim = datetime.strptime(dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d').date()
                kalan_gun = (son_teslim - today).days
                
                if kalan_gun < 0:
                    kalan_gun_text = f"GEÇTİ ({abs(kalan_gun)})"
                    tag = 'overdue'
                elif kalan_gun == 0:
                    kalan_gun_text = "BUGÜN"
                    tag = 'due_today'
                elif kalan_gun <= 3:
                    kalan_gun_text = str(kalan_gun)
                    tag = 'urgent'
                elif kalan_gun <= 7:
                    kalan_gun_text = str(kalan_gun)
                    tag = 'warning'
                else:
                    kalan_gun_text = str(kalan_gun)
                    tag = 'normal'
                    
            except:
                kalan_gun_text = "?"
                tag = 'normal'
            
            # Durum
            durum = "Tamamlandı" if dosya['tamamlandi'] else "Aktif"
            if dosya['tamamlandi']:
                tag = 'completed'
            
            # Tarihleri formatla
            try:
                son_teslim_str = datetime.strptime(dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d').strftime('%d.%m.%Y')
                sunum_tarihi_str = datetime.strptime(dosya['ana_avukata_sunum_tarihi'], '%Y-%m-%d').strftime('%d.%m.%Y')
            except:
                son_teslim_str = dosya['dilekce_son_teslim_tarihi']
                sunum_tarihi_str = dosya['ana_avukata_sunum_tarihi']
            
            # Öğeyi ekle
            self.tree.insert('', 'end', values=(
                dosya['dosya_numarasi'],
                son_teslim_str,
                sunum_tarihi_str,
                kalan_gun_text,
                durum
            ), tags=(tag,))
        
        # Renk kodları
        self.tree.tag_configure('overdue', background='#ffcccc', foreground='#cc0000')
        self.tree.tag_configure('due_today', background='#ffeecc', foreground='#cc6600')
        self.tree.tag_configure('urgent', background='#ffffcc', foreground='#cc9900')
        self.tree.tag_configure('warning', background='#ccffcc', foreground='#009900')
        self.tree.tag_configure('normal', background='white', foreground='black')
        self.tree.tag_configure('completed', background='#f0f0f0', foreground='#666666')
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        try:
            stats = self.db_manager.get_statistics()
            stats_text = f"Toplam: {stats['toplam_dosya']} | Aktif: {stats['aktif_dosya']} | Bu Hafta: {stats['bu_hafta_son_tarih']}"
            self.stats_var.set(stats_text)
        except:
            self.stats_var.set("İstatistik bilgisi alınamadı")
    
    def update_status(self, message: str):
        """Durum mesajını güncelle"""
        self.status_var.set(message)
        # 3 saniye sonra "Hazır" mesajına dön
        self.root.after(3000, lambda: self.status_var.set("Hazır"))
    
    def on_closing(self):
        """Uygulama kapatılırken"""
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinizden emin misiniz?"):
            self.root.destroy()


class DosyaDialog:
    def __init__(self, parent, db_manager: DatabaseManager, dosya: Dict = None, title: str = "Dosya"):
        self.parent = parent
        self.db_manager = db_manager
        self.dosya = dosya
        self.result = None
        
        # Dialog penceresi oluştur
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Pencereyi merkeze yerleştir
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        # Mevcut dosya bilgilerini yükle
        if self.dosya:
            self.load_dosya_data()
        
        # Enter ve Escape tuşları
        self.dialog.bind('<Return>', lambda e: self.save_dosya())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        # İlk alana odaklan
        self.dosya_no_entry.focus()
        
        # Dialog'u modal yap
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Dialog widget'larını oluştur"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dosya numarası
        ttk.Label(main_frame, text="Dosya Numarası:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.dosya_no_var = tk.StringVar()
        self.dosya_no_entry = ttk.Entry(main_frame, textvariable=self.dosya_no_var, width=30)
        self.dosya_no_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Son teslim tarihi
        ttk.Label(main_frame, text="Dilekçe Son Teslim Tarihi:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        if TKCALENDAR_AVAILABLE:
            self.tarih_entry = DateEntry(main_frame, width=12, background='darkblue',
                                       foreground='white', borderwidth=2,
                                       date_pattern='dd.mm.yyyy')
            self.tarih_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        else:
            # tkcalendar yoksa normal Entry kullan
            self.tarih_var = tk.StringVar()
            self.tarih_entry = ttk.Entry(main_frame, textvariable=self.tarih_var, width=30)
            self.tarih_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
            ttk.Label(main_frame, text="(GG.AA.YYYY formatında)", font=('Arial', 8)).grid(
                row=2, column=1, sticky=tk.W, padx=(10, 0)
            )
        
        # Ana avukata sunum tarihi (otomatik hesaplanacak)
        ttk.Label(main_frame, text="Ana Avukata Sunum Tarihi:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.sunum_tarihi_var = tk.StringVar()
        sunum_label = ttk.Label(main_frame, textvariable=self.sunum_tarihi_var, 
                               background='lightgray', relief='sunken', padding=5)
        sunum_label.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Tarih değiştiğinde sunum tarihini güncelle
        if TKCALENDAR_AVAILABLE:
            self.tarih_entry.bind('<<DateEntrySelected>>', self.update_sunum_tarihi)
        else:
            self.tarih_var.trace('w', self.update_sunum_tarihi)
        
        # Notlar
        ttk.Label(main_frame, text="Notlar:").grid(row=4, column=0, sticky=(tk.W, tk.N), pady=5)
        self.notlar_text = tk.Text(main_frame, height=4, width=30)
        self.notlar_text.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Tamamlandı checkbox (sadece düzenleme modunda)
        if self.dosya:
            self.tamamlandi_var = tk.BooleanVar()
            ttk.Checkbutton(main_frame, text="Tamamlandı", 
                          variable=self.tamamlandi_var).grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Kaydet", command=self.save_dosya).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="İptal", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Grid konfigürasyonu
        main_frame.columnconfigure(1, weight=1)
    
    def load_dosya_data(self):
        """Mevcut dosya verilerini yükle"""
        self.dosya_no_var.set(self.dosya['dosya_numarasi'])
        
        # Tarihi yükle
        try:
            tarih = datetime.strptime(self.dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d')
            if TKCALENDAR_AVAILABLE:
                self.tarih_entry.set_date(tarih.date())
            else:
                self.tarih_var.set(tarih.strftime('%d.%m.%Y'))
        except:
            pass
        
        # Notları yükle
        if self.dosya.get('notlar'):
            self.notlar_text.insert('1.0', self.dosya['notlar'])
        
        # Tamamlandı durumunu yükle
        if hasattr(self, 'tamamlandi_var'):
            self.tamamlandi_var.set(self.dosya['tamamlandi'])
        
        # Sunum tarihini güncelle
        self.update_sunum_tarihi()
    
    def update_sunum_tarihi(self, *args):
        """Ana avukata sunum tarihini güncelle"""
        try:
            if TKCALENDAR_AVAILABLE:
                tarih = self.tarih_entry.get_date()
            else:
                tarih_str = self.tarih_var.get()
                if not tarih_str:
                    self.sunum_tarihi_var.set("")
                    return
                tarih = datetime.strptime(tarih_str, '%d.%m.%Y').date()
            
            sunum_tarihi = tarih - timedelta(days=2)
            self.sunum_tarihi_var.set(sunum_tarihi.strftime('%d.%m.%Y'))
            
        except:
            self.sunum_tarihi_var.set("Geçersiz tarih")
    
    def save_dosya(self):
        """Dosyayı kaydet"""
        try:
            # Verileri al
            dosya_no = self.dosya_no_var.get().strip()
            if not dosya_no:
                messagebox.showerror("Hata", "Dosya numarası boş olamaz!")
                return
            
            # Tarihi al ve formatla
            if TKCALENDAR_AVAILABLE:
                tarih = self.tarih_entry.get_date()
                tarih_str = tarih.strftime('%Y-%m-%d')
            else:
                tarih_str_input = self.tarih_var.get()
                if not tarih_str_input:
                    messagebox.showerror("Hata", "Tarih boş olamaz!")
                    return
                tarih = datetime.strptime(tarih_str_input, '%d.%m.%Y')
                tarih_str = tarih.strftime('%Y-%m-%d')
            
            notlar = self.notlar_text.get('1.0', tk.END).strip()
            
            if self.dosya:
                # Güncelleme
                tamamlandi = self.tamamlandi_var.get() if hasattr(self, 'tamamlandi_var') else None
                self.db_manager.update_dosya(
                    self.dosya['id'], 
                    dosya_numarasi=dosya_no,
                    dilekce_son_teslim_tarihi=tarih_str,
                    notlar=notlar,
                    tamamlandi=tamamlandi
                )
            else:
                # Yeni ekleme
                self.db_manager.add_dosya(dosya_no, tarih_str, notlar)
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Hata", str(e))


class CalendarWindow:
    def __init__(self, parent, db_manager: DatabaseManager):
        self.parent = parent
        self.db_manager = db_manager
        
        # Pencere oluştur
        self.window = tk.Toplevel(parent)
        self.window.title("Takvim Görünümü")
        self.window.geometry("800x600")
        self.window.transient(parent)
        
        # Takvim görünümünü oluştur
        self.calendar_view = CalendarView(self.window, db_manager)
        
        # Pencereyi göster
        self.window.focus()


class StatisticsWindow:
    def __init__(self, parent, stats: Dict):
        self.window = tk.Toplevel(parent)
        self.window.title("İstatistikler")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        # İstatistikleri göster
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Dosya İstatistikleri", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        stats_text = f"""
Toplam Dosya Sayısı: {stats['toplam_dosya']}
Tamamlanan Dosyalar: {stats['tamamlanan_dosya']}
Aktif Dosyalar: {stats['aktif_dosya']}
Bu Hafta Son Tarihi Olanlar: {stats['bu_hafta_son_tarih']}

Tamamlanma Oranı: {(stats['tamamlanan_dosya'] / max(stats['toplam_dosya'], 1) * 100):.1f}%
"""
        
        ttk.Label(main_frame, text=stats_text, justify=tk.LEFT).pack()
        
        ttk.Button(main_frame, text="Kapat", 
                  command=self.window.destroy).pack(pady=20)


class DosyaDetayWindow:
    def __init__(self, parent, dosya: Dict):
        self.window = tk.Toplevel(parent)
        self.window.title(f"Dosya Detayları - {dosya['dosya_numarasi']}")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Detayları göster
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        ttk.Label(main_frame, text=f"Dosya: {dosya['dosya_numarasi']}", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Detay bilgileri
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tarihleri formatla
        try:
            dilekce_tarih = datetime.strptime(dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d').strftime('%d.%m.%Y')
            sunum_tarih = datetime.strptime(dosya['ana_avukata_sunum_tarihi'], '%Y-%m-%d').strftime('%d.%m.%Y')
            olusturma = datetime.strptime(dosya['olusturma_tarihi'], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
            guncelleme = datetime.strptime(dosya['guncelleme_tarihi'], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
        except:
            dilekce_tarih = dosya['dilekce_son_teslim_tarihi']
            sunum_tarih = dosya['ana_avukata_sunum_tarihi']
            olusturma = dosya['olusturma_tarihi']
            guncelleme = dosya['guncelleme_tarihi']
        
        # Kalan gün hesapla
        try:
            today = datetime.now().date()
            son_teslim = datetime.strptime(dosya['dilekce_son_teslim_tarihi'], '%Y-%m-%d').date()
            kalan_gun = (son_teslim - today).days
            kalan_gun_text = f"{kalan_gun} gün" if kalan_gun >= 0 else f"GEÇMİŞ ({abs(kalan_gun)} gün)"
        except:
            kalan_gun_text = "Bilinmiyor"
        
        info_text = f"""
Dosya Numarası: {dosya['dosya_numarasi']}

Dilekçe Son Teslim Tarihi: {dilekce_tarih}
Ana Avukata Sunum Tarihi: {sunum_tarih}
Kalan Süre: {kalan_gun_text}

Durum: {"Tamamlandı" if dosya['tamamlandi'] else "Aktif"}

Oluşturma Tarihi: {olusturma}
Son Güncelleme: {guncelleme}

Notlar:
{dosya.get('notlar', 'Not bulunmamaktadır.')}
"""
        
        text_widget = tk.Text(details_frame, wrap=tk.WORD, font=('Arial', 10))
        text_widget.insert('1.0', info_text)
        text_widget.config(state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Kapat butonu
        ttk.Button(main_frame, text="Kapat", 
                  command=self.window.destroy).pack(pady=20)