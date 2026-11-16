"""
Media Engine powered by yt-dlp and ffmpeg for extracting formats, metadata, and downloading.
"""

import os
import re
import math
import urllib.parse
from typing import Dict, Any, List, Optional
from PyQt5.QtCore import QThread, pyqtSignal

import yt_dlp
import imageio_ffmpeg


def clean_url(url: str) -> str:
    """Strip playlist and tracking parameters from YouTube URLs so only the single video is fetched instantly."""
    try:
        parsed = urllib.parse.urlparse(url)
        # If youtube.com or youtu.be, isolate the single video
        if "youtube.com" in parsed.netloc:
            query = urllib.parse.parse_qs(parsed.query)
            if "v" in query:
                # Keep only the video ID
                clean_query = urllib.parse.urlencode({"v": query["v"][0]})
                return urllib.parse.urlunparse(parsed._replace(query=clean_query))
        elif "youtu.be" in parsed.netloc:
            # youtu.be/<video_id>?list=... -> youtu.be/<video_id>
            return urllib.parse.urlunparse(parsed._replace(query=""))
    except Exception:
        pass
    return url


def format_bytes(size_bytes: Optional[int]) -> str:
    """Format bytes into readable string (e.g. 14.5 MB)."""
    if size_bytes is None or size_bytes <= 0:
        return "Unknown size"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {units[i]}"


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds into HH:MM:SS or MM:SS."""
    if not seconds or seconds < 0:
        return "Live / Unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def get_ffmpeg_path() -> Optional[str]:
    """Retrieve bundled ffmpeg path from imageio_ffmpeg."""
    try:
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(path):
            return path
    except Exception:
        pass
    return None


class FormatAnalyzer:
    """Parses raw yt-dlp format dictionaries into categorized, user-friendly options."""

    @classmethod
    def analyze(cls, info: Dict[str, Any]) -> Dict[str, Any]:
        formats = info.get("formats", [])
        duration = info.get("duration")

        # Separate streams
        video_streams = []
        audio_streams = []
        combined_streams = []
        raw_list = []

        for f in formats:
            fid = str(f.get("format_id", ""))
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")
            ext = f.get("ext", "mp4")
            height = f.get("height") or 0
            width = f.get("width") or 0
            fps = f.get("fps") or 0
            tbr = f.get("tbr") or 0
            abr = f.get("abr") or 0
            url = f.get("url") or ""

            # Estimate filesize if not directly given
            filesize = f.get("filesize") or f.get("filesize_approx")
            if not filesize and tbr and duration:
                # tbr is in kilobits per second
                filesize = int((tbr * 1000 / 8) * duration)

            has_video = vcodec != "none" and vcodec is not None
            has_audio = acodec != "none" and acodec is not None

            # Skip storyboard / manifest placeholders without direct streaming
            if "storyboard" in f.get("format_note", "").lower() or ext in ("mhtml",):
                continue

            item = {
                "format_id": fid,
                "ext": ext,
                "height": height,
                "width": width,
                "resolution": f.get("resolution") or (f"{width}x{height}" if height else "Unknown"),
                "fps": fps,
                "vcodec": vcodec,
                "acodec": acodec,
                "tbr": tbr,
                "abr": abr,
                "filesize": filesize,
                "filesize_str": format_bytes(filesize),
                "url": url,
                "has_video": has_video,
                "has_audio": has_audio,
                "protocol": f.get("protocol", "https"),
                "format_note": f.get("format_note", ""),
            }
            raw_list.append(item)

            if has_video and has_audio:
                combined_streams.append(item)
            elif has_video and not has_audio:
                video_streams.append(item)
            elif has_audio and not has_video:
                audio_streams.append(item)

        # Find best audio stream (for pairing with video or standalone audio)
        best_audio = None
        if audio_streams:
            sorted_audio = sorted(audio_streams, key=lambda a: (a.get("abr") or 0, a.get("filesize") or 0), reverse=True)
            best_audio = sorted_audio[0]

        # Generate User-Friendly Video Quality Presets
        target_heights = [2160, 1440, 1080, 720, 480, 360, 240]
        label_map = {
            2160: "4K Ultra HD (2160p)",
            1440: "2K Quad HD (1440p)",
            1080: "Full HD (1080p)",
            720: "HD (720p)",
            480: "Standard (480p)",
            360: "Medium (360p)",
            240: "Low (240p)",
        }

        video_presets = []
        seen_heights = set()

        all_video_candidates = video_streams + combined_streams
        all_video_candidates.sort(key=lambda x: (x.get("height") or 0, x.get("tbr") or 0), reverse=True)

        for target in target_heights:
            matches = [v for v in all_video_candidates if v.get("height") == target]
            if matches:
                best_v = matches[0]
                total_size = best_v.get("filesize") or 0
                if not best_v.get("has_audio") and best_audio:
                    total_size += (best_audio.get("filesize") or 0)

                video_presets.append({
                    "label": label_map.get(target, f"{target}p"),
                    "height": target,
                    "resolution": f"{best_v.get('width', 0)}x{target}",
                    "fps": best_v.get("fps"),
                    "video_format_id": best_v["format_id"],
                    "audio_format_id": best_audio["format_id"] if best_audio and not best_v.get("has_audio") else None,
                    "download_format_spec": f"{best_v['format_id']}+{best_audio['format_id']}" if best_audio and not best_v.get("has_audio") else best_v["format_id"],
                    "stream_video_url": best_v["url"],
                    "stream_audio_url": best_audio["url"] if best_audio and not best_v.get("has_audio") else None,
                    "is_muxed": best_v.get("has_audio", False),
                    "ext": "mp4",
                    "codec": best_v.get("vcodec", "Unknown"),
                    "filesize_str": format_bytes(total_size) if total_size > 0 else "Adaptive",
                })
                seen_heights.add(target)

        # Fallback if non-standard resolution
        if not video_presets and all_video_candidates:
            v = all_video_candidates[0]
            video_presets.append({
                "label": f"Best Video ({v.get('height', 'Default')}p)",
                "height": v.get("height", 0),
                "resolution": v.get("resolution", "Standard"),
                "fps": v.get("fps"),
                "video_format_id": v["format_id"],
                "audio_format_id": best_audio["format_id"] if best_audio and not v.get("has_audio") else None,
                "download_format_spec": f"{v['format_id']}+{best_audio['format_id']}" if best_audio and not v.get("has_audio") else v["format_id"],
                "stream_video_url": v["url"],
                "stream_audio_url": best_audio["url"] if best_audio and not v.get("has_audio") else None,
                "is_muxed": v.get("has_audio", False),
                "ext": "mp4",
                "codec": v.get("vcodec", "Unknown"),
                "filesize_str": v.get("filesize_str", "Unknown"),
            })

        # Audio Presets
        audio_presets = []
        if audio_streams:
            for a in sorted(audio_streams, key=lambda x: (x.get("abr") or 0), reverse=True):
                abr_val = a.get("abr") or 0
                label = f"Audio ({a.get('ext', 'mp3').upper()}) ~ {int(abr_val)} kbps" if abr_val else f"Audio ({a.get('ext', 'audio').upper()})"
                audio_presets.append({
                    "label": label,
                    "format_id": a["format_id"],
                    "download_format_spec": a["format_id"],
                    "stream_url": a["url"],
                    "codec": a.get("acodec", "Unknown"),
                    "bitrate": abr_val,
                    "ext": a.get("ext", "m4a"),
                    "filesize_str": a.get("filesize_str", "Unknown"),
                })
        elif combined_streams:
            c = combined_streams[0]
            audio_presets.append({
                "label": "Audio (Extracted from Best Video)",
                "format_id": c["format_id"],
                "download_format_spec": f"{c['format_id']}/bestaudio",
                "stream_url": c["url"],
                "codec": c.get("acodec", "AAC"),
                "bitrate": 192,
                "ext": "mp3",
                "filesize_str": "Auto extracted",
            })

        return {
            "video_presets": video_presets,
            "audio_presets": audio_presets,
            "raw_formats": raw_list,
            "best_audio": best_audio,
        }


class FetchInfoWorker(QThread):
    """Background worker to extract video information and formats without blocking UI."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.raw_url = url.strip()
        self.url = clean_url(self.raw_url)

    def run(self):
        try:
            ffmpeg_path = get_ffmpeg_path()
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "noplaylist": True,
                "extract_flat": False,
                "playlist_items": "1",
                "socket_timeout": 8,
                "ignoreerrors": False,
            }
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.url, download=False)
            except Exception as first_err:
                err_lower = str(first_err).lower()
                if any(p in err_lower for p in ["not available", "unavailable", "empty"]):
                    # Fallback to android client API which bypasses desktop bot protection
                    fallback_opts = dict(ydl_opts)
                    fallback_opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
                    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                        info = ydl.extract_info(self.url, download=False)
                else:
                    raise first_err

            if not info:
                self.error.emit("Could not retrieve media details. Please check the URL.")
                return

            if "entries" in info:
                entries = list(info.get("entries", []))
                if entries:
                    info = entries[0]
                else:
                    self.error.emit("The provided link does not contain any accessible videos.")
                    return

            analyzed = FormatAnalyzer.analyze(info)

            result = {
                "url": self.url,
                "title": info.get("title", "Untitled Video"),
                "uploader": info.get("uploader") or info.get("channel") or info.get("extractor", "Unknown Creator"),
                "duration": info.get("duration"),
                "duration_str": format_duration(info.get("duration")),
                "views": info.get("view_count"),
                "thumbnail": info.get("thumbnail"),
                "description": (info.get("description") or "")[:240],
                "extractor": info.get("extractor_key") or info.get("extractor", "Web Video"),
                "video_presets": analyzed["video_presets"],
                "audio_presets": analyzed["audio_presets"],
                "raw_formats": analyzed["raw_formats"],
                "best_audio": analyzed["best_audio"],
            }
            self.finished.emit(result)
        except Exception as e:
            raw_err = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', str(e))
            lower_err = raw_err.lower()
            if any(phrase in lower_err for phrase in ["not available", "unavailable", "private video", "has been removed", "copyright"]):
                err_str = "This video is not available on YouTube (it was removed, made private, or copyright-blocked by the uploader). Please try any other active video link."
            elif "requested format is not available" in lower_err:
                err_str = "Format could not be extracted for this video."
            else:
                err_str = raw_err.strip()
            self.error.emit(err_str)


