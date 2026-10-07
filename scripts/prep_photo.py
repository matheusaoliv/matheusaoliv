"""Prepara uma foto para virar retrato ASCII (uso local, uma vez só).

    pip install -r scripts/requirements-local.txt
    python scripts/prep_photo.py minha-foto.jpg      # gera source-prepped.png
    python scripts/make_ascii_svg.py source-prepped.png

1. remove o fundo (rembg) para só a pessoa aparecer;
2. aumenta o contraste local (CLAHE do OpenCV) para destacar o rosto;
3. compõe sobre branco: áreas claras viram espaço no ASCII.
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

from svgkit import ROOT


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cutout = remove(Image.open(sys.argv[1]).convert("RGB"))  # RGBA sem fundo

    gray = cv2.cvtColor(np.array(cutout.convert("RGB")), cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)

    white = Image.new("L", cutout.size, 255)
    white.paste(Image.fromarray(gray), mask=cutout.getchannel("A"))
    box = white.point(lambda v: 0 if v > 250 else 255).getbbox() or (0, 0, *white.size)
    out = ROOT / "source-prepped.png"
    white.crop(box).save(out)
    print(f"ok: {out.name}")


if __name__ == "__main__":
    main()
