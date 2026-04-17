import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QVBoxLayout, 
                             QLabel, QFrame, QGridLayout, QScrollArea, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon

class ShadowCard(QFrame):
    """Lớp hỗ trợ tạo thẻ có bo góc và đổ bóng giống mẫu"""
    def __init__(self, bg_color="white", radius=20):
        super().__init__()
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: {radius}px;")
        
        # Hiệu ứng đổ bóng
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

class SnackShopDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snack Shop - Dashboard")
        self.resize(1200, 850)
        self.setStyleSheet("background-color: #FDF5F0;") # Màu nền kem nhạt của Dashboard

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.init_sidebar()
        self.init_content()

    def init_sidebar(self):
        # 1. SIDEBAR (Bên trái)
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("background-color: #FF7043; border: none;") # Màu cam đặc trưng
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 40, 20, 20)

        # Logo & Title
        logo_label = QLabel("🍭 Snack Shop")
        logo_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 30px;")
        sidebar_layout.addWidget(logo_label)

        # Menu Items (Dashboard, Sản phẩm, Hóa đơn...)
        menu_items = ["📊 Dashboard", "🍿 Sản phẩm", "📄 Hóa đơn", "👥 Khách hàng", "👤 Nhân viên", "📈 Báo cáo"]
        for item in menu_items:
            btn = QLabel(item)
            if "Dashboard" in item:
                # Mục đang được chọn (Active)
                btn.setStyleSheet("background-color: white; color: #FF7043; border-radius: 12px; padding: 12px; font-weight: bold;")
            else:
                btn.setStyleSheet("color: white; padding: 12px; font-weight: 500;")
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Admin Info Area
        admin_card = QFrame()
        admin_card.setStyleSheet("background-color: rgba(255,255,255,0.2); border-radius: 15px; padding: 10px;")
        admin_layout = QVBoxLayout(admin_card)
        admin_layout.addWidget(QLabel("👤 Admin User", styleSheet="color: white; font-weight: bold;"))
        admin_layout.addWidget(QLabel("admin@snackshop.com", styleSheet="color: #FFCCBC; font-size: 11px;"))
        sidebar_layout.addWidget(admin_card)

        self.main_layout.addWidget(sidebar)

    def init_content(self):
        # 2. VÙNG NỘI DUNG CHÍNH (Bên phải)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # Header Dashboard
        header_lbl = QLabel("Dashboard 📊")
        header_lbl.setStyleSheet("font-size: 28px; font-weight: bold; color: #2D3436;")
        content_layout.addWidget(header_lbl)

        # --- TOP STATS (4 thẻ thông số) ---
        stats_layout = QHBoxLayout()
        stats_data = [
            ("Doanh thu hôm nay", "2,450,000 đ", "#E8F5E9", "💰"),
            ("Số đơn hàng", "47", "#E3F2FD", "📦"),
            ("Khách hàng mới", "12", "#F3E5F5", "👥"),
            ("Tồn kho", "234", "#FFF3E0", "🧱")
        ]

        for title, val, color, icon in stats_data:
            card = ShadowCard()
            card.setFixedSize(210, 120)
            card_layout = QVBoxLayout(card)
            
            # Icon tròn nhỏ
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedSize(30, 30)
            icon_lbl.setStyleSheet(f"background-color: {color}; border-radius: 15px; font-size: 16px;")
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("color: #636E72; font-size: 13px;")
            
            val_lbl = QLabel(val)
            val_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #2D3436;")
            
            card_layout.addWidget(icon_lbl)
            card_layout.addWidget(title_lbl)
            card_layout.addWidget(val_lbl)
            stats_layout.addWidget(card)
        
        content_layout.addLayout(stats_layout)

        # --- MAIN GRIDS (Sản phẩm bán chạy & Đơn hàng gần đây) ---
        bottom_layout = QHBoxLayout()
        
        # Thẻ Sản phẩm bán chạy
        best_seller_card = ShadowCard()
        bs_layout = QVBoxLayout(best_seller_card)
        bs_layout.setContentsMargins(20, 20, 20, 20)
        bs_layout.addWidget(QLabel("🏆 Sản phẩm bán chạy", styleSheet="font-size: 18px; font-weight: bold; color: #2D3436; margin-bottom: 10px;"))
        
        # Giả lập danh sách sản phẩm
        items = [("Bánh quy bơ", "450,000 đ"), ("Kẹo dẻo trái cây", "380,000 đ"), ("Snack khoai tây", "320,000 đ")]
        for name, price in items:
            row = QFrame()
            row.setStyleSheet("border-bottom: 1px solid #F1F2F6; padding: 5px;")
            r_layout = QHBoxLayout(row)
            r_layout.addWidget(QLabel(f"🍿 {name}"))
            r_layout.addStretch()
            r_layout.addWidget(QLabel(price, styleSheet="color: #FF7043; font-weight: bold;"))
            bs_layout.addWidget(row)
        bs_layout.addStretch()

        # Thẻ Đơn hàng gần đây
        recent_order_card = ShadowCard()
        ro_layout = QVBoxLayout(recent_order_card)
        ro_layout.setContentsMargins(20, 20, 20, 20)
        ro_layout.addWidget(QLabel("📑 Đơn hàng gần đây", styleSheet="font-size: 18px; font-weight: bold; color: #2D3436; margin-bottom: 10px;"))
        
        # Giả lập đơn hàng
        orders = [("#DH001 - Nguyễn Văn A", "Hoàn thành"), ("#DH002 - Trần Thị B", "Đang xử lý")]
        for info, status in orders:
            row = QFrame()
            row_lay = QHBoxLayout(row)
            row_lay.addWidget(QLabel(info))
            status_lbl = QLabel(status)
            status_lbl.setStyleSheet("background-color: #E8F5E9; color: #2E7D32; border-radius: 8px; padding: 4px;")
            row_lay.addStretch()
            row_lay.addWidget(status_lbl)
            ro_layout.addWidget(row)
        ro_layout.addStretch()

        bottom_layout.addWidget(best_seller_card, 6) # Tỷ lệ 60%
        bottom_layout.addWidget(recent_order_card, 4) # Tỷ lệ 40%
        content_layout.addLayout(bottom_layout)

        self.main_layout.addWidget(content_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnackShopDashboard()
    window.show()
    sys.exit(app.exec())