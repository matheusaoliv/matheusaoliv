"""Gera matheus-ascii.svg: arte ASCII que se digita linha por linha.

    python scripts/make_ascii_svg.py                      # monograma "M"
    python scripts/make_ascii_svg.py source-prepped.png   # retrato a partir de foto

Para foto, rode antes scripts/prep_photo.py (remove fundo e aumenta contraste).
Cada linha aparece um caractere por vez (clip animado com SMIL), com um
cursor verde na borda. Toca uma vez ao carregar e congela.
"""
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

from svgkit import ACCENT, TEXT, TITLE_H, esc, window, write

RAMP = " .`:-=+*cs#%@"  # claro -> escuro; o espaço some no fundo

WIDTH, HEIGHT = 370, 400
PAD_X, PAD_Y = 22, 18
ART_W = WIDTH - 2 * PAD_X

# Colunas e altura da linha: o retrato precisa de mais resolução que o monograma.
GRID_MONOGRAM = (56, 11)
GRID_PHOTO = (100, 6.5)


def grid(cols, row_h):
    rows = int((HEIGHT - TITLE_H - 2 * PAD_Y) // row_h)
    art_h = rows * row_h
    return {"cols": cols, "rows": rows, "row_h": row_h, "cell_w": ART_W / cols,
            "art_h": art_h, "top": TITLE_H + (HEIGHT - TITLE_H - art_h) / 2}

FONTS = ["DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf"]


def load_font(size):
    for name in FONTS:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def monogram(g, text="M"):
    """Letras grossas com degradê e sombra em 3D, sobre fundo branco."""
    scale = 4
    w, h = int(ART_W * scale), int(g["art_h"] * scale)
    depth = int(h * 0.05)
    # Maior fonte que cabe na caixa contando a extrusão.
    probe = load_font(100)
    left, top, right, bottom = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=probe)
    size = 100 * min((w * 0.92 - depth) / (right - left), (h * 0.9 - depth) / (bottom - top))
    font = load_font(int(size))
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    x = (w - (right - left) - depth) / 2 - left
    y = (h - (bottom - top) - depth) / 2 - top
    draw.text((x, y), text, fill=255, font=font)

    # Extrusão para baixo/direita: vira os caracteres médios (= + *).
    extrude = Image.new("L", (w, h), 0)
    for i in range(1, depth + 1, 2):
        extrude = ImageChops.lighter(extrude, ImageChops.offset(mask, i, i))

    # Face com degradê diagonal: escuro embaixo à esquerda, mais claro no topo.
    gradient = Image.linear_gradient("L").rotate(35, expand=False).resize((w, h))
    face = ImageOps.invert(gradient).point(lambda v: 10 + v * 0.45)

    img = Image.new("L", (w, h), 255)
    img.paste(170, mask=extrude)
    img.paste(face, mask=mask)
    # Contorno claro separa a face da extrusão.
    edge = mask.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0)
    edge = edge.filter(ImageFilter.MaxFilter(3))
    img.paste(235, mask=edge)
    return img


def from_photo(g, path):
    img = ImageOps.grayscale(Image.open(path))
    target = (int(ART_W * 4), int(g["art_h"] * 4))
    return ImageOps.pad(img, target, color=255, centering=(0.5, 1.0))


def to_ascii(g, img):
    # Cada célula do terminal é ~2x mais alta que larga: reduz direto para cols x rows.
    cols, rows = g["cols"], g["rows"]
    small = ImageOps.autocontrast(img.resize((cols, rows), Image.Resampling.BOX), cutoff=1)
    px = small.load()
    return [
        "".join(RAMP[min(len(RAMP) - 1, (255 - px[x, y]) * len(RAMP) // 256)] for x in range(cols))
        for y in range(rows)
    ]


def main():
    photo = len(sys.argv) > 1
    g = grid(*(GRID_PHOTO if photo else GRID_MONOGRAM))
    cols, row_h, cell_w, top, art_h = g["cols"], g["row_h"], g["cell_w"], g["top"], g["art_h"]
    lines = to_ascii(g, from_photo(g, sys.argv[1]) if photo else monogram(g))

    # Cada linha fica atrás de um clip que alarga um caractere por vez (SMIL),
    # com o cursor verde andando junto. Toca uma vez e congela.
    dur = 0.6
    steps = ";".join(f"{k * cell_w:.1f}" for k in range(cols + 1)) + f";{ART_W + 2}"
    xs = ";".join(f"{PAD_X + k * cell_w:.1f}" for k in range(cols + 2))
    rows, clips = [], []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = top + i * row_h
        begin = f'begin="{0.2 + i * 2.6 / len(lines):.3f}s" dur="{dur}s"'
        clips.append(
            f'<clipPath id="r{i}"><rect x="{PAD_X - 1}" y="{y:.2f}" width="0" height="{row_h}">'
            f'<animate attributeName="width" values="{steps}" calcMode="discrete" {begin} fill="freeze"/>'
            f"</rect></clipPath>"
        )
        rows.append(
            f'<text clip-path="url(#r{i})" x="{PAD_X}" y="{y + row_h * 0.77:.2f}" textLength="{ART_W}" '
            f'lengthAdjust="spacing" xml:space="preserve">{esc(line)}</text>'
            f'<rect x="{PAD_X}" y="{y + 1:.2f}" width="{cell_w:.2f}" height="{row_h - 2}" fill="{ACCENT}" opacity="0">'
            f'<animate attributeName="x" values="{xs}" calcMode="discrete" {begin} fill="freeze"/>'
            f'<set attributeName="opacity" to="1" {begin}/></rect>'
        )

    css = f".art {{ font-size: {cell_w / 0.6:.2f}px; white-space: pre; }}"
    defs = (
        "".join(clips)
        + f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="{top:.2f}" x2="0" y2="{top + art_h:.2f}">'
        f'<stop offset="0" stop-color="{TEXT}"/><stop offset="1" stop-color="#7d8590"/></linearGradient>'
    )
    body = f'<g class="art" fill="url(#ink)">{"".join(rows)}</g>'
    label = "ASCII art portrait of Matheus Oliveira" if photo else "ASCII art monogram M"
    write("matheus-ascii.svg", window(WIDTH, HEIGHT, "matheus@github: ~", label, body, css, defs))


if __name__ == "__main__":
    main()
