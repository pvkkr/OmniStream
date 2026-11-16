"""
OmniStream & Downloader - Universal Video Downloader & VLC Player Desktop App
"""

import sys
import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QFileDialog,
    QMessageBox, QScrollArea, QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QColor

from styles import DARK_THEME
from vlc_controller import VLCController
from media_engine import FetchInfoWorker, DownloadWorker, BufferStreamWorker, format_bytes
from ui_components import ThumbnailWidget, VLCShortcutsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OmniStream - Universal Video Downloader & VLC Player")
        self.resize(1050, 780)
        self.setMinimumSize(850, 620)

        # Core engines
        self.vlc = VLCController()
        self.current_metadata: Optional[Dict[str, Any]] = None
        self.fetch_worker: Optional[FetchInfoWorker] = None
        self.download_worker: Optional[DownloadWorker] = None
        self.buffer_worker: Optional[BufferStreamWorker] = None

        # Default save path: User's Downloads folder
        self.download_dir = str(Path.home() / "Downloads")
        self.last_downloaded_file: Optional[str] = None

        self._build_ui()
        self._update_vlc_badge()

    def _build_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(14)

        # 1. Header Frame
        header_frame = QFrame()
        header_frame.setProperty("class", "HeaderFrame")
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(16, 12, 16, 12)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        app_title = QLabel("OmniStream Video Downloader & Player")
        app_title.setObjectName("TitleLabel")
        app_subtitle = QLabel("Universal Link Downloader • Quality Selector • Direct VLC Stream with Timeline Seeking")
        app_subtitle.setObjectName("SubtitleLabel")
        title_box.addWidget(app_title)
        title_box.addWidget(app_subtitle)
        h_layout.addLayout(title_box, 1)

        vlc_box = QHBoxLayout()
        vlc_box.setSpacing(10)

        self.vlc_badge = QLabel("VLC Status")
        self.vlc_badge.setStyleSheet("padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 11px;")
        vlc_box.addWidget(self.vlc_badge)

        self.btn_vlc_locate = QPushButton("Change VLC Path")
        self.btn_vlc_locate.setProperty("class", "SecondaryButton")
        self.btn_vlc_locate.setToolTip("Select custom vlc.exe path if not auto-detected")
        self.btn_vlc_locate.clicked.connect(self._on_choose_vlc_path)
        vlc_box.addWidget(self.btn_vlc_locate)

        self.btn_shortcuts = QPushButton("⌨️ VLC Seeking Guide")
        self.btn_shortcuts.setProperty("class", "SecondaryButton")
        self.btn_shortcuts.clicked.connect(self._on_show_shortcuts)
        vlc_box.addWidget(self.btn_shortcuts)

        self.btn_github = QPushButton("⭐ GitHub")
        self.btn_github.setStyleSheet("background-color: #1e293b; color: #38bdf8; border: 1.5px solid #0284c7; font-weight: bold; border-radius: 8px; padding: 7px 14px;")
        self.btn_github.setToolTip("Open official repository: https://github.com/pvkkr/OmniStream")
        self.btn_github.clicked.connect(lambda: webbrowser.open("https://github.com/pvkkr/OmniStream"))
        vlc_box.addWidget(self.btn_github)

        h_layout.addLayout(vlc_box)
        main_layout.addWidget(header_frame)

        # 2. URL Input Card
        url_frame = QFrame()
        url_frame.setProperty("class", "CardFrame")
        url_layout = QHBoxLayout(url_frame)
        url_layout.setContentsMargins(14, 12, 14, 12)
        url_layout.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste any video URL here (YouTube, Twitter/X, TikTok, Instagram, Reddit, Vimeo, Facebook, m3u8 direct links...)")
        self.url_input.returnPressed.connect(self._on_fetch_clicked)
        url_layout.addWidget(self.url_input, 1)

        btn_paste = QPushButton("📋 Paste")
        btn_paste.setProperty("class", "SecondaryButton")
        btn_paste.clicked.connect(self._on_paste_clicked)
        url_layout.addWidget(btn_paste)

        btn_clear = QPushButton("✖")
        btn_clear.setProperty("class", "SecondaryButton")
        btn_clear.setFixedWidth(36)
        btn_clear.setToolTip("Clear URL")
        btn_clear.clicked.connect(lambda: self.url_input.clear())
        url_layout.addWidget(btn_clear)

        self.btn_fetch = QPushButton("⚡ Fetch Formats")
        self.btn_fetch.clicked.connect(self._on_fetch_clicked)
        url_layout.addWidget(self.btn_fetch)

        main_layout.addWidget(url_frame)

        # 3. Middle Content Area
        self.content_splitter = QVBoxLayout()
        self.content_splitter.setSpacing(12)

        # Video Preview Header Card
        self.preview_card = QFrame()
        self.preview_card.setProperty("class", "CardFrame")
        self.preview_card.setVisible(False)
        prev_layout = QHBoxLayout(self.preview_card)
        prev_layout.setContentsMargins(14, 14, 14, 14)
        prev_layout.setSpacing(16)

        self.thumb_widget = ThumbnailWidget(220, 125)
        prev_layout.addWidget(self.thumb_widget)

        info_box = QVBoxLayout()
        info_box.setSpacing(6)

        self.lbl_video_title = QLabel("Video Title")
        self.lbl_video_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")
        self.lbl_video_title.setWordWrap(True)
        info_box.addWidget(self.lbl_video_title)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(10)
        self.lbl_uploader = QLabel("Channel")
        self.lbl_uploader.setStyleSheet("color: #38bdf8; font-weight: 600;")
        self.lbl_duration = QLabel("Duration: --:--")
        self.lbl_duration.setStyleSheet("color: #94a3b8;")
        self.lbl_views = QLabel("Views: --")
        self.lbl_views.setStyleSheet("color: #94a3b8;")
        self.lbl_platform = QLabel("Platform")
        self.lbl_platform.setStyleSheet("background-color: #334155; color: #f1f5f9; padding: 2px 8px; border-radius: 4px; font-size: 11px;")

        meta_row.addWidget(self.lbl_uploader)
        meta_row.addWidget(self.lbl_duration)
        meta_row.addWidget(self.lbl_views)
        meta_row.addWidget(self.lbl_platform)
        meta_row.addStretch()
        info_box.addLayout(meta_row)

        self.lbl_desc = QLabel("Description snippet...")
        self.lbl_desc.setStyleSheet("color: #64748b; font-size: 12px;")
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setMaximumHeight(38)
        info_box.addWidget(self.lbl_desc)

        prev_layout.addLayout(info_box, 1)

        quick_actions = QVBoxLayout()
        quick_actions.setSpacing(8)

        self.btn_buffer_stream = QPushButton("⚡ Seekable Stream in VLC")
        self.btn_buffer_stream.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6); color: white; font-weight: bold; padding: 10px 18px; border-radius: 8px;")
        self.btn_buffer_stream.setToolTip("Buffers stream in background so timeline forward/backward seeking never resets to 0:00")
        self.btn_buffer_stream.clicked.connect(self._on_buffer_stream)
        quick_actions.addWidget(self.btn_buffer_stream)

        self.btn_quick_stream = QPushButton("▶️ Direct Stream")
        self.btn_quick_stream.setProperty("class", "StreamButton")
        self.btn_quick_stream.setToolTip("Launches directly over the network with HTTP reconnect")
        self.btn_quick_stream.clicked.connect(self._on_quick_stream)
        quick_actions.addWidget(self.btn_quick_stream)

        self.btn_quick_download = QPushButton("⬇️ Quick Download")
        self.btn_quick_download.setProperty("class", "DownloadButton")
        self.btn_quick_download.clicked.connect(self._on_quick_download)
        quick_actions.addWidget(self.btn_quick_download)

        prev_layout.addLayout(quick_actions)
        self.content_splitter.addWidget(self.preview_card)

        # Format Tabs
        self.tabs = QTabWidget()
        self.tabs.setVisible(False)

        # Tab 1: Video + Audio Presets
        self.tab_video = QWidget()
        self.tab_video_layout = QVBoxLayout(self.tab_video)
        self.tab_video_layout.setContentsMargins(12, 12, 12, 12)
        self.scroll_video = QScrollArea()
        self.scroll_video.setWidgetResizable(True)
        self.scroll_video.setStyleSheet("border: none; background: transparent;")
        self.container_video = QWidget()
        self.layout_video_cards = QVBoxLayout(self.container_video)
        self.layout_video_cards.setSpacing(8)
        self.scroll_video.setWidget(self.container_video)
        self.tab_video_layout.addWidget(self.scroll_video)
        self.tabs.addTab(self.tab_video, "🎬 Video Quality Options (Video + Audio)")

        # Tab 2: Audio Only Presets
        self.tab_audio = QWidget()
        self.tab_audio_layout = QVBoxLayout(self.tab_audio)
        self.tab_audio_layout.setContentsMargins(12, 12, 12, 12)
        self.scroll_audio = QScrollArea()
        self.scroll_audio.setWidgetResizable(True)
        self.scroll_audio.setStyleSheet("border: none; background: transparent;")
        self.container_audio = QWidget()
        self.layout_audio_cards = QVBoxLayout(self.container_audio)
        self.layout_audio_cards.setSpacing(8)
        self.scroll_audio.setWidget(self.container_audio)
        self.tab_audio_layout.addWidget(self.scroll_audio)
        self.tabs.addTab(self.tab_audio, "🎵 Audio Formats (MP3 / M4A / AAC)")

        # Tab 3: Advanced Formats Table
        self.tab_raw = QWidget()
        self.tab_raw_layout = QVBoxLayout(self.tab_raw)
        self.tab_raw_layout.setContentsMargins(10, 10, 10, 10)
        self.raw_table = QTableWidget()
        self.raw_table.setColumnCount(8)
        self.raw_table.setHorizontalHeaderLabels([
            "Format ID", "Type", "Resolution / Rate", "Ext", "V-Codec", "A-Codec", "Size", "Actions"
        ])
        self.raw_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.raw_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.raw_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.raw_table.verticalHeader().setVisible(False)
        self.raw_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tab_raw_layout.addWidget(self.raw_table)
        self.tabs.addTab(self.tab_raw, "📊 Advanced Formats (All Streams)")

        self.content_splitter.addWidget(self.tabs, 1)
        main_layout.addLayout(self.content_splitter, 1)

        # 4. Download Controls & Progress Section
        self.progress_frame = QFrame()
        self.progress_frame.setProperty("class", "CardFrame")
        p_layout = QVBoxLayout(self.progress_frame)
        p_layout.setContentsMargins(14, 12, 14, 12)
        p_layout.setSpacing(8)

        dir_row = QHBoxLayout()
        dir_row.setSpacing(10)
        lbl_dir = QLabel("Save to:")
        lbl_dir.setStyleSheet("color: #94a3b8; font-weight: 600;")
        dir_row.addWidget(lbl_dir)

        self.lbl_save_dir = QLabel(self.download_dir)
        self.lbl_save_dir.setStyleSheet("color: #f1f5f9; background: #0f121a; padding: 4px 10px; border-radius: 6px; border: 1px solid #2d3748;")
        dir_row.addWidget(self.lbl_save_dir, 1)

        btn_browse_dir = QPushButton("Browse Folder...")
        btn_browse_dir.setProperty("class", "SecondaryButton")
        btn_browse_dir.clicked.connect(self._on_choose_download_dir)
        dir_row.addWidget(btn_browse_dir)

        p_layout.addLayout(dir_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        p_layout.addWidget(self.progress_bar)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        self.lbl_status = QLabel("Ready. Enter a link above to begin.")
        self.lbl_status.setStyleSheet("color: #38bdf8; font-weight: 600;")
        stats_row.addWidget(self.lbl_status, 1)

        self.lbl_speed = QLabel("Speed: --")
        self.lbl_speed.setStyleSheet("color: #94a3b8;")
        stats_row.addWidget(self.lbl_speed)

        self.lbl_eta = QLabel("ETA: --")
        self.lbl_eta.setStyleSheet("color: #94a3b8;")
        stats_row.addWidget(self.lbl_eta)

        self.lbl_size = QLabel("Size: --")
        self.lbl_size.setStyleSheet("color: #94a3b8;")
        stats_row.addWidget(self.lbl_size)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setProperty("class", "CancelButton")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self._on_cancel_download)
        stats_row.addWidget(self.btn_cancel)

        self.btn_play_downloaded = QPushButton("▶️ Play in VLC")
        self.btn_play_downloaded.setProperty("class", "StreamButton")
        self.btn_play_downloaded.setVisible(False)
        self.btn_play_downloaded.clicked.connect(self._on_play_downloaded)
        stats_row.addWidget(self.btn_play_downloaded)

        self.btn_open_folder = QPushButton("📂 Open Folder")
        self.btn_open_folder.setProperty("class", "SecondaryButton")
        self.btn_open_folder.setVisible(False)
        self.btn_open_folder.clicked.connect(self._on_open_folder)
        stats_row.addWidget(self.btn_open_folder)

        p_layout.addLayout(stats_row)
        main_layout.addWidget(self.progress_frame)

        tip_label = QLabel(
            "💡 <b>Tip for VLC Streaming:</b> In VLC, use <b>Shift + Left/Right</b> (3s seek), "
            "<b>Alt + Left/Right</b> (10s seek), or mouse timeline scrubbing to jump backwards & forwards seamlessly! "
            "&bull; <a href=\"https://github.com/pvkkr/OmniStream\" style=\"color: #38bdf8; font-weight: bold; text-decoration: underline;\">GitHub: pvkkr/OmniStream</a>"
        )
        tip_label.setOpenExternalLinks(True)
        tip_label.setStyleSheet("color: #64748b; font-size: 11px; padding: 2px 4px;")
        main_layout.addWidget(tip_label)

    def _update_vlc_badge(self):
        if self.vlc.is_available:
            self.vlc_badge.setText("✅ VLC Player Connected")
            self.vlc_badge.setStyleSheet("background-color: #064e3b; color: #34d399; border: 1px solid #059669; border-radius: 6px; padding: 4px 10px; font-weight: bold;")
        else:
            self.vlc_badge.setText("⚠️ VLC Not Found")
            self.vlc_badge.setStyleSheet("background-color: #451a03; color: #fbbf24; border: 1px solid #d97706; border-radius: 6px; padding: 4px 10px; font-weight: bold;")

    def _on_paste_clicked(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.url_input.setText(text)
            self._on_fetch_clicked()

    def _on_choose_vlc_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Locate vlc.exe", "C:\\Program Files", "VLC Executable (vlc.exe);;All Files (*.*)"
        )
        if file_path:
            self.vlc.set_custom_path(file_path)
            self._update_vlc_badge()
            if self.vlc.is_available:
                QMessageBox.information(self, "VLC Configured", f"VLC successfully connected:\n{file_path}")

    def _on_choose_download_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.download_dir)
        if folder:
            self.download_dir = folder
            self.lbl_save_dir.setText(folder)

    def _on_show_shortcuts(self):
        dlg = VLCShortcutsDialog(self)
        dlg.exec_()

    def _on_fetch_clicked(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Missing URL", "Please enter or paste a valid video URL.")
            return

        self.btn_fetch.setEnabled(False)
        self.btn_fetch.setText("Fetching...")
        self.lbl_status.setText(f"Analyzing video streams from {url[:45]}...")
        self.progress_bar.setValue(0)

        self.fetch_worker = FetchInfoWorker(url)
        self.fetch_worker.finished.connect(self._on_fetch_success)
        self.fetch_worker.error.connect(self._on_fetch_error)
        self.fetch_worker.start()

    def _on_fetch_success(self, metadata: Dict[str, Any]):
        self.btn_fetch.setEnabled(True)
        self.btn_fetch.setText("⚡ Fetch Formats")
        self.current_metadata = metadata

        self.preview_card.setVisible(True)
        self.lbl_video_title.setText(metadata.get("title", "Unknown Title"))
        self.lbl_uploader.setText(f"👤 {metadata.get('uploader', 'Unknown')}")
        self.lbl_duration.setText(f"⏱️ {metadata.get('duration_str', '--:--')}")
        views = metadata.get("views")
        self.lbl_views.setText(f"👁️ {views:,} views" if views else "👁️ Live / Web")
        self.lbl_platform.setText(metadata.get("extractor", "Video").upper())
        self.lbl_desc.setText(metadata.get("description", ""))

        thumb_url = metadata.get("thumbnail")
        if thumb_url:
            self.thumb_widget.load_from_url(thumb_url)

        self.tabs.setVisible(True)
        self._populate_video_tab(metadata.get("video_presets", []))
        self._populate_audio_tab(metadata.get("audio_presets", []))
        self._populate_raw_table(metadata.get("raw_formats", []))

        self.lbl_status.setText("Formats loaded! Ready to stream in VLC or download.")

    def _on_fetch_error(self, err_msg: str):
        self.btn_fetch.setEnabled(True)
        self.btn_fetch.setText("⚡ Fetch Formats")
        self.lbl_status.setText("Failed to retrieve formats.")
        QMessageBox.critical(
            self,
            "Fetch Error",
            f"Could not load media from this link.\n\nError details:\n{err_msg[:400]}"
        )

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _populate_video_tab(self, presets: list):
        self._clear_layout(self.layout_video_cards)

        if not presets:
            no_lbl = QLabel("No discrete video presets found. Check 'All Available Formats' tab.")
            no_lbl.setStyleSheet("color: #94a3b8; font-style: italic;")
            self.layout_video_cards.addWidget(no_lbl)
            return

        for p in presets:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1a1e29;
                    border: 1px solid #2d3748;
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame:hover {
                    border: 1px solid #3b82f6;
                    background-color: #1f2533;
                }
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(12, 10, 12, 10)
            c_layout.setSpacing(14)

            badge = QLabel(p["label"])
            badge.setStyleSheet("""
                background-color: #0f291e;
                color: #34d399;
                border: 1px solid #059669;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px 12px;
                min-width: 140px;
            """)
            c_layout.addWidget(badge)

            fps_str = f"{p.get('fps')} fps" if p.get("fps") else ""
            details_lbl = QLabel(f"Codec: {p.get('codec', 'Auto')} • Res: {p.get('resolution')} {fps_str} • Est. Size: {p.get('filesize_str')}")
            details_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            c_layout.addWidget(details_lbl, 1)

            # Buffer & Seek (Guaranteed timeline seeking without resets)
            btn_buf = QPushButton("⚡ Buffer & Seek")
            btn_buf.setStyleSheet("background-color: #6d28d9; color: white; font-weight: bold; padding: 8px 12px; border-radius: 6px;")
            btn_buf.setToolTip("Buffers stream in background: Forward & Backward seeking works 100% without restarting!")
            btn_buf.clicked.connect(lambda _, item=p: self._buffer_and_stream(item))
            c_layout.addWidget(btn_buf)

            # Direct Stream
            btn_stream = QPushButton("▶️ Direct Stream")
            btn_stream.setProperty("class", "StreamButton")
            btn_stream.setToolTip("Direct network stream with HTTP auto-reconnect")
            btn_stream.clicked.connect(lambda _, item=p: self._stream_preset(item))
            c_layout.addWidget(btn_stream)

            # Download
            btn_dl = QPushButton("⬇️ Download")
            btn_dl.setProperty("class", "DownloadButton")
            btn_dl.clicked.connect(lambda _, item=p: self._download_preset(item))
            c_layout.addWidget(btn_dl)

            self.layout_video_cards.addWidget(card)

        self.layout_video_cards.addStretch()

    def _populate_audio_tab(self, presets: list):
        self._clear_layout(self.layout_audio_cards)

        if not presets:
            no_lbl = QLabel("No standalone audio presets found.")
            no_lbl.setStyleSheet("color: #94a3b8; font-style: italic;")
            self.layout_audio_cards.addWidget(no_lbl)
            return

        for p in presets:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #1a1e29;
                    border: 1px solid #2d3748;
                    border-radius: 8px;
                    padding: 8px;
                }
                QFrame:hover {
                    border: 1px solid #a855f7;
                    background-color: #211c2e;
                }
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(12, 10, 12, 10)
            c_layout.setSpacing(14)

            badge = QLabel(p["label"])
            badge.setStyleSheet("""
                background-color: #2a163b;
                color: #c084fc;
                border: 1px solid #9333ea;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
                min-width: 170px;
            """)
            c_layout.addWidget(badge)

            details_lbl = QLabel(f"Codec: {p.get('codec', 'Audio')} • Format: {p.get('ext', 'mp3').upper()} • Size: {p.get('filesize_str')}")
            details_lbl.setStyleSheet("color: #cbd5e1; font-size: 12px;")
            c_layout.addWidget(details_lbl, 1)

            btn_stream = QPushButton("▶️ Play Audio in VLC")
            btn_stream.setProperty("class", "StreamButton")
            btn_stream.clicked.connect(lambda _, item=p: self._stream_audio(item))
            c_layout.addWidget(btn_stream)

            btn_dl = QPushButton("⬇️ Download MP3")
            btn_dl.setProperty("class", "DownloadButton")
            btn_dl.clicked.connect(lambda _, item=p: self._download_audio(item))
            c_layout.addWidget(btn_dl)

            self.layout_audio_cards.addWidget(card)

        self.layout_audio_cards.addStretch()

    def _populate_raw_table(self, raw_list: list):
        self.raw_table.setRowCount(0)
        self.raw_table.setRowCount(len(raw_list))

        for row, r in enumerate(raw_list):
            fid_item = QTableWidgetItem(str(r["format_id"]))
            fid_item.setTextAlignment(Qt.AlignCenter)
            self.raw_table.setItem(row, 0, fid_item)

            stream_type = "Video+Audio" if (r["has_video"] and r["has_audio"]) else ("Video Only" if r["has_video"] else "Audio Only")
            type_item = QTableWidgetItem(stream_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.raw_table.setItem(row, 1, type_item)

            res_item = QTableWidgetItem(str(r["resolution"]))
            res_item.setTextAlignment(Qt.AlignCenter)
            self.raw_table.setItem(row, 2, res_item)

            ext_item = QTableWidgetItem(str(r["ext"]))
            ext_item.setTextAlignment(Qt.AlignCenter)
            self.raw_table.setItem(row, 3, ext_item)

            self.raw_table.setItem(row, 4, QTableWidgetItem(str(r["vcodec"])))
            self.raw_table.setItem(row, 5, QTableWidgetItem(str(r["acodec"])))

            size_item = QTableWidgetItem(r["filesize_str"])
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.raw_table.setItem(row, 6, size_item)

            btn_box = QWidget()
            b_layout = QHBoxLayout(btn_box)
            b_layout.setContentsMargins(4, 2, 4, 2)
            b_layout.setSpacing(6)

            btn_s = QPushButton("▶️ VLC")
            btn_s.setStyleSheet("padding: 4px 10px; font-size: 11px; background-color: #ea580c; border-radius: 4px; font-weight: bold;")
            btn_s.clicked.connect(lambda _, item=r: self._stream_raw(item))
            b_layout.addWidget(btn_s)

            btn_d = QPushButton("⬇️ Save")
            btn_d.setStyleSheet("padding: 4px 10px; font-size: 11px; background-color: #059669; border-radius: 4px; font-weight: bold;")
            btn_d.clicked.connect(lambda _, item=r: self._download_raw(item))
            b_layout.addWidget(btn_d)

            self.raw_table.setCellWidget(row, 7, btn_box)

    # Streaming Handlers
    def _stream_preset(self, preset: dict):
        if not self.vlc.is_available:
            self._warn_vlc_missing()
            return

        title = self.current_metadata.get("title") if self.current_metadata else "Stream"
        video_url = preset.get("stream_video_url")
        audio_url = preset.get("stream_audio_url")

        if not video_url:
            QMessageBox.warning(self, "Stream Error", "Stream URL could not be resolved.")
            return

        success, msg = self.vlc.launch_stream(
            video_url=video_url,
            audio_url=audio_url,
            title=title,
            caching_ms=5000
        )
        if success:
            self.lbl_status.setText(f"🚀 Streaming '{preset['label']}' in VLC with timeline seeking!")
        else:
            QMessageBox.critical(self, "Launch Error", msg)

    def _stream_audio(self, preset: dict):
        if not self.vlc.is_available:
            self._warn_vlc_missing()
            return

        title = self.current_metadata.get("title") if self.current_metadata else "Audio Stream"
        url = preset.get("stream_url")
        if not url:
            QMessageBox.warning(self, "Stream Error", "Audio URL is not directly available.")
            return

        success, msg = self.vlc.launch_stream(
            video_url=url,
            title=f"[Audio] {title}",
            caching_ms=5000
        )
        if success:
            self.lbl_status.setText("🎵 Streaming audio in VLC player.")
        else:
            QMessageBox.critical(self, "Launch Error", msg)

    def _stream_raw(self, raw_item: dict):
        if not self.vlc.is_available:
            self._warn_vlc_missing()
            return

        url = raw_item.get("url")
        if not url:
            QMessageBox.warning(self, "Stream Error", "No direct streaming URL for this raw format.")
            return

        title = self.current_metadata.get("title") if self.current_metadata else "Stream"
        audio_url = None
        if raw_item["has_video"] and not raw_item["has_audio"]:
            best_a = self.current_metadata.get("best_audio")
            if best_a:
                audio_url = best_a.get("url")

        success, msg = self.vlc.launch_stream(
            video_url=url,
            audio_url=audio_url,
            title=title,
            caching_ms=5000
        )
        if success:
            self.lbl_status.setText(f"▶️ Streaming format {raw_item['format_id']} in VLC.")
        else:
            QMessageBox.critical(self, "Launch Error", msg)

    def _on_quick_stream(self):
        if not self.current_metadata:
            return
        presets = self.current_metadata.get("video_presets", [])
        if presets:
            self._stream_preset(presets[0])
        else:
            raw = self.current_metadata.get("raw_formats", [])
            if raw:
                self._stream_raw(raw[0])

    def _on_buffer_stream(self):
        if not self.current_metadata:
            return
        presets = self.current_metadata.get("video_presets", [])
        if presets:
            self._buffer_and_stream(presets[0])

    def _buffer_and_stream(self, preset: dict):
        if not self.current_metadata:
            return
        if not self.vlc.is_available:
            self._warn_vlc_missing()
            return

        spec = preset.get("download_format_spec", "best")
        title = self.current_metadata.get("title", "Stream")
        url = self.current_metadata["url"]

        self.btn_cancel.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(f"⚡ Buffering '{preset['label']}' for seekable VLC playback...")

        self.buffer_worker = BufferStreamWorker(url=url, format_spec=spec, title=title)
        self.buffer_worker.progress.connect(self._on_buffer_progress)
        self.buffer_worker.status.connect(lambda msg: self.lbl_status.setText(msg))
        self.buffer_worker.ready.connect(self._on_buffer_ready)
        self.buffer_worker.error.connect(self._on_buffer_error)
        self.buffer_worker.start()

    def _on_buffer_progress(self, percent: float, speed: str):
        self.progress_bar.setValue(int(percent))
        self.lbl_speed.setText(f"Speed: {speed}")
        self.lbl_status.setText(f"Buffering for VLC seeking... ({int(percent)}%)")

    def _on_buffer_ready(self, file_path: str, title: str):
        self.btn_cancel.setVisible(False)
        self.progress_bar.setValue(100)
        self.last_downloaded_file = file_path
        self.lbl_status.setText("🚀 Playing buffered stream in VLC! Seek backward & forward freely.")
        self.vlc.play_local_file(file_path, title=title)

    def _on_buffer_error(self, err: str):
        self.btn_cancel.setVisible(False)
        self.lbl_status.setText("Buffering failed.")
        QMessageBox.critical(self, "Buffering Error", f"Failed to buffer stream for VLC:\n{err[:400]}")

    # Download Handlers
    def _download_preset(self, preset: dict):
        spec = preset.get("download_format_spec")
        self._start_download(spec=spec, is_audio=False)

    def _download_audio(self, preset: dict):
        spec = preset.get("download_format_spec")
        self._start_download(spec=spec, is_audio=True, audio_ext="mp3")

    def _download_raw(self, raw_item: dict):
        fid = raw_item["format_id"]
        if raw_item["has_video"] and not raw_item["has_audio"]:
            spec = f"{fid}+bestaudio"
        else:
            spec = fid
        self._start_download(spec=spec, is_audio=not raw_item["has_video"])

    def _on_quick_download(self):
        if not self.current_metadata:
            return
        presets = self.current_metadata.get("video_presets", [])
        if presets:
            self._download_preset(presets[0])
        else:
            self._start_download(spec="bestvideo+bestaudio/best", is_audio=False)

    def _start_download(self, spec: str, is_audio: bool, audio_ext: str = "mp3"):
        if not self.current_metadata:
            return

        if self.download_worker and self.download_worker.isRunning():
            QMessageBox.warning(self, "Download In Progress", "Another download is already in progress. Please wait or cancel it.")
            return

        self.btn_cancel.setVisible(True)
        self.btn_play_downloaded.setVisible(False)
        self.btn_open_folder.setVisible(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Initializing download engine...")

        target_url = self.current_metadata["url"]
        self.download_worker = DownloadWorker(
            url=target_url,
            format_spec=spec,
            output_dir=self.download_dir,
            is_audio_only=is_audio,
            audio_ext=audio_ext
        )

        self.download_worker.progress.connect(self._on_download_progress)
        self.download_worker.status_changed.connect(self._on_download_status)
        self.download_worker.finished.connect(self._on_download_finished)
        self.download_worker.error.connect(self._on_download_error)
        self.download_worker.start()

    def _on_download_progress(self, percent: float, speed: str, eta: str, downloaded: str, total: str):
        self.progress_bar.setValue(int(percent))
        self.lbl_speed.setText(f"Speed: {speed}")
        self.lbl_eta.setText(f"ETA: {eta}")
        self.lbl_size.setText(f"{downloaded} / {total}")
        self.lbl_status.setText(f"Downloading... ({int(percent)}%)")

    def _on_download_status(self, status_msg: str):
        self.lbl_status.setText(status_msg)

    def _on_download_finished(self, output_file: str):
        self.btn_cancel.setVisible(False)
        self.last_downloaded_file = output_file
        self.progress_bar.setValue(100)
        self.lbl_status.setText("✅ Download completed successfully!")
        self.btn_play_downloaded.setVisible(True)
        self.btn_open_folder.setVisible(True)

        QMessageBox.information(
            self,
            "Download Finished",
            f"Media successfully downloaded to:\n{output_file}"
        )

    def _on_download_error(self, err: str):
        self.btn_cancel.setVisible(False)
        self.lbl_status.setText("❌ Download failed.")
        QMessageBox.critical(self, "Download Error", f"An error occurred while downloading:\n{err[:400]}")

    def _on_cancel_download(self):
        if self.download_worker and self.download_worker.isRunning():
            self.download_worker.cancel()
            self.lbl_status.setText("Cancelling download...")
            self.btn_cancel.setVisible(False)

    def _on_play_downloaded(self):
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            self.vlc.play_local_file(self.last_downloaded_file)
        else:
            QMessageBox.warning(self, "File Not Found", "Downloaded file could not be located.")

    def _on_open_folder(self):
        folder = self.download_dir
        if self.last_downloaded_file and os.path.exists(self.last_downloaded_file):
            folder = os.path.dirname(self.last_downloaded_file)
        if os.path.exists(folder):
            os.startfile(folder)

    def _warn_vlc_missing(self):
        res = QMessageBox.question(
            self,
            "VLC Not Found",
            "VLC player was not detected on this system.\nWould you like to locate vlc.exe manually?",
            QMessageBox.Yes | QMessageBox.No
        )
        if res == QMessageBox.Yes:
            self._on_choose_vlc_path()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
