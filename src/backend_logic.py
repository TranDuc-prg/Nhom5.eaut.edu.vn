import sys
import mysql.connector
from mysql.connector import Error
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
                             QMainWindow, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QBrush


class QuanLyAnVatBackend:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='quanly_snack_db', 
                user='root',
                password='' 
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("Kết nối database thành công!")
        except Error as e:
            print(f"Lỗi kết nối MySQL: {e}")
            self.connection = None

    def tim_kiem_san_pham(self, tu_khoa):
        if not self.connection: return []
        try:
            query = "SELECT id, ten_sanpham, gia_ban, so_luong_ton FROM sanpham WHERE ten_sanpham LIKE %s"
            self.cursor.execute(query, (f"%{tu_khoa}%",))
            return self.cursor.fetchall()
        except Error as e:
            print(f"Lỗi truy vấn sản phẩm: {e}")
            return []

    def kiem_tra_dang_nhap(self, username, password):
        if not self.connection: return None
        try:
            query = "SELECT * FROM nhanvien WHERE tai_khoan = %s AND mat_khau = %s"
            self.cursor.execute(query, (username, password))
            return self.cursor.fetchone()
        except Error as e:
            print(f"Lỗi đăng nhập: {e}")
            return None

# ==========================================================
# 2. MÀN HÌNH CHÍNH (DASHBOARD)
# ==========================================================
class GiaoDienChinh(QMainWindow):
    def __init__(self, user_info, backend):
        super().__init__()
        self.user_info = user_info
        self.backend = backend
        self.setWindowTitle(f"Snack Shop Dashboard - {self.user_info['ho_ten']}")
        self.resize(1100, 800)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header Info
        self.label_welcome = QLabel(f"Nhân viên: {self.user_info['ho_ten']} | Quyền: {self.user_info['vai_tro']}")
        self.label_welcome.setStyleSheet("font-size: 16px; font-weight: bold; color: #5D4037; padding: 10px;")
        
        # Bảng sản phẩm
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Tên Món Ăn", "Giá Bán", "Tồn Kho"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { border-radius: 10px; background-color: white; gridline-color: #FFCCBC; }
            QHeaderView::section { background-color: #58111A; color: white; font-weight: bold; }
        """)
        self.table.setAlternatingRowColors(True)

        # Nút làm mới
        self.btn_refresh = QPushButton("🔄 Cập nhật danh sách món")
        self.btn_refresh.setStyleSheet("""
            QPushButton { background-color: #58111A; color: white; padding: 12px; font-weight: bold; border-radius: 10px; }
            QPushButton:hover { background-color: #8B5E3C; }
        """)
        self.btn_refresh.clicked.connect(self.load_data)

        layout.addWidget(self.label_welcome)
        layout.addWidget(self.table)
        layout.addWidget(self.btn_refresh)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_data(self):
        try:
            data = self.backend.tim_kiem_san_pham('')
            self.table.setRowCount(0)
            for row_idx, row_data in enumerate(data):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(str(row_data['ten_sanpham'])))
                
                gia = float(row_data['gia_ban'])
                item_gia = QTableWidgetItem(f"{gia:,.0f} đ")
                item_gia.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                self.table.setItem(row_idx, 2, item_gia)
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(row_data['so_luong_ton'])))
        except Exception as e:
            print(f"Lỗi load bảng: {e}")

# ==========================================================
# 3. MÀN HÌNH ĐĂNG NHẬP (LOGIN)
# ==========================================================
class SnackShopLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.backend = QuanLyAnVatBackend()
        self.setWindowTitle("Cofee Shop - Đăng nhập")
        self.resize(1100, 800)
        
        self.setup_ui()
        self.btn_login.clicked.connect(self.handle_login)

    def setup_ui(self):
        # Background color
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(QColor("#FFF5F2")))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Login Card
        self.login_card = QFrame()
        self.login_card.setFixedSize(380, 520)
        self.login_card.setObjectName("loginCard")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(230, 126, 34, 50))
        self.login_card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.login_card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(150)
        h_layout = QVBoxLayout(header)
        title = QLabel("Snack Shop")
        title.setObjectName("labelTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(title)

        # Body
        body = QFrame()
        b_layout = QVBoxLayout(body)
        b_layout.setContentsMargins(40, 20, 40, 20)
        
        b_layout.addWidget(QLabel("Tài khoản", objectName="labelInput"))
        self.input_username = QLineEdit(placeholderText="Nhập tài khoản")
        b_layout.addWidget(self.input_username)

        b_layout.addWidget(QLabel("Mật khẩu", objectName="labelInput"))
        self.input_password = QLineEdit(placeholderText="Nhập mật khẩu")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        b_layout.addWidget(self.input_password)

        self.btn_login = QPushButton("Đăng nhập ngay! 🎉")
        self.btn_login.setObjectName("btnLogin")
        b_layout.addWidget(self.btn_login)
        
        b_layout.addStretch()
        label_demo = QLabel("Mặc định: admin / 123456")
        label_demo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_demo.setStyleSheet("color: #A4B0BE; font-size: 11px;")
        b_layout.addWidget(label_demo)

        card_layout.addWidget(header)
        card_layout.addWidget(body)
        self.main_layout.addWidget(self.login_card)

        self.setStyleSheet("""
            QFrame#loginCard { background: white; border-radius: 30px; }
            QFrame#headerFrame { background: #58111A; border-top-left-radius: 30px; border-top-right-radius: 30px; }
            QLabel#labelTitle { color: white; font-size: 32px; font-weight: bold; }
            QLineEdit { border: 2px solid #FFCCBC; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
            QPushButton#btnLogin { background: #58111A; color: white; border-radius: 10px; padding: 12px; font-weight: bold; }
            QPushButton#btnLogin:hover { background: #8B5E3C; }
        """)

    def handle_login(self):
        user = self.backend.kiem_tra_dang_nhap(self.input_username.text(), self.input_password.text())
        if user:
            self.dashboard = GiaoDienChinh(user, self.backend)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "Lỗi", "Sai tài khoản hoặc mật khẩu! ❌")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnackShopLogin()
    window.show()
    sys.exit(app.exec())