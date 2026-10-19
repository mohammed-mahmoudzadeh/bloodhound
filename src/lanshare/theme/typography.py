"""Typography — Inter, no height/letter_spacing (Flet 1.0.x compat)."""
from __future__ import annotations

import flet as ft


class Type:
    family = "Inter"

    # Display
    display_lg = dict(size=42, weight=ft.FontWeight.W_700)
    display_md = dict(size=32, weight=ft.FontWeight.W_700)
    display_sm = dict(size=26, weight=ft.FontWeight.W_600)

    # Headlines
    headline_lg = dict(size=24, weight=ft.FontWeight.W_600)
    headline_md = dict(size=20, weight=ft.FontWeight.W_600)
    headline_sm = dict(size=18, weight=ft.FontWeight.W_600)

    # Titles
    title_lg = dict(size=16, weight=ft.FontWeight.W_600)
    title_md = dict(size=14, weight=ft.FontWeight.W_600)
    title_sm = dict(size=13, weight=ft.FontWeight.W_600)

    # Body
    body_lg = dict(size=15, weight=ft.FontWeight.W_400)
    body_md = dict(size=14, weight=ft.FontWeight.W_400)
    body_sm = dict(size=13, weight=ft.FontWeight.W_400)

    # Labels
    label_lg = dict(size=13, weight=ft.FontWeight.W_500)
    label_md = dict(size=12, weight=ft.FontWeight.W_500)
    label_sm = dict(size=11, weight=ft.FontWeight.W_500)
