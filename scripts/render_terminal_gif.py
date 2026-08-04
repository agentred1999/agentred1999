#!/usr/bin/env python3
"""
render_terminal_gif.py — renders assets/ibm-terminal.svg (which uses SMIL
<animate> for its typing/cursor animation) into assets/ibm-terminal.gif.

Why this exists: GitHub's camo image proxy strips <animate>/SMIL tags from
any SVG embedded in a README, so the SVG never actually animates there. It
still animates correctly in a real browser, so we drive a real (headless)
browser, capture frames across the animation's timeline, and encode a GIF.

Keep editing assets/ibm-terminal.svg as the source of truth. Run this
script whenever you change it, then commit both the .svg and the
regenerated .gif.

Requirements:
    pip install playwright --break-system-packages
    python3 -m playwright install chromium
    ffmpeg must be on PATH (sudo apt install ffmpeg)

Usage:
    python3 scripts/render_terminal_gif.py
    python3 scripts/render_terminal_gif.py --duration 15.4 --tail 2.0 --fps 10
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = REPO_ROOT / "assets" / "ibm-terminal.svg"
GIF_PATH = REPO_ROOT / "assets" / "ibm-terminal.gif"


def check_dependencies():
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH. Install it with: sudo apt install ffmpeg")
    try:
        import playwright  # noqa: F401
    except ImportError:
        sys.exit(
            "playwright not installed. Install it with:\n"
            "  pip install playwright --break-system-packages\n"
            "  python3 -m playwright install chromium"
        )


def capture_frames(frames_dir: Path, duration: float, tail: float, fps: int, width: int, height: int):
    from playwright.sync_api import sync_playwright

    wrapper_html = frames_dir / "wrapper.html"
    wrapper_html.write_text(f"""<!DOCTYPE html>
<html><head><style>html,body{{margin:0;padding:0;background:#fff;}}</style></head>
<body><img src="{SVG_PATH.name}" width="{width}" height="{height}"></body></html>
""")
    shutil.copy(SVG_PATH, frames_dir / SVG_PATH.name)

    total_frames = int((duration + tail) * fps)
    frame_interval = 1.0 / fps

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"file://{wrapper_html}")
        page.wait_for_timeout(50)

        start = time.time()
        for i in range(total_frames):
            target_t = i * frame_interval
            elapsed = time.time() - start
            wait_ms = max(0, (target_t - elapsed) * 1000)
            if wait_ms > 0:
                page.wait_for_timeout(wait_ms)
            page.screenshot(path=str(frames_dir / f"frame_{i:04d}.png"))

        browser.close()

    return total_frames


def encode_gif(frames_dir: Path, fps: int, out_path: Path):
    palette = frames_dir / "palette.png"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.png"),
            "-vf", "palettegen=stats_mode=diff",
            "-update", "1",
            str(palette),
        ],
        check=True, capture_output=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.png"),
            "-i", str(palette),
            "-lavfi", "paletteuse=dither=bayer:bayer_scale=3",
            "-loop", "0",
            str(out_path),
        ],
        check=True, capture_output=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=15.4,
                         help="Length in seconds of the SVG's animation timeline (match the dur= on the cursor's animate tags)")
    parser.add_argument("--tail", type=float, default=2.0,
                         help="Extra seconds to capture after typing finishes, so the resting cursor blink shows before the GIF loops")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second for the output GIF")
    parser.add_argument("--width", type=int, default=700)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()

    if not SVG_PATH.exists():
        sys.exit(f"Source SVG not found: {SVG_PATH}")

    check_dependencies()

    with tempfile.TemporaryDirectory() as tmp:
        frames_dir = Path(tmp)
        print(f"Capturing frames from {SVG_PATH.name} "
              f"({args.duration}s + {args.tail}s tail at {args.fps}fps)...")
        n = capture_frames(frames_dir, args.duration, args.tail, args.fps, args.width, args.height)
        print(f"Captured {n} frames. Encoding GIF...")
        encode_gif(frames_dir, args.fps, GIF_PATH)

    size_kb = GIF_PATH.stat().st_size / 1024
    print(f"Done: {GIF_PATH} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
