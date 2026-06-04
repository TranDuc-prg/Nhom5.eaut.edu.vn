import sys
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QGraphicsDropShadowEffect, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
                             QGroupBox, QScrollArea, QAbstractItemView)
from PyQt6.QtCharts import (QChart, QChartView, QPieSeries, QBarSeries, 
                            QBarSet, QBarCategoryAxis, QValueAxis)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QFont

# --- ĐỊNH NGHĨA CSS CHUNG CHO TOÀN BỘ APP ---
GLOBAL_STYLE = """
    QWidget {
        background-color: #F8FAFC;
    }
    
    QLabel {
        font-family: 'Segoe UI';
        color: #1E293B;
    }
    
    QComboBox {
        padding: 10px 15px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        background: white;
        font-family: 'Segoe UI';
        font-size: 13px;
        color: #334155;
    }
    QComboBox::drop-down {
        border: 0px;
    }
    QComboBox::down-arrow {
        image: none;
        border-width: 0px;
    }
    QComboBox:hover {
        border: 1px solid #A0AEC0;
    }

    /* Bảng dữ liệu Modern Style */
    QTableWidget {
        background-color: white;
        alternate-background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        gridline-color: #E2E8F0;
        font-family: 'Segoe UI';
        font-size: 13px;
    }
    QTableWidget::item {
        padding: 10px;
        border-bottom: 1px solid #F1F5F9;
    }
    QTableWidget::item:selected {
        background-color: #F1F5F9;
        color: #58111A;
    }
    
    /* Header Bảng Đẹp Trầm */
    QHeaderView::section {
        background-color: #58111A;
        color: white;
        font-weight: bold;
        font-size: 13px;
        padding: 10px;
        border: none;
    }
    QHeaderView::section:first {
        border-top-left-radius: 12px;
    }
    QHeaderView::section:last {
        border-top-right-radius: 12px;
    }

    /* Custom Thanh cuộn ScrollBar Modern */
    QScrollBar:vertical {
        border: none;
        background: #F1F5F9;
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical {
        background: #CBD5E1;
        min-height: 30px;
        border-radius: 4px;
    }
    QScrollBar::handle:vertical:hover {
        background: #94A3B8;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar:horizontal {
        border: none;
        background: #F1F5F9;
        height: 8px;
        margin: 0px;
        border-radius: 4px;
    }
    QScrollBar::handle:horizontal {
        background: #CBD5E1;
        min-width: 30px;
        border-radius: 4px;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }
"""

