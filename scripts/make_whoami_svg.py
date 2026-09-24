"""Merge ascii.svg + info-card.svg into whoami.svg (one 860-wide image).

GitHub scales README images to its column width (max-width: 100%), so two
separate <img>s wrap onto two lines. One combined SVG scales as a unit and
stays side by side. Run after make_ascii_svg.py and make_info_card.py.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEFT, RIGHT = ROOT / "ascii.svg", ROOT / "info-card.svg"
OUT = ROOT / "whoami.svg"
GAP = 4


def size(svg):
    w, h = re.search(r'<svg[^>]*?width="(\d+)" height="(\d+)"', svg).groups()
    return int(w), int(h)


def main():
    left, right = LEFT.read_text(), RIGHT.read_text()
    (lw, lh), (rw, rh) = size(left), size(right)
    W, H = lw + GAP + rw, max(lh, rh)
    # Nested <svg>s keep each card's own coordinate system; their <style>
    # blocks become document-wide, so class/keyframe names must not clash.
    right = right.replace("<svg ", f'<svg x="{lw + GAP}" y="0" ', 1)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="Mayank Yadav: ASCII portrait and profile card">\n'
        f"{left}{right}</svg>\n"
    )
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({W}x{H})")


if __name__ == "__main__":
    main()
