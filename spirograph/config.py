"""Configuration models for the Spirograph generator."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class SpiroType(str, Enum):
    """Type of spirograph curve to generate."""

    HYPOTROCHOID = "hypotrochoid"
    EPITROCHOID = "epitrochoid"


@dataclass(frozen=True)
class SpiroConfig:
    """All knobs that control the Spirograph design."""

    outer_radius: float
    inner_radius: float
    pen_offset: float
    theta_step: float
    cycles: float
    stroke_width: float
    stroke_color: str
    canvas_size: int
    spiro_type: SpiroType

    def extent(self) -> Tuple[float, float]:
        """Return a tuple containing the min and max radius for scaling."""

        if self.spiro_type is SpiroType.HYPOTROCHOID:
            return (self.outer_radius - self.inner_radius - self.pen_offset,
                    self.outer_radius + self.pen_offset)
        return (0, self.outer_radius + self.inner_radius + self.pen_offset)
