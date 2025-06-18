# Katkı Sağlama Rehberi

Hukuk Bürosu Dilekçe Takip Sistemi'ne katkı sağlamak istediğiniz için teşekkürler! 🎉

## 🚀 Nasıl Katkı Sağlarım?

### 1. Issue Açma

Hata raporu veya özellik önerisi için:
1. [Issues](https://github.com/KULLANICI_ADINIZ/hukuk-takip-sistemi/issues) sayfasına gidin
2. "New Issue" butonuna tıklayın
3. Uygun template'i seçin
4. Detaylı açıklama yapın

### 2. Pull Request Gönderme

1. Projeyi fork edin
2. Yeni bir branch oluşturun:
   ```bash
   git checkout -b feature/yeni-ozellik
   ```
3. Değişikliklerinizi yapın
4. Testleri çalıştırın:
   ```bash
   python test_core.py
   ```
5. Commit yapın:
   ```bash
   git commit -m "feat: yeni özellik açıklaması"
   ```
6. Push edin:
   ```bash
   git push origin feature/yeni-ozellik
   ```
7. Pull Request açın

## 📋 Geliştirme Standartları

### Kod Kalitesi
- Python PEP 8 standartlarına uyun
- Türkçe yorum ve docstring kullanın
- Değişken isimleri Türkçe olsun
- Fonksiyonlar küçük ve tek amaçlı olsun

### Commit Mesajları
Conventional Commits formatını kullanın:
- `feat:` - Yeni özellik
- `fix:` - Hata düzeltmesi
- `docs:` - Dokümantasyon
- `style:` - Kod formatı
- `refactor:` - Kod yeniden düzenleme
- `test:` - Test ekleme/güncelleme

### Test Etme
- Yeni özellikler için test yazın
- Mevcut testlerin geçtiğinden emin olun
- `test_core.py` ile temel testleri çalıştırın

## 🐛 Hata Raporu

Hata raporu açarken şunları ekleyin:
- İşletim sistemi ve Python versiyonu
- Hatayı yeniden oluşturma adımları
- Beklenen ve gerçek davranış
- Hata logları (varsa)

## 💡 Özellik Önerisi

Yeni özellik önerirken:
- Özelliğin amacını açıklayın
- Kullanım senaryosunu belirtin
- Alternatif çözümleri düşünün
- Mockup/wireframe ekleyin (isteğe bağlı)

## 📝 Dokümantasyon

- README.md'yi güncel tutun
- Kod içi yorumları Türkçe yazın
- Yeni özellikler için kullanım örnekleri ekleyin

## 🔧 Geliştirme Ortamı

### Gereksinimler
- Python 3.7+
- tkinter (GUI için)
- sqlite3 (veritabanı için)

### Kurulum
```bash
git clone https://github.com/KULLANICI_ADINIZ/hukuk-takip-sistemi.git
cd hukuk-takip-sistemi
python install.py
```

### Test Etme
```bash
python test_core.py  # Temel testler
python test_app.py   # Tam testler (tkinter gerekli)
```

## 🏷️ Etiketler

Issue'lar için kullanılan etiketler:
- `bug` - Hata raporu
- `enhancement` - Yeni özellik
- `documentation` - Dokümantasyon
- `good first issue` - Yeni başlayanlar için
- `help wanted` - Yardım aranan konular
- `priority: high` - Yüksek öncelik
- `priority: low` - Düşük öncelik

## 💬 İletişim

- GitHub Issues üzerinden
- Pull Request yorumları ile
- README.md'deki iletişim bilgileri

## 🙏 Teşekkürler

Her türlü katkı değerlidir:
- Hata raporları
- Özellik önerileri
- Kod katkıları
- Dokümantasyon iyileştirmeleri
- Test yazma
- Çeviri desteği

Hukuk camiasına faydalı bir araç geliştirmek için birlikte çalışalım! ⚖️