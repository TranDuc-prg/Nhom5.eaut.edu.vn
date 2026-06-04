import sys
import requests
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
                             QGridLayout, QMessageBox, QComboBox, QCheckBox, QTabWidget,
                             QDialog, QFormLayout, QTextEdit)
from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6.QtCore import Qt


class PointExchangeDialog(QDialog):
    """Hộp thoại đổi điểm tích lũy"""
    def __init__(self, diem_hien_co, parent=None):
        super().__init__(parent)
        self.diem_hien_co = diem_hien_co
        self.selected_voucher = None
        self.setWindowTitle("🎁 Đổi điểm tích lũy")
        self.setFixedSize(450, 500)
        self.setStyleSheet("background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 15px;")
        self.init_ui()
        self.load_vouchers()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("ĐỔI ĐIỂM TÍCH LŨY")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #58111A;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        self.lbl_diem = QLabel(f"🏆 Điểm hiện có: {self.diem_hien_co} điểm")
        self.lbl_diem.setStyleSheet("font-size: 16px; font-weight: bold; color: #58111A; padding: 10px; background: #FFF3E0; border-radius: 10px;")
        self.lbl_diem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_diem)
        
        layout.addWidget(QLabel("📋 Chọn ưu đãi:"))
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.voucher_container = QWidget()
        self.voucher_layout = QVBoxLayout(self.voucher_container)
        self.voucher_layout.setSpacing(10)
        self.scroll.setWidget(self.voucher_container)
        layout.addWidget(self.scroll)
        
        btn_layout = QHBoxLayout()
        self.btn_close = QPushButton("Đóng")
        self.btn_close.clicked.connect(self.reject)
        self.btn_close.setStyleSheet("background: #E0B0B4; color: white; padding: 10px; border-radius: 8px; font-weight: bold;")
        
        self.btn_exchange = QPushButton("Đổi ngay")
        self.btn_exchange.setEnabled(False)
        self.btn_exchange.clicked.connect(self.accept)
        self.btn_exchange.setStyleSheet("background: #58111A; color: white; padding: 10px; border-radius: 8px; font-weight: bold;")
        
        btn_layout.addWidget(self.btn_close)
        btn_layout.addWidget(self.btn_exchange)
        layout.addLayout(btn_layout)
    
    def load_vouchers(self):
        try:
            db = mysql.connector.connect(
                host="localhost", user="root", password="", database="quanly_snack_db"
            )
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM voucher 
                WHERE diem_doi <= %s 
                AND trang_thai = 1 
                AND (ngay_het_han >= CURDATE() OR ngay_het_han IS NULL)
                ORDER BY diem_doi ASC
            """, (self.diem_hien_co,))
            
            vouchers = cur.fetchall()
            db.close()
            
            if not vouchers:
                lbl = QLabel("Hiện chưa có ưu đãi phù hợp với số điểm của bạn.")
                lbl.setStyleSheet("color: #999; padding: 20px;")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.voucher_layout.addWidget(lbl)
                return
            
            for v in vouchers:
                btn = QPushButton()
                loai_text = "%" if v['loai_uu_dai'] == 'phantram' else "đ"
                gia_tri_text = f"{v['gia_tri']}{loai_text}"
                
                btn.setText(f"🎁 {v['ten_voucher']}\n   Đổi {v['diem_doi']} điểm → Giảm {gia_tri_text}")
                btn.setFixedHeight(80)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 10px;
                        border: 1px solid #E2E8F0;
                        border-radius: 10px;
                        background: #FAFAFA;
                        color: #1E293B;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background: #FFFFFF;
                        border-color: #58111A;
                    }
                """)
                btn.clicked.connect(lambda checked, v_data=v: self.select_voucher(v_data))
                self.voucher_layout.addWidget(btn)
                
        except Exception as e:
            print(f"Lỗi load voucher: {e}")
    
    def select_voucher(self, voucher):
        self.selected_voucher = voucher
        self.btn_exchange.setEnabled(True)
        for i in range(self.voucher_layout.count()):
            widget = self.voucher_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                if voucher['ma_voucher'] in widget.text():
                    widget.setStyleSheet("""
                        QPushButton {
                            text-align: left;
                            padding: 10px;
                            border: 2px solid #58111A;
                            border-radius: 10px;
                            background: #FFFFFF;
                            font-size: 13px;
                        }
                    """)
                else:
                    widget.setStyleSheet("""
                        QPushButton {
                            text-align: left;
                            padding: 10px;
                            border: 2px solid #E2E8F0;
                            border-radius: 10px;
                            background: white;
                            font-size: 13px;
                        }
                    """)
    
    def get_selected_voucher(self):
        return self.selected_voucher


