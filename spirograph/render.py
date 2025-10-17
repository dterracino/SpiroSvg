"""Rendering utilities for creating SVG documents."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import SpiroConfig
from .generator import generate_path

SVG_TEMPLATE = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{size}\" height=\"{size}\" viewBox=\"0 0 {size} {size}\">
  <title>Spirograph Design {design_number}</title>
  <desc>Generated on {timestamp}</desc>
  <rect x=\"0\" y=\"0\" width=\"{size}\" height=\"{size}\" fill=\"white\" />
  <path d=\"{path}\" fill=\"none\" stroke=\"{stroke_color}\" stroke-width=\"{stroke_width}\" stroke-linecap=\"round\" stroke-linejoin=\"round\" />
</svg>
"""


def build_svg(config: SpiroConfig, design_number: int) -> str:
    """Build the SVG document for the provided configuration."""

    path = generate_path(config)
    return SVG_TEMPLATE.format(
        size=config.canvas_size,
        path=path,
        stroke_color=config.stroke_color,
        stroke_width=config.stroke_width,
        timestamp=datetime.utcnow().isoformat(timespec="seconds"),
        design_number=design_number,
    )


def save_svg(svg_content: str, output: Optional[Path]) -> Path:
    """Persist the SVG document to disk, returning the output path."""

    if output is None:
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        output = Path(f"spirograph-{timestamp}.svg")
    output_path = output if isinstance(output, Path) else Path(output)
    output_path.write_text(svg_content, encoding="utf-8")
    return output_path
