# vectorize

A CLI tool that converts raster images (PNG, JPG, BMP, TIFF, WEBP) into clean SVG vector graphics. Converts images to black & white, traces the shapes, and lets you choose between single-color or gradient output with custom colors.

Optionally exports a PNG with a transparent background alongside the SVG.

## Installation

Requires Python 3.10+.

```bash
pip install -e .
```

## Quick start

```bash
# Interactive mode — walks you through mode and color choices
vectorize photo.png

# Single color (red) with default settings
vectorize photo.png -c red

# Gradient from navy to orange, 4 tone levels
vectorize photo.png -g --color-dark navy --color-light orange --levels 4

# Also export a transparent PNG
vectorize photo.png -c "#336699" --png
```

## Usage

```
vectorize [OPTIONS] INPUT_IMAGE
```

### Arguments

| Argument      | Description                              |
|---------------|------------------------------------------|
| `INPUT_IMAGE` | Path to the source image (PNG, JPG, etc) |

### Options

| Option                          | Description                                         | Default     |
|---------------------------------|-----------------------------------------------------|-------------|
| `-o`, `--output PATH`           | Output SVG path                                     | `input.svg` |
| `-c`, `--color TEXT`            | Single-color mode with hex color or name             | —           |
| `-g`, `--gradient`              | Enable gradient/multi-tone mode                      | off         |
| `--color-dark TEXT`             | Dark end of gradient                                 | `#000000`   |
| `--color-light TEXT`            | Light end of gradient                                | `#FFFFFF`   |
| `--levels INT`                  | Number of gradient tone levels (2–8)                 | `4`         |
| `-t`, `--threshold INT`         | Black & white cutoff (0–255)                         | `128`       |
| `-q`, `--quality INT`           | Speckle filter — 1 = max detail, 10 = cleanest       | `4`         |
| `--png`                         | Also export a PNG with transparent background        | off         |
| `-i` / `-I`                     | Force interactive mode on / off                       | auto        |

### Mode selection

The tool has two vectorization modes:

- **Single color** — produces an SVG where all foreground shapes use one flat color. Activated with `-c` or by choosing "single" in interactive mode.
- **Gradient** — quantizes the image into multiple tone levels and maps them to a color gradient between two endpoints. Activated with `-g` or by choosing "gradient" in interactive mode.

If you run `vectorize` with no mode flags, it enters **interactive mode** and prompts you to choose.

### Color input

Colors can be specified as:

- Hex codes: `#FF0000`, `#f00`, `FF0000`
- Preset names: `black`, `white`, `red`, `blue`, `navy`, `forest`, `orange`, `purple`

### Threshold & quality

- **Threshold** (`-t`) controls the black/white cutoff when converting the image. Lower values keep more detail as black; higher values keep less. Only affects single-color mode.
- **Quality** (`-q`) controls the speckle filter. Lower values preserve fine detail (noisier SVG), higher values produce cleaner shapes with fewer paths.

## Examples

**Basic single-color vectorization:**

```bash
vectorize logo.png -c black
# -> logo.svg
```

**Custom color with PNG export:**

```bash
vectorize portrait.jpg -c "#1a1a2e" --png -o artwork.svg
# -> artwork.svg + artwork.png (transparent background)
```

**Gradient with custom colors and 6 tone levels:**

```bash
vectorize landscape.jpg -g --color-dark "#0d1b2a" --color-light "#e0e1dd" --levels 6
# -> landscape.svg
```

**Fine-tuning with threshold and quality:**

```bash
vectorize scan.png -c navy -t 100 -q 2 --png
# Low threshold (more black), high detail (quality 2)
```

**Non-interactive mode for scripts:**

```bash
vectorize input.png -I
# Uses defaults: single color, black, no PNG
```

## How it works

1. **Load** — reads the raster image and validates the format
2. **Preprocess** — converts to grayscale, then applies thresholding (single-color) or quantization (gradient)
3. **Trace** — runs [vtracer](https://github.com/visioncortex/vtracer) to convert pixel data into vector paths
4. **Recolor** — replaces path fill colors in the SVG with your chosen color(s)
5. **Export** — writes the SVG (and optionally a transparent PNG)

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## Project structure

```
src/vectorize/
  cli.py              # Click CLI entry point and interactive prompts
  pipeline.py         # Orchestrates the full conversion pipeline
  preprocessing.py    # Image loading, validation, B&W conversion
  svg_processing.py   # SVG parsing and color replacement
  colors.py           # Hex validation, presets, color interpolation
```

## License

MIT
