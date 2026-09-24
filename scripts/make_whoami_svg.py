"""Merge ascii.svg + info-card.svg into whoami.svg and whoami-stacked.svg.

GitHub scales README images to its column width (max-width: 100%), so two
separate <img>s wrap onto two lines. whoami.svg keeps the cards side by side
at 860 wide; whoami-stacked.svg puts them in a column for phones. The README
picks one with <picture> media queries. Run after make_ascii_svg.py and
make_info_card.py.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEFT, RIGHT = ROOT / "ascii.svg", ROOT / "info-card.svg"
OUT = ROOT / "whoami.svg"
OUT_STACKED = ROOT / "whoami-stacked.svg"
GAP = 4
STACK_GAP = 12


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
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin meet" '
        f'role="img" aria-label="Mayank Yadav: ASCII portrait and profile card">\n'
        f"{left}{right}</svg>\n"
    )
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({W}x{H})")

    # Stacked: portrait scaled up to the info card's width, card underneath.
    left, right = LEFT.read_text(), RIGHT.read_text()
    sh = round(lh * rw / lw)
    left = left.replace(f'width="{lw}" height="{lh}"', f'width="{rw}" height="{sh}"', 1)
    right = right.replace("<svg ", f'<svg x="0" y="{sh + STACK_GAP}" ', 1)
    W, H = rw, sh + STACK_GAP + rh
    OUT_STACKED.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin meet" '
        f'role="img" aria-label="Mayank Yadav: ASCII portrait and profile card">\n'
        f"{left}{right}</svg>\n"
    )
    print(f"wrote {OUT_STACKED.name} ({W}x{H})")


if __name__ == "__main__":
    main()
