#!/usr/bin/env python3
"""
generate_headings.py — draws lowercase-mono section headings with a hairline
rule, in your own typeface. GitHub strips <style> and <font> from README
markdown, so this is the only way to get a heading that isn't GitHub's
default sans/mono.

Run locally (not in CI — headings change rarely, no need to regenerate
nightly). Requires assets/fonts/heading.woff2 to exist — see
scripts/subset_font.py.

Usage:
  python3 scripts/generate_headings.py "about me" assets/headings/about.svg
  python3 scripts/generate_headings.py "tech stack" assets/headings/stack.svg
"""

import base64
import sys
from pathlib import Path

GREEN = "#00FF41"
BG = "#0d1117"

FONT_PATH = Path("assets/fonts/heading.woff2")


def font_face_css():
    if not FONT_PATH.exists():
        print(
            f"warning: {FONT_PATH} not found — heading will fall back to a "
            "generic sans-serif in the SVG. Run scripts/subset_font.py first.",
            file=sys.stderr,
        )
        return ""
    data = base64.b64encode(FONT_PATH.read_bytes()).decode("ascii")
    return f'''
    @font-face {{
      font-family: 'HeadingMono';
      src: url(data:font/woff2;base64,{data}) format('woff2');
    }}'''


def build_heading(label: str, width: int = 700, height: int = 40) -> str:
    css = font_face_css()
    font_family = "'HeadingMono', monospace" if css else "monospace"
    text_width = len(label) * 9  # rough monospace advance at this size
    rule_x0 = 20 + text_width + 16

    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">
  <title>{label}</title>
  <style>{css}
    text {{ font-family: {font_family}; font-size: 16px; letter-spacing: 2px; }}
  </style>
  <rect width="{width}" height="{height}" fill="{BG}"/>
  <text x="20" y="25" fill="{GREEN}">{label.lower()}</text>
  <line x1="{rule_x0}" y1="20" x2="{width - 20}" y2="20"
        stroke="{GREEN}" stroke-width="1" opacity="0.35"/>
</svg>'''


def main():
    if len(sys.argv) != 3:
        print("usage: generate_headings.py <label> <output-path>", file=sys.stderr)
        sys.exit(1)
    label, out_path = sys.argv[1], sys.argv[2]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(build_heading(label))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
