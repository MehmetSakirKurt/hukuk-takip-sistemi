#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hukuk Bürosu Dilekçe Takip Sistemi
Veritabanı yönetimi modülü
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "hukuk_takip.db"):
        """Veritabanı yöneticisini başlat"""
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Veritabanına bağlan"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Dict benzeri erişim için
        except sqlite3.Error as e:
            raise Exception(f"Veritabanı bağlantı hatası: {e}")
    
    def create_tables(self):
        """Gerekli tabloları oluştur"""
        try:
            cursor = self.connection.cursor()
            
            # Ana dosyalar tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dosyalar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dosya_numarasi TEXT UNIQUE NOT NULL,
                    dilekce_son_teslim_tarihi DATE NOT NULL,
                    ana_avukata_sunum_tarihi DATE NOT NULL,
                    olusturma_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                    guncelleme_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tamamlandi BOOLEAN DEFAULT FALSE,
                    notlar TEXT DEFAULT ''
                )
            ''')
            
            # Trigger - güncelleme tarihini otomatik ayarla
            cursor.execute('''
                CREATE TRIGGER IF NOT EXISTS update_timestamp 
                AFTER UPDATE ON dosyalar
                BEGIN
                    UPDATE dosyalar SET guncelleme_tarihi = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END
            ''')
            
            self.connection.commit()
            
        except sqlite3.Error as e:
            raise Exception(f"Tablo oluşturma hatası: {e}")
    
    def add_dosya(self, dosya_numarasi: str, dilekce_son_teslim_tarihi: str, 
                  notlar: str = "") -> bool:
        """Yeni dosya ekle"""
        try:
            # Dosya numarası kontrolü
            if not dosya_numarasi or not dosya_numarasi.strip():
                raise ValueError("Dosya numarası boş olamaz")
            
            # Ana avukata sunum tarihini hesapla (2 takvim günü öncesi)
            dilekce_tarihi = datetime.strptime(dilekce_son_teslim_tarihi, "%Y-%m-%d")
            sunum_tarihi = dilekce_tarihi - timedelta(days=2)
            
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO dosyalar 
                (dosya_numarasi, dilekce_son_teslim_tarihi, ana_avukata_sunum_tarihi, notlar)
                VALUES (?, ?, ?, ?)
            ''', (dosya_numarasi, dilekce_son_teslim_tarihi, 
                  sunum_tarihi.strftime("%Y-%m-%d"), notlar))
            
            self.connection.commit()
            return True
            
        except sqlite3.IntegrityError:
            raise Exception(f"'{dosya_numarasi}' numaralı dosya zaten mevcut!")
        except sqlite3.Error as e:
            raise Exception(f"Dosya ekleme hatası: {e}")
        except ValueError as e:
            raise Exception(f"Tarih formatı hatası: {e}")
    
    def update_dosya(self, dosya_id: int, dosya_numarasi: str = None, 
                     dilekce_son_teslim_tarihi: str = None, 
                     notlar: str = None, tamamlandi: bool = None) -> bool:
        """Dosyayı güncelle"""
        try:
            cursor = self.connection.cursor()
            
            # Güncellenecek alanları hazırla
            updates = []
            params = []
            
            if dosya_numarasi is not None:
                updates.append("dosya_numarasi = ?")
                params.append(dosya_numarasi)
            
            if dilekce_son_teslim_tarihi is not None:
                updates.append("dilekce_son_teslim_tarihi = ?")
                params.append(dilekce_son_teslim_tarihi)
                
                # Ana avukata sunum tarihini yeniden hesapla
                dilekce_tarihi = datetime.strptime(dilekce_son_teslim_tarihi, "%Y-%m-%d")
                sunum_tarihi = dilekce_tarihi - timedelta(days=2)
                updates.append("ana_avukata_sunum_tarihi = ?")
                params.append(sunum_tarihi.strftime("%Y-%m-%d"))
            
            if notlar is not None:
                updates.append("notlar = ?")
                params.append(notlar)
            
            if tamamlandi is not None:
                updates.append("tamamlandi = ?")
                params.append(tamamlandi)
            
            if not updates:
                return False
            
            # Sorguyu çalıştır
            params.append(dosya_id)
            query = f"UPDATE dosyalar SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except sqlite3.IntegrityError:
            raise Exception(f"'{dosya_numarasi}' numaralı dosya zaten mevcut!")
        except sqlite3.Error as e:
            raise Exception(f"Dosya güncelleme hatası: {e}")
        except ValueError as e:
            raise Exception(f"Tarih formatı hatası: {e}")
    
    def delete_dosya(self, dosya_id: int) -> bool:
        """Dosyayı sil"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM dosyalar WHERE id = ?", (dosya_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Dosya silme hatası: {e}")
    
    def get_all_dosyalar(self, include_completed: bool = True, limit: int = None, offset: int = 0) -> List[Dict]:
        """Tüm dosyaları getir (pagination desteği ile)"""
        try:
            cursor = self.connection.cursor()
            
            base_query = '''
                SELECT * FROM dosyalar 
                {} 
                ORDER BY dilekce_son_teslim_tarihi ASC, olusturma_tarihi DESC
            '''
            
            if include_completed:
                where_clause = ""
                params = []
            else:
                where_clause = "WHERE tamamlandi = FALSE"
                params = []
            
            # Pagination parametreleri
            pagination_clause = ""
            if limit is not None:
                pagination_clause = f" LIMIT {limit}"
                if offset > 0:
                    pagination_clause += f" OFFSET {offset}"
            
            query = base_query.format(where_clause) + pagination_clause
            cursor.execute(query, params)
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Dosyalar getirme hatası: {e}")
    
    def get_dosya_count(self, include_completed: bool = True) -> int:
        """Toplam dosya sayısını getir"""
        try:
            cursor = self.connection.cursor()
            
            if include_completed:
                cursor.execute("SELECT COUNT(*) as count FROM dosyalar")
            else:
                cursor.execute("SELECT COUNT(*) as count FROM dosyalar WHERE tamamlandi = FALSE")
            
            return cursor.fetchone()['count']
            
        except sqlite3.Error as e:
            raise Exception(f"Dosya sayısı getirme hatası: {e}")
    
    def get_dosya_by_id(self, dosya_id: int) -> Optional[Dict]:
        """ID'ye göre dosya getir"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM dosyalar WHERE id = ?", (dosya_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Dosya getirme hatası: {e}")
    
    def search_dosyalar(self, search_term: str) -> List[Dict]:
        """Dosya numarasına göre arama yap"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM dosyalar 
                WHERE dosya_numarasi LIKE ? OR notlar LIKE ?
                ORDER BY dilekce_son_teslim_tarihi ASC
            ''', (f"%{search_term}%", f"%{search_term}%"))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Arama hatası: {e}")
    
    def get_upcoming_deadlines(self, days_ahead: int = 7) -> List[Dict]:
        """Yaklaşan son tarihleri getir"""
        try:
            cursor = self.connection.cursor()
            today = datetime.now().date()
            end_date = today + timedelta(days=days_ahead)
            
            cursor.execute('''
                SELECT * FROM dosyalar 
                WHERE ((dilekce_son_teslim_tarihi BETWEEN ? AND ?)
                   OR (ana_avukata_sunum_tarihi BETWEEN ? AND ?))
                   AND tamamlandi = FALSE
                ORDER BY dilekce_son_teslim_tarihi ASC
            ''', (today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
                  today.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Yaklaşan tarihler getirme hatası: {e}")
    
    def get_dosyalar_by_date(self, target_date: str) -> List[Dict]:
        """Belirli tarihteki dosyaları getir"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM dosyalar 
                WHERE dilekce_son_teslim_tarihi = ? 
                   OR ana_avukata_sunum_tarihi = ?
                ORDER BY dilekce_son_teslim_tarihi ASC
            ''', (target_date, target_date))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except sqlite3.Error as e:
            raise Exception(f"Tarihe göre dosya getirme hatası: {e}")
    
    def get_statistics(self) -> Dict:
        """İstatistikleri getir"""
        try:
            cursor = self.connection.cursor()
            
            # Toplam dosya sayısı
            cursor.execute("SELECT COUNT(*) as toplam FROM dosyalar")
            toplam = cursor.fetchone()['toplam']
            
            # Tamamlanan dosya sayısı
            cursor.execute("SELECT COUNT(*) as tamamlanan FROM dosyalar WHERE tamamlandi = TRUE")
            tamamlanan = cursor.fetchone()['tamamlanan']
            
            # Aktif dosya sayısı
            aktif = toplam - tamamlanan
            
            # Bu hafta son tarihi olan dosyalar
            today = datetime.now().date()
            week_end = today + timedelta(days=7)
            cursor.execute('''
                SELECT COUNT(*) as bu_hafta FROM dosyalar 
                WHERE dilekce_son_teslim_tarihi BETWEEN ? AND ?
                AND tamamlandi = FALSE
            ''', (today.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")))
            bu_hafta = cursor.fetchone()['bu_hafta']
            
            return {
                'toplam_dosya': toplam,
                'tamamlanan_dosya': tamamlanan,
                'aktif_dosya': aktif,
                'bu_hafta_son_tarih': bu_hafta
            }
            
        except sqlite3.Error as e:
            raise Exception(f"İstatistik hatası: {e}")
    
    def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Destructor - bağlantıyı kapat"""
        self.close()