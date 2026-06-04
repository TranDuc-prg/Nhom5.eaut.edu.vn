import mysql.connector
from mysql.connector import Error

class BackendSQL:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='quanly_snack_db', 
                user='root',            
                password=''             
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Kết nối MySQL thành công!")
        except Error as e:
            print(f"Lỗi kết nối: {e}")

    # --- BUSINESS LOGIC: QUẢN LÝ MÓN ĂN ---
    def lay_danh_sach_mon(self):
        self.cursor.execute("SELECT * FROM SanPham")
        return self.cursor.fetchall()

    # --- BUSINESS LOGIC: BÁN HÀNG ---
    def tao_hoa_don(self, danh_sach_chon, tong_tien):
        try:
            # 1. Thêm vào bảng HoaDon
            query_hd = "INSERT INTO HoaDon (tong_tien) VALUES (%s)"
            self.cursor.execute(query_hd, (tong_tien,))
            id_hoadon = self.cursor.lastrowid

            # 2. Thêm vào ChiTietHoaDon và trừ kho
            for item in danh_sach_chon:
                # item giả định: (id_sp, so_luong, gia)
                query_ct = "INSERT INTO ChiTietHoaDon (id_hoadon, id_sanpham, so_luong) VALUES (%s, %s, %s)"
                self.cursor.execute(query_ct, (id_hoadon, item['id'], item['so_luong']))
                
                # Logic trừ kho
                query_kho = "UPDATE SanPham SET so_luong_kho = so_luong_kho - %s WHERE id = %s"
                self.cursor.execute(query_kho, (item['so_luong'], item['id']))

            self.connection.commit()
            return True
        except Error as e:
            print(f"Lỗi thanh toán: {e}")
            self.connection.rollback()
            return False