class DownloadWorker(QThread):
    """Worker to download chosen format with real-time progress callbacks and cancel support."""

    progress = pyqtSignal(float, str, str, str, str)  # percent, speed, eta, downloaded, total
    status_changed = pyqtSignal(str)
    finished = pyqtSignal(str)  # output file path
    error = pyqtSignal(str)

    def __init__(
        self,
        url: str,
        format_spec: str,
        output_dir: str,
        is_audio_only: bool = False,
        audio_ext: str = "mp3",
    ):
        super().__init__()
        self.url = url.strip()
        self.format_spec = format_spec
        self.output_dir = output_dir
        self.is_audio_only = is_audio_only
        self.audio_ext = audio_ext
        self._is_cancelled = False
        self._downloaded_file: Optional[str] = None

    def cancel(self):
        self._is_cancelled = True

    def _progress_hook(self, d: Dict[str, Any]):
        if self._is_cancelled:
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user.")

        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0

            percent = 0.0
            if total > 0:
                percent = (downloaded / total) * 100.0

            speed_bytes = d.get("speed") or 0
            speed_str = f"{format_bytes(speed_bytes)}/s" if speed_bytes else "--"

            eta_sec = d.get("eta")
            eta_str = format_duration(eta_sec) if eta_sec else "--:--"

            downloaded_str = format_bytes(downloaded)
            total_str = format_bytes(total) if total else "Unknown"

            self.progress.emit(percent, speed_str, eta_str, downloaded_str, total_str)

        elif status == "finished":
            self.status_changed.emit("Merging streams and finalizing file...")
            fn = d.get("filename")
            if fn:
                self._downloaded_file = fn

    def run(self):
        try:
            self.status_changed.emit("Preparing download...")
            os.makedirs(self.output_dir, exist_ok=True)

            ffmpeg_path = get_ffmpeg_path()
            outtmpl = os.path.join(self.output_dir, "%(title)s [%(resolution)s].%(ext)s")

            ydl_opts: Dict[str, Any] = {
                "outtmpl": outtmpl,
                "progress_hooks": [self._progress_hook],
                "quiet": True,
                "no_warnings": True,
            }

            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            if self.is_audio_only:
                ydl_opts["format"] = self.format_spec or "bestaudio/best"
                ydl_opts["outtmpl"] = os.path.join(self.output_dir, "%(title)s.%(ext)s")
                if ffmpeg_path:
                    ydl_opts["postprocessors"] = [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": self.audio_ext,
                            "preferredquality": "320",
                        }
                    ]
            else:
                ydl_opts["format"] = self.format_spec or "bestvideo+bestaudio/best"
                ydl_opts["merge_output_format"] = "mp4"

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.url, download=True)
            except Exception as dl_err:
                err_lower = str(dl_err).lower()
                if any(p in err_lower for p in ["not available", "unavailable", "empty"]):
                    ydl_opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(self.url, download=True)
                else:
                    raise dl_err
                final_path = self._downloaded_file
                if not final_path and info:
                    final_path = ydl.prepare_filename(info)
                    if self.is_audio_only:
                        base, _ = os.path.splitext(final_path)
                        final_path = f"{base}.{self.audio_ext}"
                    else:
                        base, _ = os.path.splitext(final_path)
                        final_path = f"{base}.mp4"

                self.finished.emit(final_path or self.output_dir)

        except yt_dlp.utils.DownloadCancelled:
            self.status_changed.emit("Download cancelled.")
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))


