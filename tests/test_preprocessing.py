import pytest
from PIL import Image

from vectorize.preprocessing import (
    apply_blur,
    convert_to_bw,
    image_to_bytes,
    load_and_validate,
    restore_image,
)


def test_load_and_validate_png(sample_bw_image):
    img = load_and_validate(sample_bw_image)
    assert img.mode == "RGB"
    assert img.size == (50, 50)


def test_load_and_validate_jpg(sample_jpg_image):
    img = load_and_validate(sample_jpg_image)
    assert img.mode == "RGB"


def test_load_and_validate_invalid(tmp_path):
    bad = tmp_path / "bad.txt"
    bad.write_text("not an image")
    with pytest.raises(Exception):
        load_and_validate(str(bad))


def test_convert_to_bw():
    img = Image.new("RGB", (10, 10), (100, 100, 100))
    bw = convert_to_bw(img, threshold=128)
    assert bw.mode == "L"
    pixels = list(bw.getdata())
    assert all(p in (0, 255) for p in pixels)
    assert all(p == 0 for p in pixels)  # 100 < 128 → all black


def test_convert_to_bw_threshold():
    img = Image.new("RGB", (10, 10), (200, 200, 200))
    bw = convert_to_bw(img, threshold=128)
    pixels = list(bw.getdata())
    assert all(p == 255 for p in pixels)  # 200 > 128 → all white


def test_image_to_bytes():
    img = Image.new("L", (10, 10), 0)
    data = image_to_bytes(img)
    assert isinstance(data, bytes)
    assert data[:4] == b"\x89PNG"  # PNG magic bytes


def test_apply_blur_zero_is_identity():
    img = Image.new("L", (12, 12), 42)
    out = apply_blur(img, 0.0)
    assert list(out.getdata()) == list(img.getdata())


def test_apply_blur_positive_softens():
    img = Image.new("L", (30, 30), 0)
    for x in range(15, 30):
        for y in range(30):
            img.putpixel((x, y), 255)
    out = apply_blur(img, 2.0)
    mid = [out.getpixel((x, 15)) for x in range(12, 18)]
    assert any(v not in (0, 255) for v in mid)


def test_restore_none_is_identity():
    img = Image.new("L", (8, 8), 99)
    out = restore_image(img, "none")
    assert list(out.getdata()) == list(img.getdata())


def test_restore_fills_small_hole():
    img = Image.new("L", (32, 32), 0)
    for x in range(14, 18):
        for y in range(14, 18):
            img.putpixel((x, y), 255)
    out = restore_image(img, "medium")
    assert out.getpixel((15, 15)) == 0


def test_restore_removes_speckle():
    img = Image.new("L", (20, 20), 0)
    img.putpixel((10, 10), 255)
    out = restore_image(img, "medium")
    assert out.getpixel((10, 10)) == 0


def test_restore_invalid_strength_raises():
    img = Image.new("L", (4, 4), 0)
    with pytest.raises(ValueError, match="restore strength"):
        restore_image(img, "bogus")
