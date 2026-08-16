from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QComboBox,
    QDialogButtonBox,
    QHeaderView,
)

from app.database.connection import get_connection
from app.ui.cari_detay import CariDetayDialog


class CarilerPage(QWidget):

    def __init__(self):
        super().__init__()

        self.customers = []

        self.setWindowTitle("Cariler")
        self.resize(1000, 650)

        self.setup_ui()
        self.load_customers()

    # =====================================================
    # ARAYÜZ
    # =====================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        layout.setSpacing(15)

        # =================================================
        # BAŞLIK
        # =================================================

        title = QLabel("Cariler")

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        # =================================================
        # ÜST BAR
        # =================================================

        top_layout = QHBoxLayout()

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Cari ara..."
        )

        self.search_input.textChanged.connect(
            self.filter_customers
        )

        top_layout.addWidget(
            self.search_input
        )

        add_button = QPushButton(
            "+ Yeni Cari"
        )

        add_button.setMinimumHeight(40)

        add_button.clicked.connect(
            self.open_add_customer_dialog
        )

        top_layout.addWidget(
            add_button
        )

        refresh_button = QPushButton(
            "Yenile"
        )

        refresh_button.setMinimumHeight(40)

        refresh_button.clicked.connect(
            self.load_customers
        )

        top_layout.addWidget(
            refresh_button
        )

        layout.addLayout(
            top_layout
        )

        # =================================================
        # TABLO
        # =================================================

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Ad / Ünvan",
            "Telefon",
            "Adres",
            "Cari Türü",
        ])

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )

        self.table.setAlternatingRowColors(
            True
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.Stretch
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        # Çift tıklayınca cari detayı
        self.table.cellDoubleClicked.connect(
            self.open_customer_detail
        )

        layout.addWidget(
            self.table
        )

        # =================================================
        # ALT BİLGİ
        # =================================================

        self.info_label = QLabel(
            "Cari sayısı: 0"
        )

        self.info_label.setStyleSheet("""
            color: #888888;
            font-size: 13px;
        """)

        layout.addWidget(
            self.info_label
        )

    # =====================================================
    # CARİLERİ YÜKLE
    # =====================================================

    def load_customers(self):

        connection = None

        try:

            connection = get_connection()

            rows = connection.execute(
                """
                SELECT
                    id,
                    name,
                    phone,
                    address,
                    tax_number,
                    type,
                    notes
                FROM customers
                WHERE is_active = 1
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()

            self.customers = [
                dict(row)
                for row in rows
            ]

            self.display_customers(
                self.customers
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Hata",
                f"Cariler yüklenemedi.\n\n{error}"
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # CARİLERİ TABLOYA YAZ
    # =====================================================

    def display_customers(
        self,
        customers
    ):

        self.table.setRowCount(0)

        for row_index, customer in enumerate(
            customers
        ):

            self.table.insertRow(
                row_index
            )

            # ID
            self.table.setItem(
                row_index,
                0,
                QTableWidgetItem(
                    str(customer["id"])
                )
            )

            # Ad
            self.table.setItem(
                row_index,
                1,
                QTableWidgetItem(
                    customer["name"] or ""
                )
            )

            # Telefon
            self.table.setItem(
                row_index,
                2,
                QTableWidgetItem(
                    customer["phone"] or ""
                )
            )

            # Adres
            self.table.setItem(
                row_index,
                3,
                QTableWidgetItem(
                    customer["address"] or ""
                )
            )

            # Cari türü
            customer_type = self.get_customer_type_text(
                customer["type"]
            )

            self.table.setItem(
                row_index,
                4,
                QTableWidgetItem(
                    customer_type
                )
            )

        self.info_label.setText(
            f"Cari sayısı: {len(customers)}"
        )

    # =====================================================
    # CARİ TÜRÜ
    # =====================================================

    def get_customer_type_text(
        self,
        customer_type
    ):

        if customer_type == "customer":
            return "Müşteri"

        if customer_type == "supplier":
            return "Tedarikçi"

        if customer_type == "both":
            return "Müşteri / Tedarikçi"

        return ""

    # =====================================================
    # ARAMA
    # =====================================================

    def filter_customers(
        self,
        text
    ):

        text = (
            text
            .lower()
            .strip()
        )

        if not text:

            self.display_customers(
                self.customers
            )

            return

        filtered = []

        for customer in self.customers:

            name = (
                customer["name"]
                or ""
            ).lower()

            phone = (
                customer["phone"]
                or ""
            ).lower()

            tax_number = (
                customer["tax_number"]
                or ""
            ).lower()

            if (
                text in name
                or text in phone
                or text in tax_number
            ):

                filtered.append(
                    customer
                )

        self.display_customers(
            filtered
        )

    # =====================================================
    # CARİ DETAYI
    # =====================================================

    def open_customer_detail(
        self,
        row,
        column
    ):

        item = self.table.item(
            row,
            0
        )

        if item is None:
            return

        try:

            customer_id = int(
                item.text()
            )

            dialog = CariDetayDialog(
                customer_id,
                self
            )

            dialog.exec()

            # Detaydan işlem yapıldıysa listeyi yenile
            self.load_customers()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Hata",
                f"Cari detayı açılamadı.\n\n{error}"
            )

    # =====================================================
    # YENİ CARİ
    # =====================================================

    def open_add_customer_dialog(
        self
    ):

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "Yeni Cari"
        )

        dialog.setMinimumWidth(
            450
        )

        form = QFormLayout(
            dialog
        )

        # -------------------------------------------------
        # AD / ÜNVAN
        # -------------------------------------------------

        name_input = QLineEdit()

        name_input.setPlaceholderText(
            "Örn: Ahmet Yılmaz"
        )

        form.addRow(
            "Ad / Ünvan:",
            name_input
        )

        # -------------------------------------------------
        # TELEFON
        # -------------------------------------------------

        phone_input = QLineEdit()

        phone_input.setPlaceholderText(
            "Örn: 05551234567"
        )

        form.addRow(
            "Telefon:",
            phone_input
        )

        # -------------------------------------------------
        # ADRES
        # -------------------------------------------------

        address_input = QLineEdit()

        address_input.setPlaceholderText(
            "Adres"
        )

        form.addRow(
            "Adres:",
            address_input
        )

        # -------------------------------------------------
        # VERGİ NUMARASI
        # -------------------------------------------------

        tax_number_input = QLineEdit()

        tax_number_input.setPlaceholderText(
            "Vergi numarası"
        )

        form.addRow(
            "Vergi Numarası:",
            tax_number_input
        )

        # -------------------------------------------------
        # CARİ TÜRÜ
        # -------------------------------------------------

        type_input = QComboBox()

        type_input.addItem(
            "Müşteri",
            "customer"
        )

        type_input.addItem(
            "Tedarikçi",
            "supplier"
        )

        type_input.addItem(
            "Müşteri / Tedarikçi",
            "both"
        )

        form.addRow(
            "Cari Türü:",
            type_input
        )

        # -------------------------------------------------
        # NOT
        # -------------------------------------------------

        notes_input = QLineEdit()

        notes_input.setPlaceholderText(
            "İsteğe bağlı"
        )

        form.addRow(
            "Not:",
            notes_input
        )

        # -------------------------------------------------
        # BUTONLAR
        # -------------------------------------------------

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            dialog.accept
        )

        buttons.rejected.connect(
            dialog.reject
        )

        form.addRow(
            buttons
        )

        # -------------------------------------------------
        # DİYALOĞU AÇ
        # -------------------------------------------------

        result = dialog.exec()

        if result != QDialog.Accepted:
            return

        # =================================================
        # VERİLER
        # =================================================

        name = (
            name_input
            .text()
            .strip()
        )

        phone = (
            phone_input
            .text()
            .strip()
        )

        address = (
            address_input
            .text()
            .strip()
        )

        tax_number = (
            tax_number_input
            .text()
            .strip()
        )

        customer_type = (
            type_input.currentData()
        )

        notes = (
            notes_input
            .text()
            .strip()
        )

        # =================================================
        # KONTROL
        # =================================================

        if not name:

            QMessageBox.warning(
                self,
                "Eksik Bilgi",
                "Ad / Ünvan alanı boş bırakılamaz."
            )

            return

        # =================================================
        # KAYDET
        # =================================================

        connection = None

        try:

            connection = get_connection()

            connection.execute(
                """
                INSERT INTO customers (
                    name,
                    phone,
                    address,
                    tax_number,
                    type,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    phone,
                    address,
                    tax_number,
                    customer_type,
                    notes,
                )
            )

            connection.commit()

            QMessageBox.information(
                self,
                "Başarılı",
                f"{name} başarıyla eklendi."
            )

            self.load_customers()

        except Exception as error:

            if connection:
                connection.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"Cari kaydedilemedi.\n\n{error}"
            )

        finally:

            if connection:
                connection.close()