class BufferStreamWorker(QThread):
    """
    Buffers media to a fast temporary file so VLC can seek forward and backward
    freely without network dropouts or restarting from 0:00.
    """

    progress = pyqtSignal(float, str)  # percent, speed
    status = pyqtSignal(str)
    ready = pyqtSignal(str, str)  # file_path, title
    error = pyqtSignal(str)

    def __init__(self, url: str, format_spec: str, title: str):
        super().__init__()
        self.url = clean_url(url.strip())
        self.format_spec = format_spec
        self.title = title
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def _progress_hook(self, d: Dict[str, Any]):
        if self._is_cancelled:
            raise yt_dlp.utils.DownloadCancelled("Buffering cancelled.")

        if d.get("status") == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            percent = (downloaded / total * 100.0) if total > 0 else 0.0
            speed = d.get("speed") or 0
            speed_str = f"{format_bytes(speed)}/s" if speed else ""
            self.progress.emit(percent, speed_str)
        elif d.get("status") == "finished":
            self.status.emit("Finalizing seekable buffer for VLC...")

    def run(self):
        import tempfile
        try:
            self.status.emit("Buffering stream for smooth timeline seeking...")
            cache_dir = os.path.join(tempfile.gettempdir(), "OmniStream_cache")
            os.makedirs(cache_dir, exist_ok=True)

            ffmpeg_path = get_ffmpeg_path()
            outtmpl = os.path.join(cache_dir, "stream_cache_%(id)s.%(ext)s")

            ydl_opts: Dict[str, Any] = {
                "outtmpl": outtmpl,
                "format": self.format_spec or "bestvideo[height<=1080]+bestaudio/best",
                "merge_output_format": "mp4",
                "progress_hooks": [self._progress_hook],
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
            if ffmpeg_path:
                ydl_opts["ffmpeg_location"] = ffmpeg_path

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.url, download=True)
            except Exception as dl_err:
                err_lower = str(dl_err).lower()
                if any(p in err_lower for p in ["not available", "unavailable", "empty"]):
                    ydl_opts["extractor_args"] = {"youtube": {"player_client": ["android"]}}
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(self.url, download=True)
                else:
                    raise dl_err
                final_path = ydl.prepare_filename(info)
                base, _ = os.path.splitext(final_path)
                mp4_path = f"{base}.mp4"
                target_file = mp4_path if os.path.exists(mp4_path) else final_path

                self.ready.emit(target_file, self.title)

        except yt_dlp.utils.DownloadCancelled:
            self.status.emit("Buffering cancelled.")
        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))

