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
            print("👉 Thêm sản phẩm")
        elif choice == "2":
            print("👉 Danh sách sản phẩm")
        elif choice == "3":
            print("Thoát chương trình")
            break
        else:
            print("❌ Lựa chọn không hợp lệ")

if __name__ == "__main__":
    main()
