import sys
import os
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QComboBox,
                             QDialog, QFormLayout, QMessageBox, QFileDialog, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPixmap, QColor, QFont

# --- HỆ THỐNG STYLE SHEET (GLASSMORPHISM RED CHERRY & CAFE STYLE) ---
GLOBAL_STYLE = """
    QWidget {
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        font-size: 13px;
        color: #3D0B12;
    }
    
    /* Thanh cuộn siêu mỏng tinh tế tông Đỏ Đô */
    QScrollBar:vertical {
        border: none;
        background: rgba(245, 224, 226, 0.4);
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #962D3E;
        min-height: 30px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #58111A;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background: rgba(245, 224, 226, 0.4);
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal {
        background: #962D3E;
        min-width: 30px;
        border-radius: 4px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* Ô nhập liệu & ComboBox hiệu ứng Kính Mờ viền đỏ nhẹ */
    QLineEdit, QComboBox {
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(150, 45, 62, 0.25);
        border-radius: 12px;
        padding: 8px 12px;
        color: #3D0B12;
    }
    QLineEdit:focus, QComboBox:focus {
        border: 1px solid #58111A;
        background-color: rgba(255, 255, 255, 0.95);
    }
    QComboBox::drop-down {
        border: none;
        padding-right: 10px;
    }
"""

# --- LỚP NÚT BẤM CÓ HOẠT ẢNH HOVER/CLICK CHUYỂN SANG MÀU ĐỎ ĐÔ ---
class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None, is_primary=True):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        if self.is_primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7A1C29, stop:1 #58111A);
                    color: white;
                    border-radius: 14px;
                    font-weight: bold;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.5);
                    border: 1px solid rgba(150, 45, 62, 0.4);
                    color: #58111A;
                    border-radius: 14px;
                    font-weight: bold;
                }
            """)

    def enterEvent(self, event):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(120)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        rect = self.geometry()
        self.anim.setEndValue(QRect(rect.x() - 2, rect.y() - 2, rect.width() + 4, rect.height() + 4))
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(120)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        rect = self.geometry()
        self.anim.setEndValue(QRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4))
        self.anim.start()
        super().leaveEvent(event)


# --- DIALOG THÊM/SỬA SẢN PHẨM PHONG CÁCH KÍNH ĐỎ ĐÔ ---
class ProductDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Thông tin sản phẩm")
        self.setFixedWidth(460)
        
        self.setStyleSheet(GLOBAL_STYLE + """
            QDialog {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFBFB, stop:1 #EAE2E3);
            }
            QLabel {
                font-weight: 600;
                color: #58111A;
            }
        """)
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        form = QFormLayout()
        form.setSpacing(12)
        
        self.txt_name = QLineEdit()
        self.cb_cat = QComboBox()
        self.load_categories() 
        self.txt_price = QLineEdit()
        self.txt_stock = QLineEdit()
        
        self.image_path = ""
        self.lbl_image_preview = QLabel("Kéo thả ảnh vào đây\nhoặc nhấn chọn file")
        self.lbl_image_preview.setFixedSize(150, 150)
        self.lbl_image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed rgba(150, 45, 62, 0.5); 
                border-radius: 16px; 
                background: rgba(255, 255, 255, 0.4);
                color: #962D3E;
                font-size: 12px;
                padding: 10px;
            }
        """)
        self.lbl_image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image_preview.setWordWrap(True)
        self.lbl_image_preview.setScaledContents(True)

        self.btn_select_img = AnimatedButton("📁 Chọn ảnh từ thiết bị", is_primary=False)
        self.btn_select_img.setFixedHeight(35)
        self.btn_select_img.clicked.connect(self.select_image_dialog)

        form.addRow("Tên món/sản phẩm:", self.txt_name)
        form.addRow("Danh mục menu:", self.cb_cat)
        form.addRow("Giá bán (VND):", self.txt_price)
        form.addRow("Số lượng tồn:", self.txt_stock)
        form.addRow("Ảnh minh họa:", self.btn_select_img)
        form.addRow("", self.lbl_image_preview)
        
        layout.addLayout(form)
        
        self.product_id = None
        if data: 
            self.product_id = data[0]
            self.txt_name.setText(data[1])
            self.cb_cat.setCurrentText(data[2])
            clean_price = str(data[3]).replace(".", "").replace(" đ", "").replace(",", "").strip()
            self.txt_price.setText(clean_price)
            self.txt_stock.setText(str(data[4]))
            if len(data) > 6 and data[6]:
                self.update_preview(data[6])

        self.btn_save = AnimatedButton("LƯU THÔNG TIN", is_primary=True)
        self.btn_save.setFixedHeight(45)
        self.btn_save.clicked.connect(self.validate_and_accept)
        layout.addWidget(self.btn_save)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            file_path = files[0]
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
                self.update_preview(file_path)
                event.accept()
            else:
                QMessageBox.warning(self, "Định dạng lỗi", "Chỉ hỗ trợ file hình ảnh (png, jpg, webp)!")

    def update_preview(self, file_path):
        if os.path.exists(file_path):
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.lbl_image_preview.setPixmap(pixmap.scaled(
                    self.lbl_image_preview.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                ))
                self.lbl_image_preview.setText("")
                self.lbl_image_preview.setStyleSheet("border: 1px solid #962D3E; border-radius: 16px; background: transparent;")

    def select_image_dialog(self):
        default_path = os.path.join(os.path.expanduser("~"), "Pictures")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh sản phẩm", default_path,
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)",
            options=QFileDialog.Option.DontUseNativeDialog
        )
        if file_path:
            self.update_preview(file_path)

    def load_categories(self):
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="", database="quanly_snack_db", buffered=True)
            cursor = conn.cursor()
            cursor.execute("SELECT ten_danhmuc FROM danhmuc")
            for row in cursor.fetchall():
                self.cb_cat.addItem(row[0])
            conn.close()
        except:
            self.cb_cat.addItems(["Đồ ăn vặt", "Nước uống"])

    def validate_and_accept(self):
        if not self.txt_name.text() or not self.txt_price.text() or not self.txt_stock.text():
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng không để trống thông tin cốt lõi!")
            return
        self.accept()

    def get_data(self):
        return {
            "id": self.product_id,
            "ten": self.txt_name.text(),
            "danhmuc": self.cb_cat.currentText(),
            "gia": float(self.txt_price.text() or 0),
            "tonkho": int(self.txt_stock.text() or 0),
            "anh": self.image_path
        }


