"""Activity — full log history, structured."""
from __future__ import annotations

import flet as ft

from ..theme import Space, Type
from ..components import SectionCard, LogRow
from ._scaffold import page_scaffold


def build_activity(P, state, handlers, page_width=1200):
    entries = list(reversed(state.logs))

    if entries:
        rows = [LogRow(P, e.time, e.message, e.level) for e in entries]
        list_content = ft.Column(
            rows,
            spacing=Space.sm,
            tight=True,
        )
    else:
        list_content = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, size=32,
                            color=P["text_faint"]),
                    ft.Container(height=Space.sm),
                    ft.Text("No activity yet.",
                            color=P["text_muted"],
                            **Type.body_sm),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            padding=ft.Padding.symmetric(vertical=Space.xl),
            alignment=ft.Alignment.CENTER,
        )

    log_card = SectionCard(
        P, dark=state.dark,
        title="All Activity",
        subtitle=f"{len(entries)} entries",
        content=list_content,
    )

    body = ft.Column(
        [log_card],
        spacing=0,
        tight=True,
    )

    return page_scaffold(
        P,
        title="Activity",
        subtitle="Server log history",
        content=body,
        page_width=page_width,
    )
