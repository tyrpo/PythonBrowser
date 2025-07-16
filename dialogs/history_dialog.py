from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QMessageBox


class HistoryDialog(QDialog):
    def __init__(self, history, clear_callback):
        super().__init__()
        self.setWindowTitle("История посещений")
        self.setMinimumSize(600, 400)
        self.history = history
        self.clear_callback = clear_callback
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        for entry in self.history:
            dt = entry.get("time", "unknown time")
            url = entry.get("url", "")
            item = QListWidgetItem(f"[{dt}] {url}")
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)
        self.setLayout(layout)

    def clear_history(self):
        if QMessageBox.question(self, "Подтверждение", "Очистить всю историю?") == QMessageBox.Yes:
            self.clear_callback()
            self.list_widget.clear()
