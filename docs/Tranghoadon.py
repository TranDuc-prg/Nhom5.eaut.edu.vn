import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
                             QGridLayout, QDateEdit, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

class InvoiceCard(QFrame):
    """Thẻ hiển thị thông tin tóm tắt của một hóa đơn"""
    def __init__(self, id_hd, date, customer, total, status="Đã thanh toán"):
        super().__init__()
        self.setFixedSize(500, 220)
        self.setObjectName("invoiceCard")
        self.setStyleSheet("""
            QFrame#invoiceCard {
                background-color: white; border-radius: 20px; border: 1px solid #F1F2F6;
            }
        """)

        # Hiệu ứng đổ bóng nhẹ
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 15)

        # Header: ID và Trạng thái
        header = QHBoxLayout()
        id_lbl = QLabel(f"Hóa đơn #{id_hd}")
        id_lbl.setStyleSheet("font-weight: bold; font-size: 18px; color: #2D3436;")
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet("background-color: #E8F5E9; color: #2E7D32; padding: 4px 10px; border-radius: 10px; font-size: 11px;")
        header.addWidget(id_lbl)
        header.addStretch()
        header.addWidget(status_lbl)

        # Thời gian
        time_lbl = QLabel(f"📅 {date}")
        time_lbl.setStyleSheet("color: #636E72; font-size: 13px;")

        # Thông tin khách hàng
        cust_info = QHBoxLayout()
        cust_icon = QLabel("👤")
        cust_name = QLabel(f"Khách hàng: {customer}")
        cust_name.setStyleSheet("color: #2D3436; font-weight: 500;")
        cust_info.addWidget(cust_icon)
        cust_info.addWidget(cust_name)
        cust_info.addStretch()

        # Tổng tiền
        total_info = QHBoxLayout()
        total_icon = QLabel("💰")
        total_val = QLabel(f"{total} đ")
        total_val.setStyleSheet("font-size: 20px; font-weight: bold; color: #FF7043;")
        total_info.addWidget(total_icon)
        total_info.addWidget(total_val)
        total_info.addStretch()

        # Footer: Số lượng sản phẩm và Nút chi tiết
        footer = QHBoxLayout()
        items_lbl = QLabel("2 sản phẩm")
        items_lbl.setStyleSheet("color: #A4B0BE; font-size: 12px;")
        btn_detail = QPushButton("👁️ Xem chi tiết")
        btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detail.setStyleSheet("border: none; color: #FF7043; font-weight: bold; background: transparent;")
        
        footer.addWidget(items_lbl)
        footer.addStretch()
        footer.addWidget(btn_detail)

        layout.addLayout(header)
        layout.addWidget(time_lbl)
        layout.addSpacing(10)
        layout.addLayout(cust_info)
        layout.addLayout(total_info)
        layout.addStretch()
        layout.addLayout(footer)

class InvoiceManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snack Shop - Quản lý hóa đơn")
        self.resize(1150, 850)
        self.setStyleSheet("background-color: #FDF5F0;")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(25)

        self.init_header()
        self.init_filter_bar()
        self.init_scroll_area()

    def init_header(self):
        header_v = QVBoxLayout()
        title = QLabel("Hóa đơn 🧾")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2D3436;")
        subtitle = QLabel("Quản lý và tra cứu hóa đơn bán hàng")
        subtitle.setStyleSheet("font-size: 14px; color: #636E72;")
        header_v.addWidget(title)
        header_v.addWidget(subtitle)
        self.main_layout.addLayout(header_v)

    def init_filter_bar(self):
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo mã hóa đơn hoặc tên khách hàng...")
        self.search_input.setFixedHeight(50)
        self.search_input.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #FFCCBC; padding-left: 15px;")

        self.date_filter = QDateEdit(QDate.currentDate())
        self.date_filter.setFixedHeight(50)
        self.date_filter.setFixedWidth(180)
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #FFCCBC; padding: 0 10px;")

        filter_layout.addWidget(self.search_input, 4)
        filter_layout.addWidget(self.date_filter, 1)
        self.main_layout.addLayout(filter_layout)

    def init_scroll_area(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(container)
        self.grid.setSpacing(25)

        # Dữ liệu hóa đơn mẫu
        invoices = [
            ("1247", "2026-04-14 - 10:30", "Nguyễn Văn A", "160.000"),
            ("1246", "2026-04-14 - 10:15", "Trần Thị B", "270.000"),
            ("1245", "2026-04-14 - 09:20", "Lê Văn C", "85.000"),
            ("1244", "2026-04-13 - 16:45", "Phạm Thị D", "190.000"),
            ("1243", "2026-04-13 - 14:20", "Hoàng Văn E", "110.000"),
            ("1242", "2026-04-13 - 08:10", "Đặng Thị F", "320.000")
        ]

        for i, data in enumerate(invoices):
            card = InvoiceCard(*data)
            self.grid.addWidget(card, i // 2, i % 2)

        scroll.setWidget(container)
        self.main_layout.addWidget(scroll)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceManager()
    window.show()
    sys.exit(app.exec())