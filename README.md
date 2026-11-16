# OmniStream - Universal Video Downloader & VLC Player

A powerful Windows desktop application to download videos from any website with quality format selectors and stream directly into VLC media player with full backward & forward timeline seeking.

---

## ✨ Features

1. **Universal Link Downloader**:
   - Supports virtually any video source: **YouTube, Twitter/X, TikTok, Instagram Reels, Reddit, Vimeo, Facebook, Twitch, Dailymotion, direct MP4/m3u8 URLs**, etc.
   - Powered by `yt-dlp` and bundled `ffmpeg`.

2. **Quality & Format Selection**:
   - **Video Quality Tab**: 4K Ultra HD (2160p), 2K (1440p), Full HD (1080p), HD (720p), 480p, 360p with estimated file sizes.
   - **Audio Only Tab**: High quality MP3 (320kbps), M4A, AAC, Opus with bitrates and sizes.
   - **Advanced Formats Tab**: Detailed table showing every individual stream.

3. **VLC Streaming with Fixed Timeline Seeking**:
   - **⚡ Buffer & Seek (Guaranteed Seeking)**: Pre-buffers the stream into a local cache in a few seconds and opens in VLC. Scrubbing, jumping back, or jumping forward works **100% instantly without resetting to the start!**
   - **▶️ Direct Stream**: Streams directly over the web with `--http-reconnect`, `--http-continuous`, browser User-Agent, and 5000ms network caching so CDNs don't drop the connection on Range requests.
   - **Timeline navigation**:
     - `Shift + Left / Right`: Jump 3 seconds back / forward (fine seek)
     - `Alt + Left / Right`: Jump 10 seconds back / forward (standard seek)
     - `Ctrl + Left / Right`: Jump 1 minute back / forward
     - `Timeline Scrubbing`: Drag the bottom seekbar anywhere to jump in time!
     - `Space`: Pause / Resume

4. **Fast Downloads**:
   - Live download speed (MB/s), downloaded size, ETA countdown, and progress bar.
   - Post-download one-click buttons: **"▶️ Play in VLC"** and **"📂 Open Folder"**.

---

## 🚀 How to Launch the App

- **Desktop Shortcut**: Double-click **`OmniStream - Video Downloader & VLC`** on your Desktop.
- **Batch Launcher**: Double-click [`run.bat`](file:///c:/Users/pvkkr/Downloads/ABC/run.bat) in `c:\Users\pvkkr\Downloads\ABC`.
- **Command Line**:
  ```powershell
  cd c:\Users\pvkkr\Downloads\ABC
  python app.py
  ```
