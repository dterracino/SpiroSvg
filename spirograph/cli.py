"""Command line interface for the Spirograph generator."""
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Type

from rich.console import Console
from rich.prompt import FloatPrompt, IntPrompt, Prompt
from rich.table import Table

from .config import SpiroConfig, SpiroType
from .render import build_svg, save_svg


@dataclass(frozen=True)
class Knob:
    """Metadata describing a configurable knob."""

    name: str
    prompt: str
    value_type: Type[object]
    default: object
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    choices: Optional[List[str]] = None


KNOBS: Dict[str, Knob] = {
    "outer_radius": Knob(
        name="outer_radius",
        prompt="Outer radius of the fixed circle",
        value_type=float,
        default=180.0,
        minimum=10.0,
        maximum=400.0,
    ),
    "inner_radius": Knob(
        name="inner_radius",
        prompt="Inner radius of the rolling circle",
        value_type=float,
        default=75.0,
        minimum=5.0,
        maximum=250.0,
    ),
    "pen_offset": Knob(
        name="pen_offset",
        prompt="Distance of the pen from the rolling circle center",
        value_type=float,
        default=40.0,
        minimum=1.0,
        maximum=250.0,
    ),
    "theta_step": Knob(
        name="theta_step",
        prompt="Angle step between points (smaller = smoother)",
        value_type=float,
        default=0.02,
        minimum=0.001,
        maximum=0.2,
    ),
    "cycles": Knob(
        name="cycles",
        prompt="Number of rotations to complete",
        value_type=float,
        default=20.0,
        minimum=1.0,
        maximum=60.0,
    ),
    "stroke_width": Knob(
        name="stroke_width",
        prompt="Stroke width of the curve",
        value_type=float,
        default=2.0,
        minimum=0.1,
        maximum=10.0,
    ),
    "canvas_size": Knob(
        name="canvas_size",
        prompt="Canvas size in pixels",
        value_type=int,
        default=900,
        minimum=200,
        maximum=3000,
    ),
    "stroke_color": Knob(
        name="stroke_color",
        prompt="Stroke color (hex)",
        value_type=str,
        default="#1f77b4",
    ),
    "spiro_type": Knob(
        name="spiro_type",
        prompt="Spirograph type",
        value_type=str,
        default=SpiroType.HYPOTROCHOID.value,
        choices=[member.value for member in SpiroType],
    ),
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Spirograph mandala SVG artwork")
    parser.add_argument("--output", type=Path, help="Path to save the generated SVG")
    parser.add_argument("--design-number", type=int, help="Design number used as the random seed")
    parser.add_argument("--random", action="store_true", help="Generate all knobs randomly")
    for knob in KNOBS.values():
        if knob.name == "spiro_type":
            parser.add_argument(
                f"--{knob.name.replace('_', '-')}",
                choices=knob.choices,
                help=knob.prompt,
            )
        elif knob.value_type is int:
            parser.add_argument(
                f"--{knob.name.replace('_', '-')}",
                type=int,
                help=knob.prompt,
            )
        elif knob.value_type is float:
            parser.add_argument(
                f"--{knob.name.replace('_', '-')}",
                type=float,
                help=knob.prompt,
            )
        else:
            parser.add_argument(
                f"--{knob.name.replace('_', '-')}",
                help=knob.prompt,
            )
    return parser.parse_args()


def _prompt_for_knob(console: Console, knob: Knob) -> object:
    if knob.value_type is float:
        return FloatPrompt.ask(knob.prompt, default=str(knob.default))
    if knob.value_type is int:
        return IntPrompt.ask(knob.prompt, default=int(knob.default))
    if knob.choices:
        default = knob.default if knob.default in knob.choices else knob.choices[0]
        return Prompt.ask(knob.prompt, choices=[str(choice) for choice in knob.choices], default=str(default))
    return Prompt.ask(knob.prompt, default=str(knob.default))


def _validate_range(name: str, value: float, knob: Knob) -> float:
    if knob.minimum is not None and value < knob.minimum:
        raise ValueError(f"{name} must be >= {knob.minimum}")
    if knob.maximum is not None and value > knob.maximum:
        raise ValueError(f"{name} must be <= {knob.maximum}")
    return value


def _normalize_value(name: str, value: object, knob: Knob) -> object:
    if knob.value_type is float:
        value = float(value)
        return _validate_range(name, value, knob)
    if knob.value_type is int:
        value = int(value)
        return _validate_range(name, value, knob)
    if knob.choices:
        if value not in knob.choices:
            raise ValueError(f"Invalid choice {value} for {name}")
        return value
    if name == "stroke_color":
        text = str(value).strip()
        if not text.startswith("#") or len(text) not in {4, 7}:
            raise ValueError("Stroke color must be a hex value like #ff00aa")
        return text.lower()
    return value


def _random_value(knob: Knob, rng: random.Random) -> object:
    if knob.value_type is float:
        assert knob.minimum is not None and knob.maximum is not None
        return round(rng.uniform(knob.minimum, knob.maximum), 4)
    if knob.value_type is int:
        assert knob.minimum is not None and knob.maximum is not None
        return rng.randint(int(knob.minimum), int(knob.maximum))
    if knob.choices:
        return rng.choice(knob.choices)
    if knob.name == "stroke_color":
        return f"#{rng.randint(0, 0xFFFFFF):06x}"
    return knob.default


def _collect_knob_values(args: argparse.Namespace, console: Console, rng: random.Random) -> Dict[str, object]:
    values: Dict[str, object] = {}
    if args.random:
        console.print("[bold green]Random mode enabled[/bold green]")
        for name, knob in KNOBS.items():
            raw_value = _random_value(knob, rng)
            values[name] = _normalize_value(name, raw_value, knob)
    else:
        for name, knob in KNOBS.items():
            cli_value = getattr(args, name)
            if cli_value is not None:
                raw_value = cli_value
            else:
                raw_value = _prompt_for_knob(console, knob)
            values[name] = _normalize_value(name, raw_value, knob)
    return values


def _build_config(values: Dict[str, object]) -> SpiroConfig:
    return SpiroConfig(
        outer_radius=float(values["outer_radius"]),
        inner_radius=float(values["inner_radius"]),
        pen_offset=float(values["pen_offset"]),
        theta_step=float(values["theta_step"]),
        cycles=float(values["cycles"]),
        stroke_width=float(values["stroke_width"]),
        stroke_color=str(values["stroke_color"]),
        canvas_size=int(values["canvas_size"]),
        spiro_type=SpiroType(str(values["spiro_type"]))
    )


def _summarize_config(console: Console, config: SpiroConfig, design_number: int, output_path: Path) -> None:
    table = Table(title="Spirograph Design Summary")
    table.add_column("Knob")
    table.add_column("Value", justify="right")
    table.add_row("Design number", str(design_number))
    table.add_row("Type", config.spiro_type.value)
    table.add_row("Outer radius", f"{config.outer_radius:.2f}")
    table.add_row("Inner radius", f"{config.inner_radius:.2f}")
    table.add_row("Pen offset", f"{config.pen_offset:.2f}")
    table.add_row("Theta step", f"{config.theta_step:.4f}")
    table.add_row("Cycles", f"{config.cycles:.2f}")
    table.add_row("Stroke width", f"{config.stroke_width:.2f}")
    table.add_row("Stroke color", config.stroke_color)
    table.add_row("Canvas size", f"{config.canvas_size}px")
    table.add_row("Output", str(output_path))
    console.print(table)


def _prepare_rng(console: Console, args: argparse.Namespace) -> tuple[random.Random, int]:
    if args.design_number is not None:
        design_number = args.design_number
    elif args.random:
        design_number = random.SystemRandom().randint(1, 2**31 - 1)
        console.print(f"Generated design number [bold]{design_number}[/bold] for this random run")
    else:
        design_number = IntPrompt.ask("Design number (seed)", default=1)
    rng = random.Random(design_number)
    return rng, design_number


def main() -> None:
    args = parse_arguments()
    console = Console()
    rng, design_number = _prepare_rng(console, args)
    values = _collect_knob_values(args, console, rng)
    config = _build_config(values)
    svg = build_svg(config, design_number)
    output_path = save_svg(svg, args.output)
    _summarize_config(console, config, design_number, output_path)


if __name__ == "__main__":
    main()
