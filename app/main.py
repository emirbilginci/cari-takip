import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QDialog,
    QFrame,
    QSizePolicy,
)

from PySide6.QtCore import Qt, QTimer

from app.database.connection import get_connection
from app.ui.cariler import CarilerPage
from app.ui.urunler import UrunlerDialog
from app.ui.yeni_islem import YeniIslemDialog


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cari Takip")

        self.resize(1350, 850)
        self.setMinimumSize(1100, 700)

        self.setup_ui()

        # Dashboard otomatik yenileme
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_dashboard)
        self.timer.start(10000)

        self.refresh_dashboard()

    # ======================================================
    # ANA ARAYÜZ
    # ======================================================

    def setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        main_layout.setSpacing(35)

        # ==================================================
        # SOL MENÜ
        # ==================================================

        sidebar = QWidget()
        sidebar.setFixedWidth(300)

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        sidebar_layout.setSpacing(10)

        # Logo
        logo = QLabel("CARİ TAKİP")

        logo.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                padding: 10px 15px 25px 15px;
            }
        """)

        sidebar_layout.addWidget(logo)

        # ==================================================
        # MENÜLER
        # ==================================================

        self.home_button = self.create_menu_button(
            "🏠  Ana Sayfa"
        )

        self.customers_button = self.create_menu_button(
            "👥  Cariler"
        )

        self.transaction_button = self.create_menu_button(
            "➕  Yeni İşlem"
        )

        self.collection_button = self.create_menu_button(
            "💰  Tahsilat"
        )

        self.payment_button = self.create_menu_button(
            "💸  Ödeme"
        )

        self.products_button = self.create_menu_button(
            "📦  Ürünler"
        )

        self.stock_button = self.create_menu_button(
            "📋  Stok Hareketleri"
        )

        self.reports_button = self.create_menu_button(
            "📊  Raporlar"
        )

        sidebar_layout.addWidget(self.home_button)
        sidebar_layout.addWidget(self.customers_button)
        sidebar_layout.addWidget(self.transaction_button)
        sidebar_layout.addWidget(self.collection_button)
        sidebar_layout.addWidget(self.payment_button)
        sidebar_layout.addWidget(self.products_button)
        sidebar_layout.addWidget(self.stock_button)
        sidebar_layout.addWidget(self.reports_button)

        sidebar_layout.addStretch()

        # ==================================================
        # AYARLAR
        # ==================================================

        self.settings_button = self.create_menu_button(
            "⚙️  Ayarlar"
        )

        sidebar_layout.addWidget(
            self.settings_button
        )

        # ==================================================
        # SAĞ TARAF
        # ==================================================

        content = QWidget()

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        content_layout.setSpacing(20)

        # ==================================================
        # BAŞLIK
        # ==================================================

        title = QLabel(
            "Cari Takip Panosu"
        )

        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                padding: 5px 0px 15px 0px;
            }
        """)

        content_layout.addWidget(title)

        # ==================================================
        # DASHBOARD KARTLARI
        # ==================================================

        cards_layout = QGridLayout()
        cards_layout.setSpacing(20)

        self.total_customers_card = self.create_card(
            "Toplam Cari"
        )

        self.total_products_card = self.create_card(
            "Toplam Ürün"
        )

        self.total_receivable_card = self.create_card(
            "Toplam Alacak"
        )

        self.total_debt_card = self.create_card(
            "Toplam Borç"
        )

        self.cash_card = self.create_card(
            "Kasa"
        )

        self.net_balance_card = self.create_card(
            "Net Bakiye"
        )

        cards_layout.addWidget(
            self.total_customers_card,
            0,
            0
        )

        cards_layout.addWidget(
            self.total_products_card,
            0,
            1
        )

        cards_layout.addWidget(
            self.total_receivable_card,
            0,
            2
        )

        cards_layout.addWidget(
            self.total_debt_card,
            1,
            0
        )

        cards_layout.addWidget(
            self.cash_card,
            1,
            1
        )

        cards_layout.addWidget(
            self.net_balance_card,
            1,
            2
        )

        content_layout.addLayout(
            cards_layout
        )

        content_layout.addStretch()

        # ==================================================
        # ALT BİLGİ
        # ==================================================

        footer = QLabel(
            "Pano her 10 saniyede bir otomatik yenilenir."
        )

        footer.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 13px;
                padding: 5px;
            }
        """)

        content_layout.addWidget(footer)

        # ==================================================
        # ANA LAYOUT
        # ==================================================

        main_layout.addWidget(sidebar)

        main_layout.addWidget(
            content,
            1
        )

        # ==================================================
        # BUTON BAĞLANTILARI
        # ==================================================

        self.home_button.clicked.connect(
            self.go_home
        )

        self.customers_button.clicked.connect(
            self.open_customers
        )

        self.transaction_button.clicked.connect(
            self.open_transaction
        )

        self.collection_button.clicked.connect(
            self.open_collection
        )

        self.payment_button.clicked.connect(
            self.open_payment
        )

        self.products_button.clicked.connect(
            self.open_products
        )

        self.stock_button.clicked.connect(
            self.open_stock_movements
        )

        self.reports_button.clicked.connect(
            self.open_reports
        )

        self.settings_button.clicked.connect(
            self.open_settings
        )

    # ======================================================
    # MENÜ BUTONU
    # ======================================================

    def create_menu_button(self, text):

        button = QPushButton(text)

        button.setMinimumHeight(46)

        button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        button.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                color: white;
                border: none;
                border-radius: 2px;
                padding: 10px 15px;
                text-align: left;
                font-size: 15px;
            }

            QPushButton:hover {
                background-color: #606060;
            }

            QPushButton:pressed {
                background-color: #707070;
            }
        """)

        return button

    # ======================================================
    # DASHBOARD KARTI
    # ======================================================

    def create_card(self, title):

        card = QFrame()

        card.setMinimumHeight(225)

        card.setStyleSheet("""
            QFrame {
                background-color: #f4f4f4;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            25,
            22,
            25,
            25
        )

        title_label = QLabel(title)

        title_label.setStyleSheet("""
            QLabel {
                color: #707070;
                font-size: 16px;
                font-weight: normal;
            }
        """)

        value_label = QLabel("0.00 TL")

        value_label.setStyleSheet("""
            QLabel {
                color: #202020;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        value_label.setAlignment(
            Qt.AlignLeft | Qt.AlignBottom
        )

        layout.addWidget(title_label)

        layout.addStretch()

        layout.addWidget(value_label)

        card.value_label = value_label

        return card

    # ======================================================
    # ANA SAYFA
    # ======================================================

    def go_home(self):

        self.refresh_dashboard()

    # ======================================================
    # CARİLER
    # ======================================================

    def open_customers(self):

        try:

            dialog = QDialog(self)

            dialog.setWindowTitle("Cariler")
            dialog.resize(1150, 700)

            layout = QVBoxLayout(dialog)

            page = CarilerPage()

            layout.addWidget(page)

            dialog.exec()

            self.refresh_dashboard()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Cariler ekranı açılamadı.\n\n{e}"
            )

    # ======================================================
    # YENİ İŞLEM
    # ======================================================

    def open_transaction(self):

        try:

            dialog = YeniIslemDialog(self)

            result = dialog.exec()

            if result == QDialog.Accepted:

                self.refresh_dashboard()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Yeni işlem ekranı açılamadı.\n\n{e}"
            )

    # ======================================================
    # TAHSİLAT
    # ======================================================

    def open_collection(self):

        try:

            from app.ui.tahsilat import TahsilatDialog

            dialog = TahsilatDialog(self)

            dialog.exec()

            self.refresh_dashboard()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Tahsilat ekranı açılamadı.\n\n{e}"
            )

    # ======================================================
    # ÖDEME
    # ======================================================

    def open_payment(self):

        try:

            from app.ui.odeme import OdemeDialog

            dialog = OdemeDialog(self)

            dialog.exec()

            self.refresh_dashboard()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Ödeme ekranı açılamadı.\n\n{e}"
            )

    # ======================================================
    # ÜRÜNLER
    # ======================================================

    def open_products(self):

        try:

            dialog = UrunlerDialog(self)

            dialog.exec()

            self.refresh_dashboard()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Ürünler ekranı açılamadı.\n\n{e}"
            )

    # ======================================================
    # STOK HAREKETLERİ
    # ======================================================

    def open_stock_movements(self):

        try:

            from app.ui.stok_hareketleri import (
                StokHareketleriDialog
            )

            dialog = StokHareketleriDialog(self)

            dialog.exec()

            self.refresh_dashboard()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Stok hareketleri ekranı açılamadı.\n\n{e}"
            )

    # ======================================================
    # RAPORLAR
    # ======================================================

    def open_reports(self):

        try:

            from app.ui.raporlar import RaporlarWidget

            self.reports_widget = RaporlarWidget()

            self.reports_widget.setWindowTitle(
                "Raporlar"
            )

            self.reports_widget.resize(
                900,
                600
            )

            self.reports_widget.show()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Raporlar ekranı açılamadı.\n\n{e}"
            )


    # ======================================================
    # AYARLAR
    # ======================================================

    def open_settings(self):

        try:

            from app.ui.ayarlar import (
                AyarlarWidget
            )

            self.settings_widget = (
                AyarlarWidget()
            )

            self.settings_widget.setWindowFlag(
                Qt.Window
            )

            self.settings_widget.setWindowTitle(
                "Ayarlar"
            )

            self.settings_widget.show()

            self.settings_widget.raise_()
            self.settings_widget.activateWindow()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Ayarlar ekranı açılamadı.\\n\\n{e}"
            )


    # ======================================================
    # DASHBOARD YENİLE
    # ======================================================

    def refresh_dashboard(self):

        conn = None

        try:

            conn = get_connection()

            row = conn.execute("""
                SELECT COUNT(*) AS total
                FROM customers
                WHERE is_active = 1
            """).fetchone()

            total_customers = int(
                row["total"] or 0
            ) if row else 0

            row = conn.execute("""
                SELECT COUNT(*) AS total
                FROM products
                WHERE is_active = 1
            """).fetchone()

            total_products = int(
                row["total"] or 0
            ) if row else 0

            # ==================================================
            # TOPLAM ALACAK
            # ==================================================

            row = conn.execute("""
                SELECT
                    COALESCE(SUM(
                        CASE
                            WHEN transaction_type = 'sale_on_credit'
                                THEN amount
                            WHEN transaction_type = 'sale'
                                 AND payment_method = 'credit'
                                THEN amount
                            ELSE 0
                        END
                    ), 0) AS sales,

                    COALESCE(SUM(
                        CASE
                            WHEN transaction_type = 'payment_received'
                                THEN amount
                            ELSE 0
                        END
                    ), 0) AS collections

                FROM transactions

                WHERE is_cancelled = 0
            """).fetchone()

            credit_sales = float(
                row["sales"] or 0
            )

            collections = float(
                row["collections"] or 0
            )

            total_receivable = (
                credit_sales - collections
            )

            if total_receivable < 0:
                total_receivable = 0.0

            # ==================================================
            # TOPLAM BORÇ
            # ==================================================

            row = conn.execute("""
                SELECT
                    COALESCE(SUM(
                        CASE
                            WHEN transaction_type = 'purchase_on_credit'
                                THEN amount
                            WHEN transaction_type = 'purchase'
                                 AND payment_method = 'credit'
                                THEN amount
                            ELSE 0
                        END
                    ), 0) AS purchases,

                    COALESCE(SUM(
                        CASE
                            WHEN transaction_type = 'payment_made'
                                THEN ABS(amount)
                            ELSE 0
                        END
                    ), 0) AS payments

                FROM transactions

                WHERE is_cancelled = 0
            """).fetchone()

            credit_purchases = float(
                row["purchases"] or 0
            )

            supplier_payments = float(
                row["payments"] or 0
            )

            total_debt = (
                credit_purchases - supplier_payments
            )

            if total_debt < 0:
                total_debt = 0.0

            # ==================================================
            # KASA
            # ==================================================

            cash_balance = 0.0

            row = conn.execute("""
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM cash_transactions
                WHERE transaction_type IN (
                    'collection',
                    'income'
                )
            """).fetchone()

            if row:
                cash_balance += float(
                    row["total"] or 0
                )

            row = conn.execute("""
                SELECT COALESCE(SUM(amount), 0) AS total
                FROM cash_transactions
                WHERE transaction_type IN (
                    'payment',
                    'expense'
                )
            """).fetchone()

            if row:
                cash_balance -= float(
                    row["total"] or 0
                )

            # ==================================================
            # NET BAKİYE
            # ==================================================

            net_balance = (
                cash_balance
                + total_receivable
                - total_debt
            )

            # ==================================================
            # KARTLAR
            # ==================================================

            self.total_customers_card.value_label.setText(
                str(total_customers)
            )

            self.total_products_card.value_label.setText(
                str(total_products)
            )

            self.total_receivable_card.value_label.setText(
                self.format_money(total_receivable)
            )

            self.total_debt_card.value_label.setText(
                self.format_money(total_debt)
            )

            self.cash_card.value_label.setText(
                self.format_money(cash_balance)
            )

            if net_balance >= 0:

                self.net_balance_card.value_label.setText(
                    f"+{net_balance:,.2f} TL"
                )

            else:

                self.net_balance_card.value_label.setText(
                    f"{net_balance:,.2f} TL"
                )

        except Exception as e:

            print(
                "Dashboard hesaplama hatası:",
                e
            )

        finally:

            if conn:
                conn.close()


    # ======================================================
    # PARA FORMAT
    # ======================================================

    def format_money(self, value):

        return f"{value:,.2f} TL"


# ==========================================================
# PROGRAMI BAŞLAT
# ==========================================================

def main():

    app = QApplication(sys.argv)

    # ======================================================
    # GENEL KOYU TEMA
    # ======================================================

    app.setStyleSheet("""
        QMainWindow {
            background-color: #303030;
        }

        QWidget {
            background-color: #303030;
            color: white;
            font-family: Arial;
        }

        QDialog {
            background-color: #303030;
        }

        QPushButton {
            font-size: 14px;
        }

        QLineEdit,
        QComboBox,
        QSpinBox,
        QDoubleSpinBox,
        QDateEdit {
            background-color: #202020;
            color: white;
            border: 1px solid #555555;
            padding: 6px;
        }

        QTableWidget {
            background-color: #151515;
            color: white;
            gridline-color: #444444;
            alternate-background-color: #1d1d1d;
        }

        QHeaderView::section {
            background-color: #303030;
            color: white;
            padding: 6px;
            border: 1px solid #444444;
        }

        QGroupBox {
            border: 1px solid #555555;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())


# ==========================================================
# ÇALIŞTIR
# ==========================================================

if __name__ == "__main__":
    main()