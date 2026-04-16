import pytest
from PIL import Image

from vectorize.preprocessing import (
    convert_to_bw,
    convert_to_grayscale,
    image_to_bytes,
    load_and_validate,
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


def test_convert_to_grayscale_levels():
    img = Image.new("RGB", (10, 10), (128, 128, 128))
    gray = convert_to_grayscale(img, levels=4)
    assert gray.mode == "L"
    unique = set(gray.getdata())
    assert len(unique) >= 1
    assert len(unique) <= 4


def test_image_to_bytes():
    img = Image.new("L", (10, 10), 0)
    data = image_to_bytes(img)
    assert isinstance(data, bytes)
    assert data[:4] == b"\x89PNG"  # PNG magic bytes
