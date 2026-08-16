from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QHeaderView,
    QGroupBox,
)

from PySide6.QtCore import Qt

from app.database.connection import get_connection


class StokHareketleriDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Stok Hareketleri")
        self.resize(1150, 700)

        self.setup_ui()
        self.load_products()
        self.load_movements()

    # =========================================================
    # ARAYÜZ
    # =========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            25,
            25,
            25,
            25
        )

        layout.setSpacing(15)

        # =====================================================
        # BAŞLIK
        # =====================================================

        title = QLabel("Stok Hareketleri")

        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
            }
        """)

        layout.addWidget(title)

        subtitle = QLabel(
            "Stok giriş ve çıkış işlemlerini buradan yönetebilirsiniz."
        )

        subtitle.setStyleSheet("""
            QLabel {
                color: #aaaaaa;
                font-size: 13px;
            }
        """)

        layout.addWidget(subtitle)

        # =====================================================
        # İŞLEM PANELİ
        # =====================================================

        group = QGroupBox("Yeni Stok Hareketi")

        group_layout = QVBoxLayout(group)

        form = QFormLayout()

        # -----------------------------------------------------
        # ÜRÜN
        # -----------------------------------------------------

        self.product_combo = QComboBox()

        self.product_combo.setMinimumHeight(38)

        self.product_combo.currentIndexChanged.connect(
            self.update_current_stock
        )

        form.addRow(
            "Ürün:",
            self.product_combo
        )

        # -----------------------------------------------------
        # MEVCUT STOK
        # -----------------------------------------------------

        self.current_stock_label = QLabel(
            "0"
        )

        self.current_stock_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
        """)

        form.addRow(
            "Mevcut Stok:",
            self.current_stock_label
        )

        # -----------------------------------------------------
        # HAREKET TÜRÜ
        # -----------------------------------------------------

        self.type_combo = QComboBox()

        self.type_combo.addItem(
            "📥 Stok Girişi",
            "in"
        )

        self.type_combo.addItem(
            "📤 Stok Çıkışı",
            "out"
        )

        self.type_combo.setMinimumHeight(38)

        form.addRow(
            "Hareket Türü:",
            self.type_combo
        )

        # -----------------------------------------------------
        # MİKTAR
        # -----------------------------------------------------

        self.quantity_input = QDoubleSpinBox()

        self.quantity_input.setRange(
            0.001,
            999999999
        )

        self.quantity_input.setDecimals(
            3
        )

        self.quantity_input.setSingleStep(
            1
        )

        self.quantity_input.setMinimumHeight(
            38
        )

        form.addRow(
            "Miktar:",
            self.quantity_input
        )

        # -----------------------------------------------------
        # AÇIKLAMA
        # -----------------------------------------------------

        self.description_input = QLineEdit()

        self.description_input.setPlaceholderText(
            "Örn: Depoya yeni ürün geldi"
        )

        self.description_input.setMinimumHeight(
            38
        )

        form.addRow(
            "Açıklama:",
            self.description_input
        )

        group_layout.addLayout(form)

        # -----------------------------------------------------
        # BUTONLAR
        # -----------------------------------------------------

        button_layout = QHBoxLayout()

        self.stock_in_button = QPushButton(
            "📥 Stok Girişi Yap"
        )

        self.stock_in_button.setMinimumHeight(
            42
        )

        self.stock_in_button.clicked.connect(
            self.stock_in
        )

        self.stock_out_button = QPushButton(
            "📤 Stok Çıkışı Yap"
        )

        self.stock_out_button.setMinimumHeight(
            42
        )

        self.stock_out_button.clicked.connect(
            self.stock_out
        )

        self.refresh_button = QPushButton(
            "🔄 Yenile"
        )

        self.refresh_button.setMinimumHeight(
            42
        )

        self.refresh_button.clicked.connect(
            self.refresh_all
        )

        button_layout.addWidget(
            self.stock_in_button
        )

        button_layout.addWidget(
            self.stock_out_button
        )

        button_layout.addWidget(
            self.refresh_button
        )

        group_layout.addLayout(
            button_layout
        )

        layout.addWidget(group)

        # =====================================================
        # HAREKET GEÇMİŞİ
        # =====================================================

        history_title = QLabel(
            "Stok Hareket Geçmişi"
        )

        history_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                margin-top: 5px;
            }
        """)

        layout.addWidget(
            history_title
        )

        # =====================================================
        # TABLO
        # =====================================================

        self.table = QTableWidget()

        self.table.setColumnCount(
            8
        )

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Ürün",
            "Hareket",
            "Miktar",
            "Önceki Stok",
            "Yeni Stok",
            "Açıklama",
            "Tarih",
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

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeToContents
        )

        self.table.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.ResizeToContents
        )

        layout.addWidget(
            self.table
        )

        # =====================================================
        # ALT
        # =====================================================

        bottom_layout = QHBoxLayout()

        self.info_label = QLabel(
            "Hareket sayısı: 0"
        )

        bottom_layout.addWidget(
            self.info_label
        )

        bottom_layout.addStretch()

        close_button = QPushButton(
            "Kapat"
        )

        close_button.setMinimumWidth(
            100
        )

        close_button.clicked.connect(
            self.reject
        )

        bottom_layout.addWidget(
            close_button
        )

        layout.addLayout(
            bottom_layout
        )

    # =========================================================
    # ÜRÜNLERİ GETİR
    # =========================================================

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
                    stock_quantity
                FROM products
                WHERE is_active = 1
                ORDER BY product_name COLLATE NOCASE
                """
            ).fetchall()

            self.product_combo.clear()

            for row in rows:

                product_id = row["id"]

                name = row["product_name"]

                barcode = row["barcode"] or ""

                unit = row["unit"] or "adet"

                text = name

                if barcode:
                    text += f" | {barcode}"

                text += f" | {unit}"

                self.product_combo.addItem(
                    text,
                    product_id
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

        self.update_current_stock()

    # =========================================================
    # MEVCUT STOK
    # =========================================================

    def update_current_stock(self):

        product_id = self.product_combo.currentData()

        if not product_id:

            self.current_stock_label.setText(
                "0"
            )

            return

        conn = None

        try:

            conn = get_connection()

            row = conn.execute(
                """
                SELECT
                    stock_quantity,
                    unit
                FROM products
                WHERE id = ?
                """,
                (product_id,)
            ).fetchone()

            if row:

                stock = float(
                    row["stock_quantity"] or 0
                )

                unit = row["unit"] or "adet"

                self.current_stock_label.setText(
                    f"{stock:g} {unit}"
                )

            else:

                self.current_stock_label.setText(
                    "0"
                )

        except Exception as e:

            self.current_stock_label.setText(
                "Hata"
            )

        finally:

            if conn:
                conn.close()

    # =========================================================
    # STOK GİRİŞİ
    # =========================================================

    def stock_in(self):

        self.perform_stock_movement(
            "in"
        )

    # =========================================================
    # STOK ÇIKIŞI
    # =========================================================

    def stock_out(self):

        self.perform_stock_movement(
            "out"
        )

    # =========================================================
    # STOK HAREKETİ
    # =========================================================

    def perform_stock_movement(
        self,
        movement_type
    ):

        product_id = self.product_combo.currentData()

        if not product_id:

            QMessageBox.warning(
                self,
                "Ürün Seçilmedi",
                "Lütfen bir ürün seçin."
            )

            return

        quantity = float(
            self.quantity_input.value()
        )

        if quantity <= 0:

            QMessageBox.warning(
                self,
                "Geçersiz Miktar",
                "Miktar 0'dan büyük olmalıdır."
            )

            return

        description = (
            self.description_input
            .text()
            .strip()
        )

        conn = None

        try:

            conn = get_connection()

            # -------------------------------------------------
            # ÜRÜNÜ KİLİTLEME YERİNE GÜNCEL STOKU OKU
            # -------------------------------------------------

            product = conn.execute(
                """
                SELECT
                    product_name,
                    stock_quantity,
                    unit
                FROM products
                WHERE id = ?
                  AND is_active = 1
                """,
                (product_id,)
            ).fetchone()

            if not product:

                QMessageBox.warning(
                    self,
                    "Ürün Bulunamadı",
                    "Seçilen ürün bulunamadı."
                )

                return

            product_name = (
                product["product_name"]
            )

            previous_stock = float(
                product["stock_quantity"] or 0
            )

            unit = (
                product["unit"]
                or "adet"
            )

            # -------------------------------------------------
            # YENİ STOK
            # -------------------------------------------------

            if movement_type == "in":

                new_stock = (
                    previous_stock
                    + quantity
                )

                transaction_name = "Stok Girişi"

            else:

                if quantity > previous_stock:

                    QMessageBox.warning(
                        self,
                        "Yetersiz Stok",
                        (
                            f"{product_name} için yeterli "
                            f"stok bulunmuyor.\n\n"
                            f"Mevcut stok: "
                            f"{previous_stock:g} {unit}\n"
                            f"Çıkış miktarı: "
                            f"{quantity:g} {unit}"
                        )
                    )

                    return

                new_stock = (
                    previous_stock
                    - quantity
                )

                transaction_name = "Stok Çıkışı"

            # -------------------------------------------------
            # ÜRÜN STOĞUNU GÜNCELLE
            # -------------------------------------------------

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
                    product_id
                )
            )

            # -------------------------------------------------
            # HAREKET KAYDI
            # -------------------------------------------------

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
                    description
                )
            )

            conn.commit()

            # -------------------------------------------------
            # FORMU TEMİZLE
            # -------------------------------------------------

            self.quantity_input.setValue(
                0
            )

            self.description_input.clear()

            self.load_products()

            self.load_movements()

            QMessageBox.information(
                self,
                "Başarılı",
                (
                    f"{transaction_name} başarıyla yapıldı.\n\n"
                    f"Ürün: {product_name}\n"
                    f"Miktar: {quantity:g} {unit}\n"
                    f"Yeni stok: {new_stock:g} {unit}"
                )
            )

        except Exception as e:

            if conn:
                conn.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"Stok hareketi kaydedilemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # =========================================================
    # HAREKETLERİ GETİR
    # =========================================================

    def load_movements(self):

        conn = None

        try:

            conn = get_connection()

            rows = conn.execute(
                """
                SELECT
                    sm.id,
                    p.product_name,
                    sm.transaction_type,
                    sm.quantity,
                    sm.previous_stock,
                    sm.new_stock,
                    sm.description,
                    sm.created_at
                FROM stock_movements sm
                INNER JOIN products p
                    ON p.id = sm.product_id
                ORDER BY
                    sm.id DESC
                """
            ).fetchall()

            self.table.setRowCount(
                0
            )

            for row_index, row in enumerate(rows):

                self.table.insertRow(
                    row_index
                )

                movement_type = (
                    row["transaction_type"]
                )

                if movement_type == "in":

                    movement_text = "📥 Giriş"

                elif movement_type == "out":

                    movement_text = "📤 Çıkış"

                else:

                    movement_text = movement_type

                values = [
                    str(row["id"]),
                    row["product_name"] or "",
                    movement_text,
                    f"{float(row['quantity'] or 0):g}",
                    f"{float(row['previous_stock'] or 0):g}",
                    f"{float(row['new_stock'] or 0):g}",
                    row["description"] or "",
                    row["created_at"] or "",
                ]

                for column_index, value in enumerate(values):

                    item = QTableWidgetItem(
                        str(value)
                    )

                    item.setTextAlignment(
                        Qt.AlignCenter
                    )

                    if column_index in [1, 6, 7]:

                        item.setTextAlignment(
                            Qt.AlignLeft
                            | Qt.AlignVCenter
                        )

                    self.table.setItem(
                        row_index,
                        column_index,
                        item
                    )

            self.info_label.setText(
                f"Hareket sayısı: {len(rows)}"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Stok hareketleri yüklenemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # =========================================================
    # YENİLE
    # =========================================================

    def refresh_all(self):

        self.load_products()

        self.load_movements()