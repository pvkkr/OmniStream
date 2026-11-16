"""
VLC Player integration for streaming online media with timeline seeking.
"""

import os
import shutil
import subprocess
import winreg
from typing import Optional, Tuple, List


class VLCController:
    """Manages VLC discovery and launching with robust timeline seeking parameters."""

    STANDARD_PATHS = [
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\VideoLAN\VLC\vlc.exe"),
    ]

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    def __init__(self, custom_path: Optional[str] = None):
        self._custom_path = custom_path
        self._detected_path: Optional[str] = None
        self.detect_vlc()

    def set_custom_path(self, path: str):
        if path and os.path.exists(path):
            self._custom_path = path
        else:
            self._custom_path = None

    def detect_vlc(self) -> Optional[str]:
        """Detect the VLC executable on the machine."""
        if self._custom_path and os.path.isfile(self._custom_path):
            self._detected_path = self._custom_path
            return self._detected_path

        for path in self.STANDARD_PATHS:
            if os.path.isfile(path):
                self._detected_path = path
                return path

        which_path = shutil.which("vlc")
        if which_path and os.path.isfile(which_path):
            self._detected_path = which_path
            return which_path

        for root_key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for sub_key in (
                r"SOFTWARE\VideoLAN\VLC",
                r"SOFTWARE\WOW6432Node\VideoLAN\VLC",
            ):
                try:
                    with winreg.OpenKey(root_key, sub_key) as key:
                        val, _ = winreg.QueryValueEx(key, "InstallDir")
                        exe_candidate = os.path.join(val, "vlc.exe")
                        if os.path.isfile(exe_candidate):
                            self._detected_path = exe_candidate
                            return exe_candidate
                except Exception:
                    pass

        self._detected_path = None
        return None

    @property
    def is_available(self) -> bool:
        return self._detected_path is not None and os.path.isfile(self._detected_path)

    @property
    def executable_path(self) -> Optional[str]:
        return self._detected_path

    def launch_stream(
        self,
        video_url: str,
        audio_url: Optional[str] = None,
        title: Optional[str] = None,
        caching_ms: int = 5000,
    ) -> Tuple[bool, str]:
        """
        Launches VLC configured to prevent stream resets when seeking forward or backward.
        Uses HTTP reconnection, standard browser user agent, and high network buffering.
        """
        if not self.is_available:
            return False, "VLC player executable was not found. Please install VLC or specify its path."

        args: List[str] = [self._detected_path]

        # Primary media URL
        args.append(video_url)

        # Only pass --input-slave if explicitly requested and different from primary
        if audio_url and audio_url != video_url:
            args.append(f"--input-slave={audio_url}")

        # Essential flags to prevent VLC from resetting to 0:00 when seeking:
        # 1. Force auto-reconnect on Range seek requests instead of aborting to byte 0
        args.append("--http-reconnect")
        args.append("--http-continuous")

        # 2. Browser User-Agent so CDNs (YouTube, Vimeo, etc.) do not reject HTTP Range seeks with 403
        args.append(f"--http-user-agent={self.USER_AGENT}")

        # 3. Buffer sizing for smooth scrubbing
        args.append(f"--network-caching={caching_ms}")
        args.append(f"--live-caching={caching_ms}")
        args.append("--file-caching=2000")

        # 4. Disable fast seek dropouts that trigger restarts
        args.append("--no-input-fast-seek")

        # 5. Adaptive bitrate and clock settings
        args.append("--adaptive-logic=predictive")
        args.append("--clock-jitter=500")

        # Set title in VLC
        if title:
            clean_title = "".join(c for c in title if c.isalnum() or c in " ._- ()[]")
            args.append(f"--meta-title={clean_title}")

        try:
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008
            flags = CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS

            subprocess.Popen(
                args,
                creationflags=flags,
                close_fds=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True, "Streaming started in VLC player."
        except Exception as e:
            return False, f"Failed to launch VLC: {e}"

    def play_local_file(self, file_path: str, title: Optional[str] = None) -> Tuple[bool, str]:
        """Open a locally downloaded/buffered file in VLC with full seek capabilities."""
        if not self.is_available:
            return False, "VLC is not installed or not found."

        if not os.path.isfile(file_path):
            return False, f"File does not exist: {file_path}"

        args = [self._detected_path, file_path, "--file-caching=1000"]
        if title:
            clean_title = "".join(c for c in title if c.isalnum() or c in " ._- ()[]")
            args.append(f"--meta-title={clean_title}")

        try:
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            subprocess.Popen(
                args,
                creationflags=CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
            )
            return True, "Opened in VLC"
        except Exception as e:
            return False, f"Error launching VLC: {e}"

    @staticmethod
    def get_timeline_shortcuts_help() -> List[Tuple[str, str]]:
        return [
            ("Shift + Left / Right Arrow", "Jump 3 seconds Backward / Forward (Fine seek)"),
            ("Alt + Left / Right Arrow", "Jump 10 seconds Backward / Forward (Standard seek)"),
            ("Ctrl + Left / Right Arrow", "Jump 1 minute Backward / Forward (Medium seek)"),
            ("Ctrl + Alt + Left / Right Arrow", "Jump 5 minutes Backward / Forward (Long seek)"),
            ("Timeline Scrubbing", "Click or drag the seekbar slider at the bottom of VLC"),
            ("Ctrl + T", "Go to a specific time (hh:mm:ss)"),
            ("Spacebar", "Pause / Resume playback"),
            ("Ctrl + Up / Down Arrow", "Volume Up / Down"),
            ("F or Double-Click", "Toggle Fullscreen mode"),
        ]
