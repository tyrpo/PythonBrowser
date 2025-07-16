import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QLineEdit, QPushButton, QToolBar,
    QAction, QFileDialog, QLabel, QProgressBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

from dialogs.downloads_dialog import DownloadsDialog
from dialogs.history_dialog import HistoryDialog
from utils import safe_qurl

HISTORY_FILE = "history.json"
TABS_FILE = "tabs.json"


class BrowserTab(QWebEngineView):
    def __init__(self, url="https://www.google.com"):
        super().__init__()
        self.setUrl(safe_qurl(url))


class BrowserMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PythonBrowser")
        self.setGeometry(100, 100, 1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.history = self.load_history()
        self.downloads = []

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.history_action = QAction("📖", self)
        self.history_action.triggered.connect(self.show_history)
        self.toolbar.addAction(self.history_action)

        self.back_action = QAction("◀", self)
        self.back_action.triggered.connect(self.go_back)
        self.toolbar.addAction(self.back_action)

        self.forward_action = QAction("▶", self)
        self.forward_action.triggered.connect(self.go_forward)
        self.toolbar.addAction(self.forward_action)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.urlbar)

        self.reload_btn = QPushButton("🔄")
        self.reload_btn.clicked.connect(self.reload_page)
        self.toolbar.addWidget(self.reload_btn)

        self.downloads_btn = QPushButton("🗂")
        self.downloads_btn.clicked.connect(self.show_downloads)
        self.toolbar.addWidget(self.downloads_btn)

        self.new_tab_btn = QPushButton("➕")
        self.new_tab_btn.clicked.connect(self.add_new_tab)
        self.toolbar.addWidget(self.new_tab_btn)

        self.status = QLabel()
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(200)
        self.statusBar().addWidget(self.status)
        self.statusBar().addWidget(self.progress)

        self.tabs.currentChanged.connect(self.current_tab_changed)

        self.load_tabs()

        if self.tabs.count() == 0:
            self.add_new_tab()

    def add_new_tab(self, url="https://www.google.com"):
        new_tab = BrowserTab(url)
        index = self.tabs.addTab(new_tab, "Новая вкладка")
        self.tabs.setCurrentIndex(index)

        new_tab.urlChanged.connect(self.update_urlbar)
        new_tab.loadFinished.connect(self.update_title)
        new_tab.page().profile().downloadRequested.connect(self.handle_download)

    def update_urlbar(self, qurl):
        if self.tabs.currentWidget():
            self.urlbar.setText(qurl.toString())

    def update_title(self):
        current = self.tabs.currentWidget()
        if current:
            title = current.page().title()
            index = self.tabs.currentIndex()
            self.tabs.setTabText(index, title)
            self.history.append({
                "url": current.url().toString(),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            self.save_history()

    def navigate_to_url(self):
        url = self.urlbar.text()
        if not url.startswith("http"):
            url = "http://" + url
        current = self.tabs.currentWidget()
        if current:
            current.setUrl(safe_qurl(url))

    def reload_page(self):
        current = self.tabs.currentWidget()
        if current:
            current.reload()

    def go_back(self):
        current = self.tabs.currentWidget()
        if current and current.history().canGoBack():
            current.back()

    def go_forward(self):
        current = self.tabs.currentWidget()
        if current and current.history().canGoForward():
            current.forward()

    def show_history(self):
        dialog = HistoryDialog(self.history, self.clear_history)
        dialog.exec_()

    def clear_history(self):
        self.history = []
        self.save_history()

    def show_downloads(self):
        dialog = DownloadsDialog(self.downloads)
        dialog.exec_()

    def handle_download(self, download_item):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл как...", download_item.path(), "All Files (*)")
        if path:
            download_item.setPath(path)
            download_item.accept()
            dl_info = {
                "filename": os.path.basename(path),
                "path": path,
                "status": "Загрузка..."
            }
            self.downloads.append(dl_info)

            def progress(received, total):
                if total > 0:
                    perc = int(received / total * 100)
                    self.status.setText(f"Загрузка {dl_info['filename']}: {perc}%")
                    self.progress.setValue(perc)

            def finished():
                dl_info["status"] = "Завершено"
                self.status.setText(f"Загрузка {dl_info['filename']} завершена")
                self.progress.setValue(0)

            download_item.downloadProgress.connect(progress)
            download_item.finished.connect(finished)

    def current_tab_changed(self, index):
        current = self.tabs.widget(index)
        if current:
            self.urlbar.setText(current.url().toString())
            self.tabs.setTabText(index, current.page().title())

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def load_tabs(self):
        if os.path.exists(TABS_FILE):
            with open(TABS_FILE, "r", encoding="utf-8") as f:
                urls = json.load(f)
            for url in urls:
                self.add_new_tab(url)
        else:
            self.add_new_tab()

    def save_tabs(self):
        urls = [self.tabs.widget(i).url().toString() for i in range(self.tabs.count())]
        with open(TABS_FILE, "w", encoding="utf-8") as f:
            json.dump(urls, f, ensure_ascii=False, indent=4)

    def closeEvent(self, event):
        self.save_tabs()
        self.save_history()
        event.accept()

