import sqlite3

# Kết nối database (tạo nếu chưa có)
conn = sqlite3.connect("database/data.db")
cursor = conn.cursor()

# Tạo bảng nếu chưa có
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price TEXT
)
""")
conn.commit()


# ===== CHỨC NĂNG =====

def add_product():
    name = input("Nhập tên sản phẩm: ")
    price = input("Nhập giá: ")

    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, price))
    conn.commit()

    print("✔ Đã thêm sản phẩm!")

def show_products():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if not products:
        print("❌ Chưa có sản phẩm")
    else:
        print("\n--- DANH SÁCH SẢN PHẨM ---")
        for p in products:
            print(f"{p[0]}. {p[1]} - {p[2]}")

def delete_product():
    show_products()
    id = input("Nhập ID cần xoá: ")

    cursor.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()

    print("✔ Đã xoá!")

def menu():
    print("\n===== QUẢN LÝ CỬA HÀNG ĐỒ ĂN VẶT =====")
    print("1. Thêm sản phẩm")
    print("2. Xem danh sách sản phẩm")
    print("3. Xoá sản phẩm")
    print("4. Thoát")

def main():
    while True:
        menu()
        choice = input("Chọn chức năng: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            show_products()
        elif choice == "3":
            delete_product()
        elif choice == "4":
            print("Thoát chương trình")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    main()
