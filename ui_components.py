"""
UI Components: Thumbnail loader, Format selection cards, and VLC Navigation shortcuts guide.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QScrollArea, QFrame, QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import requests


class ImageLoaderWorker(QThread):
    """Fetches image bytes in background."""
    image_loaded = pyqtSignal(bytes)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            resp = requests.get(self.url, timeout=6)
            if resp.status_code == 200:
                self.image_loaded.emit(resp.content)
        except Exception:
            pass


class ThumbnailWidget(QLabel):
    """Thumbnail display with rounded corners and asynchronous loading."""

    def __init__(self, width: int = 260, height: int = 150):
        super().__init__()
        self._target_w = width
        self._target_h = height
        self.setFixedSize(width, height)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            background-color: #1a1e29;
            border: 1px solid #2d3748;
            border-radius: 10px;
            color: #64748b;
            font-size: 11px;
        """)
        self.setText("No Preview")
        self._worker = None

    def load_from_url(self, url: str):
        if not url:
            self.setText("No Preview")
            return
        self.setText("Loading Preview...")
        self._worker = ImageLoaderWorker(url)
        self._worker.image_loaded.connect(self._on_image_bytes)
        self._worker.start()

    def _on_image_bytes(self, data: bytes):
        image = QImage.fromData(data)
        if image.isNull():
            self.setText("Preview Failed")
            return

        pixmap = QPixmap.fromImage(image).scaled(
            self._target_w, self._target_h,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        rounded = QPixmap(self._target_w, self._target_h)
        rounded.fill(Qt.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self._target_w, self._target_h, 10, 10)
        painter.setClipPath(path)

        x = (self._target_w - pixmap.width()) // 2
        y = (self._target_h - pixmap.height()) // 2
        painter.drawPixmap(x, y, pixmap)
        painter.end()

        self.setPixmap(rounded)


class VLCShortcutsDialog(QDialog):
    """Dialog explaining VLC timeline navigation and seeking hotkeys."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("VLC Player Timeline & Seeking Guide")
        self.setFixedWidth(540)
        self.setStyleSheet("""
            QDialog {
                background-color: #12141a;
                color: #e2e8f0;
            }
            QLabel {
                color: #e2e8f0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎬 VLC Timeline Seeking & Playback Controls")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        desc = QLabel(
            "<b>Two Streaming Modes:</b><br>"
            "• <b>⚡ Buffer & Seek (Recommended)</b>: Buffers the stream locally in seconds. Scrubbing, jumping back, "
            "or jumping forward works 100% instantly without ever resetting to the start!<br>"
            "• <b>▶️ Direct Stream</b>: Streams over the web with HTTP auto-reconnect and 5-second buffer."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.4;")
        layout.addWidget(desc)

        # Shortcuts Table Frame
        frame = QFrame()
        frame.setStyleSheet("""
            background-color: #1a1e29;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 10px;
        """)
        f_layout = QVBoxLayout(frame)
        f_layout.setSpacing(8)

        shortcuts = [
            ("Shift + Left Arrow", "⏪ Jump 3 seconds BACK (Very fine seek)"),
            ("Shift + Right Arrow", "⏩ Jump 3 seconds FORWARD"),
            ("Alt + Left Arrow", "⏪ Jump 10 seconds BACK (Standard seek)"),
            ("Alt + Right Arrow", "⏩ Jump 10 seconds FORWARD"),
            ("Ctrl + Left Arrow", "⏪ Jump 1 minute BACK"),
            ("Ctrl + Right Arrow", "⏩ Jump 1 minute FORWARD"),
            ("Ctrl + Alt + Left/Right", "⏪ / ⏩ Jump 5 minutes back/forward"),
            ("Mouse Scrubbing", "🖱️ Click or drag anywhere along VLC's bottom timeline bar"),
            ("Spacebar", "⏸️ Play / Pause toggle"),
            ("Ctrl + T", "⏱️ Jump to exact time (hh:mm:ss)"),
            ("Ctrl + Up / Down Arrow", "🔊 Volume Increase / Decrease"),
        ]

        for keys, action in shortcuts:
            row = QHBoxLayout()
            k_lbl = QLabel(keys)
            k_lbl.setStyleSheet("""
                background-color: #262f40;
                color: #f8fafc;
                font-family: monospace;
                font-weight: bold;
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 170px;
            """)
            a_lbl = QLabel(action)
            a_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            row.addWidget(k_lbl)
            row.addWidget(a_lbl, 1)
            f_layout.addLayout(row)

        layout.addWidget(frame)

        # Bottom row with GitHub & Close
        btn_row = QHBoxLayout()

        import webbrowser
        btn_gh = QPushButton("⭐ Star on GitHub")
        btn_gh.setStyleSheet("""
            background-color: #1e293b;
            color: #38bdf8;
            border: 1px solid #0284c7;
            font-weight: bold;
            padding: 8px 14px;
            border-radius: 6px;
        """)
        btn_gh.clicked.connect(lambda: webbrowser.open("https://github.com/pvkkr/OmniStream"))
        btn_row.addWidget(btn_gh)
        btn_row.addStretch()

        btn_close = QPushButton("Got it!")
        btn_close.setStyleSheet("""
            background-color: #2563eb;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 6px;
        """)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)

        layout.addLayout(btn_row)