class SnackShopPOS(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        self.user_info = user_info or {"id": 5, "ho_ten": "Nhân viên"}
        self.nhanvien_id = self.user_info.get('id', 5)
        
        self.cart = {}
        self.subtotal = 0 
        self.discount_val = 0 
        self.total = 0
        self.id_khachhang_hien_tai = None
        self.diem_khach_hien_tai = 0
        self.applied_voucher = None
        
        self.db_config = {"host": "localhost", "user": "root", "password": "", "database": "quanly_snack_db"}
        
        self.init_ui()
        self.load_products()
        
        self.txt_phone.textChanged.connect(self.on_phone_changed)

    def connect_db(self):
        return mysql.connector.connect(**self.db_config)

    def on_phone_changed(self):
        phone = self.txt_phone.text().strip()
        if len(phone) >= 5:
            self.check_customer_points(phone)
    
    def check_customer_points(self, phone):
        try:
            db = self.connect_db()
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT id, ten_khachhang, diem_tich_luy, tong_chi_tieu 
                FROM khachhang 
                WHERE so_dien_thoai = %s
            """, (phone,))
            kh = cur.fetchone()
            db.close()
            
            if kh:
                self.id_khachhang_hien_tai = kh['id']
                self.diem_khach_hien_tai = kh['diem_tich_luy']
                if not self.txt_name.text().strip():
                    self.txt_name.setText(kh['ten_khachhang'])
                
                if kh['diem_tich_luy'] >= 30:
                    reply = QMessageBox.question(
                        self, 
                        "🎁 Thông báo từ hệ thống",
                        f"Chào mừng {kh['ten_khachhang']} quay trở lại!\n\n"
                        f"⭐ Bạn có {kh['diem_tich_luy']} điểm tích lũy.\n"
                        f"💰 Tổng chi tiêu: {kh['tong_chi_tieu']:,.0f}đ\n\n"
                        f"Bạn có muốn đổi điểm lấy ưu đãi không?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        self.open_point_exchange_dialog()
            else:
                self.id_khachhang_hien_tai = None
                self.diem_khach_hien_tai = 0
        except Exception as e:
            print(f"Lỗi kiểm tra khách hàng: {e}")
    
    def open_point_exchange_dialog(self):
        dialog = PointExchangeDialog(self.diem_khach_hien_tai, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            voucher = dialog.get_selected_voucher()
            if voucher:
                self.apply_point_discount(voucher)
    
    def apply_point_discount(self, voucher):
        try:
            if self.applied_voucher:
                reply = QMessageBox.question(
                    self,
                    "Xác nhận",
                    f"Bạn đã áp dụng ưu đãi '{self.applied_voucher['ten_voucher']}'.\n"
                    f"Có muốn thay thế bằng ưu đãi mới không?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            if voucher['loai_uu_dai'] == 'phantram':
                giam_gia = self.subtotal * (voucher['gia_tri'] / 100)
            else:
                giam_gia = float(voucher['gia_tri'])
            
            giam_gia = min(giam_gia, self.subtotal)
            self.discount_val = giam_gia
            self.applied_voucher = voucher
            self.update_total()
            
            loai_text = "%" if voucher['loai_uu_dai'] == 'phantram' else "đ"
            QMessageBox.information(
                self,
                "Thành công",
                f"✅ Đã áp dụng ưu đãi: {voucher['ten_voucher']}\n"
                f"🎉 Giảm: {voucher['gia_tri']}{loai_text}\n"
                f"⭐ Điểm đã dùng: {voucher['diem_doi']}\n\n"
                f"💰 Tiết kiệm được: {int(giam_gia):,}đ"
            )
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể áp dụng ưu đãi: {e}")

    def init_ui(self):
        self.setWindowTitle("Snack Shop POS - Giao diện khách hàng")
        self.resize(1300, 850)
        self.setStyleSheet("""
            QWidget { background-color: #FAFAFA; }
            QTabWidget::pane { border: 1px solid #E2E8F0; background: #FFFFFF; border-radius: 12px; }
            QTabBar::tab { 
                background: #E0B0B4; 
                color: white; 
                padding: 10px 20px; 
                border-top-left-radius: 8px; 
                border-top-right-radius: 8px;
                font-weight: bold;
                margin-right: 4px;
            }
            QTabBar::tab:selected { 
                background: #FFFFFF; 
                color: #58111A; 
                border: 1px solid #E2E8F0;
                border-bottom-color: #FFFFFF;
            }
        """)

        self.layout_tong_chinh = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.layout_tong_chinh.addWidget(self.tabs)

        # Tab mua sắm
        self.tab_mua_sam = QWidget()
        self.tab_mua_sam.setStyleSheet("background: #FAFAFA;")
        self.tabs.addTab(self.tab_mua_sam, "🍿 ĐẶT MÓN")
        main_layout = QHBoxLayout(self.tab_mua_sam)

        left_side = QVBoxLayout()
        header_left = QLabel("🍿 DANH SÁCH THỰC ĐƠN")
        header_left.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E293B; padding: 10px;")
        left_side.addWidget(header_left)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        self.container = QWidget()
        self.grid = QGridLayout(self.container)
        self.grid.setSpacing(15)
        self.grid.setContentsMargins(10, 10, 10, 10)
        scroll.setWidget(self.container)
        left_side.addWidget(scroll)
        main_layout.addLayout(left_side, 7)

        # Panel phải
        self.right_scroll = QScrollArea()
        self.right_scroll.setFixedWidth(460)
        self.right_scroll.setWidgetResizable(True)
        self.right_scroll.setStyleSheet("border: none; background: white; border-radius: 20px;")
        
        self.right_widget = QWidget()
        self.right_widget.setStyleSheet("background: white; border-radius: 20px;")
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(12)

        # Thông tin khách
        right_layout.addWidget(QLabel("<b>👤 THÔNG TIN KHÁCH HÀNG</b>"))
        phone_layout = QHBoxLayout()
        self.txt_phone = QLineEdit(placeholderText="Số điện thoại (Bắt buộc)...")
        self.txt_phone.setStyleSheet("padding: 10px; border: 1px solid #E2E8F0; border-radius: 8px;")
        self.btn_check_points = QPushButton("🎁 Điểm")
        self.btn_check_points.setFixedWidth(60)
        self.btn_check_points.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_points.setStyleSheet("background: #58111A; color: white; border-radius: 8px; font-weight: bold;")
        self.btn_check_points.clicked.connect(lambda: self.check_customer_points(self.txt_phone.text().strip()))
        phone_layout.addWidget(self.txt_phone)
        phone_layout.addWidget(self.btn_check_points)
        right_layout.addLayout(phone_layout)
        
        self.txt_name = QLineEdit(placeholderText="Tên khách hàng (Bắt buộc)...")
        self.txt_address = QLineEdit(placeholderText="Địa chỉ nhận hàng (Bắt buộc)...")
        for w in [self.txt_name, self.txt_address]:
            w.setStyleSheet("padding: 10px; border: 1px solid #E2E8F0; border-radius: 8px;")
            w.textChanged.connect(self.validate_inputs)
            right_layout.addWidget(w)

        # Giỏ hàng
        right_layout.addWidget(QLabel("<b>🛒 GIỎ HÀNG</b>"))
        self.cart_scroll = QScrollArea()
        self.cart_scroll.setMinimumHeight(250)
        self.cart_scroll.setMaximumHeight(350)
        self.cart_container = QWidget()
        self.cart_vbox = QVBoxLayout(self.cart_container)
        self.cart_vbox.setContentsMargins(5, 5, 5, 5)
        self.cart_vbox.addStretch() 
        self.cart_scroll.setWidget(self.cart_container)
        self.cart_scroll.setWidgetResizable(True)
        self.cart_scroll.setStyleSheet("background: #F1F5F9; border-radius: 10px; border: none;")
        right_layout.addWidget(self.cart_scroll)

        # Khuyến mãi & tiền
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background: #FAFAFA; border-radius: 12px; padding: 10px; border: 1px solid #E2E8F0;")
        summary_lay = QVBoxLayout(summary_frame)
        
        promo_row = QHBoxLayout()
        self.txt_promo = QLineEdit(placeholderText="Mã giảm giá...")
        self.txt_promo.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 5px; background: white;")
        self.btn_apply = QPushButton("ÁP DỤNG")
        self.btn_apply.clicked.connect(self.apply_discount)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setStyleSheet("background: #FAFAFA; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        promo_row.addWidget(self.txt_promo)
        promo_row.addWidget(self.btn_apply)
        summary_lay.addLayout(promo_row)

        self.lbl_subtotal = QLabel("Tạm tính: 0đ")
        self.lbl_discount_info = QLabel("Giảm giá: -0đ")
        self.lbl_discount_info.setStyleSheet("color: #58111A; font-weight: bold;")
        self.lbl_total = QLabel("TỔNG: 0đ")
        self.lbl_total.setStyleSheet("font-size: 24px; font-weight: 900; color: #800000;")
        
        summary_lay.addWidget(self.lbl_subtotal)
        summary_lay.addWidget(self.lbl_discount_info)
        summary_lay.addWidget(self.lbl_total)
        right_layout.addWidget(summary_frame)

        # Hình thức thanh toán
        right_layout.addWidget(QLabel("<b>💳 HÌNH THỨC THANH TOÁN</b>"))
        self.combo_pay = QComboBox()
        self.combo_pay.addItems(["Tiền mặt", "Chuyển khoản VietQR", "ZaloPay"])
        self.combo_pay.setStyleSheet("padding: 10px; border-radius: 8px; background: #F1F5F9; border: 1px solid #CBD5E1;")
        self.combo_pay.currentIndexChanged.connect(self.toggle_payment_mode)
        right_layout.addWidget(self.combo_pay)

        # QR
        self.qr_container = QFrame()
        self.qr_container.setMinimumHeight(230)
        self.qr_vbox = QVBoxLayout(self.qr_container)
        self.qr_label = QLabel("Đang tạo mã QR...")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(180, 180)
        self.chk_confirm_ck = QCheckBox("Tôi xác nhận đã nhận đủ tiền")
        self.chk_confirm_ck.setStyleSheet("font-weight: bold; color: #FFFFFF;")
        self.chk_confirm_ck.stateChanged.connect(self.validate_inputs)
        
        self.qr_vbox.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.qr_vbox.addWidget(self.chk_confirm_ck, alignment=Qt.AlignmentFlag.AlignCenter)
        self.qr_container.hide()
        right_layout.addWidget(self.qr_container)

        right_layout.addStretch()
        self.btn_pay = QPushButton("THANH TOÁN")
        self.btn_pay.setFixedHeight(55)
        self.btn_pay.setEnabled(False)
        self.btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pay.setStyleSheet("""
            QPushButton { background: #58111A; color: white; font-weight: bold; border-radius: 12px; font-size: 18px; border: none; }
            QPushButton:hover { background: #721c24; }
            QPushButton:disabled { background: #E2E8F0; color: #94A3B8; }
        """)
        self.btn_pay.clicked.connect(self.save_invoice)
        right_layout.addWidget(self.btn_pay)

        self.right_scroll.setWidget(self.right_widget)
        main_layout.addWidget(self.right_scroll)

        # Tab theo dõi đơn hàng
        self.tab_theo_doi = QWidget()
        self.tabs.addTab(self.tab_theo_doi, "🚚 THEO DÕI ĐƠN HÀNG")
        tracking_layout = QVBoxLayout(self.tab_theo_doi)

        search_f = QFrame()
        search_f.setStyleSheet("background: white; border-radius: 10px; padding: 15px;")
        sf_lay = QHBoxLayout(search_f)
        self.txt_search_track = QLineEdit(placeholderText="Nhập số điện thoại khách hàng để tra cứu...")
        self.txt_search_track.setStyleSheet("padding: 12px; font-size: 15px; border: 1px solid #ddd;")
        btn_search_track = QPushButton("🔍 TRA CỨU")
        btn_search_track.clicked.connect(self.load_order_tracking)
        btn_search_track.setStyleSheet("background: #58111A; color: white; padding: 12px 25px; font-weight: bold; border-radius: 5px;")
        sf_lay.addWidget(self.txt_search_track)
        sf_lay.addWidget(btn_search_track)
        tracking_layout.addWidget(search_f)

        self.track_scroll = QScrollArea()
        self.track_scroll.setWidgetResizable(True)
        self.track_scroll.setStyleSheet("border: none;")
        self.track_container = QWidget()
        self.track_vbox = QVBoxLayout(self.track_container)
        self.track_vbox.setContentsMargins(10, 10, 10, 10)
        self.track_vbox.addStretch()
        self.track_scroll.setWidget(self.track_container)
        tracking_layout.addWidget(self.track_scroll)

    def validate_inputs(self):
        has_info = all([self.txt_phone.text().strip(), self.txt_name.text().strip(), self.txt_address.text().strip()])
        has_items = len(self.cart) > 0
        mode = self.combo_pay.currentText()
        
        if "VietQR" in mode or "ZaloPay" in mode:
            is_valid = has_info and has_items and self.chk_confirm_ck.isChecked()
        else:
            is_valid = has_info and has_items
        self.btn_pay.setEnabled(is_valid)

    def toggle_payment_mode(self):
        mode = self.combo_pay.currentText()
        if "VietQR" in mode or "ZaloPay" in mode:
            self.qr_container.show()
            self.update_qr_display()
        else:
            self.qr_container.hide()
            self.chk_confirm_ck.setChecked(False)
        self.validate_inputs()

    def update_qr_display(self):
        if self.total > 0 and self.qr_container.isVisible():
            mode = self.combo_pay.currentText()
            amount = int(self.total)
            phone = "0366388104"
            memo = f"SnackShop_{self.txt_phone.text()}"
            
            if "VietQR" in mode:
                url = f"https://img.vietqr.io/image/970467-{phone}-compact2.png?amount={amount}&addInfo={memo}"
            else:
                url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://social.zalopay.vn/mt/jws/p2p/transfer/v2?amount={amount}%26description={memo}%26phone={phone}"
            
            try:
                res = requests.get(url, timeout=5)
                img = QImage()
                img.loadFromData(res.content)
                self.qr_label.setPixmap(QPixmap.fromImage(img).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except Exception:
                self.qr_label.setText("Lỗi kết nối mạng...")

    def apply_discount(self):
        code = self.txt_promo.text().strip()
        if not code:
            return
        try:
            db = self.connect_db()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT gia_tri, loai_giam_gia FROM khuyenmai WHERE ma_code = %s AND trang_thai = 1", (code,))
            res = cur.fetchone()
            if res:
                if res['loai_giam_gia'] == 'sotien':
                    self.discount_val = float(res['gia_tri'])
                else:
                    self.discount_val = self.subtotal * (float(res['gia_tri']) / 100)
                QMessageBox.information(self, "Khuyến mãi", "Đã áp dụng mã thành công!")
            else:
                self.discount_val = 0
                QMessageBox.warning(self, "Khuyến mãi", "Mã giảm giá không chính xác hoặc đã hết hạn.")
            db.close()
            self.update_total()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi kiểm tra mã: {e}")

    def update_total(self):
        self.subtotal = sum(v['price'] * v['qty'] for v in self.cart.values())
        self.total = max(0, self.subtotal - self.discount_val)
        self.lbl_subtotal.setText(f"Tạm tính: {int(self.subtotal):,}đ")
        self.lbl_discount_info.setText(f"Giảm giá: -{int(self.discount_val):,}đ")
        self.lbl_total.setText(f"TỔNG: {int(self.total):,}đ")
        self.update_qr_display()
        self.validate_inputs()

    def load_products(self):
        try:
            db = self.connect_db()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT id, ten_sanpham, gia_ban, hinh_anh FROM sanpham WHERE so_luong_ton > 0")
            
            self.clear_grid()
            for i, p in enumerate(cur.fetchall()):
                card = QFrame()
                card.setFixedSize(165, 230)
                card.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
                l = QVBoxLayout(card)
                
                img_label = QLabel()
                img_label.setFixedSize(140, 100)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img_label.setStyleSheet("border: none;")
                if p.get('hinh_anh'):
                    pixmap = QPixmap(p['hinh_anh'])
                    if not pixmap.isNull():
                        img_label.setPixmap(pixmap.scaled(140, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    else:
                        img_label.setText("🖼️")
                else:
                    img_label.setText("🍴")
                l.addWidget(img_label)

                name_lbl = QLabel(f"<b>{p['ten_sanpham']}</b>")
                name_lbl.setWordWrap(True)
                name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                l.addWidget(name_lbl)
                l.addWidget(QLabel(f"<span style='color: #800000; font-weight: bold;'>{int(p['gia_ban']):,}đ</span>", alignment=Qt.AlignmentFlag.AlignCenter))

                btn = QPushButton("Thêm vào giỏ")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda ch, prod=p: self.add_to_cart(prod))

                # --- ĐOẠN ĐÃ SỬA MÀU ĐỎ ĐÔ LÊN TRƯỚC ---
                btn.setStyleSheet("""
                    QPushButton {
                        background: #58111A; 
                        color: white; 
                        font-weight: bold; 
                        border-radius: 6px; 
                        padding: 5px;
                        border: none;
                    }
                    QPushButton:hover {
                        background: #731823; /* Khi rê chuột vào sẽ sáng lên một chút cho đẹp */
                    }
                    QPushButton:pressed {
                        background: #3D0B12; /* Khi click chuột giữ nút sẽ tối đi một chút */
                    }
                """)
                l.addWidget(btn)
                self.grid.addWidget(card, i // 4, i % 4)
            db.close()
        except Exception as e:
            print(f"Lỗi load sản phẩm: {e}")

    def clear_grid(self):
        if not hasattr(self, 'grid'):
            return
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
    
    def refresh_product_list(self):
        self.clear_grid()
        self.load_products()

    def add_to_cart(self, p):
        name = p['ten_sanpham']
        if name not in self.cart:
            row = QFrame()
            row.setStyleSheet("background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; margin-bottom: 2px;")
            lay = QHBoxLayout(row)
            lbl = QLabel(f"<b>{name}</b>")
            lbl.setFixedWidth(130)
            lbl.setStyleSheet("color: #1E293B; background: transparent; border: none;")
            
            btn_m = QPushButton("-")
            btn_m.setFixedSize(24, 24)
            btn_m.setStyleSheet("background: #FAFAFA; border: 1px solid #E2E8F0; border-radius: 12px; font-weight: bold; color: #1E293B;")
            
            q_lbl = QLabel("1")
            q_lbl.setFixedWidth(30)
            q_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            q_lbl.setStyleSheet("background: transparent; border: none; color: #1E293B;")
            
            btn_p = QPushButton("+")
            btn_p.setFixedSize(24, 24)
            btn_p.setStyleSheet("background: #FAFAFA; border: 1px solid #E2E8F0; border-radius: 12px; font-weight: bold; color: #1E293B;")
            
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(30, 30)
            btn_del.setStyleSheet("color: #58111A; border: none; font-size: 16px; background: transparent;")
            
            lay.addWidget(lbl)
            lay.addWidget(btn_m)
            lay.addWidget(q_lbl)
            lay.addWidget(btn_p)
            lay.addStretch()
            lay.addWidget(btn_del)
            self.cart[name] = {"id": p['id'], "price": float(p['gia_ban']), "qty": 1, "q_lbl": q_lbl, "row": row}
            btn_p.clicked.connect(lambda checked, n=name: self.change_qty(n, 1))
            btn_m.clicked.connect(lambda checked, n=name: self.change_qty(n, -1))
            btn_del.clicked.connect(lambda checked, n=name: self.remove_item(n))
            self.cart_vbox.insertWidget(self.cart_vbox.count() - 1, row)
        else:
            self.change_qty(name, 1)
        self.update_total()

    def change_qty(self, name, delta):
        new_qty = self.cart[name]['qty'] + delta
        if new_qty <= 0:
            self.remove_item(name)
        else:
            self.cart[name]['qty'] = new_qty
            self.cart[name]['q_lbl'].setText(str(new_qty))
            self.update_total()

    def remove_item(self, name):
        if name in self.cart:
            self.cart[name]['row'].deleteLater()
            del self.cart[name]
            self.update_total()

    def save_invoice(self):
        db = None
        try:
            if not self.cart:
                QMessageBox.warning(self, "Thông báo", "Giỏ hàng đang trống!")
                return

            db = self.connect_db()
            db.autocommit = False
            cur = db.cursor(dictionary=True, buffered=True)

            ten_kh = self.txt_name.text().strip() or "Khách lẻ"
            sdt_kh = self.txt_phone.text().strip()
            dia_chi_kh = self.txt_address.text().strip()
            
            if not sdt_kh:
                raise Exception("Vui lòng nhập số điện thoại khách hàng!")

            # Xử lý khách hàng
            cur.execute("SELECT id, diem_tich_luy FROM khachhang WHERE so_dien_thoai = %s", (sdt_kh,))
            kh = cur.fetchone()
            diem_cu = 0
            if not kh:
                cur.execute("""
                    INSERT INTO khachhang (ten_khachhang, so_dien_thoai, dia_chi, diem_tich_luy, tong_chi_tieu) 
                    VALUES (%s, %s, %s, 0, 0)
                """, (ten_kh, sdt_kh, dia_chi_kh))
                id_kh_final = cur.lastrowid
            else:
                id_kh_final = kh['id']
                diem_cu = kh['diem_tich_luy']

            # Kiểm tra tồn kho sản phẩm và nguyên liệu
            for name, info in self.cart.items():
                id_sp = info['id']
                sl_mua = int(info['qty'])

                cur.execute("SELECT so_luong_ton FROM sanpham WHERE id = %s", (id_sp,))
                res_sp = cur.fetchone()
                if not res_sp or res_sp['so_luong_ton'] < sl_mua:
                    raise Exception(f"Sản phẩm '{name}' không đủ tồn kho!")

                cur.execute("""
                    SELECT n.id, n.ten_nguyenlieu, n.so_luong, c.dinh_luong
                    FROM congthuc c JOIN nguyenlieu n ON c.id_nguyenlieu = n.id
                    WHERE c.id_sanpham = %s
                """, (id_sp,))
                for nl in cur.fetchall():
                    tong_can = float(nl['dinh_luong']) * sl_mua
                    if float(nl['so_luong']) < tong_can:
                        raise Exception(f"Không đủ nguyên liệu cho món '{name}'!\nThiếu: {nl['ten_nguyenlieu']}")

            # Tạo đơn hàng
            trang_thai_mac_dinh = "Chờ xác nhận"
            hinh_thuc_tt = self.combo_pay.currentText()
            
            cur.execute("INSERT INTO donhang (ngay_tao, trang_thai, tong_tien) VALUES (NOW(), %s, %s)", 
                        (trang_thai_mac_dinh, float(self.total)))
            last_id = cur.lastrowid

            cur.execute("""
                INSERT INTO hoadon (id, ngay_tao, tong_tien, giam_gia, hinh_thuc_tt, trang_thai) 
                VALUES (%s, NOW(), %s, %s, %s, %s)
            """, (last_id, float(self.total), float(self.discount_val), hinh_thuc_tt, trang_thai_mac_dinh))

            list_mon_str = []
            for name, info in self.cart.items():
                id_sp = info['id']
                sl_mua = int(info['qty'])
                gia_ban = float(info['price'])
                list_mon_str.append(f"{sl_mua}x {name}")

                cur.execute("UPDATE sanpham SET so_luong_ton = so_luong_ton - %s WHERE id = %s", (sl_mua, id_sp))

                # Lấy tên người dùng an toàn (không gây lỗi foreign key)
                raw_user = self.user_info.get('ho_ten', '').strip()
                user_name = None
                if raw_user:
                    cur.execute("SELECT ho_ten FROM user WHERE ho_ten = %s", (raw_user,))
                    if cur.fetchone():
                        user_name = raw_user
                    else:
                        user_name = None  # hoặc có thể gán mặc định "Admin" nếu tồn tại
                # Trừ nguyên liệu và ghi lịch sử kho
                cur.execute("""
                    SELECT nguyenlieu.id, nguyenlieu.ten_nguyenlieu, nguyenlieu.so_luong, congthuc.dinh_luong
                    FROM congthuc 
                    JOIN nguyenlieu ON congthuc.id_nguyenlieu = nguyenlieu.id
                    WHERE congthuc.id_sanpham = %s
                """, (id_sp,))
                for nl in cur.fetchall():
                    # Lấy tồn trước
                    cur.execute("SELECT so_luong FROM nguyenlieu WHERE id = %s FOR UPDATE", (nl['id'],))
                    ton_truoc = cur.fetchone()['so_luong']
                    so_luong_tru = float(nl['dinh_luong']) * sl_mua
                    ton_sau = ton_truoc - so_luong_tru
                    # Cập nhật
                    cur.execute("UPDATE nguyenlieu SET so_luong = %s WHERE id = %s", (ton_sau, nl['id']))
                    # Ghi lịch sử (nguoi_dung có thể là NULL)
                    cur.execute("""
                        INSERT INTO lichsu_kho (loai_gd, ten_nl, so_luong, ton_truoc, ton_sau, ly_do, nguoi_dung, ngay_gd)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                    """, ("OUT", nl['ten_nguyenlieu'], -so_luong_tru, ton_truoc, ton_sau, f"Xuất cho đơn hàng #{last_id}", user_name))

                cur.execute("""
                    INSERT INTO chitiethoadon (id_hoadon, id_sanpham, so_luong, don_gia, thanh_tien)
                    VALUES (%s, %s, %s, %s, %s)
                """, (last_id, id_sp, sl_mua, gia_ban, (sl_mua * gia_ban)))

            # Điểm tích lũy
            diem_moi = int(self.total / 10000)
            diem_tru = 0
            if self.applied_voucher:
                diem_tru = self.applied_voucher['diem_doi']
                cur.execute("""
                    INSERT INTO lich_su_doi_diem (id_khachhang, id_voucher, diem_da_dung, gia_tri_giam, id_donhang)
                    VALUES (%s, %s, %s, %s, %s)
                """, (id_kh_final, self.applied_voucher['id'], diem_tru, int(self.discount_val), last_id))
            
            diem_cuoi = diem_cu - diem_tru + diem_moi
            cur.execute("""
                UPDATE khachhang SET 
                    diem_tich_luy = %s, 
                    tong_chi_tieu = tong_chi_tieu + %s 
                WHERE id = %s
            """, (diem_cuoi, float(self.total), id_kh_final))

            cur.execute("""
                INSERT INTO chitietdonhang 
                (id, id_nhanvien, id_khachhang, ngay_tao, tong_tien, ten_khach, sdt_khach, dia_chi, hinh_thuc_tt, trang_thai, danh_sach_mon, giam_gia)
                VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
            """, (last_id, self.nhanvien_id, id_kh_final, float(self.total), ten_kh, sdt_kh, dia_chi_kh,
                  hinh_thuc_tt, trang_thai_mac_dinh, ", ".join(list_mon_str), float(self.discount_val)))

            db.commit()
            
            
            thong_bao = f"✅ Đơn hàng #{last_id} thành công!\n💰 Tổng tiền: {int(self.total):,}đ\n"
            if diem_moi > 0:
                thong_bao += f"⭐ Được cộng {diem_moi} điểm tích lũy!\n"
            if diem_tru > 0:
                thong_bao += f"🎉 Đã sử dụng {diem_tru} điểm để nhận ưu đãi!\n"
            thong_bao += f"🏆 Tổng điểm hiện tại: {diem_cuoi} điểm"
            
            QMessageBox.information(self, "Thành công", thong_bao)
            self.reset_all()

        except Exception as e:
            if db:
                db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Giao dịch thất bại:\n{str(e)}")
        finally:
            if db:
                db.close()

    def reset_all(self):
        for v in list(self.cart.values()):
            v['row'].deleteLater()
        self.cart = {}
        self.discount_val = 0
        self.applied_voucher = None
        self.id_khachhang_hien_tai = None
        self.diem_khach_hien_tai = 0
        self.update_total()
        self.txt_name.clear()
        self.txt_phone.clear()
        self.txt_address.clear()
        self.txt_promo.clear()
        self.chk_confirm_ck.setChecked(False)

    def load_order_tracking(self):
        sdt = self.txt_search_track.text().strip()
        if not sdt:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập số điện thoại để tra cứu!")
            return

        while self.track_vbox.count() > 1:
            item = self.track_vbox.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        try:
            db = self.connect_db()
            cur = db.cursor(dictionary=True)
            cur.execute("""
                SELECT id, ngay_tao, tong_tien, trang_thai, danh_sach_mon, giam_gia
                FROM chitietdonhang 
                WHERE sdt_khach = %s 
                ORDER BY ngay_tao DESC, id DESC
            """, (sdt,))
            rows = cur.fetchall()
            
            if not rows:
                lbl = QLabel("❌ Không tìm thấy đơn hàng nào.")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: #64748B; font-size: 15px; margin-top: 20px;")
                self.track_vbox.insertWidget(0, lbl)
            else:
                for r in rows:
                    st = r['trang_thai']
                    if st == "Thành công":
                        bg_color, text_color = "#DCFCE7", "#166534"
                    elif st == "Đang giao":
                        bg_color, text_color = "#DBEAFE", "#1E40AF"
                    elif st == "Đã hủy":
                        bg_color, text_color = "#FEE2E2", "#991B1B"
                    else:
                        bg_color, text_color = "#FEF3C7", "#92400E"

                    card = QFrame()
                    card.setStyleSheet(f"""
                        QFrame {{
                            background-color: white;
                            border: 1px solid #E2E8F0;
                            border-radius: 15px;
                            padding: 15px;
                            margin-bottom: 10px;
                        }}
                        QFrame:hover {{
                            border: 1px solid #94A3B8;
                        }}
                    """)
                    layout_card = QVBoxLayout(card)

                    header = QHBoxLayout()
                    lbl_id = QLabel(f"🆔 ĐƠN HÀNG <b>#{r['id']}</b>")
                    lbl_id.setStyleSheet("font-size: 14px; color: #1E293B;")
                    lbl_date = QLabel(str(r['ngay_tao']))
                    lbl_date.setStyleSheet("color: #64748B; font-size: 12px;")
                    header.addWidget(lbl_id)
                    header.addStretch()
                    header.addWidget(lbl_date)
                    layout_card.addLayout(header)

                    lbl_items = QLabel(f"🍽️ {r['danh_sach_mon']}")
                    lbl_items.setWordWrap(True)
                    lbl_items.setStyleSheet("color: #334155; font-size: 14px; padding: 5px 0;")
                    layout_card.addWidget(lbl_items)

                    footer = QHBoxLayout()
                    lbl_status = QLabel(f" {st.upper()} ")
                    lbl_status.setStyleSheet(f"""
                        background-color: {bg_color};
                        color: {text_color};
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 11px;
                        padding: 4px;
                    """)
                    giam_gia = float(r.get('giam_gia', 0))
                    if giam_gia > 0:
                        lbl_total = QLabel(f"{int(r['tong_tien']):,}đ (đã giảm {int(giam_gia):,}đ)")
                    else:
                        lbl_total = QLabel(f"{int(r['tong_tien']):,}đ")
                    lbl_total.setStyleSheet("font-size: 18px; font-weight: 900; color: #B91C1C;")
                    footer.addWidget(lbl_status)
                    footer.addStretch()
                    footer.addWidget(lbl_total)
                    layout_card.addLayout(footer)

                    self.track_vbox.insertWidget(self.track_vbox.count() - 1, card)
            db.close()
        except Exception as e:
            print(f"Lỗi: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SnackShopPOS()
    win.show()
    sys.exit(app.exec())