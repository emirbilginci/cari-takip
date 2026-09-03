# Cari Takip

Python ve PySide6 kullanılarak geliştirilmiş, küçük ve orta ölçekli işletmeler için tasarlanmış masaüstü cari hesap ve stok takip uygulaması.

Uygulama; cari hesapların, satış ve alış işlemlerinin, tahsilat ve ödemelerin, ürünlerin ve stok hareketlerinin tek bir arayüz üzerinden yönetilmesini sağlar.

## 🚀 Özellikler

- 📊 Dashboard üzerinden finansal özet görüntüleme
- 👥 Cari hesap ekleme, düzenleme ve görüntüleme
- 💰 Alacak ve borç takibi
- 🧾 Satış ve alış işlemleri
- 💵 Tahsilat ve ödeme işlemleri
- 📦 Ürün ve stok yönetimi
- 🔄 Stok hareketlerinin takibi
- 📈 Raporlama
- ⚙️ İşletme ayarları
- 💾 SQLite ile yerel veri saklama
- 🖥️ Windows üzerinde çalıştırılabilir uygulama
- 🔧 PyInstaller ile Windows `.exe` oluşturma
- 🤖 GitHub Actions ile otomatik Windows build süreci

## 🛠️ Kullanılan Teknolojiler

- **Python**
- **PySide6 / Qt** – Masaüstü kullanıcı arayüzü
- **SQLite** – Yerel veritabanı
- **PyInstaller** – Windows executable oluşturma
- **GitHub Actions** – Otomatik build

## 📁 Proje Yapısı

```text
cari-takip/
├── .github/
│   └── workflows/
│       └── windows-build.yml
├── app/
│   ├── database/
│   ├── ui/
│   └── ...
├── data/
├── requirements.txt
├── main.py
└── README.md
```

## 🎯 Projenin Amacı

Bu proje; cari hesap, satış, alış, tahsilat, ödeme ve stok takibi gibi temel işletme ihtiyaçlarını tek bir masaüstü uygulamasında yönetmek amacıyla geliştirilmiştir.

Aynı zamanda Python ile masaüstü uygulama geliştirme, SQLite veritabanı yönetimi ve Windows uygulama paketleme süreçlerini uygulamalı olarak geliştirmek amacıyla hazırlanmıştır.
