from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QComboBox,
    QMessageBox,
    QDialogButtonBox,
)

from app.database.connection import get_connection


class UrunFormDialog(QDialog):

    def __init__(self, product_id=None, parent=None):
        super().__init__(parent)

        self.product_id = product_id

        self.setWindowTitle(
            "Ürün Düzenle" if product_id else "Yeni Ürün"
        )

        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # ==================================================
        # ÜRÜN ADI
        # ==================================================

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(
            "Örn: Çimento 25 KG"
        )

        form.addRow(
            "Ürün Adı:",
            self.name_input
        )

        # ==================================================
        # BARKOD
        # ==================================================

        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText(
            "Örn: 869000000001"
        )

        form.addRow(
            "Barkod:",
            self.barcode_input
        )

        # ==================================================
        # BİRİM
        # ==================================================

        self.unit_combo = QComboBox()

        self.unit_combo.addItems([
            "adet",
            "kg",
            "gram",
            "litre",
            "metre",
            "m2",
            "m3",
        ])

        form.addRow(
            "Birim:",
            self.unit_combo
        )

        # ==================================================
        # ALIŞ FİYATI
        # ==================================================

        self.purchase_price_input = QDoubleSpinBox()

        self.purchase_price_input.setRange(
            0,
            999999999
        )

        self.purchase_price_input.setDecimals(2)
        self.purchase_price_input.setSuffix(" TL")

        form.addRow(
            "Alış Fiyatı:",
            self.purchase_price_input
        )

        # ==================================================
        # SATIŞ FİYATI
        # ==================================================

        self.sale_price_input = QDoubleSpinBox()

        self.sale_price_input.setRange(
            0,
            999999999
        )

        self.sale_price_input.setDecimals(2)
        self.sale_price_input.setSuffix(" TL")

        form.addRow(
            "Satış Fiyatı:",
            self.sale_price_input
        )

        # ==================================================
        # MÜŞTERİ FİYATI
        # ==================================================

        self.customer_price_input = QDoubleSpinBox()

        self.customer_price_input.setRange(
            0,
            999999999
        )

        self.customer_price_input.setDecimals(2)
        self.customer_price_input.setSuffix(" TL")

        form.addRow(
            "Müşteri Fiyatı:",
            self.customer_price_input
        )

        # ==================================================
        # STOK
        # ==================================================

        self.stock_input = QDoubleSpinBox()

        self.stock_input.setRange(
            0,
            999999999
        )

        self.stock_input.setDecimals(3)

        form.addRow(
            "Mevcut Stok:",
            self.stock_input
        )

        # ==================================================
        # KRİTİK STOK
        # ==================================================

        self.critical_stock_input = QDoubleSpinBox()

        self.critical_stock_input.setRange(
            0,
            999999999
        )

        self.critical_stock_input.setDecimals(3)
        self.critical_stock_input.setValue(5)

        form.addRow(
            "Kritik Stok:",
            self.critical_stock_input
        )

        # ==================================================
        # AÇIKLAMA
        # ==================================================

        self.description_input = QLineEdit()

        self.description_input.setPlaceholderText(
            "İsteğe bağlı"
        )

        form.addRow(
            "Açıklama:",
            self.description_input
        )

        layout.addLayout(form)

        # ==================================================
        # BUTONLAR
        # ==================================================

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save
            | QDialogButtonBox.Cancel
        )

        buttons.accepted.connect(
            self.save_product
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(buttons)

        # ==================================================
        # DÜZENLEME
        # ==================================================

        if self.product_id:
            self.load_product()

    # ======================================================
    # ÜRÜNÜ YÜKLE
    # ======================================================

    def load_product(self):

        conn = None

        try:

            conn = get_connection()

            product = conn.execute(
                """
                SELECT
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
                WHERE id = ?
                """,
                (self.product_id,)
            ).fetchone()

            if not product:

                QMessageBox.warning(
                    self,
                    "Hata",
                    "Ürün bulunamadı."
                )

                self.reject()
                return

            self.name_input.setText(
                product["product_name"] or ""
            )

            self.barcode_input.setText(
                product["barcode"] or ""
            )

            self.unit_combo.setCurrentText(
                product["unit"] or "adet"
            )

            self.purchase_price_input.setValue(
                float(
                    product["purchase_price"] or 0
                )
            )

            self.sale_price_input.setValue(
                float(
                    product["sale_price"] or 0
                )
            )

            self.customer_price_input.setValue(
                float(
                    product["customer_price"] or 0
                )
            )

            self.stock_input.setValue(
                float(
                    product["stock_quantity"] or 0
                )
            )

            self.critical_stock_input.setValue(
                float(
                    product["critical_stock"] or 5
                )
            )

            self.description_input.setText(
                product["description"] or ""
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Ürün yüklenemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # ======================================================
    # KAYDET
    # ======================================================

    def save_product(self):

        name = self.name_input.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "Eksik Bilgi",
                "Ürün adı gereklidir."
            )

            self.name_input.setFocus()

            return

        barcode = (
            self.barcode_input
            .text()
            .strip()
        )

        unit = (
            self.unit_combo
            .currentText()
        )

        purchase_price = (
            self.purchase_price_input
            .value()
        )

        sale_price = (
            self.sale_price_input
            .value()
        )

        customer_price = (
            self.customer_price_input
            .value()
        )

        stock = (
            self.stock_input
            .value()
        )

        critical_stock = (
            self.critical_stock_input
            .value()
        )

        description = (
            self.description_input
            .text()
            .strip()
        )

        conn = None

        try:

            conn = get_connection()

            # ==================================================
            # BARKOD KONTROLÜ
            # ==================================================

            if barcode:

                existing = conn.execute(
                    """
                    SELECT id
                    FROM products
                    WHERE barcode = ?
                      AND id != ?
                      AND is_active = 1
                    """,
                    (
                        barcode,
                        self.product_id or 0,
                    )
                ).fetchone()

                if existing:

                    QMessageBox.warning(
                        self,
                        "Barkod Kullanılıyor",
                        "Bu barkod başka bir üründe "
                        "zaten kayıtlı."
                    )

                    return

            # ==================================================
            # GÜNCELLE
            # ==================================================

            if self.product_id:

                conn.execute(
                    """
                    UPDATE products
                    SET
                        product_name = ?,
                        barcode = ?,
                        unit = ?,
                        purchase_price = ?,
                        sale_price = ?,
                        customer_price = ?,
                        stock_quantity = ?,
                        critical_stock = ?,
                        description = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        name,
                        barcode,
                        unit,
                        purchase_price,
                        sale_price,
                        customer_price,
                        stock,
                        critical_stock,
                        description,
                        self.product_id,
                    )
                )

            # ==================================================
            # YENİ ÜRÜN
            # ==================================================

            else:

                conn.execute(
                    """
                    INSERT INTO products (
                        product_name,
                        barcode,
                        unit,
                        purchase_price,
                        sale_price,
                        customer_price,
                        stock_quantity,
                        critical_stock,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        barcode,
                        unit,
                        purchase_price,
                        sale_price,
                        customer_price,
                        stock,
                        critical_stock,
                        description,
                    )
                )

            conn.commit()

            QMessageBox.information(
                self,
                "Başarılı",
                "Ürün başarıyla kaydedildi."
            )

            self.accept()

        except Exception as e:

            if conn:
                conn.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"Ürün kaydedilemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()