# --- TRÌNH QUẢN LÝ CHÍNH (MAIN BOARD) ---
class ProductManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống quản lý sản phẩm - Cafe & Snack Shop")
        self.resize(1200, 850)
        
        # Nền tổng thể chuyển sang hồng nhạt/kem sang trọng tinh thoát phối đỏ đô
        self.setStyleSheet(GLOBAL_STYLE + """
            QWidget#MainContainer {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FAF5F5, stop:1 #EFEAE9);
            }
        """)
        self.setObjectName("MainContainer")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(22)
        
        self.init_header()
        self.init_stats_bar()
        self.init_table()
        self.load_data_from_db()

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost", user="root", password="", 
            database="quanly_snack_db", buffered=True 
        )

    def init_header(self):
        header_layout = QHBoxLayout()
        
        title = QLabel("Quản lý sản phẩm ☕")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #58111A; letter-spacing: 0.5px;")
        header_layout.addWidget(title)
        
        tool_layout = QHBoxLayout()
        tool_layout.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Nhập từ khóa tìm kiếm món ăn...")
        self.search_input.setFixedSize(320, 40)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.85);
                border: 1px solid rgba(150, 45, 62, 0.2);
                border-radius: 14px;
                padding-left: 15px;
                font-size: 13px;
            }
        """)
        self.search_input.textChanged.connect(self.load_data_from_db)
        
        self.btn_add = AnimatedButton("+ Thêm món mới", is_primary=True)
        self.btn_add.setFixedSize(160, 40)
        self.btn_add.clicked.connect(self.handle_add_product)

        tool_layout.addWidget(self.search_input)
        tool_layout.addWidget(self.btn_add)
        
        header_layout.addStretch()
        header_layout.addLayout(tool_layout)
        self.main_layout.addLayout(header_layout)

    def init_stats_bar(self):
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(20)
        self.stat_labels = {}
        
        cards_info = [
            ("Tổng số mặt hàng", "#58111A", "📦"),
            ("Tổng lượng tồn kho", "#4E9F3D", "📊"),
            ("Cảnh báo hết hàng", "#D9534F", "⚠️")
        ]
        
        for title, color, icon in cards_info:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(255, 255, 255, 0.75);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 20px;
                }}
            """)
            card.setFixedHeight(105)
            
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(6)
            shadow.setColor(QColor(139, 116, 118, 45))
            card.setGraphicsEffect(shadow)
            
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(22, 15, 22, 15)
            
            v_text = QVBoxLayout()
            l_title = QLabel(title)
            l_title.setStyleSheet("color: #8C676A; font-size: 13px; font-weight: 600;")
            l_val = QLabel("0")
            l_val.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 800;")
            v_text.addWidget(l_title)
            v_text.addWidget(l_val)
            
            l_icon = QLabel(icon)
            l_icon.setStyleSheet("font-size: 28px; background: transparent;")
            
            card_layout.addLayout(v_text)
            card_layout.addStretch()
            card_layout.addWidget(l_icon)
            
            self.stats_layout.addWidget(card)
            self.stat_labels[title] = l_val
            
        self.main_layout.addLayout(self.stats_layout)

    def init_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(7) 
        self.table.setHorizontalHeaderLabels(["ID", "Hình Ảnh", "Tên Sản Phẩm", "Danh Mục", "Giá Bán", "Tồn Kho", "Thao Tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(75)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False) 
        
        # Cập nhật style bảng: màu tiêu đề đỏ đô nhẹ, chữ đỏ đô đậm sang trọng
        self.table.setStyleSheet("""
            QTableWidget { 
                background-color: rgba(255, 255, 255, 0.65); 
                border-radius: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.5);
                padding: 10px;
            }
            QTableWidget::item {
                border-bottom: 1px solid rgba(150, 45, 62, 0.08);
                color: #58111A;
                font-weight: 500;
            }
            QTableWidget::item:selected {
                background-color: rgba(150, 45, 62, 0.15);
                color: #58111A;
            }
            QHeaderView::section { 
                background-color: #EFE6E7; 
                color: #58111A;
                padding: 10px; 
                font-weight: bold; 
                border: none;
                font-size: 13px;
            }
            QHeaderView::section:first {
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        
        table_shadow = QGraphicsDropShadowEffect()
        table_shadow.setBlurRadius(25)
        table_shadow.setXOffset(0)
        table_shadow.setYOffset(8)
        table_shadow.setColor(QColor(139, 116, 118, 35))
        self.table.setGraphicsEffect(table_shadow)
        
        self.main_layout.addWidget(self.table)

    def load_data_from_db(self):
        search_text = self.search_input.text()
        self.table.setRowCount(0)
        try:
            db = self.connect_db()
            cursor = db.cursor()
            
            query = """
                SELECT s.id, s.ten_sanpham, d.ten_danhmuc, s.gia_ban, s.so_luong_ton, s.hinh_anh 
                FROM sanpham s 
                JOIN danhmuc d ON s.id_danhmuc = d.id 
                WHERE s.ten_sanpham LIKE %s ORDER BY s.id DESC
            """
            cursor.execute(query, (f"%{search_text}%",))
            rows = cursor.fetchall()

            for idx, r in enumerate(rows):
                self.table.insertRow(idx)
                
                # Cột ID
                item_id = QTableWidgetItem(str(r[0]))
                item_id.setData(Qt.ItemDataRole.UserRole, r[5]) 
                item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(idx, 0, item_id)
                
                # Cột Thumbnail ảnh món ăn
                pic_label = QLabel()
                pic_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                if r[5] and os.path.exists(r[5]):
                    pix = QPixmap(r[5])
                    if not pix.isNull():
                        pic_label.setPixmap(pix.scaled(55, 55, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        pic_label.setStyleSheet("border-radius: 10px; background: transparent;")
                else:
                    pic_label.setText("☕ Không ảnh")
                    pic_label.setStyleSheet("color: #D2B4B6; font-size: 11px; font-weight: bold;")
                self.table.setCellWidget(idx, 1, pic_label)

                # Chèn text các cột dữ liệu thông thường
                cols = [r[1], r[2], f"{r[3]:,.0f} đ".replace(",", "."), str(r[4])]
                for i, val in enumerate(cols):
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(idx, i + 2, item)
                
                self.table.setCellWidget(idx, 6, self.create_action_buttons())

            self.update_stats(cursor)
            db.close()
        except Exception as e: 
            print(f"Lỗi tải dữ liệu: {e}")

    def update_stats(self, cursor):
        cursor.execute("SELECT COUNT(*) FROM sanpham")
        total_p = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(so_luong_ton) FROM sanpham")
        total_s = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM sanpham WHERE so_luong_ton < 10")
        low_s = cursor.fetchone()[0]

        self.stat_labels["Tổng số mặt hàng"].setText(str(total_p))
        self.stat_labels["Tổng lượng tồn kho"].setText(str(total_s))
        self.stat_labels["Cảnh báo hết hàng"].setText(str(low_s))

    def handle_add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                db = self.connect_db(); cursor = db.cursor()
                cursor.execute("SELECT id FROM danhmuc WHERE ten_danhmuc = %s", (data['danhmuc'],))
                res = cursor.fetchone()
                if res:
                    cursor.execute("INSERT INTO sanpham (ten_sanpham, id_danhmuc, gia_ban, so_luong_ton, hinh_anh) VALUES (%s, %s, %s, %s, %s)",
                                   (data['ten'], res[0], data['gia'], data['tonkho'], data['anh']))
                    db.commit()
                db.close(); self.load_data_from_db()
            except Exception as e: QMessageBox.critical(self, "Lỗi", str(e))

    def handle_edit_product(self):
        btn = self.sender()
        row = self.table.indexAt(btn.parent().pos()).row()
        p_data = [self.table.item(row, 0).text(), self.table.item(row, 2).text(),
                  self.table.item(row, 3).text(), self.table.item(row, 4).text(),
                  self.table.item(row, 5).text(), "", self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)]

        dialog = ProductDialog(self, data=p_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                db = self.connect_db(); cursor = db.cursor()
                cursor.execute("SELECT id FROM danhmuc WHERE ten_danhmuc = %s", (data['danhmuc'],))
                res = cursor.fetchone()
                if res:
                    cursor.execute("UPDATE sanpham SET ten_sanpham=%s, id_danhmuc=%s, gia_ban=%s, so_luong_ton=%s, hinh_anh=%s WHERE id=%s",
                                   (data['ten'], res[0], data['gia'], data['tonkho'], data['anh'], p_data[0]))
                    db.commit()
                db.close(); self.load_data_from_db()
            except Exception as e: QMessageBox.critical(self, "Lỗi", str(e))

    def handle_delete(self):
        btn = self.sender()
        row = self.table.indexAt(btn.parent().pos()).row()
        p_id = self.table.item(row, 0).text()
        if QMessageBox.question(self, "Xác nhận", f"Xóa vĩnh viễn mặt hàng ID {p_id} khỏi hệ thống?") == QMessageBox.StandardButton.Yes:
            try:
                db = self.connect_db(); cursor = db.cursor()
                cursor.execute("DELETE FROM sanpham WHERE id = %s", (p_id,))
                db.commit(); db.close(); self.load_data_from_db()
            except Exception as e: QMessageBox.critical(self, "Lỗi", str(e))

    def create_action_buttons(self):
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(10, 2, 10, 2)
        l.setSpacing(8)
        
        e = QPushButton("Sửa")
        d = QPushButton("Xóa")
        
        # Nút sửa/xóa đồng bộ nhẹ nhàng, hover chuyển sang sắc đỏ đô/xanh đậm cá tính
        e.setStyleSheet("""
            QPushButton {
                background: rgba(78, 159, 61, 0.13); color: #4E9F3D; 
                font-weight: bold; border-radius: 8px; padding: 6px 14px; border: none;
            }
            QPushButton:hover { background: #4E9F3D; color: white; }
        """)
        d.setStyleSheet("""
            QPushButton {
                background: rgba(88, 17, 26, 0.12); color: #58111A; 
                font-weight: bold; border-radius: 8px; padding: 6px 14px; border: none;
            }
            QPushButton:hover { background: #58111A; color: white; }
        """)
        
        e.setCursor(Qt.CursorShape.PointingHandCursor)
        d.setCursor(Qt.CursorShape.PointingHandCursor)
        
        e.clicked.connect(self.handle_edit_product)
        d.clicked.connect(self.handle_delete)
        
        l.addWidget(e)
        l.addWidget(d)
        return w


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont("Inter")
    if font.fromString("Segoe UI"):
        app.setFont(font)
        
    window = ProductManager()
    window.show()
    sys.exit(app.exec())