import re

import click

PRESET_COLORS = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "blue": "#0000FF",
    "navy": "#000080",
    "forest": "#228B22",
    "orange": "#FF8C00",
    "purple": "#800080",
}


def validate_hex_color(value: str) -> str:
    v = value.strip()
    if v.lower() in PRESET_COLORS:
        return PRESET_COLORS[v.lower()]

    if not v.startswith("#"):
        v = "#" + v

    if re.fullmatch(r"#[0-9a-fA-F]{3}", v):
        v = "#" + v[1] * 2 + v[2] * 2 + v[3] * 2

    if not re.fullmatch(r"#[0-9a-fA-F]{6}", v):
        raise click.BadParameter(
            f"Invalid color '{value}'. Use hex (#FF0000) or name ({', '.join(PRESET_COLORS)})"
        )

    return v.upper()


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def interpolate_color(color1: str, color2: str, t: float) -> str:
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex(
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b)),
    )
