from vectorize.svg_processing import (
    _fill_brightness,
    replace_gradient_colors,
    replace_single_color,
)

SAMPLE_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <path d="M0 0h50v50H0z" fill="#000000"/>
  <path d="M50 0h50v100H0z" fill="#808080"/>
  <path d="M0 50h100v50H0z" fill="#FFFFFF"/>
</svg>
"""

SAMPLE_SVG_NO_NS = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100" height="100">
  <path d="M0 0h50v50H0z" fill="#000000"/>
  <path d="M50 0h50v50H0z" fill="#FFFFFF"/>
</svg>
"""


def test_fill_brightness_black():
    assert _fill_brightness("#000000") == 0.0


def test_fill_brightness_white():
    assert _fill_brightness("#FFFFFF") == 1.0


def test_fill_brightness_rgb():
    b = _fill_brightness("rgb(128, 128, 128)")
    assert 0.4 < b < 0.6


def test_replace_single_color():
    result = replace_single_color(SAMPLE_SVG, "#FF0000")
    assert "#FF0000" in result
    # White path should be preserved (brightness > 0.9)
    assert "FFFFFF" in result or "ffffff" in result.lower()


def test_replace_single_color_no_namespace():
    result = replace_single_color(SAMPLE_SVG_NO_NS, "#00FF00")
    assert "#00FF00" in result


def test_replace_gradient_colors():
    result = replace_gradient_colors(SAMPLE_SVG, "#000080", "#FF8C00", 4)
    # Should contain interpolated colors, not the original grays
    assert "#000080" in result or "#000080" in result.upper()
    assert "808080" not in result
