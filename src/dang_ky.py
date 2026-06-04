import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QFrame, QMessageBox, QGraphicsDropShadowEffect, QFileDialog, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QBrush, QPixmap, QPainter, QPen


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
# GIAO DIỆN ĐĂNG KÝ PREMIUM FLAT LUXURY (ĐỒNG BỘ ĐỎ ĐÔ)
# =========================================================
class SnackShopRegister(QWidget):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.image_path = ""
        
        self.setWindowTitle("The Coffee Shop - Register Profile")
        self.setMinimumSize(1200, 750)
        
        # --- BẢNG MÀU ĐỎ ĐÔ THƯỢNG HẠNG ĐỒNG BỘ HOÀN HẢO ---
        self.color_wine_dark = "#58111A"       # Đỏ đô đậm chủ đạo (Deep Burgundy)
        self.color_bg_main = "#FDFBF9"         # Nền trắng ngà ánh hồng siêu mịn
        self.color_text_dark = "#2C1316"       # Màu chữ chính cốt lõi
        self.color_text_muted = "#8A7678"      # Màu nhãn và chữ phụ
        self.color_border = "#E8DCDD"          # Màu viền nhạt tinh tế
        self.color_accent = "#902936"          # Màu đỏ đô sáng nhung quý phái làm điểm nhấn khi Hover

        self.init_ui()

    def init_ui(self):
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(QColor(self.color_bg_main)))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # THẺ CARD CHÍNH
        self.reg_card = QFrame()
        self.reg_card.setObjectName("regCard")
        self.reg_card.setFixedSize(1000, 680)

        # Đổ bóng môi trường đồng điệu với trang Login
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 15)
        shadow.setColor(QColor(88, 17, 26, 20))
        self.reg_card.setGraphicsEffect(shadow)

        card_layout = QHBoxLayout(self.reg_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # =========================================================================
        # NỬA TRÁI: KHU VỰC ẢNH & THƯƠNG HIỆU
        # =========================================================================
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(45, 55, 45, 45)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_left_title = QLabel("HỒ SƠ\nTHÀNH VIÊN.")
        lbl_left_title.setObjectName("leftTitle")
        lbl_left_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_left_title)
        left_layout.addSpacing(25)

        self.setAcceptDrops(True)
        self.lbl_img = QLabel("Kéo thả ảnh chân dung\n\nhoặc click để chọn...")
        self.lbl_img.setObjectName("profileImageZone")
        self.lbl_img.setFixedSize(200, 200)
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_img.setScaledContents(True)
        self.lbl_img.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_img.mousePressEvent = lambda e: self.browse_image()
        
        left_layout.addWidget(self.lbl_img, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addSpacing(20)

        lbl_img_hint = QLabel("Hỗ trợ định dạng định danh tiêu chuẩn\nPNG, JPG, JPEG")
        lbl_img_hint.setObjectName("leftDesc")
        lbl_img_hint.setWordWrap(True)
        lbl_img_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(lbl_img_hint)

        left_layout.addStretch()
        
        footer = QLabel("PREMIUM COFFEE MEMBERSHIP")
        footer.setObjectName("leftFooter")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(footer)

        # =========================================================================
        # NỬA PHẢI: FORM ĐĂNG KÝ
        # =========================================================================
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(55, 45, 55, 45)
        right_layout.setSpacing(10)

        lbl_title = QLabel("Tạo Tài Khoản")
        lbl_title.setObjectName("formTitle")
        lbl_subtitle = QLabel("Đăng ký thành viên Hệ Thống để nhận đặc quyền vận hành.")
        lbl_subtitle.setObjectName("formSubtitle")
        right_layout.addWidget(lbl_title)
        right_layout.addWidget(lbl_subtitle)
        right_layout.addSpacing(15)

        fields_data = [
            ("HỌ VÀ TÊN", "Nhập họ và tên đầy đủ...", "txt_ho_ten"),
            ("TÊN ĐĂNG NHẬP", "Tạo tài khoản đăng nhập...", "txt_user"),
            ("MẬT KHẨU BẢO MẬT", "Tạo mật khẩu an toàn...", "txt_pass"),
            ("SỐ ĐIỆN THOẠI", "Nhập số điện thoại liên hệ...", "txt_sdt"),
            ("ĐỊA CHỈ", "Nhập địa chỉ cư trú hiện tại...", "txt_dc")
        ]

        for label_text, placeholder, attr_name in fields_data:
            lbl_field = QLabel(label_text, objectName="inputLabel")
            right_layout.addWidget(lbl_field)
            
            container = FocusFrame()
            lay = QHBoxLayout(container)
            lay.setContentsMargins(15, 4, 15, 4)
            
            line_edit = PremiumLineEdit(container, placeholder)
            if "MẬT KHẨU" in label_text:
                line_edit.setEchoMode(QLineEdit.EchoMode.Password)
                
            setattr(self, attr_name, line_edit)
            lay.addWidget(line_edit)
            right_layout.addWidget(container)

        right_layout.addSpacing(15)

        # NÚT ĐĂNG KÝ Submit (Đã đồng bộ Object Name chuẩn CSS)
        btn_reg = QPushButton("HOÀN TẤT ĐĂNG KÝ →")
        btn_reg.setObjectName("btnRegisterSubmit")
        btn_reg.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reg.clicked.connect(self.handle_register)
        right_layout.addWidget(btn_reg)

        # LINK QUAY LẠI (Đã đồng bộ Object Name chuẩn CSS)
        btn_back = QPushButton("Đã sở hữu tài khoản? Đăng nhập ngay")
        btn_back.setObjectName("btnBackLink")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(self.go_back)
        right_layout.addWidget(btn_back)

        right_layout.addStretch()

        card_layout.addWidget(left_panel, 42)
        card_layout.addWidget(right_panel, 58)
        self.main_layout.addWidget(self.reg_card)

        self.setup_styles()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.accept()
        else: e.ignore()

    def dropEvent(self, e):
        path = e.mimeData().urls()[0].toLocalFile()
        if path.lower().endswith(('.png', '.jpg', '.jpeg')):
            self.update_img(path)

    def browse_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh chân dung", "", "Images (*.png *.jpg *.jpeg)")
        if path: self.update_img(path)

    def update_img(self, path):
        self.image_path = path
        pixmap = QPixmap(path)
        self.lbl_img.setPixmap(pixmap)
        # Tinh chỉnh border-radius hình tròn mịn màng đồng quy chuẩn luxury
        self.lbl_img.setStyleSheet(f"border: 2px solid {self.color_border}; border-radius: 100px; background: #FFFFFF;")

    def handle_register(self):
        u = self.txt_user.text().strip()
        p = self.txt_pass.text().strip()
        name = self.txt_ho_ten.text().strip()
        
        if not u or not p or not name:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đủ Họ tên, Tài khoản, Mật khẩu!")
            return

        try:
            db = mysql.connector.connect(**self.login_window.db_config)
            cursor = db.cursor()
            sql = "INSERT INTO user (tai_khoan, mat_khau, ho_ten, vai_tro, so_dien_thoai, dia_chi, anh_chan_dung) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (u, p, name, 'KhachHang', self.txt_sdt.text().strip(), self.txt_dc.text().strip(), self.image_path))
            db.commit()
            db.close()
            
            QMessageBox.information(self, "Thành công", "Đăng ký thành công! Hãy đăng nhập.")
            self.go_back()
        except Exception as e:
            QMessageBox.critical(self, "Thất bại", f"Tài khoản đã tồn tại hoặc lỗi CSDL:\n{e}")

    def go_back(self):
        self.login_window.showMaximized()
        self.close()

    # =====================================================
    # TOÀN BỘ STYLESHEET ĐÃ ĐƯỢC ĐỒNG BỘ KHỚP HOÀN TOÀN ID UI
    # =====================================================
    def setup_styles(self):
        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}

            QFrame#regCard {{
                background-color: #FFFFFF;
                border-radius: 16px;
            }}

            QFrame#leftPanel {{
                background-color: {self.color_wine_dark};
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }}

            QLabel#leftTitle {{
                color: #FFFFFF;
                font-size: 36px;
                font-weight: 800;
                letter-spacing: 2px;
                line-height: 1.2;
            }}

            QLabel#profileImageZone {{
                background-color: rgba(255, 255, 255, 0.07);
                border: 2px dashed rgba(255, 255, 255, 0.25);
                border-radius: 100px;
                color: #D9C5C7;
                font-size: 12px;
            }}
            QLabel#profileImageZone:hover {{
                background-color: rgba(255, 255, 255, 0.12);
                border-color: {self.color_accent};
                color: #FFFFFF;
            }}

            QLabel#leftDesc {{
                color: #D9C5C7;
                font-size: 12px;
                line-height: 1.5;
            }}

            QLabel#leftFooter {{
                color: #9C7175;
                font-size: 10px;
                font-weight: bold;
                letter-spacing: 1px;
            }}

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

            QFrame#inputContainer {{
                background-color: #FDFBFB;
                border: 1.5px solid {self.color_border};
                border-radius: 10px;
            }}
            QFrame#inputContainer[focused="true"] {{
                background-color: #FFFFFF;
                border: 1.5px solid {self.color_wine_dark};
            }}

            QLineEdit {{
                border: none;
                background: transparent;
                font-size: 14px;
                color: {self.color_text_dark};
                padding: 8px 0px;
            }}

            /* ĐÃ SỬA CHUẨN ID: NÚT BẤM ĐĂNG KÝ Submit CHỦ ĐẠO */
            QPushButton#btnRegisterSubmit {{
                background-color: {self.color_wine_dark};
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 16px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 1px;
                margin-top: 5px;
            }}
            QPushButton#btnRegisterSubmit:hover {{
                background-color: {self.color_accent};
            }}
            QPushButton#btnRegisterSubmit:pressed {{
                background-color: #38070C;
            }}

            /* ĐÃ SỬA CHUẨN ID: LINK QUAY LẠI ĐĂNG NHẬP */
            QPushButton#btnBackLink {{
                background: transparent;
                border: none;
                color: {self.color_text_muted};
                font-size: 12px;
                font-weight: bold;
                text-align: left;
                margin-top: 5px;
            }}
            QPushButton#btnBackLink:hover {{
                color: {self.color_wine_dark};
                text-decoration: underline;
            }}
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    class MockLogin: db_config = {"host": "localhost", "user": "root", "password": "", "database": "quanly_coffee_db"}
    def showMaximized(): print("Mock quay lại Login")
    mock = MockLogin()
    mock.showMaximized = showMaximized
    
    window = SnackShopRegister(mock)
    window.show()
    sys.exit(app.exec())