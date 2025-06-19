# Hukuk Bürosu Dilekçe Takip Sistemi

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

Hukuk bürolarında dilekçe son teslim tarihlerinin ve ana avukata sunum tarihlerinin takibi için geliştirilmiş masaüstü uygulaması.

## 📸 Ekran Görüntüleri

> Not: Ekran görüntüleri güncelleme sürecinde eklenecektir.

## 🚀 Hızlı Başlangıç

```bash
# Projeyi klonlayın
git clone https://github.com/KULLANICI_ADINIZ/hukuk-takip-sistemi.git
cd hukuk-takip-sistemi

# Kurulum scriptini çalıştırın
python install.py

# Uygulamayı başlatın
python main.py
```

## 🔋 Özellikler

### 🎯 Versiyon 2.0 "Jüpiter" - YENİ!
- 🎨 **Modern UI/UX**: ttkbootstrap ile 14 farklı tema
- 🏠 **Dinamik Dashboard**: 4 akıllı kart ile gerçek zamanlı durum
- ⌨️ **Komut Paleti (Ctrl+K)**: Hızlı erişim tüm işlevlere
- 🔍 **Gelişmiş Filtreler**: Akıllı filtreleme ve arama
- ⚡ **Performans**: Pagination ile büyük veri seti desteği
- 🧪 **%100 Test Kapsamı**: Tam otomatize edilmiş test sistemi

### 📊 Temel Özellikler
- ✅ **Dosya Yönetimi**: Dosya ekleme, düzenleme, silme
- 📅 **Otomatik Tarih Hesaplama**: Son teslim tarihinden 2 gün öncesi ana avukata sunum tarihi
- 🗓️ **Takvim Görünümü**: Tüm tarihleri görsel takvim üzerinde görme
- 🔔 **Günlük Bildirimler**: Her gün saat 09:00'da otomatik hatırlatmalar
- 🔍 **Arama ve Filtreleme**: Dosya numarası veya notlara göre arama
- 📊 **İstatistikler**: Dosya sayıları ve tamamlanma oranları
- 💾 **Kalıcı Veri Depolama**: SQLite veritabanı ile güvenli veri saklama
- ✔️ **Tamamlanma İzleme**: Dosyaları tamamlandı olarak işaretleme

## 🛠️ Sistem Gereksinimleri

- **İşletim Sistemi**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.7 veya üzeri
- **RAM**: En az 512 MB
- **Disk Alanı**: 50 MB boş alan

## 📦 Kurulum

### 1. Python Kurulumu

Python 3.7+ sisteminizde yüklü olmalıdır. Kontrol etmek için terminal/komut istemcisinde:

```bash
python --version
# veya
python3 --version
```

