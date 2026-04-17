import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class ProductManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snack Shop - Quản lý sản phẩm")
        self.resize(1100, 850)
        self.setStyleSheet("background-color: #FDF5F0;") # Nền kem nhạt

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        self.init_header()
        self.init_stats_bar()
        self.init_table()

    def init_header(self):
        # Tiêu đề chính
        header_layout = QVBoxLayout()
        title = QLabel("Quản lý sản phẩm 🍿")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #2D3436;")
        subtitle = QLabel("Danh sách tất cả sản phẩm trong cửa hàng")
        subtitle.setStyleSheet("font-size: 14px; color: #636E72;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        self.main_layout.addLayout(header_layout)

        # Thanh công cụ: Tìm kiếm + Lọc + Thêm mới
        tool_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm kiếm sản phẩm...")
        self.search_input.setFixedHeight(45)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: white; border: 1px solid #FFCCBC; 
                border-radius: 15px; padding-left: 15px; font-size: 14px;
            }
        """)

        self.filter_box = QComboBox()
        self.filter_box.addItems(["Tất cả danh mục", "Bánh kẹo", "Snack mặn", "Nước ngọt"])
        self.filter_box.setFixedHeight(45)
        self.filter_box.setFixedWidth(180)
        self.filter_box.setStyleSheet("""
            QComboBox { background-color: #E3F2FD; border-radius: 12px; padding-left: 10px; border: none; }
        """)

        self.btn_add = QPushButton("+ Thêm sản phẩm")
        self.btn_add.setFixedHeight(45)
        self.btn_add.setFixedWidth(160)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #FF7043; color: white; font-weight: bold; 
                border-radius: 15px; font-size: 14px;
            }
            QPushButton:hover { background-color: #E64A19; }
        """)

        tool_layout.addWidget(self.search_input, 4)
        tool_layout.addWidget(self.filter_box, 1)
        tool_layout.addWidget(self.btn_add)
        self.main_layout.addLayout(tool_layout)

    def init_stats_bar(self):
        # Thanh thống kê nhanh
        stats_frame = QFrame()
        stats_frame.setStyleSheet("background-color: white; border-radius: 20px;")
        stats_frame.setFixedHeight(100)
        layout = QHBoxLayout(stats_frame)

        stats = [
            ("8", "Tổng sản phẩm", "#FF7043"),
            ("1190", "Tổng tồn kho", "#2ECC71"),
            ("2505", "Đã bán", "#3498DB"),
            ("8", "Kết quả lọc", "#9B59B6")
        ]

        for val, label, color in stats:
            item_layout = QVBoxLayout()
            v_lbl = QLabel(val)
            v_lbl.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
            v_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l_lbl = QLabel(label)
            l_lbl.setStyleSheet("font-size: 12px; color: #636E72;")
            l_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            item_layout.addWidget(v_lbl)
            item_layout.addWidget(l_lbl)
            layout.addLayout(item_layout)

        self.main_layout.addWidget(stats_frame)

    def init_table(self):
        # Bảng danh sách sản phẩm
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Mã SP", "Sản phẩm", "Danh mục", "Giá", "Tồn kho", "Đã bán", "Thao tác"])
        
        # Cấu hình Header ngang
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #FF8A65; color: white; font-weight: bold;
                height: 45px; border: none; font-size: 14px;
            }
        """)

        # Cấu hình Header dọc (SỬA LỖI TẠI ĐÂY)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(60) # Đặt chiều cao dòng mặc định là 60px

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; border-radius: 15px; gridline-color: transparent;
                border: none;
            }
            QTableWidget::item { border-bottom: 1px solid #F1F2F6; padding: 10px; }
        """)

        # Dữ liệu mẫu
        product_data = [
            ("SP001", "Bánh quy bơ", "Bánh kẹo", "15.000 đ", "120", "450"),
            ("SP002", "Kẹo dẻo trái cây", "Bánh kẹo", "12.000 đ", "200", "380"),
            ("SP003", "Snack khoai tây", "Snack mặn", "18.000 đ", "85", "320")
        ]

        self.table.setRowCount(len(product_data))
        for row, data in enumerate(product_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter) # Căn giữa văn bản
                
                # Định dạng riêng cho cột Sản phẩm và Giá
                if col == 1: item.setText(f"🍪 {value}")
                if col == 3: item.setForeground(QColor("#FF7043"))
                
                self.table.setItem(row, col, item)

            # Cột Thao tác
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(10, 5, 10, 5)
            
            btn_edit = QPushButton("Sửa")
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("background-color: #E3F2FD; color: #1976D2; border-radius: 8px; padding: 5px 10px; font-weight: bold;")
            
            btn_delete = QPushButton("Xóa")
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_delete.setStyleSheet("background-color: #FFEBEE; color: #C62828; border-radius: 8px; padding: 5px 10px; font-weight: bold;")
            
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            self.table.setCellWidget(row, 6, action_widget)

        self.main_layout.addWidget(self.table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProductManager()
    window.show()
    sys.exit(app.exec())
