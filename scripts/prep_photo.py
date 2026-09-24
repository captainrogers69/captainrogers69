"""One-off local prep: cut out the subject, crop, boost contrast -> source-prepped.png (gray + alpha).

usage: python scripts/prep_photo.py <photo> [left top right bottom]
Crop box is in source pixels; default fits IMG_5456.PNG (head + shoulders).
Needs requirements-local.txt (rembg, opencv); CI never runs this.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"
DEFAULT_BOX = (400, 150, 960, 730)


def main():
    if len(sys.argv) not in (2, 6):
        raise SystemExit(__doc__)
    src = Image.open(sys.argv[1]).convert("RGB")
    box = tuple(map(int, sys.argv[2:6])) if len(sys.argv) == 6 else DEFAULT_BOX

    cut = remove(src.crop(box))  # RGBA, background alpha = 0
    rgba = np.array(cut)
    gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)

    # Unsharp mask so glasses/beard edges survive the downscale to glyphs.
    blur = cv2.GaussianBlur(gray, (0, 0), 3)
    gray = cv2.addWeighted(gray, 1.6, blur, -0.6, 0)

    # Keep alpha: the ASCII step uses it to decide blank vs subject.
    out = np.dstack([gray, rgba[..., 3]])
    Image.fromarray(out, "LA").save(OUT)
    print(f"wrote {OUT.name} {out.shape[1]}x{out.shape[0]}")


if __name__ == "__main__":
    main()
