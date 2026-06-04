
import sys
import mysql.connector
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QGraphicsDropShadowEffect, QPushButton, QStackedWidget, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QColor, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

try:
    from quanlysanpham import ProductManager  
    from Tranghoadon import InvoiceManager    
    from Trangbanhang import SnackShopPOS      
    from Trangbaocao import ReportManager
    from TrangkhachHang import CustomerManagement 
    from Trangquanlydonhang import OrderManagementApp 
    from TrangKho import WarehouseApp 
    from Quanlychamcong import AttendanceManagement
except ImportError as e:
    print(f"⚠️ Cảnh báo: Thiếu file giao diện con: {e}")

# STYLE SHEET THANH CUỘN (Tone màu đỏ mận mảnh dẻ)
SCROLLBAR_STYLE = """
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: rgba(88, 17, 26, 0.15);
    min-height: 40px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(88, 17, 26, 0.3);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none; background: none;
}
"""

# ==========================================================
# THÀNH PHẦN UI HỖ TRỢ (PREMIUM MINIMALIST CARD)
# ==========================================================
class ModernGlassCard(QFrame):
    """Thẻ viền mảnh tối giản cao cấp, bóng đổ mịn màng nghệ thuật"""
    def __init__(self, bg_color="#FFFFFF", radius=16, parent=None):
        super().__init__(parent)
        self.bg_color = bg_color
        self.radius = radius
        
        # Viền mảnh bo góc nhẹ nhàng như form nhập liệu của ảnh mẫu
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.bg_color};
                border: 1px solid rgba(88, 17, 26, 0.08);
                border-radius: {self.radius}px;
            }}
        """)
        
        # Đổ bóng vùng mờ lớn nhưng độ đậm cực thấp, giữ nền trắng sạch sẽ
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(25)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(6)
        self.shadow.setColor(QColor(88, 17, 26, 12)) 
        self.setGraphicsEffect(self.shadow)
        
    def enterEvent(self, event):
        """Hiệu ứng phản hồi nhẹ khi di chuột"""
        self.shadow.setBlurRadius(35)
        self.shadow.setYOffset(10)
        self.shadow.setColor(QColor(88, 17, 26, 22))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shadow.setBlurRadius(25)
        self.shadow.setYOffset(6)
        self.shadow.setColor(QColor(88, 17, 26, 12))
        super().leaveEvent(event)


class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def plot(self, data, labels):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor='none')
        
        # Đường biểu diễn màu Đỏ mận chủ đạo #58111A
        ax.plot(labels, data, linewidth=3, color="#58111A", marker='o', 
                markersize=6, markerfacecolor="white", markeredgewidth=2)
        
        # Đổ vùng màu gradient mờ phía dưới đường biểu diễn
        ax.fill_between(labels, data, alpha=0.06, color="#58111A")
        
        ax.set_title("XU HƯỚNG DOANH THU TRONG NGÀY", fontsize=10, fontweight='bold', color="#58111A", pad=15)
        ax.grid(True, linestyle=":", alpha=0.3, color="#58111A")
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        rgba_color = (88/255, 17/255, 26/255, 0.15) 
        ax.spines['left'].set_color(rgba_color)
        ax.spines['bottom'].set_color(rgba_color)
        
        ax.tick_params(colors='#58111A', labelsize=9)
        ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        self.figure.tight_layout()
        self.canvas.draw()


# ==========================================================
# GIAO DIỆN CHÍNH (MAIN INTERFACE)
# ==========================================================
class GiaoDienChinh(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        
        self.user_info = user_info or {"id": 5, "ho_ten": "Nhân viên", "vai_tro": "Nhân viên"}
        self.nhanvien_id = self.user_info.get('id', 5)
        
        self.setWindowTitle(f"Snack Shop POS - {self.user_info['ho_ten']}")
        self.setMinimumSize(1150, 780)
        
        # Nền phải màu trắng sữa mềm mại tiệp màu nền Đăng nhập
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI Variable", "Segoe UI", "Inter", sans-serif;
            }
            GiaoDienChinh {
                background-color: #FAFAFA;
            }
        """)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar_frame = QFrame()
        self.content_stack = QStackedWidget() 
        self.content_stack.setStyleSheet("background: transparent;")

        self.init_sidebar()
        self.init_pages()

        self.main_layout.addWidget(self.sidebar_frame)
        self.main_layout.addWidget(self.content_stack, 1)

        # Điều hướng mặc định đến tab Chấm công
        self.content_stack.setCurrentIndex(8)
        for btn in self.buttons:
            if "Chấm công" in btn.text():
                btn.setChecked(True)
            else:
                btn.setChecked(False)

        self.load_dashboard_data()

    def connect_db(self):
        try:
            return mysql.connector.connect(host="localhost", user="root", password="", database="quanly_snack_db")
        except Exception: 
            return None

    def init_sidebar(self):
        self.sidebar_frame.setFixedWidth(270)
        # Sidebar phẳng phẳng lì, không bo góc phải, màu đỏ mận sâu nguyên khối (#4A0E14)
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #4A0E14; 
                border: none;
            }
        """)
        layout = QVBoxLayout(self.sidebar_frame)
        layout.setContentsMargins(20, 45, 20, 25)

        # Gắn thương hiệu Typography chuẩn từ hình ảnh minh họa
        logo = QLabel("THE SNACK SHOP.")
        logo.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 40px; margin-left: 12px;")
        layout.addWidget(logo)

        menu_items = [
            ("🏠   Tổng quan", 0), 
            ("🛒   Bán hàng", 3), 
            ("🍕   Thực đơn", 1), 
            ("📄   Đơn hàng", 6), 
            ("👥   Khách hàng", 5),
            ("📦   Kho hàng", 7),
            ("📋   Chấm công", 8)
        ]

        self.buttons = []
        for text, index in menu_items:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Phối màu nút: Chữ hồng mận nhạt -> Khi được chọn đổi sang màu Đỏ mận đậm trên nền trắng kem sạch
            btn.setStyleSheet("""
                QPushButton {
                    color: #E0B0B4;  
                    border: none; 
                    padding-left: 20px;
                    text-align: left; 
                    border-radius: 12px; 
                    font-weight: 600;
                    font-size: 14px;
                    background-color: transparent;
                }
                QPushButton:hover { 
                    background-color: rgba(255, 255, 255, 0.08);
                    color: #FFFFFF;
                }
                QPushButton:checked { 
                    background-color: #FDF4F5; 
                    color: #58111A; 
                    font-weight: 700;
                }
            """)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        # Nút đăng xuất tinh gọn ở đáy menu sidebar
        btn_logout = QPushButton("🚪   Đăng xuất")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setFixedHeight(45)
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05); 
                color: #F5E6E8; 
                border-radius: 12px; 
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { 
                background-color: #962D37; 
                color: #FFFFFF; 
            }
        """)
        btn_logout.clicked.connect(self.handle_logout) 
        layout.addWidget(btn_logout)

    def switch_page(self, index):
        self.content_stack.setCurrentIndex(index)
        if index == 0: 
            self.load_dashboard_data()
        if index == 7:
            try: self.content_stack.widget(7).load_data()
            except: pass

    def init_pages(self):
        self.page_dashboard = QWidget()
        self.setup_dashboard_content(self.page_dashboard)
        self.content_stack.addWidget(self.page_dashboard)
        
        widgets = [
            ProductManager, InvoiceManager, SnackShopPOS, ReportManager,
            CustomerManagement, OrderManagementApp, WarehouseApp, AttendanceManagement
        ]
        
        for widget_class in widgets:
            try:
                if widget_class in [SnackShopPOS, WarehouseApp, AttendanceManagement]:
                    instance = widget_class(self.user_info)
                else:
                    instance = widget_class()
                self.content_stack.addWidget(instance)
            except Exception as e:
                print(f"Lỗi khởi tạo trang {widget_class.__name__}: {e}")
                error_lbl = QLabel(f"Lỗi tải giao diện: {widget_class.__name__}")
                error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_stack.addWidget(error_lbl)

    def setup_dashboard_content(self, target_widget):
        layout = QVBoxLayout(target_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Tiêu đề Header
        self.welcome_lbl = QLabel(f"Chào mừng trở lại, {self.user_info['ho_ten']}! 👋")
        self.welcome_lbl.setStyleSheet("font-size: 24px; font-weight: 700; color: #4A0E14; letter-spacing: -0.5px;")
        layout.addWidget(self.welcome_lbl)
        
        # Thẻ thông tin nhanh (Stats)
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(25)
        layout.addLayout(self.stats_layout)

        # Khu vực biểu đồ & Đơn hàng
        body = QHBoxLayout()
        body.setSpacing(25)
        
        self.chart_card = ModernGlassCard(bg_color="#FFFFFF")
        v_chart = QVBoxLayout(self.chart_card)
        v_chart.setContentsMargins(20, 20, 20, 20)
        self.chart = ChartWidget()
        v_chart.addWidget(self.chart)
        body.addWidget(self.chart_card, 65)

        self.recent_order_card = ModernGlassCard(bg_color="#FFFFFF")
        v_order_wrapper = QVBoxLayout(self.recent_order_card)
        v_order_wrapper.setContentsMargins(22, 22, 22, 22)
        
        title_order = QLabel("🧾 ĐƠN HÀNG GẦN ĐÂY")
        title_order.setStyleSheet("font-weight: 700; color: #4A0E14; font-size: 12px; letter-spacing: 0.5px;")
        v_order_wrapper.addWidget(title_order)
        
        scroll = QScrollArea()
        scroll.setStyleSheet(SCROLLBAR_STYLE)
        scroll.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.v_order_list = QVBoxLayout(scroll_content)
        self.v_order_list.setContentsMargins(0, 10, 0, 0)
        self.v_order_list.setSpacing(12)
        self.v_order_list.addStretch()
        
        scroll.setWidget(scroll_content)
        v_order_wrapper.addWidget(scroll)
        body.addWidget(self.recent_order_card, 35)
        
        layout.addLayout(body)

    def load_dashboard_data(self):
        db = self.connect_db()
        if not db: return
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT COUNT(*) as sl, SUM(tong_tien) as tt 
                FROM chitietdonhang 
                WHERE id_nhanvien = %s AND DATE(ngay_tao) = CURDATE() AND trang_thai = 'Đã hoàn thành'
            """, (self.nhanvien_id,))
            res = cursor.fetchone()
            
            while self.stats_layout.count(): 
                self.stats_layout.takeAt(0).widget().deleteLater()
                
            self.add_stat_card("ĐƠN HOÀN THÀNH", str(res['sl'] or 0), "🛒", "#58111A")
            self.add_stat_card("DOANH THU CỦA TÔI", f"{float(res['tt'] or 0):,.0f}đ", "💰", "#A8202E")

            cursor.execute("""
                SELECT HOUR(ngay_tao) as gio, SUM(tong_tien) as tien 
                FROM chitietdonhang 
                WHERE id_nhanvien = %s AND DATE(ngay_tao) = CURDATE() AND trang_thai = 'Đã hoàn thành'
                GROUP BY HOUR(ngay_tao) ORDER BY gio ASC
            """, (self.nhanvien_id,))
            data = cursor.fetchall()
            h = [f"{d['gio']}h" for d in data] if data else ["0h"]
            r = [float(d['tien']) for d in data] if data else [0]
            self.chart.plot(r, h)

            while self.v_order_list.count() > 1:
                child = self.v_order_list.takeAt(0)
                if child.widget(): child.widget().deleteLater()

            cursor.execute("""
                SELECT id, ten_khach, tong_tien, ngay_tao FROM chitietdonhang 
                WHERE id_nhanvien = %s ORDER BY ngay_tao DESC LIMIT 5
            """, (self.nhanvien_id,))
            
            for d in cursor.fetchall():
                row = QFrame()
                row.setStyleSheet("""
                    QFrame {
                        background-color: #FCF9F9;
                        border-radius: 10px;
                        border: 1px solid rgba(88, 17, 26, 0.06);
                    }
                """)
                v = QVBoxLayout(row)
                v.setContentsMargins(12, 12, 12, 12)
                
                lbl_top = QLabel(f"<b>#{d['id']}</b> — {d['ngay_tao'].strftime('%H:%M')}")
                lbl_top.setStyleSheet("color: #962D37; font-size: 11px;")
                lbl_bot = QLabel(f"{d['ten_khach'] or 'Khách vãng lai'}  |  <b>{float(d['tong_tien']):,.0f}đ</b>")
                lbl_bot.setStyleSheet("color: #4A0E14; font-size: 13px;")
                
                v.addWidget(lbl_top)
                v.addWidget(lbl_bot)
                self.v_order_list.insertWidget(self.v_order_list.count()-1, row)
            db.close()
        except Exception as e: 
            print(f"Lỗi Dashboard: {e}")

    def add_stat_card(self, title, val, icon, color):
        card = ModernGlassCard(bg_color="#FFFFFF")
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 20, 20, 20)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 26px; color: {color};")
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #A0787C; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
        
        val_lbl = QLabel(val)
        val_lbl.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {color}; margin-top: 4px;")
        
        v.addWidget(icon_lbl)
        v.addWidget(title_lbl)
        v.addWidget(val_lbl)
        self.stats_layout.addWidget(card)

    def handle_logout(self):
        reply = QMessageBox.question(
            self, 'Xác nhận đăng xuất',
            'Bạn có chắc chắn muốn rời phiên làm việc này không?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from login import SnackShopLogin
                self.login_window = SnackShopLogin()
                self.login_window.showMaximized()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể quay lại màn hình đăng nhập:\n{e}")
                return
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI Variable", 10))
    window = GiaoDienChinh()
    window.showMaximized()
    window.show()
    sys.exit(app.exec())

