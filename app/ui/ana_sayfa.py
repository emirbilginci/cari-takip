from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QGridLayout,
)
from PySide6.QtCore import Qt

from app.database.connection import get_connection


class AnaSayfaWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.load_data()

    # =========================================================
    # ARAYÜZ
    # =========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(30, 30, 30, 30)

        # Başlık
        title = QLabel("Cari Takip Panosu")

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        layout.addSpacing(20)

        # Kartlar grid
        cards_layout = QGridLayout()

        cards_layout.setSpacing(15)

        # Toplam Cari
        self.total_customers_card = self.create_card(
            "Toplam Cari",
            "0"
        )

        cards_layout.addWidget(
            self.total_customers_card,
            0,
            0
        )

        # Toplam Ürün
        self.total_products_card = self.create_card(
            "Toplam Ürün",
            "0"
        )

        cards_layout.addWidget(
            self.total_products_card,
            0,
            1
        )

        # Toplam Alacak
        self.total_receivable_card = self.create_card(
            "Toplam Alacak",
            "0,00 TL"
        )

        cards_layout.addWidget(
            self.total_receivable_card,
            0,
            2
        )

        # Toplam Borç
        self.total_payable_card = self.create_card(
            "Toplam Borç",
            "0,00 TL"
        )

        cards_layout.addWidget(
            self.total_payable_card,
            1,
            0
        )

        # Kasa Bakiyesi
        self.cash_balance_card = self.create_card(
            "Kasa Bakiyesi",
            "0,00 TL"
        )

        cards_layout.addWidget(
            self.cash_balance_card,
            1,
            1
        )

        layout.addLayout(cards_layout)

        layout.addSpacing(30)

        # Alt bilgi
        info_label = QLabel(
            "Pano her 10 saniyede bir otomatik yenilenir. "
            "Manuel yenileme için sayfayı tıklayabilirsiniz."
        )

        info_label.setStyleSheet("""
            font-size: 12px;
            color: gray;
        """)

        layout.addWidget(info_label)

        layout.addStretch()

    # =========================================================
    # KART OLUŞTUR
    # =========================================================

    def create_card(self, title, value):

        card = QWidget()

        card.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 8px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(card)

        # Başlık
        title_label = QLabel(title)

        title_label.setStyleSheet("""
            font-size: 14px;
            color: gray;
        """)

        layout.addWidget(title_label)

        # Değer
        value_label = QLabel(value)

        value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #333;
        """)

        layout.addWidget(value_label)

        card.value_label = value_label

        return card

    # =========================================================
    # VERİLERİ YÜKLE
    # =========================================================

    def load_data(self):

        try:

            conn = get_connection()

            # Toplam Cari
            customers_result = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM customers
                WHERE is_active = 1
                """
            ).fetchone()

            total_customers = customers_result["count"]

            # Toplam Ürün
            products_result = conn.execute(
                """
                SELECT COUNT(*) AS count
                FROM products
                WHERE is_active = 1
                """
            ).fetchone()

            total_products = products_result["count"]

            # Toplam Alacak (müşteri bakiyesi)
            receivable_result = conn.execute(
                """
                SELECT
                    customer_id,
                    COALESCE(SUM(CASE WHEN transaction_type = 'sale_on_credit' THEN amount ELSE 0 END), 0) AS sales,
                    COALESCE(SUM(CASE WHEN transaction_type = 'payment_received' THEN amount ELSE 0 END), 0) AS payments
                FROM transactions
                WHERE is_cancelled = 0
                GROUP BY customer_id
                """
            ).fetchall()

            total_receivable = 0

            for row in receivable_result:

                customer_id = row["customer_id"]

                # Müşteri türünü kontrol et
                customer = conn.execute(
                    """
                    SELECT type
                    FROM customers
                    WHERE id = ?
                    """,
                    (customer_id,)
                ).fetchone()

                if customer and customer["type"] in ["customer", "both"]:

                    sales = float(row["sales"] or 0)
                    payments = float(row["payments"] or 0)

                    balance = sales - payments

                    if balance > 0:
                        total_receivable += balance

            # Toplam Borç (tedarikçi bakiyesi)
            total_payable = 0

            for row in receivable_result:

                customer_id = row["customer_id"]

                customer = conn.execute(
                    """
                    SELECT type
                    FROM customers
                    WHERE id = ?
                    """,
                    (customer_id,)
                ).fetchone()

                if customer and customer["type"] in ["supplier", "both"]:

                    # Alış işlemleri
                    purchase_result = conn.execute(
                        """
                        SELECT COALESCE(SUM(amount), 0) AS total
                        FROM transactions
                        WHERE customer_id = ?
                          AND transaction_type = 'purchase_on_credit'
                          AND is_cancelled = 0
                        """,
                        (customer_id,)
                    ).fetchone()

                    purchase = float(purchase_result["total"] or 0)

                    # Ödeme işlemleri
                    payment_result = conn.execute(
                        """
                        SELECT COALESCE(SUM(amount), 0) AS total
                        FROM transactions
                        WHERE customer_id = ?
                          AND transaction_type = 'payment_made'
                          AND is_cancelled = 0
                        """,
                        (customer_id,)
                    ).fetchone()

                    payment = float(payment_result["total"] or 0)

                    balance = purchase - payment

                    if balance > 0:
                        total_payable += balance

            # Kasa Bakiyesi
            cash_result = conn.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
                FROM cash_transactions
                """
            ).fetchone()

            income = float(cash_result["income"] or 0)
            expense = float(cash_result["expense"] or 0)

            cash_balance = income - expense

            conn.close()

            # Kartları güncelle
            self.total_customers_card.value_label.setText(
                str(total_customers)
            )

            self.total_products_card.value_label.setText(
                str(total_products)
            )

            self.total_receivable_card.value_label.setText(
                f"{total_receivable:,.2f} TL"
            )

            self.total_payable_card.value_label.setText(
                f"{total_payable:,.2f} TL"
            )

            self.cash_balance_card.value_label.setText(
                f"{cash_balance:,.2f} TL"
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Veriler yüklenemedi.\n\n{e}"
            )
