from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QDateEdit,
    QFrame,
    QProgressBar,
)
from PySide6.QtCore import QDate, Qt

from app.database.connection import get_connection


class RaporlarWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Raporlar")

        self.setup_ui()

    # =========================================================
    # ARAYÜZ
    # =========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            30,
            25,
            30,
            30
        )

        layout.setSpacing(15)

        # =====================================================
        # BAŞLIK
        # =====================================================

        title = QLabel(
            "Raporlar"
        )

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        subtitle = QLabel(
            "İşletmenin satış, alış, tahsilat, borç ve alacak durumunu inceleyin."
        )

        subtitle.setStyleSheet("""
            color: #888888;
            font-size: 13px;
        """)

        layout.addWidget(subtitle)

        # =====================================================
        # TARİH FİLTRESİ
        # =====================================================

        filter_frame = QFrame()

        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 10px;
            }

            QLabel {
                font-size: 13px;
            }

            QDateEdit,
            QComboBox {
                padding: 7px 10px;
                border: 1px solid #666666;
                border-radius: 6px;
                background-color: #2d2d2d;
            }

            QPushButton {
                padding: 8px 18px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)

        filter_layout = QHBoxLayout(
            filter_frame
        )

        filter_layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        filter_layout.addWidget(
            QLabel("Hazır Aralık:")
        )

        self.date_filter = QComboBox()

        self.date_filter.addItems([
            "Tümü",
            "Bu Ay",
            "Bu Yıl",
            "Özel Tarih",
        ])

        self.date_filter.currentTextChanged.connect(
            self.on_filter_changed
        )

        filter_layout.addWidget(
            self.date_filter
        )

        filter_layout.addSpacing(15)

        filter_layout.addWidget(
            QLabel("Başlangıç:")
        )

        self.start_date = QDateEdit()

        self.start_date.setCalendarPopup(
            True
        )

        self.start_date.setDisplayFormat(
            "dd.MM.yyyy"
        )

        self.start_date.setDate(
            QDate.currentDate().addMonths(-1)
        )

        filter_layout.addWidget(
            self.start_date
        )

        filter_layout.addSpacing(10)

        filter_layout.addWidget(
            QLabel("Bitiş:")
        )

        self.end_date = QDateEdit()

        self.end_date.setCalendarPopup(
            True
        )

        self.end_date.setDisplayFormat(
            "dd.MM.yyyy"
        )

        self.end_date.setDate(
            QDate.currentDate()
        )

        filter_layout.addWidget(
            self.end_date
        )

        filter_layout.addSpacing(15)

        apply_button = QPushButton(
            "Uygula"
        )

        apply_button.clicked.connect(
            self.load_reports
        )

        filter_layout.addWidget(
            apply_button
        )

        refresh_button = QPushButton(
            "Yenile"
        )

        refresh_button.clicked.connect(
            self.load_reports
        )

        filter_layout.addWidget(
            refresh_button
        )

        filter_layout.addStretch()

        layout.addWidget(
            filter_frame
        )

        # İlk açılışta "Tümü" seçili olduğu için
        # tarih alanlarını pasif hale getir.
        self.start_date.setEnabled(False)
        self.end_date.setEnabled(False)

        # =====================================================
        # ÖZET KARTLARI
        # =====================================================

        cards_layout = QGridLayout()

        cards_layout.setSpacing(
            12
        )

        self.sales_card = self.create_card(
            "Toplam Satış"
        )

        self.purchase_card = self.create_card(
            "Toplam Alış"
        )

        self.collection_card = self.create_card(
            "Toplam Tahsilat"
        )

        self.receivable_card = self.create_card(
            "Toplam Alacak"
        )

        self.payable_card = self.create_card(
            "Toplam Borç"
        )

        self.cash_card = self.create_card(
            "Kasa Bakiyesi"
        )

        cards_layout.addWidget(
            self.sales_card,
            0,
            0
        )

        cards_layout.addWidget(
            self.purchase_card,
            0,
            1
        )

        cards_layout.addWidget(
            self.collection_card,
            0,
            2
        )

        cards_layout.addWidget(
            self.receivable_card,
            1,
            0
        )

        cards_layout.addWidget(
            self.payable_card,
            1,
            1
        )

        cards_layout.addWidget(
            self.cash_card,
            1,
            2
        )

        layout.addLayout(
            cards_layout
        )

        # =====================================================
        # GÖRSEL KARŞILAŞTIRMA
        # =====================================================

        comparison_title = QLabel(
            "Satış / Alış Karşılaştırması"
        )

        comparison_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        layout.addWidget(
            comparison_title
        )

        comparison_frame = QFrame()

        comparison_frame.setStyleSheet("""
            QFrame {
                background-color: #363636;
                border-radius: 10px;
            }

            QLabel {
                font-size: 13px;
            }

            QProgressBar {
                border: none;
                border-radius: 6px;
                background-color: #242424;
                height: 14px;
                text-align: center;
            }

            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 6px;
            }
        """)

        comparison_layout = QVBoxLayout(
            comparison_frame
        )

        comparison_layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        # Satış
        sales_row = QHBoxLayout()

        self.sales_visual_label = QLabel(
            "Satış"
        )

        self.sales_visual_label.setMinimumWidth(
            80
        )

        self.sales_bar = QProgressBar()

        self.sales_bar.setRange(
            0,
            100
        )

        self.sales_bar.setTextVisible(
            False
        )

        sales_row.addWidget(
            self.sales_visual_label
        )

        sales_row.addWidget(
            self.sales_bar
        )

        comparison_layout.addLayout(
            sales_row
        )

        # Alış
        purchase_row = QHBoxLayout()

        self.purchase_visual_label = QLabel(
            "Alış"
        )

        self.purchase_visual_label.setMinimumWidth(
            80
        )

        self.purchase_bar = QProgressBar()

        self.purchase_bar.setRange(
            0,
            100
        )

        self.purchase_bar.setTextVisible(
            False
        )

        purchase_row.addWidget(
            self.purchase_visual_label
        )

        purchase_row.addWidget(
            self.purchase_bar
        )

        comparison_layout.addLayout(
            purchase_row
        )

        layout.addWidget(
            comparison_frame
        )

        # =====================================================
        # NET İŞLETME SONUCU
        # =====================================================

        self.net_result_label = QLabel(
            "Net İşletme Sonucu: 0.00 TL"
        )

        self.net_result_label.setAlignment(
            Qt.AlignCenter
        )

        self.net_result_label.setStyleSheet("""
            background-color: #3a3a3a;
            border-radius: 10px;
            padding: 15px;
            font-size: 20px;
            font-weight: bold;
        """)

        layout.addWidget(
            self.net_result_label
        )

        # =====================================================
        # DETAY TABLOSU
        # =====================================================

        details_title = QLabel(
            "Rapor Özeti"
        )

        details_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        layout.addWidget(
            details_title
        )

        self.table = QTableWidget()

        self.table.setColumnCount(
            2
        )

        self.table.setHorizontalHeaderLabels([
            "Başlık",
            "Değer",
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.Stretch
        )

        self.table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.table.setAlternatingRowColors(
            True
        )

        layout.addWidget(
            self.table
        )

        self.load_reports()

    # =========================================================
    # KART OLUŞTUR
    # =========================================================

    def create_card(self, title):

        card = QFrame()

        card.setMinimumHeight(
            90
        )

        card.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 10px;
            }
        """)

        card_layout = QVBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            15,
            10,
            15,
            10
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet("""
            color: #aaaaaa;
            font-size: 12px;
        """)

        value_label = QLabel(
            "0.00 TL"
        )

        value_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
        """)

        card_layout.addWidget(
            title_label
        )

        card_layout.addStretch()

        card_layout.addWidget(
            value_label
        )

        card.value_label = value_label

        return card

    # =========================================================
    # TARİH ARALIĞI
    # =========================================================

    def get_date_values(self):

        selected = self.date_filter.currentText()

        today = QDate.currentDate()

        if selected == "Bu Ay":

            start = QDate(
                today.year(),
                today.month(),
                1
            )

            end = today

        elif selected == "Bu Yıl":

            start = QDate(
                today.year(),
                1,
                1
            )

            end = today

        elif selected == "Özel Tarih":

            start = self.start_date.date()
            end = self.end_date.date()

        else:

            return None, None

        return (
            start.toString("yyyy-MM-dd"),
            end.toString("yyyy-MM-dd")
        )

    # =========================================================
    # RAPORLARI YÜKLE
    # =========================================================

    def load_reports(self):

        conn = None

        try:

            start_date, end_date = (
                self.get_date_values()
            )

            if (
                start_date
                and end_date
                and start_date > end_date
            ):

                QMessageBox.warning(
                    self,
                    "Tarih Hatası",
                    "Başlangıç tarihi bitiş tarihinden sonra olamaz."
                )

                return

            conn = get_connection()

            # =================================================
            # TARİH SQL
            # =================================================

            transaction_date_filter = ""

            date_params = ()

            if start_date and end_date:

                transaction_date_filter = """
                    AND date(transaction_date)
                    BETWEEN ? AND ?
                """

                date_params = (
                    start_date,
                    end_date
                )

            # =================================================
            # SATIŞ
            # =================================================

            sales_result = conn.execute(
                f"""
                SELECT
                    COALESCE(
                        SUM(amount),
                        0
                    ) AS total
                FROM transactions
                WHERE transaction_type IN (
                    'sale',
                    'sale_on_credit'
                )
                AND is_cancelled = 0
                {transaction_date_filter}
                """,
                date_params
            ).fetchone()

            total_sales = float(
                sales_result["total"] or 0
            )

            # =================================================
            # ALIŞ
            # =================================================

            purchase_result = conn.execute(
                f"""
                SELECT
                    COALESCE(
                        SUM(amount),
                        0
                    ) AS total
                FROM transactions
                WHERE transaction_type IN (
                    'purchase',
                    'purchase_on_credit'
                )
                AND is_cancelled = 0
                {transaction_date_filter}
                """,
                date_params
            ).fetchone()

            total_purchases = float(
                purchase_result["total"] or 0
            )

            # =================================================
            # TAHSİLAT
            # =================================================

            collection_result = conn.execute(
                f"""
                SELECT
                    COALESCE(
                        SUM(ABS(amount)),
                        0
                    ) AS total
                FROM transactions
                WHERE transaction_type = 'payment_received'
                AND is_cancelled = 0
                {transaction_date_filter}
                """,
                date_params
            ).fetchone()

            total_collection = float(
                collection_result["total"] or 0
            )

            # =================================================
            # CARİLER
            # =================================================

            customers = conn.execute(
                """
                SELECT
                    id,
                    type
                FROM customers
                WHERE is_active = 1
                """
            ).fetchall()

            total_receivable = 0.0
            total_payable = 0.0

            for customer in customers:

                customer_id = customer["id"]
                customer_type = customer["type"]

                # ---------------------------------------------
                # ALACAK
                # ---------------------------------------------

                if customer_type in (
                    "customer",
                    "both"
                ):

                    credit_sales_result = conn.execute(
                        f"""
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
                            ) AS total
                        FROM transactions
                        WHERE customer_id = ?
                          AND is_cancelled = 0
                          {transaction_date_filter}
                        """,
                        (
                            customer_id,
                            *date_params
                        )
                    ).fetchone()

                    credit_sales = float(
                        credit_sales_result["total"] or 0
                    )

                    collection_result = conn.execute(
                        f"""
                        SELECT
                            COALESCE(
                                SUM(ABS(amount)),
                                0
                            ) AS total
                        FROM transactions
                        WHERE customer_id = ?
                          AND transaction_type = 'payment_received'
                          AND is_cancelled = 0
                          {transaction_date_filter}
                        """,
                        (
                            customer_id,
                            *date_params
                        )
                    ).fetchone()

                    collections = float(
                        collection_result["total"] or 0
                    )

                    balance = (
                        credit_sales
                        - collections
                    )

                    if balance > 0:

                        total_receivable += balance

                # ---------------------------------------------
                # BORÇ
                # ---------------------------------------------

                if customer_type in (
                    "supplier",
                    "both"
                ):

                    credit_purchase_result = conn.execute(
                        f"""
                        SELECT
                            COALESCE(
                                SUM(
                                    CASE
                                        WHEN transaction_type = 'purchase_on_credit'
                                            THEN amount

                                        WHEN transaction_type = 'purchase'
                                             AND payment_method = 'credit'
                                            THEN amount

                                        ELSE 0
                                    END
                                ),
                                0
                            ) AS total
                        FROM transactions
                        WHERE customer_id = ?
                          AND is_cancelled = 0
                          {transaction_date_filter}
                        """,
                        (
                            customer_id,
                            *date_params
                        )
                    ).fetchone()

                    credit_purchases = float(
                        credit_purchase_result["total"] or 0
                    )

                    payment_result = conn.execute(
                        f"""
                        SELECT
                            COALESCE(
                                SUM(ABS(amount)),
                                0
                            ) AS total
                        FROM transactions
                        WHERE customer_id = ?
                          AND transaction_type = 'payment_made'
                          AND is_cancelled = 0
                          {transaction_date_filter}
                        """,
                        (
                            customer_id,
                            *date_params
                        )
                    ).fetchone()

                    payments = float(
                        payment_result["total"] or 0
                    )

                    balance = (
                        credit_purchases
                        - payments
                    )

                    if balance > 0:

                        total_payable += balance

            # =================================================
            # KASA
            # =================================================

            cash_date_filter = ""

            if start_date and end_date:

                cash_date_filter = """
                    AND date(transaction_date)
                    BETWEEN ? AND ?
                """

            cash_result = conn.execute(
                f"""
                SELECT
                    COALESCE(
                        SUM(amount),
                        0
                    ) AS balance
                FROM cash_transactions
                WHERE 1 = 1
                {cash_date_filter}
                """,
                date_params
            ).fetchone()

            cash_balance = float(
                cash_result["balance"] or 0
            )

            # =================================================
            # NET İŞLETME SONUCU
            #
            # Satış - Alış
            #
            # Tahsilat ve ödeme burada kullanılmaz.
            # Çünkü bunlar işletmenin gelir/gideri değil,
            # cari bakiyenin kapanmasıdır.
            # =================================================

            net_result = (
                total_sales
                - total_purchases
            )

            # =================================================
            # YUVARLA
            # =================================================

            total_sales = round(
                total_sales,
                2
            )

            total_purchases = round(
                total_purchases,
                2
            )

            total_collection = round(
                total_collection,
                2
            )

            total_receivable = round(
                total_receivable,
                2
            )

            total_payable = round(
                total_payable,
                2
            )

            cash_balance = round(
                cash_balance,
                2
            )

            net_result = round(
                net_result,
                2
            )

            # =================================================
            # KARTLARI GÜNCELLE
            # =================================================

            self.sales_card.value_label.setText(
                f"{total_sales:,.2f} TL"
            )

            self.purchase_card.value_label.setText(
                f"{total_purchases:,.2f} TL"
            )

            self.collection_card.value_label.setText(
                f"{total_collection:,.2f} TL"
            )

            self.receivable_card.value_label.setText(
                f"{total_receivable:,.2f} TL"
            )

            self.payable_card.value_label.setText(
                f"{total_payable:,.2f} TL"
            )

            self.cash_card.value_label.setText(
                f"{cash_balance:,.2f} TL"
            )

            # =================================================
            # SATIŞ / ALIŞ GÖRSELİ
            # =================================================

            maximum = max(
                total_sales,
                total_purchases,
                1
            )

            sales_percent = int(
                (total_sales / maximum) * 100
            )

            purchase_percent = int(
                (total_purchases / maximum) * 100
            )

            self.sales_bar.setValue(
                sales_percent
            )

            self.purchase_bar.setValue(
                purchase_percent
            )

            self.sales_visual_label.setText(
                f"Satış  {total_sales:,.2f} TL"
            )

            self.purchase_visual_label.setText(
                f"Alış  {total_purchases:,.2f} TL"
            )

            # =================================================
            # NET SONUÇ
            # =================================================

            if net_result > 0:

                self.net_result_label.setText(
                    f"Net İşletme Sonucu  +{net_result:,.2f} TL"
                )

            elif net_result < 0:

                self.net_result_label.setText(
                    f"Net İşletme Sonucu  {net_result:,.2f} TL"
                )

            else:

                self.net_result_label.setText(
                    "Net İşletme Sonucu  0,00 TL"
                )

            # =================================================
            # DETAY TABLOSU
            # =================================================

            reports = [
                (
                    "Toplam Satış",
                    f"{total_sales:,.2f} TL"
                ),
                (
                    "Toplam Alış",
                    f"{total_purchases:,.2f} TL"
                ),
                (
                    "Toplam Tahsilat",
                    f"{total_collection:,.2f} TL"
                ),
                (
                    "Toplam Alacak",
                    f"{total_receivable:,.2f} TL"
                ),
                (
                    "Toplam Borç",
                    f"{total_payable:,.2f} TL"
                ),
                (
                    "Kasa Bakiyesi",
                    f"{cash_balance:,.2f} TL"
                ),
                (
                    "Net İşletme Sonucu",
                    f"{net_result:,.2f} TL"
                ),
            ]

            self.table.setRowCount(
                0
            )

            for row_index, (
                report_title,
                report_value
            ) in enumerate(reports):

                self.table.insertRow(
                    row_index
                )

                title_item = QTableWidgetItem(
                    report_title
                )

                value_item = QTableWidgetItem(
                    report_value
                )

                title_item.setTextAlignment(
                    Qt.AlignVCenter | Qt.AlignLeft
                )

                value_item.setTextAlignment(
                    Qt.AlignVCenter | Qt.AlignRight
                )

                self.table.setItem(
                    row_index,
                    0,
                    title_item
                )

                self.table.setItem(
                    row_index,
                    1,
                    value_item
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Hata",
                f"Raporlar yüklenemedi.\n\n{e}"
            )

        finally:

            if conn:

                conn.close()

    # =========================================================
    # FİLTRE DEĞİŞİNCE
    # =========================================================

    def on_filter_changed(self):

        selected = self.date_filter.currentText()

        today = QDate.currentDate()

        # =====================================================
        # TÜMÜ
        # =====================================================

        if selected == "Tümü":

            self.start_date.setEnabled(False)
            self.end_date.setEnabled(False)

        # =====================================================
        # BU AY
        # =====================================================

        elif selected == "Bu Ay":

            self.start_date.setDate(
                QDate(
                    today.year(),
                    today.month(),
                    1
                )
            )

            self.end_date.setDate(
                today
            )

            self.start_date.setEnabled(False)
            self.end_date.setEnabled(False)

        # =====================================================
        # BU YIL
        # =====================================================

        elif selected == "Bu Yıl":

            self.start_date.setDate(
                QDate(
                    today.year(),
                    1,
                    1
                )
            )

            self.end_date.setDate(
                today
            )

            self.start_date.setEnabled(False)
            self.end_date.setEnabled(False)

        # =====================================================
        # ÖZEL TARİH
        # =====================================================

        elif selected == "Özel Tarih":

            self.start_date.setEnabled(True)
            self.end_date.setEnabled(True)

        # Raporu otomatik yenile
        self.load_reports()

