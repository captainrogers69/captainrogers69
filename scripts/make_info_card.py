"""Write info-card.svg: neofetch-style card whose rows fade/slide in.

Edit ROWS to update. Height matches ascii.svg so the README table lines up.
STATIC=1 renders the final frame.
"""
import os
import re
from pathlib import Path

from window import BAR, frame

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
ASCII = ROOT / "ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
W, PAD = 486, 24
USER, HOST = "mayank-mobiledev", "github"
ROWS = [
    ("Role", "Senior Mobile Engineer @ CodeVIT"),
    ("Prev", "SoluLab · AllEvents · WashInTime"),
    ("Stack", "Flutter · Node.js · TypeScript"),
    ("Platforms", "Android · iOS · macOS"),
    ("Shipped", "AllEvents · Toskie · NotchPeek"),
    None,
    ("GitHub", "@captainrogers69"),
    ("X", "@captainroger69"),
]
SWATCHES = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#9be9a8", "#e6edf3"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    m = ASCII.exists() and re.search(r'height="(\d+)"', ASCII.read_text())
    H = int(m.group(1)) if m else 388

    step = 0.14
    parts, t = [], 0.4

    def group(body):
        nonlocal t
        style = "" if STATIC else f' style="animation-delay:{t:.2f}s"'
        parts.append(f'<g class="row"{style}>{body}</g>')
        t += step

    y = BAR + 30
    group(f'<text y="{y}"><tspan class="p">{USER}</tspan><tspan class="d">@</tspan>'
          f'<tspan class="p">{HOST}</tspan></text>')
    y += 20
    group(f'<text y="{y}" class="d">{"-" * (len(USER) + len(HOST) + 1)}</text>')
    y += 30
    key_w = max(len(r[0]) for r in ROWS if r) + 2
    for row in ROWS:
        if row is None:
            y += 14
            continue
        k, v = row
        group(f'<text y="{y}"><tspan class="k">{k}</tspan><tspan class="d">{":".ljust(key_w - len(k))}</tspan>'
              f'<tspan class="v">{esc(v)}</tspan></text>')
        y += 26

    sw_y = H - PAD - 44
    group("".join(
        f'<rect x="{i * 30}" y="{sw_y}" width="26" height="14" rx="2" fill="{c}"/>'
        for i, c in enumerate(SWATCHES)
    ))
    group(f'<text y="{H - PAD}"><tspan class="p">{USER}@{HOST}</tspan><tspan class="d"> ~ $ </tspan>'
          f'<tspan class="cur">\u2588</tspan></text>')

    anim = "" if STATIC else """
  .row { opacity: 0; animation: in .5s ease-out forwards; }
  .cur { animation: blink 1.1s steps(1) infinite; }
  @keyframes in { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: none; } }
  @keyframes blink { 50% { fill-opacity: 0; } }"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mayank Yadav: Senior Mobile Engineer at CodeVIT">
<style>
  text {{ font-family: {FONT}; font-size: 13px; white-space: pre; }}
  .p {{ fill: #39d353; font-weight: 600; }}
  .k {{ fill: #9be9a8; font-weight: 600; }}
  .v {{ fill: #e6edf3; }}
  .d {{ fill: #7d8590; }}
  .cur {{ fill: #39d353; }}{anim}
</style>
{frame(W, H, f"{USER}@{HOST}: ~$ neofetch")}
<g transform="translate({PAD} 0)" xml:space="preserve">
{chr(10).join(parts)}
</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({W}x{H})")


if __name__ == "__main__":
    main()
