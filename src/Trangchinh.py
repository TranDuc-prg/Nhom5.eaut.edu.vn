import sys
import mysql.connector
import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QGraphicsDropShadowEffect, QPushButton, QStackedWidget, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPalette

# Thử import các thư viện biểu đồ
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvas = None
    print("⚠️ Cảnh báo: Thiếu thư viện matplotlib để hiển thị biểu đồ.")

try:
    from quanlysanpham import ProductManager  
    from Tranghoadon import InvoiceManager    
    from Trangbanhang import SnackShopPOS      
    from Trangbaocao import ReportManager
    from TrangkhachHang import CustomerManagement 
    from Trangquanlydonhang import OrderManagementApp 
    from Quanlynguoidung import UserManager      
    from login import SnackShopLogin
    from Quanlychamcong import AttendanceManagement
    from TrangKho import WarehouseApp  
except ImportError as e:
    print(f"⚠️ Cảnh báo: Thiếu file giao diện con: {e}")

# ==========================================================
# GIAO DIỆN HỆ THỐNG TOÀN CỤC (STYLESHEET TRANG TRÍ LUXURY)
# ==========================================================
LUXURY_STYLE = """
    /* Cấu hình chung font chữ hiện đại */
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Thiết kế thanh cuộn mượt mà tone xám hồng mờ tinh tế */
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 6px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: rgba(144, 41, 54, 0.2); /* Màu đỏ đô nhạt mờ */
        min-height: 40px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical:hover {
        background: rgba(144, 41, 54, 0.6);
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    QScrollBar:horizontal {
        border: none;
        background: transparent;
        height: 6px;
    }
    QScrollBar::handle:horizontal {
        background: rgba(144, 41, 54, 0.2);
        border-radius: 3px;
    }
"""

