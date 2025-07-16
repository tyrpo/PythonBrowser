from PyQt5.QtCore import QUrl


def safe_qurl(url):
    if not isinstance(url, str) or not url:
        url = "https://www.google.com"
    return QUrl(url)
