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
def sample_jpg_image(tmp_path):
    img = Image.new("RGB", (50, 50), (100, 100, 100))
    path = tmp_path / "sample.jpg"
    img.save(path, format="JPEG")
    return str(path)
