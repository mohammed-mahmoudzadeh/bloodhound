"""Flet application — UI shell. Business logic untouched."""
from __future__ import annotations

import atexit
import asyncio
import os
import signal
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Callable, Dict

import flet as ft
from flet import Page

from .config import (
    IS_ANDROID,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)
from .state import AppState
from .settings_store import load_settings, save_settings
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


def main(page: Page):
    page.adaptive = True
    
    if not IS_ANDROID:
        try:
            page.window.title_bar_hidden = True
            page.window.title_bar_buttons_hidden = True
            page.window.width = WINDOW_DEFAULT_WIDTH
            page.window.height = WINDOW_DEFAULT_HEIGHT
            page.window.min_width = WINDOW_MIN_WIDTH
            page.window.min_height = WINDOW_MIN_HEIGHT
        except Exception:
            pass

    _configure_page(page)

    # ============================================================
    # Early Splash
    # ============================================================
    temp_splash = ft.Container(bgcolor="#000000", alignment=ft.Alignment.CENTER, expand=True)
    splash_state = {"removed": False}
    try:
        page.overlay.append(temp_splash)
        page.update()
    except Exception:
        pass

    # ============================================================
    # Initialize State & Theme
    # ============================================================
    state = AppState()
    settings_load_error: Exception | None = None
    try:
        load_settings(state)
    except (OSError, ValueError) as ex:
        settings_load_error = ex
    server = FlaskServer(port=int(state.port))

    theme_holder = {
        "mode": state.theme_mode,
        "system_dark": _system_is_dark(page),
        "P": None,
    }

    def current_dark() -> bool:
        m = theme_holder["mode"]
        if m == "dark": return True
        if m == "light": return False
        return theme_holder["system_dark"]

    def P() -> dict:
        if theme_holder["P"] is None:
            theme_holder["P"] = build_palette(current_dark())
        return theme_holder["P"]

    def refresh_palette():
        theme_holder["P"] = build_palette(current_dark())
        state.dark = current_dark()
        state.theme_mode = theme_holder["mode"]

    refresh_palette()

    def _safe_area_top() -> int:
        """Return the top safe-area inset (status bar height) in px."""
        if not IS_ANDROID:
            return 0
        try:
            from jnius import autoclass
            activity_host = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
            if activity_host:
                host = autoclass(activity_host)
                activity = host.mActivity
            else:
                from android import mActivity as activity  # type: ignore
            if activity is None:
                return 18
            res = activity.getResources()
            res_id = res.getIdentifier("status_bar_height", "dimen", "android")
            if res_id > 0:
                raw = int(res.getDimensionPixelSize(res_id))
                return max(raw - 18, 18)
        except Exception:
            pass
        return 18

    # ============================================================
    # Assets
    # ============================================================
    _here = Path(__file__).resolve()
    _asset_candidates = [
        _here.parent.parent / "assets",
        _here.parent.parent.parent / "assets",
        Path.cwd() / "assets",
        Path.cwd() / "src" / "assets",
    ]
    assets_dir = None
    for _p in _asset_candidates:
        if _p.is_dir() and (_p / "logo_dark.png").exists():
            assets_dir = _p
            break

    def _get_logo_src() -> str | None:
        if not assets_dir:
            return None
        logo_filename = "logo_dark.png" if current_dark() else "logo_light.png"
        return str(assets_dir / logo_filename)

    # ============================================================
    # Splash UI
    # ============================================================
    p = P()
    splash_icon_src = _get_logo_src()

    if splash_icon_src:
        splash_icon = ft.Image(src=splash_icon_src, width=160, height=160, fit=ft.BoxFit.CONTAIN)
    else:
        splash_icon = ft.Icon(ft.Icons.FOLDER_SHARED_ROUNDED, size=160, color=p["primary"])

    brand_text = ft.Row(
        [
            ft.Text("Blood", size=32, weight=ft.FontWeight.W_400, color=p["text_muted"], font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace"),
            ft.Text("Hound", size=32, weight=ft.FontWeight.W_800, color=p["text"], font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace", style=ft.TextStyle(letter_spacing=2)),
        ],
        spacing=0, alignment=ft.MainAxisAlignment.CENTER, tight=True
    )

    subtitle_text = ft.Text("Share files over your local network", size=15, color=p["text_muted"], weight=ft.FontWeight.W_400, text_align=ft.TextAlign.CENTER, style=ft.TextStyle(letter_spacing=0.5))

    dot1 = ft.Container(width=6, height=6, border_radius=3, bgcolor=p["text_muted"], animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT), opacity=0.3)
    dot2 = ft.Container(width=6, height=6, border_radius=3, bgcolor=p["text_muted"], animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT), opacity=0.6)
    dot3 = ft.Container(width=6, height=6, border_radius=3, bgcolor=p["text_muted"], animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT), opacity=1.0)
    loading_dots = ft.Row([dot1, dot2, dot3], alignment=ft.MainAxisAlignment.CENTER, spacing=8, height=20, tight=True)

    splash_layer = ft.Container(
        content=ft.Column(
            [
                ft.Container(expand=True), 
                splash_icon,
                ft.Container(height=24),   
                brand_text,
                ft.Container(height=8),    
                subtitle_text,
                ft.Container(expand=True), 
                loading_dots,
                ft.Container(height=48),   
            ],
            spacing=0, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=p["bg"], alignment=ft.Alignment.CENTER, expand=True,
    )

    try:
        page.overlay.clear()
        page.overlay.append(splash_layer)
        page.update()
    except Exception:
        pass

    if IS_ANDROID:
        try:
            from jnius import autoclass
            autoclass("android.media.MediaMetadataRetriever")
            autoclass("android.provider.Settings")
            autoclass("android.os.PowerManager")
        except Exception:
            pass

    # ============================================================
    # Services & Handlers Setup
    # ============================================================
    file_picker = ft.FilePicker()
    ph = None
    try:
        from .core.permissions import build_handler
        ph = build_handler()
    except Exception:
        ph = None
    for svc in [file_picker, ph]:
        if svc is None: continue
        try: page.services.append(svc)
        except Exception:
            try: page.overlay.append(svc)
            except Exception: pass

    def safe_update():
        try: page.update()
        except Exception: pass

    def run_async(fn, *args, **kwargs):
        try: page.run_task(fn, *args, **kwargs)
        except Exception:
            threading.Thread(target=lambda: fn(*args, **kwargs), daemon=True).start()

    def log(message: str, level: str = "info"):
        state.add_log(_now(), message, level)

    def persist_settings():
        try: save_settings(state)
        except OSError as ex:
            log(f"Could not save settings: {ex}", "err")

    if settings_load_error is not None:
        log(f"Could not load saved settings: {settings_load_error}", "err")

    def shutdown_server():
        try:
            if server.is_alive():
                server.stop()
                state.server_running = False
        except Exception: pass
    atexit.register(shutdown_server)

    # ============================================================
    # Core Logic
    # ============================================================
    def on_minimize(e=None):
        try: page.window.minimized = True
        except Exception:
            try: page.window.minimize()
            except Exception: pass

    def on_maximize(e=None):
        try:
            if page.window.maximized: page.window.maximized = False
            else: page.window.maximized = True
        except Exception:
            try: page.window.maximize()
            except Exception: pass

    async def _close_window_async():
        for method_name in ("destroy", "close", "exit_app"):
            try:
                method = getattr(page.window, method_name, None)
                if method is None: continue
                result = method()
                if hasattr(result, "__await__"): await result
                return
            except Exception: continue

    def on_close(e=None):
        persist_settings()
        shutdown_server()
        try: page.run_task(_close_window_async)
        except Exception:
            try: page.window.destroy()
            except Exception:
                try: page.window.close()
                except Exception: pass

    def _window_controls() -> ft.Control:
        def _btn(icon, on_click, tooltip, hover_color):
            c = ft.Container(
                content=ft.Icon(icon, size=18, color=P()["text_dim"]),
                width=36, height=36, border_radius=Radius.md,
                alignment=ft.Alignment.CENTER, ink=True, tooltip=tooltip,
                on_click=on_click, animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            )
            def _on_hover(e):
                try:
                    c.bgcolor = hover_color if e.data == "true" else "transparent"
                    c.update()
                except Exception: pass
            c.on_hover = _on_hover
            return c
        return ft.Row([
            _btn(ft.Icons.REMOVE_ROUNDED, on_minimize, "Minimize", P()["surface_2"]),
            _btn(ft.Icons.CROP_SQUARE_ROUNDED, on_maximize, "Maximize", P()["surface_2"]),
            _btn(ft.Icons.CLOSE_ROUNDED, on_close, "Close", "#e81123"),
        ], spacing=0, tight=True)

    def set_theme(mode: str):
        if mode not in ("auto", "light", "dark"): return
        theme_holder["mode"] = mode
        state.theme_mode = mode
        refresh_palette()
        page.theme_mode = ft.ThemeMode.DARK if current_dark() else ft.ThemeMode.LIGHT
        persist_settings()
        render()

    def cycle_theme(e=None):
        order = ["auto", "light", "dark"]
        cur = theme_holder["mode"]
        nxt = order[(order.index(cur) + 1) % len(order)]
        set_theme(nxt)

    def _theme_icon() -> tuple[str, str]:
        m = theme_holder["mode"]
        if m == "auto": return ft.Icons.BRIGHTNESS_AUTO_ROUNDED, "Theme: Auto (system)"
        if m == "light": return ft.Icons.LIGHT_MODE_ROUNDED, "Theme: Light"
        return ft.Icons.DARK_MODE_ROUNDED, "Theme: Dark"

    def _pick_default_index(interfaces):
        for i, (_, ip) in enumerate(interfaces):
            if ip.startswith("192.168."): return i
        for i, (_, ip) in enumerate(interfaces):
            if ip == "127.0.0.1": return i
        return 0

    def _find_index_for_ip(interfaces, target_ip):
        for i, (_, ip) in enumerate(interfaces):
            if ip == target_ip: return i
        return -1

    def _apply_interfaces(interfaces):
        old_ip = state.iface_ip
        state.interfaces = interfaces
        if not state.iface_picked:
            state.iface_index = _pick_default_index(interfaces)
            state.iface_picked = True
        else:
            idx = _find_index_for_ip(interfaces, old_ip)
            if idx >= 0: state.iface_index = idx
            elif not (0 <= state.iface_index < len(interfaces)): state.iface_index = 0
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
                    log(f"Detected {len(ips)} interfaces — {state.iface_label} · {state.iface_ip}", "ok")
                    render()
                try:
                    page.run_task(_apply)
                except Exception as ex:
                    log(f"Could not schedule UI update: {ex}", "warn")
                    _apply_interfaces(ips)
                    try:
                        safe_update()
                    except Exception:
                        pass
            except Exception as ex: log(f"Refresh failed: {ex}", "err")
        threading.Thread(target=_work, daemon=True).start()

    def on_iface_change(index: int):
        if not (0 <= index < len(state.interfaces)): return
        state.iface_index = index
        label, ip = state.interfaces[index]
        state.iface_label = label
        state.iface_ip = ip
        state.iface_picked = True
        persist_settings()
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
            except Exception as ex: log(f"Restart failed: {ex}", "err")
        render()

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
            if port < 1024 or port > 65535: raise ValueError
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
                if IS_ANDROID:
                    try:
                        from .core.share.android_services import start_foreground_service
                        coro = start_foreground_service()
                        if callable(coro):
                            run_async(coro)
                            log("Foreground service requested.", "info")
                    except Exception as ex: log(f"Foreground service failed: {ex}", "err")
            else:
                log("Server failed to start — check logs.", "err")
                state.server_running = False
        except OSError as ex:
            if "Address already in use" in str(ex): log(f"Port {port} is busy. Try another.", "err")
            else: log(f"OS error: {ex}", "err")
            state.server_running = False
        except Exception as ex:
            log(f"Failed: {type(ex).__name__}: {ex}", "err")
            state.server_running = False
        render()

    async def pick_folder(e=None):
        log("Opening folder picker…", "info")
        try:
            path = await file_picker.get_directory_path(dialog_title="Select a folder to share")
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
            persist_settings()
            log(f"Folder: {p}", "ok")
            render()
        except Exception as ex: log(f"Error: {ex}", "err")

    async def share_all(e=None):
        if not IS_ANDROID:
            _set_share_dir(str(Path.home()))
            return
        if ph is None:
            log("Permission handler unavailable.", "err")
            return
        try:
            import flet_permission_handler as fph
            status = await ph.get_status(fph.Permission.MANAGE_EXTERNAL_STORAGE)
            if not status or status.name != "GRANTED":
                log("Grant storage permission first. Tap 'Permissions'.", "warn")
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
        from .core.share.android_services import has_storage_permission
        if has_storage_permission():
            log("Storage access already granted.", "ok")
            state.view = 0
            render()
            return
        log("Opening system settings for 'All files access'…", "warn")
        try:
            status = await ph.request(fph.Permission.MANAGE_EXTERNAL_STORAGE)
            if status and status.name == "GRANTED":
                log("Storage access granted successfully.", "ok")
                state.view = 0
                render()
                return
            log("Waiting for you to grant 'All files access' in Settings…", "info")
        except Exception as ex:
            log(f"Permission request error: {ex}", "err")
            render()

    async def request_battery_exemption(e=None):
        if not IS_ANDROID:
            log("Battery exemption is Android-only.", "warn")
            render()
            return
        try:
            from .core.share.android_services import is_ignoring_battery_optimizations, open_battery_optimization_dialog
        except ImportError as ex:
            log(f"Failed to load Android services: {ex}", "err")
            return
        if is_ignoring_battery_optimizations():
            log("Battery optimization exemption is already active.", "ok")
            render()
            return
        ok = open_battery_optimization_dialog()
        if not ok:
            log("Could not open battery settings. Please enable it manually in Settings > Apps > BloodHound > Battery.", "warn")
            render()
            return
        log("Battery settings opened. Waiting for your choice...", "info")
        render()
        async def _check_after_return():
            await asyncio.sleep(1.5)
            for _ in range(10):
                if is_ignoring_battery_optimizations():
                    log("Battery exemption granted successfully.", "ok")
                    render()
                    return
                await asyncio.sleep(1.0)
            if not is_ignoring_battery_optimizations():
                log("Battery exemption was not granted. The server may stop in the background.", "warn")
                render()
        run_async(_check_after_return)

    async def copy_url(e=None):
        try:
            await ft.Clipboard().set(state.access_url)
            log("URL copied.", "ok")
        except Exception as ex: log(f"Copy failed: {ex}", "err")

    async def open_url(e=None):
        try: await ft.UrlLauncher().launch_url(state.access_url)
        except Exception as ex:
            try:
                import webbrowser
                webbrowser.open(state.access_url)
            except Exception: log(f"Open failed: {ex}", "err")

    async def show_qr(e=None):
        try: from .core.qr import make_qr_data_uri
        except ImportError:
            log("QR module not available.", "err")
            return
        url = state.access_url
        data_uri = make_qr_data_uri(url)
        if not data_uri:
            log("Failed to generate QR code — is 'qrcode' installed?", "err")
            return
        p = P()
        def _close_qr(e=None):
            try: page.pop_dialog()
            except Exception:
                try:
                    page.dialog.open = False
                    page.update()
                except Exception: pass
        
        img_kwargs = {"src": data_uri, "width": 260, "height": 260}
        try: img_kwargs["fit"] = ft.BoxFit.CONTAIN
        except Exception: pass
        qr_image = ft.Image(**img_kwargs)
        
        qr_card = ft.Container(
            content=qr_image,
            padding=ft.Padding.all(12),
            bgcolor="#FFFFFF",
            border=ft.Border.all(1, p["text_faint"]),
            border_radius=Radius.md,
            on_click=_close_qr,
            ink=False,
        )
        
        dialog_content = ft.Column([
            ft.Text("Scan to connect", size=17, weight=ft.FontWeight.W_600, color=p["text"]),
            ft.Container(height=4),
            ft.Text("Point your phone's camera at the QR code.", size=12, color=p["text_muted"], text_align=ft.TextAlign.CENTER),
            ft.Container(height=Space.md),
            qr_card,
        ], spacing=0, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        dialog_kwargs = {
            "content": ft.Container(content=dialog_content, padding=ft.Padding.all(Space.md)),
            "bgcolor": p["surface_2"],
            "modal": True,
            "on_dismiss": _close_qr,
        }
        try: dialog_kwargs["shape"] = ft.RoundedRectangleBorder(radius=Radius.lg)
        except Exception: pass
        dialog = ft.AlertDialog(**dialog_kwargs)
        try: page.show_dialog(dialog)
        except Exception:
            try:
                page.dialog = dialog
                dialog.open = True
                page.update()
            except Exception as ex: log(f"Dialog failed: {ex}", "err")

    def on_nav(e):
        try: state.view = e.control.selected_index
        except AttributeError: state.view = getattr(e, "selected_index", 0)
        render()

    def _nav_to(index: int):
        def handler(e=None):
            state.view = index
            render()
        return handler

    def set_port(value: str):
        try:
            port_int = int(value)
            if 1024 <= port_int <= 65535:
                state.port = value
                persist_settings()
        except (ValueError, TypeError):
            pass

    def set_device_name(value: str):
        state.device_name = value
        persist_settings()

    handlers: Dict[str, Callable] = {
        "log": log, "cycle_theme": cycle_theme, "set_theme": set_theme,
        "toggle_server": toggle_server, "pick_folder": lambda: run_async(pick_folder, None),
        "share_all": lambda: run_async(share_all, None), "request_permissions": lambda: run_async(request_permissions, None),
        "request_battery_exemption": lambda: run_async(request_battery_exemption, None),
        "refresh_ip": refresh_ip, "copy_url": lambda: run_async(copy_url, None),
        "open_url": lambda: run_async(open_url, None), "show_qr": lambda: run_async(show_qr, None),
        "on_iface_change": on_iface_change,
        "set_port": set_port,
        "set_device_name": set_device_name,
    }

    # ============================================================
    # Render Function (Responsive)
    # ============================================================
    root_holder = ft.Container(expand=True)
    destinations = [
        {"icon": ft.Icons.GRID_VIEW_ROUNDED, "label": "Dashboard"},
        {"icon": ft.Icons.HISTORY_ROUNDED, "label": "Activity"},
        {"icon": ft.Icons.SETTINGS_ROUNDED, "label": "Settings"},
    ]

    _last_wide: bool | None = None
    SIDEBAR_WIDTH = 180

    def render():
        nonlocal _last_wide
        
        p = P()
        page.bgcolor = p["bg"]
        page.theme_mode = ft.ThemeMode.DARK if current_dark() else ft.ThemeMode.LIGHT

        width = page.width or (WINDOW_DEFAULT_WIDTH if not IS_ANDROID else 400)
        
        # --- Responsive Breakpoints ---
        is_mobile = width < BP.md
        is_narrow_desktop = BP.md <= width < 900
        
        _last_wide = not is_mobile

        theme_icon, theme_tooltip = _theme_icon()
        
        # --- Header Brand Logo Sizing ---
        if is_mobile:
            logo_size = 56
            img_size = 44
            brand_font_size = 20
            subtitle_font_size = 13
        else:
            logo_size = 56
            img_size = 44
            brand_font_size = 20
            subtitle_font_size = 13

        # --- Brand Logo (no background, no border) ---
        logo_src = _get_logo_src()
        if logo_src:
            brand_logo = ft.Image(
                src=logo_src,
                width=img_size,
                height=img_size,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            brand_logo = ft.Icon(ft.Icons.FOLDER_SHARED_ROUNDED, size=44, color=p["text"])

        brand_column = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Blood", size=brand_font_size, weight=ft.FontWeight.W_400, color=p["text_muted"], font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace"),
                        ft.Text("Hound", size=brand_font_size, weight=ft.FontWeight.W_700, color=p["text"], font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace"),
                    ],
                    spacing=0, tight=True
                ),
                ft.Text("File server", size=subtitle_font_size, color=p["text_muted"])
            ], 
            spacing=2, tight=True
        )

        # --- Build Header ---
        if not is_mobile:
            # Desktop Header
            header_left = ft.Row(
                [brand_logo, ft.Container(width=Space.md), brand_column],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            )
            
            icon_size = 40
            header_content = ft.Row(
                [
                    ft.WindowDragArea(content=header_left, maximizable=True),
                    ft.Container(expand=True),
                    ft.Container(
                        content=IconActionButton(p, icon=theme_icon, on_click=cycle_theme, tooltip=theme_tooltip, size=icon_size),
                        padding=ft.Padding.only(bottom=4),
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            
            if is_narrow_desktop:
                header_content.controls.extend([
                    ft.Container(width=Space.sm),
                    ft.Container(
                        content=IconActionButton(p, icon=ft.Icons.HISTORY_ROUNDED, on_click=_nav_to(1), tooltip="Activity", size=icon_size),
                        padding=ft.Padding.only(bottom=4),
                    ),
                    ft.Container(width=Space.sm),
                    ft.Container(
                        content=IconActionButton(p, icon=ft.Icons.SETTINGS_ROUNDED, on_click=_nav_to(2), tooltip="Settings", size=icon_size),
                        padding=ft.Padding.only(bottom=4),
                    ),
                ])
            else:
                header_content.controls.extend([
                    ft.Container(width=Space.md),
                    _window_controls()
                ])
            
            appbar = ft.Container(
                content=header_content,
                padding=ft.Padding.symmetric(horizontal=Space.lg, vertical=Space.sm),
                bgcolor=p["bg"],
                border=ft.Border.only(bottom=ft.BorderSide(1, p["border"]))
            )
        else:
            # Mobile Header
            icon_size = 40
            if state.view == 0:
                mobile_content = ft.Row(
                    [
                        brand_logo,
                        ft.Container(width=Space.sm),
                        brand_column,
                        ft.Container(expand=True),
                        ft.Container(
                            content=IconActionButton(p, icon=ft.Icons.HISTORY_ROUNDED, on_click=_nav_to(1), tooltip="Activity", size=icon_size),
                            padding=ft.Padding.only(bottom=4),
                        ),
                        ft.Container(width=Space.sm),
                        ft.Container(
                            content=IconActionButton(p, icon=ft.Icons.SETTINGS_ROUNDED, on_click=_nav_to(2), tooltip="Settings", size=icon_size),
                            padding=ft.Padding.only(bottom=4),
                        ),
                        ft.Container(width=Space.sm),
                        ft.Container(
                            content=IconActionButton(p, icon=theme_icon, on_click=cycle_theme, tooltip=theme_tooltip, size=icon_size),
                            padding=ft.Padding.only(bottom=4),
                        ),
                    ],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
                appbar = ft.Container(
                    content=mobile_content,
                    padding=ft.Padding.symmetric(horizontal=Space.md, vertical=Space.sm),
                    bgcolor=p["bg"],
                    border=ft.Border.only(bottom=ft.BorderSide(1, p["border"]))
                )
            else:
                trailing = [
                    ft.Container(
                        content=IconActionButton(p, icon=theme_icon, on_click=cycle_theme, tooltip=theme_tooltip, size=icon_size),
                        padding=ft.Padding.only(bottom=4),
                    ),
                ]
                back_btn = IconActionButton(p, icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=_nav_to(0), tooltip="Back", size=icon_size)
                title = "Activity" if state.view == 1 else "Settings"
                appbar = AppBar(p, title=title, subtitle="", leading=back_btn, trailing=trailing)

        # --- Build Body ---
        effective_width = width - (SIDEBAR_WIDTH if not is_mobile else 0)
        body = build_view(state.view, p, state, handlers, page_width=effective_width)

        sidebar = ft.Container()
        if not is_mobile:
            sidebar.content = NavSidebar(p, state.view, on_nav, destinations, state=state)
            sidebar.visible = True
        else:
            sidebar.content = None
            sidebar.visible = False

        if IS_ANDROID and is_mobile:
            top_pad = _safe_area_top()
        else:
            top_pad = 0

        bottom_pad = 16 if (IS_ANDROID and is_mobile) else 0

        top_spacer = ft.Container(height=top_pad) if top_pad > 0 else None
        bottom_spacer = ft.Container(height=bottom_pad) if bottom_pad > 0 else None

        body_scroll = ft.Column(
            [body],
            spacing=0,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        body_container = ft.Container(
            content=body_scroll,
            expand=True,
            bgcolor=p["bg"],
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        shell_children = [
            top_spacer,
            appbar,
            ft.Row(
                [sidebar, body_container],
                spacing=0,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            bottom_spacer,
        ]
        shell_children = [c for c in shell_children if c is not None]

        shell = ft.Column(shell_children, spacing=0, expand=True)
        root_holder.content = ft.Container(shell, bgcolor=p["bg"], expand=True)
        safe_update()

    # ============================================================
    # Lifecycle & Resize Handling
    # ============================================================
    def on_resize(e):
        nonlocal _last_wide
        try:
            width = page.width or (WINDOW_DEFAULT_WIDTH if not IS_ANDROID else 400)
            new_wide = width >= BP.md
            if new_wide != _last_wide:
                _last_wide = new_wide
            render()
        except Exception:
            pass
        
    page.on_resize = on_resize

    def on_lifecycle(e: ft.AppLifecycleStateChangeEvent):
        if IS_ANDROID and e.state == ft.AppLifecycleState.RESUME:
            from .core.share.android_services import has_storage_permission
            if has_storage_permission() and state.view != 0:
                state.view = 0
                log("Storage permission granted. Returning to dashboard.", "ok")
                render()

    try: page.on_app_lifecycle_state_change = on_lifecycle
    except Exception: pass

    def on_disconnect(e=None):
        try: log("Session ended — stopping server.", "info")
        except Exception: pass
        persist_settings()
        shutdown_server()
        try: safe_update()
        except Exception: pass
    try: page.on_disconnect = on_disconnect
    except Exception: pass

    log("App ready.", "ok")
    if IS_ANDROID:
        from .core.share.android_services import is_ignoring_battery_optimizations, has_storage_permission
        if not is_ignoring_battery_optimizations():
            log("⚠️ Background server may be stopped. Use 'Battery Exemption' to fix this.", "warn")
        if not has_storage_permission():
            log("⚠️ Storage permission not granted. Use 'Permissions' to allow file access.", "warn")
        else:
            log("Storage access is already granted.", "ok")
        log("Tap 'Permissions' then 'Share all'.", "info")
    else:
        log("Pick a folder to start.", "info")

    page.add(root_holder)
    render()
    refresh_ip()
    page.update()

    async def _remove_splash_async():
        async def _animate_dots():
            try:
                while not splash_state["removed"]:
                    dot1.opacity, dot2.opacity, dot3.opacity = 1.0, 0.3, 0.3
                    dot1.update(), dot2.update(), dot3.update()
                    await asyncio.sleep(0.2)
                    if splash_state["removed"]: break
                    
                    dot1.opacity, dot2.opacity, dot3.opacity = 0.3, 1.0, 0.3
                    dot1.update(), dot2.update(), dot3.update()
                    await asyncio.sleep(0.2)
                    if splash_state["removed"]: break
                    
                    dot1.opacity, dot2.opacity, dot3.opacity = 0.3, 0.3, 1.0
                    dot1.update(), dot2.update(), dot3.update()
                    await asyncio.sleep(0.2)
            except Exception:
                pass

        dot_task = asyncio.create_task(_animate_dots())
        try:
            await asyncio.sleep(4.0)
            if not splash_state["removed"]:
                splash_state["removed"] = True
                try: await dot_task 
                except Exception: pass
                try:
                    page.overlay.clear()
                    page.update()
                except Exception: pass

            if not IS_ANDROID:
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
                except Exception: pass
        finally:
            try:
                dot_task.cancel()
            except Exception:
                pass
        
    try: 
        page.run_task(_remove_splash_async)
    except Exception:
        def _fallback():
            time.sleep(4.0)
            try:
                page.overlay.clear()
                page.update()
            except Exception: pass
        threading.Thread(target=_fallback, daemon=True).start()


def _configure_page(page: ft.Page):
    page.title = "BloodHound"
    page.padding = 0
    page.bgcolor = "#000000"
    page.theme_mode = ft.ThemeMode.DARK

    page.theme = ft.Theme(
        font_family="Inter",
        color_scheme=ft.ColorScheme(
            primary="#18181b", 
            surface="#ffffff",
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            bgcolor="#ffffff", 
            indicator_color="transparent",
            label_text_style=ft.TextStyle(color="#18181b", size=12, font_family="Inter"),
        ),
        system_overlay_style=ft.SystemOverlayStyle(
            status_bar_color="#ffffff",
            status_bar_icon_brightness=ft.Brightness.DARK,
        ),
    )

    page.dark_theme = ft.Theme(
        font_family="Inter",
        color_scheme=ft.ColorScheme(
            primary="#fafafa", 
            surface="#000000",
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            bgcolor="#000000", 
            indicator_color="transparent",
            label_text_style=ft.TextStyle(color="#fafafa", size=12, font_family="Inter"),
        ),
        system_overlay_style=ft.SystemOverlayStyle(
            status_bar_color="#000000",
            status_bar_icon_brightness=ft.Brightness.LIGHT,
        ),
    )

def _system_is_dark(page: ft.Page) -> bool:
    try: return page.platform_brightness == ft.Brightness.DARK
    except Exception: return True


def _now() -> str:
    return time.strftime("%H:%M:%S")