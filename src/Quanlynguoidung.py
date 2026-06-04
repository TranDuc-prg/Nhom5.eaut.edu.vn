import sys
import mysql.connector
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox, QMessageBox, 
                             QFrame, QFileDialog, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt6.QtGui import QCursor, QPixmap, QPainter, QPainterPath, QColor, QPen

# ========================== STYLE SHEET GLASSMORPHISM CAFE CHUYÊN NGHIỆP ==========================
CAFE_GLASS_QSS = """
    QWidget {
        font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
        color: #3E2723;
        font-size: 13px;
    }
    
    QWidget#MainWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FDFBF7, stop:1 #EAE3DA);
    }
    
    QFrame#LeftCard, QFrame#RightCard, QFrame#FilterCard {
        background-color: rgba(255, 255, 255, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.7);
        border-radius: 20px;
    }
    
    QLabel#Header {
        font-size: 24px;
        font-weight: 800;
        color: #58111A; /* Đỏ đô thẫm nguyên bản của bạn */
        letter-spacing: 0.5px;
    }
    
    QLineEdit, QComboBox {
        border: 1px solid rgba(88, 17, 26, 0.2); /* Viền đỏ đô nhẹ */
        border-radius: 12px;
        padding: 10px 14px;
        background-color: rgba(255, 255, 255, 0.85);
        color: #3E2723;
    }
    
    QLineEdit:focus, QComboBox:focus {
        border: 2px solid #58111A; /* Focus lên màu đỏ đô #58111A đậm nét */
        background-color: #FFFFFF;
    }
    
    QComboBox::drop-down {
        border: none;
        padding-right: 12px;
    }
    
    QTableWidget {
        background-color: transparent;
        border: none;
        gridline-color: rgba(88, 17, 26, 0.08);
    }
    
    QHeaderView::section {
        background-color: #58111A; /* Tiêu đề bảng chuẩn sắc đỏ đô #58111A */
        color: #FFF8E7;
        padding: 12px;
        font-weight: bold;
        border: none;
        border-radius: 8px;
    }
    
    QTableWidget::item {
        border-bottom: 1px solid rgba(88, 17, 26, 0.05);
        color: #4A3E3D;
    }
    
    QTableWidget::item:selected {
        background-color: rgba(88, 17, 26, 0.15); /* Highlight dòng được chọn bằng đỏ đô trong suốt */
        color: #58111A;
    }
    
    QMessageBox {
        background-color: #FDFBF7;
    }
    QMessageBox QPushButton {
        background-color: #58111A;
        color: white;
        border-radius: 8px;
        padding: 6px 18px;
        font-weight: bold;
    }
    QMessageBox QPushButton:hover {
        background-color: #3A0B11; /* Đỏ đô đậm hơn khi hover nút alert */
    }

    /* Tinh chỉnh thanh cuộn */
    QScrollBar:vertical {
        border: none;
        background: rgba(88, 17, 26, 0.02);
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: rgba(88, 17, 26, 0.25);
        min-height: 24px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #58111A;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""
# ========================== LỚP NÚT BẤM ANIMATION QUYẾN RŨ (ZOOM & FADE HOVER) ==========================
class CafeButton(QPushButton):
    def __init__(self, text, start_color, end_color, hover_color, parent=None):
        super().__init__(parent) # Chỉ truyền parent vào class cha QPushButton
        self.setText(text)       # Đặt chữ cho nút bấm bằng hàm độc lập
        self.start_color = start_color
        self.end_color = end_color
        self.hover_color = hover_color
        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style(is_hover=False)
        
    def update_style(self, is_hover=False):
        if is_hover:
            bg_style = f"background-color: {self.hover_color};"
        else:
            bg_style = f"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.start_color}, stop:1 {self.end_color});"
            
        self.setStyleSheet(f"""
            QPushButton {{
                {bg_style}
                color: white; 
                font-weight: bold; 
                border-radius: 12px; 
                border: none; 
                font-size: 13px;
                padding-left: 15px;
                padding-right: 15px;
            }}
        """)

    def enterEvent(self, event):
        # Hiệu ứng mượt mà nở rộng bề ngang chữ
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(150)
        self.anim.setStartValue(self.width())
        self.anim.setEndValue(self.width() + 6)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.update_style()
        super().leaveEvent(event)


# ========================== GIAO DIỆN CHÍNH NÂNG CẤP TOÀN DIỆN ==========================
class UserManager(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info
        self.setWindowTitle("Quản lý tài khoản cao cấp - Snack Shop")
        self.setMinimumSize(1250, 880)
        self.setObjectName("MainWidget")
        
        # Tạo thư mục lưu trữ ảnh chân dung hệ thống nếu chưa tồn tại
        self.avatar_dir = os.path.join(os.getcwd(), "assets", "avatars")
        os.makedirs(self.avatar_dir, exist_ok=True)
        
        # Cấu hình Database
        self.db_config = {
            "host": "localhost", 
            "user": "root", 
            "password": "", 
            "database": "quanly_snack_db"
        }
        
        self.current_image_path = "" 
        self.init_ui()
        self.load_data()
        self.start_fade_in_animation()

    def start_fade_in_animation(self):
        """Hiệu ứng khởi chạy app mờ dần sang hiển thị sắc nét đỉnh cao"""
        self.setWindowOpacity(0.0)
        self.win_anim = QPropertyAnimation(self, b"windowOpacity")
        self.win_anim.setDuration(500)
        self.win_anim.setStartValue(0.0)
        self.win_anim.setEndValue(1.0)
        self.win_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.win_anim.start()

    def get_round_pixmap(self, image_path, size=120):
        target = QPixmap(size, size)
        target.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(target)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)

        if image_path and os.path.exists(image_path):
            src_pixmap = QPixmap(image_path)
            scaled = src_pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            x = (size - scaled.width()) // 2
            y = (size - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.setBrush(QColor("#EADBC8"))
            painter.setPen(Qt.GlobalColor.transparent)
            painter.drawEllipse(0, 0, size, size)
            
        painter.setClipping(False)
        painter.setPen(QPen(QColor("#58111A"), 2))
        painter.drawEllipse(1, 1, size-2, size-2)
        painter.end()
        return target

    def init_ui(self):
        self.setStyleSheet(CAFE_GLASS_QSS)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 35)

        # Thanh tiêu đề chính
        header_layout = QHBoxLayout()
        header = QLabel(" HỆ THỐNG QUẢN TRỊ TÀI KHOẢN ")
        header.setObjectName("Header")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(25)

        # --- PANEL TRÁI: FORM NHẬP LIỆU (3D CARD) ---
        left_card = QFrame()
        left_card.setObjectName("LeftCard")
        left_card.setFixedWidth(360)
        
        shadow_left = QGraphicsDropShadowEffect(self)
        shadow_left.setBlurRadius(25)
        shadow_left.setColor(QColor(88, 17, 26, 30))
        shadow_left.setOffset(0, 8)
        left_card.setGraphicsEffect(shadow_left)

        form_layout = QVBoxLayout(left_card)
        form_layout.setContentsMargins(25, 25, 25, 25)
        form_layout.setSpacing(10)

        self.lbl_avatar = QLabel()
        self.lbl_avatar.setFixedSize(120, 120)
        self.lbl_avatar.setPixmap(self.get_round_pixmap("", 120))
        
        btn_upload = QPushButton("Thay đổi ảnh chân dung")
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.clicked.connect(self.upload_image)
        btn_upload.setStyleSheet("color: #58111A; font-weight: bold; border: none; background: transparent; text-decoration: underline;")
        form_layout.addWidget(self.lbl_avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(btn_upload, alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addSpacing(5)

        self.txt_id = self.create_input("ID tự sinh tự động", enabled=False)
        self.txt_tk = self.create_input("Nhập tên đăng nhập...")
        self.txt_mk = self.create_input("Nhập mật khẩu bảo mật...", is_password=True)
        self.txt_ten = self.create_input("Nhập họ và tên đầy đủ...")
        self.cb_vaitro = QComboBox()
        self.cb_vaitro.addItems(["Admin", "NhanVien", "KhachHang"])

        for label, widget in [("MÃ SỐ THÀNH VIÊN:", self.txt_id), ("TÀI KHOẢN ĐĂNG NHẬP:", self.txt_tk), 
                             ("MẬT KHẨU TRUY CẬP:", self.txt_mk), ("HỌ VÀ TÊN THÀNH VIÊN:", self.txt_ten), ("VAI TRÒ HỆ THỐNG:", self.cb_vaitro)]:
            l = QLabel(label)
            l.setStyleSheet("font-weight: 700; color: #5C4033; font-size: 11px; letter-spacing: 0.5px;")
            form_layout.addWidget(l)
            form_layout.addWidget(widget)

        form_layout.addSpacing(10)
        
        self.btn_add = CafeButton("THÊM THÀNH VIÊN MỚI", "#2E7D32", "#1B5E20", "#123E14") # Nút Thêm (Xanh lá thành công)
        self.btn_edit = CafeButton("CẬP NHẬT THÔNG TIN", "#7A1C27", "#58111A", "#3A0B11") # Nút Sửa (Gradient Đỏ đô thẫm phối màu #58111A)
        self.btn_del = CafeButton("XÓA TÀI KHOẢN KHỎI HỆ THỐNG", "#D32F2F", "#A11F1F", "#731010") # Nút Xóa (Đỏ tươi cảnh báo)
        self.btn_clear = CafeButton("LÀM TRỐNG KHUNG NHẬP", "#8D6E63", "#5D4037", "#402C26") # Nút Clear (Nâu ấm trầm)
        self.btn_add.clicked.connect(self.add_user)
        self.btn_edit.clicked.connect(self.update_user)
        self.btn_del.clicked.connect(self.delete_user)
        self.btn_clear.clicked.connect(self.clear_form)

        form_layout.addWidget(self.btn_add)
        form_layout.addWidget(self.btn_edit)
        form_layout.addWidget(self.btn_del)
        form_layout.addWidget(self.btn_clear)

        # --- PANEL PHẢI: KHU VỰC TÌM KIẾM & BẢNG HIỂN THỊ DỮ LIỆU ---
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setSpacing(15)

        # Khung Tìm kiếm - Lọc dữ liệu Realtime nhanh chóng
        filter_card = QFrame()
        filter_card.setObjectName("FilterCard")
        filter_card.setFixedHeight(65)
        
        shadow_filter = QGraphicsDropShadowEffect(self)
        shadow_filter.setBlurRadius(15)
        shadow_filter.setColor(QColor(62, 39, 35, 20))
        shadow_filter.setOffset(0, 4)
        filter_card.setGraphicsEffect(shadow_filter)

        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(20, 0, 20, 0)
        filter_layout.setSpacing(15)

        filter_layout.addWidget(QLabel("🔍 Tìm kiếm nhanh:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Nhập từ khóa tài khoản hoặc họ tên cần tìm kiếm...")
        self.txt_search.textChanged.connect(self.filter_data)
        filter_layout.addWidget(self.txt_search, stretch=3)

        filter_layout.addWidget(QLabel("Vai trò:"))
        self.cb_filter_role = QComboBox()
        self.cb_filter_role.addItems(["Tất cả vai trò", "Admin", "NhanVien", "KhachHang"])
        self.cb_filter_role.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(self.cb_filter_role, stretch=1)

        right_panel_layout.addWidget(filter_card)

        # Khung bảng chính dữ liệu
        right_card = QFrame()
        right_card.setObjectName("RightCard")
        
        shadow_right = QGraphicsDropShadowEffect(self)
        shadow_right.setBlurRadius(25)
        shadow_right.setColor(QColor(62, 39, 35, 30))
        shadow_right.setOffset(0, 8)
        right_card.setGraphicsEffect(shadow_right)

        table_layout = QVBoxLayout(right_card)
        table_layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Chân dung", "Tài khoản", "Họ và tên", "Vai trò", "Mật khẩu"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 95) 
        self.table.verticalHeader().setDefaultSectionSize(75) 
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.cellClicked.connect(self.get_row_data)

        table_layout.addWidget(self.table)
        right_panel_layout.addWidget(right_card)

        body_layout.addWidget(left_card)
        body_layout.addLayout(right_panel_layout, stretch=1)
        main_layout.addLayout(body_layout)

    def create_input(self, placeholder, enabled=True, is_password=False):
        txt = QLineEdit()
        txt.setPlaceholderText(placeholder)
        txt.setEnabled(enabled)
        if is_password: 
            txt.setEchoMode(QLineEdit.EchoMode.Password)
        return txt

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh đại diện", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                # Quản lý File thông minh: Sao chép file ảnh vào thư mục nội bộ dự án bảo toàn dữ liệu
                ext = os.path.splitext(file_path)[1]
                filename = f"avatar_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                dest_path = os.path.join(self.avatar_dir, filename)
                shutil.copy2(file_path, dest_path)
                
                # Lưu đường dẫn cục bộ mới bảo mật
                self.current_image_path = os.path.relpath(dest_path, os.getcwd())
                self.lbl_avatar.setPixmap(self.get_round_pixmap(self.current_image_path, 120))
            except Exception as e:
                QMessageBox.warning(self, "Lỗi nạp file", f"Không thể sao lưu file ảnh chân dung: {e}")

    def load_data(self):
        try:
            db = mysql.connector.connect(**self.db_config)
            cursor = db.cursor()
            cursor.execute("SELECT id, tai_khoan, ho_ten, vai_tro, anh_chan_dung, mat_khau FROM user")
            self.all_rows_cache = cursor.fetchall() # Tạo cache dữ liệu nội bộ phục vụ Tìm kiếm nhanh
            db.close()
            self.render_table_rows(self.all_rows_cache)
        except Exception as e: 
            print(f"Lỗi tải danh sách: {e}")

    def render_table_rows(self, data_rows):
        """Hàm vẽ dữ liệu lên bảng động"""
        self.table.setRowCount(0)
        for r_idx, r_data in enumerate(data_rows):
            self.table.insertRow(r_idx)
            
            # ID
            item_id = QTableWidgetItem(str(r_data[0]))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(r_idx, 0, item_id)

            # Container Ảnh tròn
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_lbl = QLabel()
            img_lbl.setFixedSize(58, 58)
            img_lbl.setPixmap(self.get_round_pixmap(r_data[4], 58))
            layout.addWidget(img_lbl)
            self.table.setCellWidget(r_idx, 1, container)

            # Text khác
            for i in range(1, 4):
                item = QTableWidgetItem(str(r_data[i]) if r_data[i] else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r_idx, i + 1, item)
            
            # Mật khẩu
            pwd_item = QTableWidgetItem(str(r_data[5]))
            pwd_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pwd_item.setForeground(QColor("#8D6E63"))
            self.table.setItem(r_idx, 5, pwd_item)

            # Lưu đường dẫn ảnh vào UserRole ẩn
            self.table.item(r_idx, 0).setData(Qt.ItemDataRole.UserRole, r_data[4])

    def filter_data(self):
        """Hành động tìm kiếm nâng cao lọc đa điều kiện cực kỳ tốc độ"""
        search_text = self.txt_search.text().lower().strip()
        selected_role = self.cb_filter_role.currentText()
        
        filtered_results = []
        for row in self.all_rows_cache:
            tk = str(row[1]).lower() if row[1] else ""
            ho_ten = str(row[2]).lower() if row[2] else ""
            vai_tro = str(row[3]) if row[3] else ""
            
            # Khớp từ khóa tìm kiếm
            match_keyword = (search_text in tk) or (search_text in ho_ten)
            # Khớp phân loại vai trò
            match_role = (selected_role == "Tất cả vai trò") or (selected_role == vai_tro)
            
            if match_keyword and match_role:
                filtered_results.append(row)
                
        self.render_table_rows(filtered_results)

    def get_row_data(self, row, col):
        try:
            self.txt_id.setText(self.table.item(row, 0).text())
            self.txt_tk.setText(self.table.item(row, 2).text())
            self.txt_ten.setText(self.table.item(row, 3).text())
            self.cb_vaitro.setCurrentText(self.table.item(row, 4).text())
            self.txt_mk.setText(self.table.item(row, 5).text())
            path = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.current_image_path = path if path else ""
            self.lbl_avatar.setPixmap(self.get_round_pixmap(self.current_image_path, 120))
        except: 
            pass

    def add_user(self):
        if not self.txt_tk.text() or not self.txt_mk.text(): 
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập đầy đủ tài khoản và mật khẩu!")
            return
        try:
            db = mysql.connector.connect(**self.db_config)
            cursor = db.cursor()
            sql = "INSERT INTO user (tai_khoan, mat_khau, ho_ten, vai_tro, anh_chan_dung) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.txt_tk.text(), self.txt_mk.text(), self.txt_ten.text(), self.cb_vaitro.currentText(), self.current_image_path))
            db.commit()
            db.close()
            self.load_data()
            self.clear_form()
            QMessageBox.information(self, "Thành công", "Đã thêm tài khoản thành viên thành công!")
        except Exception as e: 
            QMessageBox.critical(self, "Lỗi", str(e))

    def update_user(self):
        uid = self.txt_id.text()
        if not uid: 
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn một tài khoản từ danh sách bảng để cập nhật!")
            return
        try:
            db = mysql.connector.connect(**self.db_config)
            cursor = db.cursor()
            sql = "UPDATE user SET tai_khoan=%s, mat_khau=%s, ho_ten=%s, vai_tro=%s, anh_chan_dung=%s WHERE id=%s"
            cursor.execute(sql, (self.txt_tk.text(), self.txt_mk.text(), self.txt_ten.text(), self.cb_vaitro.currentText(), self.current_image_path, uid))
            db.commit()
            db.close()
            self.load_data()
            QMessageBox.information(self, "Thành công", "Cập nhật dữ liệu tài khoản hoàn tất!")
        except Exception as e: 
            QMessageBox.critical(self, "Lỗi", str(e))

    def delete_user(self):
        uid = self.txt_id.text()
        if not uid: 
            QMessageBox.warning(self, "Thông báo", "Vui lòng chọn tài khoản cần xóa trong bảng!")
            return
        confirm = QMessageBox.question(self, "Xác nhận hành động", f"Bạn có chắc chắn muốn xóa vĩnh viễn tài khoản ID {uid}?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                db = mysql.connector.connect(**self.db_config)
                cursor = db.cursor()
                cursor.execute("DELETE FROM user WHERE id=%s", (uid,))
                db.commit()
                db.close()
                self.load_data()
                self.clear_form()
                QMessageBox.information(self, "Thành công", "Đã gỡ bỏ tài khoản thành công!")
            except Exception as e: 
                QMessageBox.critical(self, "Lỗi", str(e))

    def clear_form(self):
        for txt in [self.txt_id, self.txt_tk, self.txt_mk, self.txt_ten]: 
            txt.clear()
        self.lbl_avatar.setPixmap(self.get_round_pixmap("", 120))
        self.current_image_path = ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = UserManager()
    win.show()
    sys.exit(app.exec())