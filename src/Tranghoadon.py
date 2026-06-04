import sys
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
                             QGridLayout, QGraphicsDropShadowEffect, QMessageBox, 
                             QDialog, QAbstractScrollArea)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPalette, QBrush

# --- HỆ THỐNG STYLE SHEET (GLASSMORPHISM LUXURY CAFE STYLE) ---
GLOBAL_STYLE = """
    QWidget {
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
        font-size: 13px;
        color: #3E2723;
    }
    
    /* Thanh cuộn siêu mỏng tinh tế, bo góc mượt mà */
    QScrollBar:vertical {
        border: none;
        background: rgba(245, 235, 224, 0.4);
        width: 6px;
        margin: 0px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #A67B5B;
        min-height: 30px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical:hover {
        background: #5C3D2E;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background: rgba(245, 235, 224, 0.4);
        height: 6px;
        margin: 0px;
        border-radius: 3px;
    }
    QScrollBar::handle:horizontal {
        background: #A67B5B;
        min-width: 30px;
        border-radius: 3px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* Thanh tìm kiếm Glassmorphism hiện đại */
    QLineEdit {
        background-color: rgba(255, 255, 255, 0.75);
        border: 1px solid rgba(166, 123, 91, 0.25);
        border-radius: 16px;
        padding: 10px 18px;
        color: #3E2723;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 1px solid #783D19;
        background-color: rgba(255, 255, 255, 0.95);
    }
"""

