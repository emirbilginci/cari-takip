from PySide6.QtWidgets import (

    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLabel,
    QHeaderView,
    QDateEdit,
    QGroupBox,
)

from PySide6.QtCore import QDate, Qt

from app.database.connection import get_connection


class YeniIslemDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Yeni İşlem")
        self.resize(1050, 700)

        self.setup_ui()
        self.load_customers()
        self.load_products()

    # ==================================================
    # ARAYÜZ
    # ==================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout.setSpacing(15)

        # ==================================================
        # BAŞLIK
        # ==================================================

        title = QLabel("Yeni İşlem")

        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
            }
        """)

        layout.addWidget(title)

        # ==================================================
        # İŞLEM BİLGİLERİ
        # ==================================================

        info_group = QGroupBox("İşlem Bilgileri")

        info_layout = QFormLayout(info_group)

        # İşlem türü
        self.transaction_type = QComboBox()

        self.transaction_type.addItem(
            "Satış",
            "sale"
        )

        self.transaction_type.addItem(
            "Alış",
            "purchase"
        )

        self.transaction_type.currentIndexChanged.connect(
            self.update_price
        )

        info_layout.addRow(
            "İşlem Türü:",
            self.transaction_type
        )

        # Cari
        self.customer_combo = QComboBox()

        info_layout.addRow(
            "Cari:",
            self.customer_combo
        )

        # Ödeme yöntemi
        self.payment_method = QComboBox()

        self.payment_method.addItem(
            "Peşin",
            "cash"
        )

        self.payment_method.addItem(
            "Veresiye",
            "credit"
        )

        info_layout.addRow(
            "Ödeme:",
            self.payment_method
        )

        # Tarih
        self.date_input = QDateEdit()

        self.date_input.setDate(
            QDate.currentDate()
        )

        self.date_input.setCalendarPopup(
            True
        )

        info_layout.addRow(
            "Tarih:",
            self.date_input
        )

        # Vade
        self.due_date_input = QDateEdit()

        self.due_date_input.setDate(
            QDate.currentDate()
        )

        self.due_date_input.setCalendarPopup(
            True
        )

        info_layout.addRow(
            "Vade Tarihi:",
            self.due_date_input
        )

        # Fatura
        self.invoice_input = QLineEdit()

        self.invoice_input.setPlaceholderText(
            "İsteğe bağlı"
        )

        info_layout.addRow(
            "Fatura No:",
            self.invoice_input
        )

        # Açıklama
        self.description_input = QLineEdit()

        self.description_input.setPlaceholderText(
            "İşlem açıklaması"
        )

        info_layout.addRow(
            "Açıklama:",
            self.description_input
        )

        layout.addWidget(info_group)

        # ==================================================
        # ÜRÜN EKLEME
        # ==================================================

        product_group = QGroupBox(
            "Ürün Ekle"
        )

        product_layout = QHBoxLayout(
            product_group
        )

        self.product_combo = QComboBox()

        self.product_combo.currentIndexChanged.connect(
            self.update_price
        )

        product_layout.addWidget(
            self.product_combo,
            3
        )

        self.quantity_input = QDoubleSpinBox()

        self.quantity_input.setRange(
            0.001,
            999999
        )

        self.quantity_input.setDecimals(
            3
        )

        self.quantity_input.setValue(
            1
        )

        self.quantity_input.setSuffix(
            " adet"
        )

        product_layout.addWidget(
            self.quantity_input
        )

        self.price_input = QDoubleSpinBox()

        self.price_input.setRange(
            0,
            999999999
        )

        self.price_input.setDecimals(
            2
        )

        self.price_input.setSuffix(
            " TL"
        )

        product_layout.addWidget(
            self.price_input
        )

        add_product_button = QPushButton(
            "+ Ürün Ekle"
        )

        add_product_button.clicked.connect(
            self.add_item
        )

        product_layout.addWidget(
            add_product_button
        )

        layout.addWidget(
            product_group
        )

        # ==================================================
        # ÜRÜN TABLOSU
        # ==================================================

        self.items_table = QTableWidget()

        self.items_table.setColumnCount(6)

        self.items_table.setHorizontalHeaderLabels([
            "Ürün ID",
            "Ürün",
            "Miktar",
            "Birim Fiyat",
            "Toplam",
            "Sil",
        ])

        self.items_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.items_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.items_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.items_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        self.items_table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        self.items_table.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        layout.addWidget(
            self.items_table
        )

        # ==================================================
        # TOPLAM
        # ==================================================

        total_layout = QHBoxLayout()

        total_layout.addStretch()

        total_title = QLabel(
            "Genel Toplam:"
        )

        total_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        total_layout.addWidget(
            total_title
        )

        self.total_label = QLabel(
            "0.00 TL"
        )

        self.total_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
        """)

        total_layout.addWidget(
            self.total_label
        )

        layout.addLayout(
            total_layout
        )

        # ==================================================
        # ALT BUTONLAR
        # ==================================================

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        self.save_button = QPushButton(
            "İşlemi Kaydet"
        )

        self.save_button.setMinimumHeight(
            45
        )

        self.save_button.clicked.connect(
            self.save_transaction
        )

        button_layout.addWidget(
            self.save_button
        )

        self.cancel_button = QPushButton(
            "Kapat"
        )

        self.cancel_button.setMinimumHeight(
            45
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        button_layout.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            button_layout
        )

    # ==================================================
    # CARİLERİ GETİR
    # ==================================================

    def load_customers(self):

        conn = None

        try:

            conn = get_connection()

            rows = conn.execute(
                """
                SELECT
                    id,
                    name
                FROM customers
                WHERE is_active = 1
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()

            self.customer_combo.clear()

            for row in rows:

                self.customer_combo.addItem(
                    row["name"],
                    row["id"]
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Cariler yüklenemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

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
                    purchase_price,
                    sale_price,
                    customer_price,
                    stock_quantity
                FROM products
                WHERE is_active = 1
                ORDER BY product_name COLLATE NOCASE
                """
            ).fetchall()

            self.products = [
                dict(row)
                for row in rows
            ]

            self.product_combo.clear()

            for product in self.products:

                text = product["product_name"]

                if product["barcode"]:

                    text += (
                        f" | {product['barcode']}"
                    )

                self.product_combo.addItem(
                    text,
                    product["id"]
                )

            self.update_price()

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
    # FİYATI GÜNCELLE
    # ==================================================

    def update_price(self):

        product_id = (
            self.product_combo.currentData()
        )

        if not product_id:
            return

        transaction_type = (
            self.transaction_type.currentData()
        )

        product = None

        for item in getattr(
            self,
            "products",
            []
        ):

            if item["id"] == product_id:

                product = item
                break

        if not product:
            return

        if transaction_type == "purchase":

            price = float(
                product["purchase_price"]
                or 0
            )

        else:

            price = float(
                product["customer_price"]
                or product["sale_price"]
                or 0
            )

        self.price_input.setValue(
            price
        )

    # ==================================================
    # ÜRÜN EKLE
    # ==================================================

    def add_item(self):

        product_id = (
            self.product_combo.currentData()
        )

        if not product_id:

            QMessageBox.warning(
                self,
                "Ürün Seçilmedi",
                "Lütfen bir ürün seçin."
            )

            return

        product = None

        for item in self.products:

            if item["id"] == product_id:

                product = item
                break

        if not product:
            return

        quantity = (
            self.quantity_input.value()
        )

        price = (
            self.price_input.value()
        )

        if quantity <= 0:

            QMessageBox.warning(
                self,
                "Hatalı Miktar",
                "Miktar 0'dan büyük olmalıdır."
            )

            return

        # Satışta stok kontrolü
        if (
            self.transaction_type.currentData()
            == "sale"
        ):

            stock = float(
                product["stock_quantity"]
                or 0
            )

            # Aynı ürün daha önce eklenmiş mi?
            existing_quantity = 0

            for row in range(
                self.items_table.rowCount()
            ):

                item = self.items_table.item(
                    row,
                    0
                )

                if (
                    item
                    and int(item.text())
                    == product_id
                ):

                    existing_quantity += float(
                        self.items_table.item(
                            row,
                            2
                        ).text()
                    )

            if existing_quantity + quantity > stock:

                QMessageBox.warning(
                    self,
                    "Yetersiz Stok",
                    f"{product['product_name']} için "
                    f"yeterli stok yok.\n\n"
                    f"Mevcut stok: {stock:g}"
                )

                return

        total = (
            quantity * price
        )

        row = self.items_table.rowCount()

        self.items_table.insertRow(
            row
        )

        values = [
            str(product_id),
            product["product_name"],
            f"{quantity:g}",
            f"{price:,.2f} TL",
            f"{total:,.2f} TL",
        ]

        for column, value in enumerate(
            values
        ):

            item = QTableWidgetItem(
                value
            )

            item.setTextAlignment(
                Qt.AlignCenter
            )

            if column == 1:

                item.setTextAlignment(
                    Qt.AlignLeft
                    | Qt.AlignVCenter
                )

            self.items_table.setItem(
                row,
                column,
                item
            )

        delete_button = QPushButton(
            "Sil"
        )

        delete_button.clicked.connect(
            lambda checked=False,
            r=row:
            self.remove_item(r)
        )

        self.items_table.setCellWidget(
            row,
            5,
            delete_button
        )

        self.update_total()

    # ==================================================
    # ÜRÜN SİL
    # ==================================================

    def remove_item(
        self,
        row
    ):

        if (
            row < 0
            or row >= self.items_table.rowCount()
        ):

            return

        self.items_table.removeRow(
            row
        )

        self.update_delete_buttons()
        self.update_total()

    # ==================================================
    # SİL BUTONLARINI YENİLE
    # ==================================================

    def update_delete_buttons(self):

        for row in range(
            self.items_table.rowCount()
        ):

            button = QPushButton(
                "Sil"
            )

            button.clicked.connect(
                lambda checked=False,
                r=row:
                self.remove_item(r)
            )

            self.items_table.setCellWidget(
                row,
                5,
                button
            )

    # ==================================================
    # TOPLAM
    # ==================================================

    def update_total(self):

        total = 0.0

        for row in range(
            self.items_table.rowCount()
        ):

            item = self.items_table.item(
                row,
                4
            )

            if not item:
                continue

            value = (
                item.text()
                .replace(" TL", "")
                .replace(",", "")
            )

            try:

                total += float(value)

            except ValueError:

                pass

        self.total_label.setText(
            f"{total:,.2f} TL"
        )

    # ==================================================
    # İŞLEMİ KAYDET
    # ==================================================

    def save_transaction(self):

        customer_id = (
            self.customer_combo.currentData()
        )

        if not customer_id:

            QMessageBox.warning(
                self,
                "Cari Seçilmedi",
                "Lütfen bir cari seçin."
            )

            return

        if self.items_table.rowCount() == 0:

            QMessageBox.warning(
                self,
                "Ürün Yok",
                "İşleme en az bir ürün eklemelisiniz."
            )

            return

        transaction_type = (
            self.transaction_type.currentData()
        )

        payment_method = (
            self.payment_method.currentData()
        )

        total = self.calculate_total()

        if total <= 0:

            QMessageBox.warning(
                self,
                "Hatalı Tutar",
                "İşlem toplamı 0'dan büyük olmalıdır."
            )

            return

        # --------------------------------------------------
        # SATIŞTA SON STOK KONTROLÜ
        # --------------------------------------------------

        conn = None

        try:

            conn = get_connection()

            conn.execute(
                "BEGIN"
            )

            # ----------------------------------------------
            # İŞLEMİ OLUŞTUR
            # ----------------------------------------------

            description = (
                self.description_input
                .text()
                .strip()
            )

            invoice_number = (
                self.invoice_input
                .text()
                .strip()
            )

            due_date = None

            if payment_method == "credit":

                due_date = (
                    self.due_date_input
                    .date()
                    .toString(
                        "yyyy-MM-dd"
                    )
                )

            transaction_date = (
                self.date_input
                .date()
                .toString(
                    "yyyy-MM-dd"
                )
            )

            cursor = conn.execute(
                """
                INSERT INTO transactions (
                    customer_id,
                    transaction_date,
                    transaction_type,
                    description,
                    amount,
                    payment_method,
                    due_date,
                    invoice_number,
                    is_cancelled
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?,0)
                """,
                (
                    customer_id,
                    transaction_date,
                    transaction_type,
                    description,
                    total,
                    payment_method,
                    due_date,
                    invoice_number,
                )
            )

            transaction_id = cursor.lastrowid

            # ----------------------------------------------
            # ÜRÜNLER
            # ----------------------------------------------

            for row in range(
                self.items_table.rowCount()
            ):

                product_id = int(
                    self.items_table.item(
                        row,
                        0
                    ).text()
                )

                quantity = float(
                    self.items_table.item(
                        row,
                        2
                    ).text()
                )

                price_text = (
                    self.items_table.item(
                        row,
                        3
                    ).text()
                    .replace(
                        " TL",
                        ""
                    )
                    .replace(
                        ",",
                        ""
                    )
                )

                unit_price = float(
                    price_text
                )

                total_price = (
                    quantity
                    * unit_price
                )

                # ------------------------------------------
                # STOK
                # ------------------------------------------

                product = conn.execute(
                    """
                    SELECT
                        product_name,
                        stock_quantity
                    FROM products
                    WHERE id = ?
                      AND is_active = 1
                    """,
                    (product_id,)
                ).fetchone()

                if not product:

                    raise Exception(
                        "Ürün bulunamadı."
                    )

                previous_stock = float(
                    product["stock_quantity"]
                    or 0
                )

                # Satış = stok düşer
                if transaction_type == "sale":

                    new_stock = (
                        previous_stock
                        - quantity
                    )

                    if new_stock < 0:

                        raise Exception(
                            f"{product['product_name']} "
                            f"için yeterli stok yok."
                        )

                    movement_type = "sale"

                    movement_description = (
                        f"Satış #{transaction_id}"
                    )

                # Alış = stok artar
                else:

                    new_stock = (
                        previous_stock
                        + quantity
                    )

                    movement_type = "purchase"

                    movement_description = (
                        f"Alış #{transaction_id}"
                    )

                # ------------------------------------------
                # TRANSACTION ITEM
                # ------------------------------------------

                conn.execute(
                    """
                    INSERT INTO transaction_items (
                        transaction_id,
                        product_id,
                        quantity,
                        unit_price,
                        total_price
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        transaction_id,
                        product_id,
                        quantity,
                        unit_price,
                        total_price,
                    )
                )

                # ------------------------------------------
                # ÜRÜN STOĞUNU GÜNCELLE
                # ------------------------------------------

                conn.execute(
                    """
                    UPDATE products
                    SET
                        stock_quantity = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        new_stock,
                        product_id,
                    )
                )

                # ------------------------------------------
                # STOK HAREKETİ
                # ------------------------------------------

                conn.execute(
                    """
                    INSERT INTO stock_movements (
                        product_id,
                        transaction_type,
                        quantity,
                        previous_stock,
                        new_stock,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        product_id,
                        movement_type,
                        quantity,
                        previous_stock,
                        new_stock,
                        movement_description,
                    )
                )

            # ----------------------------------------------
            # PEŞİN İŞLEM → KASA
            # ----------------------------------------------

            if payment_method == "cash":

                cash_type = (
                    "collection"
                    if transaction_type == "sale"
                    else "payment"
                )

                cash_description = (
                    "Peşin satış"
                    if transaction_type == "sale"
                    else "Peşin alış"
                )

                conn.execute(
                    """
                    INSERT INTO cash_transactions (
                        customer_id,
                        transaction_type,
                        amount,
                        description
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        customer_id,
                        cash_type,
                        total,
                        f"{cash_description} #{transaction_id}",
                    )
                )

            conn.commit()

            QMessageBox.information(
                self,
                "Başarılı",
                f"{'Satış' if transaction_type == 'sale' else 'Alış'} "
                f"başarıyla kaydedildi.\n\n"
                f"Toplam: {total:,.2f} TL"
            )

            self.accept()

        except Exception as e:

            if conn:

                conn.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"İşlem kaydedilemedi.\n\n{e}"
            )

        finally:

            if conn:

                conn.close()

    # ==================================================
    # TOPLAM HESAPLA
    # ==================================================

    def calculate_total(self):

        total = 0.0

        for row in range(
            self.items_table.rowCount()
        ):

            item = self.items_table.item(
                row,
                4
            )

            if not item:
                continue

            value = (
                item.text()
                .replace(
                    " TL",
                    ""
                )
                .replace(
                    ",",
                    ""
                )
            )

            try:

                total += float(
                    value
                )

            except ValueError:

                pass

        return total
