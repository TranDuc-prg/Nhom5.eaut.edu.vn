products = []

def add_product():
    name = input("Nhập tên sản phẩm: ")
    price = input("Nhập giá: ")
    products.append({"name": name, "price": price})
    print("✔ Đã thêm sản phẩm!")

def show_products():
    if not products:
        print("❌ Chưa có sản phẩm")
    else:
        print("\n--- DANH SÁCH SẢN PHẨM ---")
        for i, p in enumerate(products, 1):
            print(f"{i}. {p['name']} - {p['price']}")

def menu():
    print("\n===== QUẢN LÝ CỬA HÀNG ĐỒ ĂN VẶT =====")
    print("1. Thêm sản phẩm")
    print("2. Xem danh sách sản phẩm")
    print("3. Thoát")

def main():
    while True:
        menu()
        choice = input("Chọn chức năng: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            show_products()
        elif choice == "3":
            print("Thoát chương trình")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    main()
