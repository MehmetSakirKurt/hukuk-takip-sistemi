# GitHub'a Yükleme - Git Komutları

Bu dosya, Hukuk Bürosu Dilekçe Takip Sistemi'ni GitHub'a yüklemek için gereken tüm Git komutlarını içerir.

## 🚀 İlk Kez GitHub'a Yükleme

### 1. Git Repository Başlatma

```bash
# Proje klasörüne gidin
cd hukuk_takip_sistemi

# Git repository'sini başlatın
git init

# İlk commit için tüm dosyaları ekleyin
git add .

# İlk commit'i yapın
git commit -m "feat: İlk commit - Hukuk Bürosu Dilekçe Takip Sistemi

- Ana uygulama (main.py) eklendi
- SQLite veritabanı yönetimi (database.py)
- Tkinter GUI arayüzü (gui.py)
- Takvim görünümü modülü (calendar_view.py)
- Günlük bildirim sistemi (notifications.py)
- Kurulum scriptleri ve testler
- Detaylı README.md ve dokümantasyon"
```

### 2. GitHub'da Repository Oluşturma

1. GitHub'da oturum açın
2. "New repository" butonuna tıklayın
3. Repository adı: `hukuk-takip-sistemi`
4. Açıklama: `Hukuk büroları için dilekçe takip masaüstü uygulaması`
5. Public olarak ayarlayın
6. README, .gitignore, LICENSE seçmeyin (zaten var)
7. "Create repository" butonuna tıklayın

### 3. Local Repository'yi GitHub'a Bağlama

```bash
# GitHub repository'sini remote olarak ekleyin
# KULLANICI_ADINIZI kendi GitHub kullanıcı adınızla değiştirin
git remote add origin https://github.com/KULLANICI_ADINIZ/hukuk-takip-sistemi.git

# Ana branch'i main olarak ayarlayın (GitHub standardı)
git branch -M main

# İlk push'u yapın
git push -u origin main
```

## 🔄 Güncellemeler İçin Git Workflow

### Günlük Çalışma Döngüsü

```bash
# Yeni özellik branch'i oluşturun
git checkout -b feature/yeni-ozellik

# Değişikliklerinizi yapın...

# Değişiklikleri stage'e alın
git add .

# Commit yapın (Conventional Commits formatında)
git commit -m "feat: yeni özellik açıklaması"

# Branch'i GitHub'a push edin
git push origin feature/yeni-ozellik

# GitHub'da Pull Request açın
# Merge olduktan sonra:

# Main branch'e geçin
git checkout main

# Güncel değişiklikleri çekin
git pull origin main

# Kullanılmayan branch'i silin
git branch -d feature/yeni-ozellik
```

### Hızlı Güncelleme

```bash
# Değişiklikleri ekleyin
git add .

# Commit yapın
git commit -m "fix: hata düzeltmesi açıklaması"

# Push edin
git push origin main
```

## 📋 Faydalı Git Komutları

### Durum Kontrolü

```bash
# Git durumunu kontrol edin
git status

# Commit geçmişini görün
git log --oneline

# Değişiklikleri görmek için
git diff

# Branch'leri listeleyin
git branch -a
```

### Geri Alma İşlemleri

```bash
# Son commit'i geri alın (değişiklikleri korur)
git reset --soft HEAD~1

# Tüm değişiklikleri geri alın (DİKKAT!)
git reset --hard HEAD

# Belirli dosyayı önceki haline döndürün
git checkout HEAD -- dosya_adi.py
```

### Remote Repository İşlemleri

```bash
# Remote repository'leri listeleyin
git remote -v

# Remote repository URL'ini değiştirin
git remote set-url origin https://github.com/YENI_KULLANICI/hukuk-takip-sistemi.git

# Yeni remote ekleyin
git remote add upstream https://github.com/ORIGINAL_OWNER/hukuk-takip-sistemi.git
```

## 🏷️ Release Yayınlama

### Version Tag Oluşturma

```bash
# Tag oluşturun
git tag -a v1.0.0 -m "İlk stabil sürüm - v1.0.0

Özellikler:
- Dosya ekleme/düzenleme/silme
- Otomatik tarih hesaplama
- Takvim görünümü
- Günlük bildirimler
- İstatistikler"

# Tag'i GitHub'a push edin
git push origin v1.0.0

# Tüm tag'leri push edin
git push origin --tags
```

### GitHub Release Oluşturma

1. GitHub repository sayfasında "Releases" tıklayın
2. "Create a new release" butonuna tıklayın
3. Tag'i seçin (v1.0.0)
4. Release başlığı: "Hukuk Takip Sistemi v1.0.0"
5. Açıklama ekleyin
6. "Publish release" tıklayın

## 🤝 İşbirliği İçin Git Komutları

### Fork'tan Çalışma

```bash
# Original repository'yi upstream olarak ekleyin
git remote add upstream https://github.com/ORIGINAL_OWNER/hukuk-takip-sistemi.git

# Upstream'den güncellemeleri çekin
git fetch upstream

# Main branch'i güncelleyin
git checkout main
git merge upstream/main

# Güncellemeleri fork'unuza push edin
git push origin main
```

### Pull Request Workflow

```bash
# Yeni feature branch oluşturun
git checkout -b feature/yeni-ozellik

# Değişiklikleri yapın ve commit edin
git add .
git commit -m "feat: yeni özellik"

# Fork'unuza push edin
git push origin feature/yeni-ozellik

# GitHub'da Pull Request açın
```

## ❗ Önemli Notlar

### .gitignore Kontrolü

Şu dosyalar commit edilmemelidir:
- `*.db` (veritabanı dosyaları)
- `__pycache__/` (Python cache)
- `.vscode/`, `.idea/` (IDE ayarları)
- `*.log` (log dosyaları)

### Commit Mesaj Formatı

```
<tip>: <kısa açıklama>

<detaylı açıklama (isteğe bağlı)>
```

Tipler:
- `feat:` - Yeni özellik
- `fix:` - Hata düzeltmesi
- `docs:` - Dokümantasyon
- `style:` - Kod formatı
- `refactor:` - Kod reorganizasyonu
- `test:` - Test ekleme/güncelleme

### Branch Adlandırma

- `feature/ozellik-adi` - Yeni özellikler
- `bugfix/hata-adi` - Hata düzeltmeleri
- `docs/belge-adi` - Dokümantasyon
- `hotfix/acil-duzeltme` - Acil düzeltmeler

## 🎯 Örnek Tam Workflow

```bash
# 1. Projeyi klonlayın
git clone https://github.com/KULLANICI_ADINIZ/hukuk-takip-sistemi.git
cd hukuk-takip-sistemi

# 2. Yeni özellik için branch oluşturun
git checkout -b feature/dosya-arşivleme

# 3. Kodunuzu yazın...

# 4. Testleri çalıştırın
python test_core.py

# 5. Değişiklikleri commit edin
git add .
git commit -m "feat: dosya arşivleme özelliği eklendi

- Tamamlanan dosyaları arşiv klasörüne taşıma
- Arşiv dosyalarını geri yükleme
- Arşiv istatistikleri"

# 6. GitHub'a push edin
git push origin feature/dosya-arşivleme

# 7. Pull Request açın
# 8. Merge olduktan sonra branch'i temizleyin
git checkout main
git pull origin main
git branch -d feature/dosya-arşivleme
```

Bu komutları takip ederek projenizi başarıyla GitHub'da yönetebilirsiniz! 🚀