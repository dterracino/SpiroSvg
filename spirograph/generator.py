"""Spirograph curve generation utilities."""
from __future__ import annotations

import math
from typing import List, Sequence, Tuple

from .config import SpiroConfig, SpiroType

Point = Tuple[float, float]


def _hypotrochoid_point(theta: float, config: SpiroConfig) -> Point:
    r, R, d = config.inner_radius, config.outer_radius, config.pen_offset
    k = R - r
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    angle_multiplier = k / r
    return (
        k * cos_theta + d * math.cos(angle_multiplier * theta),
        k * sin_theta - d * math.sin(angle_multiplier * theta),
    )


def _epitrochoid_point(theta: float, config: SpiroConfig) -> Point:
    r, R, d = config.inner_radius, config.outer_radius, config.pen_offset
    k = R + r
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    angle_multiplier = k / r
    return (
        k * cos_theta - d * math.cos(angle_multiplier * theta),
        k * sin_theta - d * math.sin(angle_multiplier * theta),
    )


def generate_points(config: SpiroConfig) -> List[Point]:
    """Generate all points for the configured Spirograph curve."""

    total_angle = 2 * math.pi * config.cycles
    steps = max(1, int(total_angle / config.theta_step))
    points: List[Point] = []
    for index in range(steps + 1):
        theta = index * config.theta_step
        if config.spiro_type is SpiroType.HYPOTROCHOID:
            point = _hypotrochoid_point(theta, config)
        else:
            point = _epitrochoid_point(theta, config)
        points.append(point)
    return points


def scale_points(points: Sequence[Point], config: SpiroConfig) -> List[Point]:
    """Scale raw curve points to fit inside the configured canvas."""

    if not points:
        return []

    min_extent, max_extent = config.extent()
    span = max_extent - min_extent
    if math.isclose(span, 0.0):
        span = max(config.outer_radius, 1.0)
    half_canvas = config.canvas_size / 2
    scale = half_canvas / max(span / 2, 1.0)

    scaled: List[Point] = []
    for x, y in points:
        scaled.append((half_canvas + x * scale, half_canvas + y * scale))
    return scaled


def points_to_path(points: Sequence[Point]) -> str:
    """Convert a sequence of points into an SVG path string."""

    if not points:
        raise ValueError("Cannot build a path from an empty sequence of points")

    iterator = iter(points)
    first = next(iterator)
    segments = [f"M {first[0]:.3f} {first[1]:.3f}"]
    segments.extend(f"L {x:.3f} {y:.3f}" for x, y in iterator)
    return " ".join(segments)


def generate_path(config: SpiroConfig) -> str:
    """Generate a scaled SVG path for the provided configuration."""

    points = generate_points(config)
    scaled_points = scale_points(points, config)
    return points_to_path(scaled_points)