class StatCard(QFrame):
    def __init__(self, title, value, color_start, color_end, icon="📈", sub_text=""):
        super().__init__()
        self.setMinimumHeight(120)
        
        # Thiết kế Card Gradient & Hiệu ứng Hover biên viền màu gỗ mộc khi di chuột qua
        self.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color_start}, stop:1 {color_end});
                border-radius: 16px;
                border: 1px solid transparent;
            }}
            QFrame:hover {{
                border: 1px solid #A52A2A;
            }}
            QLabel {{ background: transparent; color: white; font-family: 'Segoe UI'; }}
        """)
        
        # Đổ bóng mềm sâu (Blur 30, Offset Y: 6)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(53, 32, 21, 35)) # Màu bóng đổ pha chút nâu trầm nhẹ
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(4)

        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet("font-size: 22px; font-weight: bold;")
        
        self.sub_lbl = QLabel(sub_text)
        self.sub_lbl.setStyleSheet("font-size: 11px; font-weight: 500; color: rgba(255, 255, 255, 0.8);")
        
        title_lbl = QLabel(f"{icon}  {title}")
        title_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: rgba(255, 255, 255, 0.7); margin-top: 5px;")
        
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.sub_lbl)
        layout.addStretch()
        layout.addWidget(title_lbl)


class ReportManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Báo cáo Thống kê - Coffee Shop")
        self.db_config = {"host": "localhost", "user": "root", "password": "", "database": "quanly_snack_db"}
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        # Apply CSS toàn app
        self.setStyleSheet(GLOBAL_STYLE)
        
        # Widget chứa nội dung
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        
        self.main_layout = QVBoxLayout(scroll_widget)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(25)

        # 1. Thẻ thống kê (Chuyển sang dải màu ấm/Đỏ trầm quý phái theo mẫu yêu cầu)
        stats_layout = QHBoxLayout()
        self.card_rev = StatCard("Doanh thu", "0đ", "#58111A", "#8B1E2D", "💰")
        self.card_ord = StatCard("Đơn hàng", "0", "#6B1620", "#A52A2A", "📦")
        self.card_avg = StatCard("Trung bình/đơn", "0đ", "#7A1D28", "#B23A48", "📊")
        self.card_profit = StatCard("Lợi nhuận", "0đ", "#58111A", "#C0392B", "📈")
        self.card_cus = StatCard("Khách hàng", "0", "#2D3748", "#4A5568", "👥")
        self.card_avg_cost = StatCard("Giá vốn TB nguyên liệu", "0đ/kg", "#1A252C", "#34495E", "⚖️")

        for card in [self.card_rev, self.card_ord, self.card_avg, self.card_profit, self.card_cus, self.card_avg_cost]:
            stats_layout.addWidget(card)
        self.main_layout.addLayout(stats_layout)

        # 2. Bộ lọc thời gian
        filter_layout = QHBoxLayout()
        filter_lbl = QLabel("Thời gian:")
        filter_lbl.setStyleSheet("font-weight: bold; color: #475569; font-size: 13px;")
        
        self.time_filter = QComboBox()
        self.time_filter.addItems(["7 ngày gần đây", "4 tuần gần đây", "Các tháng trong năm", "Năm nay"])
        self.time_filter.setFixedWidth(200)
        self.time_filter.currentIndexChanged.connect(self.refresh_data)
        
        filter_layout.addStretch()
        filter_layout.addWidget(filter_lbl)
        filter_layout.addWidget(self.time_filter)
        self.main_layout.addLayout(filter_layout)

        # 3. Biểu đồ chính (Hàng 1)
        charts_layout = QHBoxLayout()
        self.bar_chart_view = self.create_chart_view()
        self.bar_chart_view.setMinimumHeight(420)
        self.pie_chart_view = self.create_chart_view()
        self.pie_chart_view.setMinimumHeight(420)
        
        charts_layout.addWidget(self.bar_chart_view, 1)
        charts_layout.addWidget(self.pie_chart_view, 1)
        self.main_layout.addLayout(charts_layout)

        # 4. Biểu đồ phụ & Bảng Top Khách hàng (Hàng 2)
        bottom_layout = QHBoxLayout()
        self.line_chart_view = self.create_chart_view()
        self.line_chart_view.setMinimumHeight(350)

        self.table_container = QFrame()
        self.table_container.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        
        # Đổ bóng nhẹ cho khung bảng
        table_shadow = QGraphicsDropShadowEffect()
        table_shadow.setBlurRadius(20)
        table_shadow.setOffset(0, 4)
        table_shadow.setColor(QColor(0,0,0,15))
        self.table_container.setGraphicsEffect(table_shadow)

        table_v_layout = QVBoxLayout(self.table_container)
        table_v_layout.setContentsMargins(15, 15, 15, 15)
        
        title_top_cus = QLabel("🏆  TOP KHÁCH HÀNG THÂN THIẾT")
        title_top_cus.setStyleSheet("font-weight: bold; font-size: 14px; color: #58111A; padding-bottom: 5px;")
        
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(3)
        self.top_table.setHorizontalHeaderLabels(["Khách hàng", "SĐT", "Điểm"])
        self.top_table.setAlternatingRowColors(True)
        self.top_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.top_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table_v_layout.addWidget(title_top_cus)
        table_v_layout.addWidget(self.top_table)

        bottom_layout.addWidget(self.line_chart_view, 1)
        bottom_layout.addWidget(self.table_container, 1)
        self.main_layout.addLayout(bottom_layout)
        
        # 5. Bảng chi tiết lợi nhuận theo kỳ
        self.detail_group = QGroupBox("📋  Chi tiết lợi nhuận theo kỳ")
        self.detail_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-family: 'Segoe UI';
                font-size: 14px;
                color: #58111A;
                margin-top: 10px;
                padding-top: 20px;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0px 8px;
                background-color: #F8FAFC;
                border-radius: 4px;
            }
        """)
        
        group_shadow = QGraphicsDropShadowEffect()
        group_shadow.setBlurRadius(20)
        group_shadow.setOffset(0, 4)
        group_shadow.setColor(QColor(0,0,0,15))
        self.detail_group.setGraphicsEffect(group_shadow)

        detail_layout = QVBoxLayout(self.detail_group)
        detail_layout.setContentsMargins(15, 15, 15, 15)
        
        self.detail_table = QTableWidget()
        self.detail_table.setMinimumHeight(220)
        self.detail_table.setColumnCount(5)
        self.detail_table.setHorizontalHeaderLabels(["Kỳ", "Doanh thu", "Giá vốn", "Lợi nhuận", "Tỷ suất"])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_table.setAlternatingRowColors(True)
        self.detail_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        detail_layout.addWidget(self.detail_table)
        self.main_layout.addWidget(self.detail_group)

        # Cấu hình ScrollArea bọc ngoài cùng mượt mà
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Cửa sổ chính layout
        main_win_layout = QVBoxLayout(self)
        main_win_layout.setContentsMargins(0, 0, 0, 0)
        main_win_layout.addWidget(scroll_area)
        self.setLayout(main_win_layout)

    def get_average_material_cost(self, cursor):
        query = "SELECT ten_nguyenlieu, gia_nhap, don_vi FROM nguyenlieu WHERE gia_nhap > 0"
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows: return 0
        total_cost, count = 0, 0
        for row in rows:
            gia = float(row['gia_nhap'])
            don_vi = (row['don_vi'] or '').lower()
            if don_vi in ['gram', 'ml']:
                gia_kg = gia * 1000
            else:
                gia_kg = gia
            total_cost += gia_kg
            count += 1
        return total_cost / count if count > 0 else 0

    def get_product_cost(self, cursor):
        query = """
            SELECT c.id_sanpham, COALESCE(SUM(c.dinh_luong * n.gia_nhap), 0) as gia_von
            FROM congthuc c JOIN nguyenlieu n ON c.id_nguyenlieu = n.id GROUP BY c.id_sanpham
        """
        cursor.execute(query)
        return {row['id_sanpham']: float(row['gia_von']) for row in cursor.fetchall()}

    def get_profit_stats(self, cursor, period_filter):
        date_condition = self.get_date_condition(period_filter)
        product_costs = self.get_product_cost(cursor)
        query = f"""
            SELECT h.id, h.tong_tien, ct.id_sanpham, ct.so_luong
            FROM chitietdonhang h JOIN chitiethoadon ct ON h.id = ct.id_hoadon WHERE {date_condition}
        """
        cursor.execute(query)
        total_rev, total_cost = 0, 0
        for row in cursor.fetchall():
            total_rev += float(row['tong_tien'] or 0)
            total_cost += row['so_luong'] * product_costs.get(row['id_sanpham'], 0)
        return {"total_rev": total_rev, "total_cost": total_cost}
    
    def get_period_profit_stats(self, cursor, period_filter):
        date_condition = self.get_date_condition(period_filter)
        product_costs = self.get_product_cost(cursor)
        
        if period_filter == "7 ngày gần đây":
            date_format, group_by, sort_by = "DATE_FORMAT(h.ngay_tao, '%d/%m')", "DATE(h.ngay_tao)", "h.ngay_tao"
        elif period_filter == "4 tuần gần đây":
            date_format, group_by, sort_by = "CONCAT('Tuần ', WEEK(h.ngay_tao))", "WEEK(h.ngay_tao)", "MIN(h.ngay_tao)"
        elif period_filter == "Các tháng trong năm":
            date_format, group_by, sort_by = "DATE_FORMAT(h.ngay_tao, '%m/%Y')", "MONTH(h.ngay_tao), YEAR(h.ngay_tao)", "MIN(h.ngay_tao)"
        else:
            date_format, group_by, sort_by = "CAST(YEAR(h.ngay_tao) AS CHAR)", "YEAR(h.ngay_tao)", "YEAR(h.ngay_tao)"
        
        query = f"""
            SELECT {date_format} as period_label, SUM(h.tong_tien) as total_rev,
                   GROUP_CONCAT(CONCAT(ct.id_sanpham, ':', ct.so_luong)) as items
            FROM chitietdonhang h JOIN chitiethoadon ct ON h.id = ct.id_hoadon
            WHERE {date_condition} GROUP BY {group_by} ORDER BY {sort_by} ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        period_stats = []
        for row in rows:
            rev = float(row['total_rev'] or 0)
            cost = 0
            if row['items']:
                for item in row['items'].split(','):
                    parts = item.split(':')
                    if len(parts) == 2:
                        cost += int(parts[1]) * product_costs.get(int(parts[0]), 0)
            profit = rev - cost
            margin = (profit / rev * 100) if rev > 0 else 0
            period_stats.append({
                "period": row['period_label'], "revenue": rev, "cost": cost, "profit": profit, "margin": margin
            })
        return period_stats

    def get_date_condition(self, filter_text):
        if filter_text == "7 ngày gần đây": return "h.ngay_tao >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif filter_text == "4 tuần gần đây": return "h.ngay_tao >= DATE_SUB(NOW(), INTERVAL 4 WEEK)"
        return "YEAR(h.ngay_tao) = YEAR(NOW())"
    
    def create_chart_view(self):
        view = QChartView()
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
        
        # Thêm hiệu ứng đổ bóng cho các block biểu đồ
        chart_shadow = QGraphicsDropShadowEffect()
        chart_shadow.setBlurRadius(25)
        chart_shadow.setOffset(0, 5)
        chart_shadow.setColor(QColor(0, 0, 0, 15))
        view.setGraphicsEffect(chart_shadow)
        return view

    def format_currency(self, val):
        try:
            return f"{int(round(val)):,}".replace(",", ".") + "đ"
        except:
            return "0đ"

    def refresh_data(self):
        try:
            db = mysql.connector.connect(**self.db_config)
            cursor = db.cursor(dictionary=True)
            filter_text = self.time_filter.currentText()
            
            stats = self.get_profit_stats(cursor, filter_text)
            rev, cost = stats['total_rev'], stats['total_cost']
            profit = rev - cost
            margin = (profit / rev * 100) if rev > 0 else 0

            self.card_rev.val_lbl.setText(self.format_currency(rev))
            self.card_profit.val_lbl.setText(self.format_currency(profit))
            
            # Cải thiện hiển thị tỷ suất
            if margin >= 0:
                self.card_profit.sub_lbl.setText(f"Tỷ suất biên: +{margin:.1f}%")
                self.card_profit.sub_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #9AE6B4;")
            else:
                self.card_profit.sub_lbl.setText(f"Tỷ suất biên: {margin:.1f}%")
                self.card_profit.sub_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #FEB2B2;")
            
            cursor.execute(f"SELECT COUNT(DISTINCT id) as total FROM chitietdonhang h WHERE {self.get_date_condition(filter_text)}")
            total_orders = cursor.fetchone()['total']
            self.card_ord.val_lbl.setText(str(total_orders))
            self.card_avg.val_lbl.setText(self.format_currency(rev / total_orders if total_orders > 0 else 0))
            
            cursor.execute("SELECT COUNT(id) as total FROM khachhang")
            self.card_cus.val_lbl.setText(str(cursor.fetchone()['total']))
            
            avg_mat = self.get_average_material_cost(cursor)
            self.card_avg_cost.val_lbl.setText(f"{avg_mat/1000:.1f}00đ/kg" if avg_mat >= 1000 else f"{avg_mat:.0f}đ/kg")
            self.card_avg_cost.sub_lbl.setText("Trung bình giá nhập kho")
            
            # Cập nhật Charts & Tables
            self.update_bar_chart(cursor, filter_text)
            self.update_pie_chart(cursor)
            self.update_line_chart(cursor)
            self.update_top_table(cursor)
            
            period_stats = self.get_period_profit_stats(cursor, filter_text)
            self.detail_table.setRowCount(len(period_stats))
            for i, stat in enumerate(period_stats):
                self.detail_table.setItem(i, 0, QTableWidgetItem(stat['period']))
                self.detail_table.setItem(i, 1, QTableWidgetItem(self.format_currency(stat['revenue'])))
                self.detail_table.setItem(i, 2, QTableWidgetItem(self.format_currency(stat['cost'])))
                self.detail_table.setItem(i, 3, QTableWidgetItem(self.format_currency(stat['profit'])))
                
                margin_item = QTableWidgetItem(f"{stat['margin']:.1f}%")
                margin_item.setForeground(QColor(34, 197, 94) if stat['margin'] >= 0 else QColor(239, 68, 68))
                margin_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
                self.detail_table.setItem(i, 4, margin_item)
            
            db.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi đồng bộ cơ sở dữ liệu:\n{str(e)}")

    def update_bar_chart(self, cursor, filter_text):
        bar_rev, bar_cost = QBarSet("Doanh thu"), QBarSet("Giá vốn")
        bar_rev.setColor(QColor("#58111A")) # Gỗ trầm mộc
        bar_cost.setColor(QColor("#E53E3E")) # Đỏ ấm tương phản
        
        product_costs = self.get_product_cost(cursor)
        date_condition = self.get_date_condition(filter_text)
        
        if filter_text == "7 ngày gần đây":
            date_format, group_by, sort_by = "DATE_FORMAT(h.ngay_tao, '%d/%m')", "DATE(h.ngay_tao)", "h.ngay_tao"
        elif filter_text == "4 tuần gần đây":
            date_format, group_by, sort_by = "CONCAT('Tuần ', WEEK(h.ngay_tao))", "WEEK(h.ngay_tao)", "MIN(h.ngay_tao)"
        elif filter_text == "Các tháng trong năm":
            date_format, group_by, sort_by = "DATE_FORMAT(h.ngay_tao, '%m/%Y')", "MONTH(h.ngay_tao), YEAR(h.ngay_tao)", "MIN(h.ngay_tao)"
        else:
            date_format, group_by, sort_by = "CAST(YEAR(h.ngay_tao) AS CHAR)", "YEAR(h.ngay_tao)", "YEAR(h.ngay_tao)"
        
        query = f"""
            SELECT {date_format} as period, SUM(h.tong_tien) as total_rev,
                   GROUP_CONCAT(CONCAT(ct.id_sanpham, ':', ct.so_luong)) as items
            FROM chitietdonhang h JOIN chitiethoadon ct ON h.id = ct.id_hoadon
            WHERE {date_condition} GROUP BY {group_by} ORDER BY {sort_by} ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        categories = []
        max_val = 0
        for row in rows:
            categories.append(str(row['period']))
            rev = float(row['total_rev'] or 0)
            cost = 0
            if row['items']:
                for item in row['items'].split(','):
                    parts = item.split(':')
                    if len(parts) == 2:
                        cost += int(parts[1]) * product_costs.get(int(parts[0]), 0)
            bar_rev.append(rev)
            bar_cost.append(cost)
            max_val = max(max_val, rev, cost)
        
        chart = QChart()
        # Kích hoạt toàn bộ hiệu ứng chuyển động mượt mà (AllAnimations)
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        if not categories:
            chart.setTitle("Không có dữ liệu hiển thị")
            self.bar_chart_view.setChart(chart)
            return
        
        series = QBarSeries()
        series.append(bar_rev)
        series.append(bar_cost)
        chart.addSeries(series)
        chart.setTitle("Kinh doanh: Doanh thu & Giá vốn")
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max_val * 1.2 if max_val > 0 else 1000000)
        axis_y.setLabelFormat("%'d")
        axis_y.setTitleText("VNĐ")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        self.bar_chart_view.setChart(chart)
    
    def update_pie_chart(self, cursor):
        series = QPieSeries()
        cursor.execute("""
            SELECT CASE WHEN hinh_thuc_tt IS NULL OR hinh_thuc_tt = '' THEN 'Khác' ELSE hinh_thuc_tt END as payment_method, 
                   COUNT(id) as so_luong FROM chitietdonhang GROUP BY payment_method
        """)
        rows = cursor.fetchall()
        total = sum(r['so_luong'] for r in rows)
        
        for r in rows:
            percentage = (r['so_luong'] / total * 100) if total > 0 else 0
            series.append(f"{r['payment_method']} ({percentage:.1f}%)", float(r['so_luong']))
        
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        if series.count() == 0:
            chart.setTitle("Không tìm thấy dữ liệu thanh toán")
            self.pie_chart_view.setChart(chart)
            return
        
        chart.addSeries(series)
        chart.setTitle("Cơ cấu Phương thức thanh toán")
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        self.pie_chart_view.setChart(chart)

    def update_line_chart(self, cursor):
        bar_set = QBarSet("Số lượng đơn")
        bar_set.setColor(QColor("#58111A")) # Tone màu nâu vàng nhẹ sang trọng
        
        categories = []
        cursor.execute("""
            SELECT DATE_FORMAT(h.ngay_tao, '%d/%m') as lb, COUNT(DISTINCT h.id) as sl 
            FROM chitietdonhang h WHERE h.ngay_tao >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(h.ngay_tao) ORDER BY h.ngay_tao ASC
        """)
        rows = cursor.fetchall()
        
        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        if not rows:
            chart.setTitle("Thiếu dữ liệu đơn hàng tuần qua")
            self.line_chart_view.setChart(chart)
            return
        
        for r in rows:
            categories.append(r['lb'])
            bar_set.append(float(r['sl']))
        
        series = QBarSeries()
        series.append(bar_set)
        series.setLabelsVisible(True)
        chart.addSeries(series)
        chart.setTitle("Tần suất Đơn hàng (7 ngày gần nhất)")
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        axis_y.setTitleText("Đơn hàng")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        self.line_chart_view.setChart(chart)

    def update_top_table(self, cursor):
        cursor.execute("""
            SELECT ten_khachhang, so_dien_thoai, diem_tich_luy FROM khachhang 
            WHERE ten_khachhang IS NOT NULL AND ten_khachhang != ''
            ORDER BY diem_tich_luy DESC LIMIT 5
        """)
        rows = cursor.fetchall()
        self.top_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.top_table.setItem(i, 0, QTableWidgetItem(str(row['ten_khachhang'])))
            self.top_table.setItem(i, 1, QTableWidgetItem(str(row['so_dien_thoai'] or '---')))
            
            score_item = QTableWidgetItem(str(row['diem_tich_luy']))
            score_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            score_item.setForeground(QColor("#58111A"))
            self.top_table.setItem(i, 2, score_item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. Setup Font hệ thống đẹp toàn diện cho ứng dụng
    app.setFont(QFont("Segoe UI", 10))
    
    window = ReportManager()
    window.resize(1420, 960)
    window.show()
    sys.exit(app.exec())