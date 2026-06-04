import sys
from PyQt6.QtWidgets import QApplication
from login import SnackShopLogin

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SnackShopLogin()
    window.showMaximized()   
    sys.exit(app.exec())