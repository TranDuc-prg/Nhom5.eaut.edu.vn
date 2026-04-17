import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCharts import (QChart, QChartView, QLineSeries, QPieSeries, 
                            QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QFont

class StatCard(QFrame):
    def __init__(self, title, value, color_start, color_end, icon="📈"):
        super().__init__()
        self.setFixedHeight(140)
        self.setObjectName("statCard")
        # Gradient background và bo góc
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color_start}, stop:1 {color_end});
                border-radius: 20px;
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 45))
        shadow.setYOffset(10)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Thêm Icon phụ để giao diện sinh động
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 20px; background: transparent; color: rgba(255,255,255,0.6);")
        layout.addWidget(icon_lbl, alignment=Qt.AlignmentFlag.AlignRight)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("color: white; font-size: 26px; font-weight: 800; background: transparent;")
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 14px; font-weight: 500; background: transparent;")
        
        layout.addWidget(val_lbl)
        layout.addWidget(title_lbl)

class ReportDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snack Shop - Hệ thống Báo cáo Chuyên sâu")
        self.resize(1200, 950)
        self.setStyleSheet("background-color: #FDF5F0;") # Nền kem

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(35, 35, 35, 35)
        self.main_layout.setSpacing(30)

        # 1. Top Stats Row
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(StatCard("Tổng doanh thu", "206.000.000đ", "#FF6D00", "#FF9100", "💰"))
        stats_layout.addWidget(StatCard("Tổng đơn hàng", "2.315", "#00BFA5", "#1DE9B6", "📦"))
        stats_layout.addWidget(StatCard("Giá trị TB/đơn", "88.984đ", "#AA00FF", "#D500F9", "📊"))
        stats_layout.addWidget(StatCard("Khách hàng mới", "489", "#C51162", "#F50057", "👥"))
        self.main_layout.addLayout(stats_layout)

        # 2. Middle Row: Line Chart & Pie Chart
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.create_line_chart(), 6)
        middle_layout.addWidget(self.create_pie_chart(), 4)
        self.main_layout.addLayout(middle_layout)

        # 3. Bottom Row: Bar Chart
        self.main_layout.addWidget(self.create_bar_chart())

    def create_chart_view(self, chart):
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        chart.setBackgroundRoundness(20)
        chart.layout().setContentsMargins(0, 0, 0, 0)
        
        view = QChartView(chart)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #F1F2F6;")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        view.setGraphicsEffect(shadow)
        return view

    def create_line_chart(self):
        series = QLineSeries()
        series.setName("Doanh thu")
        series.append(0, 120); series.append(1, 160); series.append(2, 140); series.append(3, 210)
        
        # Tùy chỉnh đường kẻ
        pen = series.pen()
        pen.setWidth(4)
        pen.setColor(QColor("#FF7043"))
        series.setPen(pen)
        series.setPointsVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Doanh thu theo quý (Triệu VNĐ)")
        chart.setTitleFont(QFont("Arial", 14, QFont.Weight.Bold))

        axis_x = QValueAxis()
        axis_x.setLabelFormat("Q%d")
        axis_x.setRange(0, 3)
        axis_x.setTickCount(4)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setRange(0, 300)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        return self.create_chart_view(chart)

    def create_pie_chart(self):
        series = QPieSeries()
        slices = [
            series.append("Snack", 35),
            series.append("Đồ uống", 30),
            series.append("Bánh kẹo", 25),
            series.append("Khác", 10)
        ]
        
        colors = ["#FF7043", "#4DB6AC", "#FFB74D", "#9575CD"]
        for i, slice_item in enumerate(slices):
            slice_item.setBrush(QColor(colors[i]))
            slice_item.setLabelVisible(True)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Phân bổ theo danh mục")
        chart.setTitleFont(QFont("Arial", 14, QFont.Weight.Bold))
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        return self.create_chart_view(chart)

    def create_bar_chart(self):
        set0 = QBarSet("Số đơn hàng")
        set0.append([520, 580, 550, 680, 710, 640])
        set0.setBrush(QColor("#1DE9B6"))

        series = QBarSeries()
        series.append(set0)

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Số lượng đơn hàng 6 tháng gần nhất")
        chart.setTitleFont(QFont("Arial", 14, QFont.Weight.Bold))

        axis_x = QBarCategoryAxis()
        axis_x.append(["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6"])
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        return self.create_chart_view(chart)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportDashboard()
    window.show()
    sys.exit(app.exec())