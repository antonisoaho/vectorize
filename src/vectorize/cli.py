from pathlib import Path

import click

from .colors import validate_hex_color
from .pipeline import run

RESTORE_CHOICES = ["none", "light", "medium", "heavy"]


@click.command()
@click.argument("input_image", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None, help="Output SVG path (default: input name with .svg)")
@click.option("--color", "-c", type=str, default=None, help="Hex color or name (e.g. #FF0000 or 'red')")
@click.option("--threshold", "-t", type=click.IntRange(0, 255), default=128, help="B&W threshold (0-255)")
@click.option("--quality", "-q", type=click.IntRange(1, 10), default=4, help="Speckle filter (1=max detail, 10=clean)")
@click.option("--blur", type=click.FloatRange(0.0, 10.0), default=0.0, help="Gaussian blur radius before threshold. 0 = off.")
@click.option(
    "--restore",
    "restore_opt",
    type=click.Choice(RESTORE_CHOICES, case_sensitive=False),
    default=None,
    help="Clean up scraped/damaged shapes (none/light/medium/heavy).",
)
@click.option("--png", is_flag=True, default=False, help="Also export a PNG with transparent background")
@click.option("--interactive/--no-interactive", "-i/-I", default=None, help="Force interactive mode on/off")
def main(input_image, output, color, threshold, quality, blur, restore_opt, png, interactive):
    """Convert a raster image (PNG, JPG, etc.) to a single-color SVG."""
    if output is None:
        output = str(Path(input_image).with_suffix(".svg"))

    prompted_color = False
    if color:
        color = validate_hex_color(color)
    elif interactive is False:
        color = "#000000"
    else:
        prompted_color = True
        color = click.prompt("Color (hex or name)", default="#000000", value_proc=validate_hex_color)

    if restore_opt is None:
        if interactive is True or prompted_color:
            restore = click.prompt(
                "Restore strength",
                type=click.Choice(RESTORE_CHOICES, case_sensitive=False),
                default="none",
            )
        else:
            restore = "none"
    else:
        restore = restore_opt

    config = {
        "input_path": input_image,
        "output_path": output,
        "color": color,
        "threshold": threshold,
        "quality": quality,
        "blur": blur,
        "restore": restore,
        "png": png,
    }

    run(config)
