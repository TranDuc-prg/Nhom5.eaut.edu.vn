import sys
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
    QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

# ============================================================
# GIAO DIỆN CHI TIẾT ĐƠN HÀNG
# ============================================================
class OrderDetailDialog(QDialog):
    def __init__(self, data, db_config):
        super().__init__()
        self.data = data
        self.db_config = db_config
        self.setWindowTitle(f"Hóa đơn chi tiết #{data['id']}")
        self.setFixedWidth(450)
        self.setFixedHeight(600)
        self.setStyleSheet("background-color: white;")
        self.init_ui()
        self.load_order_items()

    def init_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel(f"CHI TIẾT ĐƠN HÀNG #{self.data['id']}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF7E5F; padding: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        info_box = QFrame()
        info_box.setStyleSheet("background-color: #F8F9FA; border-radius: 10px; border: 1px solid #eee;")
        info_lay = QVBoxLayout(info_box)
        
        infos = [
            (f"👤 Khách hàng: {self.data['ten_khach']}"),
            (f"📞 Điện thoại: {self.data['sdt']}"),
            (f"📍 Địa chỉ: {self.data['dia_chi']}"),
            (f"💳 Thanh toán: {self.data['hinh_thuc_tt']}")
        ]
        for text in infos:
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 13px; color: #444; border: none;")
            info_lay.addWidget(lbl)
        layout.addWidget(info_box)

        layout.addWidget(QLabel("<b>📋 DANH SÁCH MÓN:</b>"))
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.item_container = QWidget()
        self.item_layout = QVBoxLayout(self.item_container)
        self.item_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.item_container)
        layout.addWidget(self.scroll)

        footer_lay = QHBoxLayout()
        total_lbl = QLabel(f"TỔNG CỘNG: <span style='color: #E74C3C; font-size: 18px;'>{self.data['tong_tien']:,}đ</span>")
        total_lbl.setStyleSheet("font-weight: bold; font-size: 15px; padding: 10px;")
        footer_lay.addStretch()
        footer_lay.addWidget(total_lbl)
        layout.addLayout(footer_lay)

        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(self.close)
        btn_close.setStyleSheet("background-color: #666; color: white; padding: 10px; border-radius: 5px; font-weight: bold;")
        layout.addWidget(btn_close)

    def load_order_items(self):
            try:
                db = mysql.connector.connect(**self.db_config)
                cur = db.cursor(dictionary=True)
                
                # 1. SỬA QUAN TRỌNG: Truy vấn cột 'danh_sach_mon' từ bảng 'chitietdonhang'
                cur.execute("SELECT danh_sach_mon FROM chitietdonhang WHERE id = %s", (self.data['id'],))
                result = cur.fetchone()
                
                if result and result['danh_sach_mon']:
                    # 2. Tách chuỗi văn bản thành danh sách (Ví dụ: "1x Bánh mì, 2x Nước")
                    mon_an_list = result['danh_sach_mon'].split(", ")
                    
                    for mon in mon_an_list:
                        # Tạo khung hiển thị cho từng món
                        row = QFrame()
                        row.setStyleSheet("border-bottom: 1px solid #eee; padding: 10px; background: #fff;")
                        l = QHBoxLayout(row)
                        
                        lbl_mon = QLabel(f"<b>{mon}</b>")
                        lbl_mon.setStyleSheet("font-size: 14px; color: #333;")
                        
                        l.addWidget(lbl_mon)
                        l.addStretch()
                        self.item_layout.addWidget(row)
                else:
                    self.item_layout.addWidget(QLabel("Không có dữ liệu món ăn."))
                    
                db.close()
            except Exception as e:
                print(f"Lỗi hiển thị chi tiết: {e}")

