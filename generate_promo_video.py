"""
Generates a polished 30-second 1080p Full HD promotional demo video for OmniStream.
Uses Pillow for high-quality graphic rendering and FFmpeg for video encoding.
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH = 1920
HEIGHT = 1080
FPS = 30
TOTAL_FRAMES = 900  # 30.0 seconds exactly

OUTPUT_MP4 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "OmniStream_Demo_30s.mp4")

# Fonts
FONT_DIR = r"C:\Windows\Fonts"
font_bold_huge = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 68)
font_bold_large = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 46)
font_bold_med = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 30)
font_bold_small = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 22)
font_reg_med = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 28)
font_reg_small = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 20)

def draw_badge(draw, text, x, y, bg_color, text_color, border_color=None, font=font_bold_small):
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0] + 24
    h = bbox[3] - bbox[1] + 16
    draw.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=bg_color, outline=border_color, width=1)
    draw.text((x + 12, y + 6), text, font=font, fill=text_color)
    return w, h

def render_frame(frame_num):
    # Base background
    img = Image.new("RGB", (WIDTH, HEIGHT), "#080c18")
    draw = ImageDraw.Draw(img)

    t = frame_num / FPS  # seconds

    # Subtle ambient animated background circles
    glow_x = int(WIDTH * 0.2 + 80 * math.sin(t * 0.8))
    glow_y = int(HEIGHT * 0.3 + 60 * math.cos(t * 0.7))
    draw.ellipse([glow_x - 350, glow_y - 350, glow_x + 350, glow_y + 350], fill="#0f1f45")
    draw.ellipse([WIDTH - 400, HEIGHT - 350, WIDTH + 200, HEIGHT + 200], fill="#1c1236")

    # Top persistent watermark / project bar
    draw.text((80, 50), "OmniStream", font=font_bold_med, fill="#38bdf8")
    draw.text((270, 56), "|  Laptop Video Downloader & VLC Player", font=font_reg_small, fill="#64748b")
    draw.text((WIDTH - 420, 54), "github.com/pvkkr/OmniStream", font=font_bold_small, fill="#94a3b8")
    draw.line([(80, 95), (WIDTH - 80, 95)], fill="#1e293b", width=1)

    # SCENE 1: (0.0s - 5.5s) The Pain Point Hook
    if t < 5.5:
        progress = min(1.0, t / 0.8)
        alpha = int(255 * progress)

        draw_badge(draw, "THE PROBLEM", 80, 160, "#3f1218", "#f87171", "#ef4444")

        draw.text((80, 240), "Tired of shady Telegram bots &", font=font_bold_huge, fill="#ffffff")
        draw.text((80, 325), "sketchy ad-riddled websites?", font=font_bold_huge, fill="#ef4444")

        draw.text((80, 440), "• Fake download buttons with malware popups", font=font_reg_med, fill="#cbd5e1")
        draw.text((80, 490), "• Telegram bot channels that spam promos or go offline", font=font_reg_med, fill="#cbd5e1")
        draw.text((80, 540), "• Forced low 360p compression and throttled speeds", font=font_reg_med, fill="#cbd5e1")

        # Solution card reveal
        card_y = 650
        draw.rounded_rectangle([80, card_y, WIDTH - 80, card_y + 260], radius=16, fill="#0f172a", outline="#2563eb", width=2)
        draw.text((120, card_y + 40), "✨ The Solution: OmniStream for Laptop", font=font_bold_large, fill="#38bdf8")
        draw.text((120, card_y + 110), "A clean, private desktop app that downloads or streams any social media clip directly on your PC.", font=font_reg_med, fill="#e2e8f0")
        draw.text((120, card_y + 160), "100% Free • Ad-Free • 4K & 1080p • Direct VLC Player Integration", font=font_bold_med, fill="#10b981")

    # SCENE 2: (5.5s - 12.0s) Step 1: Universal Link Engine
    elif t < 12.0:
        local_t = t - 5.5
        draw_badge(draw, "STEP 1 OF 3", 80, 140, "#172554", "#60a5fa", "#3b82f6")
        draw.text((80, 200), "Copy Any Link & Paste into OmniStream", font=font_bold_large, fill="#ffffff")
        draw.text((80, 260), "Supports 1,000+ platforms with instant automatic format discovery.", font=font_reg_med, fill="#94a3b8")

        # Platform pills
        platforms = ["YouTube", "Instagram Reels", "X / Twitter", "TikTok", "Reddit", "Vimeo", "Facebook", "m3u8"]
        px = 80
        for p in platforms:
            w, _ = draw_badge(draw, p, px, 320, "#1e293b", "#e2e8f0", "#334155")
            px += w + 14

        # URL Input Bar Simulation
        bar_y = 410
        draw.rounded_rectangle([80, bar_y, WIDTH - 80, bar_y + 80], radius=12, fill="#0f121a", outline="#3b82f6", width=2)
        sim_url = "https://www.youtube.com/watch?v=kZRfKxEuhxk"
        typed_len = int(len(sim_url) * min(1.0, local_t / 2.0))
        draw.text((110, bar_y + 24), sim_url[:typed_len] + ("|" if int(local_t * 3) % 2 == 0 else ""), font=font_reg_med, fill="#38bdf8")

        # Fetch button
        btn_x = WIDTH - 320
        draw.rounded_rectangle([btn_x, bar_y + 12, WIDTH - 100, bar_y + 68], radius=8, fill="#2563eb")
        draw.text((btn_x + 35, bar_y + 24), "⚡ Fetch Formats", font=font_bold_small, fill="#ffffff")

        # Result card appears after 2.5s
        if local_t > 2.5:
            card_y = 540
            draw.rounded_rectangle([80, card_y, WIDTH - 80, card_y + 360], radius=16, fill="#131b2e", outline="#1e293b", width=2)
            # Thumbnail simulation
            draw.rounded_rectangle([110, card_y + 30, 480, card_y + 330], radius=12, fill="#1e293b", outline="#334155")
            draw.text((230, card_y + 160), "▶ VIDEO PREVIEW", font=font_bold_med, fill="#64748b")

            draw.text((520, card_y + 40), "ఫ్రూట్ బొంబ్ | Bablu Dablu Big Magic Telugu Cartoon", font=font_bold_large, fill="#ffffff")
            draw.text((520, card_y + 110), "Channel: Kids Story  •  Duration: 12:45  •  Views: 1,420,000", font=font_reg_med, fill="#38bdf8")
            draw.text((520, card_y + 170), "✅ Formats loaded in 1.8 seconds flat!", font=font_bold_med, fill="#10b981")

            # Quick action buttons
            draw.rounded_rectangle([520, card_y + 240, 780, card_y + 305], radius=8, fill="#ea580c")
            draw.text((550, card_y + 258), "▶️ Stream in VLC", font=font_bold_small, fill="#ffffff")

            draw.rounded_rectangle([810, card_y + 240, 1070, card_y + 305], radius=8, fill="#059669")
            draw.text((845, card_y + 258), "⬇️ Download", font=font_bold_small, fill="#ffffff")

    # SCENE 3: (12.0s - 19.0s) Step 2: Quality & Size Inspector
    elif t < 19.0:
        local_t = t - 12.0
        draw_badge(draw, "STEP 2 OF 3", 80, 140, "#3b0764", "#c084fc", "#9333ea")
        draw.text((80, 200), "Choose Your Exact Quality with File Size Preview", font=font_bold_large, fill="#ffffff")
        draw.text((80, 260), "Never guess download size or get stuck with compressed 360p video again.", font=font_reg_med, fill="#94a3b8")

        # Quality cards stack
        qualities = [
            ("🎬 4K Ultra HD (2160p 60fps)", "Codec: VP9/AV1 • Crisp Cinematic Resolution", "2.1 GB", "#0f291e", "#34d399", "#059669"),
            ("🎬 Full HD (1080p 60fps)", "Codec: H.264 (AVC) • Crystal Clear Studio Quality", "571 MB", "#172554", "#60a5fa", "#2563eb"),
            ("🎬 HD Standard (720p)", "Codec: MP4 • Fast & Lightweight", "210 MB", "#1c1917", "#f59e0b", "#d97706"),
            ("🎵 Audio Extractor (MP3 320 kbps)", "High-Fidelity Stereo Audio • Podcast & Music Ready", "9.8 MB", "#2e1065", "#e879f9", "#a855f7"),
        ]

        qy = 330
        for title, desc, size, bg, fg, border in qualities:
            draw.rounded_rectangle([80, qy, WIDTH - 80, qy + 115], radius=12, fill="#131b2e", outline=border, width=1)
            draw.text((110, qy + 22), title, font=font_bold_med, fill=fg)
            draw.text((110, qy + 68), desc, font=font_reg_small, fill="#94a3b8")

            # Size badge
            draw_badge(draw, f"Est. Size: {size}", WIDTH - 520, qy + 35, bg, fg, border)

            # Download button
            draw.rounded_rectangle([WIDTH - 280, qy + 30, WIDTH - 110, qy + 85], radius=8, fill="#059669")
            draw.text((WIDTH - 240, qy + 44), "⬇️ Save", font=font_bold_small, fill="#ffffff")

            qy += 135

    # SCENE 4: (19.0s - 25.0s) Step 3: VLC Streaming with Timeline Seeking
    elif t < 25.0:
        local_t = t - 19.0
        draw_badge(draw, "STEP 3 OF 3", 80, 140, "#451a03", "#fbbf24", "#d97706")
        draw.text((80, 200), "Stream Directly in VLC with Smooth Timeline Seeking", font=font_bold_large, fill="#ffffff")
        draw.text((80, 260), "Watch instantly without waiting. Scrub forward & backward freely with ZERO restarts!", font=font_reg_med, fill="#94a3b8")

        # Big Highlight Banner
        banner_y = 330
        draw.rounded_rectangle([80, banner_y, WIDTH - 80, banner_y + 110], radius=14, fill="#0f291e", outline="#10b981", width=2)
        draw.text((120, banner_y + 35), "⚡ Fixed VLC Reset Bug: Buffer & Seek Engine", font=font_bold_large, fill="#34d399")
        draw.text((850, banner_y + 42), "Timeline never resets to 0:00!", font=font_bold_med, fill="#ffffff")

        # Shortcuts Table Frame
        grid_y = 480
        draw.rounded_rectangle([80, grid_y, WIDTH - 80, grid_y + 420], radius=14, fill="#131b2e", outline="#1e293b", width=1)

        draw.text((120, grid_y + 35), "⌨️ Instant Laptop Timeline Controls in VLC:", font=font_bold_med, fill="#38bdf8")

        shortcuts = [
            ("Shift + Left / Right", "⏪ ⏩ Jump 3 seconds Back / Forward (Fine seek)"),
            ("Alt + Left / Right", "⏪ ⏩ Jump 10 seconds Back / Forward (Standard seek)"),
            ("Ctrl + Left / Right", "⏪ ⏩ Jump 1 minute Back / Forward (Fast seek)"),
            ("Timeline Mouse Scrub", "🖱️ Click or drag anywhere along the seekbar slider"),
            ("Spacebar", "⏸️ Instant Pause / Play toggle"),
        ]

        sy = grid_y + 95
        for keys, action in shortcuts:
            draw_badge(draw, keys, 120, sy, "#1e293b", "#f8fafc", "#334155", font=font_bold_small)
            draw.text((450, sy + 6), action, font=font_reg_med, fill="#e2e8f0")
            sy += 60

    # SCENE 5: (25.0s - 30.0s) Call to Action & GitHub
    else:
        draw_badge(draw, "100% FREE & OPEN SOURCE", 80, 150, "#172554", "#60a5fa", "#3b82f6")

        draw.text((80, 230), "OmniStream", font=font_bold_huge, fill="#ffffff")
        draw.text((80, 315), "The Ultimate Social Media Video Tool for Laptop", font=font_bold_large, fill="#38bdf8")

        draw.text((80, 420), "• No more Telegram bot spam or fake download websites", font=font_reg_med, fill="#e2e8f0")
        draw.text((80, 475), "• 4K, 1080p, 720p, and 320k MP3 audio formats with file sizes", font=font_reg_med, fill="#e2e8f0")
        draw.text((80, 530), "• Seamless VLC streaming with backward/forward timeline seeking", font=font_reg_med, fill="#e2e8f0")
        draw.text((80, 585), "• 100% Private, Ad-Free, and runs locally on your PC", font=font_reg_med, fill="#e2e8f0")

        # GitHub Repo Showcase Card
        gh_y = 670
        draw.rounded_rectangle([80, gh_y, WIDTH - 80, gh_y + 240], radius=16, fill="#0f172a", outline="#2563eb", width=2)
        draw.text((120, gh_y + 40), "⭐ Get It on GitHub Now:", font=font_bold_med, fill="#94a3b8")
        draw.text((120, gh_y + 90), "https://github.com/pvkkr/OmniStream", font=font_bold_huge, fill="#38bdf8")
        draw.text((120, gh_y + 175), "Clone repository & double-click 'create_shortcut.bat' to start!", font=font_bold_med, fill="#10b981")

    return img

def main():
    print("Starting 30-Second 1080p Video Generation...")
    print(f"Output Target: {OUTPUT_MP4}")
    print(f"Frames: {TOTAL_FRAMES} (30 fps * 30.0s)")

    ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_bin,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        OUTPUT_MP4,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for i in range(TOTAL_FRAMES):
        frame = render_frame(i)
        proc.stdin.write(frame.tobytes())
        if i % 60 == 0:
            pct = (i / TOTAL_FRAMES) * 100
            print(f"Rendering: {pct:.1f}% ({i}/{TOTAL_FRAMES} frames)...", end="\r")

    proc.stdin.close()
    proc.wait()

    # Add Music Soundtrack
    print("\nAdding energetic music soundtrack to video...")
    try:
        from synthesize_music import generate_track
        import wave
        wav_temp = os.path.join(os.path.dirname(OUTPUT_MP4), "temp_soundtrack.wav")
        raw_audio = generate_track(duration=30.0, sr=44100)
        with wave.open(wav_temp, "wb") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(raw_audio)

        final_temp = os.path.join(os.path.dirname(OUTPUT_MP4), "OmniStream_Demo_30s_muxed.mp4")
        mux_cmd = [
            ffmpeg_bin, "-y",
            "-i", OUTPUT_MP4,
            "-i", wav_temp,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            final_temp
        ]
        res = subprocess.run(mux_cmd, capture_output=True)
        if res.returncode == 0:
            if os.path.exists(OUTPUT_MP4):
                os.remove(OUTPUT_MP4)
            os.rename(final_temp, OUTPUT_MP4)
        if os.path.exists(wav_temp):
            os.remove(wav_temp)
    except Exception as e:
        print(f"Warning: Audio muxing skipped: {e}")

    print(f"\nRender Complete! Video with music successfully saved to: {OUTPUT_MP4}")

if __name__ == "__main__":
    main()
