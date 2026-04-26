# vectorize

**What it does:** CLI that turns a raster logo or graphic into a **single-color SVG** (grayscale → threshold → [vtracer](https://github.com/visioncortex/vtracer) trace, then recolor paths). Optional **transparent PNG** export and **restore** presets for noisy scans.

**Prerequisites:** **Python 3.10–3.13** (3.14+ excluded: vtracer wheels are unreliable there). A normal `pip install` pulls the rest (Pillow, Click, lxml, vtracer).

## Install

```bash
git clone https://github.com/antonisoaho/vectorize.git
cd vectorize
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

## Usage

```bash
vectorize image.png                    # prompts: color, then restore strength
vectorize image.png -c red             # no prompts; restore defaults to none
vectorize image.png -c "#336699" --png
vectorize image.png -I                 # scripted: black, no restore, no prompts
```

Run `vectorize --help` for flags (`-o`, `-t`, `-q`, `--blur`, `--restore`, `-i`/`-I`, etc.). Supported inputs: PNG, JPEG, BMP, TIFF, WEBP, GIF.

## Development

```bash
pip install -e ".[dev]" && pytest -v
```

MIT
