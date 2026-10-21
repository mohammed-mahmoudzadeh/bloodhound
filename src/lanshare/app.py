"""Flet application — UI shell. Business logic untouched."""
from __future__ import annotations

import atexit
import os
import signal
import threading
import time
from pathlib import Path
from typing import Callable, Dict

import flet as ft

from .config import (
    IS_ANDROID,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)
from .state import AppState
from .theme import BP, Space, Radius, build_palette
from .components import (
    AppBar, NavBar, NavSidebar, StatusChip, IconActionButton,
    SecondaryButton,
)
from .core.network import get_all_ips, get_primary_ip
from .core.server import FlaskServer
from .views import build_view


def run():
    ft.run(main)


def main(page: ft.Page):
    # ============================================================
    # HIDE the system title bar BEFORE anything else.
    # ============================================================
    if not IS_ANDROID:
        try:
            page.window.title_bar_hidden = True
            page.window.title_bar_buttons_hidden = True
        except Exception:
            pass
        try:
            page.window.width = WINDOW_DEFAULT_WIDTH
            page.window.height = WINDOW_DEFAULT_HEIGHT
            page.window.min_width = WINDOW_MIN_WIDTH
            page.window.min_height = WINDOW_MIN_HEIGHT
        except Exception:
            pass

    _configure_page(page)

    state = AppState()
    server = FlaskServer(port=8000)

    # ============================================================
    # SPLASH ICON — path first, embedded base64 fallback
    # ============================================================
    splash_icon_path = None

    _here = Path(__file__).resolve()
    _icon_candidates = [
        _here.parent.parent.parent / "assets" / "icon.png",
        _here.parent.parent / "assets" / "icon.png",
        Path.cwd() / "assets" / "icon.png",
        Path.cwd() / "src" / "assets" / "icon.png",
    ]
    for _p in _icon_candidates:
        if _p.is_file():
            splash_icon_path = str(_p)
            break

    if splash_icon_path is None:
        try:
            from .core.qr import image_as_data_uri
            data_uri = image_as_data_uri("icon.png")
            if data_uri:
                splash_icon_path = data_uri
        except Exception:
            splash_icon_path = None

    if splash_icon_path is not None:
        splash_icon = ft.Image(
            src=splash_icon_path,
            width=140,
            height=140,
        )
    else:
        splash_icon = ft.Icon(
            ft.Icons.FOLDER_SHARED_ROUNDED,
            size=120,
            color="#FACC15",
        )

    splash_layer = ft.Container(
        content=ft.Column(
            [
                splash_icon,
                ft.Container(height=20),
                ft.Text(
                    "LANShare",
                    size=32,
                    weight=ft.FontWeight.W_700,
                    color="#FAFAFA",
                ),
                ft.Container(height=6),
                ft.Text(
                    "Share files over your local network",
                    size=14,
                    color="#71717A",
                ),
            ],
            spacing=0,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#000000",
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    splash_state = {"removed": False}

    # ---- Theme holder ----
    theme_holder = {
        "mode": "auto",
        "system_dark": _system_is_dark(page),
        "P": None,
    }

    def current_dark() -> bool:
        m = theme_holder["mode"]
        if m == "dark":
            return True
        if m == "light":
            return False
        return theme_holder["system_dark"]

    def P() -> dict:
        if theme_holder["P"] is None:
            theme_holder["P"] = build_palette(current_dark())
        return theme_holder["P"]

    def refresh_palette():
        theme_holder["P"] = build_palette(current_dark())
        state.dark = current_dark()

    refresh_palette()

    top_pad = 28 if IS_ANDROID else 0

    # ============================================================
    # Warm-up pyjnius on the main thread (Android only)
    # ============================================================
    if IS_ANDROID:
        try:
            from jnius import autoclass
            autoclass("android.media.MediaMetadataRetriever")
            autoclass("android.provider.Settings")
            autoclass("android.os.PowerManager")
        except Exception:
            pass

    # ============================================================
    # Services — file picker + permission handler
    # ============================================================
    file_picker = ft.FilePicker()

    ph = None
    try:
        from .core.permissions import build_handler
        ph = build_handler()
    except Exception:
        ph = None

    for svc in [file_picker, ph]:
        if svc is None:
            continue
        try:
            page.services.append(svc)
        except Exception:
            try:
                page.overlay.append(svc)
            except Exception:
                pass

    # ---- Helpers ----
    def safe_update():
        try:
            page.update()
        except Exception:
            pass

    def run_async(fn, *args, **kwargs):
        try:
            page.run_task(fn, *args, **kwargs)
        except Exception:
            threading.Thread(
                target=lambda: fn(*args, **kwargs), daemon=True).start()

    def log(message: str, level: str = "info"):
        state.add_log(_now(), message, level)

    # ---- Auto-shutdown ----
    def shutdown_server():
        try:
            if server.is_alive():
                server.stop()
                state.server_running = False
        except Exception:
            pass

    atexit.register(shutdown_server)

    # ---- Window controls ----
    def on_minimize(e=None):
        try:
            page.window.minimized = True
        except Exception:
            try:
                page.window.minimize()
            except Exception:
                pass

    def on_maximize(e=None):
        try:
            if page.window.maximized:
                page.window.maximized = False
            else:
                page.window.maximized = True
        except Exception:
            try:
                page.window.maximize()
            except Exception:
                pass

    async def _close_window_async():
        for method_name in ("destroy", "close", "exit_app"):
            try:
                method = getattr(page.window, method_name, None)
                if method is None:
                    continue
                result = method()
                if hasattr(result, "__await__"):
                    await result
                return
            except Exception:
                continue

    def on_close(e=None):
        shutdown_server()
        try:
            page.run_task(_close_window_async)
        except Exception:
            try:
                page.window.destroy()
            except Exception:
                try:
                    page.window.close()
                except Exception:
                    pass

    def _window_controls() -> ft.Control:
        def _btn(icon, on_click, tooltip, hover_color):
            c = ft.Container(
                content=ft.Icon(icon, size=16, color=P()["text_dim"]),
                width=36, height=36,
                border_radius=Radius.md,
                alignment=ft.Alignment.CENTER,
                ink=True,
                tooltip=tooltip,
                on_click=on_click,
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            )
            def _on_hover(e):
                try:
                    c.bgcolor = (
                        hover_color if e.data == "true" else "transparent"
                    )
                    c.update()
                except Exception:
                    pass
            c.on_hover = _on_hover
            return c

        return ft.Row(
            [
                _btn(ft.Icons.REMOVE_ROUNDED,
                     on_minimize, "Minimize", P()["surface_2"]),
                _btn(ft.Icons.CROP_SQUARE_ROUNDED,
                     on_maximize, "Maximize", P()["surface_2"]),
                _btn(ft.Icons.CLOSE_ROUNDED,
                     on_close, "Close", "#e81123"),
            ],
            spacing=0,
            tight=True,
        )

    # ---- Theme ----
    def set_theme(mode: str):
        if mode not in ("auto", "light", "dark"):
            return
        theme_holder["mode"] = mode
        refresh_palette()
        page.theme_mode = (
            ft.ThemeMode.DARK if current_dark() else ft.ThemeMode.LIGHT
        )
        render()

    def cycle_theme(e=None):
        order = ["auto", "light", "dark"]
        cur = theme_holder["mode"]
        nxt = order[(order.index(cur) + 1) % len(order)]
        set_theme(nxt)

    def _theme_icon() -> tuple[str, str]:
        m = theme_holder["mode"]
        if m == "auto":
            return ft.Icons.BRIGHTNESS_AUTO_ROUNDED, "Theme: Auto (system)"
        if m == "light":
            return ft.Icons.LIGHT_MODE_ROUNDED, "Theme: Light"
        return ft.Icons.DARK_MODE_ROUNDED, "Theme: Dark"

    # ---- Interface management ----
    def _pick_default_index(interfaces):
        for i, (_, ip) in enumerate(interfaces):
            if ip.startswith("192.168."):
                return i
        for i, (_, ip) in enumerate(interfaces):
            if ip not in ("0.0.0.0", "127.0.0.1"):
                return i
        return 0

    def _find_index_for_ip(interfaces, target_ip):
        for i, (_, ip) in enumerate(interfaces):
            if ip == target_ip:
                return i
        return -1

    def _apply_interfaces(interfaces):
        old_ip = state.iface_ip
        state.interfaces = interfaces

        if not state.iface_picked:
            state.iface_index = _pick_default_index(interfaces)
            state.iface_picked = True
        else:
            idx = _find_index_for_ip(interfaces, old_ip)
            if idx >= 0:
                state.iface_index = idx
            elif not (0 <= state.iface_index < len(interfaces)):
                state.iface_index = 0

        if interfaces:
            label, ip = interfaces[state.iface_index]
            state.iface_label = label
            state.iface_ip = ip

    def refresh_ip(e=None):
        def _work():
            try:
                ips = get_all_ips()

                def _apply():
                    _apply_interfaces(ips)
                    log(
                        f"Detected {len(ips)} interfaces — "
                        f"{state.iface_label} · {state.iface_ip}",
                        "ok",
                    )
                    render()

                try:
                    page.run_task(_apply)
                except Exception:
                    _apply()
            except Exception as ex:
                log(f"Refresh failed: {ex}", "err")

        threading.Thread(target=_work, daemon=True).start()

    def on_iface_change(index: int):
        if not (0 <= index < len(state.interfaces)):
            return
        state.iface_index = index
        label, ip = state.interfaces[index]
        state.iface_label = label
        state.iface_ip = ip
        state.iface_picked = True
        log(f"Selected interface: {label} · {ip}", "info")

        if server.is_alive():
            log("Restarting server on new interface…", "warn")
            server.stop()
            state.server_running = False
            time.sleep(0.3)

            try:
                server.share_dir = state.share_dir
                server.port = int(state.port)
                server.bind_host = ip
                server.start()
                time.sleep(0.4)
                if server.is_alive():
                    state.server_running = True
                    log(f"Server running on {ip}:{state.port}", "ok")
                    log(f"Open: {state.access_url}", "info")
            except Exception as ex:
                log(f"Restart failed: {ex}", "err")

        render()

    # ---- Server ----
    def toggle_server(e=None):
        if server.is_alive():
            server.stop()
            state.server_running = False
            log("Server stopped.", "warn")
            render()
            return

        if not state.share_dir:
            log("Pick a folder first.", "warn")
            render()
            return

        try:
            port = int(state.port)
            if port < 1024 or port > 65535:
                raise ValueError
        except ValueError:
            log("Invalid port — using 8000.", "warn")
            state.port = "8000"
            port = 8000

        bind_host = state.bind_host

        try:
            server.share_dir = state.share_dir
            server.port = port
            server.bind_host = bind_host

            log(f"Starting server on {bind_host}:{port}…", "info")
            server.start()
            time.sleep(0.4)

            if server.is_alive():
                state.server_running = True
                log(f"Server running on {bind_host}:{port}", "ok")
                log(f"Open: {state.access_url}", "info")

                # ---- Android: start foreground service ----
                if IS_ANDROID:
                    try:
                        from .core.share.android_services import start_foreground_service
                        coro = start_foreground_service()
                        if callable(coro):
                            run_async(coro)
                            log("Foreground service requested.", "info")
                    except Exception as ex:
                        log(f"Foreground service failed: {ex}", "err")
            else:
                log("Server failed to start — check logs.", "err")
                state.server_running = False

        except OSError as ex:
            if "Address already in use" in str(ex):
                log(f"Port {port} is busy. Try another.", "err")
            else:
                log(f"OS error: {ex}", "err")
            state.server_running = False
        except Exception as ex:
            log(f"Failed: {type(ex).__name__}: {ex}", "err")
            state.server_running = False

        render()

    # ---- Folder picker ----
    async def pick_folder(e=None):
        log("Opening folder picker…", "info")
        try:
            path = await file_picker.get_directory_path(
                dialog_title="Select a folder to share")
        except Exception as ex:
            log(f"Picker error: {ex}", "err")
            return
        if not path:
            log("Cancelled.", "warn")
            return
        _set_share_dir(path)

    def _set_share_dir(path_str: str):
        try:
            p = Path(path_str).expanduser().resolve()
            if not p.exists() or not p.is_dir():
                log(f"Not a folder: {p}", "err")
                return
            if server.is_alive():
                server.stop()
                state.server_running = False
            state.share_dir = str(p)
            log(f"Folder: {p}", "ok")
            render()
        except Exception as ex:
            log(f"Error: {ex}", "err")

    # ---- Share all / Permissions / Battery ----
    async def share_all(e=None):
        if not IS_ANDROID:
            _set_share_dir(str(Path.home()))
            return
        if ph is None:
            log("Permission handler unavailable.", "err")
            return
        try:
            import flet_permission_handler as fph
            status = await ph.get_status(
                fph.Permission.MANAGE_EXTERNAL_STORAGE)
            if not status or status.name != "GRANTED":
                log("Grant storage permission first.", "warn")
                return
        except Exception as ex:
            log(f"Permission check failed: {ex}", "err")
            return
        _set_share_dir("/storage/emulated/0")

    async def request_permissions(e=None):
        if not IS_ANDROID or ph is None:
            log("Not available on this platform.", "warn")
            render()
            return
        try:
            import flet_permission_handler as fph
        except ImportError:
            log("flet_permission_handler not installed.", "err")
            render()
            return
        log("Checking permissions…", "info")
        try:
            loc = await ph.get_status(fph.Permission.LOCATION)
            if not loc or loc.name != "GRANTED":
                await ph.request(fph.Permission.LOCATION)
        except Exception:
            pass
        try:
            status = await ph.get_status(
                fph.Permission.MANAGE_EXTERNAL_STORAGE)
            if status and status.name == "GRANTED":
                log("Storage access already granted.", "ok")
                render()
                return
            log("Requesting storage access…", "warn")
            status = await ph.request(
                fph.Permission.MANAGE_EXTERNAL_STORAGE)
            if not (status and status.name == "GRANTED"):
                log("Opening app settings…", "warn")
                await ph.open_app_settings()
                log("Enable 'All files access' and restart.", "info")
            else:
                log("Granted.", "ok")
        except Exception as ex:
            log(f"Permission error: {ex}", "err")
        render()

    async def request_battery_exemption(e=None):
        if not IS_ANDROID:
            log("Battery exemption is Android-only.", "warn")
            render()
            return

        try:
            from .core.share.android_services import (
                is_ignoring_battery_optimizations,
                open_battery_optimization_dialog,
            )
        except ImportError as ex:
            log(f"Failed to load Android services: {ex}", "err")
            return

        # If already exempt, just inform the user
        if is_ignoring_battery_optimizations():
            log("Battery optimization exemption is already active.", "ok")
            render()
            return

        # Try to open the dialog
        ok = open_battery_optimization_dialog()
        if not ok:
            log(
                "Could not open battery settings. Please enable it manually in Settings > Apps > LANShare > Battery.",
                "warn"
            )
            render()
            return

        # Dialog was opened. Wait for the user to return, then re-check.
        log("Battery settings opened. Waiting for your choice...", "info")
        render()

        async def _check_after_return():
            import asyncio
            await asyncio.sleep(1.5)

            for _ in range(10):
                if is_ignoring_battery_optimizations():
                    log("Battery exemption granted successfully.", "ok")
                    render()
                    return
                await asyncio.sleep(1.0)

            if not is_ignoring_battery_optimizations():
                log(
                    "Battery exemption was not granted. The server may stop in the background.",
                    "warn"
                )
                render()

        run_async(_check_after_return)

    # ---- URL actions ----
    async def copy_url(e=None):
        try:
            await ft.Clipboard().set(state.access_url)
            log("URL copied.", "ok")
        except Exception as ex:
            log(f"Copy failed: {ex}", "err")

    async def open_url(e=None):
        try:
            await ft.UrlLauncher().launch_url(state.access_url)
        except Exception as ex:
            try:
                import webbrowser
                webbrowser.open(state.access_url)
            except Exception:
                log(f"Open failed: {ex}", "err")

    # ---- QR dialog ----
    async def show_qr(e=None):
        try:
            from .core.qr import make_qr_data_uri
        except ImportError:
            log("QR module not available.", "err")
            return

        url = state.access_url
        data_uri = make_qr_data_uri(url)

        if not data_uri:
            log("Failed to generate QR code — is 'qrcode' installed?",
                "err")
            return

        p = P()

        def _close_qr(e=None):
            try:
                page.pop_dialog()
            except Exception:
                try:
                    page.dialog.open = False
                    page.update()
                except Exception:
                    pass

        img_kwargs = {
            "src": data_uri,
            "width": 260,
            "height": 260,
        }
        try:
            img_kwargs["fit"] = ft.BoxFit.CONTAIN
        except Exception:
            pass

        qr_image = ft.Image(**img_kwargs)
        qr_card = ft.Container(
            content=qr_image,
            padding=ft.Padding.all(8),
            bgcolor="#FFFFFF",
            border_radius=Radius.md,
            on_click=_close_qr,
            ink=False,
        )

        dialog_content = ft.Column(
            [
                ft.Text("Scan to connect",
                        size=17, weight=ft.FontWeight.W_600,
                        color=p["text"]),
                ft.Container(height=4),
                ft.Text("Point your phone's camera at the QR code.",
                        size=12, color=p["text_muted"],
                        text_align=ft.TextAlign.CENTER),
                ft.Container(height=Space.md),
                qr_card,
            ],
            spacing=0,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        dialog_kwargs = {
            "content": ft.Container(
                content=dialog_content,
                padding=ft.Padding.all(Space.md),
            ),
            "bgcolor": p["surface"],
            "modal": True,
            "on_dismiss": _close_qr,
        }
        try:
            dialog_kwargs["shape"] = ft.RoundedRectangleBorder(
                radius=Radius.lg)
        except Exception:
            pass

        dialog = ft.AlertDialog(**dialog_kwargs)

        try:
            page.show_dialog(dialog)
        except Exception:
            try:
                page.dialog = dialog
                dialog.open = True
                page.update()
            except Exception as ex:
                log(f"Dialog failed: {ex}", "err")

    # ---- Navigation ----
    def on_nav(e):
        try:
            state.view = e.control.selected_index
        except AttributeError:
            state.view = getattr(e, "selected_index", 0)
        render()

    # ---- Handlers map ----
    handlers: Dict[str, Callable] = {
        "log": log,
        "cycle_theme": cycle_theme,
        "set_theme": set_theme,
        "toggle_server": toggle_server,
        "pick_folder": lambda: run_async(pick_folder, None),
        "share_all": lambda: run_async(share_all, None),
        "request_permissions": lambda: run_async(request_permissions, None),
        "request_battery_exemption": lambda: run_async(request_battery_exemption, None),
        "refresh_ip": refresh_ip,
        "copy_url": lambda: run_async(copy_url, None),
        "open_url": lambda: run_async(open_url, None),
        "show_qr": lambda: run_async(show_qr, None),
        "on_iface_change": on_iface_change,
    }

    # ---- Layout holders ----
    appbar_holder = ft.Container()
    body_scroll = ft.Column(
        [], spacing=0, tight=True,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    rail_holder = ft.Container(visible=False)
    navbar_holder = ft.Container(visible=False)

    destinations = [
        {"icon": ft.Icons.GRID_VIEW_ROUNDED, "label": "Dashboard"},
        {"icon": ft.Icons.HISTORY_ROUNDED, "label": "Activity"},
        {"icon": ft.Icons.SETTINGS_ROUNDED, "label": "Settings"},
    ]

    # ---- Root holder ----
    root_holder = ft.Container(expand=True)

    # ---- Render ----
    def render():
        p = P()
        page.bgcolor = p["bg"]

        wide = (page.width or 0) >= BP.md
        theme_icon, theme_tooltip = _theme_icon()

        brand_logo = ft.Container(
            content=ft.Icon(
                ft.Icons.FOLDER_SHARED_ROUNDED,
                size=22,
                color=p["text"],
            ),
            width=40, height=40,
            bgcolor=p["surface_2"],
            border=ft.Border.all(1, p["border"]),
            border_radius=Radius.lg,
            alignment=ft.Alignment.CENTER,
        )

        brand_column = ft.Column(
            [
                ft.Text("LANShare", size=17,
                        weight=ft.FontWeight.W_700,
                        color=p["text"]),
                ft.Text("File server", size=12,
                        color=p["text_muted"]),
            ],
            spacing=2,
            tight=True,
        )

        status_tone = "online" if state.server_running else "offline"

        if wide:
            drag_region = ft.WindowDragArea(
                content=ft.Container(
                    content=ft.Row(
                        [
                            brand_logo,
                            ft.Container(width=Space.sm + 4),
                            brand_column,
                            ft.Container(expand=True),
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        tight=False,
                    ),
                    expand=True,
                ),
                expand=True,
                maximizable=True,
            )

            controls_row = ft.Row(
                [
                    IconActionButton(
                        p,
                        icon=theme_icon,
                        on_click=cycle_theme,
                        tooltip=theme_tooltip,
                    ),
                    ft.Container(width=Space.sm),
                    StatusChip(
                        p,
                        "Online" if state.server_running else "Offline",
                        status_tone,
                    ),
                    ft.Container(width=Space.md),
                    _window_controls(),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            )

            appbar_holder.content = ft.Container(
                content=ft.Row(
                    [drag_region, controls_row],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding.symmetric(
                    horizontal=Space.lg, vertical=Space.md),
                border=ft.Border.only(
                    bottom=ft.BorderSide(1, p["border"])),
                bgcolor=p["bg"],
            )
        else:
            appbar_holder.content = AppBar(
                p,
                title="LANShare",
                subtitle="File server",
                trailing=[
                    IconActionButton(
                        p,
                        icon=theme_icon,
                        on_click=cycle_theme,
                        tooltip=theme_tooltip,
                    ),
                    ft.Container(width=Space.sm),
                    StatusChip(
                        p,
                        "Online" if state.server_running else "Offline",
                        status_tone,
                    ),
                ],
            )
        appbar_holder.visible = True

        body = build_view(
            state.view, p, state, handlers,
            page_width=page.width or 1200,
        )
        body_scroll.controls.clear()
        body_scroll.controls.append(body)

        rail_holder.visible = wide
        navbar_holder.visible = not wide
        if wide:
            rail_holder.content = NavSidebar(
                p, state.view, on_nav, destinations, state=state)
        else:
            navbar_holder.content = NavBar(
                p, state.view, on_nav, destinations)

        top_spacer = (
            ft.Container(height=top_pad) if top_pad else ft.Container()
        )
        bottom_pad = 16 if (IS_ANDROID and not wide) else 0
        bottom_spacer = (
            ft.Container(height=bottom_pad) if bottom_pad else ft.Container()
        )

        shell = ft.Column(
            [
                top_spacer,
                appbar_holder,
                ft.Row(
                    [
                        rail_holder,
                        ft.Container(
                            content=body_scroll,
                            expand=True,
                            bgcolor=p["bg"],
                        ),
                    ],
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
                navbar_holder,
                bottom_spacer,
            ],
            spacing=0,
            expand=True,
        )

        root_holder.content = ft.Container(
            shell, bgcolor=p["bg"], expand=True)
        safe_update()

    page.on_resize = lambda e: render()

    # ---- Lifecycle hooks ----
    def on_disconnect(e=None):
        try:
            log("Session ended — stopping server.", "info")
        except Exception:
            pass
        shutdown_server()
        try:
            safe_update()
        except Exception:
            pass

    try:
        page.on_disconnect = on_disconnect
    except Exception:
        pass

    # ---- Bootstrap ----
    log("App ready.", "ok")
    if IS_ANDROID:
        try:
            from .core.share.android_services import is_ignoring_battery_optimizations
            if not is_ignoring_battery_optimizations():
                log("⚠️ Background server may be stopped. Use 'Battery Exemption' to fix this.", "warn")
            else:
                log("Battery optimization exemption is already active.", "ok")
        except Exception as ex:
            log(f"Could not check battery status: {ex}", "warn")

        log("Tap 'Permissions' then 'Share all'.", "info")
    else:
        log("Pick a folder to start.", "info")

    # ============================================================
    # UI BUILD ORDER
    # ============================================================
    page.add(root_holder)

    render()
    refresh_ip()

    try:
        page.overlay.append(splash_layer)
    except Exception:
        pass

    page.update()

    # ============================================================
    # AUTO-REMOVE SPLASH — 2.5s
    # ============================================================
    async def _remove_splash_async():
        import asyncio

        await asyncio.sleep(2.5)

        if not splash_state["removed"]:
            splash_state["removed"] = True
            try:
                page.overlay.clear()
                page.update()
            except Exception:
                pass

        try:
            w = page.window.width or WINDOW_DEFAULT_WIDTH
            h = page.window.height or WINDOW_DEFAULT_HEIGHT
            for _ in range(2):
                page.window.width = w + 2
                page.window.height = h + 2
                page.update()
                await asyncio.sleep(0.05)
                page.window.width = w
                page.window.height = h
                page.update()
                await asyncio.sleep(0.05)
        except Exception:
            pass

    try:
        page.run_task(_remove_splash_async)
    except Exception:
        def _fallback():
            time.sleep(2.5)
            try:
                page.overlay.clear()
                page.update()
            except Exception:
                pass

        threading.Thread(target=_fallback, daemon=True).start()


# ============================================================
# Page config
# ============================================================
def _configure_page(page: ft.Page):
    page.title = "LANShare"
    page.padding = 0
    page.bgcolor = "#000000"
    page.theme_mode = ft.ThemeMode.DARK


def _system_is_dark(page: ft.Page) -> bool:
    try:
        return page.platform_brightness == ft.Brightness.DARK
    except Exception:
        return True


def _now() -> str:
    return time.strftime("%H:%M:%S")
