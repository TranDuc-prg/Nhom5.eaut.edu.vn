import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QLabel, QFrame, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class CustomerCard(QFrame):
    def __init__(self, name, phone, rank, orders, points, total_spent, last_purchase):
        super().__init__()
        self.setFixedSize(320, 380)
        self.setObjectName("CustomerCard")
        
        # Mapping màu sắc cho từng hạng khách hàng
        rank_colors = {
            "Gold": "#FFD700",
            "Silver": "#C0C0C0",
            "VIP": "#FF6B6B"
        }
        rank_bg = rank_colors.get(rank, "#E0E0E0")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header: Avatar + Name + Rank
        header_layout = QHBoxLayout()
        avatar = QLabel("👤") # Bạn có thể thay bằng QPixmap
        avatar.setStyleSheet("font-size: 30px; background-color: #F4A460; border-radius: 25px; padding: 5px;")
        avatar.setFixedSize(50, 50)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #333;")
        phone_label = QLabel(phone)
        phone_label.setStyleSheet("color: #666; font-size: 13px;")
        info_layout.addWidget(name_label)
        info_layout.addWidget(phone_label)

        rank_label = QLabel(rank)
        rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_label.setFixedSize(60, 25)
        rank_label.setStyleSheet(f"background-color: {rank_bg}; border-radius: 12px; font-weight: bold; font-size: 11px;")

        header_layout.addWidget(avatar)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        header_layout.addWidget(rank_label)
        layout.addLayout(header_layout)

        # Body details
        layout.addWidget(self.create_info_row("📦 Đơn hàng", str(orders)))
        layout.addWidget(self.create_info_row("⭐ Điểm tích lũy", str(points), bg="#E0F2F1"))
        
        # Total Spent Section
        spent_box = QVBoxLayout()
        spent_box.setSpacing(5)
        spent_label = QLabel("Tổng chi tiêu")
        spent_label.setStyleSheet("color: #888; font-size: 12px;")
        spent_value = QLabel(f"{total_spent}đ")
        spent_value.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF5722;")
        
        spent_frame = QFrame()
        spent_frame.setStyleSheet("background-color: #FFF5F2; border-radius: 10px; border: none;")
        spent_layout = QVBoxLayout(spent_frame)
        spent_layout.addWidget(spent_label)
        spent_layout.addWidget(spent_value)
        layout.addWidget(spent_frame)

        # Footer
        footer = QLabel(f"Mua hàng gần nhất: {last_purchase}")
        footer.setStyleSheet("color: #999; font-size: 11px; margin-top: 10px;")
        layout.addWidget(footer)

    def create_info_row(self, label_text, value_text, bg="transparent"):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {bg}; border-radius: 8px;")
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(10, 8, 10, 8)
        
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #555; border: none;")
        val = QLabel(value_text)
        val.setStyleSheet("font-weight: bold; border: none;")
        
        row_layout.addWidget(lbl)
        row_layout.addStretch()
        row_layout.addWidget(val)
        return frame

class CustomerManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý khách hàng")
        self.resize(1100, 800)
        self.setStyleSheet("background-color: #FFF8F3;") # Màu nền kem nhạt

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Title
        title = QLabel("Khách hàng")
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: #2D2424;")
        sub_title = QLabel("Quản lý thông tin khách hàng và lịch sử mua hàng")
        sub_title.setStyleSheet("font-size: 14px; color: #8D7B68; margin-bottom: 20px;")
        
        main_layout.addWidget(title)
        main_layout.addWidget(sub_title)

        # Search Bar
        search_input = QLineEdit()
        search_input.setPlaceholderText("🔍 Tìm kiếm theo tên, số điện thoại hoặc email...")
        search_input.setFixedWidth(400)
        search_input.setFixedHeight(45)
        search_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #EAEAEA;
                border-radius: 22px;
                padding-left: 20px;
                font-size: 14px;
            }
        """)
        main_layout.addWidget(search_input)
        main_layout.addSpacing(30)

        # Scroll Area for Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(25)

        # Dữ liệu mẫu
        customers = [
            ("Nguyễn Văn A", "0901234567", "Gold", 24, 385, "3.850.000", "2026-04-14"),
            ("Trần Thị B", "0912345678", "Silver", 18, 294, "2.940.000", "2026-04-14"),
            ("Lê Văn C", "0923456789", "VIP", 32, 512, "5.120.000", "2026-04-14"),
            ("Phạm Thị D", "0934567890", "Silver", 15, 228, "2.280.000", "2026-04-13"),
            ("Hoàng Văn E", "0945678901", "VIP", 45, 765, "7.650.000", "2026-04-13"),
        ]

        for i, data in enumerate(customers):
            card = CustomerCard(*data)
            self.grid_layout.addWidget(card, i // 3, i % 3)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        # Style chung cho Card
        self.setStyleSheet(self.styleSheet() + """
            #CustomerCard {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #F0F0F0;
            }
            #CustomerCard:hover {
                border: 1px solid #FFDAB9;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomerManagement()
    window.show()
    sys.exit(app.exec())