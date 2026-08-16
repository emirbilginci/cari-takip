from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QLabel,
)

from app.database.connection import get_connection


class TahsilatDialog(QDialog):

    def __init__(
        self,
        customer_id=None,
        customer_name=None,
        parent=None
    ):

        super().__init__(parent)

        self.customer_id = customer_id
        self.customer_name = customer_name
        self.current_balance = 0.0

        self.setWindowTitle("Tahsilat Al")
        self.setMinimumWidth(420)

        # ==================================================
        # ANA LAYOUT
        # ==================================================

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # ==================================================
        # CARİ
        # ==================================================

        self.customer_combo = QComboBox()

        form.addRow(
            "Cari:",
            self.customer_combo
        )

        # ==================================================
        # MEVCUT ALACAK
        # ==================================================

        self.balance_label = QLineEdit()

        self.balance_label.setReadOnly(True)
        self.balance_label.setText(
            "0,00 TL"
        )

        form.addRow(
            "Mevcut Alacak:",
            self.balance_label
        )

        # ==================================================
        # TAHSİLAT TUTARI
        # ==================================================

        self.amount_input = QDoubleSpinBox()

        self.amount_input.setRange(
            0.00,
            999999999.99
        )

        self.amount_input.setDecimals(2)

        self.amount_input.setSingleStep(
            10.00
        )

        self.amount_input.setSuffix(
            " TL"
        )

        self.amount_input.setValue(
            0.00
        )

        form.addRow(
            "Tahsilat Tutarı:",
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
            "Tahsilat"
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
            "Tahsilatı Kaydet"
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
        # CARİ DEĞİŞİNCE
        # ==================================================

        self.customer_combo.currentIndexChanged.connect(
            self.on_customer_changed
        )

        # ==================================================
        # CARİLERİ YÜKLE
        # ==================================================

        self.load_customers()

    # ======================================================
    # CARİLERİ YÜKLE
    # ======================================================

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
                ORDER BY name
                """
            ).fetchall()

            self.customer_combo.blockSignals(
                True
            )

            self.customer_combo.clear()

            selected_index = -1

            for row in rows:

                self.customer_combo.addItem(
                    row["name"],
                    row["id"]
                )

                # Cari detayından geldiysek
                # o cariyi otomatik seç
                if (
                    self.customer_id is not None
                    and row["id"] == self.customer_id
                ):

                    selected_index = (
                        self.customer_combo.count() - 1
                    )

            # ==================================================
            # OTOMATİK CARİ SEÇ
            # ==================================================

            if selected_index >= 0:

                self.customer_combo.setCurrentIndex(
                    selected_index
                )

            self.customer_combo.blockSignals(
                False
            )

            # Cari seçiliyse bakiyeyi yükle
            self.on_customer_changed()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Cariler yüklenemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # ======================================================
    # CARİ DEĞİŞİNCE
    # ======================================================

    def on_customer_changed(self):

        customer_id = (
            self.customer_combo.currentData()
        )

        if customer_id is None:

            self.customer_id = None
            self.current_balance = 0.0

            self.balance_label.setText(
                "0,00 TL"
            )

            self.amount_input.setMaximum(
                0.00
            )

            self.amount_input.setValue(
                0.00
            )

            return

        self.customer_id = int(
            customer_id
        )

        self.customer_name = (
            self.customer_combo.currentText()
        )

        self.load_balance()

    # ======================================================
    # BAKİYE HESAPLA
    # ======================================================

    def load_balance(self):

        conn = None

        try:

            conn = get_connection()

            # ==================================================
            # ALACAK HESABI
            #
            # Yeni sistem:
            # sale + credit
            #
            # Eski sistem:
            # sale_on_credit
            #
            # Tahsilatlar:
            # payment_received
            # ==================================================

            result = conn.execute(
                """
                SELECT

                    COALESCE(
                        SUM(
                            CASE
                                WHEN transaction_type = 'sale_on_credit'
                                THEN amount

                                WHEN transaction_type = 'sale'
                                     AND payment_method = 'credit'
                                THEN amount

                                ELSE 0
                            END
                        ),
                        0
                    ) AS credit_sales,

                    COALESCE(
                        SUM(
                            CASE
                                WHEN transaction_type = 'payment_received'
                                THEN amount

                                ELSE 0
                            END
                        ),
                        0
                    ) AS collections

                FROM transactions

                WHERE customer_id = ?
                  AND is_cancelled = 0
                """,
                (self.customer_id,)
            ).fetchone()

            credit_sales = float(
                result["credit_sales"] or 0
            )

            collections = float(
                result["collections"] or 0
            )

            balance = (
                credit_sales
                - collections
            )

            if balance < 0:

                balance = 0.0

            self.current_balance = round(
                balance,
                2
            )

            # ==================================================
            # EKRANA YAZ
            # ==================================================

            self.balance_label.setText(
                f"{self.current_balance:,.2f} TL"
            )

            # ==================================================
            # TAHSİLAT MAKSİMUMU
            # ==================================================

            if self.current_balance > 0:

                self.amount_input.setMaximum(
                    self.current_balance
                )

                # Varsayılan 100 TL
                # fakat alacak 100'den küçükse
                # alacağın tamamını göster.

                self.amount_input.setValue(
                    min(
                        self.current_balance,
                        100.00
                    )
                )

            else:

                self.amount_input.setMaximum(
                    0.00
                )

                self.amount_input.setValue(
                    0.00
                )

        except Exception as e:

            self.current_balance = 0.0

            self.balance_label.setText(
                "0,00 TL"
            )

            self.amount_input.setMaximum(
                0.00
            )

            self.amount_input.setValue(
                0.00
            )

            print(
                "Tahsilat bakiye hatası:",
                e
            )

        finally:

            if conn:
                conn.close()

    # ======================================================
    # TAHSİLATI KAYDET
    # ======================================================

    def save_payment(self):

        # ==================================================
        # CARİ KONTROLÜ
        # ==================================================

        if self.customer_id is None:

            QMessageBox.warning(
                self,
                "Cari Seçilmedi",
                "Lütfen bir cari seçin."
            )

            return

        amount = float(
            self.amount_input.value()
        )

        payment_method = (
            self.payment_method.currentText()
        )

        description = (
            self.description_input.text().strip()
        )

        # ==================================================
        # TUTAR KONTROLÜ
        # ==================================================

        if amount <= 0:

            QMessageBox.warning(
                self,
                "Geçersiz Tutar",
                "Tahsilat tutarı 0'dan büyük olmalıdır."
            )

            return

        # ==================================================
        # GÜNCEL BAKİYEYİ TEKRAR KONTROL ET
        # ==================================================

        self.load_balance()

        if self.current_balance <= 0:

            QMessageBox.warning(
                self,
                "Alacak Yok",
                "Bu carinin tahsil edilecek alacağı bulunmuyor."
            )

            return

        if amount > self.current_balance + 0.001:

            QMessageBox.warning(
                self,
                "Geçersiz Tutar",
                (
                    f"Mevcut alacak: "
                    f"{self.current_balance:,.2f} TL\n\n"
                    "Tahsilat tutarı mevcut alacaktan "
                    "fazla olamaz."
                )
            )

            return

        if not description:

            description = "Tahsilat"

        conn = None

        try:

            conn = get_connection()

            # ==================================================
            # CARİ HAREKETİ
            # ==================================================

            cursor = conn.execute(
                """
                INSERT INTO transactions (
                    customer_id,
                    transaction_type,
                    payment_method,
                    description,
                    amount,
                    is_cancelled
                )
                VALUES (?, ?, ?, ?, ?, 0)
                """,
                (
                    self.customer_id,
                    "payment_received",
                    payment_method,
                    description,
                    amount,
                )
            )

            transaction_id = cursor.lastrowid

            # ==================================================
            # KASA HAREKETİ
            # ==================================================

            conn.execute(
                """
                INSERT INTO cash_transactions (
                    transaction_id,
                    customer_id,
                    transaction_date,
                    transaction_type,
                    amount,
                    description
                )
                VALUES (
                    ?,
                    ?,
                    datetime('now'),
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    transaction_id,
                    self.customer_id,
                    "collection",
                    amount,
                    f"{self.customer_name} - {description}",
                )
            )

            conn.commit()

            QMessageBox.information(
                self,
                "Başarılı",
                (
                    f"{amount:,.2f} TL tahsilat "
                    "başarıyla kaydedildi."
                )
            )

            self.accept()

        except Exception as e:

            if conn:

                conn.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"Tahsilat kaydedilemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()


# ==========================================================
# BASİT LABEL YARDIMCISI
# ==========================================================

def QLabelText(text):

    return QLabel(text)