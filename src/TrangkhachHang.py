import sys
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QLabel, QFrame, QGridLayout, QScrollArea,
                             QDialog, QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPalette, QBrush

# --- HỆ THỐNG STYLE SHEET (GLASSMORPHISM LUXERY CAFE STYLING) ---
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

    /* Thanh tìm kiếm Glassmorphism hiện đại */
    QLineEdit {
        background-color: rgba(255, 255, 255, 0.75);
        border: 1px solid rgba(166, 123, 91, 0.25);
        border-radius: 16px;
        padding: 12px 20px;
        color: #3E2723;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 1px solid #783D19;
        background-color: rgba(255, 255, 255, 0.95);
    }
"""

# --- LỚP NÚT BẤM HOẠT ẢNH MƯỢT MÀ (ANIMATED BUTTON) ---
class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #352015, stop:1 #6B0D0D);
                color: white;
                border-radius: 14px;
                font-weight: bold;
                font-size: 13px;
                border: none;
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


# --- 1. THẺ HIỂN THỊ KHÁCH HÀNG (CARD NỔI 3D LẬP THỂ & HOVER ĐỘNG) ---
class CustomerCard(QFrame):
    def __init__(self, name, phone, rank, orders, points, total_spent, last_purchase):
        super().__init__()
        
        self.data = {
            "name": name if name else "Khách vãng lai",
            "phone": phone if phone else "Không có SĐT",
            "rank": rank, "orders": orders, "points": points,
            "total_spent": total_spent, "last_purchase": last_purchase
        }

        self.setFixedSize(330, 360)
        self.setObjectName("CustomerCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Style Glassmorphism nền mờ ảo, bo góc mịn màng 20px
        self.setStyleSheet("""
            QFrame#CustomerCard {
                background-color: rgba(255, 255, 255, 0.75); 
                border-radius: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.6);
            }
        """)
        
        # Tạo hiệu ứng đổ bóng khối 3D sâu
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(20)
        self.shadow.setOffset(0, 6)
        self.shadow.setColor(QColor(139, 126, 116, 40))  
        self.setGraphicsEffect(self.shadow)
        
        # Định cấu hình màu sắc Badge Hạng thành viên sang trọng
        rank_styles = {
            "VIP": "background-color:#FEE2E2;color:#B91C1C;",
            "Vàng": "background-color:#FEF3C7;color:#B45309;",
            "Bạc": "background-color:#F1F5F9;color:#475569;",
            "Đồng": "background-color:#E7E5E4;color:#78716C;"
        }
        rank_css = rank_styles.get(rank, "background-color: rgba(200, 200, 200, 0.2); color: #666;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 20)
        layout.setSpacing(14)

        # Header Card
        header_layout = QHBoxLayout()
        avatar = QLabel("👤")
        avatar.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #352015, stop:1 #6B0D0D); 
            border-radius: 22px; 
            font-size: 20px;
        """)
        avatar.setFixedSize(44, 44)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        name_label = QLabel(self.data["name"])
        name_label.setStyleSheet("font-weight: 800; font-size: 15px; color: #4A3525; background: transparent;")
        phone_label = QLabel(self.data["phone"])
        phone_label.setStyleSheet("color: #8C7867; font-size: 12px; font-weight: 500; background: transparent;")
        info_layout.addWidget(name_label)
        info_layout.addWidget(phone_label)

        rank_label = QLabel(rank)
        rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_label.setFixedSize(65, 26)
        rank_label.setStyleSheet(rank_css + "border-radius: 10px; font-weight: 800; font-size: 11px;")

        header_layout.addWidget(avatar)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        header_layout.addWidget(rank_label)
        layout.addLayout(header_layout)

        # Body Card
        layout.addWidget(self.create_info_row("📦 Đơn hàng đã đặt", f"{orders} đơn"))
        layout.addWidget(self.create_info_row("⭐ Điểm tích lũy", f"{points} điểm", bg="rgba(166, 123, 91, 0.08)"))
        
        # Vùng tổng chi tiêu khối 3D chìm tinh tế
        spent_frame = QFrame()
        spent_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0.5); border-radius: 12px; border: 1px solid rgba(166, 123, 91, 0.1);")
        spent_layout = QVBoxLayout(spent_frame)
        spent_layout.setContentsMargins(15, 10, 15, 10)
        spent_layout.setSpacing(2)
        
        lbl_title = QLabel("Tổng tích lũy chi tiêu")
        lbl_title.setStyleSheet("color: #8C7867; font-size: 11px; font-weight: 600; background: transparent;")
        spent_value = QLabel(f"{total_spent:,.0f} đ".replace(",", "."))
        spent_value.setStyleSheet("font-size: 22px; font-weight: 800; color: #783D19; background: transparent;")
        
        spent_layout.addWidget(lbl_title)
        spent_layout.addWidget(spent_value)
        layout.addWidget(spent_frame)

        # Footer Card
        last_date = last_purchase.strftime("%d/%m/%Y") if last_purchase else "Chưa có giao dịch"
        footer = QLabel(f"⏱️ Mua hàng lần cuối: {last_date}")
        footer.setStyleSheet("color: #A67B5B; font-size: 11px; font-weight: 500; background: transparent;")
        
        layout.addStretch()
        layout.addWidget(footer)

    def create_info_row(self, label_text, value_text, bg="transparent"):
        frame = QFrame()
        frame.setStyleSheet(f"background-color: {bg}; border-radius: 10px; border: none;")
        row_layout = QHBoxLayout(frame)
        row_layout.setContentsMargins(12, 8, 12, 8)
        
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #5C4033; font-size: 13px; font-weight: 500; background: transparent;")
        val = QLabel(value_text)
        val.setStyleSheet("font-weight: 700; color: #4A3525; background: transparent;")
        
        row_layout.addWidget(lbl)
        row_layout.addStretch()
        row_layout.addWidget(val)
        return frame

    def enterEvent(self, event):
        # Hiệu ứng Tương tác chuột 3D: Đổi màu viền và làm sâu bóng đổ mượt mà
        self.setStyleSheet("""
            QFrame#CustomerCard {
                background-color: rgba(255, 255, 255, 0.95); 
                border-radius: 20px; 
                border: 1px solid rgba(120, 61, 25, 0.35);
            }
        """)
        self.shadow.setBlurRadius(26)
        self.shadow.setColor(QColor(120, 61, 25, 50))
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Trả về trạng thái kính mờ ban đầu
        self.setStyleSheet("""
            QFrame#CustomerCard {
                background-color: rgba(255, 255, 255, 0.75); 
                border-radius: 20px; 
                border: 1px solid rgba(255, 255, 255, 0.6);
            }
        """)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(139, 126, 116, 40))
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = CustomerDetailDialog(self.data, self)
            dialog.exec()


