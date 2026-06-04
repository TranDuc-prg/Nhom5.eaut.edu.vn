import sys
import mysql.connector

from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QMessageBox, QGraphicsDropShadowEffect,
    QCheckBox
)

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPalette, QBrush, QPainter, QPen, QFont

# Import trang đăng ký từ file dang_ky.py
from dang_ky import SnackShopRegister


# =========================================================
# LOGO VECTOR NGHỆ THUẬT (Vẽ bằng code siêu sắc nét)
# =========================================================
class CoffeeLogoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(80, 80)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Màu vàng đồng sang trọng của hạt cafe rang nghệ thuật
        pen = QPen(QColor("#C7A17A"), 2.5)
        painter.setPen(pen)

        # Vẽ thân tách cà phê tối giản
        painter.drawArc(15, 30, 40, 32, 180 * 16, 180 * 16)
        painter.drawLine(15, 30, 55, 30)
        
        # Quai cầm tách
        painter.drawArc(48, 36, 12, 12, 270 * 16, 180 * 16)
        
        # Đĩa lót tách
        painter.drawLine(10, 65, 60, 65)
        
        # Làn khói nóng cách điệu hình hình học thanh lịch
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.drawArc(22, 12, 8, 12, 90 * 16, 90 * 16)
        painter.drawArc(32, 10, 8, 12, 270 * 16, 90 * 16)
        painter.drawArc(42, 12, 8, 12, 90 * 16, 90 * 16)


