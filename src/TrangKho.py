import sys
import mysql.connector
from PyQt6.QtCore import Qt, QSize, QDate, QDateTime
from PyQt6.QtGui import QFont, QColor, QIcon, QPalette
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGridLayout, 
                             QScrollArea, QFrame, QProgressBar, QLineEdit,
                             QDialog, QTextEdit, QMessageBox, QGraphicsDropShadowEffect,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QDoubleSpinBox, QTabWidget, QDateEdit)
from PyQt6.QtGui import QFont, QColor, QIcon
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QPageLayout, QPageSize
from PyQt6.QtWidgets import QFileDialog, QDateEdit
from datetime import datetime, timedelta

# ========================== DATABASE ==========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "quanly_snack_db"
}
def get_db_connection():
    try:
        return mysql.connector.connect(
            **DB_CONFIG,
            buffered=True
        )
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return None

# ========================== DIALOG LỊCH SỬ GIÁ ==========================
class PriceHistoryDialog(QDialog):
    def __init__(self, ingredient_id, ingredient_name, parent=None):
        super().__init__(parent)
        self.ingredient_id = ingredient_id
        self.ingredient_name = ingredient_name
        self.setWindowTitle(f"Lịch sử giá nhập - {ingredient_name}")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: white; border-radius: 10px;")
        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"LỊCH SỬ NHẬP GIÁ: {self.ingredient_name}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #58111A;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Ngày giờ", "Số lượng", "Giá nhập", "Giá TB sau nhập"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(35)
        btn_close.setStyleSheet("background: #58111A; color: white; font-weight: bold; border-radius: 5px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def load_history(self):
        db = get_db_connection()
        if not db:
            return
        try:
            cursor = db.cursor(dictionary=True)
            query = """
                SELECT ngay_gd, so_luong, gia_nhap, ton_sau
                FROM lichsu_kho
                WHERE ten_nl = %s AND loai_gd = 'IN'
                ORDER BY ngay_gd DESC
            """
            cursor.execute(query, (self.ingredient_name,))
            rows = cursor.fetchall()
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                ngay = row['ngay_gd'].strftime("%d/%m/%Y %H:%M:%S") if row['ngay_gd'] else ""
                so_luong = f"{row['so_luong']:.2f}" if row['so_luong'] else "0"
                gia_nhap = f"{row['gia_nhap']:,.0f}đ" if row['gia_nhap'] else "0đ"
                gia_tb_sau = f"{row['ton_sau']:,.0f}đ" if row['ton_sau'] else "0đ"
                self.table.setItem(i, 0, QTableWidgetItem(ngay))
                self.table.setItem(i, 1, QTableWidgetItem(so_luong))
                self.table.setItem(i, 2, QTableWidgetItem(gia_nhap))
                self.table.setItem(i, 3, QTableWidgetItem(gia_tb_sau))
        except Exception as e:
            print(f"Lỗi tải lịch sử giá: {e}")
        finally:
            db.close()

# ========================== DIALOG NHẬP/XUẤT/ĐIỀU CHỈNH ==========================
class TransactionDialog(QDialog):
    def __init__(self, mode, data, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.data = data
        self.current_qty = float(data[2])
        self.current_price = float(data[6]) if len(data) > 6 else 0.0
        self.max_qty = 300.0 
        self.min_qty = 5.0
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()

    def init_ui(self):
        # Container chính
        main_container = QFrame(self)
        main_container.setStyleSheet("background-color: white; border-radius: 30px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 10)
        main_container.setGraphicsEffect(shadow)
        
        # Layout chính của container
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== THÊM SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #58111A;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # Content widget bên trong scroll
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(35, 35, 35, 35)
        layout.setSpacing(12)

        # Tiêu đề
        title_map = {"IN": "📥 NHẬP KHO", "OUT": "📤 XUẤT KHO", "ADJUST": "⚙ ĐIỀU CHỈNH"}
        title_lbl = QLabel(title_map[self.mode])
        title_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet("color: #58111A; margin-bottom: 10px;")
        layout.addWidget(title_lbl)

        # Tên nguyên liệu
        name_lbl = QLabel(self.data[1])
        name_lbl.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet("color: #2C3E50; margin-bottom: 15px;")
        layout.addWidget(name_lbl)

        # Khung thông tin
        info_frame = QFrame()
        info_frame.setStyleSheet("background: #F8F9FA; border-radius: 15px; padding: 12px;")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(8)
        
        info_layout.addWidget(QLabel(f"📦 Tồn hiện tại: <b style='color:#58111A;'>{self.current_qty:,.0f} {self.data[3]}</b>"))
        info_layout.addWidget(QLabel(f"💰 Giá TB hiện tại: <b>{self.current_price:,.0f}đ/{self.data[3]}</b>"))
        info_layout.addWidget(QLabel(f"📊 Mức tối đa: <b>{self.max_qty:,.0f} {self.data[3]}</b>"))
        info_layout.addWidget(QLabel(f"⚠️ Ngưỡng cảnh báo: <b>{self.min_qty:,.0f} {self.data[3]}</b>"))
        
        layout.addWidget(info_frame)

        # Số lượng
        layout.addWidget(QLabel("🔢 Số lượng thực hiện:"))
        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Nhập số lượng...")
        self.qty_input.setFixedHeight(40)
        self.qty_input.setStyleSheet("border: 1px solid #DDD; border-radius: 10px; padding: 0 15px; font-size: 14px;")
        self.qty_input.textChanged.connect(self.update_preview)
        layout.addWidget(self.qty_input)

        self.price_input = None
        if self.mode == "IN":
            layout.addWidget(QLabel("💵 Giá nhập:"))
            self.price_input = QLineEdit()
            self.price_input.setPlaceholderText("Nhập giá cho lô hàng...")
            self.price_input.setFixedHeight(40)
            self.price_input.setStyleSheet("border: 1px solid #DDD; border-radius: 10px; padding: 0 15px; font-size: 14px;")
            self.price_input.textChanged.connect(self.update_preview)
            layout.addWidget(self.price_input)

            # Ngày tháng - đặt trên 1 hàng
            date_layout = QHBoxLayout()
            
            # Ngày sản xuất
            sx_widget = QWidget()
            sx_layout = QVBoxLayout(sx_widget)
            sx_layout.setContentsMargins(0, 0, 5, 0)
            sx_layout.addWidget(QLabel("📅 Ngày sản xuất:"))
            self.date_sx = QDateEdit()
            self.date_sx.setCalendarPopup(True)
            self.date_sx.setDate(QDate.currentDate())
            self.date_sx.setDisplayFormat("dd/MM/yyyy")
            self.date_sx.setFixedHeight(40)
            sx_layout.addWidget(self.date_sx)
            date_layout.addWidget(sx_widget)
            
            # Hạn sử dụng
            hh_widget = QWidget()
            hh_layout = QVBoxLayout(hh_widget)
            hh_layout.setContentsMargins(5, 0, 0, 0)
            hh_layout.addWidget(QLabel("⚠️ Hạn sử dụng:"))
            self.date_hh = QDateEdit()
            self.date_hh.setCalendarPopup(True)
            self.date_hh.setDate(QDate.currentDate().addDays(30))
            self.date_hh.setDisplayFormat("dd/MM/yyyy")
            self.date_hh.setFixedHeight(40)
            hh_layout.addWidget(self.date_hh)
            date_layout.addWidget(hh_widget)
            
            layout.addLayout(date_layout)

        # Lý do
        layout.addWidget(QLabel("📝 Lý do / Ghi chú:"))
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Nhập lý do (không bắt buộc)...")
        self.reason_input.setFixedHeight(70)
        self.reason_input.setStyleSheet("border: 1px solid #DDD; border-radius: 10px; padding: 8px;")
        layout.addWidget(self.reason_input)

        # Preview box
        self.preview_box = QFrame()
        self.preview_box.setStyleSheet("background: #FFF5EE; border-radius: 12px; padding: 10px;")
        pre_lay = QVBoxLayout(self.preview_box)
        self.pre_txt = QLabel("")
        self.pre_txt.setStyleSheet("font-weight: bold; color: #58111A;")
        self.pre_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pre_txt.setWordWrap(True)
        pre_lay.addWidget(self.pre_txt)
        layout.addWidget(self.preview_box)

        layout.addSpacing(10)
        
        # Nút bấm
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("❌ Hủy")
        cancel_btn.setStyleSheet("background: #FDF2E9; color: #58111A; border-radius: 20px; height: 45px; font-weight: bold; border: none;")
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("✅ Xác nhận")
        confirm_btn.setStyleSheet("background: #58111A; color: white; border-radius: 20px; height: 45px; font-weight: bold; border: none;")
        confirm_btn.clicked.connect(self.process_transaction)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(confirm_btn)
        layout.addLayout(btn_layout)
        
        # Thêm stretch ở cuối
        layout.addStretch()
        
        # Gán content widget vào scroll
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Gắn container vào dialog
        v_main = QVBoxLayout(self)
        v_main.addWidget(main_container)
        
        # Đặt kích thước dialog cố định, vừa phải
        self.setFixedSize(520, 650)
        self.update_preview()

    def update_preview(self):
        try:
            qty_txt = self.qty_input.text().replace(',', '.')
            qty_val = float(qty_txt) if qty_txt else 0
            
            min_qty = self.min_qty
            max_qty = self.max_qty

            if self.mode == "IN":
                new_qty = self.current_qty + qty_val
                
                warning_msg = ""
                if new_qty > max_qty:
                    warning_msg = f"\n⚠️ Vượt mức tối đa ({max_qty:,.0f} {self.data[3]})!"
                elif new_qty <= min_qty:
                    warning_msg = f"\n⚠️ Dưới ngưỡng {min_qty:,.0f} {self.data[3]}!"
                
                if self.price_input and self.price_input.text():
                    try:
                        price_txt = self.price_input.text().replace(',', '.')
                        new_price = float(price_txt)
                        if new_price > 0 and qty_val > 0:
                            total_value = self.current_qty * self.current_price
                            new_value = total_value + (qty_val * new_price)
                            avg_price = new_value / new_qty if new_qty > 0 else self.current_price
                            self.pre_txt.setText(f"Sau nhập: {new_qty:,.0f} {self.data[3]}{warning_msg}\n💰 Giá TB mới: {avg_price:,.0f}đ/{self.data[3]}")
                        else:
                            self.pre_txt.setText(f"Sau nhập: {new_qty:,.0f} {self.data[3]}{warning_msg}\n(Chưa nhập giá)")
                    except:
                        self.pre_txt.setText(f"Sau nhập: {new_qty:,.0f} {self.data[3]}{warning_msg}")
                else:
                    self.pre_txt.setText(f"Sau nhập: {new_qty:,.0f} {self.data[3]}{warning_msg}")
                    
            elif self.mode == "OUT":
                if qty_val > self.current_qty:
                    self.pre_txt.setText(f"❌ Lỗi: Xuất {qty_val:,.0f} > tồn {self.current_qty:,.0f}!")
                else:
                    new_qty = self.current_qty - qty_val
                    warning_msg = f"\n⚠️ Dưới ngưỡng {min_qty:,.0f}!" if new_qty <= min_qty else ""
                    self.pre_txt.setText(f"Sau xuất: {new_qty:,.0f} {self.data[3]}{warning_msg}")
                    
            else:  # ADJUST
                new_qty = qty_val
                warning_msg = ""
                if new_qty > max_qty:
                    warning_msg = f"\n⚠️ Vượt mức tối đa ({max_qty:,.0f})!"
                elif new_qty <= min_qty and new_qty > 0:
                    warning_msg = f"\n⚠️ Dưới ngưỡng {min_qty:,.0f}!"
                elif new_qty == 0:
                    warning_msg = f"\n⚠️ Tồn kho = 0!"
                self.pre_txt.setText(f"Sau điều chỉnh: {new_qty:,.0f} {self.data[3]}{warning_msg}")
            
            # Đổi màu preview
            if 'new_qty' in locals():
                if new_qty > max_qty:
                    self.preview_box.setStyleSheet("background: #FADBD8; border-radius: 12px; padding: 10px;")
                    self.pre_txt.setStyleSheet("font-weight: bold; color: #C0392B;")
                elif new_qty <= min_qty and new_qty > 0:
                    self.preview_box.setStyleSheet("background: #FEF9E7; border-radius: 12px; padding: 10px;")
                    self.pre_txt.setStyleSheet("font-weight: bold; color: #E67E22;")
                elif new_qty == 0:
                    self.preview_box.setStyleSheet("background: #FADBD8; border-radius: 12px; padding: 10px;")
                    self.pre_txt.setStyleSheet("font-weight: bold; color: #C0392B;")
                else:
                    self.preview_box.setStyleSheet("background: #EBF5FB; border-radius: 12px; padding: 10px;")
                    self.pre_txt.setStyleSheet("font-weight: bold; color: #2980B9;")
                    
        except Exception as e:
            self.pre_txt.setText(f"Lỗi: {str(e)}")
    
    def process_transaction(self):
        # Giữ nguyên phần process_transaction của bạn
        qty_txt = self.qty_input.text().replace(',', '.')
        if not qty_txt:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập số lượng!")
            return
            
        try:
            qty_val = float(qty_txt)
            if qty_val <= 0:
                QMessageBox.warning(self, "Cảnh báo", "Số lượng phải lớn hơn 0!")
                return
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số lượng nhập vào không hợp lệ!")
            return

        ingredient_id = self.data[0]
        ingredient_name = self.data[1]
        reason = self.reason_input.toPlainText().strip()
        
        min_qty = self.min_qty
        max_qty = self.max_qty
        
        if self.mode == "IN":
            new_qty = self.current_qty + qty_val
            
            if new_qty > max_qty:
                reply = QMessageBox.question(
                    self, 
                    "Cảnh báo vượt định mức", 
                    f"Số lượng sau khi nhập ({new_qty:,.0f} {self.data[3]}) sẽ vượt quá giới hạn tối đa ({max_qty:,.0f} {self.data[3]}).\nBạn có muốn tiếp tục?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            if not self.price_input or not self.price_input.text():
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập giá nhập!")
                return
                
            price_txt = self.price_input.text().replace(',', '.')
            try:
                input_price = float(price_txt)
                if input_price <= 0:
                    QMessageBox.warning(self, "Lỗi", "Giá nhập phải lớn hơn 0!")
                    return
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Giá nhập không hợp lệ!")
                return
            
            total_value = self.current_qty * self.current_price
            new_value = total_value + (qty_val * input_price)
            new_avg_price = new_value / new_qty if new_qty > 0 else self.current_price
            
            ngay_sx = self.date_sx.date().toPyDate() if hasattr(self, 'date_sx') else None
            ngay_hh = self.date_hh.date().toPyDate() if hasattr(self, 'date_hh') else None
            
        elif self.mode == "OUT":
            if qty_val > self.current_qty:
                QMessageBox.warning(self, "Lỗi kho", f"Số lượng xuất ({qty_val}) vượt quá tồn kho ({self.current_qty} {self.data[3]})!")
                return
            new_qty = self.current_qty - qty_val
            input_price = 0.0
            new_avg_price = self.current_price
            ngay_sx = None
            ngay_hh = None
            
            if new_qty <= min_qty:
                reply = QMessageBox.question(
                    self,
                    "Cảnh báo tồn kho thấp",
                    f"Sau khi xuất, tồn kho còn {new_qty:,.0f} {self.data[3]} (dưới ngưỡng {min_qty:,.0f}).\nBạn có muốn tiếp tục?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
        else:
            new_qty = qty_val
            qty_val = new_qty - self.current_qty
            input_price = 0.0
            new_avg_price = self.current_price
            ngay_sx = None
            ngay_hh = None
            
            if new_qty > max_qty:
                reply = QMessageBox.question(
                    self,
                    "Cảnh báo vượt định mức",
                    f"Số lượng sau khi điều chỉnh ({new_qty:,.0f} {self.data[3]}) vượt quá mức tối đa ({max_qty:,.0f}).\nBạn có muốn tiếp tục?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

        conn = get_db_connection()
        if not conn:
            QMessageBox.critical(self, "Lỗi kết nối", "Không thể kết nối database!")
            return

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE nguyenlieu SET so_luong = %s, gia_nhap = %s WHERE id = %s",
                        (new_qty, new_avg_price, ingredient_id))
            
            cursor.execute("""
                INSERT INTO lichsu_kho (ten_nl, loai_gd, so_luong, gia_nhap, ton_sau, ton_truoc, ngay_gd, ly_do, ngay_sx, ngay_hh)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)
            """, (ingredient_name, self.mode, qty_val if self.mode != "OUT" else -qty_val,
                input_price if self.mode == "IN" else self.current_price,
                new_avg_price, self.current_qty, reason, ngay_sx, ngay_hh))
            
            conn.commit()
            QMessageBox.information(self, "Thành công", f"Đã {self.mode} {abs(qty_val):,.0f} {self.data[3]}!")
            self.accept()
            
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {str(e)}")
        finally:
            conn.close()


# ========================== DIALOG THÊM/SỬA NGUYÊN LIỆU ==========================
class IngredientDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Thêm nguyên liệu" if not data else "Sửa nguyên liệu")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        if data:
            self.load_data()

    def init_ui(self):
        main_container = QFrame(self)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 24px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        icon = QLabel("🍱")
        icon.setStyleSheet("font-size: 32px;")
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Form fields
        fields = [
            ("Tên nguyên liệu", "txt_name", QLineEdit()),
            ("Đơn vị tính", "cbo_unit", QComboBox()),
            ("Ngưỡng cảnh báo", "spin_threshold", QDoubleSpinBox()),
            ("Mức chứa tối đa (Max)", "spin_max", QDoubleSpinBox()),
            ("Nhà cung cấp", "cbo_supplier", QComboBox()),
            ("Giá nhập (₫/đơn vị)", "spin_price", QDoubleSpinBox()),
        ]

        for label_text, attr_name, widget in fields:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("font-weight: bold; color: #555;")
            if isinstance(widget, QLineEdit):
                widget.setPlaceholderText(f"Nhập {label_text.lower()}")
                widget.setStyleSheet("""
                    QLineEdit {
                        border: 1px solid #DDD;
                        border-radius: 12px;
                        padding: 10px 15px;
                        background: #F9F9F9;
                    }
                    QLineEdit:focus {
                        border: 1px solid #58111A;
                        background: white;
                    }
                """)
            elif isinstance(widget, QComboBox):
                widget.setStyleSheet("""
                    QComboBox {
                        border: 1px solid #DDD;
                        border-radius: 12px;
                        padding: 8px 15px;
                        background: #F9F9F9;
                    }
                    QComboBox::drop-down {
                        border: none;
                    }
                """)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setStyleSheet("""
                    QDoubleSpinBox {
                        border: 1px solid #DDD;
                        border-radius: 12px;
                        padding: 8px 15px;
                        background: #F9F9F9;
                    }
                """)
                if label_text == "Ngưỡng cảnh báo":
                    widget.setSuffix(" đơn vị")
                elif label_text == "Giá nhập (₫/đơn vị)":
                    widget.setPrefix("₫ ")
                    widget.setMaximum(10_000_000)
                # --- THÊM ĐOẠN NÀY ĐỂ ĐỊNH DẠNG CHO Ô MAX MỚI ---
                elif label_text == "Mức chứa tối đa (Max)":
                    widget.setSuffix(" đơn vị")
                    widget.setMaximum(10_000_000)
            row.addWidget(lbl)
            row.addWidget(widget)
            layout.addLayout(row)
            setattr(self, attr_name, widget)

        # Đổ dữ liệu cho combobox đơn vị và nhà cung cấp
        self.cbo_unit.addItems(["gram", "kg", "ml", "lit", "cái"])
        self.load_suppliers()

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #F1F1F1;
                color: #666;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #E0E0E0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Lưu lại")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #58111A;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #58111A;
            }
        """)
        save_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        v_main = QVBoxLayout(self)
        v_main.addWidget(main_container)
        self.setFixedSize(550, 550)

    def load_suppliers(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ten_ncc FROM nhacungcap ORDER BY ten_ncc")
            for r in cursor.fetchall():
                self.cbo_supplier.addItem(r[1], r[0])
            conn.close()

    def load_data(self):
        self.txt_name.setText(self.data[1])
        self.cbo_unit.setCurrentText(self.data[3])
        self.spin_threshold.setValue(float(self.data[4]))
        # --- THÊM ĐOẠN NÀY: Nạp dữ liệu Max từ mảng data lên SpinBox ---
        if len(self.data) > 7 and self.data[7] is not None:
            self.spin_max.setValue(float(self.data[7]))
        else:
            self.spin_max.setValue(3000.0) # Giá trị mặc định nếu chưa có dữ liệu cũ
        idx = self.cbo_supplier.findData(self.data[5])
        if idx >= 0:
            self.cbo_supplier.setCurrentIndex(idx)
        self.spin_price.setValue(float(self.data[6]))

    def get_data(self):
        return {
            "name": self.txt_name.text().strip(),
            "unit": self.cbo_unit.currentText(),
            "threshold": self.spin_threshold.value(),
            "max_kho": self.spin_max.value(),
            "supplier_id": self.cbo_supplier.currentData(),
            "price": self.spin_price.value()
        }
# ========================== DIALOG THÊM/SỬA NHÀ CUNG CẤP ==========================
class SupplierDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.data = data
        self.setWindowTitle("Thêm nhà cung cấp" if not data else "Sửa nhà cung cấp")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        if data:
            self.load_data()

    def init_ui(self):
        main_container = QFrame(self)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 24px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header = QHBoxLayout()
        icon = QLabel("🏢")
        icon.setStyleSheet("font-size: 32px;")
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Tên nhà cung cấp
        name_lbl = QLabel("Tên nhà cung cấp")
        name_lbl.setStyleSheet("font-weight: bold; color: #555;")
        layout.addWidget(name_lbl)
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("VD: Công ty TNHH ABC")
        self.txt_name.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDD;
                border-radius: 12px;
                padding: 12px 15px;
                background: #F9F9F9;
            }
            QLineEdit:focus {
                border: 1px solid #58111A;
                background: white;
            }
        """)
        layout.addWidget(self.txt_name)

        # Số điện thoại
        phone_lbl = QLabel("Số điện thoại")
        phone_lbl.setStyleSheet("font-weight: bold; color: #555;")
        layout.addWidget(phone_lbl)
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("VD: 0901234567")
        self.txt_phone.setStyleSheet("""
            QLineEdit {
                border: 1px solid #DDD;
                border-radius: 12px;
                padding: 12px 15px;
                background: #F9F9F9;
            }
            QLineEdit:focus {
                border: 1px solid #58111A;
                background: white;
            }
        """)
        layout.addWidget(self.txt_phone)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #F1F1F1;
                color: #666;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #E0E0E0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Lưu lại")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #58111A;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #58111A;
            }
        """)
        save_btn.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        v_main = QVBoxLayout(self)
        v_main.addWidget(main_container)
        self.setFixedSize(450, 380)

    def load_data(self):
        self.txt_name.setText(self.data[1])
        self.txt_phone.setText(self.data[2] if self.data[2] else "")

    def get_data(self):
        return {"name": self.txt_name.text().strip(), "phone": self.txt_phone.text().strip()}

# ========================== DIALOG THÊM/SỬA CÔNG THỨC ==========================
class RecipeDialog(QDialog):
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.product_id = product_id
        self.ingredients = []
        self.setWindowTitle("Thêm công thức" if not product_id else "Sửa công thức")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()
        if product_id:
            self.load_recipe()

    def init_ui(self):
        main_container = QFrame(self)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 24px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        main_container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(main_container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        icon = QLabel("📝")
        icon.setStyleSheet("font-size: 32px;")
        title = QLabel(self.windowTitle())
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2C3E50;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Chọn sản phẩm
        prod_lbl = QLabel("Sản phẩm")
        prod_lbl.setStyleSheet("font-weight: bold; color: #555;")
        layout.addWidget(prod_lbl)
        self.cbo_product = QComboBox()
        self.cbo_product.setStyleSheet("""
            QComboBox {
                border: 1px solid #DDD;
                border-radius: 12px;
                padding: 8px 15px;
                background: #F9F9F9;
            }
        """)
        self.load_products()
        layout.addWidget(self.cbo_product)

        # Giá bán
        price_lbl = QLabel("Giá bán (VNĐ)")
        price_lbl.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
        layout.addWidget(price_lbl)
        self.spin_price = QDoubleSpinBox()
        self.spin_price.setMaximum(100_000_000)
        self.spin_price.setPrefix("₫ ")
        self.spin_price.setStyleSheet("padding: 8px; border-radius: 10px; border: 1px solid #DDD;")
        layout.addWidget(self.spin_price)

        # Danh sách nguyên liệu
        ing_lbl = QLabel("Danh sách nguyên liệu")
        ing_lbl.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
        layout.addWidget(ing_lbl)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Nguyên liệu", "Định lượng", "Đơn vị", "Hành động"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #EEE;
                border-radius: 12px;
                background: white;
            }
            QHeaderView::section {
                background: #F8F9FA;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        add_btn = QPushButton("➕ Thêm nguyên liệu")
        add_btn.setStyleSheet("""
            QPushButton {
                background: #3498DB;
                color: white;
                border-radius: 20px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980B9;
            }
        """)
        add_btn.clicked.connect(self.add_ingredient_row)
        layout.addWidget(add_btn)

        # Hướng dẫn
        inst_lbl = QLabel("Hướng dẫn chế biến")
        inst_lbl.setStyleSheet("font-weight: bold; color: #555; margin-top: 10px;")
        layout.addWidget(inst_lbl)
        self.txt_instruction = QTextEdit()
        self.txt_instruction.setPlaceholderText("Nhập các bước chế biến...")
        self.txt_instruction.setMaximumHeight(100)
        self.txt_instruction.setStyleSheet("""
            QTextEdit {
                border: 1px solid #DDD;
                border-radius: 12px;
                padding: 10px;
                background: #F9F9F9;
            }
            QTextEdit:focus {
                border: 1px solid #58111A;
            }
        """)
        layout.addWidget(self.txt_instruction)

        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #F1F1F1;
                color: #666;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #E0E0E0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Lưu công thức")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #58111A;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #58111A;
            }
        """)
        save_btn.clicked.connect(self.save_recipe)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        v_main = QVBoxLayout(self)
        v_main.addWidget(main_container)
        self.setFixedSize(700, 700)

    def load_products(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ten_sanpham FROM sanpham ORDER BY ten_sanpham")
            for r in cursor.fetchall():
                self.cbo_product.addItem(r[1], r[0])
            conn.close()

    def load_recipe(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT huong_dan, gia_ban FROM sanpham WHERE id = %s", (self.product_id,))
            row = cursor.fetchone()
            if row:
                self.txt_instruction.setText(row['huong_dan'] or "")
                self.spin_price.setValue(row['gia_ban'] or 0)
            cursor.execute("""
                SELECT nl.id, nl.ten_nguyenlieu, ct.dinh_luong, nl.don_vi
                FROM congthuc ct
                JOIN nguyenlieu nl ON ct.id_nguyenlieu = nl.id
                WHERE ct.id_sanpham = %s
            """, (self.product_id,))
            rows = cursor.fetchall()
            for r in rows:
                self.ingredients.append({
                    "id": r['id'],
                    "name": r['ten_nguyenlieu'],
                    "qty": r['dinh_luong'],
                    "unit": r['don_vi']
                })
            self.refresh_table()
            conn.close()

    def add_ingredient_row(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Chọn nguyên liệu")
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        container = QFrame(dlg)
        container.setStyleSheet("background: white; border-radius: 20px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel("Chọn nguyên liệu")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        cbo = QComboBox()
        cbo.setStyleSheet("padding: 8px; border-radius: 10px; border: 1px solid #DDD;")
        
        # Mở kết nối riêng cho việc load danh sách
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id, ten_nguyenlieu, don_vi FROM nguyenlieu ORDER BY ten_nguyenlieu")
                for r in cursor.fetchall():
                    cbo.addItem(f"{r[1]} ({r[2]})", r[0])
            except Exception as e:
                print(f"Lỗi load nguyên liệu: {e}")
            finally:
                conn.close()
        else:
            QMessageBox.warning(dlg, "Lỗi", "Không thể kết nối database")
            dlg.reject()
            return

        sp_qty = QDoubleSpinBox()
        sp_qty.setMaximum(100000)
        sp_qty.setSuffix(" đơn vị")
        sp_qty.setStyleSheet("padding: 8px; border-radius: 10px; border: 1px solid #DDD;")

        layout.addWidget(QLabel("Nguyên liệu:"))
        layout.addWidget(cbo)
        layout.addWidget(QLabel("Định lượng:"))
        layout.addWidget(sp_qty)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("background: #58111A; color: white; border-radius: 15px; padding: 8px;")
        ok_btn.clicked.connect(dlg.accept)
        cancel_btn = QPushButton("Hủy")
        cancel_btn.setStyleSheet("background: #F1F1F1; border-radius: 15px; padding: 8px;")
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        v_main = QVBoxLayout(dlg)
        v_main.addWidget(container)
        dlg.setFixedSize(400, 350)

        # Lưu id và đơn vị trước khi đóng dialog
        if dlg.exec():
            ing_id = cbo.currentData()
            ing_text = cbo.currentText()
            ing_name = ing_text.split(" (")[0]
            qty = sp_qty.value()
            unit = ""
            # Mở kết nối mới để lấy đơn vị
            conn2 = get_db_connection()
            if conn2:
                try:
                    cursor2 = conn2.cursor()
                    cursor2.execute("SELECT don_vi FROM nguyenlieu WHERE id = %s", (ing_id,))
                    row = cursor2.fetchone()
                    if row:
                        unit = row[0]
                except Exception as e:
                    print(f"Lỗi lấy đơn vị: {e}")
                finally:
                    conn2.close()
            self.ingredients.append({
                "id": ing_id,
                "name": ing_name,
                "qty": qty,
                "unit": unit
            })
            self.refresh_table()

    def refresh_table(self):
        self.table.setRowCount(len(self.ingredients))
        for i, ing in enumerate(self.ingredients):
            self.table.setItem(i, 0, QTableWidgetItem(ing['name']))
            self.table.setItem(i, 1, QTableWidgetItem(str(ing['qty'])))
            self.table.setItem(i, 2, QTableWidgetItem(ing['unit']))
            del_btn = QPushButton("🗑️ Xóa")
            del_btn.setStyleSheet("background: #F44336; color: white; border-radius: 10px; padding: 5px;")
            del_btn.clicked.connect(lambda ch, idx=i: self.delete_row(idx))
            self.table.setCellWidget(i, 3, del_btn)
        self.table.resizeRowsToContents()

    def delete_row(self, idx):
        self.ingredients.pop(idx)
        self.refresh_table()

    def save_recipe(self):
        product_id = self.cbo_product.currentData()
        if not product_id:
            QMessageBox.warning(self, "Lỗi", "Chưa chọn sản phẩm")
            return
        if not self.ingredients:
            QMessageBox.warning(self, "Lỗi", "Công thức cần ít nhất 1 nguyên liệu")
            return

        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE sanpham SET huong_dan = %s, gia_ban = %s WHERE id = %s",
                           (self.txt_instruction.toPlainText(), self.spin_price.value(), product_id))
            cursor.execute("DELETE FROM congthuc WHERE id_sanpham = %s", (product_id,))
            for ing in self.ingredients:
                cursor.execute("INSERT INTO congthuc (id_sanpham, id_nguyenlieu, dinh_luong) VALUES (%s, %s, %s)",
                               (product_id, ing['id'], ing['qty']))
            conn.commit()
            QMessageBox.information(self, "Thành công", "Đã lưu công thức")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu: {e}")
        finally:
            conn.close()
# ========================== CARD THỐNG KÊ ==========================
class InfoCard(QFrame):
    def __init__(self, title, value, color_hex):
        super().__init__()
        self.setFixedHeight(130)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color_hex};
                border-radius: 20px;
            }}
            QLabel {{ color: white; border: none; background: transparent; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        self.val_lbl = QLabel(str(value))
        self.val_lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.title_lbl = QLabel(title)
        self.title_lbl.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.title_lbl)

# ========================== CARD NGUYÊN LIỆU ==========================
class IngredientCard(QFrame):
    def __init__(self, data, parent_app):
        super().__init__()
        self.data = data
        self.parent_app = parent_app
        self.min_val = 5.0      # MIN cố định = 5
        self.max_val = 300.0    # MAX cố định = 300
        self.init_ui()

    def init_ui(self):
        from PyQt6.QtCore import QDate

        self.setStyleSheet("background: white; border-radius: 25px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0,0,0,20))
        shadow.setOffset(0,4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        qty = float(self.data[2])
        
        # Xác định trạng thái với min=5, max=300
        if qty == 0:
            st_txt, st_col = "Hết hàng", "#FF4D4D"
        elif qty <= self.min_val:
            st_txt, st_col = "Sắp hết", "#FFB300"
        elif qty >= self.max_val:
            st_txt, st_col = "Quá tải", "#F44336"
        else:
            st_txt, st_col = "Bình thường", "#4CAF50"

        h = QHBoxLayout()
        name = QLabel(self.data[1])
        name.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        tag = QLabel(st_txt)
        tag.setStyleSheet(f"background: {st_col}22; color: {st_col}; padding: 4px 12px; border-radius: 10px; font-size: 10px; font-weight: bold;")
        h.addWidget(name)
        h.addStretch()
        h.addWidget(tag)
        layout.addLayout(h)

        layout.addWidget(QLabel("Nguyên liệu thô"))
        layout.addWidget(QLabel(f"Tồn kho: {qty} {self.data[3]}"))

        # Progress Bar
        bar = QProgressBar()
        bar.setFixedHeight(8)
        bar.setTextVisible(False)
        
        # Tính phần trăm với min=5, max=300
        if self.max_val > self.min_val:
            if qty <= self.min_val:
                percent = int((qty / self.min_val) * 30) if self.min_val > 0 else 0
            elif qty <= self.max_val:
                percent = 30 + int(((qty - self.min_val) / (self.max_val - self.min_val)) * 40)
            else:
                percent = 70 + int(min(((qty - self.max_val) / self.max_val) * 30, 30))
        else:
            percent = 50
        
        percent = min(100, max(0, percent))
        bar.setValue(int(percent))
        bar.setStyleSheet(f"QProgressBar {{ background: #F5F5F5; border: none; border-radius: 4px; }} QProgressBar::chunk {{ background: {st_col}; }}")
        layout.addWidget(bar)

        # Hiển thị Min/Max
        limit_lay = QHBoxLayout()
        limit_lay.addWidget(QLabel(f"Min: {int(self.min_val)}"))
        limit_lay.addStretch()
        limit_lay.addWidget(QLabel(f"Max: {int(self.max_val)}"))
        layout.addLayout(limit_lay)

        # Phần còn lại giữ nguyên...
        avg_price = float(self.data[6]) if len(self.data) > 6 else 0
        layout.addWidget(QLabel(f"Đơn giá TB: {avg_price:,.0f}đ/{self.data[3]}"))

        latest_price = float(self.data[8]) if len(self.data) > 8 else 0
        self.lbl_latest_price = QLabel(f"Giá nhập mới nhất: {latest_price:,.0f}đ/{self.data[3]}")
        layout.addWidget(self.lbl_latest_price)

        btn_history = QPushButton("📜 Lịch sử giá")
        btn_history.setStyleSheet("background: #3498DB; color: white; border-radius: 10px; height: 30px; font-weight: bold;")
        btn_history.clicked.connect(self.show_price_history)
        layout.addWidget(btn_history)

        layout.addWidget(QLabel(f"Nhà cung cấp: {self.data[5] or 'N/A'}"))

        btns = QHBoxLayout()
        b_in = QPushButton(" ↗ Nhập")
        b_in.setStyleSheet("background: #00C853; color: white; border-radius: 10px; height: 35px; border: none; font-weight: bold;")
        b_out = QPushButton(" ↘ Xuất")
        b_out.setStyleSheet("background: #F44336; color: white; border-radius: 10px; height: 35px; border: none; font-weight: bold;")
        b_adj = QPushButton(" ⚙ Điều chỉnh")
        b_adj.setStyleSheet("background: #80CBC4; color: white; border-radius: 10px; height: 35px; border: none; font-weight: bold;")
        b_edit = QPushButton(" ✏ Sửa")
        b_edit.setStyleSheet("background: #FFC107; color: white; border-radius: 10px; height: 35px; border: none; font-weight: bold;")
        b_del = QPushButton(" 🗑 Xóa")
        b_del.setStyleSheet("background: #F44336; color: white; border-radius: 10px; height: 35px; border: none; font-weight: bold;")
        
        b_in.clicked.connect(lambda: self.parent_app.open_tx("IN", self.data))
        b_out.clicked.connect(lambda: self.parent_app.open_tx("OUT", self.data))
        b_adj.clicked.connect(lambda: self.parent_app.open_tx("ADJUST", self.data))
        b_edit.clicked.connect(lambda: self.parent_app.edit_ingredient(self.data[0], self.data))
        b_del.clicked.connect(lambda: self.parent_app.delete_ingredient(self.data[0], self.data[1]))
        
        btns.addWidget(b_in)
        btns.addWidget(b_out)
        btns.addWidget(b_adj)
        btns.addWidget(b_edit)
        btns.addWidget(b_del)
        layout.addLayout(btns)

    def show_price_history(self):
        dlg = PriceHistoryDialog(self.data[0], self.data[1], self.parent_app)
        dlg.exec()
# ========================== CARD CÔNG THỨC ==========================
class RecipeDetailDialog(QDialog):
    def __init__(self, name, servings, ingredients, instruction, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        container = QFrame(self)
        container.setStyleSheet("background-color: white; border-radius: 30px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0,0,0,60))
        shadow.setOffset(0,10)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(35, 35, 35, 35)

        title = QLabel(name)
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)
        layout.addWidget(QLabel(f"Công thức cho {servings} phần ăn"))
        layout.addSpacing(20)
        layout.addWidget(QLabel("<b>NGUYÊN LIỆU CHI TIẾT:</b>"))
        for ing, qty in ingredients:
            line = QHBoxLayout()
            line.addWidget(QLabel(ing))
            q_lbl = QLabel(qty)
            q_lbl.setStyleSheet("color: #58111A; font-weight: bold;")
            q_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            line.addWidget(q_lbl)
            layout.addLayout(line)
        layout.addSpacing(20)
        layout.addWidget(QLabel("<b>HƯỚNG DẪN:</b>"))
        note = QLabel(instruction if instruction else "Chưa có hướng dẫn cụ thể cho món này.")
        note.setWordWrap(True)
        note.setStyleSheet("background: #FDF7F0; padding: 15px; border-radius: 15px; color: #666; line-height: 140%;")
        layout.addWidget(note)
        btn = QPushButton("Đóng cửa sổ")
        btn.setStyleSheet("background: #58111A; color: white; border-radius: 15px; height: 45px; font-weight: bold; border: none; margin-top: 15px;")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        v_main = QVBoxLayout(self)
        v_main.addWidget(container)
        self.setFixedSize(450, 650)

class RecipeCard(QFrame):
    def __init__(self, product_id, recipe_name, servings, ingredients, instruction, creator, updated_date, parent_app):
        super().__init__()
        self.product_id = product_id
        self.recipe_name = recipe_name
        self.servings = servings
        self.ingredients = ingredients
        self.instruction = instruction
        self.parent_app = parent_app
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: white; border-radius: 25px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0,0,0,25))
        shadow.setOffset(0,5)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        name_lbl = QLabel(recipe_name)
        name_lbl.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(name_lbl)
        sub_lbl = QLabel(f"Nguyên liệu (Cho {servings} phần):")
        sub_lbl.setStyleSheet("color: #888; font-size: 11px; margin-bottom: 15px;")
        layout.addWidget(sub_lbl)
        for i, (ing, qty) in enumerate(ingredients):
            if i > 3:
                more_lbl = QLabel(f"... và {len(ingredients) - 4} nguyên liệu khác")
                more_lbl.setStyleSheet("color: #AAA; font-style: italic; font-size: 11px;")
                layout.addWidget(more_lbl)
                break
            ing_lay = QHBoxLayout()
            lbl_n = QLabel(ing)
            lbl_n.setStyleSheet("color: #333; font-size: 13px;")
            lbl_q = QLabel(qty)
            lbl_q.setStyleSheet("color: #58111A; font-weight: bold; font-size: 13px;")
            lbl_q.setAlignment(Qt.AlignmentFlag.AlignRight)
            ing_lay.addWidget(lbl_n)
            ing_lay.addWidget(lbl_q)
            layout.addLayout(ing_lay)
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("background-color: #F8F8F8; border: none; min-height: 1px; margin: 5px 0px;")
            layout.addWidget(line)
        layout.addStretch()
        footer_txt = f"Cập nhật bởi: {creator}\nNgày: {updated_date}"
        footer = QLabel(footer_txt)
        footer.setStyleSheet("color: #CCC; font-size: 9px; margin-top: 10px;")
        layout.addWidget(footer)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("✏ Sửa")
        edit_btn.setStyleSheet("background: #FFC107; color: white; border-radius: 10px; height: 30px; font-weight: bold;")
        edit_btn.clicked.connect(self.edit_recipe)
        del_btn = QPushButton("🗑 Xóa")
        del_btn.setStyleSheet("background: #F44336; color: white; border-radius: 10px; height: 30px; font-weight: bold;")
        del_btn.clicked.connect(self.delete_recipe)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dlg = RecipeDetailDialog(self.recipe_name, self.servings, self.ingredients, self.instruction, self)
            dlg.exec()

    def edit_recipe(self):
        dlg = RecipeDialog(self.parent_app, self.product_id)
        if dlg.exec():
            self.parent_app.load_recipes()

    def delete_recipe(self):
        reply = QMessageBox.question(self, "Xác nhận", f"Xóa công thức của món '{self.recipe_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM congthuc WHERE id_sanpham = %s", (self.product_id,))
                    cursor.execute("UPDATE sanpham SET huong_dan = NULL WHERE id = %s", (self.product_id,))
                    conn.commit()
                    QMessageBox.information(self.parent_app, "Thành công", "Đã xóa công thức")
                    self.parent_app.load_recipes()
                except Exception as e:
                    QMessageBox.critical(self.parent_app, "Lỗi", str(e))
                finally:
                    conn.close()

# ========================== CARD LỊCH SỬ ==========================
class HistoryCard(QFrame):
    def __init__(self, type_tx, item_name, qty, old_qty, new_qty, reason, user, date):
        super().__init__()
        self.setFixedHeight(150)
        self.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #F0F0F0;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)

        h1 = QHBoxLayout()
        is_in = qty > 0
        tag_col = "#27AE60" if is_in else "#E74C3C"
        tag_txt = "↗ Nhập kho" if is_in else "↘ Xuất kho"
        tag = QLabel(tag_txt)
        tag.setStyleSheet(f"background: {tag_col}22; color: {tag_col}; padding: 5px 12px; border-radius: 10px; font-weight: bold; font-size: 10px;")
        name = QLabel(item_name)
        name.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        h1.addWidget(tag)
        h1.addWidget(name)
        h1.addStretch()
        layout.addLayout(h1)

        h2 = QHBoxLayout()
        for label, val, col in [("Số lượng", f"{'+' if is_in else ''}{qty}", tag_col),
                                ("Tồn trước", old_qty, "#333"),
                                ("Tồn sau", new_qty, "#333")]:
            v_lay = QVBoxLayout()
            v_lay.addWidget(QLabel(label, styleSheet="color: #888; font-size: 11px;"))
            val_lbl = QLabel(str(val))
            val_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            val_lbl.setStyleSheet(f"color: {col};")
            v_lay.addWidget(val_lbl)
            h2.addLayout(v_lay)
            h2.addStretch()
        layout.addLayout(h2)

        footer = QHBoxLayout()
        footer.addWidget(QLabel(f"Lý do: {reason if reason else 'Không có'}", styleSheet="color: #666; font-style: italic;"))
        footer.addStretch()
        footer.addWidget(QLabel(f"👤 {user}  |  🕒 {date}", styleSheet="color: #AAA; font-size: 10px;"))
        layout.addLayout(footer)

# ========================== CARD NHÀ CUNG CẤP ==========================
class SupplierCard(QFrame):
    def __init__(self, data, parent_app):
        super().__init__()
        self.data = data
        self.parent_app = parent_app
        self.setFixedHeight(120)
        self.setStyleSheet("background: white; border-radius: 20px; border: 1px solid #F0F0F0;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)

        h1 = QHBoxLayout()
        icon = QLabel("🏢")
        name = QLabel(data[1])
        name.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        h1.addWidget(icon)
        h1.addWidget(name)
        h1.addStretch()
        layout.addLayout(h1)

        h2 = QHBoxLayout()
        phone_lbl = QLabel(f"📞 Số điện thoại: <b>{data[2] if data[2] else 'N/A'}</b>")
        phone_lbl.setStyleSheet("color: #555; font-size: 13px;")
        h2.addWidget(phone_lbl)
        layout.addLayout(h2)

        footer = QLabel(f"ID Đối tác: #{data[0]}")
        footer.setStyleSheet("color: #CCC; font-size: 10px;")
        layout.addWidget(footer)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("✏ Sửa")
        edit_btn.setStyleSheet("background: #FFC107; color: white; border-radius: 10px; height: 30px; font-weight: bold;")
        edit_btn.clicked.connect(self.edit_supplier)
        del_btn = QPushButton("🗑 Xóa")
        del_btn.setStyleSheet("background: #F44336; color: white; border-radius: 10px; height: 30px; font-weight: bold;")
        del_btn.clicked.connect(self.delete_supplier)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

    def edit_supplier(self):
        self.parent_app.edit_supplier(self.data[0], self.data)

    def delete_supplier(self):
        self.parent_app.delete_supplier(self.data[0], self.data[1])

class ExpiryManagementDialog(QDialog):
    def __init__(self, ingredient_id, ingredient_name, parent=None):
        super().__init__(parent)
        self.ingredient_id = ingredient_id
        self.ingredient_name = ingredient_name
        self.setWindowTitle(f"Quản lý hạn sử dụng - {ingredient_name}")
        self.setMinimumSize(800, 500)
        self.setStyleSheet("background-color: white; border-radius: 12px;")
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"📅 CÁC LÔ NHẬP CỦA: {self.ingredient_name}")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #58111A;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Ngày nhập", "Số lượng", "Ngày SX", "Hạn SD", "Hành động"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(35)
        btn_close.setStyleSheet("background: #58111A; color: white; font-weight: bold; border-radius: 5px;")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def load_data(self):
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, ngay_gd, so_luong, ngay_sx, ngay_hh
            FROM lichsu_kho
            WHERE ten_nl = %s AND loai_gd = 'IN' AND ngay_hh IS NOT NULL
            ORDER BY ngay_hh ASC
        """, (self.ingredient_name,))
        rows = cursor.fetchall()
        db.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(row['ngay_gd'].strftime("%d/%m/%Y %H:%M:%S")))
            self.table.setItem(i, 2, QTableWidgetItem(f"{float(row['so_luong']):,.2f}"))
            sx_str = row['ngay_sx'].strftime("%d/%m/%Y") if row['ngay_sx'] else ""
            hh_str = row['ngay_hh'].strftime("%d/%m/%Y") if row['ngay_hh'] else ""
            self.table.setItem(i, 3, QTableWidgetItem(sx_str))
            self.table.setItem(i, 4, QTableWidgetItem(hh_str))

            # Nút sửa
            edit_btn = QPushButton("✏ Sửa")
            edit_btn.setStyleSheet("background: #3498DB; color: white; border-radius: 8px; padding: 4px;")
            edit_btn.clicked.connect(lambda ch, idx=row['id'], cur_sx=row['ngay_sx'], cur_hh=row['ngay_hh']: self.edit_expiry(idx, cur_sx, cur_hh))
            # Nút xóa
            del_btn = QPushButton("🗑 Xóa")
            del_btn.setStyleSheet("background: #F44336; color: white; border-radius: 8px; padding: 4px;")
            del_btn.clicked.connect(lambda ch, idx=row['id'], qty=float(row['so_luong']): self.delete_lot(idx, qty))

            widget = QWidget()
            btn_layout = QHBoxLayout(widget)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(i, 5, widget)

    def edit_expiry(self, log_id, old_sx, old_hh):
        dlg = QDialog(self)
        dlg.setWindowTitle("Sửa ngày sản xuất / hạn sử dụng")
        dlg.setModal(True)
        layout = QVBoxLayout(dlg)

        layout.addWidget(QLabel("Ngày sản xuất:"))
        sx_edit = QDateEdit()
        sx_edit.setCalendarPopup(True)
        if old_sx:
            sx_edit.setDate(QDate(old_sx.year, old_sx.month, old_sx.day))
        else:
            sx_edit.setDate(QDate.currentDate())
        sx_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(sx_edit)

        layout.addWidget(QLabel("Hạn sử dụng:"))
        hh_edit = QDateEdit()
        hh_edit.setCalendarPopup(True)
        if old_hh:
            hh_edit.setDate(QDate(old_hh.year, old_hh.month, old_hh.day))
        else:
            hh_edit.setDate(QDate.currentDate().addDays(30))
        hh_edit.setDisplayFormat("dd/MM/yyyy")
        layout.addWidget(hh_edit)

        btn_save = QPushButton("Lưu lại")
        btn_save.setStyleSheet("background: #27AE60; color: white; border-radius: 10px; height: 35px;")
        btn_save.clicked.connect(lambda: self.save_expiry(log_id, sx_edit.date().toPyDate(), hh_edit.date().toPyDate(), dlg))
        layout.addWidget(btn_save)

        dlg.exec()

    def save_expiry(self, log_id, new_sx, new_hh, dialog):
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor()
        cursor.execute("UPDATE lichsu_kho SET ngay_sx = %s, ngay_hh = %s WHERE id = %s", (new_sx, new_hh, log_id))
        db.commit()
        db.close()
        QMessageBox.information(self, "Thành công", "Đã cập nhật hạn sử dụng.")
        dialog.accept()
        self.load_data()
        # Refresh lại main grid
        self.parent().load_data()

    def delete_lot(self, log_id, qty):
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor(dictionary=True)

        # Lấy ngày nhập của lô
        cursor.execute("SELECT ngay_gd FROM lichsu_kho WHERE id = %s", (log_id,))
        row = cursor.fetchone()
        if not row:
            db.close()
            return
        import_date = row['ngay_gd']

        # Kiểm tra có giao dịch OUT nào sau ngày nhập không
        cursor.execute("""
            SELECT COUNT(*) as cnt
            FROM lichsu_kho
            WHERE ten_nl = %s AND loai_gd = 'OUT' AND ngay_gd >= %s
        """, (self.ingredient_name, import_date))
        out_count = cursor.fetchone()['cnt']

        if out_count > 0:
            QMessageBox.warning(self, "Không thể xóa", "Lô này đã có phát sinh xuất kho sau ngày nhập. Không thể xóa vì ảnh hưởng đến tồn kho.")
            db.close()
            return

        reply = QMessageBox.question(self, "Xác nhận xóa lô", f"Xóa lô nhập ngày {import_date.strftime('%d/%m/%Y')} với số lượng {qty}?\n\nSố lượng này sẽ bị trừ khỏi tồn kho hiện tại.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            db.close()
            return

        # Cập nhật tồn kho nguyên liệu
        cursor.execute("SELECT so_luong FROM nguyenlieu WHERE ten_nguyenlieu = %s", (self.ingredient_name,))
        cur = cursor.fetchone()
        if not cur:
            db.close()
            return
        current_qty = float(cur['so_luong'])
        new_qty = current_qty - qty
        if new_qty < 0:
            QMessageBox.warning(self, "Lỗi tồn kho", f"Sau khi xóa lô, tồn kho sẽ âm ({new_qty}). Không thể xóa.")
            db.close()
            return

        cursor.execute("UPDATE nguyenlieu SET so_luong = %s WHERE ten_nguyenlieu = %s", (new_qty, self.ingredient_name))

        # Ghi lịch sử điều chỉnh – lấy tên người dùng an toàn
        user_name = "Hệ thống"
        if hasattr(self.parent(), 'user_info') and self.parent().user_info:
            user_name = self.parent().user_info.get('ho_ten', 'Hệ thống')
        log_reason = f"[Hệ thống] Xóa lô nhập ID {log_id} (SL {qty}) do quản lý hạn sử dụng"
        cursor.execute("""
            INSERT INTO lichsu_kho (loai_gd, ten_nl, so_luong, ton_truoc, ton_sau, ly_do, nguoi_dung, ngay_gd)
            VALUES ('ADJUST', %s, %s, %s, %s, %s, %s, NOW())
        """, (self.ingredient_name, -qty, current_qty, new_qty, log_reason, user_name))

        # Xóa bản ghi lịch sử nhập lô
        cursor.execute("DELETE FROM lichsu_kho WHERE id = %s", (log_id,))

        db.commit()
        db.close()
        QMessageBox.information(self, "Thành công", f"Đã xóa lô và cập nhật tồn kho còn {new_qty}.")
        self.load_data()
        self.parent().load_data()  # Refresh main grid

# ========================== CỬA SỔ CHÍNH ==========================
class WarehouseApp(QMainWindow):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info if user_info else {"ho_ten": "Hệ thống", "vai_tro": "Quản trị"}
        self.setWindowTitle("Quản lý kho coffee - Pro")
        self.resize(1200, 950)
        self.setStyleSheet("QMainWindow { background-color: #FDF7F0; }")

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(30, 20, 30, 20)

        self.tab_active = "background: #58111A; color: white; padding: 8px 20px; border-radius: 10px; font-weight: bold; border: none;"
        self.tab_inactive = "background: white; color: #555; padding: 8px 20px; border-radius: 10px; border: 1px solid #DDD;"

        # Banner cảnh báo
        self.alarm = QFrame()
        self.alarm.setStyleSheet("background: white; border: 1px solid #FF4D4D; border-left: 5px solid #FF4D4D; border-radius: 12px;")
        al_lay = QHBoxLayout(self.alarm)
        self.al_txt = QLabel("")
        al_lay.addWidget(QLabel("⚠️"))
        al_lay.addWidget(self.al_txt)
        al_lay.addStretch()
        self.main_layout.addWidget(self.alarm)
        self.alarm.hide()

        # Header
        header_lay = QHBoxLayout()
        title = QLabel("Quản lý kho")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        user_label = QLabel(f"👤 {self.user_info['ho_ten']}")
        user_label.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        header_lay.addWidget(title)
        header_lay.addStretch()
        header_lay.addWidget(user_label)
        self.main_layout.addLayout(header_lay)

        # Dashboard
        self.dash_layout = QHBoxLayout()
        self.card_total = InfoCard("Loại nguyên liệu", 0, "#F39C12")
        self.card_low = InfoCard("Sắp hết nguyên liệu", 0, "#E74C3C")
        self.card_formula = InfoCard("Công thức", 0, "#2ECC71")
        self.card_value = InfoCard("Giá trị tồn", "0đ", "#8E44AD")
        self.card_avg_cost = InfoCard("Giá TB nguyên liệu", "0đ/kg", "#3498DB")
        for c in [self.card_total, self.card_low, self.card_formula, self.card_value, self.card_avg_cost]:
            self.dash_layout.addWidget(c)
        self.main_layout.addLayout(self.dash_layout)

        # Toolbar
        toolbar = QHBoxLayout()
        btn_add_ing = QPushButton("➕ Thêm nguyên liệu")
        btn_add_ing.clicked.connect(self.add_ingredient)
        btn_add_supp = QPushButton("🏢 Thêm nhà cung cấp")
        btn_add_supp.clicked.connect(self.add_supplier)
        btn_add_recipe = QPushButton("📝 Thêm công thức")
        btn_add_recipe.clicked.connect(self.add_recipe)
        toolbar.addWidget(btn_add_ing)
        toolbar.addWidget(btn_add_supp)
        toolbar.addWidget(btn_add_recipe)
        toolbar.addStretch()
        self.main_layout.addLayout(toolbar)

        # Tìm kiếm
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm kiếm nhanh nguyên liệu, công thức...")
        self.txt_search.setFixedHeight(45)
        self.txt_search.setStyleSheet("""
            QLineEdit {
                background: white; border: 1px solid #DDD; border-radius: 15px;
                padding-left: 15px; font-size: 14px; margin: 10px 0px;
            }
        """)
        self.txt_search.textChanged.connect(self.dispatch_search)
        self.main_layout.addWidget(self.txt_search)

        # Bộ lọc
        self.filter_layout = QHBoxLayout()
        self.filter_layout.setContentsMargins(0, 5, 0, 10)
        self.filter_layout.setSpacing(15)
        self.filter_supplier = QComboBox()
        self.filter_supplier.addItem("📦 Tất cả nhà cung cấp", None)
        self.filter_supplier.currentIndexChanged.connect(self.on_filter_changed)
        self.filter_status = QComboBox()
        self.filter_status.addItem("📊 Tất cả trạng thái", None)
        self.filter_status.addItem("🔴 Hết hàng (tồn = 0)")
        self.filter_status.addItem("🟡 Sắp hết (tồn ≤ ngưỡng)")
        self.filter_status.addItem("🟢 Bình thường")
        self.filter_status.currentIndexChanged.connect(self.on_filter_changed)
        self.filter_category = QComboBox()
        self.filter_category.addItem("📂 Tất cả danh mục", None)
        self.filter_category.currentIndexChanged.connect(self.on_filter_changed)
        self.filter_history_type = QComboBox()
        self.filter_history_type.addItem("🔄 Tất cả giao dịch", None)
        self.filter_history_type.addItem("📥 Nhập kho")
        self.filter_history_type.addItem("📤 Xuất kho")
        self.filter_history_type.addItem("⚙️ Điều chỉnh")
        self.filter_history_type.currentIndexChanged.connect(self.on_filter_changed)
        self.filter_layout.addWidget(QLabel("🔍 Lọc nâng cao:"))
        self.filter_layout.addWidget(self.filter_supplier)
        self.filter_layout.addWidget(self.filter_status)
        self.filter_layout.addWidget(self.filter_category)
        self.filter_layout.addWidget(self.filter_history_type)
        self.filter_layout.addStretch()
        self.filter_supplier.hide()
        self.filter_status.hide()
        self.filter_category.hide()
        self.filter_history_type.hide()
        self.main_layout.addLayout(self.filter_layout)

        # Tab bar
        tab_lay = QHBoxLayout()
        self.btn_nl = QPushButton("🍊 Nguyên liệu")
        self.btn_ct = QPushButton("📝 Công thức")
        self.btn_his = QPushButton("🕒 Lịch sử")
        self.btn_ncc = QPushButton("🏢 Nhà cung cấp")
        self.btn_profit = QPushButton("📊 Lợi nhuận")
        self.btn_report = QPushButton("📊 Báo cáo kho")
        self.btn_nl.clicked.connect(self.on_tab_clicked)
        self.btn_ct.clicked.connect(self.on_tab_clicked)
        self.btn_his.clicked.connect(self.on_tab_clicked)
        self.btn_ncc.clicked.connect(self.on_tab_clicked)
        self.btn_profit.clicked.connect(self.on_tab_clicked)
        self.btn_report.clicked.connect(self.on_tab_clicked)
        tab_lay.addWidget(self.btn_nl)
        tab_lay.addWidget(self.btn_ct)
        tab_lay.addWidget(self.btn_his)
        tab_lay.addWidget(self.btn_ncc)
        tab_lay.addWidget(self.btn_profit)
        tab_lay.addWidget(self.btn_report)
        tab_lay.addStretch()
        self.main_layout.addLayout(tab_lay)

        # Grid hiển thị
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(25)
        self.scroll.setWidget(self.container)
        self.main_layout.addWidget(self.scroll)

        self.ensure_columns()
        self.ensure_expiry_columns()
        self.ensure_selling_price_column()  # Thêm cột giá bán
        self.load_filter_options()
        self.load_data()
        self.show_low_stock_notification()
        

    # ------------------ Hỗ trợ hạn sử dụng ------------------
    def ensure_expiry_columns(self):
        """Thêm cột ngày sản xuất và hạn sử dụng vào bảng lichsu_kho nếu chưa có"""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("ALTER TABLE lichsu_kho ADD COLUMN ngay_sx DATE DEFAULT NULL")
                conn.commit()
            except:
                pass
            try:
                cursor.execute("ALTER TABLE lichsu_kho ADD COLUMN ngay_hh DATE DEFAULT NULL")
                conn.commit()
            except:
                pass
            conn.close()

    def ensure_selling_price_column(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("ALTER TABLE sanpham ADD COLUMN gia_ban FLOAT DEFAULT 0")
                conn.commit()
            except:
                pass
            conn.close()

    def get_nearest_expiry(self, ingredient_name):
        """Trả về ngày hết hạn gần nhất của lô CÒN TỒN (dựa trên tồn lũy kế)"""
        conn = get_db_connection()
        if not conn:
            return None, None
        cursor = conn.cursor(dictionary=True)
        # Lấy tất cả các lô IN có hạn, sắp xếp theo hạn tăng dần
        cursor.execute("""
            SELECT id, ngay_hh, so_luong, ngay_gd
            FROM lichsu_kho
            WHERE ten_nl = %s AND loai_gd = 'IN' AND ngay_hh IS NOT NULL
            ORDER BY ngay_hh ASC
        """, (ingredient_name,))
        lots = cursor.fetchall()
        conn.close()
        
        # Duyệt từng lô, tính tồn thực tế (bằng cách trừ đi các giao dịch OUT sau ngày nhập lô)
        for lot in lots:
            # Tính tổng xuất sau ngày nhập lô này
            conn2 = get_db_connection()
            if not conn2:
                continue
            cursor2 = conn2.cursor(dictionary=True)
            cursor2.execute("""
                SELECT COALESCE(SUM(-so_luong), 0) as total_out
                FROM lichsu_kho
                WHERE ten_nl = %s AND loai_gd = 'OUT' AND ngay_gd >= %s
            """, (ingredient_name, lot['ngay_gd']))
            out_qty = cursor2.fetchone()['total_out']
            conn2.close()
            
            # Nếu lượng xuất sau lô này nhỏ hơn số lượng lô thì lô vẫn còn tồn
            if out_qty < lot['so_luong']:
                return lot['ngay_hh'], lot['so_luong'] - out_qty
        return None, None
    # ------------------ Các phương thức hiện có (giữ nguyên, chỉ sửa open_tx) ------------------
    def ensure_columns(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("ALTER TABLE lichsu_kho ADD COLUMN gia_nhap FLOAT DEFAULT NULL")
                conn.commit()
            except:
                pass
            conn.close()

    def load_filter_options(self):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, ten_ncc FROM nhacungcap ORDER BY ten_ncc")
            self.filter_supplier.clear()
            self.filter_supplier.addItem("📦 Tất cả nhà cung cấp", None)
            for row in cursor.fetchall():
                self.filter_supplier.addItem(row[1], row[0])
            cursor.execute("SELECT id, ten_danhmuc FROM danhmuc ORDER BY ten_danhmuc")
            self.filter_category.clear()
            self.filter_category.addItem("📂 Tất cả danh mục", None)
            for row in cursor.fetchall():
                self.filter_category.addItem(row[1], row[0])
            conn.close()

    def on_filter_changed(self):
        if self.btn_nl.styleSheet() == self.tab_active:
            self.load_data()
        elif self.btn_ct.styleSheet() == self.tab_active:
            self.load_recipes()
        elif self.btn_his.styleSheet() == self.tab_active:
            self.load_history()

    def on_tab_clicked(self):
        sender = self.sender()
        if sender == self.btn_nl:
            self.load_data()
            self.filter_supplier.show()
            self.filter_status.show()
            self.filter_category.hide()
            self.filter_history_type.hide()
            self.txt_search.setPlaceholderText("🔍 Tìm kiếm nguyên liệu...")
            self.txt_search.show()
        elif sender == self.btn_ct:
            self.load_recipes()
            self.filter_supplier.hide()
            self.filter_status.hide()
            self.filter_category.show()
            self.filter_history_type.hide()
            self.txt_search.setPlaceholderText("🔍 Tìm kiếm công thức...")
            self.txt_search.show()
        elif sender == self.btn_his:
            self.load_history()
            self.filter_supplier.hide()
            self.filter_status.hide()
            self.filter_category.hide()
            self.filter_history_type.show()
            self.txt_search.setPlaceholderText("🔍 Tìm theo tên nguyên liệu hoặc lý do...")
            self.txt_search.show()
        elif sender == self.btn_ncc:
            self.load_suppliers()
            self.filter_supplier.hide()
            self.filter_status.hide()
            self.filter_category.hide()
            self.filter_history_type.hide()
            self.txt_search.setPlaceholderText("🔍 Tìm tên hoặc số điện thoại nhà cung cấp...")
            self.txt_search.show()
        elif sender == self.btn_profit:
            self.load_profit_stats()
            self.filter_supplier.hide()
            self.filter_status.hide()
            self.filter_category.hide()
            self.filter_history_type.hide()
            self.txt_search.hide()
        elif sender == self.btn_report:
            self.load_report()
            self.filter_supplier.hide()
            self.filter_status.hide()
            self.filter_category.hide()
            self.filter_history_type.hide()
            self.txt_search.hide()
        else:
            self.load_data()

    # ========== Các hàm tính toán giữ nguyên ==========
    def get_average_material_cost(self, cursor):
        query = "SELECT ten_nguyenlieu, gia_nhap, don_vi FROM nguyenlieu WHERE gia_nhap > 0"
        cursor.execute(query)
        rows = cursor.fetchall()
        if not rows:
            return 0
        total_cost = 0
        count = 0
        for row in rows:
            gia = float(row['gia_nhap'])
            don_vi = row['don_vi'] or ''
            if don_vi.lower() == 'gram':
                gia_kg = gia * 1000
            elif don_vi.lower() == 'kg':
                gia_kg = gia
            elif don_vi.lower() == 'ml':
                gia_kg = gia * 1000
            elif don_vi.lower() == 'lit':
                gia_kg = gia
            else:
                gia_kg = gia
            total_cost += gia_kg
            count += 1
        return total_cost / count if count > 0 else 0

    def get_product_cost(self, cursor):
        query = """
            SELECT c.id_sanpham, COALESCE(SUM(c.dinh_luong * n.gia_nhap), 0) as gia_von
            FROM congthuc c
            JOIN nguyenlieu n ON c.id_nguyenlieu = n.id
            GROUP BY c.id_sanpham
        """
        cursor.execute(query)
        result = {}
        for row in cursor.fetchall():
            result[row['id_sanpham']] = float(row['gia_von'])
        return result

    def get_date_condition(self, filter_text):
        if filter_text == "7 ngày gần đây":
            return "h.ngay_tao >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif filter_text == "4 tuần gần đây":
            return "h.ngay_tao >= DATE_SUB(NOW(), INTERVAL 4 WEEK)"
        elif filter_text == "Các tháng trong năm":
            return "YEAR(h.ngay_tao) = YEAR(NOW())"
        else:
            return "YEAR(h.ngay_tao) = YEAR(NOW())"

    def get_period_profit_stats(self, cursor, period_filter):
        date_condition = self.get_date_condition(period_filter)
        product_costs = self.get_product_cost(cursor)
        if period_filter == "7 ngày gần đây":
            date_format = "DATE_FORMAT(h.ngay_tao, '%d/%m')"
            group_by = "DATE(h.ngay_tao)"
            sort_by = "h.ngay_tao"
        elif period_filter == "4 tuần gần đây":
            date_format = "CONCAT('Tuần ', WEEK(h.ngay_tao))"
            group_by = "WEEK(h.ngay_tao)"
            sort_by = "MIN(h.ngay_tao)"
        elif period_filter == "Các tháng trong năm":
            date_format = "DATE_FORMAT(h.ngay_tao, '%m/%Y')"
            group_by = "MONTH(h.ngay_tao), YEAR(h.ngay_tao)"
            sort_by = "MIN(h.ngay_tao)"
        else:
            date_format = "YEAR(h.ngay_tao)"
            group_by = "YEAR(h.ngay_tao)"
            sort_by = "YEAR(h.ngay_tao)"

        query = f"""
            SELECT 
                {date_format} as period_label,
                {group_by} as period_key,
                SUM(h.tong_tien) as total_rev,
                GROUP_CONCAT(CONCAT(ct.id_sanpham, ':', ct.so_luong)) as items
            FROM chitietdonhang h
            JOIN chitiethoadon ct ON h.id = ct.id_hoadon
            WHERE {date_condition}
            GROUP BY {group_by}
            ORDER BY {sort_by} ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        stats = []
        for row in rows:
            rev = float(row['total_rev'] or 0)
            cost = 0
            if row['items']:
                for item in row['items'].split(','):
                    parts = item.split(':')
                    if len(parts) == 2:
                        sp_id = int(parts[0])
                        so_luong = int(parts[1])
                        cost += so_luong * product_costs.get(sp_id, 0)
            profit = rev - cost
            margin = (profit / rev * 100) if rev > 0 else 0
            stats.append({
                "period": row['period_label'],
                "revenue": rev,
                "cost": cost,
                "profit": profit,
                "margin": margin
            })
        return stats

    def format_currency(self, val):
        try:
            int_val = int(round(val))
            return f"{int_val:,}đ".replace(",", ".")
        except:
            return "0đ"

    def dispatch_search(self):
        if self.btn_nl.styleSheet() == self.tab_active:
            self.load_data()
        elif self.btn_ct.styleSheet() == self.tab_active:
            self.load_recipes()
        elif self.btn_his.styleSheet() == self.tab_active:
            self.load_history()
        elif self.btn_ncc.styleSheet() == self.tab_active:
            self.load_suppliers()
        elif self.btn_profit.styleSheet() == self.tab_active:
            # Refresh các bảng lợi nhuận nếu đang mở
            if hasattr(self, 'summary_profit_table'):
                self.refresh_summary_profit()
            if hasattr(self, 'ingredient_profit_table'):
                self.refresh_ingredient_profit()

    def clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def load_suppliers(self):
        self.btn_nl.setStyleSheet(self.tab_inactive)
        self.btn_ct.setStyleSheet(self.tab_inactive)
        self.btn_his.setStyleSheet(self.tab_inactive)
        self.btn_ncc.setStyleSheet(self.tab_active)
        self.btn_profit.setStyleSheet(self.tab_inactive)
        self.txt_search.show()
        self.clear_grid()
        search_text = self.txt_search.text().strip()
        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = "SELECT id, ten_ncc, sdt FROM nhacungcap"
            if search_text:
                query += " WHERE ten_ncc LIKE %s OR sdt LIKE %s"
                cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            else:
                query += " ORDER BY ten_ncc ASC"
                cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                lbl = QLabel("Không tìm thấy nhà cung cấp nào.")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: #888; font-size: 14px; margin-top: 30px;")
                self.grid.addWidget(lbl, 0, 0, 1, 2)
                return
            for i, r in enumerate(rows):
                card = SupplierCard(r, self)
                self.grid.addWidget(card, i // 2, i % 2)
            self.grid.setRowStretch((len(rows)//2) + 1, 1)
        finally:
            conn.close()

    def load_history(self):
        self.btn_nl.setStyleSheet(self.tab_inactive)
        self.btn_ct.setStyleSheet(self.tab_inactive)
        self.btn_his.setStyleSheet(self.tab_active)
        self.btn_ncc.setStyleSheet(self.tab_inactive)
        self.btn_profit.setStyleSheet(self.tab_inactive)
        self.txt_search.show()
        self.clear_grid()
        search_text = self.txt_search.text().strip()
        history_type = self.filter_history_type.currentIndex()
        type_map = {1: 'IN', 2: 'OUT', 3: 'ADJUST'}
        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = "SELECT loai_gd, ten_nl, so_luong, ton_truoc, ton_sau, ly_do, nguoi_dung, ngay_gd FROM lichsu_kho WHERE 1=1"
            params = []
            if search_text:
                query += " AND (ten_nl LIKE %s OR ly_do LIKE %s)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            if history_type in type_map:
                query += " AND loai_gd = %s"
                params.append(type_map[history_type])
            query += " ORDER BY ngay_gd DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if not rows:
                lbl = QLabel("Không tìm thấy lịch sử phù hợp.")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: #888; font-size: 15px; margin-top: 50px;")
                self.grid.addWidget(lbl, 0, 0, 1, 2)
                return
            for i, r in enumerate(rows):
                d_str = r[7].strftime("%H:%M %d/%m/%Y") if hasattr(r[7], 'strftime') else str(r[7])
                card = HistoryCard(r[0], r[1], r[2], r[3], r[4], r[5], r[6], d_str)
                self.grid.addWidget(card, i, 0, 1, 2)
            self.grid.setRowStretch(len(rows), 1)
        finally:
            conn.close()

    def load_data(self):
        self.btn_nl.setStyleSheet(self.tab_active)
        self.btn_ct.setStyleSheet(self.tab_inactive)
        self.btn_his.setStyleSheet(self.tab_inactive)
        self.btn_ncc.setStyleSheet(self.tab_inactive)
        self.btn_profit.setStyleSheet(self.tab_inactive)
        self.clear_grid()
        search_text = self.txt_search.text().strip()
        supplier_id = self.filter_supplier.currentData()
        status_filter = self.filter_status.currentIndex()
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT nl.id, nl.ten_nguyenlieu, nl.so_luong, nl.don_vi, nl.nguong_canh_bao, ncc.ten_ncc, nl.gia_nhap 
                FROM nguyenlieu nl 
                LEFT JOIN nhacungcap ncc ON nl.id_ncc = ncc.id
                WHERE 1=1
            """
            params = []
            if search_text:
                query += " AND nl.ten_nguyenlieu LIKE %s"
                params.append(f"%{search_text}%")
            if supplier_id:
                query += " AND nl.id_ncc = %s"
                params.append(supplier_id)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            filtered_rows = []
            for r in rows:
                qty = float(r['so_luong'])
                threshold = float(r['nguong_canh_bao'])
                if status_filter == 1:
                    if qty == 0:
                        filtered_rows.append(r)
                elif status_filter == 2:
                    if 0 < qty <= threshold:
                        filtered_rows.append(r)
                elif status_filter == 3:
                    if qty > threshold:
                        filtered_rows.append(r)
                else:
                    filtered_rows.append(r)
            total_val = 0.0
            low_count = 0
            crit = []
            for r in filtered_rows:
                q, p = float(r['so_luong']), float(r['gia_nhap'])
                total_val += q * p
                if q <= float(r['nguong_canh_bao']):
                    low_count += 1
                if q == 0:
                    crit.append(r['ten_nguyenlieu'])
            self.card_total.val_lbl.setText(str(len(filtered_rows)))
            self.card_low.val_lbl.setText(str(low_count))
            self.card_value.val_lbl.setText(f"{total_val/1000000:.1f}M" if total_val >= 1000000 else f"{total_val/1000:,.0f}k")
            cursor.execute("SELECT COUNT(DISTINCT id_sanpham) FROM congthuc")
            real_formula_count = cursor.fetchone()['COUNT(DISTINCT id_sanpham)'] or 0
            self.card_formula.val_lbl.setText(str(real_formula_count))
            avg_cost = self.get_average_material_cost(cursor)
            if avg_cost >= 1000:
                self.card_avg_cost.val_lbl.setText(f"{avg_cost/1000:.1f}00đ/kg")
            else:
                self.card_avg_cost.val_lbl.setText(f"{avg_cost:.0f}đ/kg")
            if crit:
                self.alarm.show()
                self.al_txt.setText(f"Cảnh báo: {len(crit)} nguyên liệu đã hết hàng! ({', '.join(crit)})")
            else:
                self.alarm.hide()

            # --- KHU VỰC ĐÃ SỬA: ĐƯA DỮ LIỆU ĐỘNG VÀO INGREDIENT CARD VÀ LAYOUT GRID ---
            price_cursor = conn.cursor(dictionary=True)
            for i, r in enumerate(filtered_rows):
                latest_price = 0
                price_cursor.execute("""
                    SELECT gia_nhap FROM lichsu_kho 
                    WHERE ten_nl = %s AND loai_gd = 'IN' 
                    ORDER BY ngay_gd DESC LIMIT 1
                """, (r['ten_nguyenlieu'],))
                latest_row = price_cursor.fetchone()
                if latest_row and latest_row['gia_nhap']:
                    latest_price = latest_row['gia_nhap']
                
                # --- ĐOẠN XỬ LÝ TRỰC QUAN HÓA CHO TỪNG CARD ---
                ton_kho = float(r['so_luong'])
                nguong_canh_bao = float(r['nguong_canh_bao'])
                
                # Định nghĩa max_kho cho nguyên liệu (ví dụ mặc định là 3000 hoặc tùy ý bạn cấu hình)
                max_kho = float(r['max_kho']) if ('max_kho' in r and r['max_kho']) else 3000.0  

                if max_kho > 0:
                    phan_tram_thuc_te = (ton_kho / max_kho) * 100
                else:
                    phan_tram_thuc_te = 0

                phan_tram_hien_thi = min(int(phan_tram_thuc_te), 100)

                # Định nghĩa màu sắc & nhãn trạng thái dựa trên lượng tồn thực tế so với ngưỡng
                if ton_kho > max_kho:
                    color_style = "#E74C3C"      # ĐỎ khi quá tải
                    status_text = f"Quá tải (+{int(phan_tram_thuc_te - 100)}%)"
                    status_bg = "#FADBD8"        
                    status_color = "#C0392B"     
                elif ton_kho <= nguong_canh_bao:
                    color_style = "#F1C40F"      # VÀNG khi sắp hết / đã hết
                    status_text = "Sắp hết" if ton_kho > 0 else "Hết hàng"
                    status_bg = "#FCF3CF"
                    status_color = "#B7950B"
                else:
                    color_style = "#2ECC71"      # XANH LÁ khi an toàn
                    status_text = "An toàn"
                    status_bg = "#D4EFDF"
                    status_color = "#196F3D"

                # Đóng gói dữ liệu nguyên bản cần cho IngredientCard
                card_data = (r['id'], r['ten_nguyenlieu'], r['so_luong'], r['don_vi'], 
                             r['nguong_canh_bao'], r['ten_ncc'], r['gia_nhap'], latest_price)
                
                # Tạo widget Card mới
                card_widget = IngredientCard(card_data, self)
                
                # Tự động chèn thêm Progress Bar và Label trạng thái vào UI của Card này nếu class có hỗ trợ nhúng động, 
                # hoặc bạn có thể gọi trực tiếp một hàm setup giao diện bên trong file chứa class IngredientCard như sau:
                if hasattr(card_widget, 'setup_visuals'):
                    card_widget.setup_visuals(phan_tram_hien_thi, color_style, status_text, status_bg, status_color)
                
                # Thêm card_widget vào layout ô lưới (3 cột)
                self.grid.addWidget(card_widget, i // 3, i % 3)
                
            price_cursor.close()
        finally:
            conn.close()
    def load_recipes(self):
        self.btn_nl.setStyleSheet(self.tab_inactive)
        self.btn_ct.setStyleSheet(self.tab_active)
        self.btn_his.setStyleSheet(self.tab_inactive)
        self.btn_ncc.setStyleSheet(self.tab_inactive)
        self.btn_profit.setStyleSheet(self.tab_inactive)
        self.clear_grid()
        search_text = self.txt_search.text().strip()
        category_id = self.filter_category.currentData()
        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = """
                SELECT sp.id, sp.ten_sanpham, sp.huong_dan, sp.nguoi_cap_nhat, sp.ngay_cap_nhat
                FROM sanpham sp
                WHERE 1=1
            """
            params = []
            if search_text:
                query += " AND sp.ten_sanpham LIKE %s"
                params.append(f"%{search_text}%")
            if category_id:
                query += " AND sp.id_danhmuc = %s"
                params.append(category_id)
            cursor.execute(query, params)
            sp_list = cursor.fetchall()
            for i, sp in enumerate(sp_list):
                id_sp, ten_sp, huong_dan, creator, up_date = sp
                date_str = up_date.strftime("%d/%m/%Y") if up_date and hasattr(up_date, 'strftime') else "22/04/2026"
                user_str = creator if creator else "Chưa rõ"
                cursor.execute("""
                    SELECT nl.ten_nguyenlieu, ct.dinh_luong, nl.don_vi 
                    FROM congthuc ct
                    JOIN nguyenlieu nl ON ct.id_nguyenlieu = nl.id
                    WHERE ct.id_sanpham = %s
                """, (id_sp,))
                ingredients = [(r[0], f"{r[1]} {r[2]}") for r in cursor.fetchall()]
                card = RecipeCard(id_sp, ten_sp, "1", ingredients, huong_dan, user_str, date_str, self)
                self.grid.addWidget(card, i // 2, i % 2)
        finally:
            conn.close()

    # ========== SỬA open_tx để lưu ngày SX và HH ==========
    def open_tx(self, mode, data):
        raw_name = self.user_info.get('ho_ten', '')
        raw_role = self.user_info.get('vai_tro', '')
        is_admin = "TRAN VIET DUC" in raw_name.upper() or "QUẢN TRỊ VIÊN" in raw_role.upper()
        vai_tro_hien_tai = "Quản lý" if is_admin else "Nhân viên"
        if mode == "ADJUST" and vai_tro_hien_tai == "Nhân viên":
            QMessageBox.warning(self, "Quyền hạn", f"Tài khoản '{raw_name}' không có quyền điều chỉnh!")
            return

        dlg = TransactionDialog(mode, data, self)
        if dlg.exec():
            try:
                qty_txt = dlg.qty_input.text().replace(',', '.')
                qty_val = round(float(qty_txt), 2) if qty_txt else 0.0
                if mode == "IN" and qty_val <= 0:
                    QMessageBox.warning(self, "Lỗi", "Số lượng nhập phải lớn hơn 0!")
                    return
                if mode == "OUT" and qty_val <= 0:
                    QMessageBox.warning(self, "Lỗi", "Số lượng xuất phải lớn hơn 0!")
                    return
                reason_input = dlg.reason_input.toPlainText().strip() or "Cập nhật kho"
                conn = get_db_connection()
                if not conn:
                    return
                cursor = conn.cursor()
                ton_truoc = round(float(data[2]), 2)
                gia_truoc = float(data[6]) if len(data) > 6 else 0.0
                log_name = raw_name.strip()
                cursor.execute("SELECT ho_ten FROM user WHERE ho_ten = %s", (log_name,))
                if not cursor.fetchone():
                    log_name = "Trần Việt Đức"

                if mode == "IN":
                    new_price_txt = dlg.price_input.text().replace(',', '.') if dlg.price_input else ""
                    new_price = float(new_price_txt) if new_price_txt else None
                    if new_price is None or new_price <= 0:
                        QMessageBox.warning(self, "Lỗi", "Vui lòng nhập giá nhập hợp lệ (số dương)!")
                        return
                    # Lấy ngày sản xuất và hạn sử dụng từ dialog (nếu có)
                    ngay_sx = None
                    ngay_hh = None
                    if hasattr(dlg, 'date_sx') and dlg.date_sx:
                        ngay_sx = dlg.date_sx.date().toPyDate()
                    if hasattr(dlg, 'date_hh') and dlg.date_hh:
                        ngay_hh = dlg.date_hh.date().toPyDate()
                    ton_sau = ton_truoc + qty_val
                    total_value_truoc = ton_truoc * gia_truoc
                    total_nhap = qty_val * new_price
                    gia_tb_moi = (total_value_truoc + total_nhap) / ton_sau
                    cursor.execute("UPDATE nguyenlieu SET so_luong = %s, gia_nhap = %s WHERE id = %s",
                                   (ton_sau, gia_tb_moi, data[0]))
                    reason_final = f"[{vai_tro_hien_tai}] {reason_input} (giá nhập: {new_price:,.0f})"
                    cursor.execute("""
                        INSERT INTO lichsu_kho (loai_gd, ten_nl, so_luong, ton_truoc, ton_sau, ly_do, nguoi_dung, ngay_gd, gia_nhap, ngay_sx, ngay_hh)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)
                    """, ("IN", data[1], qty_val, ton_truoc, ton_sau, reason_final, log_name, new_price, ngay_sx, ngay_hh))

                elif mode == "OUT":
                    if ton_truoc < qty_val:
                        QMessageBox.warning(self, "Lỗi", "Số lượng hàng trong kho không đủ!")
                        return
                    ton_sau = ton_truoc - qty_val
                    cursor.execute("UPDATE nguyenlieu SET so_luong = %s WHERE id = %s", (ton_sau, data[0]))
                    reason_final = f"[{vai_tro_hien_tai}] {reason_input}"
                    cursor.execute("""
                        INSERT INTO lichsu_kho (loai_gd, ten_nl, so_luong, ton_truoc, ton_sau, ly_do, nguoi_dung, ngay_gd)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, ("OUT", data[1], -qty_val, ton_truoc, ton_sau, reason_final, log_name))

                else:
                    ton_sau = qty_val
                    qty_change = round(ton_sau - ton_truoc, 2)
                    cursor.execute("UPDATE nguyenlieu SET so_luong = %s WHERE id = %s", (ton_sau, data[0]))
                    reason_final = f"[{vai_tro_hien_tai}] {reason_input}"
                    cursor.execute("""
                        INSERT INTO lichsu_kho (loai_gd, ten_nl, so_luong, ton_truoc, ton_sau, ly_do, nguoi_dung, ngay_gd)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, ("ADJUST", data[1], qty_change, ton_truoc, ton_sau, reason_final, log_name))

                conn.commit()
                conn.close()
                self.load_data()
                if hasattr(self, 'summary_profit_table'):
                    self.refresh_summary_profit()
                if hasattr(self, 'ingredient_profit_table'):
                    self.refresh_ingredient_profit()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi SQL", f"Lỗi: {e}")

    # ------------------ CRUD giữ nguyên ------------------
    def add_ingredient(self):
        dlg = IngredientDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO nguyenlieu (ten_nguyenlieu, don_vi, nguong_canh_bao, id_ncc, gia_nhap)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (data['name'], data['unit'], data['threshold'], data['supplier_id'], data['price']))
                    conn.commit()
                    QMessageBox.information(self, "Thành công", "Đã thêm nguyên liệu")
                    self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", str(e))
                finally:
                    conn.close()

    def edit_ingredient(self, ing_id, ing_data):
        dlg = IngredientDialog(self, ing_data)
        if dlg.exec():
            data = dlg.get_data()
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE nguyenlieu SET ten_nguyenlieu=%s, don_vi=%s, nguong_canh_bao=%s, id_ncc=%s, gia_nhap=%s
                        WHERE id=%s
                    """, (data['name'], data['unit'], data['threshold'], data['supplier_id'], data['price'], ing_id))
                    conn.commit()
                    QMessageBox.information(self, "Thành công", "Đã cập nhật nguyên liệu")
                    self.load_data()
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", str(e))
                finally:
                    conn.close()

    def delete_ingredient(self, ing_id, ing_name):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM congthuc WHERE id_nguyenlieu = %s", (ing_id,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Ràng buộc", f"Nguyên liệu '{ing_name}' đang được dùng trong công thức. Không thể xóa.")
                conn.close()
                return
            reply = QMessageBox.question(self, "Xác nhận", f"Xóa nguyên liệu '{ing_name}' ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                cursor.execute("DELETE FROM nguyenlieu WHERE id = %s", (ing_id,))
                conn.commit()
                QMessageBox.information(self, "Thành công", "Đã xóa nguyên liệu")
                self.load_data()
            conn.close()

    def add_supplier(self):
        dlg = SupplierDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO nhacungcap (ten_ncc, sdt) VALUES (%s, %s)",
                                   (data['name'], data['phone']))
                    conn.commit()
                    QMessageBox.information(self, "Thành công", "Đã thêm nhà cung cấp")
                    self.load_suppliers()
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", str(e))
                finally:
                    conn.close()

    def edit_supplier(self, supplier_id, supplier_data):
        dlg = SupplierDialog(self, supplier_data)
        if dlg.exec():
            data = dlg.get_data()
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE nhacungcap SET ten_ncc=%s, sdt=%s WHERE id=%s",
                                   (data['name'], data['phone'], supplier_id))
                    conn.commit()
                    QMessageBox.information(self, "Thành công", "Đã cập nhật nhà cung cấp")
                    self.load_suppliers()
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", str(e))
                finally:
                    conn.close()

    def delete_supplier(self, supplier_id, supplier_name):
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM nguyenlieu WHERE id_ncc = %s", (supplier_id,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Ràng buộc", f"Nhà cung cấp '{supplier_name}' đang được dùng trong nguyên liệu. Không thể xóa.")
                conn.close()
                return
            reply = QMessageBox.question(self, "Xác nhận", f"Xóa nhà cung cấp '{supplier_name}' ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                cursor.execute("DELETE FROM nhacungcap WHERE id = %s", (supplier_id,))
                conn.commit()
                QMessageBox.information(self, "Thành công", "Đã xóa nhà cung cấp")
                self.load_suppliers()
            conn.close()

    def add_recipe(self):
        dlg = RecipeDialog(self)
        if dlg.exec():
            self.load_recipes()

    # ================== BÁO CÁO LỢI NHUẬN MỚI ==================
    def load_profit_stats(self):
        self.btn_nl.setStyleSheet(self.tab_inactive)
        self.btn_ct.setStyleSheet(self.tab_inactive)
        self.btn_his.setStyleSheet(self.tab_inactive)
        self.btn_ncc.setStyleSheet(self.tab_inactive)
        self.btn_profit.setStyleSheet(self.tab_active)
        self.clear_grid()

        # Ngắt kết nối signal cũ nếu có
        if hasattr(self, 'profit_filter') and self.profit_filter is not None:
            try:
                self.profit_filter.currentTextChanged.disconnect()
            except:
                pass
        if hasattr(self, 'ingredient_period') and self.ingredient_period is not None:
            try:
                self.ingredient_period.currentIndexChanged.disconnect()
            except:
                pass
        if hasattr(self, 'ingredient_date') and self.ingredient_date is not None:
            try:
                self.ingredient_date.dateChanged.disconnect()
            except:
                pass

        profit_tabs = QTabWidget()
        profit_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab { padding: 10px 20px; background: #F4F4F4; border-radius: 8px; margin-right: 5px; }
            QTabBar::tab:selected { background: #58111A; color: white; }
        """)

        # Tab tổng hợp
        tab_summary = self.create_summary_profit_tab()
        profit_tabs.addTab(tab_summary, "📊 Tổng hợp lợi nhuận")

        # Tab theo nguyên liệu
        tab_by_ingredient = self.create_ingredient_profit_tab()
        profit_tabs.addTab(tab_by_ingredient, "🥕 Lợi nhuận theo nguyên liệu")

        self.grid.addWidget(profit_tabs, 0, 0, 1, 2)

    def create_summary_profit_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        filter_layout = QHBoxLayout()
        self.profit_filter = QComboBox()
        self.profit_filter.addItems(["7 ngày gần đây", "4 tuần gần đây", "Các tháng trong năm", "Năm nay"])
        self.profit_filter.currentTextChanged.connect(self.refresh_summary_profit)
        filter_layout.addStretch()
        filter_layout.addWidget(QLabel("📅 Chọn kỳ:"))
        filter_layout.addWidget(self.profit_filter)
        layout.addLayout(filter_layout)

        self.summary_profit_table = QTableWidget()
        self.summary_profit_table.setColumnCount(5)
        self.summary_profit_table.setHorizontalHeaderLabels(["Kỳ", "Doanh thu", "Giá vốn", "Lợi nhuận", "Tỷ suất"])
        
        # Style cho horizontal header (tiêu đề cột) – màu cam hoặc đỏ mận tùy ý
        self.summary_profit_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        self.summary_profit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Style cho vertical header (cột số thứ tự bên trái) – màu đỏ mận
        self.summary_profit_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
                padding: 4px;
                border: none;
            }
        """)
        
        # Style cho ô dữ liệu (nền trắng, chữ đen)
        self.summary_profit_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F8F9FA;
            }
            QTableWidget::item {
                background-color: white;
                color: black;
            }
            QTableWidget::item:alternate {
                background-color: #F8F9FA;
            }
            QTableWidget::item:selected {
                background-color: #58111A;
                color: white;
            }
        """)
        self.summary_profit_table.setAlternatingRowColors(True)
        layout.addWidget(self.summary_profit_table)
        
        self.refresh_summary_profit()
        return widget

    def create_ingredient_profit_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Chọn kỳ:"))
        self.ingredient_period = QComboBox()
        self.ingredient_period.addItems(["Ngày", "Tuần", "Tháng", "Năm"])
        self.profit_filter.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #DDD;
                border-radius: 8px;
                padding: 6px 12px;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #58111A;
                selection-color: white;
                border: 1px solid #DDD;
                outline: none;
            }
        """)
        self.ingredient_period.currentIndexChanged.connect(self.refresh_ingredient_profit)
        self.ingredient_period.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #DDD;
                border-radius: 8px;
                padding: 6px 12px;
            }

            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #58111A;
                selection-color: white;
                border: 1px solid #DDD;
                outline: none;
            }
        """)
        filter_row.addWidget(self.ingredient_period)

        filter_row.addSpacing(20)
        filter_row.addWidget(QLabel("Chọn ngày/ tuần/ tháng cụ thể:"))
        self.ingredient_date = QDateEdit()
        self.ingredient_date.setCalendarPopup(True)
        self.ingredient_date.setDate(QDate.currentDate())
        self.ingredient_date.dateChanged.connect(self.refresh_ingredient_profit)
        self.ingredient_date.setStyleSheet("""
            QDateEdit {
                background-color: white;
                color: black;
                padding: 6px 10px;
                border: 1px solid #DDD;
                border-radius: 8px;
                font-size: 13px;
            }
            QDateEdit::drop-down { border: none; width: 20px; }
            QDateEdit::down-arrow { image: none; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 5px solid #58111A; margin-right: 5px; }
            QDateEdit QLineEdit { color: black; background-color: white; }
        """)
        filter_row.addWidget(self.ingredient_date)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        self.ingredient_profit_table = QTableWidget()
        self.ingredient_profit_table.setColumnCount(6)
        self.ingredient_profit_table.setHorizontalHeaderLabels(["Nguyên liệu", "Đơn vị", "Doanh thu đóng góp", "Giá vốn", "Lợi nhuận", "Biên lợi nhuận"])
        
        # Style cho horizontal header (tiêu đề cột)
        self.ingredient_profit_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        self.ingredient_profit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Style cho vertical header (cột số thứ tự bên trái) - QUAN TRỌNG
        self.ingredient_profit_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
                padding: 4px;
                border: none;
            }
        """)
        
        # Style cho ô dữ liệu (nền trắng, chữ đen)
        self.ingredient_profit_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #F8F9FA;
            }
            QTableWidget::item {
                background-color: white;
                color: black;
            }
            QTableWidget::item:alternate {
                background-color: #F8F9FA;
            }
            QTableWidget::item:selected {
                background-color: #58111A;
                color: white;
            }
        """)
        self.ingredient_profit_table.setAlternatingRowColors(True)
        layout.addWidget(self.ingredient_profit_table)

        self.refresh_ingredient_profit()
        return widget


    def refresh_summary_profit(self):
        if not hasattr(self, 'profit_filter') or self.profit_filter is None:
            return
        try:
            filter_text = self.profit_filter.currentText()
        except RuntimeError:
            return
        db = get_db_connection()
        if not db:
            return
        cursor = db.cursor(dictionary=True)
        stats = self.get_period_profit_stats(cursor, filter_text)
        db.close()
        self.summary_profit_table.setRowCount(len(stats))
        for i, stat in enumerate(stats):
            self.summary_profit_table.setItem(i, 0, QTableWidgetItem(stat['period']))
            self.summary_profit_table.setItem(i, 1, QTableWidgetItem(self.format_currency(stat['revenue'])))
            self.summary_profit_table.setItem(i, 2, QTableWidgetItem(self.format_currency(stat['cost'])))
            self.summary_profit_table.setItem(i, 3, QTableWidgetItem(self.format_currency(stat['profit'])))
            margin_item = QTableWidgetItem(f"{stat['margin']:.1f}%")
            margin_item.setForeground(QColor(34, 197, 94) if stat['margin'] >= 0 else QColor(239, 68, 68))
            self.summary_profit_table.setItem(i, 4, margin_item)

    def refresh_ingredient_profit(self):
        period_type = self.ingredient_period.currentText()
        base_date = self.ingredient_date.date().toPyDate()
        # Xác định start_date, end_date
        if period_type == "Ngày":
            start_date = base_date
            end_date = base_date + timedelta(days=1)
        elif period_type == "Tuần":
            start_date = base_date - timedelta(days=base_date.weekday())
            end_date = start_date + timedelta(days=7)
        elif period_type == "Tháng":
            start_date = base_date.replace(day=1)
            if base_date.month == 12:
                end_date = base_date.replace(year=base_date.year+1, month=1, day=1)
            else:
                end_date = base_date.replace(month=base_date.month+1, day=1)
        else:  # Năm
            start_date = base_date.replace(month=1, day=1)
            end_date = base_date.replace(year=base_date.year+1, month=1, day=1)

        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)

        # Lấy tất cả hóa đơn trong khoảng
        cursor.execute("""
            SELECT ct.id_sanpham, ct.so_luong
            FROM chitiethoadon ct
            JOIN chitietdonhang h ON ct.id_hoadon = h.id
            WHERE h.ngay_tao >= %s AND h.ngay_tao < %s
        """, (start_date, end_date))
        orders = cursor.fetchall()

        # Lấy giá bán và công thức cho từng sản phẩm
        product_data = {}
        for order in orders:
            sp_id = order['id_sanpham']
            qty_sold = float(order['so_luong']) if order['so_luong'] is not None else 0.0
            if sp_id not in product_data:
                cursor.execute("SELECT gia_ban FROM sanpham WHERE id = %s", (sp_id,))
                sp = cursor.fetchone()
                selling_price = float(sp['gia_ban']) if sp and sp['gia_ban'] is not None else 0.0
                cursor.execute("""
                    SELECT nl.id, nl.ten_nguyenlieu, ct.dinh_luong, nl.don_vi, nl.gia_nhap
                    FROM congthuc ct
                    JOIN nguyenlieu nl ON ct.id_nguyenlieu = nl.id
                    WHERE ct.id_sanpham = %s
                """, (sp_id,))
                ingredients = cursor.fetchall()
                # Ép kiểu các giá trị số
                for ing in ingredients:
                    ing['dinh_luong'] = float(ing['dinh_luong'])
                    ing['gia_nhap'] = float(ing['gia_nhap'])
                product_data[sp_id] = {
                    'selling_price': selling_price,
                    'ingredients': ingredients,
                    'quantity_sold': 0.0
                }
            product_data[sp_id]['quantity_sold'] += qty_sold

        # Tính đóng góp của từng nguyên liệu
        ingredient_profit = {}
        for sp_id, data in product_data.items():
            qty_sold = data['quantity_sold']
            if qty_sold == 0:
                continue
            revenue = qty_sold * data['selling_price']
            total_cost = 0.0
            for ing in data['ingredients']:
                ing_cost = ing['dinh_luong'] * ing['gia_nhap'] * qty_sold
                total_cost += ing_cost

            if total_cost <= 0:
                continue

            for ing in data['ingredients']:
                ing_cost = ing['dinh_luong'] * ing['gia_nhap'] * qty_sold
                ing_name = ing['ten_nguyenlieu']
                if ing_name not in ingredient_profit:
                    ingredient_profit[ing_name] = {
                        'revenue': 0.0,
                        'cost': 0.0,
                        'unit': ing['don_vi']
                    }
                revenue_share = revenue * (ing_cost / total_cost)
                ingredient_profit[ing_name]['revenue'] += revenue_share
                ingredient_profit[ing_name]['cost'] += ing_cost
        conn.close()

        # Tạo bảng
        self.ingredient_profit_table.setRowCount(len(ingredient_profit))
        for i, (name, vals) in enumerate(ingredient_profit.items()):
            profit = vals['revenue'] - vals['cost']
            margin = (profit / vals['revenue'] * 100) if vals['revenue'] > 0 else 0
            self.ingredient_profit_table.setItem(i, 0, QTableWidgetItem(name))
            self.ingredient_profit_table.setItem(i, 1, QTableWidgetItem(vals['unit']))
            self.ingredient_profit_table.setItem(i, 2, QTableWidgetItem(self.format_currency(vals['revenue'])))
            self.ingredient_profit_table.setItem(i, 3, QTableWidgetItem(self.format_currency(vals['cost'])))
            profit_item = QTableWidgetItem(self.format_currency(profit))
            profit_item.setForeground(QColor(34, 197, 94) if profit >= 0 else QColor(239, 68, 68))
            self.ingredient_profit_table.setItem(i, 4, profit_item)
            margin_item = QTableWidgetItem(f"{margin:.1f}%")
            margin_item.setForeground(QColor(34, 197, 94) if margin >= 0 else QColor(239, 68, 68))
            self.ingredient_profit_table.setItem(i, 5, margin_item)
        self.ingredient_profit_table.resizeColumnsToContents()

    # ================== BÁO CÁO KHO ==================
    def show_low_stock_notification(self):
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        # Nguyên liệu sắp hết (tồn <= ngưỡng)
        cursor.execute("""
            SELECT ten_nguyenlieu, so_luong, nguong_canh_bao, don_vi
            FROM nguyenlieu
            WHERE so_luong <= nguong_canh_bao AND so_luong > 0
        """)
        low_stock = cursor.fetchall()
        msg = ""
        if low_stock:
            msg = "⚠️ Các nguyên liệu sắp hết cần nhập thêm:\n"
            for item in low_stock:
                msg += f"- {item['ten_nguyenlieu']}: Tồn {item['so_luong']} {item['don_vi']}, ngưỡng {item['nguong_canh_bao']}\n"
        # Nguyên liệu sắp hết hạn trong 7 ngày tới
        cursor.execute("""
            SELECT DISTINCT ten_nl, ngay_hh 
            FROM lichsu_kho 
            WHERE loai_gd = 'IN' AND ngay_hh IS NOT NULL 
              AND ngay_hh BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY ngay_hh
        """)
        expiring = cursor.fetchall()
        if expiring:
            if msg:
                msg += "\n"
            msg += "⚠️ Nguyên liệu sắp hết hạn trong 7 ngày tới:\n"
            for e in expiring:
                msg += f"- {e['ten_nl']}: hết hạn {e['ngay_hh'].strftime('%d/%m/%Y')}\n"
        conn.close()
        if msg:
            QMessageBox.information(self, "Cảnh báo tồn kho & hạn sử dụng", msg)

    def load_report(self):
        self.btn_nl.setStyleSheet(self.tab_inactive)
        self.btn_ct.setStyleSheet(self.tab_inactive)
        self.btn_his.setStyleSheet(self.tab_inactive)
        self.btn_ncc.setStyleSheet(self.tab_inactive)
        self.btn_profit.setStyleSheet(self.tab_inactive)
        self.btn_report.setStyleSheet(self.tab_active)
        self.clear_grid()

        from PyQt6.QtWidgets import QTabWidget
        report_tabs = QTabWidget()
        report_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: transparent; }
            QTabBar::tab { padding: 10px 20px; background: #F4F4F4; border-radius: 8px; margin-right: 5px; }
            QTabBar::tab:selected { background: #58111A; color: white; }
        """)

        # Tab tồn kho
        tab_inv = QWidget()
        inv_layout = QVBoxLayout(tab_inv)
        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(6)
        self.inv_table.setHorizontalHeaderLabels(["Nguyên liệu", "Đơn vị", "Tồn kho", "Giá TB (đ/đv)", "Giá trị tồn (đ)", "Hạn gần nhất"])
        
        # Style cho toàn bảng (ô dữ liệu)
        self.inv_table.setStyleSheet("""
            QTableWidget::item {
                background-color: white;
                color: black;
            }
        """)
        # Style cho header ngang
        self.inv_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        # Style cho header dọc (cột số thứ tự)
        self.inv_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
            }
        """)
        self.inv_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        inv_layout.addWidget(self.inv_table)
        
        btn_excel_inv = QPushButton("📎 Xuất Excel")
        btn_excel_inv.setStyleSheet("background: #27AE60; color: white; border-radius: 10px; height: 35px; margin-top: 10px;")
        btn_excel_inv.clicked.connect(self.export_inventory_to_excel)
        inv_layout.addWidget(btn_excel_inv)
        report_tabs.addTab(tab_inv, "📦 Tồn kho")

        # Tab Nhập - Xuất - Tồn
        tab_iol = QWidget()
        iol_layout = QVBoxLayout(tab_iol)
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("Chọn tháng:"))
        self.month_picker = QDateEdit()
        self.month_picker.setCalendarPopup(True)
        self.month_picker.setDisplayFormat("MM/yyyy")
        self.month_picker.setDate(datetime.today())
        self.month_picker.dateChanged.connect(self.load_monthly_iol_report)
        month_layout.addWidget(self.month_picker)
        month_layout.addStretch()
        iol_layout.addLayout(month_layout)

        self.iol_table = QTableWidget()
        self.iol_table.setColumnCount(6)
        self.iol_table.setHorizontalHeaderLabels(
            ["Nguyên liệu", "Đơn vị", "Tồn đầu tháng", "Nhập trong tháng", "Xuất trong tháng", "Tồn cuối tháng"]
        )
        # Style cho ô dữ liệu
        self.iol_table.setStyleSheet("""
            QTableWidget::item {
                background-color: white;
                color: black;
            }
        """)
        # Style header ngang
        self.iol_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        # Style header dọc
        self.iol_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #58111A;
                color: white;
                font-weight: bold;
            }
        """)
        self.iol_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        iol_layout.addWidget(self.iol_table)

        btn_excel_iol = QPushButton("📎 Xuất Excel")
        btn_excel_iol.setStyleSheet("background: #27AE60; color: white; border-radius: 10px; height: 35px; margin-top: 10px;")
        btn_excel_iol.clicked.connect(self.export_iol_to_excel)
        iol_layout.addWidget(btn_excel_iol)
        report_tabs.addTab(tab_iol, "📆 Nhập - Xuất - Tồn")

        self.grid.addWidget(report_tabs, 0, 0, 1, 2)
        self.load_inventory_report()
        self.load_monthly_iol_report()
    def load_inventory_report(self):
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, ten_nguyenlieu, don_vi, so_luong, gia_nhap FROM nguyenlieu ORDER BY ten_nguyenlieu")
        rows = cursor.fetchall()
        self.inv_table.setRowCount(len(rows))
        total_value = 0
        for i, r in enumerate(rows):
            qty = float(r['so_luong'])
            price = float(r['gia_nhap']) if r['gia_nhap'] else 0
            value = qty * price
            total_value += value
            self.inv_table.setItem(i, 0, QTableWidgetItem(r['ten_nguyenlieu']))
            self.inv_table.setItem(i, 1, QTableWidgetItem(r['don_vi']))
            self.inv_table.setItem(i, 2, QTableWidgetItem(f"{qty:,.2f}".replace(",", ".")))
            self.inv_table.setItem(i, 3, QTableWidgetItem(f"{price:,.0f}đ".replace(",", ".")))
            self.inv_table.setItem(i, 4, QTableWidgetItem(f"{value:,.0f}đ".replace(",", ".")))
            # Lấy hạn gần nhất
            expiry, _ = self.get_nearest_expiry(r['ten_nguyenlieu'])
            expiry_str = expiry.strftime("%d/%m/%Y") if expiry else ""
            self.inv_table.setItem(i, 5, QTableWidgetItem(expiry_str))
        # Dòng tổng
        self.inv_table.insertRow(len(rows))
        self.inv_table.setItem(len(rows), 3, QTableWidgetItem("TỔNG GIÁ TRỊ TỒN:"))
        self.inv_table.setItem(len(rows), 4, QTableWidgetItem(f"{total_value:,.0f}đ".replace(",", ".")))
        conn.close()

    def load_monthly_iol_report(self):
        date = self.month_picker.date()
        month = date.month()
        year = date.year()
        from datetime import datetime
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year+1, 1, 1)
        else:
            end_date = datetime(year, month+1, 1)

        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, ten_nguyenlieu, don_vi FROM nguyenlieu")
        materials = cursor.fetchall()

        self.iol_table.clearContents()
        self.iol_table.setRowCount(0)
        self.iol_table.setColumnCount(6)
        self.iol_table.setHorizontalHeaderLabels(
            ["Nguyên liệu", "Đơn vị", "Tồn đầu tháng", "Nhập trong tháng", "Xuất trong tháng", "Tồn cuối tháng"]
        )

        data = []
        for mat in materials:
            name = mat['ten_nguyenlieu']
            unit = mat['don_vi']
            cursor.execute("SELECT COALESCE(SUM(so_luong), 0) as dau_ky FROM lichsu_kho WHERE ten_nl = %s AND ngay_gd < %s", (name, start_date))
            dau_ky = cursor.fetchone()['dau_ky'] or 0
            cursor.execute("SELECT COALESCE(SUM(so_luong), 0) as nhap FROM lichsu_kho WHERE ten_nl = %s AND loai_gd = 'IN' AND ngay_gd >= %s AND ngay_gd < %s", (name, start_date, end_date))
            nhap = cursor.fetchone()['nhap'] or 0
            cursor.execute("SELECT COALESCE(SUM(-so_luong), 0) as xuat FROM lichsu_kho WHERE ten_nl = %s AND loai_gd = 'OUT' AND ngay_gd >= %s AND ngay_gd < %s", (name, start_date, end_date))
            xuat = cursor.fetchone()['xuat'] or 0
            ton_cuoi = dau_ky + nhap - xuat
            data.append((name, unit, dau_ky, nhap, xuat, ton_cuoi))
        conn.close()

        self.iol_table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.iol_table.setItem(i, 0, QTableWidgetItem(row[0]))
            self.iol_table.setItem(i, 1, QTableWidgetItem(row[1]))
            self.iol_table.setItem(i, 2, QTableWidgetItem(f"{row[2]:,.2f}".replace(",", ".")))
            self.iol_table.setItem(i, 3, QTableWidgetItem(f"{row[3]:,.2f}".replace(",", ".")))
            self.iol_table.setItem(i, 4, QTableWidgetItem(f"{row[4]:,.2f}".replace(",", ".")))
            self.iol_table.setItem(i, 5, QTableWidgetItem(f"{row[5]:,.2f}".replace(",", ".")))

    def export_table_to_excel(self, table_widget, filename, title):
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            QMessageBox.warning(self, "Thiếu thư viện", "Vui lòng cài đặt openpyxl: pip install openpyxl")
            return
        wb = Workbook()
        ws = wb.active
        ws.title = title
        headers = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
        ws.append(headers)
        for col_idx, _ in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="58111A", end_color="FF8540", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        for row in range(table_widget.rowCount()):
            row_data = [table_widget.item(row, col).text() if table_widget.item(row, col) else "" for col in range(table_widget.columnCount())]
            ws.append(row_data)
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    max_len = max(max_len, len(str(cell.value)))
                except:
                    pass
            ws.column_dimensions[col_letter].width = max_len + 2
        wb.save(filename)
        QMessageBox.information(self, "Thành công", f"Đã xuất ra file:\n{filename}")

    def export_inventory_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Xuất báo cáo tồn kho", "tonkho.xlsx", "Excel Files (*.xlsx)")
        if file_path:
            self.export_table_to_excel(self.inv_table, file_path, "Tồn kho")

    def export_iol_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Xuất báo cáo nhập-xuất-tồn", "nhapxuatton.xlsx", "Excel Files (*.xlsx)")
        if file_path:
            self.export_table_to_excel(self.iol_table, file_path, "Nhập-Xuất-Tồn")

if __name__ == "__main__":
    from PyQt6.QtGui import QPalette, QColor
    from PyQt6.QtCore import Qt
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Tạo palette sáng rõ
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 133, 64))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)
    
    window = WarehouseApp()
    window.show()
    sys.exit(app.exec())