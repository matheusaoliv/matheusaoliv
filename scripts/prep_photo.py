"""Prepara uma foto para virar retrato ASCII (uso local, uma vez só).

    pip install -r scripts/requirements-local.txt
    python scripts/prep_photo.py minha-foto.jpg      # gera source-prepped.png
    python scripts/make_ascii_svg.py source-prepped.png

1. remove o fundo (rembg, modelo próprio para pessoas): o fundo vira espaço;
2. aumenta o contraste local (CLAHE do OpenCV) e realça bordas (óculos, sorriso);
3. converte brilho em "tinta" para o fundo escuro do terminal: quanto mais
   clara a pele, mais denso o caractere (imagem positiva, não negativo). O
   cabelo escuro ganha um mínimo de tinta para não sumir, e os tons mais claros
   (camiseta branca) perdem tinta para não virarem um bloco sólido;
4. enquadra cabeça e ombros.
Saída: tons de cinza onde preto = caractere mais denso e branco = espaço.
A foto original e o source-prepped.png ficam fora do git (.gitignore).
"""
import sys

import cv2
import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove

from svgkit import ROOT

ASPECT = 330 / 326  # altura / largura da área da arte em make_ascii_svg.py
CROP = 0.70         # lado do recorte em relação à altura da pessoa na foto

# Curva brilho -> tinta: mínimo (cabelo), pico, joelho e queda (camiseta).
FLOOR, PEAK, KNEE, DROP, GAMMA = 0.14, 0.95, 0.72, 0.55, 1.3


def ink(gray):
    a = np.asarray(gray, dtype=np.float32) / 255
    up = FLOOR + (PEAK - FLOOR) * (np.minimum(a, KNEE) / KNEE) ** GAMMA
    down = np.where(a > KNEE, (a - KNEE) / (1 - KNEE) * DROP, 0)
    return np.clip(up - down, 0, 1)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    img = Image.open(sys.argv[1]).convert("RGB")
    alpha = remove(img, session=new_session("u2net_human_seg")).getchannel("A")
    mask = alpha.point(lambda a: 255 if a > 128 else 0)

    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(6, 6)).apply(gray)
    gray = Image.fromarray(gray).filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
    person = Image.fromarray((255 - ink(gray) * 255).astype(np.uint8))

    out = Image.new("L", img.size, 255)
    out.paste(person, mask=mask)

    # Enquadra do topo da cabeça para baixo, centrado na cabeça.
    x0, y0, x1, y1 = mask.getbbox()
    head = np.array(mask)[y0:y0 + (y1 - y0) // 4]
    cx = int(np.nonzero(head)[1].mean())
    size = int((y1 - y0) * CROP)
    top = max(0, y0 - size // 40)
    box = (cx - size // 2, top, cx + size // 2, top + int(size * ASPECT))

    path = ROOT / "source-prepped.png"
    out.crop(box).save(path)
    print(f"ok: {path.name} (recorte {box})")


if __name__ == "__main__":
    main()
