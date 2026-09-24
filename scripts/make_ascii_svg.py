"""source-prepped.png -> ascii.svg: portrait that types itself in row by row.

Each row is revealed by a CSS clip-path wipe (keyframes keep running in
<img>-embedded SVGs on GitHub).

Light glyphs on the dark card, so brighter pixels get denser characters;
transparent pixels (the removed background) stay blank. STATIC=1 skips animation.
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
W, PAD, TOP = 370, 16, 44
COLS = 84
LINE_H = 8
ROW_DUR, ROW_GAP = 0.35, 0.05  # seconds per row wipe, stagger between rows


def to_rows(img):
    char_w = (W - 2 * PAD) / COLS
    rows = round(COLS * img.height / img.width * char_w / LINE_H)
    px = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32)
    lum, alpha = px[..., 0], px[..., 1]
    subject = alpha >= 128
    # Stretch contrast over the subject only, so the face uses the full ramp.
    lo, hi = np.percentile(lum[subject], (3, 99))
    norm = np.clip((lum - lo) / (hi - lo), 0, 1) ** 0.85
    lines = []
    for r in range(rows):
        line = []
        for c in range(COLS):
            if not subject[r, c]:
                line.append(" ")
            else:  # at least the faintest glyph so dark cloth still reads
                line.append(RAMP[1 + int(norm[r, c] * (len(RAMP) - 2) + 0.5)])
        lines.append("".join(line).rstrip())
    while lines and not lines[0]:
        lines.pop(0)
    return lines, char_w


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    lines, char_w = to_rows(Image.open(SRC).convert("LA"))
    H = TOP + len(lines) * LINE_H + PAD

    texts = []
    for i, line in enumerate(lines):
        if not line:
            continue
        y = TOP + (i + 1) * LINE_H - 2
        span = len(line) * char_w
        attrs = f'x="{PAD}" y="{y}" textLength="{span:.1f}" lengthAdjust="spacingAndGlyphs"'
        style = "" if STATIC else f' style="animation-delay:{0.3 + i * ROW_GAP:.2f}s"'
        texts.append(f"<text {attrs}{style}>{esc(line)}</text>")

    anim = "" if STATIC else f"""
  .a text {{ clip-path: inset(0 100% 0 0); animation: type {ROW_DUR}s steps(24, end) forwards; }}
  @keyframes type {{ to {{ clip-path: inset(0 0 0 0); }} }}"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait of Mayank Yadav">
<defs>
  <linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="{TOP}" x2="0" y2="{H}">
    <stop offset="0" stop-color="#e6edf3"/>
    <stop offset=".55" stop-color="#9be9a8"/>
    <stop offset="1" stop-color="#26a641"/>
  </linearGradient>
</defs>
<style>
  text {{ font-family: {FONT}; }}
  .a text {{ font-size: {char_w * 1.66:.2f}px; fill: url(#g); white-space: pre; }}
  .l {{ fill: #7d8590; font-size: 11px; }}{anim}
</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="{PAD}" y="26" class="l">~/mayank.jpg | ascii</text>
<g class="a" xml:space="preserve">{''.join(texts)}</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({COLS}x{len(lines)} chars, {W}x{H})")


if __name__ == "__main__":
    main()
