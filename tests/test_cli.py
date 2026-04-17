from click.testing import CliRunner

from vectorize.cli import main


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Convert a raster image" in result.output


def test_single_color_mode(sample_bw_image, tmp_path):
    output = str(tmp_path / "out.svg")
    runner = CliRunner()
    result = runner.invoke(main, [sample_bw_image, "-o", output, "-c", "#FF0000", "-I"])
    assert result.exit_code == 0, result.output
    with open(output) as f:
        svg = f.read()
    assert "<svg" in svg or "<?xml" in svg


def test_default_output_path(sample_bw_image):
    runner = CliRunner()
    result = runner.invoke(main, [sample_bw_image, "-c", "#000000", "-I"])
    assert result.exit_code == 0, result.output


def test_named_color(sample_bw_image, tmp_path):
    output = str(tmp_path / "out.svg")
    runner = CliRunner()
    result = runner.invoke(main, [sample_bw_image, "-o", output, "-c", "red", "-I"])
    assert result.exit_code == 0, result.output


def test_png_export(sample_bw_image, tmp_path):
    output = str(tmp_path / "out.svg")
    png_output = str(tmp_path / "out.png")
    runner = CliRunner()
    result = runner.invoke(main, [sample_bw_image, "-o", output, "-c", "#000000", "--png", "-I"])
    assert result.exit_code == 0, result.output
    assert "Saved PNG" in result.output
    with open(png_output, "rb") as f:
        header = f.read(8)
    assert header[:4] == b"\x89PNG"


def test_blur_and_restore_flags(sample_bw_image, tmp_path):
    output = str(tmp_path / "out.svg")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            sample_bw_image,
            "-o",
            output,
            "-c",
            "#000000",
            "-I",
            "--blur",
            "2",
            "--restore",
            "light",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Applying blur" in result.output
    assert "Restoring" in result.output
    with open(output) as f:
        svg = f.read()
    assert "<svg" in svg or "<?xml" in svg
