from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem


class DownloadsDialog(QDialog):
    def __init__(self, downloads_list):
        super().__init__()
        self.setWindowTitle("Загрузки")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        for dl in downloads_list:
            item = QListWidgetItem(f"{dl['filename']} — {dl['status']} — {dl.get('path','')}")
            self.list_widget.addItem(item)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