# ============================================================
# CARD ĐƠN HÀNG (CẬP NHẬT LOGIC TRẠNG THÁI)
# ============================================================
class OrderCard(QFrame):
    refresh_needed = pyqtSignal()

    def __init__(self, data, db_config):
        super().__init__()
        self.data = data
        self.db_config = db_config
        self.setObjectName("OrderCard")
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            #OrderCard { background-color: white; border-radius: 15px; border: 1px solid #eee; }
            #OrderCard:hover { border: 1.5px solid #FF7E5F; }
            QLabel { color: #444; }
            QPushButton { border-radius: 5px; padding: 6px 12px; font-weight: bold; color: white; }
        """)

        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel(f"Đơn hàng #{self.data['id']}")
        title.setStyleSheet("font-weight: bold; font-size: 18px;")
        
        # Đổi màu nhãn trạng thái theo giá trị
        st = self.data['trang_thai']
        st_colors = {
            "Chờ xác nhận": "#FFA500",
            "Đã xác nhận": "#4A90E2",
            "Đang vận chuyển": "#9B59B6",
            "Đã hoàn thành": "#2ECC71",
            "Đã hủy": "#E74C3C"
        }
        color = st_colors.get(st, "#666")
        status_tag = QLabel(st)
        status_tag.setStyleSheet(f"background-color: {color}22; color: {color}; font-weight: bold; padding: 3px 10px; border-radius: 10px;")
        
        price = QLabel(f"{self.data['tong_tien']:,}đ")
        price.setStyleSheet("color: #E74C3C; font-size: 20px; font-weight: bold;")
        
        header.addWidget(title)
        header.addWidget(status_tag)
        header.addStretch()
        header.addWidget(price)

        body = QVBoxLayout()
        body.addWidget(QLabel(f"📅 {self.data['ngay_tao']}"))
        body.addWidget(QLabel(f"👤 {self.data['ten_khach']} - {self.data['sdt']}"))
        body.addWidget(QLabel(f"📍 {self.data['dia_chi']}"))

        # Footer: Xử lý hiển thị nút bấm theo quy trình
        footer = QHBoxLayout()
        btn_action = QPushButton()
        btn_cancel = QPushButton("✕ Hủy đơn")
        btn_cancel.setStyleSheet("background-color: #FF5F5F;")
        btn_detail = QPushButton("👁 Chi tiết")
        btn_detail.setStyleSheet("background-color: #26C6DA;")

        # Logic chuyển đổi trạng thái tiếp theo
        if st == "Chờ xác nhận":
            btn_action.setText("✓ Xác nhận đơn")
            btn_action.setStyleSheet("background-color: #4A90E2;")
            btn_action.clicked.connect(lambda: self.update_status("Đã xác nhận"))
            btn_cancel.clicked.connect(lambda: self.update_status("Đã hủy"))
        elif st == "Đã xác nhận":
            btn_action.setText("🚚 Giao hàng")
            btn_action.setStyleSheet("background-color: #9B59B6;")
            btn_action.clicked.connect(lambda: self.update_status("Đang vận chuyển"))
            btn_cancel.clicked.connect(lambda: self.update_status("Đã hủy"))
        elif st == "Đang vận chuyển":
            btn_action.setText("🏁 Hoàn thành")
            btn_action.setStyleSheet("background-color: #2ECC71;")
            btn_action.clicked.connect(lambda: self.update_status("Đã hoàn thành"))
            btn_cancel.hide()
        else: # Đã hoàn thành hoặc Đã hủy
            btn_action.hide()
            btn_cancel.hide()

        btn_detail.clicked.connect(self.open_detail)

        footer.addWidget(btn_action)
        footer.addWidget(btn_cancel)
        footer.addWidget(btn_detail)
        footer.addStretch()
        
        layout.addLayout(header)
        layout.addLayout(body)
        layout.addLayout(footer)

    def open_detail(self):
        dlg = OrderDetailDialog(self.data, self.db_config)
        dlg.exec()

    def update_status(self, new_status):
        try:
            db = mysql.connector.connect(**self.db_config)
            cur = db.cursor()
            cur.execute("UPDATE chitietdonhang SET trang_thai=%s WHERE id=%s", (new_status, self.data['id']))
            db.commit()
            db.close()
            self.refresh_needed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

# ============================================================
# MÀN HÌNH CHÍNH
# ============================================================
class OrderManagementApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý đơn hàng")
        self.resize(1100, 750)
        self.db_config = {
            "host": "localhost", "user": "root", "password": "", "database": "quanly_snack_db"
        }
        self.current_filter = "Tất cả"
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("Quản lý đơn hàng")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        main_layout.addWidget(title)

        tab_layout = QHBoxLayout()
        tabs = ["Tất cả", "Chờ xác nhận", "Đã xác nhận", "Đang vận chuyển", "Đã hoàn thành", "Đã hủy"]
        for t in tabs:
            btn = QPushButton(t)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton { background: white; border: 1px solid #ddd; border-radius: 15px; padding: 8px 15px; }
                QPushButton:checked { background: #FF7E5F; color: white; border: none; }
            """)
            if t == "Tất cả": btn.setChecked(True)
            btn.clicked.connect(self.set_filter)
            tab_layout.addWidget(btn)
        tab_layout.addStretch()
        main_layout.addLayout(tab_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Tìm theo mã đơn, tên hoặc SĐT...")
        self.search_bar.setStyleSheet("background: white; border-radius: 15px; padding: 12px; border: 1px solid #eee;")
        self.search_bar.textChanged.connect(self.load_data)
        main_layout.addWidget(self.search_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.container = QWidget()
        self.list_layout = QVBoxLayout(self.container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setSpacing(15)
        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

    def set_filter(self):
        sender = self.sender()
        for btn in self.findChildren(QPushButton):
            if btn.isCheckable(): btn.setChecked(False)
        sender.setChecked(True)
        self.current_filter = sender.text()
        self.load_data()

    def load_data(self):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        try:
            db = mysql.connector.connect(**self.db_config)
            cur = db.cursor(dictionary=True)
            search = f"%{self.search_bar.text()}%"
            query = "SELECT * FROM chitietdonhang WHERE (ten_khach LIKE %s OR sdt_khach LIKE %s OR id LIKE %s)"
            params = [search, search, search]
            if self.current_filter != "Tất cả":
                query += " AND trang_thai = %s"
                params.append(self.current_filter)
            query += " ORDER BY id DESC"
            cur.execute(query, tuple(params))
            for r in cur.fetchall():
                card_data = {
                    "id": r["id"], "ngay_tao": str(r["ngay_tao"]), "ten_khach": r["ten_khach"] or "Khách lẻ",
                    "sdt": r["sdt_khach"] or "N/A", "dia_chi": r["dia_chi"] or "Tại quầy",
                    "tong_tien": float(r["tong_tien"]), "trang_thai": r["trang_thai"] or "Chờ xác nhận",
                    "hinh_thuc_tt": r["hinh_thuc_tt"]
                }
                card = OrderCard(card_data, self.db_config)
                card.refresh_needed.connect(self.load_data)
                self.list_layout.addWidget(card)
            db.close()
        except Exception as e: print(f"Lỗi: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderManagementApp()
    window.show()
    sys.exit(app.exec())