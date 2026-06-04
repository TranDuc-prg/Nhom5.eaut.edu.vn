import sys
import requests
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFrame, QScrollArea,
                             QGridLayout, QMessageBox, QComboBox, QCheckBox, QTabWidget)
from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6.QtCore import Qt

class SnackShopPOS(QWidget):
    def __init__(self, user_info=None):
        super().__init__()
        # Nhận ID nhân viên từ trang chính, mặc định là 5 nếu không có
        self.user_info = user_info or {"id": 5}
        self.nhanvien_id = self.user_info.get('id', 5)
        
        self.cart = {}
        self.subtotal = 0 
        self.discount_val = 0 
        self.total = 0
        self.db_config = {"host": "localhost", "user": "root", "password": "", "database": "quanly_snack_db"}
        
        self.init_ui()
        self.load_products()

    def connect_db(self):
        return mysql.connector.connect(**self.db_config)

    def init_ui(self):
            self.setWindowTitle("Snack Shop POS -Giao diện khách hàng ")
            self.resize(1300, 850)
            self.setStyleSheet("background-color: #F8FAFC;") 

            # --- PHẦN MỚI: TẠO TAB ĐỂ CHỨA CẢ MUA HÀNG VÀ THEO DÕI ---
            self.layout_tong_chinh = QVBoxLayout(self)
            self.tabs = QTabWidget()
            self.layout_tong_chinh.addWidget(self.tabs)

            # 1. TẠO TAB MUA SẮM (Chứa code cũ của bạn)
            self.tab_mua_sam = QWidget()
            self.tabs.addTab(self.tab_mua_sam, " ĐẶT MÓN")
            main_layout = QHBoxLayout(self.tab_mua_sam) # Gán layout cũ vào Tab này

            # --- PANEL TRÁI: THỰC ĐƠN (GIỮ NGUYÊN CODE CŨ) ---
            left_side = QVBoxLayout()
            header_left = QLabel("DANH SÁCH THỰC ĐƠN")
            header_left.setStyleSheet("font-size: 22px; font-weight: bold; color: #1E293B; padding: 10px;")
            left_side.addWidget(header_left)
            
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("border: none; background: transparent;")
            self.container = QWidget()
            self.grid = QGridLayout(self.container)
            self.grid.setSpacing(15)
            scroll.setWidget(self.container)
            left_side.addWidget(scroll)
            main_layout.addLayout(left_side, 7)

            # --- PANEL PHẢI: THANH TOÁN (GIỮ NGUYÊN CODE CŨ) ---
            self.right_scroll = QScrollArea()
            self.right_scroll.setFixedWidth(460)
            self.right_scroll.setWidgetResizable(True)
            self.right_scroll.setStyleSheet("border: none; background: white; border-radius: 20px;")
            
            self.right_widget = QWidget()
            self.right_widget.setStyleSheet("background: white;")
            right_layout = QVBoxLayout(self.right_widget)
            right_layout.setContentsMargins(15, 15, 15, 15)
            right_layout.setSpacing(12)

            # 1. Thông tin khách
            right_layout.addWidget(QLabel("<b>👤 THÔNG TIN KHÁCH HÀNG</b>"))
            self.txt_phone = QLineEdit(placeholderText="Số điện thoại (Bắt buộc)...")
            self.txt_name = QLineEdit(placeholderText="Tên khách hàng (Bắt buộc)...")
            self.txt_address = QLineEdit(placeholderText="Địa chỉ nhận hàng (Bắt buộc)...")
            
            for w in [self.txt_phone, self.txt_name, self.txt_address]:
                w.setStyleSheet("padding: 10px; border: 1px solid #CBD5E1; border-radius: 8px;")
                w.textChanged.connect(self.validate_inputs)
                right_layout.addWidget(w)

            # 2. Giỏ hàng
            right_layout.addWidget(QLabel("<b>🛒 GIỎ HÀNG</b>"))
            self.cart_scroll = QScrollArea()
            self.cart_scroll.setMinimumHeight(250)
            self.cart_container = QWidget()
            self.cart_vbox = QVBoxLayout(self.cart_container)
            self.cart_vbox.setContentsMargins(5, 5, 5, 5)
            self.cart_vbox.addStretch() 
            self.cart_scroll.setWidget(self.cart_container)
            self.cart_scroll.setWidgetResizable(True)
            self.cart_scroll.setStyleSheet("background: #F1F5F9; border-radius: 10px; border: none;")
            right_layout.addWidget(self.cart_scroll)

            # 3. Khuyến mãi & Tiền
            summary_frame = QFrame()
            summary_frame.setStyleSheet("background: #F8FAFC; border-radius: 12px; padding: 10px; border: 1px solid #E2E8F0;")
            summary_lay = QVBoxLayout(summary_frame)
            
            promo_row = QHBoxLayout()
            self.txt_promo = QLineEdit(placeholderText="Mã giảm giá...")
            self.txt_promo.setStyleSheet("padding: 8px; border: 1px solid #CBD5E1; border-radius: 5px; background: white;")
            self.btn_apply = QPushButton("ÁP DỤNG")
            self.btn_apply.clicked.connect(self.apply_discount)
            self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_apply.setStyleSheet("background: #800000; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
            promo_row.addWidget(self.txt_promo)
            promo_row.addWidget(self.btn_apply)
            summary_lay.addLayout(promo_row)

            self.lbl_subtotal = QLabel("Tạm tính: 0đ")
            self.lbl_discount_info = QLabel("Giảm giá: -0đ")
            self.lbl_discount_info.setStyleSheet("color: #E11D48; font-weight: bold;")
            self.lbl_total = QLabel("TỔNG: 0đ")
            self.lbl_total.setStyleSheet("font-size: 24px; font-weight: 900; color: #800000;")
            
            summary_lay.addWidget(self.lbl_subtotal)
            summary_lay.addWidget(self.lbl_discount_info)
            summary_lay.addWidget(self.lbl_total)
            right_layout.addWidget(summary_frame)

            # 4. Hình thức thanh toán
            right_layout.addWidget(QLabel("<b>💳 HÌNH THỨC THANH TOÁN</b>"))
            self.combo_pay = QComboBox()
            self.combo_pay.addItems(["Tiền mặt", "Chuyển khoản VietQR", "ZaloPay"])
            self.combo_pay.setStyleSheet("padding: 10px; border-radius: 8px; background: #F1F5F9; border: 1px solid #CBD5E1;")
            self.combo_pay.currentIndexChanged.connect(self.toggle_payment_mode)
            right_layout.addWidget(self.combo_pay)

            # Khu vực QR
            self.qr_container = QFrame()
            self.qr_container.setMinimumHeight(230)
            self.qr_vbox = QVBoxLayout(self.qr_container)
            self.qr_label = QLabel("Đang tạo mã QR...")
            self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.qr_label.setFixedSize(180, 180)
            self.chk_confirm_ck = QCheckBox("Tôi xác nhận đã nhận đủ tiền")
            self.chk_confirm_ck.setStyleSheet("font-weight: bold; color: #166534;")
            self.chk_confirm_ck.stateChanged.connect(self.validate_inputs)
            
            self.qr_vbox.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)
            self.qr_vbox.addWidget(self.chk_confirm_ck, alignment=Qt.AlignmentFlag.AlignCenter)
            self.qr_container.hide()
            right_layout.addWidget(self.qr_container)

            # 5. Nút Xuất hóa đơn
            right_layout.addStretch()
            self.btn_pay = QPushButton("XUẤT HÓA ĐƠN")
            self.btn_pay.setFixedHeight(55)
            self.btn_pay.setEnabled(False)
            self.btn_pay.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_pay.setStyleSheet("""
                QPushButton { background: #800000; color: white; font-weight: bold; border-radius: 12px; font-size: 18px; }
                QPushButton:hover { background: #A00000; }
                QPushButton:disabled { background: #CBD5E1; color: #64748B; }
            """)
            self.btn_pay.clicked.connect(self.save_invoice)
            right_layout.addWidget(self.btn_pay)

            self.right_scroll.setWidget(self.right_widget)
            main_layout.addWidget(self.right_scroll)

            # --- PHẦN MỚI: TẠO TAB THEO DÕI ĐƠN HÀNG ---
            self.tab_theo_doi = QWidget()
            self.tabs.addTab(self.tab_theo_doi, "🚚 THEO DÕI ĐƠN HÀNG")
            tracking_layout = QVBoxLayout(self.tab_theo_doi)

            # Thanh tìm kiếm
            search_f = QFrame()
            search_f.setStyleSheet("background: white; border-radius: 10px; padding: 15px;")
            sf_lay = QHBoxLayout(search_f)
            self.txt_search_track = QLineEdit(placeholderText="Nhập số điện thoại khách hàng để tra cứu...")
            self.txt_search_track.setStyleSheet("padding: 12px; font-size: 15px; border: 1px solid #ddd;")
            btn_search_track = QPushButton("🔍 TRA CỨU")
            btn_search_track.clicked.connect(self.load_order_tracking)
            btn_search_track.setStyleSheet("background: #1E293B; color: white; padding: 12px 25px; font-weight: bold; border-radius: 5px;")
            sf_lay.addWidget(self.txt_search_track)
            sf_lay.addWidget(btn_search_track)
            tracking_layout.addWidget(search_f)

            # Danh sách đơn hàng trả về
            self.track_scroll = QScrollArea()
            self.track_scroll.setWidgetResizable(True)
            self.track_scroll.setStyleSheet("border: none;")
            self.track_container = QWidget()
            self.track_vbox = QVBoxLayout(self.track_container)
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
            else: # ZaloPay
                url = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://social.zalopay.vn/mt/jws/p2p/transfer/v2?amount={amount}%26description={memo}%26phone={phone}"
            
            try:
                res = requests.get(url, timeout=5)
                img = QImage()
                img.loadFromData(res.content)
                self.qr_label.setPixmap(QPixmap.fromImage(img).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except: 
                self.qr_label.setText("Lỗi kết nối mạng...")

    def apply_discount(self):
        code = self.txt_promo.text().strip()
        if not code: return
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
                QMessageBox.information(self, "Khuyến mãi", f"Đã áp dụng mã thành công!")
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
            for i, p in enumerate(cur.fetchall()):
                card = QFrame()
                card.setFixedSize(165, 210)
                card.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E2E8F0;")
                l = QVBoxLayout(card)
                
                img_label = QLabel()
                img_label.setFixedSize(120, 100)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                if p['hinh_anh']:
                    pixmap = QPixmap(p['hinh_anh'])
                    img_label.setPixmap(pixmap.scaled(
                        120, 100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    ))
                else:
                    img_label.setText("No Image")

                l.addWidget(img_label)
                
                name_lbl = QLabel(f"<b>{p['ten_sanpham']}</b>")
                name_lbl.setWordWrap(True)
                name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                l.addWidget(name_lbl)
                
                l.addWidget(QLabel(f"<span style='color: #800000; font-weight: bold;'>{int(p['gia_ban']):,}đ</span>", alignment=Qt.AlignmentFlag.AlignCenter))
                
                btn = QPushButton("Thêm vào giỏ")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda ch, prod=p: self.add_to_cart(prod))
                btn.setStyleSheet("background: #F1F5F9; font-weight: bold; border-radius: 6px; padding: 5px;")
                l.addWidget(btn)
                
                self.grid.addWidget(card, i // 4, i % 4)
            db.close()
        except Exception as e:
            print(f"Lỗi load sản phẩm: {e}")

    def add_to_cart(self, p):
        name = p['ten_sanpham']
        if name not in self.cart:
            row = QFrame()
            row.setStyleSheet("background: white; border-radius: 8px; margin-bottom: 2px;")
            lay = QHBoxLayout(row)
            
            lbl = QLabel(f"<b>{name}</b>")
            lbl.setFixedWidth(130)
            
            btn_m = QPushButton("-")
            btn_m.setFixedSize(24, 24)
            btn_m.setStyleSheet("background: #E2E8F0; border-radius: 12px; font-weight: bold;")
            
            q_lbl = QLabel("1")
            q_lbl.setFixedWidth(30)
            q_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn_p = QPushButton("+")
            btn_p.setFixedSize(24, 24)
            btn_p.setStyleSheet("background: #E2E8F0; border-radius: 12px; font-weight: bold;")
            
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(30, 30)
            btn_del.setStyleSheet("color: red; border: none; font-size: 16px;")
            
            lay.addWidget(lbl)
            lay.addWidget(btn_m)
            lay.addWidget(q_lbl)
            lay.addWidget(btn_p)
            lay.addStretch()
            lay.addWidget(btn_del)
            
            self.cart[name] = {"id": p['id'], "price": float(p['gia_ban']), "qty": 1, "q_lbl": q_lbl, "row": row}
            
            btn_p.clicked.connect(lambda: self.change_qty(name, 1))
            btn_m.clicked.connect(lambda: self.change_qty(name, -1))
            btn_del.clicked.connect(lambda: self.remove_item(name))
            
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
        try:
            db = self.connect_db()
            cur = db.cursor(dictionary=True)
            
            ten_kh = self.txt_name.text().strip()
            sdt_kh = self.txt_phone.text().strip()
            dia_chi_kh = self.txt_address.text().strip()
            list_mon = ", ".join([f"{v['qty']}x {k}" for k, v in self.cart.items()])
            tong_tien_bill = float(self.total)

            if not sdt_kh:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số điện thoại khách hàng!")
                return

            cur.execute("SELECT id FROM khachhang WHERE so_dien_thoai = %s", (sdt_kh,))
            kh = cur.fetchone()
            id_kh_final = None
            
            if not kh:
                sql_ins_kh = """INSERT INTO khachhang (ten_khachhang, so_dien_thoai, dia_chi, diem_tich_luy, tong_chi_tieu) 
                                VALUES (%s, %s, %s, 0, 0)"""
                cur.execute(sql_ins_kh, (ten_kh or "Khách lẻ", sdt_kh, dia_chi_kh))
                id_kh_final = cur.lastrowid
            else:
                id_kh_final = kh['id']
                cur.execute("UPDATE khachhang SET ten_khachhang=%s, dia_chi=%s WHERE id=%s", 
                        (ten_kh, dia_chi_kh, id_kh_final))

            sql_dh = """INSERT INTO chitietdonhang 
                        (id_nhanvien, id_khachhang, ngay_tao, tong_tien, ten_khach, sdt_khach, dia_chi, hinh_thuc_tt, trang_thai, danh_sach_mon, giam_gia) 
                        VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cur.execute(sql_dh, (
                self.nhanvien_id, 
                id_kh_final, 
                tong_tien_bill, 
                ten_kh, 
                sdt_kh, 
                dia_chi_kh, 
                self.combo_pay.currentText(), 
                "Chờ xác nhận", 
                list_mon,
                self.discount_val
            ))
            
            db.commit()
            db.close()
            
            QMessageBox.information(self, "Thành công", f"Đơn hàng #{cur.lastrowid} đã được tạo!\nTrạng thái: CHỜ XÁC NHẬN")
            self.reset_all()
            
        except Exception as e:
            if 'db' in locals() and db.is_connected(): db.rollback()
            QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể tạo đơn hàng: {str(e)}")

    def reset_all(self):
        for v in list(self.cart.values()):
            v['row'].deleteLater()
        self.cart = {}
        self.discount_val = 0
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

            # Xóa danh sách cũ
            while self.track_vbox.count() > 1:
                item = self.track_vbox.takeAt(0)
                if item.widget(): item.widget().deleteLater()

            try:
                db = self.connect_db()
                cur = db.cursor(dictionary=True)
                cur.execute("SELECT id, ngay_tao, tong_tien, trang_thai, danh_sach_mon FROM chitietdonhang WHERE sdt_khach = %s ORDER BY id DESC", (sdt,))
                rows = cur.fetchall()
                
                if not rows:
                    lbl = QLabel("❌ Không tìm thấy đơn hàng nào.")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lbl.setStyleSheet("color: #64748B; font-size: 15px; margin-top: 20px;")
                    self.track_vbox.insertWidget(0, lbl)
                else:
                    for r in rows:
                        # Quyết định màu sắc dựa trên trạng thái
                        st = r['trang_thai']
                        if st == "Thành công":
                            bg_color, text_color = "#DCFCE7", "#166534"  # Xanh lá
                        elif st == "Đang giao":
                            bg_color, text_color = "#DBEAFE", "#1E40AF"  # Xanh dương
                        elif st == "Đã hủy":
                            bg_color, text_color = "#FEE2E2", "#991B1B"  # Đỏ
                        else: # Chờ xác nhận
                            bg_color, text_color = "#FEF3C7", "#92400E"  # Vàng cam

                        card = QFrame()
                        # CSS làm đẹp: Có đổ bóng nhẹ và viền bo tròn
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

                        # Header: Mã đơn và Ngày tạo
                        header = QHBoxLayout()
                        lbl_id = QLabel(f"🆔 ĐƠN HÀNG <b>#{r['id']}</b>")
                        lbl_id.setStyleSheet("font-size: 14px; color: #1E293B;")
                        lbl_date = QLabel(str(r['ngay_tao']))
                        lbl_date.setStyleSheet("color: #64748B; font-size: 12px;")
                        header.addWidget(lbl_id)
                        header.addStretch()
                        header.addWidget(lbl_date)
                        layout_card.addLayout(header)

                        # Nội dung món ăn
                        lbl_items = QLabel(f"🍽️ {r['danh_sach_mon']}")
                        lbl_items.setWordWrap(True)
                        lbl_items.setStyleSheet("color: #334155; font-size: 14px; padding: 5px 0;")
                        layout_card.addWidget(lbl_items)

                        # Dòng cuối: Trạng thái và Tổng tiền
                        footer = QHBoxLayout()
                        
                        # Label Trạng thái kiểu Badge (huy hiệu)
                        lbl_status = QLabel(f" {st.upper()} ")
                        lbl_status.setStyleSheet(f"""
                            background-color: {bg_color};
                            color: {text_color};
                            border-radius: 6px;
                            font-weight: bold;
                            font-size: 11px;
                            padding: 4px;
                        """)
                        
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