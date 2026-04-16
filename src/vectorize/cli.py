from pathlib import Path

import click

from .colors import validate_hex_color
from .pipeline import run


@click.command()
@click.argument("input_image", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default=None, help="Output SVG path (default: input name with .svg)")
@click.option("--color", "-c", type=str, default=None, help="Hex color for single-color mode (e.g. #FF0000 or 'red')")
@click.option("--gradient", "-g", is_flag=True, default=False, help="Enable gradient/multi-tone mode")
@click.option("--color-dark", type=str, default=None, help="Gradient dark end color (default: #000000)")
@click.option("--color-light", type=str, default=None, help="Gradient light end color (default: #FFFFFF)")
@click.option("--levels", type=click.IntRange(2, 8), default=None, help="Number of gradient tone levels (2-8)")
@click.option("--threshold", "-t", type=click.IntRange(0, 255), default=128, help="B&W threshold (0-255)")
@click.option("--quality", "-q", type=click.IntRange(1, 10), default=4, help="Speckle filter (1=max detail, 10=clean)")
@click.option(
    "--blur",
    type=click.FloatRange(0.0, 10.0),
    default=0.0,
    help="Gaussian blur radius (pre-trace, on grayscale). 0 = off.",
)
@click.option(
    "--restore",
    "restore_opt",
    type=click.Choice(["none", "light", "medium", "heavy"], case_sensitive=False),
    default=None,
    help="Clean up scraped/damaged shapes after threshold/quantize (omit in interactive mode to be prompted).",
)
@click.option("--png", is_flag=True, default=False, help="Also export a PNG with transparent background")
@click.option("--interactive/--no-interactive", "-i/-I", default=None, help="Force interactive mode on/off")
def main(input_image, output, color, gradient, color_dark, color_light, levels, threshold, quality, blur, restore_opt, png, interactive):
    """Convert a raster image (PNG, JPG, etc.) to SVG."""
    if output is None:
        output = str(Path(input_image).with_suffix(".svg"))

    entered_mode_prompt = False
    # Determine mode
    if gradient:
        mode = "gradient"
    elif color:
        mode = "single"
        color = validate_hex_color(color)
    elif interactive is False:
        mode = "single"
        color = "#000000"
    else:
        # Interactive mode
        entered_mode_prompt = True
        mode = click.prompt(
            "Vectorization mode",
            type=click.Choice(["single", "gradient"], case_sensitive=False),
            default="single",
        )

    # Gather color settings
    if mode == "single" and color is None:
        color = click.prompt("Color (hex or name)", default="#000000", value_proc=validate_hex_color)

    if mode == "gradient":
        if levels is None:
            if interactive is False:
                levels = 4
            else:
                levels = click.prompt("Number of tone levels", type=click.IntRange(2, 8), default=4)
        if color_dark is None:
            if interactive is False:
                color_dark = "#000000"
            else:
                color_dark = click.prompt("Dark color (hex or name)", default="#000000", value_proc=validate_hex_color)
        else:
            color_dark = validate_hex_color(color_dark)
        if color_light is None:
            if interactive is False:
                color_light = "#FFFFFF"
            else:
                color_light = click.prompt("Light color (hex or name)", default="#FFFFFF", value_proc=validate_hex_color)
        else:
            color_light = validate_hex_color(color_light)

    if restore_opt is None:
        if interactive is False:
            restore = "none"
        elif interactive is True or entered_mode_prompt:
            restore = click.prompt(
                "Restore strength",
                type=click.Choice(["none", "light", "medium", "heavy"], case_sensitive=False),
                default="none",
            )
        else:
            restore = "none"
    else:
        restore = restore_opt

    # Build config
    config = {
        "input_path": input_image,
        "output_path": output,
        "mode": mode,
        "threshold": threshold,
        "quality": quality,
        "blur": blur,
        "restore": restore,
        "png": png,
    }

    if mode == "single":
        config["color"] = color
    else:
        config["color_dark"] = color_dark
        config["color_light"] = color_light
        config["levels"] = levels

    run(config)
