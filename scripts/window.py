"""Shared macOS-style window frame for the profile cards.

frame(W, H, title) -> SVG for the card background and title bar;
content should start below BAR.
"""
BAR = 32
RADIUS = 10
DOTS = ("#ff5f57", "#febc2e", "#28c840")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame(W, H, title):
    r = RADIUS
    bar = (f'<path d="M.5 {BAR} V{r + .5} a{r} {r} 0 0 1 {r} -{r} H{W - r - .5} '
           f'a{r} {r} 0 0 1 {r} {r} V{BAR} Z" fill="#161b22"/>')
    dots = "".join(
        f'<circle cx="{20 + i * 20}" cy="{BAR / 2}" r="6" fill="{c}"/>' for i, c in enumerate(DOTS)
    )
    return (
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{r}" fill="#0d1117"/>'
        f"{bar}{dots}"
        f'<text x="{W / 2}" y="{BAR / 2 + 4}" text-anchor="middle" '
        f'style="font-size:12px;fill:#7d8590">{esc(title)}</text>'
        f'<line x1=".5" x2="{W - .5}" y1="{BAR}" y2="{BAR}" stroke="#30363d"/>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="{r}" fill="none" stroke="#30363d"/>'
    )
