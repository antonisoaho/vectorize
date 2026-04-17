# vectorize

Turn a raster image (PNG, JPG, BMP, TIFF, WEBP) into a clean single-color **SVG**. Optionally also export a **transparent PNG**.

---

## Install

Requires **Python 3.10–3.13**.

```bash
git clone https://github.com/antonisoaho/vectorize.git
cd vectorize

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -e .
```

`vectorize` is now on your PATH.

---

## Quick start

```bash
# Walk through prompts (color, restore)
vectorize photo.png

# One-shot: red SVG
vectorize photo.png -c red

# Also drop a transparent PNG next to the SVG
vectorize photo.png -c "#336699" --png
```

---

## Options

| Flag              | What it does                                          | Default     |
| ----------------- | ----------------------------------------------------- | ----------- |
| `-o, --output`    | Output SVG path                                       | `input.svg` |
| `-c, --color`     | Hex (`#FF0000`) or name (`red`, `navy`…)              | prompt      |
| `-t, --threshold` | Black/white cutoff, `0`–`255`                         | `128`       |
| `-q, --quality`   | Speckle filter. `1` = most detail, `10` = cleanest    | `4`         |
| `--blur`          | Soften edges before tracing (`0.0`–`10.0`)            | `0`         |
| `--restore`       | Repair damaged logos: `none`/`light`/`medium`/`heavy` | `none`      |
| `--png`           | Also export transparent PNG                           | off         |
| `-I`              | Skip all prompts (use defaults)                       | —           |

**Color names:** `black`, `white`, `red`, `blue`, `navy`, `forest`, `orange`, `purple`.

---

## Examples

**Black logo:**

```bash
vectorize logo.png -c black
```

**Custom color + transparent PNG:**

```bash
vectorize portrait.jpg -c "#1a1a2e" --png
```

**Repair a scuffed scan:**

```bash
vectorize scuffed-logo.png -c black --restore heavy --blur 1.0
```

**Scripted (no prompts):**

```bash
vectorize input.png -c red -I
```

---

## How it works

1. Load image → grayscale.
2. Optional blur.
3. Threshold to pure black & white.
4. Optional restore (fills pinholes, removes speckle).
5. Trace with [vtracer](https://github.com/visioncortex/vtracer).
6. Swap path fill to your color → write SVG (and optional PNG).

---

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

## License

MIT
