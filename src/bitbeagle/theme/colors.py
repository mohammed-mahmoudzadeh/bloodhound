"""Color tokens — flat, professional, WCAG AA compliant."""
from __future__ import annotations

import flet as ft


def build_palette(dark: bool) -> dict:
    """Semantic palette — matches the web UI exactly (Monochrome)."""
    if dark:
        return {
            # Surfaces
            "bg":             "#000000",
            "surface":        "#0a0a0a",
            "surface_2":      "#141414",
            "surface_3":      "#1f1f1f",
            "surface_hover":  "#1a1a1a",
            # Borders
            "border":         "#1f1f1f",
            "border_soft":    "#141414",
            "border_strong":  "#2e2e2e",
            # Text
            "text":           "#fafafa",
            "text_dim":       "#d4d4d8",
            "text_muted":     "#71717a",
            "text_faint":     "#52525b",
            # Accent (Monochrome: White in dark mode)
            "primary":        "#fafafa",
            "primary_hover":  "#d4d4d8",
            "primary_bg":     "#1f1f1f",
            "on_primary":     "#000000",
            # Status
            "success":        "#fafafa",
            "success_bg":     "#1f1f1f",
            "error":          "#f87171",
            "error_bg":       "#3b0a0a",
            "warning":        "#fbbf24",
            "warning_bg":     "#3b2a05",
            "info":           "#60a5fa",
            "info_bg":        "#082f49",
            "status_online":  "#fafafa",
            "status_offline": "#71717a",
            # Misc
            "shadow":         "#000000",
        }
    return {
        "bg":             "#ffffff",
        "surface":        "#fafafa",
        "surface_2":      "#f4f4f5",
        "surface_3":      "#e4e4e7",
        "surface_hover":  "#f1f1f3",
        "border":         "#e4e4e7",
        "border_soft":    "#efeff3",
        "border_strong":  "#d4d4d8",
        "text":           "#18181b",
        "text_dim":       "#3f3f46",
        "text_muted":     "#71717a",
        "text_faint":     "#a1a1aa",
        # Accent (Monochrome: Black in light mode)
        "primary":        "#18181b",
        "primary_hover":  "#3f3f46",
        "primary_bg":     "#f4f4f5",
        "on_primary":     "#ffffff",
        "success":        "#18181b",
        "success_bg":     "#f4f4f5",
        "error":          "#dc2626",
        "error_bg":       "#fef2f2",
        "warning":        "#d97706",
        "warning_bg":     "#fffbeb",
        "info":           "#0284c7",
        "info_bg":        "#f0f9ff",
        "status_online":  "#18181b",
        "status_offline": "#a1a1aa",
        "shadow":         "#000000",
    }

def card_shadow(dark: bool):
    return None