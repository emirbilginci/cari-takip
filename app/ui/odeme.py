from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

from app.database.connection import get_connection


class OdemeDialog(QDialog):

    def __init__(self, customer_id=None, customer_name=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Ödeme Yap")
        self.setMinimumWidth(420)

        self.customer_id = customer_id
        self.customer_name = customer_name

        self.current_balance = 0.0

        # ==================================================
        # ANA LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # ==================================================
        # TEDARİKÇİ
        # ==================================================

        self.supplier_combo = QComboBox()

        form.addRow(
            "Tedarikçi:",
            self.supplier_combo
        )

        # ==================================================
        # MEVCUT BORÇ
        # ==================================================

        self.balance_label = QLineEdit()
        self.balance_label.setReadOnly(True)
        self.balance_label.setText("0,00 TL")

        form.addRow(
            "Mevcut Borç:",
            self.balance_label
        )

        # ==================================================
        # ÖDEME TUTARI
        # ==================================================

        self.amount_input = QDoubleSpinBox()

        self.amount_input.setRange(
            0.00,
            999999999.99
        )

        self.amount_input.setDecimals(2)
        self.amount_input.setSingleStep(10.00)
        self.amount_input.setSuffix(" TL")
        self.amount_input.setValue(0.00)

        self.amount_input.valueChanged.connect(
            self.on_amount_changed
        )

        form.addRow(
            "Ödeme Tutarı:",
            self.amount_input
        )

        # ==================================================
        # ÖDEME YÖNTEMİ
        # ==================================================

        self.payment_method = QComboBox()

        self.payment_method.addItems([
            "Nakit",
            "Banka Havalesi",
            "Kredi Kartı",
            "Çek",
            "Diğer",
        ])

        form.addRow(
            "Ödeme Yöntemi:",
            self.payment_method
        )

        # ==================================================
        # AÇIKLAMA
        # ==================================================

        self.description_input = QLineEdit()

        self.description_input.setText(
            "Tedarikçi ödemesi"
        )

        form.addRow(
            "Açıklama:",
            self.description_input
        )

        layout.addLayout(form)

        # ==================================================
        # BUTONLAR
        # ==================================================

        self.save_button = QPushButton(
            "Ödemeyi Kaydet"
        )

        self.cancel_button = QPushButton(
            "İptal"
        )

        self.save_button.clicked.connect(
            self.save_payment
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        layout.addWidget(
            self.save_button
        )

        layout.addWidget(
            self.cancel_button
        )

        # ==================================================
        # TEDARİKÇİ DEĞİŞİNCE
        # ==================================================

        self.supplier_combo.currentIndexChanged.connect(
            self.on_supplier_changed
        )

        # ==================================================
        # TEDARİKÇİLERİ YÜKLE
        # ==================================================

        self.load_suppliers()

    # ======================================================
    # TEDARİKÇİLERİ YÜKLE
    # ======================================================

    def load_suppliers(self):

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
                  AND (
                        type = 'supplier'
                        OR type = 'both'
                  )
                ORDER BY name
                """
            ).fetchall()

            self.supplier_combo.blockSignals(True)

            self.supplier_combo.clear()

            selected_index = -1

            for row in rows:

                self.supplier_combo.addItem(
                    row["name"],
                    row["id"]
                )

                # Cari Detayı'ndan geldiysek
                # o cariyi otomatik seç
                if (
                    self.customer_id is not None
                    and row["id"] == self.customer_id
                ):
                    selected_index = (
                        self.supplier_combo.count() - 1
                    )

            # ==================================================
            # OTOMATİK CARİ SEÇ
            # ==================================================

            if selected_index >= 0:

                self.supplier_combo.setCurrentIndex(
                    selected_index
                )

            self.supplier_combo.blockSignals(False)

            # Bakiye yükle
            self.on_supplier_changed()

            # ==================================================
            # HİÇ TEDARİKÇİ YOKSA
            # ==================================================

            if self.supplier_combo.count() == 0:

                self.balance_label.setText(
                    "0,00 TL"
                )

                self.amount_input.setRange(
                    0.00,
                    0.00
                )

                self.amount_input.setValue(
                    0.00
                )

                self.amount_input.setEnabled(
                    False
                )

                self.save_button.setEnabled(
                    False
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Tedarikçiler yüklenemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # ======================================================
    # TEDARİKÇİ DEĞİŞİNCE
    # ======================================================

    def on_supplier_changed(self):

        supplier_id = (
            self.supplier_combo.currentData()
        )

        if supplier_id is None:

            self.current_balance = 0.0

            self.balance_label.setText(
                "0,00 TL"
            )

            self.amount_input.setRange(
                0.00,
                0.00
            )

            self.amount_input.setValue(
                0.00
            )

            self.amount_input.setEnabled(
                False
            )

            self.save_button.setEnabled(
                False
            )

            return

        conn = None

        try:

            conn = get_connection()

            # ==================================================
            # SADECE BİZİM TEDARİKÇİYE OLAN BORCUMUZ
            #
            # purchase_on_credit = bize mal sattı
            # payment_made     = bizim yaptığımız ödeme
            #
            # Ödeme NEGATİF tutuluyor.
            #
            # Örnek:
            #
            # Alış       +140
            # Ödeme      -100
            # ----------------
            # Borç        40
            # ==================================================

            row = conn.execute(
                """
                SELECT
                    COALESCE(
                        SUM(
                            CASE
                                WHEN transaction_type =
                                     'purchase_on_credit'
                                THEN amount

                                WHEN transaction_type =
                                     'purchase'
                                     AND payment_method = 'credit'
                                THEN amount

                                ELSE 0
                            END
                        ),
                        0
                    ) AS purchases,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN transaction_type =
                                     'payment_made'
                                THEN amount
                                ELSE 0
                            END
                        ),
                        0
                    ) AS payments

                FROM transactions

                WHERE customer_id = ?
                  AND is_cancelled = 0
                """,
                (supplier_id,)
            ).fetchone()

            purchases = float(
                row["purchases"] or 0
            )

            payments = float(
                row["payments"] or 0
            )

            balance = purchases + payments

            # Küçük floating point hatalarını temizle
            if abs(balance) < 0.01:
                balance = 0.0

            balance = round(
                balance,
                2
            )

            # Borç negatif olamaz
            if balance < 0:
                balance = 0.0

            self.current_balance = balance

            self.balance_label.setText(
                f"{balance:,.2f} TL"
            )

            # ==================================================
            # ÖDEME ALANI
            # ==================================================

            if balance > 0:

                self.amount_input.setEnabled(
                    True
                )

                self.amount_input.setRange(
                    0.01,
                    balance
                )

                default_amount = min(
                    balance,
                    100.00
                )

                self.amount_input.setValue(
                    round(
                        default_amount,
                        2
                    )
                )

                self.save_button.setEnabled(
                    True
                )

            else:

                self.amount_input.setRange(
                    0.00,
                    0.00
                )

                self.amount_input.setValue(
                    0.00
                )

                self.amount_input.setEnabled(
                    False
                )

                self.save_button.setEnabled(
                    False
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Bakiye hesaplanamadı.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # ======================================================
    # ÖDEME TUTARI DEĞİŞİNCE
    # ======================================================

    def on_amount_changed(self, value):

        if value < 0:

            self.amount_input.setValue(
                0.00
            )

            return

        if (
            self.current_balance > 0
            and value > self.current_balance
        ):

            self.amount_input.setValue(
                self.current_balance
            )

    # ======================================================
    # ÖDEMEYİ KAYDET
    # ======================================================

    def save_payment(self):

        supplier_id = (
            self.supplier_combo.currentData()
        )

        amount = round(
            self.amount_input.value(),
            2
        )

        payment_method = (
            self.payment_method.currentText()
        )

        description = (
            self.description_input.text().strip()
        )

        # ==================================================
        # KONTROLLER
        # ==================================================

        if supplier_id is None:

            QMessageBox.warning(
                self,
                "Uyarı",
                "Lütfen tedarikçi seçin."
            )

            return

        if amount <= 0:

            QMessageBox.warning(
                self,
                "Uyarı",
                "Ödeme tutarı 0'dan büyük olmalıdır."
            )

            return

        if self.current_balance <= 0:

            QMessageBox.warning(
                self,
                "Uyarı",
                "Bu tedarikçiye ödenecek borç bulunmuyor."
            )

            return

        if amount > self.current_balance + 0.001:

            QMessageBox.warning(
                self,
                "Uyarı",
                "Ödeme tutarı mevcut borçtan fazla olamaz."
            )

            return

        if not description:

            description = "Tedarikçi ödemesi"

        conn = None

        try:

            conn = get_connection()

            # ==================================================
            # 1. CARİ İŞLEMİ
            #
            # Ödeme NEGATİF kaydedilir.
            # ==================================================

            payment_amount = -abs(amount)

            cursor = conn.execute(
                """
                INSERT INTO transactions (
                    customer_id,
                    transaction_type,
                    description,
                    amount,
                    payment_method
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    supplier_id,
                    "payment_made",
                    description,
                    payment_amount,
                    payment_method,
                )
            )

            transaction_id = cursor.lastrowid

            # ==================================================
            # 2. KASA HAREKETİ
            #
            # cash_transactions.amount pozitif tutuluyor.
            # transaction_type = payment olduğu için bu para çıkışıdır.
            # ==================================================

            supplier_name = (
                self.supplier_combo.currentText()
            )

            conn.execute(
                """
                INSERT INTO cash_transactions (
                    transaction_id,
                    customer_id,
                    transaction_type,
                    amount,
                    description
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    transaction_id,
                    supplier_id,
                    "payment",
                    amount,
                    f"{supplier_name} - {description}",
                )
            )

            conn.commit()

            # ==================================================
            # BAŞARILI
            # ==================================================

            QMessageBox.information(
                self,
                "Başarılı",
                f"{amount:,.2f} TL ödeme kaydedildi.\n\n"
                f"Tedarikçi: {supplier_name}\n"
                f"Ödeme yöntemi: {payment_method}"
            )

            self.accept()

        except Exception as e:

            if conn:
                conn.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"Ödeme kaydedilemedi.\n\n"
                f"Hata:\n{e}"
            )

        finally:

            if conn:
                conn.close()