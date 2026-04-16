from pathlib import Path

from PIL import Image

from vectorize.pipeline import _export_png, run


def test_single_color_pipeline(sample_bw_image, tmp_path):
    output = str(tmp_path / "result.svg")
    config = {
        "input_path": sample_bw_image,
        "output_path": output,
        "mode": "single",
        "color": "#336699",
        "threshold": 128,
        "quality": 4,
    }
    run(config)
    result = Path(output).read_text()
    assert "<svg" in result or "<?xml" in result
    assert "#336699" in result


def test_gradient_pipeline(sample_color_image, tmp_path):
    output = str(tmp_path / "result.svg")
    config = {
        "input_path": sample_color_image,
        "output_path": output,
        "mode": "gradient",
        "color_dark": "#1A1A2E",
        "color_light": "#E94560",
        "levels": 4,
        "threshold": 128,
        "quality": 4,
    }
    run(config)
    result = Path(output).read_text()
    assert "<svg" in result or "<?xml" in result


def test_export_png_gradient_opaque_midtones_transparent_brightest(tmp_path):
    """Brightest quantized band is transparent; other bands are fully opaque."""
    levels = 4
    img = Image.new("L", (4, 1), 0)
    img.putpixel((0, 0), 0)
    img.putpixel((1, 0), 85)
    img.putpixel((2, 0), 170)
    img.putpixel((3, 0), 255)
    png_path = tmp_path / "g.png"
    config = {
        "mode": "gradient",
        "levels": levels,
        "color_dark": "#000000",
        "color_light": "#FFFFFF",
    }
    _export_png(img, config, png_path)
    out = Image.open(png_path).convert("RGBA")
    assert out.getpixel((3, 0))[3] == 0
    assert out.getpixel((1, 0))[3] == 255
    assert out.getpixel((2, 0))[3] == 255


def test_single_pipeline_with_restore_and_blur(sample_bw_image, tmp_path):
    output = str(tmp_path / "result.svg")
    config = {
        "input_path": sample_bw_image,
        "output_path": output,
        "mode": "single",
        "color": "#336699",
        "threshold": 128,
        "quality": 4,
        "restore": "medium",
        "blur": 1.0,
    }
    run(config)
    result = Path(output).read_text()
    assert "<svg" in result or "<?xml" in result
    assert "#336699" in result
