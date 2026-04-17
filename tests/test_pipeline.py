from pathlib import Path

from vectorize.pipeline import run


def test_single_color_pipeline(sample_bw_image, tmp_path):
    output = str(tmp_path / "result.svg")
    config = {
        "input_path": sample_bw_image,
        "output_path": output,
        "color": "#336699",
        "threshold": 128,
        "quality": 4,
    }
    run(config)
    result = Path(output).read_text()
    assert "<svg" in result or "<?xml" in result
    assert "#336699" in result


def test_single_pipeline_with_restore_and_blur(sample_bw_image, tmp_path):
    output = str(tmp_path / "result.svg")
    config = {
        "input_path": sample_bw_image,
        "output_path": output,
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