# --- LỚP NÚT BẤM CÓ HOẠT ẢNH MƯỢT MÀ (ANIMATED BUTTON) ---
class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None, is_primary=True):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        
        if self.is_primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #A67B5B, stop:1 #783D19);
                    color: white;
                    border-radius: 14px;
                    font-weight: bold;
                    font-size: 13px;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.5);
                    border: 1px solid rgba(166, 123, 91, 0.4);
                    color: #783D19;
                    border-radius: 14px;
                    font-weight: bold;
                    font-size: 13px;
                }
            """)

    def enterEvent(self, event):
        # Tạo hoạt ảnh phóng to nhẹ khi di chuột vào (Hover Animation)
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(120)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        rect = self.geometry()
        self.anim.setEndValue(QRect(rect.x() - 2, rect.y() - 2, rect.width() + 4, rect.height() + 4))
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Hoạt ảnh thu nhỏ mượt mà về vị trí cũ khi rời chuột
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(120)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        rect = self.geometry()
        self.anim.setEndValue(QRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4))
        self.anim.start()
        super().leaveEvent(event)


# 1. Hộp thoại hiển thị chi tiết đơn hàng (Hiệu ứng Kính mờ cao cấp)
class OrderDetailDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        order_id = data.get('id_donhang') or data.get('id')
        chi_phi = self.tinh_gia_von(order_id)
        self.setWindowTitle(f"Chi tiết hóa đơn #{order_id}")
        self.setFixedWidth(520)
        self.setStyleSheet(GLOBAL_STYLE + """
            QDialog { 
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FDFBF7, stop:1 #EAE3DA);
                border-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(18)

        title = QLabel(f"CHI TIẾT HÓA ĐƠN #{order_id}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #4A3525; letter-spacing: 1px;")
        layout.addWidget(title)

        top_line = QFrame()
        top_line.setFrameShape(QFrame.Shape.HLine)
        top_line.setStyleSheet("background-color: rgba(166, 123, 91, 0.3); max-height: 1px;")
        layout.addWidget(top_line)

        def add_info_row(label, value, is_bold=False, color="#4A3525"):
            row = QHBoxLayout()
            lbl = QLabel(f"{label}:")
            lbl.setStyleSheet("color: #8C7867; font-size: 13px; font-weight: 600; min-width: 130px;")
            
            val_text = str(value) if value and str(value).strip() != "" else "---"
            val = QLabel(val_text)
            style = f"color: {color}; font-size: 14px;"
            if is_bold: 
                style += " font-weight: 700;"
            
            val.setStyleSheet(style)
            val.setWordWrap(True)
            row.addWidget(lbl)
            row.addWidget(val, 1)
            layout.addLayout(row)

        date_obj = data.get('ngay_tao')
        date_str = date_obj.strftime("%d/%m/%Y %H:%M:%S") if date_obj else "---"
        add_info_row("📅 Thời gian lập", date_str)

        trang_thai = data.get('trang_thai', 'Chờ xử lý')
        status_colors = {
            "Đã hoàn thành": "#4E9F3D", "Thành công": "#4E9F3D", "Đã xong": "#4E9F3D",
            "Đã hủy": "#D9534F"
        }
        status_color = status_colors.get(trang_thai, "#58111A")
        add_info_row("🔔 Trạng thái đơn", trang_thai, True, status_color)

        add_info_row("👤 Khách hàng", data.get('ten_khach', 'Khách lẻ'), True, "#4A3525")
        add_info_row("📞 Số điện thoại", data.get('sdt_khach', '---'))
        add_info_row("📍 Hình thức bán", data.get('dia_chi', 'Mua tại cửa hàng'))
        add_info_row("💳 Thanh toán", data.get('hinh_thuc_tt', 'Tiền mặt'), False, "#5C4033")
        
        giam_gia = data.get('giam_gia', 0)
        add_info_row("🏷️ Chiết khấu/Giảm", f"{giam_gia:,} đ".replace(",", "."))

        mid_line = QFrame()
        mid_line.setFrameShape(QFrame.Shape.HLine)
        mid_line.setStyleSheet("background-color: rgba(166, 123, 91, 0.2); max-height: 1px;")
        layout.addWidget(mid_line)

        item_title = QLabel("📦 DANH SÁCH MÓN CHI TIẾT:")
        item_title.setStyleSheet("font-weight: 700; color: #4A3525; font-size: 13px;")
        layout.addWidget(item_title)

        raw_items = data.get('danh_sach_mon', "Không có thông tin món ăn")
        formatted_items = raw_items.replace(", ", "\n• ").replace(",", "\n• ")
        
        items_lbl = QLabel(f"• {formatted_items}")
        items_lbl.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.6); 
            border: 1px solid rgba(166, 123, 91, 0.15);
            padding: 15px; 
            border-radius: 14px; 
            color: #3E2723; 
            font-size: 13px;
            line-height: 20px;
        """)
        items_lbl.setWordWrap(True)
        layout.addWidget(items_lbl)
        tong_von = 0

        if chi_phi:
            cost_title = QLabel("💰 GIÁ VỐN CHI TIẾT:")
            cost_title.setStyleSheet(
                "font-weight:700;color:#4A3525;font-size:13px;"
            )
            layout.addWidget(cost_title)

            text = ""

            for item in chi_phi:
                gia_von = float(item["tong_gia_von"])
                tong_von += gia_von

                text += (
                    f"{item['ten_sanpham']}\n"
                    f"SL: {item['so_luong']} | "
                    f"Giá vốn: {gia_von:,.0f} đ\n\n"
                )

            lbl_cost = QLabel(text)
            lbl_cost.setWordWrap(True)
            lbl_cost.setStyleSheet("""
                background-color: rgba(255,255,255,0.6);
                border:1px solid rgba(166,123,91,0.15);
                padding:12px;
                border-radius:12px;
            """)

            layout.addWidget(lbl_cost)
        total_layout = QHBoxLayout()
        total_lbl = QLabel("TỔNG TIỀN PHẢI THU:")
        total_lbl.setStyleSheet("font-size: 13px; font-weight: 800; color: #4A3525;")
        
        price = float(data.get('tong_tien', 0))
        price_lbl = QLabel(f"{price:,.0f} đ".replace(",", "."))
        price_lbl.setStyleSheet("font-size: 22px; font-weight: 800; color: #783D19;")
        
        total_layout.addWidget(total_lbl)
        total_layout.addStretch()
        total_layout.addWidget(price_lbl)
        layout.addLayout(total_layout)
        lai = float(data.get('tong_tien', 0)) - tong_von

        add_info_row(
            "💵 Tổng giá vốn",
            f"{tong_von:,.0f} đ".replace(",", "."),
            True,
            "#D9534F"
        )

        add_info_row(
            "📈 Lợi nhuận",
            f"{lai:,.0f} đ".replace(",", "."),
            True,
            "#4E9F3D"
        )
        close_btn = AnimatedButton("ĐÓNG CỬA SỔ", is_primary=True)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    def tinh_gia_von(self, order_id):
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="quanly_snack_db"
            )

            cursor = db.cursor(dictionary=True)

            sql = """
            SELECT
                sp.ten_sanpham,
                ct.so_luong,
                ct.thanh_tien,

                SUM(c.dinh_luong * nl.gia_nhap) AS gia_von_1_mon,

                SUM(c.dinh_luong * nl.gia_nhap) * ct.so_luong AS tong_gia_von

            FROM chitiethoadon ct
            JOIN sanpham sp ON ct.id_sanpham = sp.id
            JOIN congthuc c ON sp.id = c.id_sanpham
            JOIN nguyenlieu nl ON c.id_nguyenlieu = nl.id
            WHERE ct.id_hoadon = %s
            GROUP BY ct.id
            """

            cursor.execute(sql, (order_id,))
            data = cursor.fetchall()

            db.close()
            return data

        except Exception as e:
            print(e)
            return []

# 2. Thẻ hiển thị hóa đơn (Bo góc mượt mà & Đổ bóng nổi 3D Lập thể)
class InvoiceCard(QFrame):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setMinimumHeight(210)
        self.setObjectName("invoiceCard")
        
        # Style Glassmorphism bóng bẩy, bo góc 18px mượt mà
        self.setStyleSheet("""
            QFrame#invoiceCard { 
                background-color: rgba(255, 255, 255, 0.75); 
                border-radius: 18px; 
                border: 1px solid rgba(255, 255, 255, 0.6); 
            }
        """)

        # Tạo hiệu ứng đổ bóng 3D khối lập thể cực sâu
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 6)
        self.shadow.setColor(QColor(139, 126, 116, 40))  
        self.setGraphicsEffect(self.shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 18)
        layout.setSpacing(6)

        # Header: ID & Trạng thái Badge tinh tế
        header = QHBoxLayout()
        id_lbl = QLabel(f"Đơn hàng #{data['id']}")
        id_lbl.setStyleSheet("font-weight: 800; font-size: 15px; color: #4A3525;")
        
        status = data['trang_thai'] or "Chờ xử lý"
        colors = {
            "Đã hoàn thành": ("rgba(78, 159, 61, 0.12)", "#4E9F3D"),
            "Thành công": ("rgba(78, 159, 61, 0.12)", "#4E9F3D"),
            "Đã xong": ("rgba(78, 159, 61, 0.12)", "#4E9F3D"),
            "Đã hủy": ("rgba(219, 83, 79, 0.12)", "#D9534F")
        }
        bg, txt = colors.get(status, ("rgba(230, 126, 34, 0.12)", "#58111A"))
        
        status_lbl = QLabel(status)
        status_lbl.setStyleSheet(f"""
            background-color: {bg}; color: {txt}; 
            padding: 4px 12px; border-radius: 8px; 
            font-size: 11px; font-weight: bold;
        """)
        header.addWidget(id_lbl)
        header.addStretch()
        header.addWidget(status_lbl)

        date_str = data['ngay_tao'].strftime("%d/%m/%Y - %H:%M")
        time_lbl = QLabel(f"📅  {date_str}")
        time_lbl.setStyleSheet("color: #8C7867; font-size: 12px; font-weight: 500;")

        name = data['ten_khach'] if data['ten_khach'] else "Khách vãng lai"
        cust_lbl = QLabel(f"👤  {name}  •  {data['hinh_thuc_tt']}")
        cust_lbl.setStyleSheet("color: #3E2723; font-weight: 700; font-size: 13px; margin-top: 2px;")

        total = float(data['tong_tien'])
        price_lbl = QLabel(f"{total:,.0f} đ".replace(",", "."))
        price_lbl.setStyleSheet("font-size: 20px; font-weight: 800; color: #783D19; margin-top: 2px;")

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(166, 123, 91, 0.1); max-height: 1px; margin-top: 4px;")

        # Footer
        footer = QHBoxLayout()
        items_raw = data['danh_sach_mon'] or ""
        count = len(items_raw.split(',')) if items_raw else 0
        info_lbl = QLabel(f"🛍️  {count} nhóm món ăn")
        info_lbl.setStyleSheet("color: #A67B5B; font-size: 12px; font-weight: 600;")
        
        btn_detail = QPushButton("👁️  Xem chi tiết")
        btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detail.setStyleSheet("""
            QPushButton {
                border: none; background: transparent; color: #A67B5B; 
                font-weight: bold; font-size: 13px; padding: 2px;
            }
            QPushButton:hover { color: #783D19; }
        """)
        btn_detail.clicked.connect(self.show_detail)

        footer.addWidget(info_lbl)
        footer.addStretch()
        footer.addWidget(btn_detail)

        layout.addLayout(header)
        layout.addWidget(time_lbl)
        layout.addWidget(cust_lbl)
        layout.addWidget(price_lbl)
        layout.addWidget(separator)
        layout.addStretch()
        layout.addLayout(footer)

    def enterEvent(self, event):
        # Hiệu ứng di chuột 3D: Đổi màu viền mượt và tăng độ đậm của bóng đổ
        self.setStyleSheet("""
            QFrame#invoiceCard { 
                background-color: rgba(255, 255, 255, 0.9); 
                border-radius: 18px; 
                border: 1px solid rgba(120, 61, 25, 0.4); 
            }
        """)
        self.shadow.setBlurRadius(28)
        self.shadow.setColor(QColor(120, 61, 25, 55))
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Trả lại trạng thái 3D mộc mạc ban đầu
        self.setStyleSheet("""
            QFrame#invoiceCard { 
                background-color: rgba(255, 255, 255, 0.75); 
                border-radius: 18px; 
                border: 1px solid rgba(255, 255, 255, 0.6); 
            }
        """)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(139, 126, 116, 40))
        super().leaveEvent(event)

    def show_detail(self):
        dialog = OrderDetailDialog(self.data, self)
        dialog.exec()


# 3. Trình quản lý danh sách hóa đơn chính
class InvoiceManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống Quản lý Đơn hàng - Cafe & Snack Shop")
        self.resize(1200, 850)
        
        self.setStyleSheet(GLOBAL_STYLE)
        self.setObjectName("MainWindow")

        # Thiết lập màu nền Gradient mịn màng cho toàn app (Tone Cafe sữa đá nhạt)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 1200, 850)
        gradient.setColorAt(0.0, QColor("#F6F3EE"))
        gradient.setColorAt(1.0, QColor("#EEEAE2"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(35, 35, 35, 35)
        self.main_layout.setSpacing(22)

        module_title = QLabel("LỊCH SỬ HÓA ĐƠN HỆ THỐNG ☕")
        module_title.setStyleSheet("font-size: 24px; font-weight: 800; color: #4A3525; letter-spacing: 0.5px;")
        self.main_layout.addWidget(module_title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Nhập mã hóa đơn hoặc tên khách hàng cần tra cứu...")
        self.search_input.setFixedHeight(46)
        self.search_input.textChanged.connect(self.load_data)
        self.main_layout.addWidget(self.search_input)

        # Phân vùng cuộn trong suốt kết hợp style ẩn viền thô ráp
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(24)
        self.grid.setContentsMargins(4, 4, 4, 4)
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.load_data()

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost", user="root", password="", database="quanly_snack_db"
        )

    def load_data(self):
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget: 
                widget.setParent(None)

        try:
            db = self.connect_db()
            cursor = db.cursor(dictionary=True)
            search = f"%{self.search_input.text()}%"
            
            query = "SELECT * FROM chitietdonhang WHERE id LIKE %s OR ten_khach LIKE %s ORDER BY ngay_tao DESC"
            cursor.execute(query, (search, search))
            
            for i, row in enumerate(cursor.fetchall()):
                card = InvoiceCard(row)
                self.grid.addWidget(card, i // 2, i % 2)
            
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể tải danh sách đơn hàng:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ép font mặc định của toàn ứng dụng sang dạng font chữ tròn hiện đại
    font = QFont("Segoe UI")
    if font.fromString("Inter"):
        app.setFont(font)
        
    window = InvoiceManager()
    window.show()
    sys.exit(app.exec())