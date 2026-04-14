import customtkinter as ctk
from database import connect_db
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import messagebox

class AutoCareApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ chính
        self.title("AutoCare Manager - Desktop Admin System")
        self.geometry("1200x800")
        ctk.set_appearance_mode("light")
        
        # Layout 1x2 (Sidebar x Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="AutoCare Manager", 
                                font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        self.logo.pack(pady=30)

        # Menu điều hướng
        menu_options = [
            ("Tổng quan", self.show_dashboard),
            ("Khách hàng", self.show_customers),
            ("Xe", self.show_cars),
            ("Dịch vụ", self.show_services),
            ("Kho hàng", self.show_inventory),
            ("Nhân viên", self.show_employees)
        ]

        for text, command in menu_options:
            btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", 
                                text_color="gray80", hover_color="#333333",
                                anchor="w", height=40, command=command)
            btn.pack(fill="x", padx=20, pady=5)

        # --- CONTENT AREA ---
        self.content_frame = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # Khởi tạo màn hình mặc định
        self.show_dashboard()

    def clear_content(self):
        """Xóa các widget cũ trước khi chuyển tab"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ================= 1. GIAO DIỆN TỔNG QUAN =================
    def show_dashboard(self):
        self.clear_content()
        
        header = ctk.CTkLabel(self.content_frame, text="Tổng quan", 
                             font=("Arial", 28, "bold"), text_color="black")
        header.pack(anchor="w", padx=30, pady=(20, 10))

        # Lấy dữ liệu thực từ DB
        db = connect_db()
        stats = {"KH": 0, "Xe": 0}
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            stats["KH"] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM cars")
            stats["Xe"] = cursor.fetchone()[0]
            db.close()

        # Container cho các Card
        cards_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20)

        # Thông tin các Card
        items = [
            ("Tổng khách hàng", str(stats["KH"]), "#2563eb", "↑ 12%"),
            ("Xe quản lý", str(stats["Xe"]), "#059669", "↑ 8%"),
            ("Lịch hẹn tháng", "156", "#dc2626", "↓ 3%"),
            ("Doanh thu tháng", "67tr", "#7c3aed", "↑ 15%")
        ]

        for title, val, color, trend in items:
            card = ctk.CTkFrame(cards_frame, fg_color="white", corner_radius=15, width=230, height=120)
            card.pack_propagate(False)
            card.pack(side="left", padx=10, pady=10)
            
            ctk.CTkLabel(card, text=title, font=("Arial", 13), text_color="gray").pack(pady=(15,0))
            ctk.CTkLabel(card, text=val, font=("Arial", 30, "bold"), text_color=color).pack()
            ctk.CTkLabel(card, text=trend, font=("Arial", 11), text_color="green" if "↑" in trend else "red").pack()

        # Biểu đồ doanh thu
        chart_container = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=15)
        chart_container.pack(fill="both", expand=True, padx=30, pady=20)
        self.plot_chart(chart_container)

    def plot_chart(self, parent):
        fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
        months = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']
        rev = [30, 45, 38, 55, 48, 62]
        ax.plot(months, rev, marker='o', color='#2563eb')
        ax.set_title("Biến động doanh thu (Triệu VNĐ)")
        
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ================= 2. GIAO DIỆN KHÁCH HÀNG =================
    def show_customers(self):
        self.clear_content()
        
        # Thanh tiêu đề và nút thêm
        top_bar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkLabel(top_bar, text="Quản lý khách hàng", font=("Arial", 24, "bold"), text_color="black").pack(side="left")
        ctk.CTkButton(top_bar, text="+ Thêm khách hàng", fg_color="#2563eb", text_color="white").pack(side="right")

        # Khung tìm kiếm
        search_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Tìm kiếm khách hàng...", width=400)
        search_entry.pack(anchor="w", padx=30, pady=10)

        # Bảng hiển thị (Dùng ScrollableFrame)
        table_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="white", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Header bảng
        headers = ["ID", "Họ tên", "Số điện thoại", "Email", "Thao tác"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=("Arial", 13, "bold"), text_color="black").grid(row=0, column=i, padx=20, pady=10, sticky="w")

        # Tải dữ liệu từ SQL
        db = connect_db()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT id, full_name, phone, email FROM customers")
            rows = cursor.fetchall()
            for r_idx, row in enumerate(rows, start=1):
                for c_idx, val in enumerate(row):
                    ctk.CTkLabel(table_frame, text=str(val), text_color="black").grid(row=r_idx, column=c_idx, padx=20, pady=5, sticky="w")
                # Nút xóa
                ctk.CTkButton(table_frame, text="Xóa", width=60, height=25, fg_color="#ef4444", 
                             command=lambda id=row[0]: self.delete_customer(id)).grid(row=r_idx, column=4, padx=20)
            db.close()

    def delete_customer(self, cust_id):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa khách hàng này?"):
            db = connect_db()
            if db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM customers WHERE id = %s", (cust_id,))
                db.commit()
                db.close()
                self.show_customers()

    # ================= CÁC MỤC KHÁC (STUB) =================
    def show_cars(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Quản lý xe - Đang phát triển", font=("Arial", 20), text_color="gray").pack(pady=50)

    def show_services(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Dịch vụ - Đang phát triển", font=("Arial", 20), text_color="gray").pack(pady=50)

    def show_inventory(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Kho hàng - Đang phát triển", font=("Arial", 20), text_color="gray").pack(pady=50)

    def show_employees(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Nhân viên - Đang phát triển", font=("Arial", 20), text_color="gray").pack(pady=50)

if __name__ == "__main__":
    app = AutoCareApp()
    app.mainloop()