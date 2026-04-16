import re

from lxml import etree

from .colors import hex_to_rgb, interpolate_color

SVG_NS = "http://www.w3.org/2000/svg"
NAMESPACES = {"svg": SVG_NS}


def _find_paths(root: etree._Element) -> list[etree._Element]:
    paths = root.xpath("//svg:path", namespaces=NAMESPACES)
    if not paths:
        paths = root.xpath("//path")
    return paths


def _get_fill(el: etree._Element) -> str | None:
    fill = el.get("fill")
    if fill:
        return fill

    style = el.get("style", "")
    m = re.search(r"fill:\s*([^;]+)", style)
    if m:
        return m.group(1).strip()

    return None


def _set_fill(el: etree._Element, color: str) -> None:
    if el.get("fill") is not None:
        el.set("fill", color)
    elif "fill:" in el.get("style", ""):
        el.set("style", re.sub(r"fill:\s*[^;]+", f"fill:{color}", el.get("style")))
    else:
        el.set("fill", color)


def _fill_brightness(fill_str: str) -> float | None:
    fill_str = fill_str.strip()

    if fill_str.lower() in ("white", "#ffffff", "#fff", "rgb(255,255,255)"):
        return 1.0
    if fill_str.lower() in ("black", "#000000", "#000", "rgb(0,0,0)"):
        return 0.0

    m = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", fill_str)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    h = fill_str.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    if re.fullmatch(r"[0-9a-fA-F]{6}", h):
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    return None


def _serialize(root: etree._Element) -> str:
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode("utf-8")


def replace_single_color(svg_str: str, target_color: str) -> str:
    root = etree.fromstring(svg_str.encode("utf-8"))
    for path in _find_paths(root):
        fill = _get_fill(path)
        if fill is None:
            continue
        brightness = _fill_brightness(fill)
        if brightness is not None and brightness > 0.9:
            continue
        _set_fill(path, target_color)

    return _serialize(root)


def replace_gradient_colors(
    svg_str: str, color_dark: str, color_light: str, levels: int
) -> str:
    root = etree.fromstring(svg_str.encode("utf-8"))

    for path in _find_paths(root):
        fill = _get_fill(path)
        if fill is None:
            continue
        brightness = _fill_brightness(fill)
        if brightness is None:
            continue
        new_color = interpolate_color(color_dark, color_light, brightness)
        _set_fill(path, new_color)

    return _serialize(root)