Python yüklü değilse [python.org](https://python.org) adresinden indirin.

### 2. Proje Dosyalarını İndirme

Proje dosyalarını bir klasöre çıkarın:

```
hukuk_takip_sistemi/
├── main.py
├── database.py
├── gui.py
├── calendar_view.py
├── notifications.py
├── requirements.txt
└── README.md
```

### 3. Gerekli Kütüphaneleri Yükleme

Terminal/komut istemcisinde proje klasörüne gidin ve aşağıdaki komutları çalıştırın:

```bash
# Proje klasörüne git
cd hukuk_takip_sistemi

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt

# Windows kullanıcıları için ek olarak:
pip install pywin32
```

**Not**: Eğer `pip` komutu çalışmıyorsa `pip3` kullanın.

### 4. İsteğe Bağlı Kütüphaneler

Bu kütüphaneler olmadan da uygulama çalışır, ancak daha iyi deneyim için önerilir:

- **tkcalendar**: Görsel tarih seçici için
- **plyer**: Sistem bildirimleri için

Kurulum:
```bash
pip install tkcalendar plyer
```

## 🚀 Uygulamayı Çalıştırma

### Basit Çalıştırma

Terminal/komut istemcisinde proje klasöründe:

```bash
python main.py
```

### Windows'ta Çalıştırma

1. **main.py** dosyasına çift tıklayın
2. Veya komut istemcisinde: `python main.py`

### Linux/macOS'ta Çalıştırma

```bash
python3 main.py
```

## 📋 Kullanım Kılavuzu

### İlk Çalıştırma

Uygulama ilk çalıştırıldığında otomatik olarak `hukuk_takip.db` adında bir veritabanı dosyası oluşturur.

### Yeni Dosya Ekleme

1. **"Yeni Dosya Ekle"** butonuna tıklayın
2. Dosya numarasını girin
3. Dilekçe son teslim tarihini seçin (takvim aracı ile)
4. Ana avukata sunum tarihi otomatik hesaplanır
5. İsteğe bağlı notlar ekleyin
6. **"Kaydet"** butonuna tıklayın

### Dosya Düzenleme

1. Listeden düzenlemek istediğiniz dosyayı seçin
2. **"Düzenle"** butonuna tıklayın veya F2 tuşuna basın
3. Gerekli değişiklikleri yapın
4. **"Kaydet"** butonuna tıklayın

### Dosya Silme

1. Listeden silmek istediğiniz dosyayı seçin
2. **"Sil"** butonuna tıklayın veya Delete tuşuna basın
3. Onay verin

### Arama Yapma

**Arama** kutusuna dosya numarası veya not içeriği yazın. Sonuçlar otomatik olarak filtrelenir.

### Takvim Görünümü

**"Takvim Görünümü"** butonuna tıklayarak tarihleri görsel olarak görüntüleyin:

- 🔴 Kırmızı: Son teslim tarihleri
- 🔵 Mavi: Ana avukata sunum tarihleri
- 🟡 Sarı: Bugünün tarihi

### Bildirimler

Uygulama her gün saat 09:00'da otomatik olarak:
- 7 gün içinde son tarihi olan dosyalar için bildirim gönderir
- Masaüstü bildirimi ve uygulama içi pencere gösterir

## ⚙️ Konfigürasyon

### Bildirim Saatini Değiştirme

`notifications.py` dosyasında `notification_time` değişkenini değiştirin:

```python
self.notification_time = "08:30"  # Saat 08:30 için
```

### Bildirim Süresini Değiştirme

`notifications.py` dosyasında `days_ahead` değişkenini değiştirin:

```python
self.days_ahead = 3  # 3 gün öncesinden bildirim için
```

## 🔧 Sorun Giderme

### "tkinter bulunamadı" hatası

**Linux** için:
```bash
sudo apt-get install python3-tk
```

**macOS** için:
```bash
brew install python-tk
```

### "tkcalendar bulunamadı" hatası

```bash
pip install tkcalendar
```

Bu kütüphane olmadan da uygulama çalışır, sadece tarih girişi manuel olur.

### Sistem bildirimleri çalışmıyor

```bash
pip install plyer
```

Windows için ayrıca:
```bash
pip install pywin32
```

### Veritabanı hatası

Eğer `hukuk_takip.db` dosyası bozulduysa:
1. Dosyayı silin
2. Uygulamayı yeniden başlatın
3. Yeni temiz veritabanı oluşturulur

## 💾 Yedekleme

### Otomatik Yedekleme

Menüden **Dosya > Veritabanını Yedekle** seçeneğini kullanın.

### Manuel Yedekleme

`hukuk_takip.db` dosyasını güvenli bir yere kopyalayın.

## 🎯 Klavye Kısayolları

### 🆕 Yeni Kısayollar (v2.0)
- **Ctrl+K**: Komut paleti aç
- **Ctrl+F**: Arama kutusuna odaklan

### 📋 Temel Kısayollar
- **Ctrl+N**: Yeni dosya ekle
- **F2**: Seçili dosyayı düzenle
- **Delete**: Seçili dosyayı sil
- **F5**: Verileri yenile
- **Ctrl+Q**: Uygulamadan çık

## 📄 Dosya Yapısı

```
hukuk_takip_sistemi/
├── main.py              # Ana uygulama dosyası
├── database.py          # Veritabanı yönetimi
├── gui.py              # Kullanıcı arayüzü
├── calendar_view.py    # Takvim görünümü
├── notifications.py    # Bildirim sistemi
├── requirements.txt    # Gerekli kütüphaneler
├── README.md          # Bu dosya
├── hukuk_takip.db     # Veritabanı (otomatik oluşur)
└── hukuk_takip_errors.log # Hata logları (otomatik oluşur)
```

## 🔒 Güvenlik

- Tüm veriler yerel olarak SQLite veritabanında saklanır
- İnternet bağlantısı gerektirmez
- Kişisel veriler dışarı gönderilmez

## 🐛 Bilinen Sorunlar

1. **Çok büyük dosya listeleri** performans sorununa neden olabilir
2. **Windows 7** tam desteklenmeyebilir
3. **Eski Python sürümleri** (3.6 altı) desteklenmez

## 🔄 Güncelleme

Yeni sürüm için tüm `.py` dosyalarını değiştirin. Veritabanı dosyası korunur.

## 📞 Destek

Sorun yaşıyorsanız:

1. **Hata loglarını** kontrol edin (`hukuk_takip_errors.log`)
2. **Python ve kütüphane sürümlerini** kontrol edin
3. **Terminal/komut istemcisinden** çalıştırarak hata mesajlarını görün

## 📝 Lisans

Bu yazılım eğitim amaçlı geliştirilmiştir. Ticari kullanım için uygun modifikasyonlar yapılabilir.

## 🎉 Teşekkürler

Bu uygulamayı kullandığınız için teşekkürler! Hukuki süreçlerinizin düzenli takibinde başarılar dileriz.

---

**Geliştirici Notu**: Bu uygulama Python ve tkinter kullanılarak geliştirilmiştir. Kod açık kaynak olup, ihtiyaçlarınıza göre değiştirilebilir.