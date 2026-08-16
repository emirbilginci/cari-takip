from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QLabel,
)

from PySide6.QtCore import Qt

from app.database.connection import get_connection
from app.ui.urun_form import UrunFormDialog


class UrunlerDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Ürünler")
        self.resize(1100, 650)

        self.setup_ui()
        self.load_products()

    # ==================================================
    # ARAYÜZ
    # ==================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        layout.setSpacing(12)

        # ==================================================
        # BAŞLIK
        # ==================================================

        title = QLabel("Ürünler")

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        # ==================================================
        # ÜST BÖLÜM
        # ==================================================

        top_layout = QHBoxLayout()

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Ürün adı veya barkod ara..."
        )

        self.search_input.textChanged.connect(
            self.filter_products
        )

        top_layout.addWidget(
            self.search_input
        )

        self.refresh_button = QPushButton(
            "Yenile"
        )

        self.refresh_button.setMinimumHeight(40)

        self.refresh_button.clicked.connect(
            self.load_products
        )

        top_layout.addWidget(
            self.refresh_button
        )

        self.add_button = QPushButton(
            "+ Yeni Ürün"
        )

        self.add_button.setMinimumHeight(40)

        self.add_button.clicked.connect(
            self.add_product
        )

        top_layout.addWidget(
            self.add_button
        )

        layout.addLayout(
            top_layout
        )

        # ==================================================
        # TABLO
        # ==================================================

        self.table = QTableWidget()

        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Ürün",
            "Barkod",
            "Birim",
            "Alış",
            "Satış",
            "Müşteri",
            "Stok",
            "Durum",
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

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        # ID biraz dar olsun
        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        # Barkod
        self.table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        # Birim
        self.table.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        # Çift tıklama
        self.table.cellDoubleClicked.connect(
            self.edit_product
        )

        layout.addWidget(
            self.table
        )

        # ==================================================
        # ALT BÖLÜM
        # ==================================================

        bottom_layout = QHBoxLayout()

        self.info_label = QLabel(
            "Ürün sayısı: 0"
        )

        bottom_layout.addWidget(
            self.info_label
        )

        bottom_layout.addStretch()

        self.edit_button = QPushButton(
            "Düzenle"
        )

        self.edit_button.clicked.connect(
            self.edit_selected_product
        )

        bottom_layout.addWidget(
            self.edit_button
        )

        self.delete_button = QPushButton(
            "Pasife Al"
        )

        self.delete_button.clicked.connect(
            self.deactivate_product
        )

        bottom_layout.addWidget(
            self.delete_button
        )

        self.close_button = QPushButton(
            "Kapat"
        )

        self.close_button.clicked.connect(
            self.reject
        )

        bottom_layout.addWidget(
            self.close_button
        )

        layout.addLayout(
            bottom_layout
        )

    # ==================================================
    # ÜRÜNLERİ GETİR
    # ==================================================

    def load_products(self):

        conn = None

        try:

            conn = get_connection()

            rows = conn.execute(
                """
                SELECT
                    id,
                    product_name,
                    barcode,
                    unit,
                    purchase_price,
                    sale_price,
                    customer_price,
                    stock_quantity,
                    critical_stock,
                    description
                FROM products
                WHERE is_active = 1
                ORDER BY product_name COLLATE NOCASE
                """
            ).fetchall()

            self.products = [
                dict(row)
                for row in rows
            ]

            self.display_products(
                self.products
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Ürünler yüklenemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # ==================================================
    # ÜRÜNLERİ TABLOYA YAZ
    # ==================================================

    def display_products(
        self,
        products
    ):

        self.table.setRowCount(0)

        for row_index, product in enumerate(
            products
        ):

            self.table.insertRow(
                row_index
            )

            # ------------------------------------------
            # VERİLER
            # ------------------------------------------

            product_id = product["id"]

            name = (
                product["product_name"]
                or ""
            )

            barcode = (
                product["barcode"]
                or ""
            )

            unit = (
                product["unit"]
                or "adet"
            )

            purchase_price = float(
                product["purchase_price"]
                or 0
            )

            sale_price = float(
                product["sale_price"]
                or 0
            )

            customer_price = float(
                product["customer_price"]
                or 0
            )

            stock = float(
                product["stock_quantity"]
                or 0
            )

            critical_stock = float(
                product["critical_stock"]
                or 0
            )

            # ------------------------------------------
            # STOK DURUMU
            # ------------------------------------------

            if stock <= 0:

                status = "Tükendi"

            elif stock <= critical_stock:

                status = "Kritik Stok"

            else:

                status = "Normal"

            values = [
                str(product_id),
                name,
                barcode,
                unit,
                f"{purchase_price:,.2f} TL",
                f"{sale_price:,.2f} TL",
                f"{customer_price:,.2f} TL",
                f"{stock:g}",
                status,
            ]

            # ------------------------------------------
            # TABLOYA YAZ
            # ------------------------------------------

            for column_index, value in enumerate(
                values
            ):

                item = QTableWidgetItem(
                    str(value)
                )

                item.setTextAlignment(
                    Qt.AlignCenter
                )

                if column_index == 1:

                    item.setTextAlignment(
                        Qt.AlignLeft
                        | Qt.AlignVCenter
                    )

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )

            # ------------------------------------------
            # STOK DURUMUNA GÖRE SATIR
            # ------------------------------------------

            if stock <= 0:

                for column in range(
                    self.table.columnCount()
                ):

                    item = self.table.item(
                        row_index,
                        column
                    )

                    if item:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

            elif stock <= critical_stock:

                for column in range(
                    self.table.columnCount()
                ):

                    item = self.table.item(
                        row_index,
                        column
                    )

                    if item:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

        self.info_label.setText(
            f"Ürün sayısı: {len(products)}"
        )

    # ==================================================
    # ARAMA
    # ==================================================

    def filter_products(
        self,
        text
    ):

        text = text.lower().strip()

        if not text:

            self.display_products(
                self.products
            )

            return

        filtered = []

        for product in self.products:

            name = (
                product["product_name"]
                or ""
            ).lower()

            barcode = (
                product["barcode"]
                or ""
            ).lower()

            if (
                text in name
                or text in barcode
            ):

                filtered.append(
                    product
                )

        self.display_products(
            filtered
        )

    # ==================================================
    # YENİ ÜRÜN
    # ==================================================

    def add_product(self):

        dialog = UrunFormDialog(
            None,
            self
        )

        if dialog.exec() == QDialog.Accepted:

            self.load_products()

    # ==================================================
    # ÇİFT TIKLAMA İLE DÜZENLE
    # ==================================================

    def edit_product(
        self,
        row,
        column
    ):

        item = self.table.item(
            row,
            0
        )

        if not item:
            return

        try:

            product_id = int(
                item.text()
            )

        except ValueError:

            return

        self.open_edit_dialog(
            product_id
        )

    # ==================================================
    # SEÇİLİ ÜRÜNÜ DÜZENLE
    # ==================================================

    def edit_selected_product(
        self
    ):

        row = (
            self.table.currentRow()
        )

        if row < 0:

            QMessageBox.information(
                self,
                "Ürün Seçilmedi",
                "Lütfen düzenlemek istediğiniz "
                "ürünü seçin."
            )

            return

        item = self.table.item(
            row,
            0
        )

        if not item:
            return

        product_id = int(
            item.text()
        )

        self.open_edit_dialog(
            product_id
        )

    # ==================================================
    # DÜZENLEME PENCERESİ
    # ==================================================

    def open_edit_dialog(
        self,
        product_id
    ):

        dialog = UrunFormDialog(
            product_id,
            self
        )

        if dialog.exec() == QDialog.Accepted:

            self.load_products()

    # ==================================================
    # PASİFE AL
    # ==================================================

    def deactivate_product(
        self
    ):

        row = (
            self.table.currentRow()
        )

        if row < 0:

            QMessageBox.information(
                self,
                "Ürün Seçilmedi",
                "Lütfen pasife almak istediğiniz "
                "ürünü seçin."
            )

            return

        item = self.table.item(
            row,
            0
        )

        if not item:
            return

        product_id = int(
            item.text()
        )

        name_item = self.table.item(
            row,
            1
        )

        product_name = (
            name_item.text()
            if name_item
            else "Bu ürün"
        )

        answer = QMessageBox.question(
            self,
            "Ürünü Pasife Al",
            f"'{product_name}' ürününü pasife "
            f"almak istediğinize emin misiniz?",
            QMessageBox.Yes
            | QMessageBox.No
        )

        if answer != QMessageBox.Yes:

            return

        conn = None

        try:

            conn = get_connection()

            conn.execute(
                """
                UPDATE products
                SET
                    is_active = 0,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (product_id,)
            )

            conn.commit()

            self.load_products()

            QMessageBox.information(
                self,
                "Başarılı",
                f"'{product_name}' pasife alındı."
            )

        except Exception as e:

            if conn:
                conn.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"Ürün pasife alınamadı.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()