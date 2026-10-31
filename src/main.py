"""BitBeagle — Flet entry point."""
from __future__ import annotations

import flet as ft

from bitbeagle.app import main


if __name__ == "__main__":
    ft.run(main)
