"""Render data/contributions.json as an animated contrib-heatmap.svg.

Cells drop in along a diagonal sweep (CSS keyframes, which GitHub keeps
running inside <img>-embedded SVGs). STATIC=1 renders the final frame.
"""
import json
import os
from datetime import date
from pathlib import Path

from window import BAR, frame

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
STATIC = os.environ.get("STATIC") == "1"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

W = 860
CELL, GAP = 12, 3
STEP = CELL + GAP
GRID_Y = 62
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt_day(iso):
    d = date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}"


def main():
    data = json.loads(DATA.read_text())
    days, stats = data["days"], data["stats"]

    first = date.fromisoformat(days[0]["date"])
    start_sunday = first.toordinal() - (first.weekday() + 1) % 7

    def pos(iso):
        dt = date.fromisoformat(iso)
        return dt, (dt.toordinal() - start_sunday) // 7, (dt.weekday() + 1) % 7

    ncols = pos(days[-1]["date"])[1] + 1
    # Centre the grid; weekday labels hang off its left edge.
    GRID_X = round((W - ncols * STEP + GAP) / 2) + 12

    cells, month_labels = [], []
    for d in days:
        dt, col, row = pos(d["date"])
        if dt.day == 1 and col < ncols - 2:
            if month_labels and col - month_labels[-1][0] < 3:
                month_labels.pop()  # partial first month would collide
            month_labels.append((col, MONTHS[dt.month - 1]))
        x, y = GRID_X + col * STEP, GRID_Y + row * STEP
        delay = (col + row) * 0.018
        title = f"{d['count']} contribution{'s' * (d['count'] != 1)} on {fmt_day(d['date'])}"
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{PALETTE[min(d["level"], 4)]}" style="animation-delay:{delay:.3f}s">'
            f"<title>{title}</title></rect>"
        )

    grid_h = 7 * STEP
    legend_y = GRID_Y + grid_h + 14
    footer_y = legend_y + 42
    H = footer_y + 34 + BAR
    sweep_end = (ncols + 7) * 0.018 + 0.4

    tiles = [
        ("contributions", f"{stats['total']:,}"),
        ("active days", stats["active_days"]),
        ("current streak", f"{stats['current_streak']}d"),
        ("longest streak", f"{stats['longest_streak']}d"),
        ("best day", f"{stats['best_day']['count']} · {fmt_day(stats['best_day']['date'])}"),
    ]
    tile_w = (W - 48) / len(tiles)
    footer = []
    for i, (label, value) in enumerate(tiles):
        x = 24 + i * tile_w
        footer.append(
            f'<g class="f" style="animation-delay:{sweep_end + i * 0.12:.2f}s">'
            f'<text x="{x:.0f}" y="{footer_y}" class="v">{esc(value)}</text>'
            f'<text x="{x:.0f}" y="{footer_y + 17}" class="l">{label}</text></g>'
        )

    legend_x = W - 24 - 5 * STEP - 34
    legend = [f'<text x="{legend_x - 8}" y="{legend_y + 10}" class="l" text-anchor="end">less</text>']
    for i, c in enumerate(PALETTE):
        legend.append(f'<rect x="{legend_x + i * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    legend.append(f'<text x="{legend_x + 5 * STEP + 4}" y="{legend_y + 10}" class="l">more</text>')

    months = "".join(
        f'<text x="{GRID_X + col * STEP}" y="{GRID_Y - 8}" class="l">{m}</text>'
        for col, m in month_labels
    )
    weekdays = "".join(
        f'<text x="{GRID_X - 8}" y="{GRID_Y + r * STEP + 10}" class="l" text-anchor="end">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    anim = "" if STATIC else """
  .c { opacity: 0; transform-box: fill-box; transform-origin: center;
       animation: drop .45s cubic-bezier(.2,.8,.3,1.2) forwards; }
  .f { opacity: 0; animation: fade .6s ease-out forwards; }
  @keyframes drop { from { opacity: 0; transform: translateY(-8px) scale(.4); }
                    to   { opacity: 1; transform: none; } }
  @keyframes fade { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin meet" role="img" aria-label="{stats['total']} GitHub contributions in the last year">
<style>
  text {{ font-family: {FONT}; }}
  .l {{ fill: #7d8590; font-size: 11px; }}
  .v {{ fill: #e6edf3; font-size: 18px; font-weight: 600; }}
  .h {{ fill: #e6edf3; font-size: 13px; }}{anim}
</style>
{frame(W, H, "mayank-mobiledev@github: ~$ ./contributions.sh")}
<g transform="translate(0 {BAR})">
<text x="24" y="28" class="h">{stats['total']:,} contributions in the last year</text>
<text x="{W - 24}" y="28" class="l" text-anchor="end">updated {esc(data['generated'])}</text>
{months}
{weekdays}
{''.join(cells)}
{''.join(legend)}
<line x1="24" x2="{W - 24}" y1="{footer_y - 30}" y2="{footer_y - 30}" stroke="#21262d"/>
{''.join(footer)}
</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({ncols} weeks, {W}x{H})")


if __name__ == "__main__":
    main()
