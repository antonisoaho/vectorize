from io import BytesIO
from pathlib import Path

import click
from PIL import Image

SUPPORTED_FORMATS = {"PNG", "JPEG", "BMP", "TIFF", "WEBP", "GIF"}


def load_and_validate(path: str) -> Image.Image:
    p = Path(path)
    if not p.exists():
        raise click.ClickException(f"File not found: {path}")

    try:
        with Image.open(p) as img:
            img.verify()
    except Exception as e:
        raise click.ClickException(f"Invalid or corrupt image: {e}")

    img = Image.open(p)
    fmt = img.format
    if fmt not in SUPPORTED_FORMATS:
        raise click.ClickException(
            f"Unsupported format '{fmt}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    return img.convert("RGB")


def convert_to_bw(img: Image.Image, threshold: int = 128) -> Image.Image:
    gray = img.convert("L")
    return gray.point(lambda x: 255 if x > threshold else 0, mode="L")


def convert_to_grayscale(img: Image.Image, levels: int = 4) -> Image.Image:
    gray = img.convert("L")
    step = 256 / levels
    max_val = 255 / (levels - 1) if levels > 1 else 0
    return gray.point(lambda x: int(min(x / step, levels - 1)) * int(max_val))


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
