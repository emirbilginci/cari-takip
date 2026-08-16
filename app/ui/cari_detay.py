from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)

from app.database.connection import get_connection
from app.ui.yeni_islem import YeniIslemDialog
from app.ui.tahsilat import TahsilatDialog
from app.ui.odeme import OdemeDialog


class CariDetayDialog(QDialog):

    def __init__(self, customer_id, parent=None):
        super().__init__(parent)

        self.customer_id = customer_id

        self.setWindowTitle("Cari Detayı")
        self.resize(1200, 850)

        self.setup_ui()
        self.load_customer()

    # =====================================================
    # ARAYÜZ
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            30,
            25,
            30,
            25
        )

        main_layout.setSpacing(12)

        # =================================================
        # CARİ BİLGİLERİ
        # =================================================

        self.name_label = QLabel("Cari")

        self.name_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        main_layout.addWidget(
            self.name_label
        )

        self.info_label = QLabel("")

        self.info_label.setStyleSheet("""
            font-size: 14px;
        """)

        main_layout.addWidget(
            self.info_label
        )

        # =================================================
        # ÖZET ALANI
        # =================================================

        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(25)

        # -------------------------------------------------
        # TOPLAM SATIŞ
        # -------------------------------------------------

        sales_box = QVBoxLayout()

        sales_title = QLabel(
            "Toplam Satış"
        )

        self.sales_label = QLabel(
            "0,00 TL"
        )

        self.sales_label.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
        """)

        sales_box.addWidget(
            sales_title
        )

        sales_box.addWidget(
            self.sales_label
        )

        # -------------------------------------------------
        # TOPLAM TAHSİLAT
        # -------------------------------------------------

        collection_box = QVBoxLayout()

        collection_title = QLabel(
            "Toplam Tahsilat"
        )

        self.collection_label = QLabel(
            "0,00 TL"
        )

        self.collection_label.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
        """)

        collection_box.addWidget(
            collection_title
        )

        collection_box.addWidget(
            self.collection_label
        )

        # -------------------------------------------------
        # ALACAĞIMIZ
        # -------------------------------------------------

        receivable_box = QVBoxLayout()

        receivable_title = QLabel(
            "Alacağımız"
        )

        self.receivable_label = QLabel(
            "0,00 TL"
        )

        self.receivable_label.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
        """)

        receivable_box.addWidget(
            receivable_title
        )

        receivable_box.addWidget(
            self.receivable_label
        )

        # -------------------------------------------------
        # BORCUMUZ
        # -------------------------------------------------

        payable_box = QVBoxLayout()

        payable_title = QLabel(
            "Borcumuz"
        )

        self.payable_label = QLabel(
            "0,00 TL"
        )

        self.payable_label.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
        """)

        payable_box.addWidget(
            payable_title
        )

        payable_box.addWidget(
            self.payable_label
        )

        # -------------------------------------------------
        # NET BAKİYE
        # -------------------------------------------------

        balance_box = QVBoxLayout()

        balance_title = QLabel(
            "Net Bakiye"
        )

        self.net_balance_label = QLabel(
            "0,00 TL"
        )

        self.net_balance_label.setStyleSheet("""
            font-size: 21px;
            font-weight: bold;
        """)

        balance_box.addWidget(
            balance_title
        )

        balance_box.addWidget(
            self.net_balance_label
        )

        # -------------------------------------------------
        # ÖZETİ EKLE
        # -------------------------------------------------

        summary_layout.addLayout(
            sales_box
        )

        summary_layout.addLayout(
            collection_box
        )

        summary_layout.addLayout(
            receivable_box
        )

        summary_layout.addLayout(
            payable_box
        )

        summary_layout.addLayout(
            balance_box
        )

        main_layout.addLayout(
            summary_layout
        )

        # =================================================
        # ÜRÜN HAREKETLERİ
        # =================================================

        products_title = QLabel(
            "Ürün Hareketleri"
        )

        products_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        main_layout.addWidget(
            products_title
        )

        self.products_table = QTableWidget()

        self.products_table.setColumnCount(
            6
        )

        self.products_table.setHorizontalHeaderLabels([
            "İşlem",
            "Ürün",
            "Miktar",
            "Birim",
            "Birim Fiyat",
            "Toplam",
        ])

        self.products_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.Stretch
        )

        for column in [0, 2, 3, 4, 5]:

            self.products_table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeToContents
            )

        self.products_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.products_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.products_table.setAlternatingRowColors(
            True
        )

        self.products_table.setMinimumHeight(
            220
        )

        main_layout.addWidget(
            self.products_table
        )

        # =================================================
        # İŞLEM GEÇMİŞİ
        # =================================================

        history_title = QLabel(
            "İşlem Geçmişi"
        )

        history_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        main_layout.addWidget(
            history_title
        )

        self.history_table = QTableWidget()

        self.history_table.setColumnCount(
            4
        )

        self.history_table.setHorizontalHeaderLabels([
            "Tarih",
            "İşlem",
            "Açıklama",
            "Tutar",
        ])

        self.history_table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.Stretch
        )

        for column in [0, 1, 3]:

            self.history_table.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeToContents
            )

        self.history_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.history_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.history_table.setAlternatingRowColors(
            True
        )

        self.history_table.setMinimumHeight(
            220
        )

        main_layout.addWidget(
            self.history_table
        )

        # =================================================
        # BUTONLAR
        # =================================================

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        # -------------------------------------------------
        # İŞLEM İPTAL
        # -------------------------------------------------

        cancel_transaction_button = QPushButton(
            "İşlemi İptal Et"
        )

        cancel_transaction_button.setMinimumHeight(
            40
        )

        cancel_transaction_button.clicked.connect(
            self.cancel_selected_transaction
        )

        button_layout.addWidget(
            cancel_transaction_button
        )

        # -------------------------------------------------
        # TAHSİLAT AL
        # -------------------------------------------------

        collection_button = QPushButton(
            "Tahsilat Al"
        )

        collection_button.setMinimumHeight(
            40
        )

        collection_button.clicked.connect(
            self.open_collection
        )

        button_layout.addWidget(
            collection_button
        )

        # -------------------------------------------------
        # ÖDEME YAP
        # -------------------------------------------------

        payment_button = QPushButton(
            "Ödeme Yap"
        )

        payment_button.setMinimumHeight(
            40
        )

        payment_button.clicked.connect(
            self.open_payment
        )

        button_layout.addWidget(
            payment_button
        )

        # -------------------------------------------------
        # YENİ İŞLEM
        # -------------------------------------------------

        transaction_button = QPushButton(
            "Yeni İşlem"
        )

        transaction_button.setMinimumHeight(
            40
        )

        transaction_button.clicked.connect(
            self.open_transaction
        )

        button_layout.addWidget(
            transaction_button
        )

        # -------------------------------------------------
        # KAPAT
        # -------------------------------------------------

        close_button = QPushButton(
            "Kapat"
        )

        close_button.setMinimumHeight(
            40
        )

        close_button.clicked.connect(
            self.close
        )

        button_layout.addWidget(
            close_button
        )

        main_layout.addLayout(
            button_layout
        )

    # =====================================================
    # CARİ BİLGİLERİNİ YÜKLE
    # =====================================================

    def load_customer(self):

        connection = None

        try:

            connection = get_connection()

            customer = connection.execute(
                """
                SELECT
                    id,
                    name,
                    phone,
                    address,
                    tax_number
                FROM customers
                WHERE id = ?
                """,
                (self.customer_id,)
            ).fetchone()

            if not customer:

                QMessageBox.warning(
                    self,
                    "Hata",
                    "Cari bulunamadı."
                )

                self.close()

                return

            self.name_label.setText(
                customer["name"]
            )

            phone = (
                customer["phone"]
                or "-"
            )

            address = (
                customer["address"]
                or "-"
            )

            self.info_label.setText(
                f"Telefon: {phone}    |    "
                f"Adres: {address}"
            )

            self.load_summary(
                connection
            )

            self.load_products(
                connection
            )

            self.load_history(
                connection
            )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Cari bilgileri yüklenemedi.\n\n{e}"
            )

        finally:

            if connection:
                connection.close()

    # =====================================================
    # ÖZET HESAPLA
    # =====================================================

    def load_summary(self, connection):

        rows = connection.execute(
            """
            SELECT
                transaction_type,
                payment_method,
                COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE customer_id = ?
              AND is_cancelled = 0
            GROUP BY
                transaction_type,
                payment_method
            """,
            (self.customer_id,)
        ).fetchall()

        total_sales = 0.0
        total_collection = 0.0

        total_purchases = 0.0
        total_supplier_payment = 0.0

        # =================================================
        # HAREKETLERİ TOPLA
        # =================================================

        for row in rows:

            transaction_type = (
                row["transaction_type"]
            )

            total = float(
                row["total"] or 0
            )

            # ---------------------------------------------
            # VERESİYE SATIŞ
            # ---------------------------------------------

            if transaction_type == "sale_on_credit":

                total_sales += total

            # ---------------------------------------------
            # PEŞİN SATIŞ
            #
            # Satış toplamına dahil.
            # Ancak peşin satış müşterinin bize borcunu
            # artırmaz.
            # ---------------------------------------------

            elif transaction_type == "sale":

                total_sales += total

            # ---------------------------------------------
            # TAHSİLAT
            # ---------------------------------------------

            elif transaction_type == "payment_received":

                total_collection += abs(
                    total
                )

            # ---------------------------------------------
            # VERESİYE ALIŞ
            # ---------------------------------------------

            elif transaction_type == "purchase_on_credit":

                total_purchases += total

            # ---------------------------------------------
            # PEŞİN ALIŞ
            #
            # Alış toplamına dahil fakat borç oluşturmaz.
            # ---------------------------------------------

            elif transaction_type == "purchase":

                total_purchases += total

            # ---------------------------------------------
            # TEDARİKÇİYE ÖDEME
            #
            # amount NEGATİF.
            # ---------------------------------------------

            elif transaction_type == "payment_made":

                total_supplier_payment += total

        # =================================================
        # ALACAĞIMIZ
        #
        # SADECE VERESİYE SATIŞLAR
        # EKSİ TAHSİLATLAR
        #
        # Peşin satış zaten tahsil edilmiştir.
        # =================================================

        credit_sales = 0.0

        for row in rows:

            transaction_type = (
                row["transaction_type"]
            )

            # Eski sistem: sale_on_credit
            if transaction_type == "sale_on_credit":

                credit_sales += float(
                    row["total"] or 0
                )

            # Yeni sistem: sale + payment_method=credit
            elif transaction_type == "sale":

                payment_method = (
                    row["payment_method"]
                    or ""
                )

                if payment_method == "credit":

                    credit_sales += float(
                        row["total"] or 0
                    )

        receivable = (
            credit_sales
            - total_collection
        )

        # =================================================
        # BORCUMUZ
        #
        # SADECE VERESİYE ALIŞLAR
        # EKSİ TEDARİKÇİ ÖDEMELERİ
        # =================================================

        credit_purchases = 0.0

        for row in rows:

            if row["transaction_type"] == "purchase_on_credit":

                credit_purchases += float(
                    row["total"] or 0
                )

        payable = (
            credit_purchases
            + total_supplier_payment
        )

        # Borç negatif olamaz
        if payable < 0:

            payable = 0.0

        # =================================================
        # NET BAKİYE
        # =================================================

        net_balance = (
            receivable
            - payable
        )

        # =================================================
        # YUVARLAMA
        # =================================================

        total_sales = round(
            total_sales,
            2
        )

        total_collection = round(
            total_collection,
            2
        )

        receivable = round(
            receivable,
            2
        )

        payable = round(
            payable,
            2
        )

        net_balance = round(
            net_balance,
            2
        )

        # =================================================
        # EKRANA YAZ
        # =================================================

        self.sales_label.setText(
            f"{total_sales:,.2f} TL"
        )

        self.collection_label.setText(
            f"{total_collection:,.2f} TL"
        )

        self.receivable_label.setText(
            f"{receivable:,.2f} TL"
        )

        self.payable_label.setText(
            f"{payable:,.2f} TL"
        )

        if net_balance > 0:

            self.net_balance_label.setText(
                f"+{net_balance:,.2f} TL"
            )

        elif net_balance < 0:

            self.net_balance_label.setText(
                f"{net_balance:,.2f} TL"
            )

        else:

            self.net_balance_label.setText(
                "0,00 TL"
            )

    # =====================================================
    # ÜRÜN HAREKETLERİ
    # =====================================================

    def load_products(self, connection):

        self.products_table.setRowCount(
            0
        )

        rows = connection.execute(
            """
            SELECT
                t.transaction_type,
                p.product_name,
                ti.quantity,
                p.unit,
                ti.unit_price,
                ti.total_price
            FROM transaction_items ti

            INNER JOIN transactions t
                ON t.id = ti.transaction_id

            INNER JOIN products p
                ON p.id = ti.product_id

            WHERE t.customer_id = ?
              AND t.is_cancelled = 0
              AND t.transaction_type IN (
                    'sale',
                    'sale_on_credit',
                    'purchase',
                    'purchase_on_credit'
              )

            ORDER BY
                t.transaction_date DESC,
                t.id DESC
            """,
            (self.customer_id,)
        ).fetchall()

        for row in rows:

            row_number = (
                self.products_table.rowCount()
            )

            self.products_table.insertRow(
                row_number
            )

            transaction_type = (
                row["transaction_type"]
            )

            # =================================================
            # İŞLEM TÜRÜ
            # =================================================

            if transaction_type in (
                "purchase",
                "purchase_on_credit"
            ):

                display_type = "Alış"

            else:

                display_type = "Satış"

            # =================================================
            # VERİLER
            # =================================================

            product_name = (
                row["product_name"]
                or "-"
            )

            quantity = float(
                row["quantity"] or 0
            )

            unit = (
                row["unit"]
                or "adet"
            )

            unit_price = float(
                row["unit_price"] or 0
            )

            total = float(
                row["total_price"] or 0
            )

            values = [
                display_type,
                product_name,
                self.format_quantity(
                    quantity
                ),
                unit,
                f"{unit_price:,.2f} TL",
                f"{total:,.2f} TL",
            ]

            for column, value in enumerate(values):

                self.products_table.setItem(
                    row_number,
                    column,
                    QTableWidgetItem(
                        value
                    )
                )

    # =====================================================
    # İŞLEM GEÇMİŞİ
    # =====================================================

    def load_history(self, connection):

        self.history_table.setRowCount(
            0
        )

        rows = connection.execute(
            """
            SELECT
                id,
                transaction_date,
                transaction_type,
                description,
                amount,
                payment_method
            FROM transactions
            WHERE customer_id = ?
              AND is_cancelled = 0
            ORDER BY
                transaction_date DESC,
                id DESC
            """,
            (self.customer_id,)
        ).fetchall()

        for row in rows:

            row_number = (
                self.history_table.rowCount()
            )

            self.history_table.insertRow(
                row_number
            )

            transaction_type = (
                row["transaction_type"]
            )

            amount = float(
                row["amount"] or 0
            )

            # =================================================
            # İŞLEM ADI
            # =================================================

            if transaction_type == "sale_on_credit":

                display_type = (
                    "Veresiye Satış"
                )

                display_amount = abs(
                    amount
                )

            elif transaction_type == "sale":

                # sale işlemlerinde ödeme yöntemine bak.
                #
                # cash   -> Peşin Satış
                # credit -> Veresiye Satış
                payment_method = (
                    row["payment_method"]
                    or ""
                )

                if payment_method == "credit":

                    display_type = (
                        "Veresiye Satış"
                    )

                else:

                    display_type = (
                        "Peşin Satış"
                    )

                display_amount = abs(
                    amount
                )

            elif transaction_type == "payment_received":

                display_type = (
                    "Tahsilat"
                )

                display_amount = -abs(
                    amount
                )

            elif transaction_type == "purchase_on_credit":

                display_type = (
                    "Veresiye Alış"
                )

                display_amount = -abs(
                    amount
                )

            elif transaction_type == "purchase":

                # purchase işlemlerinde ödeme yöntemine bak.
                #
                # cash   -> Peşin Alış
                # credit -> Veresiye Alış
                payment_method = (
                    row["payment_method"]
                    or ""
                )

                if payment_method == "credit":

                    display_type = (
                        "Veresiye Alış"
                    )

                else:

                    display_type = (
                        "Peşin Alış"
                    )

                display_amount = -abs(
                    amount
                )

            elif transaction_type == "payment_made":

                display_type = (
                    "Ödeme"
                )

                # payment_made veritabanında
                # zaten NEGATİF.
                display_amount = amount

            else:

                display_type = (
                    transaction_type
                )

                display_amount = amount

            # =================================================
            # TARİH
            # =================================================

            transaction_date = str(
                row["transaction_date"]
            )

            if " " in transaction_date:

                transaction_date = (
                    transaction_date.split(" ")[0]
                )

            # =================================================
            # AÇIKLAMA
            # =================================================

            description = (
                row["description"]
                or ""
            )

            # =================================================
            # TABLOYA EKLE
            # =================================================

            self.history_table.setItem(
                row_number,
                0,
                QTableWidgetItem(
                    transaction_date
                )
            )

            self.history_table.setItem(
                row_number,
                1,
                QTableWidgetItem(
                    display_type
                )
            )

            self.history_table.setItem(
                row_number,
                2,
                QTableWidgetItem(
                    description
                )
            )

            self.history_table.setItem(
                row_number,
                3,
                QTableWidgetItem(
                    f"{display_amount:,.2f} TL"
                )
            )

    # =====================================================
    # İŞLEM İPTAL ET
    # =====================================================

    def cancel_selected_transaction(self):

        selected_rows = (
            self.history_table.selectionModel().selectedRows()
        )

        if not selected_rows:

            QMessageBox.warning(
                self,
                "İşlem Seçilmedi",
                "Lütfen iptal etmek istediğiniz işlemi seçin."
            )

            return

        row_number = selected_rows[0].row()

        # Tablo satırındaki tarih / işlem bilgilerini al
        transaction_type_item = (
            self.history_table.item(
                row_number,
                1
            )
        )

        amount_item = (
            self.history_table.item(
                row_number,
                3
            )
        )

        if not transaction_type_item:

            QMessageBox.warning(
                self,
                "Hata",
                "Seçilen işlem bulunamadı."
            )

            return

        transaction_type = (
            transaction_type_item.text()
        )

        amount_text = (
            amount_item.text()
            if amount_item
            else ""
        )

        answer = QMessageBox.question(
            self,
            "İşlemi İptal Et",
            (
                "Seçilen işlemi iptal etmek istediğinize "
                "emin misiniz?\n\n"
                f"İşlem: {transaction_type}\n"
                f"Tutar: {amount_text}\n\n"
                "İşlem silinmeyecek, iptal olarak işaretlenecektir."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if answer != QMessageBox.Yes:

            return

        conn = None

        try:

            conn = get_connection()

            # Önce seçilen satırın hangi transaction olduğunu
            # güvenli şekilde tarih + tip + müşteri üzerinden bul.
            rows = conn.execute(
                """
                SELECT
                    id,
                    transaction_type,
                    amount,
                    transaction_date
                FROM transactions
                WHERE customer_id = ?
                  AND is_cancelled = 0
                ORDER BY
                    transaction_date DESC,
                    id DESC
                """,
                (self.customer_id,)
            ).fetchall()

            if row_number >= len(rows):

                QMessageBox.warning(
                    self,
                    "Hata",
                    "Seçilen işlem artık bulunamıyor."
                )

                return

            transaction_id = rows[row_number]["id"]

            conn.execute(
                """
                UPDATE transactions
                SET is_cancelled = 1
                WHERE id = ?
                """,
                (transaction_id,)
            )

            conn.commit()

            QMessageBox.information(
                self,
                "İşlem İptal Edildi",
                "İşlem başarıyla iptal edildi."
            )

            self.load_customer()

        except Exception as e:

            if conn:
                conn.rollback()

            QMessageBox.critical(
                self,
                "Hata",
                f"İşlem iptal edilemedi.\n\n{e}"
            )

        finally:

            if conn:
                conn.close()

    # =====================================================
    # TAHSİLAT AL
    # =====================================================

    def open_collection(self):

        dialog = TahsilatDialog(
            self.customer_id,
            self.name_label.text(),
            self
        )

        result = dialog.exec()

        if result == QDialog.Accepted:

            self.load_customer()

    # =====================================================
    # ÖDEME YAP
    # =====================================================

    def open_payment(self):

        dialog = OdemeDialog(
            self.customer_id,
            self.name_label.text(),
            self
        )

        result = dialog.exec()

        if result == QDialog.Accepted:

            self.load_customer()

    # =====================================================
    # YENİ İŞLEM
    # =====================================================

    def open_transaction(self):

        dialog = YeniIslemDialog(
            self.customer_id,
            self
        )

        result = dialog.exec()

        if result == QDialog.Accepted:

            self.load_customer()

    # =====================================================
    # MİKTAR FORMATLAMA
    # =====================================================

    def format_quantity(self, quantity):

        if quantity == int(quantity):

            return str(
                int(quantity)
            )

        return (
            f"{quantity:.3f}"
            .rstrip("0")
            .rstrip(".")
        )