# --- 2. HỘP THOẠI CHI TIẾT HỒ SƠ (GLASSMORPHISM DIALOG LUXURY) ---
class CustomerDetailDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Hồ sơ: {data['name']}")
        self.setFixedSize(460, 540)
        self.setStyleSheet(GLOBAL_STYLE + """
            QDialog {
                background-color: qlineargradient(
                x1:0,y1:0,x2:0,y2:1,
                stop:0 #FFFFFF,
                stop:1 #F8FAFC
            );
                border-radius: 24px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(16)
        
        title = QLabel("HỒ SƠ THÀNH VIÊN")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #4A3525; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Thanh phân cách mờ tinh tế
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(166, 123, 91, 0.25); max-height: 1px;")
        layout.addWidget(sep)

        # Khối hiển thị thông tin phân tầng sắc nét dạng Kính mờ thay cho QTextEdit cũ
        info_container = QFrame()
        info_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.6);
                border: 1px solid rgba(166, 123, 91, 0.15);
                border-radius: 16px;
            }
            QLabel { background: transparent; border: none; }
        """)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(14)

        def add_detail_row(icon_text, label, value, is_highlight=False):
            row = QHBoxLayout()
            lbl = QLabel(f"{icon_text}  {label}:")
            lbl.setStyleSheet("color: #8C7867; font-size: 13px; font-weight: 600;")
            val = QLabel(str(value))
            if is_highlight:
                val.setStyleSheet("font-size: 16px; font-weight: 800; color: #783D19;")
            else:
                val.setStyleSheet("font-size: 13px; font-weight: 700; color: #4A3525;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            info_layout.addLayout(row)

        last_date = data['last_purchase'].strftime("%d/%m/%Y %H:%M") if data['last_purchase'] else "Chưa có dữ liệu"
        
        add_detail_row("👤", "Họ tên khách hàng", data['name'])
        add_detail_row("📞", "Số điện thoại", data['phone'])
        add_detail_row("🏆", "Hạng thành viên", data['rank'])
        add_detail_row("⭐", "Điểm tích lũy hiện tại", f"{data['points']} điểm")
        add_detail_row("📦", "Tổng số đơn hàng đặt", f"{data['orders']} đơn")
        add_detail_row("💰", "Tổng chi tiêu tích lũy", f"{data['total_spent']:,.0f} đ".replace(",", "."), is_highlight=True)
        add_detail_row("📅", "Thời gian mua gần nhất", last_date)

        layout.addWidget(info_container)

        note_lbl = QLabel("ℹ️ Dữ liệu hồ sơ thành viên đồng bộ thời gian thực từ hệ thống.")
        note_lbl.setStyleSheet("color: #A67B5B; font-size: 11px; font-style: italic;")
        note_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note_lbl)

        btn_close = AnimatedButton("ĐÓNG CỬA SỔ")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)


