from pathlib import Path

import click
import vtracer
from PIL import Image

from . import preprocessing, svg_processing
from .colors import hex_to_rgb, interpolate_color


def run(config: dict) -> None:
    click.echo(f"Loading {config['input_path']}...")
    img = preprocessing.load_and_validate(config["input_path"])

    click.echo("Converting to grayscale...")
    gray = img.convert("L")

    blur = float(config.get("blur", 0.0) or 0.0)
    if blur > 0:
        click.echo(f"Applying blur (radius {blur})...")
        gray = preprocessing.apply_blur(gray, blur)

    restore = config.get("restore", "none")

    if config["mode"] == "single":
        click.echo("Converting to black & white...")
        processed = preprocessing.convert_to_bw(gray, config["threshold"])
        if restore != "none":
            click.echo(f"Restoring ({restore})...")
            processed = preprocessing.restore_image(processed, restore)
    else:
        if restore != "none":
            click.echo(f"Restoring ({restore}) for gradient (median denoise on grayscale only)...")
            gray = preprocessing.denoise_gray_for_gradient(gray, restore)
        click.echo(f"Converting to {config['levels']}-level grayscale...")
        processed = preprocessing.convert_to_grayscale(gray, config["levels"])

    img_bytes = preprocessing.image_to_bytes(processed)

    click.echo("Vectorizing...")
    try:
        if config["mode"] == "single":
            svg_str = vtracer.convert_raw_image_to_svg(
                img_bytes,
                img_format="png",
                colormode="binary",
                mode="spline",
                filter_speckle=config["quality"],
                path_precision=8,
            )
        else:
            svg_str = vtracer.convert_raw_image_to_svg(
                img_bytes,
                img_format="png",
                colormode="color",
                hierarchical="stacked",
                mode="spline",
                filter_speckle=config["quality"],
                color_precision=6,
                layer_difference=max(1, 256 // config["levels"]),
                path_precision=8,
            )
    except Exception as e:
        raise click.ClickException(f"Vectorization failed: {e}")

    click.echo("Applying colors...")
    if config["mode"] == "single":
        svg_str = svg_processing.replace_single_color(svg_str, config["color"])
    else:
        svg_str = svg_processing.replace_gradient_colors(
            svg_str, config["color_dark"], config["color_light"], config["levels"]
        )

    output = Path(config["output_path"])
    try:
        output.write_text(svg_str, encoding="utf-8")
    except OSError as e:
        raise click.ClickException(f"Cannot write output: {e}")

    click.echo(f"Saved SVG to {output}")

    if config.get("png"):
        png_path = output.with_suffix(".png")
        click.echo("Rendering PNG with transparent background...")
        try:
            _export_png(processed, config, png_path)
        except Exception as e:
            raise click.ClickException(f"PNG export failed: {e}")
        click.echo(f"Saved PNG to {png_path}")


def _export_png(processed: Image.Image, config: dict, png_path: Path) -> None:
    w, h = processed.size
    rgba = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    gray = processed if processed.mode == "L" else processed.convert("L")
    pixels_gray = gray.load()
    pixels_out = rgba.load()

    # Near-white stays transparent after restore / anti-aliasing
    _bg_cutoff = 250

    if config["mode"] == "single":
        r, g, b = hex_to_rgb(config["color"])
        for y in range(h):
            for x in range(w):
                v = pixels_gray[x, y]
                if v >= _bg_cutoff:
                    continue
                alpha = 255 - v
                pixels_out[x, y] = (r, g, b, alpha)
    else:
        levels = config["levels"]
        color_dark = config["color_dark"]
        color_light = config["color_light"]
        denom = max(1, levels - 1)
        for y in range(h):
            for x in range(w):
                v = pixels_gray[x, y]
                k = preprocessing.gradient_level_index(v, levels)
                if k >= levels - 1:
                    continue
                t = k / denom
                cr, cg, cb = hex_to_rgb(interpolate_color(color_dark, color_light, t))
                pixels_out[x, y] = (cr, cg, cb, 255)

    rgba.save(str(png_path), format="PNG")
