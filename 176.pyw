# 176.py
# Ultra-dark private browser "176"
# PyQt5 + WebEngine, fully private, modern Opera-style UI
# Author: You, ready for GitHub

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QToolButton, QHBoxLayout, QWidget, QLabel, QProgressBar, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo
from PyQt5.QtCore import QUrl, QByteArray

# ---------------------------
# Private Interceptor (DNT)
# ---------------------------
class PrivateInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        info.setHttpHeader(b"DNT", b"1")
        try:
            info.setHttpHeader(b"Referer", QByteArray(b""))
        except Exception:
            pass

# ---------------------------
# Main Browser Class
# ---------------------------
class Browser176(QMainWindow):
    HOME_URL = "https://duckduckgo.com"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("176 — Private Browser")
        self.setWindowIcon(self._create_icon())
        self.resize(1300, 850)

        self._create_private_profile()
        self._setup_ui()
        self._apply_dark_theme()
        self.show()

    # ---------------------------
    # Custom Window Icon
    # ---------------------------
    def _create_icon(self):
        pix = QtGui.QPixmap(64, 64)
        pix.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pix)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(QtGui.QColor("#00d4ff")))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(0, 0, 64, 64)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(25,25,25)))
        painter.drawEllipse(16,8,48,48)
        painter.end()
        return QtGui.QIcon(pix)

    # ---------------------------
    # Private Profile
    # ---------------------------
    def _create_private_profile(self):
        self.profile = QWebEngineProfile(self)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.profile.setCachePath("")
        self.profile.setPersistentStoragePath("")
        self.interceptor = PrivateInterceptor(self)
        self.profile.setRequestInterceptor(self.interceptor)

    # ---------------------------
    # Setup UI
    # ---------------------------
    def _setup_ui(self):
        # Web engine
        self.web = QWebEngineView()
        page = QWebEnginePage(self.profile, self.web)
        self.web.setPage(page)
        self.web.setUrl(QUrl(self.HOME_URL))
        self.setCentralWidget(self.web)

        # Toolbar
        nav = QtWidgets.QToolBar("Navigation")
        nav.setMovable(False)
        nav.setIconSize(QtCore.QSize(20,20))
        self.addToolBar(nav)

        # Back
        back_btn = QAction("◀", self)
        back_btn.triggered.connect(self.web.back)
        nav.addAction(back_btn)

        # Forward
        fwd_btn = QAction("▶", self)
        fwd_btn.triggered.connect(self.web.forward)
        nav.addAction(fwd_btn)

        # Refresh button
        refresh_btn = QToolButton()
        refresh_btn.setText("⟳ Refresh")
        refresh_btn.clicked.connect(self.web.reload)
        nav.addWidget(refresh_btn)

        # Home
        home_btn = QAction("🏠", self)
        home_btn.triggered.connect(lambda: self.web.setUrl(QUrl(self.HOME_URL)))
        nav.addAction(home_btn)

        nav.addSeparator()

        # URL bar
        self.urlbar = QLineEdit()
        self.urlbar.setClearButtonEnabled(True)
        self.urlbar.returnPressed.connect(self._navigate_to_url)
        self.urlbar.setPlaceholderText("Search or enter URL...")
        url_widget = QWidget()
        url_layout = QHBoxLayout()
        url_layout.setContentsMargins(0,0,0,0)
        url_layout.addWidget(self.urlbar)
        url_widget.setLayout(url_layout)
        url_widget.setMinimumWidth(600)
        nav.addWidget(url_widget)

        # Go button
        go_btn = QToolButton()
        go_btn.setText("Go")
        go_btn.clicked.connect(self._navigate_to_url)
        nav.addWidget(go_btn)

        nav.addSeparator()

        # Status + Progress
        self.status_label = QLabel("Private Mode")
        self.status_label.setContentsMargins(8,0,8,0)
        nav.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setMaximumHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(160)
        nav.addWidget(self.progress)

        # Connections
        self.web.urlChanged.connect(self._update_urlbar)
        self.web.loadProgress.connect(self._set_progress)
        self.web.loadFinished.connect(self._load_finished)
        self.web.titleChanged.connect(self._update_title)

    # ---------------------------
    # Dark Theme
    # ---------------------------
    def _apply_dark_theme(self):
        dark_stylesheet = """
        QMainWindow, QWidget, QToolBar { background-color: #0b0c0e; color: #ffffff; border: none; }
        QLineEdit { background-color: #1c1e23; color: #ffffff; border: 1px solid #2a2c33; padding: 6px; border-radius: 8px; selection-background-color: #00d4ff; }
        QToolButton, QPushButton, QToolBar QToolButton { background-color: #16171b; color: #00d4ff; border: 1px solid #2a2c33; padding: 6px 10px; border-radius: 8px; min-height: 30px; }
        QToolButton:hover, QPushButton:hover { background-color: #1f2127; }
        QLabel { color: #9bb7d1; }
        QProgressBar { background-color: #0b0c0e; border: 1px solid #2a2c33; border-radius: 3px; }
        QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d4ff, stop:1 #6effc9); border-radius: 3px; }
        """
        self.setStyleSheet(dark_stylesheet)
        self.web.setStyleSheet("background-color: #070708;")

    # ---------------------------
    # Navigation
    # ---------------------------
    def _navigate_to_url(self):
        raw = self.urlbar.text().strip()
        if not raw:
            return
        if " " in raw or "." not in raw:
            # Search
            self.web.setUrl(QUrl(f"https://duckduckgo.com/?q={QtCore.QUrl.toPercentEncoding(raw).data().decode('latin1')}"))
            return
        url = QUrl.fromUserInput(raw)
        if url.scheme() == "":
            url.setScheme("http")
        self.web.setUrl(url)

    # ---------------------------
    # Update UI
    # ---------------------------
    def _update_urlbar(self, q):
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def _set_progress(self, p):
        self.progress.setValue(p)
        self.status_label.setText(f"Loading... {p}%")

    def _load_finished(self, ok):
        if ok:
            self.status_label.setText("Done (Private)")
        else:
            self.status_label.setText("Load failed")
        QtCore.QTimer.singleShot(1000, lambda: self.status_label.setText("Private Mode"))

    def _update_title(self, title):
        self.setWindowTitle(f"{title} — 176 (Private)")

# ---------------------------
# Run App
# ---------------------------
def main():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    win = Browser176()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