# --- 3. TRÌNH QUẢN LÝ DANH SÁCH KHÁCH HÀNG CHÍNH ---
class CustomerManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hệ thống Quản lý Khách hàng -  Snack Shop")
        self.resize(1150, 850)
        self.setStyleSheet(GLOBAL_STYLE)

        # Đổ màu nền Gradient mịn màng cho toàn Module (Tone Latte nhẹ nhàng)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 1150, 850)
        gradient.setColorAt(0.0, QColor("#F8FAFC"))
        gradient.setColorAt(1.0, QColor("#EEF2F7"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(35, 35, 35, 35)
        self.main_layout.setSpacing(20)

        title = QLabel("QUẢN LÝ DỮ LIỆU KHÁCH HÀNG 👥")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #4A3525; letter-spacing: 0.5px;")
        self.main_layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Nhập danh tính, họ tên hoặc số điện thoại khách hàng cần tra cứu...")
        self.search_input.setFixedHeight(46)
        self.search_input.textChanged.connect(self.load_data)
        self.main_layout.addWidget(self.search_input)

        # Cấu hình vùng cuộn trong suốt tinh tế ẩn viền thô ráp
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(24)
        self.grid_layout.setContentsMargins(4, 4, 4, 4)
        
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.load_data()

    def connect_db(self):
        return mysql.connector.connect(
            host="localhost", user="root", password="", database="quanly_snack_db"
        )

    def load_data(self):
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget: 
                widget.setParent(None)

        search_text = self.search_input.text()
        
        try:
            db = self.connect_db()
            cursor = db.cursor(dictionary=True)
            
            query = """
                SELECT 
                    k.id, 
                    k.ten_khachhang, 
                    k.so_dien_thoai, 
                    k.diem_tich_luy,
                    COUNT(d.id) as so_don_hang, 
                    IFNULL(SUM(d.tong_tien), 0) as tong_chi_tieu,
                    MAX(d.ngay_tao) as ngay_mua_cuoi
                FROM khachhang k
                LEFT JOIN chitietdonhang d ON k.so_dien_thoai = d.sdt_khach
                WHERE k.ten_khachhang LIKE %s OR k.so_dien_thoai LIKE %s
                GROUP BY k.id
                ORDER BY ngay_mua_cuoi DESC, k.id DESC
            """
            val = (f"%{search_text}%", f"%{search_text}%")
            cursor.execute(query, val)
            
            for i, row in enumerate(cursor.fetchall()):
                spent = float(row['tong_chi_tieu'])
                
                # Phân cấp danh hiệu Khách hàng chuyên nghiệp
                rank = "Đồng"
                if spent > 2000000: rank = "VIP"
                elif spent > 1000000: rank = "Vàng"
                elif spent > 500000: rank = "Bạc"

                card = CustomerCard(
                    row['ten_khachhang'], 
                    row['so_dien_thoai'], 
                    rank, 
                    row['so_don_hang'], 
                    row['diem_tich_luy'], 
                    spent, 
                    row['ngay_mua_cuoi']
                )
                # Bố trí đều đặn 3 cột trên một hàng ngang
                self.grid_layout.addWidget(card, i // 3, i % 3)

            db.close()
        except Exception as e:
            print(f"Lỗi truy vấn hệ thống dữ liệu: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Ép phông chữ mặc định sang dạng font không chân hình khối tròn bo mịn
    font = QFont("Segoe UI")
    if font.fromString("Inter"):
        app.setFont(font)
        
    window = CustomerManagement()
    window.show()
    sys.exit(app.exec())