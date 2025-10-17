# SpiroSvg

SpiroSvg is a small Python utility that creates colourful spirograph-inspired mandala artwork as scalable vector graphics (SVG). The project provides a command line interface for configuring the curve geometry, interactively tweaking parameters, and exporting the final design as an SVG file.

## Features

- Generates both **hypotrochoid** and **epitrochoid** style curves.
- Interactive prompts with sensible defaults for every "knob" that controls the design.
- Optional random mode for quickly exploring new combinations.
- Deterministic output when a design number (random seed) is supplied.
- Produces ready-to-share SVG files with metadata and consistent sizing.

## Project structure

```text
├── main.py              # Console entry point (`python -m spirograph`)
├── requirements.txt     # Runtime dependencies
└── spirograph/
    ├── __init__.py
    ├── cli.py           # Command line interface logic and prompts
    ├── config.py        # Data models describing the spirograph configuration
    ├── generator.py     # Curve generation and scaling utilities
    └── render.py        # SVG rendering helpers
```

## Installation

1. Ensure you are using Python 3.9 or newer.
2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\\Scripts\\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

You can run the tool either through the module entry point or the `main.py` helper script. Both options launch the same CLI experience.

```bash
python -m spirograph
# or
python main.py
```

### Choosing parameters interactively

Running the command without arguments opens an interactive session that walks through each configurable knob. Defaults are shown in brackets, so you can simply press <kbd>Enter</kbd> to accept them. At the end of the run an SVG file such as `spirograph-20240101-120000.svg` will be written to the current directory, and a summary table of the design will be displayed.

### Command line arguments

Every knob can also be supplied via command line flags. This is useful for scripting or re-running favourite designs.

```bash
python -m spirograph \
  --design-number 1337 \
  --outer-radius 180 \
  --inner-radius 75 \
  --pen-offset 40 \
  --theta-step 0.02 \
  --cycles 20 \
  --stroke-width 2 \
  --stroke-color "#1f77b4" \
  --canvas-size 900 \
  --spiro-type hypotrochoid \
  --output my-design.svg
```

### Random designs

To let the tool pick values for you, enable random mode. A randomly generated design number is printed so you can reproduce the result later by passing it back via `--design-number`.

```bash
python -m spirograph --random
```

### Reusing designs

Design numbers double as seeds for the random number generator. Re-running the tool with the same design number and options will always generate the same artwork. This makes it easy to share interesting combinations with collaborators.

## Development

The codebase is intentionally small and dependency-light. The key modules to explore are:

- `spirograph/generator.py` for the mathematical curve generation.
- `spirograph/render.py` for serialising those curves into SVG paths.
- `spirograph/cli.py` for command line orchestration.

Pull requests and experiments are welcome! Feel free to fork the repository, tweak parameters, or extend the renderer with gradients and fill effects.
