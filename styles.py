"""
Modern Dark Theme stylesheet for the Video Downloader & VLC Streamer App.
"""

DARK_THEME = """
QWidget {
    background-color: #12141a;
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #0f1117;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #1a1e29;
    width: 10px;
    margin: 0px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #334155;
    min-height: 25px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: #1a1e29;
    height: 10px;
    margin: 0px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #334155;
    min-width: 25px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #475569;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Cards & Frames */
QFrame.CardFrame {
    background-color: #1a1e29;
    border: 1px solid #2a3346;
    border-radius: 12px;
}

QFrame.HeaderFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e293b, stop:1 #0f172a);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 12px;
}

/* Headings */
QLabel#TitleLabel {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.5px;
}

QLabel#SubtitleLabel {
    font-size: 12px;
    color: #94a3b8;
}

QLabel#SectionHeader {
    font-size: 15px;
    font-weight: 600;
    color: #f1f5f9;
}

/* Input Fields */
QLineEdit {
    background-color: #0f121a;
    border: 1.5px solid #2e384d;
    border-radius: 8px;
    padding: 10px 14px;
    color: #f8fafc;
    font-size: 13px;
    selection-background-color: #3b82f6;
}
QLineEdit:focus {
    border: 1.5px solid #3b82f6;
    background-color: #131826;
}
QLineEdit:placeholder {
    color: #64748b;
}

/* Buttons */
QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #1d4ed8;
}
QPushButton:pressed {
    background-color: #1e40af;
}
QPushButton:disabled {
    background-color: #1e293b;
    color: #64748b;
}

QPushButton.SecondaryButton {
    background-color: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
}
QPushButton.SecondaryButton:hover {
    background-color: #334155;
    color: #ffffff;
}
QPushButton.SecondaryButton:pressed {
    background-color: #0f172a;
}

QPushButton.BufferButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    padding: 11px 22px;
    border-radius: 8px;
}
QPushButton.BufferButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #7c3aed);
}
QPushButton.BufferButton:pressed {
    background: #5b21b6;
}

QPushButton.StreamButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ea580c, stop:1 #f97316);
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    padding: 11px 22px;
    border-radius: 8px;
}
QPushButton.StreamButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c2410c, stop:1 #ea580c);
}
QPushButton.StreamButton:pressed {
    background: #9a3412;
}

QPushButton.DownloadButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    padding: 11px 22px;
    border-radius: 8px;
}
QPushButton.DownloadButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #047857, stop:1 #059669);
}
QPushButton.DownloadButton:pressed {
    background: #065f46;
}

QPushButton.CancelButton {
    background-color: #dc2626;
    color: white;
}
QPushButton.CancelButton:hover {
    background-color: #b91c1c;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #2a3346;
    background: #151821;
    border-radius: 10px;
    top: -1px;
}
QTabBar::tab {
    background: #1e2433;
    color: #94a3b8;
    padding: 9px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 4px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #151821;
    color: #38bdf8;
    border: 1px solid #2a3346;
    border-bottom: 1px solid #151821;
}
QTabBar::tab:hover:!selected {
    background: #273043;
    color: #cbd5e1;
}

/* Table Widget */
QTableWidget {
    background-color: #12151e;
    border: 1px solid #262f40;
    border-radius: 8px;
    gridline-color: #1e2638;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}
QTableWidget::item {
    padding: 7px;
    border-bottom: 1px solid #1c2230;
}
QTableWidget::item:selected {
    background-color: #1d4ed8;
}
QHeaderView::section {
    background-color: #1a202c;
    color: #94a3b8;
    font-weight: 600;
    font-size: 12px;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #2d3748;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #2a3346;
    background-color: #0f121a;
    border-radius: 8px;
    height: 18px;
    text-align: center;
    color: #ffffff;
    font-weight: 600;
    font-size: 11px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #38bdf8);
    border-radius: 7px;
}

/* Combo Box */
QComboBox {
    background-color: #1a202c;
    border: 1.5px solid #2e384d;
    border-radius: 8px;
    padding: 7px 12px;
    color: #f8fafc;
    min-width: 140px;
}
QComboBox:hover {
    border: 1.5px solid #3b82f6;
}
QComboBox::drop-down {
    border: none;
    width: 25px;
}
QComboBox QAbstractItemView {
    background-color: #1e2433;
    border: 1px solid #2e384d;
    selection-background-color: #2563eb;
    selection-color: white;
    padding: 4px;
}

/* Badges / Status */
QLabel.Badge {
    background-color: #1e293b;
    color: #38bdf8;
    border: 1px solid #38bdf8;
    border-radius: 10px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: bold;
}

QLabel.QualityBadge {
    background-color: #0f291e;
    color: #34d399;
    border: 1px solid #059669;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}

QLabel.AudioBadge {
    background-color: #2a163b;
    color: #c084fc;
    border: 1px solid #9333ea;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
}
"""
