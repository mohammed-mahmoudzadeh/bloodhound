"""Typography — Inter, no height/letter_spacing (Flet 1.0.x compat)."""
from __future__ import annotations

import flet as ft


class Type:
    family = "Inter"

    # Display
    display_lg = dict(size=42, weight=ft.FontWeight.W_700, font_family=family)
    display_md = dict(size=32, weight=ft.FontWeight.W_700, font_family=family)
    display_sm = dict(size=26, weight=ft.FontWeight.W_600, font_family=family)

    # Headlines
    headline_lg = dict(size=24, weight=ft.FontWeight.W_600, font_family=family)
    headline_md = dict(size=20, weight=ft.FontWeight.W_600, font_family=family)
    headline_sm = dict(size=18, weight=ft.FontWeight.W_600, font_family=family)

    # Titles
    title_lg = dict(size=16, weight=ft.FontWeight.W_600, font_family=family)
    title_md = dict(size=15, weight=ft.FontWeight.W_600, font_family=family)
    title_sm = dict(size=14, weight=ft.FontWeight.W_600, font_family=family)

    # Body
    body_lg = dict(size=15, weight=ft.FontWeight.W_400, font_family=family)
    body_md = dict(size=14, weight=ft.FontWeight.W_400, font_family=family)
    body_sm = dict(size=13, weight=ft.FontWeight.W_400, font_family=family)

    # Labels
    label_lg = dict(size=13, weight=ft.FontWeight.W_500, font_family=family)
    label_md = dict(size=12, weight=ft.FontWeight.W_500, font_family=family)
    label_sm = dict(size=11, weight=ft.FontWeight.W_500, font_family=family)