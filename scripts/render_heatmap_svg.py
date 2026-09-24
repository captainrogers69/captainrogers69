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
GREEN, ORANGE = "#39d353", "#f0883e"
TILE_H, TILE_GAP = 58, 12
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
    sweep_end = (ncols + 7) * 0.018 + 0.4

    life = data["lifetime"]
    top_month = stats["busiest_month"]["month"]
    rows = [
        ("stats --year", [
            ("\U0001F525", "current streak", f"{stats['current_streak']}d", ORANGE),
            ("\U0001F4C8", "contributions", f"{stats['total']:,}", GREEN),
            ("\u26A1\uFE0F", "longest streak", f"{stats['longest_streak']}d", GREEN),
            ("\U0001F3C6", f"best day · {fmt_day(stats['best_day']['date'])}", str(stats["best_day"]["count"]), GREEN),
            ("\U0001F4C5", f"top month · {MONTHS[int(top_month[5:]) - 1]}", str(stats["busiest_month"]["count"]), GREEN),
        ]),
        ("stats --lifetime", [
            ("\U0001F4CA", "all-time total", f"{life['total']:,}", GREEN),
            ("\u26A1\uFE0F", "longest streak", f"{life['longest_streak']}d", GREEN),
            ("\U0001F680", f"best year · {life['best_year']['year']}", f"{life['best_year']['count']:,}", GREEN),
            ("\U0001F5D3\uFE0F", "on GitHub since", str(life["since"]), GREEN),
            ("\U0001F4E6", "public repos", str(life["public_repos"]), GREEN),
        ]),
    ]
    tile_w = (W - 48 - 4 * TILE_GAP) / 5
    footer, y0, n = [], legend_y + 50, 0
    for cmd, tiles in rows:
        footer.append(
            f'<g class="f" style="animation-delay:{sweep_end + n * 0.08:.2f}s">'
            f'<text x="24" y="{y0}" class="h"><tspan fill="{GREEN}">$</tspan> {cmd}</text></g>'
        )
        n += 1
        for i, (icon, label, value, color) in enumerate(tiles):
            x, y = 24 + i * (tile_w + TILE_GAP), y0 + 12
            footer.append(
                f'<g class="f" style="animation-delay:{sweep_end + n * 0.08:.2f}s">'
                f'<rect x="{x:.1f}" y="{y}" width="{tile_w:.1f}" height="{TILE_H}" rx="6" fill="#161b22" stroke="#30363d"/>'
                f'<rect x="{x:.1f}" y="{y}" width="3" height="{TILE_H}" rx="1.5" fill="{color}"/>'
                f'<text x="{x + 16:.1f}" y="{y + 27}" class="v" fill="{color}">{esc(value)}</text>'
                f'<text x="{x + 16:.1f}" y="{y + 46}" class="t">{icon} {esc(label)}</text></g>'
            )
            n += 1
        y0 += 12 + TILE_H + 32
    H = y0 - 32 + 20 + BAR

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
  .v {{ font-size: 18px; font-weight: 700; }}
  .t {{ fill: #8b949e; font-size: 11px; white-space: pre; }}
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
{''.join(footer)}
</g>
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT.name} ({ncols} weeks, {W}x{H})")


if __name__ == "__main__":
    main()
