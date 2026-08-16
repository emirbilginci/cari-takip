from pathlib import Path
import json
import shutil
import sqlite3

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QFileDialog,
    QFrame,
)
from PySide6.QtCore import Qt


class AyarlarWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Ayarlar")
        self.resize(700, 600)

        self.project_root = Path(__file__).resolve().parents[2]
        self.settings_path = (
            self.project_root
            / "data"
            / "settings.json"
        )

        self.setup_ui()
        self.load_settings()

    # =========================================================
    # ARAYÜZ
    # =========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            30,
            25,
            30,
            30
        )

        layout.setSpacing(18)

        # =====================================================
        # BAŞLIK
        # =====================================================

        title = QLabel("Ayarlar")

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        subtitle = QLabel(
            "İşletme bilgilerini ve uygulama ayarlarını yönetin."
        )

        subtitle.setStyleSheet("""
            color: #888888;
            font-size: 13px;
        """)

        layout.addWidget(subtitle)

        # =====================================================
        # İŞLETME BİLGİLERİ
        # =====================================================

        business_group = QGroupBox(
            "İşletme Bilgileri"
        )

        business_layout = QFormLayout(
            business_group
        )

        business_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        business_layout.setSpacing(12)

        self.business_name = QLineEdit()
        self.business_name.setPlaceholderText(
            "İşletme adını girin"
        )

        self.phone = QLineEdit()
        self.phone.setPlaceholderText(
            "Telefon numarası"
        )

        self.address = QLineEdit()
        self.address.setPlaceholderText(
            "İşletme adresi"
        )

        self.currency = QComboBox()

        self.currency.addItems([
            "TL",
            "USD",
            "EUR",
            "GBP",
        ])

        business_layout.addRow(
            "İşletme Adı:",
            self.business_name
        )

        business_layout.addRow(
            "Telefon:",
            self.phone
        )

        business_layout.addRow(
            "Adres:",
            self.address
        )

        business_layout.addRow(
            "Para Birimi:",
            self.currency
        )

        layout.addWidget(
            business_group
        )

        # =====================================================
        # YEDEKLEME
        # =====================================================

        backup_group = QGroupBox(
            "Veritabanı"
        )

        backup_layout = QVBoxLayout(
            backup_group
        )

        backup_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        backup_info = QLabel(
            "Veritabanınızın yedeğini alarak "
            "müşteri, ürün ve işlem kayıtlarınızı koruyabilirsiniz."
        )

        backup_info.setWordWrap(True)

        backup_info.setStyleSheet("""
            color: #aaaaaa;
        """)

        backup_layout.addWidget(
            backup_info
        )

        backup_button = QPushButton(
            "💾 Veritabanı Yedeği Al"
        )

        backup_button.setMinimumHeight(
            42
        )

        backup_button.clicked.connect(
            self.create_backup
        )

        backup_layout.addWidget(
            backup_button
        )

        layout.addWidget(
            backup_group
        )

        # =====================================================
        # UYGULAMA BİLGİSİ
        # =====================================================

        info_frame = QFrame()

        info_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 8px;
            }
        """)

        info_layout = QVBoxLayout(
            info_frame
        )

        info_layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        info_title = QLabel(
            "Cari Takip"
        )

        info_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)

        info_layout.addWidget(
            info_title
        )

        info_text = QLabel(
            "Cari hesap, ürün, stok, tahsilat, ödeme "
            "ve raporlama yönetim uygulaması."
        )

        info_text.setStyleSheet("""
            color: #aaaaaa;
        """)

        info_layout.addWidget(
            info_text
        )

        version = QLabel(
            "Sürüm: 1.0"
        )

        version.setStyleSheet("""
            color: #888888;
            font-size: 12px;
        """)

        info_layout.addWidget(
            version
        )

        layout.addWidget(
            info_frame
        )

        layout.addStretch()

        # =====================================================
        # BUTONLAR
        # =====================================================

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        cancel_button = QPushButton(
            "Kapat"
        )

        cancel_button.setMinimumHeight(
            40
        )

        cancel_button.clicked.connect(
            self.close
        )

        button_layout.addWidget(
            cancel_button
        )

        save_button = QPushButton(
            "Ayarları Kaydet"
        )

        save_button.setMinimumHeight(
            40
        )

        save_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding-left: 20px;
                padding-right: 20px;
            }
        """)

        save_button.clicked.connect(
            self.save_settings
        )

        button_layout.addWidget(
            save_button
        )

        layout.addLayout(
            button_layout
        )

    # =========================================================
    # AYARLARI YÜKLE
    # =========================================================

    def load_settings(self):

        if not self.settings_path.exists():

            self.business_name.setText(
                "Cari Takip"
            )

            self.currency.setCurrentText(
                "TL"
            )

            return

        try:

            with open(
                self.settings_path,
                "r",
                encoding="utf-8"
            ) as file:

                settings = json.load(file)

            self.business_name.setText(
                settings.get(
                    "business_name",
                    "Cari Takip"
                )
            )

            self.phone.setText(
                settings.get(
                    "phone",
                    ""
                )
            )

            self.address.setText(
                settings.get(
                    "address",
                    ""
                )
            )

            currency = settings.get(
                "currency",
                "TL"
            )

            index = self.currency.findText(
                currency
            )

            if index >= 0:

                self.currency.setCurrentIndex(
                    index
                )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Uyarı",
                f"Ayarlar okunamadı.\n\n{e}"
            )

    # =========================================================
    # AYARLARI KAYDET
    # =========================================================

    def save_settings(self):

        try:

            self.settings_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            settings = {
                "business_name":
                    self.business_name.text().strip(),

                "phone":
                    self.phone.text().strip(),

                "address":
                    self.address.text().strip(),

                "currency":
                    self.currency.currentText(),
            }

            with open(
                self.settings_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    settings,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

            QMessageBox.information(
                self,
                "Başarılı",
                "Ayarlar başarıyla kaydedildi."
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Ayarlar kaydedilemedi.\n\n{e}"
            )

    # =========================================================
    # VERİTABANI YEDEĞİ
    # =========================================================

    def get_database_path(self):

        try:

            from app.database.connection import (
                get_connection
            )

            conn = get_connection()

            row = conn.execute(
                "PRAGMA database_list"
            ).fetchone()

            conn.close()

            if row is None:
                return None

            # SQLite database_list:
            # seq, name, file
            database_path = row[2]

            if not database_path:
                return None

            return Path(database_path)

        except Exception:

            return None

    def create_backup(self):

        database_path = (
            self.get_database_path()
        )

        if (
            database_path is None
            or not database_path.exists()
        ):

            QMessageBox.warning(
                self,
                "Yedekleme",
                "Veritabanı dosyası bulunamadı."
            )

            return

        default_name = (
            "cari_takip_yedek.db"
        )

        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Veritabanı Yedeğini Kaydet",
            str(
                Path.home()
                / "Desktop"
                / default_name
            ),
            "SQLite Database (*.db);;Tüm Dosyalar (*)"
        )

        if not save_path:
            return

        try:

            shutil.copy2(
                database_path,
                save_path
            )

            QMessageBox.information(
                self,
                "Yedekleme Başarılı",
                "Veritabanı yedeği başarıyla oluşturuldu.\n\n"
                f"Konum:\n{save_path}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Yedekleme Hatası",
                f"Veritabanı yedeklenemedi.\n\n{e}"
            )