# =========================================================
# ICON ĐƯỢC TINH CHỈNH CHI TIẾT
# =========================================================
class IconWidget(QWidget):
    def __init__(self, icon_type):
        super().__init__()
        self.icon_type = icon_type
        self.setFixedSize(20, 20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(QColor("#8C7E76"), 2)
        painter.setPen(pen)

        if self.icon_type == "user":
            painter.drawEllipse(5, 2, 10, 10)
            painter.drawArc(1, 14, 18, 10, 0 * 16, 180 * 16)
        elif self.icon_type == "lock":
            painter.drawRect(3, 9, 14, 10)
            painter.drawArc(5, 3, 10, 12, 0 * 16, 180 * 16)


# =========================================================
# KHUNG NHẬP LIỆU THÔNG MINH (Tự đổi viền khi Focus)
# =========================================================
class FocusFrame(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("inputContainer")
        self.setProperty("focused", "false")
        
    def set_focused(self, focused):
        self.setProperty("focused", str(focused).lower())
        self.style().unpolish(self)
        self.style().polish(self)


class PremiumLineEdit(QLineEdit):
    def __init__(self, parent_frame, placeholder=""):
        super().__init__()
        self.parent_frame = parent_frame
        self.setPlaceholderText(placeholder)
        self.setFrame(False)
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self.parent_frame:
            self.parent_frame.set_focused(True)
            
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.parent_frame:
            self.parent_frame.set_focused(False)


# =========================================================
# GIAO DIỆN CHÍNH PREMIUM LUXURY
# =========================================================
class SnackShopLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("The Snack Shop - Management System")
        self.setMinimumSize(1200, 750)

        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "quanly_snack_db"
        }

        # --- BẢNG MÀU ĐỎ ĐÔ THƯỢNG HẠNG VÀ SANG TRỌNG ---
        self.color_wine_dark = "#58111A"       # Đỏ đô đậm chủ đạo (Deep Burgundy)
        self.color_bg_main = "#FDFBF9"         # Nền trắng ngà ánh hồng siêu mịn
        self.color_text_dark = "#2C1316"       # Màu chữ chính cốt lõi
        self.color_text_muted = "#8A7678"      # Màu nhãn và chữ phụ
        self.color_border = "#E8DCDD"          # Màu viền nhạt tinh tế
        self.color_accent = "#902936"          # Màu đỏ đô sáng nhung quý phái làm điểm nhấn khi Hover
        self.color_logo_gold = "#D4AF37"       # Màu vàng hoàng gia cho Logo nổi bật trên nền đỏ đô           # Nâu sáng Cappuccino quý phái

        self.init_ui()

    def init_ui(self):
        # Thiết lập nền tổng thể mềm mại
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(QColor(self.color_bg_main)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # CARD ĐĂNG NHẬP TRUNG TÂM
        self.login_card = QFrame()
        self.login_card.setObjectName("loginCard")
        self.login_card.setFixedSize(1000, 600)

        # Hiệu ứng đổ bóng môi trường siêu mượt (Premium Soft Ambient Shadow)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 15)
        shadow.setColor(QColor(30, 16, 10, 20)) # Bóng nâu trong suốt nhẹ nhàng, không xám bẩn
        self.login_card.setGraphicsEffect(shadow)

        card_layout = QHBoxLayout(self.login_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # =================================================
        # NỬA TRÁI: ĐỊNH VỊ THƯƠNG HIỆU (LUXURY PANEL)
        # =================================================
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(55, 65, 55, 55)

        # Nạp Logo vẽ nghệ thuật bằng code
        self.logo_widget = CoffeeLogoWidget()
        
        lbl_brand_title = QLabel("THE\nSNACK\nSHOP.")
        lbl_brand_title.setObjectName("brandTitle")

        lbl_brand_desc = QLabel(
            "Hệ thống quản lý chuỗi vận hành & điểm bán hàng thông minh.\n"
            "Tối giản nền tảng — Tối đa hiệu năng."
        )
        lbl_brand_desc.setObjectName("brandDesc")
        lbl_brand_desc.setWordWrap(True)

        left_layout.addWidget(self.logo_widget)
        left_layout.addSpacing(15)
        left_layout.addWidget(lbl_brand_title)
        left_layout.addSpacing(25)
        left_layout.addWidget(lbl_brand_desc)
        left_layout.addStretch()

        footer = QLabel("PREMIUM SNACK POS V2.6")
        footer.setObjectName("brandFooter")
        left_layout.addWidget(footer)

        # =================================================
        # NỬA PHẢI: FORM ĐĂNG NHẬP SANG TRỌNG
        # =================================================
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(65, 65, 65, 65)
        right_layout.setSpacing(16)

        # Tiêu đề biểu mẫu chính
        lbl_title = QLabel("Đăng Nhập")
        lbl_title.setObjectName("formTitle")

        lbl_subtitle = QLabel("Chào mừng trở lại! Vui lòng truy cập tài khoản hệ thống.")
        lbl_subtitle.setObjectName("formSubtitle")

        right_layout.addWidget(lbl_title)
        right_layout.addWidget(lbl_subtitle)
        right_layout.addSpacing(25)

        # Ô NHẬP TÀI KHOẢN (Có tương tác viền thông minh)
        lbl_user = QLabel("TÊN ĐĂNG NHẬP")
        lbl_user.setObjectName("inputLabel")
        right_layout.addWidget(lbl_user)

        user_container = FocusFrame()
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(15, 6, 15, 6)
        user_layout.setSpacing(12)

        user_icon = IconWidget("user")
        self.input_username = PremiumLineEdit(user_container, "Nhập tên tài khoản của bạn...")
        
        user_layout.addWidget(user_icon)
        user_layout.addWidget(self.input_username)
        right_layout.addWidget(user_container)

        # Ô NHẬP MẬT KHẨU (Tích hợp nút Flat Reveal chuyên nghiệp)
        lbl_pass = QLabel("MẬT KHẨU")
        lbl_pass.setObjectName("inputLabel")
        right_layout.addWidget(lbl_pass)

        pass_container = FocusFrame()
        pass_layout = QHBoxLayout(pass_container)
        pass_layout.setContentsMargins(15, 6, 10, 6)
        pass_layout.setSpacing(12)

        lock_icon = IconWidget("lock")
        self.input_password = PremiumLineEdit(pass_container, "Nhập mật khẩu bảo mật...")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Nút phẳng hiển thị mật khẩu đẹp mắt
        self.btn_toggle_pass = QPushButton("👁")
        self.btn_toggle_pass.setObjectName("btnTogglePass")
        self.btn_toggle_pass.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_pass.setFixedSize(30, 30)

        def toggle_password_visibility():
            if self.input_password.echoMode() == QLineEdit.EchoMode.Password:
                self.input_password.setEchoMode(QLineEdit.EchoMode.Normal)
                self.btn_toggle_pass.setText("✕") # Đổi kí hiệu khi mở
            else:
                self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
                self.btn_toggle_pass.setText("👁")

        self.btn_toggle_pass.clicked.connect(toggle_password_visibility)

        pass_layout.addWidget(lock_icon)
        pass_layout.addWidget(self.input_password)
        pass_layout.addWidget(self.btn_toggle_pass)
        right_layout.addWidget(pass_container)

        # LẮP ĐƯỜNG PHẢN HỒI PHÍM ENTER ĐĂNG NHẬP QUY CHUẨN
        self.input_username.returnPressed.connect(self.handle_login)
        self.input_password.returnPressed.connect(self.handle_login)

        # GHI NHỚ ĐĂNG NHẬP (Custom CSS tạo hình khối phẳng cực đẹp)
        self.remember_check = QCheckBox("Duy trì trạng thái đăng nhập trên thiết bị này")
        self.remember_check.setCursor(Qt.CursorShape.PointingHandCursor)
        right_layout.addWidget(self.remember_check)
        right_layout.addSpacing(5)

        # NÚT ĐĂNG NHẬP PREMIUM
        self.btn_login = QPushButton("TIẾP TỤC VÀO HỆ THỐNG →")
        self.btn_login.setObjectName("btnLogin")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self.handle_login)
        right_layout.addWidget(self.btn_login)

        # LIÊN KẾT ĐĂNG KÝ PHẲNG TINH GỌN
        self.btn_register = QPushButton("Tạo tài khoản quản trị mới")
        self.btn_register.setObjectName("btnRegLink")
        self.btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_register.clicked.connect(self.open_register)
        right_layout.addWidget(self.btn_register)

        right_layout.addStretch()

        # LIÊN KẾT CÁC PANEL VÀO KHUNG CHÍNH
        card_layout.addWidget(left_panel, 44)
        card_layout.addWidget(right_panel, 56)
        self.main_layout.addWidget(self.login_card)

        self.setup_styles()

    def open_register(self):
        self.reg_window = SnackShopRegister(self)
        self.reg_window.showMaximized()
        self.hide()

    def handle_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        # HIỆU ỨNG TẢI TRẠNG THÁI TRỰC QUAN TRÊN PHÍM BẤM
        self.btn_login.setText("ĐANG XÁC THỰC THÔNG TIN...")
        self.btn_login.setEnabled(False)
        QApplication.processEvents()

        try:
            db = mysql.connector.connect(**self.db_config)
            cursor = db.cursor(dictionary=True)
            query = "SELECT id, tai_khoan, ho_ten, vai_tro FROM user WHERE tai_khoan = %s AND mat_khau = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            db.close()

            if user:
                QMessageBox.information(self, "Thành công", f"Chào mừng trở lại, {user['ho_ten']}!")
                self.redirect_by_role(user)
            else:
                QMessageBox.critical(self, "Lỗi", "Tài khoản hoặc mật khẩu không chính xác!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi CSDL", f"Kết nốt cơ sở dữ liệu thất bại:\n{e}")

        self.btn_login.setText("TIẾP TỤC VÀO HỆ THỐNG →")
        self.btn_login.setEnabled(True)

    def redirect_by_role(self, user_info):
        role = str(user_info.get('vai_tro', '')).strip()
        try:
            if role == 'Admin':
                from Trangchinh import GiaoDienChinh
                self.next_screen = GiaoDienChinh(user_info=user_info)
            elif role == 'NhanVien':
                from Trangnhanvien import GiaoDienChinh as GiaoDienNhanVien
                self.next_screen = GiaoDienNhanVien(user_info=user_info)
            else:
                from Trangbanhang import SnackShopPOS
                self.next_screen = SnackShopPOS(user_info=user_info)

            self.next_screen.showMaximized()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể điều hướng phân quyền giao diện:\n{e}")

    # =====================================================
    # TOÀN BỘ STYLESHEET CHUẨN ĐỒ HỌA THƯƠNG HIỆU CAO CẤP
    # =====================================================
    # =====================================================
    # TOÀN BỘ STYLESHEET CHUẨN ĐỒ HỌA THƯƠNG HIỆU CAO CẤP
    # =====================================================
    def setup_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}

            /* Khung chính phẳng bo góc nghệ thuật vừa phải */
            QFrame#loginCard {{
                background-color: #FFFFFF;
                border-radius: 16px;
            }}

            /* ĐÃ SỬA: Đổi sang màu đỏ đô wine_dark */
            QFrame#leftPanel {{
                background-color: {self.color_wine_dark};
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }}

            QLabel#brandTitle {{
                color: #FFFFFF;
                font-size: 40px;
                font-weight: 800;
                letter-spacing: 3px;
                line-height: 1.1;
            }}

            QLabel#brandDesc {{
                color: #D9C5C7;
                font-size: 13px;
                line-height: 1.6;
            }}

            QLabel#brandFooter {{
                color: #9C7175;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }}

            /* Khối điền thông tin bên phải */
            QLabel#formTitle {{
                color: {self.color_text_dark};
                font-size: 30px;
                font-weight: bold;
                letter-spacing: -0.5px;
            }}

            QLabel#formSubtitle {{
                color: {self.color_text_muted};
                font-size: 13px;
            }}

            QLabel#inputLabel {{
                color: {self.color_text_muted};
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1.5px;
            }}

            /* THÙNG CHỨA Ô NHẬP LIỆU: Phản hồi thông minh khi Focus */
            QFrame#inputContainer {{
                background-color: #FDFBFB;
                border: 1.5px solid {self.color_border};
                border-radius: 10px;
            }}
            
            /* ĐÃ SỬA: Đổi sang màu đỏ đô wine_dark khi focus */
            QFrame#inputContainer[focused="true"] {{
                background-color: #FFFFFF;
                border: 1.5px solid {self.color_wine_dark};
            }}

            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 14px;
                color: {self.color_text_dark};
                padding: 10px 0px;
            }}

            /* Nút ẩn hiện mật khẩu Flat tinh giản */
            QPushButton#btnTogglePass {{
                border: none;
                background: transparent;
                color: #8A7678;
                font-size: 14px;
            }}
            
            /* ĐÃ SỬA: Đổi sang màu đỏ đô wine_dark khi hover */
            QPushButton#btnTogglePass:hover {{
                color: {self.color_wine_dark};
            }}

            /* CUSTOM QCHECKBOX FLAT LUXURY (Hiệu ứng khối Inset đắt giá) */
            QCheckBox {{
                color: {self.color_text_muted};
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1.5px solid {self.color_border};
                border-radius: 5px;
                background-color: #FDFBFB;
            }}
            QCheckBox::indicator:hover {{
                border-color: {self.color_accent};
            }}
            
            /* ĐÃ SỬA: Đổi sang màu đỏ đô wine_dark khi check */
            QCheckBox::indicator:checked {{
                background-color: {self.color_wine_dark};
                border: 4px solid #FFFFFF;
            }}

            /* NÚT BẤM KHỐI PHẲNG CHỦ ĐẠO MÀU ĐỎ ĐÔ */
            /* ĐÃ SỬA: Đổi sang màu đỏ đô wine_dark */
            QPushButton#btnLogin {{
                background-color: {self.color_wine_dark};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 16px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1px;
                margin-top: 10px;
            }}
            QPushButton#btnLogin:hover {{
                background-color: {self.color_accent};
            }}
            QPushButton#btnLogin:pressed {{
                background-color: #38070C;
            }}

            /* LIÊN KẾT ĐĂNG KÝ */
            QPushButton#btnRegLink {{
                background: transparent;
                border: none;
                color: {self.color_text_muted};
                font-size: 12px;
                font-weight: bold;
                text-align: left;
                margin-top: 5px;
            }}
            
            /* ĐÃ SỬA: Đổi sang màu đỏ đô wine_dark khi hover link */
            QPushButton#btnRegLink:hover {{
                color: {self.color_wine_dark};
                text-decoration: underline;
            }}
        """)

# =========================================================
# KHỞI CHẠY HỆ THỐNG GIAO DIỆN KHÔNG LỖI
# =========================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnackShopLogin()
    window.show()
    window.setWindowState(Qt.WindowState.WindowMaximized)
    sys.exit(app.exec())