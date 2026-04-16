import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
                             QGridLayout, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor

class ProductCard(QFrame):
    """Thẻ sản phẩm trong danh sách lưới"""
    def __init__(self, name, price, icon):
        super().__init__()
        self.setFixedSize(160, 180)
        self.setObjectName("productCard")
        self.setStyleSheet("""
            QFrame#productCard {
                background-color: white; border-radius: 20px;
            }
            QFrame#productCard:hover {
                border: 2px solid #FF7043;
            }
        """)

        # Hiệu ứng đổ bóng
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 40px;")
        
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-weight: bold; font-size: 14px; color: #2D3436;")
        name_lbl.setWordWrap(True)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        price_lbl = QLabel(f"{price}đ")
        price_lbl.setStyleSheet("color: #FF7043; font-weight: bold; font-size: 13px;")

        layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(price_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

class SnackShopPOS(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snack Shop - Bán hàng")
        self.resize(1200, 800)
        self.setStyleSheet("background-color: #FDF5F0;")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- PHẦN BÊN TRÁI: DANH SÁCH SẢN PHẨM ---
        left_side = QVBoxLayout()
        
        title = QLabel("Bán hàng 🛍️")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2D3436;")
        subtitle = QLabel("Chọn sản phẩm để thêm vào giỏ hàng")
        subtitle.setStyleSheet("color: #636E72; margin-bottom: 10px;")
        
        left_side.addWidget(title)
        left_side.addWidget(subtitle)

        # Vùng cuộn danh sách sản phẩm
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(15)

        # Dữ liệu mẫu sản phẩm
        products = [
            ("Snack khoai tây", "60.000", "🥔"), ("Nước ngọt Coca", "40.000", "🥤"),
            ("Bánh quy socola", "50.000", "🍪"), ("Kẹo dẻo trái cây", "40.000", "🍓"),
            ("Chocolate sữa", "60.000", "🍫"), ("Nước ép cam", "45.000", "🧃"),
            ("Khoai tây chiên", "35.000", "🍟"), ("Popcorn bơ", "30.000", "🍿"),
            ("Kem que", "25.000", "🍦"), ("Bánh mì sandwich", "35.000", "🥪")
        ]

        for i, (name, price, icon) in enumerate(products):
            card = ProductCard(name, price, icon)
            self.grid_layout.addWidget(card, i // 4, i % 4)

        scroll.setWidget(container)
        left_side.addWidget(scroll)
        main_layout.addLayout(left_side, 7)

        # --- PHẦN BÊN PHẢI: GIỎ HÀNG ---
        right_side = QFrame()
        right_side.setObjectName("cartSide")
        right_side.setStyleSheet("""
            QFrame#cartSide {
                background-color: white; border-radius: 25px;
            }
        """)
        
        # Đổ bóng cho giỏ hàng
        right_shadow = QGraphicsDropShadowEffect()
        right_shadow.setBlurRadius(20)
        right_shadow.setColor(QColor(0, 0, 0, 20))
        right_side.setGraphicsEffect(right_shadow)

        cart_layout = QVBoxLayout(right_side)
        cart_layout.setContentsMargins(20, 25, 20, 25)

        # Tiêu đề giỏ hàng
        cart_header = QHBoxLayout()
        cart_icon = QLabel("🛒")
        cart_icon.setStyleSheet("font-size: 24px; background-color: #FFF3E0; padding: 10px; border-radius: 15px;")
        cart_title = QVBoxLayout()
        cart_title.addWidget(QLabel("Giỏ hàng", styleSheet="font-weight: bold; font-size: 18px;"))
        cart_title.addWidget(QLabel("1 sản phẩm", styleSheet="color: #636E72; font-size: 12px;"))
        cart_header.addWidget(cart_icon)
        cart_header.addLayout(cart_title)
        cart_header.addStretch()
        
        cart_layout.addLayout(cart_header)
        cart_layout.addSpacing(20)

        # Ô nhập tên khách hàng
        cart_layout.addWidget(QLabel("Tên khách hàng", styleSheet="font-weight: bold; color: #2D3436;"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("Nhập tên khách hàng (tùy chọn)")
        name_input.setStyleSheet("border: 1px solid #FFCCBC; border-radius: 10px; padding: 10px; background: #FFFBF9;")
        cart_layout.addWidget(name_input)
        
        cart_layout.addSpacing(20)

        # Danh sách mục trong giỏ (Giả lập 1 món)
        item_box = QFrame()
        item_box.setStyleSheet("background-color: #FDF5F0; border-radius: 15px; padding: 10px;")
        item_lay = QVBoxLayout(item_box)
        
        item_info = QHBoxLayout()
        item_info.addWidget(QLabel("🥛 Sữa chua", styleSheet="font-weight: bold;"))
        item_info.addStretch()
        item_info.addWidget(QLabel("🗑️", styleSheet="color: #FF7043;"))
        
        qty_lay = QHBoxLayout()
        qty_lay.addWidget(QLabel("20.000đ", styleSheet="color: #FF7043; font-weight: bold;"))
        qty_lay.addStretch()
        btn_minus = QPushButton("-")
        btn_plus = QPushButton("+")
        for b in [btn_minus, btn_plus]:
            b.setFixedSize(25, 25)
            b.setStyleSheet("background: #FF7043; color: white; border-radius: 5px; font-weight: bold;")
        qty_lay.addWidget(btn_minus)
        qty_lay.addWidget(QLabel(" 1 "))
        qty_lay.addWidget(btn_plus)
        
        item_lay.addLayout(item_info)
        item_lay.addLayout(qty_lay)
        cart_layout.addWidget(item_box)

        cart_layout.addStretch()

        # Tổng kết tiền
        total_lay = QVBoxLayout()
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("color: #F1F2F6;")
        total_lay.addWidget(line)
        
        def add_row(label, val, bold=False):
            row = QHBoxLayout()
            l = QLabel(label); v = QLabel(val)
            if bold: l.setStyleSheet("font-weight: bold; font-size: 18px;"); v.setStyleSheet("font-weight: bold; font-size: 18px; color: #FF7043;")
            else: l.setStyleSheet("color: #636E72;"); v.setStyleSheet("font-weight: bold;")
            row.addWidget(l); row.addStretch(); row.addWidget(v)
            return row

        total_lay.addLayout(add_row("Tạm tính:", "20.000đ"))
        total_lay.addLayout(add_row("Giảm giá:", "0đ"))
        total_lay.addLayout(add_row("Tổng cộng:", "20.000đ", True))
        
        cart_layout.addLayout(total_lay)

        # Nút thanh toán
        btn_pay = QPushButton("✓ Thanh toán")
        btn_pay.setFixedHeight(50)
        btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pay.setStyleSheet("""
            QPushButton {
                background-color: #FF7043; color: white; font-weight: bold; 
                font-size: 16px; border-radius: 15px;
            }
            QPushButton:hover { background-color: #E64A19; }
        """)
        cart_layout.addWidget(btn_pay)

        main_layout.addWidget(right_side, 3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnackShopPOS()
    window.show()
    sys.exit(app.exec())