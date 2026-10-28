"""Layout tokens — spacing, radius, motion, breakpoints."""
from __future__ import annotations

import flet as ft


class Space:
    xs = 4
    sm = 8
    md = 16
    lg = 24
    xl = 32
    xxl = 48


class Radius:
    sm = 6
    md = 8
    lg = 10
    xl = 12
    xxl = 16
    pill = 999


class Motion:
    """Animation durations in milliseconds."""
    fast_ms = 150
    base_ms = 200
    slow_ms = 300

    @staticmethod
    def fast():
        return ft.Animation(Motion.fast_ms, ft.AnimationCurve.EASE_OUT)

    @staticmethod
    def base():
        return ft.Animation(Motion.base_ms, ft.AnimationCurve.EASE_IN_OUT)

    @staticmethod
    def slow():
        return ft.Animation(Motion.slow_ms, ft.AnimationCurve.EASE_IN_OUT)

    @staticmethod
    def spring():
        return ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC)


class BP:
    xs = 576
    sm = 576
    md = 768
    lg = 992
    xl = 1200


def content_max_for(width: int) -> int | None:
    if width >= BP.xl:
        return 960
    if width >= BP.lg:
        return 880
    if width >= BP.md:
        return 720
    if width >= BP.sm:
        return 540
    return None