# ==========================================================
# CARD NỔI 3D GLASSMORPHISM
# ==========================================================
class GlassCard3D(QFrame):
    def __init__(self, radius=24, parent=None):
        super().__init__(parent)
        # Nền kính bán trong suốt kết hợp viền mờ sang trọng
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 255, 255, 0.75);
                border: 1px solid rgba(232, 220, 221, 0.6);
                border-radius: {radius}px;
            }}
        """)
        
        # Đổ bóng tạo hiệu ứng chiều sâu 3D (Khối nổi)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(35)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(12)
        self.shadow.setColor(QColor(88, 17, 26, 20))  # Bóng đổ màu Espresso ấm áp nhạt
        self.setGraphicsEffect(self.shadow)

# ==========================================================
# BIỂU ĐỒ DOANH THU CAFE SANG TRỌNG
# ==========================================================
class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        if FigureCanvas is None:
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Biểu đồ không khả dụng (Thiếu Matplotlib)"))
            return
        # Tạo biểu đồ với nền trong suốt khớp Glassmorphism
        self.figure = Figure(figsize=(6, 4), dpi=100, facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, data, labels):
        if FigureCanvas is None: return
        self.figure.clear()
        
        ax = self.figure.add_subplot(111, facecolor='none')
        # Đường line màu đỏ rượu vang mượt mà
        ax.plot(labels, data, linewidth=3.5, color="#902936", marker='o', 
                markersize=7, markerfacecolor="#FFFFFF", markeredgewidth=2.5, markeredgecolor="#902936")
        
        # Đổ vùng màu Gradient mềm mại phía dưới đường tuyến tính
        ax.fill_between(labels, data, alpha=0.15, color="#58111A")
        for i, val in enumerate(data):
            if val > 0:
                display_text = f"{val/1000:,.0f}k" if val >= 1000 else f"{val:,.0f}"
                ax.annotate(display_text, (labels[i], data[i]), textcoords="offset points", 
                            xytext=(0, 12), ha='center', fontsize=9, fontweight='bold', color="#2C1316")

        ax.get_yaxis().set_visible(False)
        ax.grid(True, linestyle=":", alpha=0.3, color="#E8DCDD")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # Đồng bộ màu đường biên dưới theo màu đỏ rượu thẫm mờ
        ax.spines['bottom'].set_color((88/255, 17/255, 26/255, 0.2))
        ax.tick_params(colors='#8A7678', labelsize=9)
        
        self.figure.tight_layout()
        self.canvas.draw()

# ==========================================================
# GIAO DIỆN CHÍNH (MAIN DASHBOARD LUXURY)
# ==========================================================
class GiaoDienChinh(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        
        if user_info is not None:
            self.user_info = user_info
        else:
            self.user_info = {
                "id": 5, 
                "ho_ten": "Hệ thống Quản lý", 
                "vai_tro": "Quản trị viên"
            }
        
        self.setWindowTitle(f"Hệ thống POS Luxury Snack - {self.user_info.get('ho_ten', 'Admin')}")
        self.setMinimumSize(1200, 800)
        # Cấu hình bảng màu đỏ đô đồng bộ cục bộ để dễ truy vấn
        self.color_wine_dark = "#58111A"       # Đỏ đô đậm chủ đạo
        self.color_bg_main = "#FDFBF9"         # Nền trắng ngà ánh hồng
        self.color_text_dark = "#2C1316"       # Màu chữ cốt lõi
        self.color_text_muted = "#8A7678"      # Màu nhãn và chữ phụ
        self.color_accent = "#902936"          # Màu đỏ đô sáng nhung quý phái
        # Thiết lập bộ stylesheet luxury toàn cục cho ứng dụng
        self.setStyleSheet(LUXURY_STYLE)

        # Layout chính phân tách Sidebar và Content vùng làm việc
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Widget đệm để tạo background gradient lãng mạn cho quán cafe hoàng hôn
        self.bg_frame = QFrame(self)
        self.bg_frame.setObjectName("BgFrame")
        self.bg_frame.setStyleSheet("""
            QFrame#BgFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #FFFDFC, stop:0.5 #FAF5F2, stop:1 #F3EAE6);
            }
        """)
        
        self.bg_layout = QHBoxLayout(self.bg_frame)
        self.bg_layout.setContentsMargins(0, 0, 0, 0)
        self.bg_layout.setSpacing(0)

        self.sidebar_frame = QFrame()
        self.content_stack = QStackedWidget() 

        self.init_sidebar()
        self.init_pages()

        self.bg_layout.addWidget(self.sidebar_frame)
        self.bg_layout.addWidget(self.content_stack)
        self.main_layout.addWidget(self.bg_frame)

        self.load_dashboard_data()

    def connect_db(self):
        try:
            return mysql.connector.connect(
                host="localhost", user="root", password="", database="quanly_snack_db"
            )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi kết nối", f"Không thể kết nối Database: {e}")
            return None

    def init_sidebar(self):
        self.sidebar_frame.setFixedWidth(280)
        # Thiết kế thanh Sidebar màu Gỗ Mun hoàng gia đậm sâu thẳm sắc nét
        self.sidebar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color_wine_dark};
                border-top-right-radius: 30px;
                border-bottom-right-radius: 30px;
            }}
        """)
        
        layout = QVBoxLayout(self.sidebar_frame)
        layout.setContentsMargins(25, 45, 25, 30)
        layout.setSpacing(8)

        logo = QLabel("👑 LUXURY POS")
        logo.setStyleSheet("color: #F3EAE6; font-size: 24px; font-weight: 900; letter-spacing: 2px; margin-bottom: 35px;")
        layout.addWidget(logo)

        menu_items = [
            ("📊 Tổng quan Dashboard", 0), 
            ("🍿 Quản lý Sản phẩm", 1), 
            ("📄 Quản lý Hóa đơn", 2),
            ("👑 Trực quan Bán hàng", 3), 
            ("📈 Báo cáo Doanh thu", 4), 
            ("👥 Hồ sơ Khách hàng", 5),
            ("🚚 Điều phối Đơn hàng", 6), 
            ("🔐 Tài khoản Hệ thống", 7), 
            ("📦 Quản lý Kho hàng", 8)
        ]

        vai_tro = str(self.user_info.get('vai_tro', "")).lower().strip()
        if "admin" in vai_tro or "quản" in vai_tro:
            menu_items.append(("📋 Chấm công Nhân viên", 9))

        self.buttons = []
        for text, index in menu_items:
            btn = QPushButton(text)
            btn.setFixedHeight(50)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Phong cách nút menu bo góc mượt, hiệu ứng hover nhẹ nhàng sang trọng
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: #CBB9BA; border: none; padding-left: 20px;
                    font-size: 14px; font-weight: 500; text-align: left; border-radius: 16px;
                    background-color: transparent;
                }}
                QPushButton:hover {{ 
                    color: #FFFFFF;
                    background-color: rgba(255, 255, 255, 0.08); 
                }}
                QPushButton:checked {{ 
                    color: #FFFFFF; 
                    background-color: {self.color_accent}; 
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            layout.addWidget(btn)
            self.buttons.append(btn)

        if self.buttons: 
            self.buttons[0].setChecked(True)
            
        layout.addStretch()

        btn_logout = QPushButton("🚪 Đăng xuất")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                color: #FFAEBA; border: none; text-align: left; 
                padding: 12px 20px; font-size: 14px; font-weight: bold; border-radius: 12px;
            }
            QPushButton:hover { color: #FFF; background-color: rgba(255, 174, 186, 0.15); }
        """)
        btn_logout.clicked.connect(self.handle_logout) 
        layout.addWidget(btn_logout)

    # Hiệu ứng chuyển trang Animation mượt mà nhịp nhàng quý phái (Fade out / Fade In)
    def switch_page(self, index):
        current_widget = self.content_stack.currentWidget()
        next_widget = self.content_stack.widget(index)
        
        if current_widget == next_widget:
            return

        # Hiệu ứng mờ dần và hiện rõ mượt mà quyến rũ
        self.anim = QPropertyAnimation(self.content_stack, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        def finish_fade():
            self.content_stack.setCurrentIndex(index)
            if index == 0:
                self.load_dashboard_data()
            self.anim_back = QPropertyAnimation(self.content_stack, b"windowOpacity")
            self.anim_back.setDuration(300)
            self.anim_back.setStartValue(0.0)
            self.anim_back.setEndValue(1.0)
            self.anim_back.start()

        self.anim.finished.connect(finish_fade)
        self.anim.start()

    def init_pages(self):
        # 0. Dashboard (Khởi tạo trang chủ chính)
        self.page_dashboard = QWidget()
        self.setup_dashboard_content(self.page_dashboard)
        self.content_stack.addWidget(self.page_dashboard)

        # Danh sách các trang quản trị nghiệp vụ con
        widgets = [
            ProductManager, InvoiceManager, SnackShopPOS, ReportManager,
            CustomerManagement, OrderManagementApp, UserManager, WarehouseApp, AttendanceManagement
        ]
        
        for widget_class in widgets:
            try:
                pages_need_user = [SnackShopPOS, WarehouseApp, AttendanceManagement, UserManager]
                if widget_class in pages_need_user:
                    instance = widget_class(user_info=self.user_info)
                else:
                    instance = widget_class()
                self.content_stack.addWidget(instance)
            except Exception as e:
                lbl = QLabel(f"🌟 Module {widget_class.__name__} đang đồng bộ...")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: #8B5E3C; font-style: italic;")
                self.content_stack.addWidget(lbl)

    def handle_logout(self):
        reply = QMessageBox.question(
            self, "Xác nhận", "Bạn có thực sự muốn rời khỏi phiên làm việc?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                from login import SnackShopLogin   
                self.login_window = SnackShopLogin()
                self.login_window.show()
            except:
                pass
            self.close()

    def setup_dashboard_content(self, target_widget):
        # Sử dụng Scroll Area ẩn để giao diện luôn co giãn tốt trên mọi độ phân giải màn hình
        scroll = QScrollArea(target_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(35)

        # Tiêu đề lời chào thượng lưu lịch lãm
        welcome = QLabel(f"Xin chào buổi sáng, {self.user_info['ho_ten']} ✨")
        welcome.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {self.color_text_dark}; letter-spacing: -0.5px;")
        layout.addWidget(welcome)
        
        # Khối hiển thị thẻ thống kê nhanh hàng đầu
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(25)
        layout.addLayout(self.stats_layout)

        # Thân cấu trúc Dashboard chia cột tỉ lệ (65% Biểu đồ - 35% Top Sản phẩm)
        body = QHBoxLayout()
        body.setSpacing(25)
        layout.addLayout(body)

        self.chart_card = GlassCard3D()
        chart_vbox = QVBoxLayout(self.chart_card)
        chart_vbox.setContentsMargins(25, 25, 25, 25)
        
        chart_title = QLabel("📊 Xu hướng doanh thu tuần này")
        chart_title.setStyleSheet(f"font-weight: bold; font-size: 18px; color: {self.color_text_dark};")
        chart_vbox.addWidget(chart_title)
        
        self.chart = ChartWidget()
        chart_vbox.addWidget(self.chart)
        body.addWidget(self.chart_card, 2)

        self.top_card = GlassCard3D()
        top_vbox = QVBoxLayout(self.top_card)
        top_vbox.setContentsMargins(25, 25, 25, 25)
        
        top_title = QLabel("🏆 Best Seller trong ngày")
        top_title.setStyleSheet(f"font-weight: bold; font-size: 18px; color: {self.color_text_dark};")
        top_vbox.addWidget(top_title)
        
        self.top_list_layout = QVBoxLayout()
        self.top_list_layout.setSpacing(12)
        top_vbox.addLayout(self.top_list_layout)
        top_vbox.addStretch()
        body.addWidget(self.top_card, 1)

        # Đơn hàng mới phát sinh gần đây nhất
        self.recent_order_card = GlassCard3D()
        self.v_order_list = QVBoxLayout(self.recent_order_card)
        self.v_order_list.setContentsMargins(25, 25, 25, 25)
        
        order_title = QLabel("📝 Tiến trình đơn hàng Realtime")
        order_title.setStyleSheet(f"font-weight: bold; font-size: 18px; color: {self.color_text_dark};")
        self.v_order_list.addWidget(order_title)
        
        layout.addWidget(self.recent_order_card)
        layout.addStretch()
        
        scroll.setWidget(scroll_content)
        
        main_target_layout = QVBoxLayout(target_widget)
        main_target_layout.setContentsMargins(0,0,0,0)
        main_target_layout.addWidget(scroll)

    def load_dashboard_data(self):
        db = self.connect_db()
        if not db: return
            
        try:
            cursor = db.cursor(dictionary=True, buffered=True)

            # --- 1. THỐNG KÊ DOANH THU NHANH ---
            cursor.execute("SELECT SUM(tong_tien) as total FROM chitietdonhang")
            res_total = cursor.fetchone()
            revenue = float(res_total['total']) if res_total and res_total['total'] else 0.0
            
            cursor.execute("SELECT COUNT(id) as count FROM chitietdonhang WHERE DATE(ngay_tao) = CURDATE()")
            orders_today = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(id) as count FROM sanpham WHERE so_luong_ton < 10")
            low_stock_count = cursor.fetchone()['count']

            self.update_stats_ui([
                ("Doanh thu tích lũy", f"{revenue:,.0f} đ", "💰"),
                ("Đơn phục vụ hôm nay", str(orders_today) + " đơn", "☕"),
                ("Nguyên liệu sắp hết", f"{low_stock_count} mục", "⚠️") 
            ])

            # --- 2. VẼ ĐƯỜNG CONG BIỂU ĐỒ ---
            today = datetime.date.today()
            dates = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
            stats = {d.strftime('%Y-%m-%d'): 0 for d in dates}
            
            cursor.execute("""
                SELECT DATE(ngay_tao) as d, SUM(tong_tien) as t 
                FROM chitietdonhang 
                WHERE ngay_tao >= CURDATE() - INTERVAL 6 DAY 
                GROUP BY DATE(ngay_tao)
            """)
            for row in cursor.fetchall():
                date_key = str(row['d'])
                if date_key in stats:
                    stats[date_key] = float(row['t'])
            
            if hasattr(self, 'chart'):
                self.chart.plot(list(stats.values()), [d.strftime('%d/%m') for d in dates])

            # --- 3. ĐỌC DANH SÁCH SẢN PHẨM PHỔ BIẾN ---
            while self.top_list_layout.count():
                child = self.top_list_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
            
            cursor.execute("SELECT danh_sach_mon FROM chitietdonhang")
            all_orders = cursor.fetchall()
            product_counts = {}

            for order in all_orders:
                raw_str = order['danh_sach_mon']
                if not raw_str: continue
                items = raw_str.split(', ')
                for item in items:
                    try:
                        if 'x ' in item:
                            parts = item.split('x ', 1)
                            qty = int(parts[0])
                            name = parts[1].strip()
                            product_counts[name] = product_counts.get(name, 0) + qty
                    except:
                        continue

            top_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            if not top_products:
                no_data = QLabel("Chưa ghi nhận dữ liệu bán lẻ")
                no_data.setStyleSheet(f"color: {self.color_text_muted}; font-style: italic;")
                self.top_list_layout.addWidget(no_data)
            else:
                for i, (name, total) in enumerate(top_products, 1):
                    lbl = QLabel(f"🏆  {name}  —  {total} ly")
                    lbl.setStyleSheet(f"""
                        font-size: 14px; color: {self.color_text_dark}; font-weight: 500;
                        padding: 10px; border-bottom: 1px dashed rgba(88, 17, 26, 0.15);
                    """)
                    self.top_list_layout.addWidget(lbl)

            # --- 4. HÓA ĐƠN TRỰC TUYẾN GẦN ĐÂY ---
            while self.v_order_list.count() > 1:
                child = self.v_order_list.takeAt(1)
                if child.widget(): child.widget().deleteLater()

            cursor.execute("SELECT id, ten_khach, tong_tien, ngay_tao, trang_thai FROM chitietdonhang ORDER BY ngay_tao DESC LIMIT 4")
            
            for order in cursor.fetchall():
                name = order['ten_khach'] or "Khách vãng lai"
                status = order['trang_thai'] or "Đã thanh toán"
                time_str = order['ngay_tao'].strftime('%H:%M')
                amount = float(order['tong_tien']) if order['tong_tien'] else 0
                
                txt = f"⚡  Mã #{order['id']}   |   {time_str}   |   {name}   |   Total: {amount:,.0f}đ"
                
                order_lbl = QLabel(txt)
                order_lbl.setStyleSheet(f"""
                    font-size: 14px; padding: 12px; color: {self.color_text_dark}; 
                    background: rgba(255,255,255,0.5); border-radius: 12px; margin-top: 4px;
                    border: 1px solid rgba(232, 220, 221, 0.4);
                """)
                self.v_order_list.addWidget(order_lbl)

        except Exception as e:
            print(f"❌ Lỗi Dashboard: {e}")
        finally:
            if 'db' in locals() and db.is_connected():
                cursor.close()
                db.close()

    def update_stats_ui(self, data_list):
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        for title, value, icon in data_list:
            card = GlassCard3D(radius=20)
            v_lay = QVBoxLayout(card)
            v_lay.setContentsMargins(20, 20, 20, 20)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 28px; margin-bottom: 4px;")
            
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"color: {self.color_text_muted}; font-size: 13px; font-weight: 600; text-transform: uppercase;")
            
            value_lbl = QLabel(value)
            value_lbl.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {self.color_accent}; margin-top: 2px;")
            v_lay.addWidget(icon_lbl)
            v_lay.addWidget(title_lbl)
            v_lay.addWidget(value_lbl)
            
            self.stats_layout.addWidget(card)

# ==========================================================
# KHỞI CHẠY HỆ THỐNG
# ==========================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Thiết lập Font chữ tiêu chuẩn cao cấp toàn diện hệ thống
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(253, 251, 249))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(44, 19, 22))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(44, 19, 22))
    palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(44, 19, 22))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(144, 41, 54))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)
    
    # Tinh chỉnh QHeaderView của tất cả các bảng con mượt mà, đồng điệu tone Cafe
    app.setStyleSheet(app.styleSheet() + """
        QHeaderView::section {
            background-color: #58111A;
            color: white;
            font-weight: bold;
            padding: 8px;
            border: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTableWidget {
            background-color: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(88, 17, 26, 0.2);
            gridline-color: rgba(88, 17, 26, 0.1);
            border-radius: 12px;
        }
    """)
    
    window = GiaoDienChinh()
    window.showMaximized()
    sys.exit(app.exec())