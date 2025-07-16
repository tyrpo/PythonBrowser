import sys
from PyQt5.QtWidgets import QApplication
from browser_main import BrowserMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserMainWindow()
    window.show()
    sys.exit(app.exec_())




