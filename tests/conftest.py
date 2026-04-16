import pytest
from PIL import Image


@pytest.fixture
def sample_bw_image(tmp_path):
    img = Image.new("L", (50, 50), 255)
    for x in range(15, 35):
        for y in range(15, 35):
            img.putpixel((x, y), 0)
    path = tmp_path / "sample.png"
    img.save(path)
    return str(path)


@pytest.fixture
def sample_color_image(tmp_path):
    img = Image.new("RGB", (50, 50), (200, 200, 200))
    for x in range(0, 25):
        for y in range(0, 50):
            img.putpixel((x, y), (50, 50, 50))
    path = tmp_path / "sample_color.png"
    img.save(path)
    return str(path)


@pytest.fixture
def sample_jpg_image(tmp_path):
    img = Image.new("RGB", (50, 50), (100, 100, 100))
    path = tmp_path / "sample.jpg"
    img.save(path, format="JPEG")
    return str(path)
