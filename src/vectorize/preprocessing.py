from io import BytesIO
from pathlib import Path

import click
from PIL import Image, ImageFilter

SUPPORTED_FORMATS = {"PNG", "JPEG", "BMP", "TIFF", "WEBP", "GIF"}

# Single-color restore: (median_size, close_radius, open_radius, closing_repeats)
# - Small median only (large medians smear fine type on stamps).
# - Closing = MinFilter then MaxFilter with kernel 2*close_radius+1, repeated
#   ``closing_repeats`` times — fills paper-colored pinholes inside black ink
#   without the old heavy “opening” pass that ate thin strokes.
# - open_radius kept for API compatibility; presets use 0 (opening hurt logos).
RESTORE_PRESETS = {
    "none": (0, 0, 0, 0),
    "light": (3, 1, 0, 1),
    "medium": (3, 1, 0, 3),
    "heavy": (3, 1, 0, 7),
}


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


def apply_blur(img: Image.Image, radius: float) -> Image.Image:
    if radius <= 0:
        return img
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def _kernel_size(radius: int) -> int:
    """Odd square kernel size from morphological radius (radius 1 -> 3)."""
    return 2 * radius + 1


def gradient_tone_step(levels: int) -> float:
    """Luminance step between quantized bands (``convert_to_grayscale``)."""
    if levels <= 1:
        return 255.0
    return 255.0 / (levels - 1)


def gradient_level_index(v: int, levels: int) -> int:
    """Map a gray value to the nearest quantization band index ``0 .. levels-1``."""
    if levels <= 1:
        return 0
    step = gradient_tone_step(levels)
    k = int(round(v / step))
    return max(0, min(levels - 1, k))


def denoise_gray_for_gradient(img: Image.Image, strength: str) -> Image.Image:
    """Median-only denoise before quantization (gradient mode).

    Morphological ops are skipped so band boundaries stay clean; strength maps
    to median kernel size from the same preset names as ``restore_image``.
    """
    if strength not in RESTORE_PRESETS:
        raise ValueError(
            f"restore strength must be one of {sorted(RESTORE_PRESETS)}, got {strength!r}"
        )
    if strength == "none":
        return img

    median_sz, _, _, _ = RESTORE_PRESETS[strength]
    out = img if img.mode == "L" else img.convert("L")
    if median_sz > 0:
        out = out.filter(ImageFilter.MedianFilter(size=median_sz))
    return out


def restore_image(img: Image.Image, strength: str) -> Image.Image:
    """Solidify black ink on a binary mask (0 = ink, 255 = paper).

    - Light **median** (3×3) softens scanner noise without melting serifs.
    - **Closing** for black foreground: ``MinFilter`` then ``MaxFilter`` with a
      small odd kernel, repeated — grows ink into pinholes / distress gaps,
      then trims the fringe so lines stay crisp.
    - ``heavy`` uses more closing passes, not a huge median (which looked worse
      than ``none`` on fine stamp lettering).

    Works on ``L`` (and ``1``) images; returns ``L``.
    """
    if strength not in RESTORE_PRESETS:
        raise ValueError(
            f"restore strength must be one of {sorted(RESTORE_PRESETS)}, got {strength!r}"
        )
    if strength == "none":
        return img

    median_sz, close_r, open_r, close_passes = RESTORE_PRESETS[strength]
    out = img if img.mode in ("L", "1") else img.convert("L")
    if out.mode == "1":
        out = out.convert("L")

    if median_sz > 0:
        out = out.filter(ImageFilter.MedianFilter(size=median_sz))
    if close_r > 0 and close_passes > 0:
        n = _kernel_size(close_r)
        for _ in range(close_passes):
            out = out.filter(ImageFilter.MinFilter(size=n)).filter(ImageFilter.MaxFilter(size=n))
    if open_r > 0:
        n = _kernel_size(open_r)
        out = out.filter(ImageFilter.MinFilter(size=n)).filter(ImageFilter.MaxFilter(size=n))
    return out


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
