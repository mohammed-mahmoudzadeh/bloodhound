"""Flet application — UI shell. Business logic untouched."""
from __future__ import annotations

import atexit
import asyncio
import json
import os
import threading
import time
from pathlib import Path
from typing import Callable, Dict, Any

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
    AppBar, NavSidebar, StatusChip, IconActionButton,
)
from .core.network import get_all_ips
from .core.server import FlaskServer, PortInUseError
from .views import build_view


def run():
    ft.run(main)


# ============================================================
# Splash launch tracker — controls first-run vs. subsequent-run
# ============================================================
def _launch_counter_path() -> Path:
    base = Path.home() / ".cache" / "bloodhound"
    try:
        flet_data = os.environ.get("FLET_APP_STORAGE_DATA")
        if flet_data:
            base = Path(flet_data)
    except Exception:
        pass
    try:
        base.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return base / "launch_counter.json"


def _is_first_launch_today() -> bool:
    path = _launch_counter_path()
    today = time.strftime("%Y-%m-%d")
    data: dict = {}
    try:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    last_day = data.get("day")
    count = int(data.get("count", 0))

    if last_day != today:
        data = {"day": today, "count": 1}
        try:
            path.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass
        return True

    data["count"] = count + 1
    try:
        path.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass
    return False


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

    initial_bg = "#000000" if _system_is_dark(page) else "#fafafa"
    temp_splash = ft.Container(
        bgcolor=initial_bg,
        alignment=ft.Alignment.CENTER,
        expand=True,
    )
    splash_state = {"removed": False}
    try:
        page.overlay.append(temp_splash)
        page.update()
    except Exception:
        pass

    state = AppState()
    settings_load_error: Exception | None = None
    try:
        load_settings(state)
    except (OSError, ValueError) as ex:
        settings_load_error = ex
    server = FlaskServer(port=int(state.port))

    theme_holder: dict[str, Any] = {
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
        if not IS_ANDROID:
            return 0
        try:
            from jnius import autoclass  # type: ignore[import-not-found]
            activity_host = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
            if activity_host:
                host = autoclass(activity_host)
                activity = host.mActivity
            else:
                from android import mActivity as activity  # type: ignore[import-not-found]
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

    p = P()
    splash_icon_src = _get_logo_src()

    if splash_icon_src:
        logo_widget: ft.Control = ft.Image(
            src=splash_icon_src,
            width=200, # Slightly larger, but not overwhelming
            height=200,
            fit=ft.BoxFit.CONTAIN,
        )
    else:
        logo_widget = ft.Icon(
            ft.Icons.FOLDER_SHARED_ROUNDED,
            size=200,
            color=p["primary"],
        )

    brand_text = ft.Row(
        [
            ft.Text(
                "Blood", size=38, weight=ft.FontWeight.W_500, color=p["text_muted"],
                font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace",
            ),
            ft.Text(
                "Hound", size=38, weight=ft.FontWeight.W_900, color=p["text"],
                font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace",
                style=ft.TextStyle(letter_spacing=3.5),
            ),
        ],
        spacing=0, alignment=ft.MainAxisAlignment.CENTER, tight=True,
    )

    subtitle_text = ft.Text(
        "Share files over your local network", size=14, color=p["text_muted"],
        weight=ft.FontWeight.W_400, text_align=ft.TextAlign.CENTER,
        style=ft.TextStyle(letter_spacing=2.0),
    )

    dot1 = ft.Container(width=8, height=8, border_radius=4, bgcolor=p["text_muted"], animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT), opacity=0.2)
    dot2 = ft.Container(width=8, height=8, border_radius=4, bgcolor=p["text_muted"], animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT), opacity=0.4)
    dot3 = ft.Container(width=8, height=8, border_radius=4, bgcolor=p["text_muted"], animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT), opacity=0.2)

    dots_container = ft.Row([dot1, dot2, dot3], alignment=ft.MainAxisAlignment.CENTER, spacing=12, height=24, tight=True)

    splash_layer = ft.Container(
        content=ft.Column(
            [
                # --- Top space: visually smaller (optical center) ---
                ft.Container(expand=5),
                
                # --- Center: logo ---
                logo_widget,
                
                # --- Bottom space: visually larger to balance the text below ---
                ft.Container(expand=6),
                
                # --- Text + dots pinned to the bottom ---
                brand_text,
                ft.Container(height=10),
                subtitle_text,
                ft.Container(height=40),
                dots_container,
                ft.Container(height=64), # Safe bottom padding for mobile
            ],
            spacing=0, tight=True, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=p["bg"], alignment=ft.Alignment.CENTER, expand=True,
    )

    try:
        page.overlay.clear()
    except Exception:
        pass
    try:
        page.overlay.append(splash_layer)
        page.update()
    except Exception:
        pass

    if IS_ANDROID:
        try:
            from jnius import autoclass  # type: ignore[import-not-found]
            autoclass("android.media.MediaMetadataRetriever")
            autoclass("android.provider.Settings")
            autoclass("android.os.PowerManager")
        except Exception:
            pass

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
        try:
            page.run_task(fn, *args, **kwargs)
        except Exception:
            def _runner():
                try:
                    asyncio.run(fn(*args, **kwargs))
                except Exception:
                    pass
            threading.Thread(target=_runner, daemon=True).start()

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

    def on_minimize(e=None):
        try:
            page.window.minimized = True
        except Exception:
            pass

    def on_maximize(e=None):
        try:
            page.window.maximized = not page.window.maximized
        except Exception:
            pass

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
        try:
            _task = page.run_task(_close_window_async)
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

    def _theme_icon() -> tuple[ft.IconData, str]:
        m = theme_holder["mode"]
        if m == "auto": return ft.Icons.BRIGHTNESS_AUTO_ROUNDED, "Theme: Auto (system)"
        if m == "light": return ft.Icons.LIGHT_MODE_ROUNDED, "Theme: Light"
        return ft.Icons.DARK_MODE_ROUNDED, "Theme: Dark"

    def _pick_default_index(interfaces):
        private_prefixes = ("192.168.", "10.", "172.16.", "172.17.", "172.18.",
                            "172.19.", "172.20.", "172.21.", "172.22.", "172.23.",
                            "172.24.", "172.25.", "172.26.", "172.27.", "172.28.",
                            "172.29.", "172.30.", "172.31.")
        for i, (label, ip) in enumerate(interfaces):
            if label == "Wi-Fi" or any(ip.startswith(p) for p in private_prefixes):
                return i
        for i, (label, ip) in enumerate(interfaces):
            if ip == "127.0.0.1":
                return i
        return 0

    def _find_index_for_ip(interfaces, target_ip):
        for i, (_, ip) in enumerate(interfaces):
            if ip == target_ip: return i
        return -1

    def _apply_interfaces(interfaces):
        old_ip = state.iface_ip
        state.interfaces = interfaces
        if not interfaces:
            return

        wifi_idx = -1
        for i, (label, ip) in enumerate(interfaces):
            if label == "Wi-Fi" or ip.startswith("192.168.") or ip.startswith("10."):
                wifi_idx = i
                break

        if not state.iface_picked:
            state.iface_index = _pick_default_index(interfaces)
            state.iface_picked = True
        elif wifi_idx >= 0 and state.iface_ip == "0.0.0.0":
            state.iface_index = wifi_idx
        else:
            idx = _find_index_for_ip(interfaces, old_ip)
            if idx >= 0:
                state.iface_index = idx
            else:
                state.iface_index = _pick_default_index(interfaces)

        label, ip = interfaces[state.iface_index]
        state.iface_label = label
        state.iface_ip = ip

    # --- refresh_ip is now async so ActionButton can show a spinner ---
    async def refresh_ip(e=None):
        try:
            # Run the blocking scan in a background thread
            loop = asyncio.get_running_loop()
            ips = await loop.run_in_executor(None, get_all_ips)
            _apply_interfaces(ips)
            log(f"Detected {len(ips)} interfaces — {state.iface_label} · {state.iface_ip}", "ok")
            render()
            # Give Flet a moment to flush the update.
            await asyncio.sleep(0.05)
        except Exception as ex:
            log(f"Refresh failed: {ex}", "err")

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

    async def toggle_server(e=None):
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

        # ---- Always re-scan interfaces before binding ----
        # The previous state.interfaces list may be stale (Wi-Fi dropped,
        # IP renewed, etc.) since the app launched. get_all_ips() runs in
        # an executor, so it does not block the UI thread.
        try:
            loop = asyncio.get_running_loop()
            ips = await loop.run_in_executor(None, get_all_ips)
            if ips:
                _apply_interfaces(ips)
                persist_settings()
        except Exception as ex:
            log(f"Interface refresh failed: {ex}", "warn")

        valid_ips = {ip for _, ip in state.interfaces}
        if state.iface_ip not in valid_ips:
            # Safe fallback: bind to loopback only (local access).
            log("No LAN interface available — binding to 127.0.0.1 (local only).", "warn")
            state.iface_label = "Localhost"
            state.iface_ip = "127.0.0.1"
            idx = _find_index_for_ip(state.interfaces, "127.0.0.1")
            state.iface_index = idx if idx >= 0 else 0

        bind_host = state.bind_host

        try:
            server.share_dir = state.share_dir
            server.port = port
            server.bind_host = bind_host
            log(f"Starting server on {bind_host}:{port}…", "info")
            server.start()
            await asyncio.sleep(0.4)
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
        except PortInUseError:
            log(
                f"Port {port} is already in use. "
                f"Stop the other program or pick a different port.",
                "err",
            )
            state.server_running = False
        except OSError as ex:
            if "Address already in use" in str(ex):
                log(f"Port {port} is busy. Try another.", "err")
            elif "Cannot assign requested address" in str(ex):
                # Safety net: bind host turned out to be invalid despite the
                # pre-check. Retry once on loopback (always bindable, safe).
                log(f"Bind address unavailable ({bind_host}) — retrying on 127.0.0.1…", "warn")
                try:
                    server.bind_host = "127.0.0.1"
                    state.iface_label = "Localhost"
                    state.iface_ip = "127.0.0.1"
                    server.start()
                    await asyncio.sleep(0.4)
                    if server.is_alive():
                        state.server_running = True
                        log(f"Server running on 127.0.0.1:{port} (local only)", "ok")
                        log(f"Open: {state.access_url}", "info")
                    else:
                        state.server_running = False
                except PortInUseError:
                    log(
                        f"Port {port} is already in use. "
                        f"Stop the other program or pick a different port.",
                        "err",
                    )
                    state.server_running = False
                except Exception as ex2:
                    log(f"Fallback failed: {type(ex2).__name__}: {ex2}", "err")
                    state.server_running = False
            else:
                log(f"OS error: {ex}", "err")
            if not state.server_running:
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

            was_running = server.is_alive()

            if was_running:
                server.stop()
                state.server_running = False
                time.sleep(0.3)

            state.share_dir = str(p)
            persist_settings()
            log(f"Folder: {p}", "ok")

            if was_running:
                log("Restarting server on new folder…", "warn")
                try:
                    port = int(state.port)
                    bind_host = state.bind_host
                    server.share_dir = state.share_dir
                    server.port = port
                    server.bind_host = bind_host
                    server.start()
                    time.sleep(0.4)
                    if server.is_alive():
                        state.server_running = True
                        log(f"Server running on {bind_host}:{port}", "ok")
                        log(f"Open: {state.access_url}", "info")
                except PortInUseError:
                    log(
                        f"Port {state.port} is already in use. "
                        f"Stop the other program or pick a different port.",
                        "err",
                    )
                    state.server_running = False
                except Exception as ex:
                    log(f"Server start failed: {ex}", "err")
                    state.server_running = False
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
                pass

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
            log("Dialog failed.", "err")

    def on_nav(e):
        if isinstance(e, int):
            state.view = e
        else:
            try:
                state.view = e.control.selected_index
            except AttributeError:
                state.view = getattr(e, "selected_index", 0)
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

    _device_name_timer: dict[str, Any] = {"id": None}

    def set_device_name(value: str):
        state.device_name = value

        async def _delayed_save():
            await asyncio.sleep(0.5)
            persist_settings()

        try:
            if _device_name_timer["id"] is not None:
                try:
                    page.cancel_timer(_device_name_timer["id"])
                except Exception:
                    pass
            _device_name_timer["id"] = page.run_task(_delayed_save)
        except Exception:
            persist_settings()

    handlers: Dict[str, Callable[..., Any]] = {
        "log": log, "cycle_theme": cycle_theme, "set_theme": set_theme,
        "toggle_server": toggle_server,
        "pick_folder": pick_folder,
        "share_all": share_all,
        "request_permissions": lambda e=None: run_async(request_permissions, e),
        "request_battery_exemption": lambda e=None: run_async(request_battery_exemption, e),
        "refresh_ip": refresh_ip,
        "copy_url": lambda e=None: run_async(copy_url, e),
        "open_url": lambda e=None: run_async(open_url, e),
        "show_qr": lambda e=None: run_async(show_qr, e),
        "on_iface_change": on_iface_change,
        "set_port": set_port,
        "set_device_name": set_device_name,
        "_get_url": lambda: state.access_url,
    }

    root_holder = ft.Container(expand=True)
    destinations = [
        {"icon": ft.Icons.GRID_VIEW_ROUNDED, "label": "Dashboard"},
        {"icon": ft.Icons.HISTORY_ROUNDED, "label": "Activity"},
        {"icon": ft.Icons.SETTINGS_ROUNDED, "label": "Settings"},
    ]

    _last_wide: bool | None = None
    SIDEBAR_WIDTH = 200

    def render():
        nonlocal _last_wide

        p = P()
        page.bgcolor = p["bg"]
        page.theme_mode = ft.ThemeMode.DARK if current_dark() else ft.ThemeMode.LIGHT

        raw_width = page.width or (WINDOW_DEFAULT_WIDTH if not IS_ANDROID else 400)
        width = int(raw_width)

        is_mobile = width < BP.md
        is_narrow_desktop = BP.md <= width < 900

        _last_wide = not is_mobile

        theme_icon, theme_tooltip = _theme_icon()

        logo_src = _get_logo_src()
        
        # Responsive sizes for mobile vs desktop
        logo_size = 52 if is_mobile else 64
        brand_size = 22 if is_mobile else 24

        if logo_src:
            brand_logo: ft.Control = ft.Image(
                src=logo_src,
                width=logo_size,
                height=logo_size,
                fit=ft.BoxFit.CONTAIN,
            )
        else:
            brand_logo = ft.Icon(ft.Icons.FOLDER_SHARED_ROUNDED, size=logo_size, color=p["text"])

        brand_column = ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Blood", size=brand_size, weight=ft.FontWeight.W_500, color=p["text_muted"], font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace"),
                        ft.Text("Hound", size=brand_size, weight=ft.FontWeight.W_900, color=p["text"], font_family="ui-monospace, SF Mono, Menlo, Consolas, monospace"),
                    ],
                    spacing=0, tight=True
                ),
            ],
            spacing=0,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER
        )

        if not is_mobile:
            header_left = ft.Row(
                [brand_logo, ft.Container(width=Space.md), brand_column],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            )

            icon_size = 44 if not is_narrow_desktop else 40
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
            icon_size = 38
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

        effective_width = int(width - (SIDEBAR_WIDTH if not is_mobile else 0))
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

        shell_children: list[ft.Control] = [
            c for c in [
                top_spacer,
                appbar,
                ft.Row(
                    [sidebar, body_container],
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
                bottom_spacer,
            ] if c is not None
        ]

        shell = ft.Column(shell_children, spacing=0, expand=True)
        root_holder.content = ft.Container(shell, bgcolor=p["bg"], expand=True)
        safe_update()

    def on_resize(e):
        nonlocal _last_wide
        try:
            raw_width = page.width or (WINDOW_DEFAULT_WIDTH if not IS_ANDROID else 400)
            width = int(raw_width)
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
    try:
        page.on_disconnect = on_disconnect
    except Exception as ex:
        log(f"on_disconnect not supported: {ex}", "warn")

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

    run_async(refresh_ip)

    page.add(root_holder)
    render()
    page.update()

    first_today = _is_first_launch_today()

    SPLASH_MIN_SHOW_FIRST = 5.0
    SPLASH_MIN_SHOW_RETURN = 3.0
    SPLASH_MAX_WAIT = 10.0

    splash_min_show = SPLASH_MIN_SHOW_FIRST if first_today else SPLASH_MIN_SHOW_RETURN
    app_ready = {"value": True}

    async def _remove_splash_async():
        async def _animate_dots():
            try:
                while not splash_state["removed"]:
                    dot1.opacity = 1.0
                    dot2.opacity = 0.3
                    dot3.opacity = 0.2
                    try: dots_container.update()
                    except Exception: pass
                    await asyncio.sleep(0.25)
                    if splash_state["removed"]: break

                    dot1.opacity = 0.3
                    dot2.opacity = 1.0
                    dot3.opacity = 0.2
                    try: dots_container.update()
                    except Exception: pass
                    await asyncio.sleep(0.25)
                    if splash_state["removed"]: break

                    dot1.opacity = 0.2
                    dot2.opacity = 0.3
                    dot3.opacity = 1.0
                    try: dots_container.update()
                    except Exception: pass
                    await asyncio.sleep(0.25)
            except Exception:
                pass

        dot_task = asyncio.create_task(_animate_dots())
        start_time = time.time()

        try:
            while not app_ready["value"] and (time.time() - start_time) < SPLASH_MAX_WAIT:
                await asyncio.sleep(0.1)

            elapsed = time.time() - start_time
            if elapsed < splash_min_show:
                await asyncio.sleep(splash_min_show - elapsed)

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
                    w = int(page.window.width or WINDOW_DEFAULT_WIDTH)
                    h = int(page.window.height or WINDOW_DEFAULT_HEIGHT)
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
            time.sleep(splash_min_show)
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
        color_scheme=ft.ColorScheme(primary="#18181b", surface="#ffffff"),
        navigation_bar_theme=ft.NavigationBarTheme(
            bgcolor="#ffffff", indicator_color="transparent",
            label_text_style=ft.TextStyle(color="#18181b", size=12, font_family="Inter"),
        ),
        system_overlay_style=ft.SystemOverlayStyle(
            status_bar_color="#ffffff",
            status_bar_icon_brightness=ft.Brightness.DARK,
        ),
    )
    page.dark_theme = ft.Theme(
        font_family="Inter",
        color_scheme=ft.ColorScheme(primary="#fafafa", surface="#000000"),
        navigation_bar_theme=ft.NavigationBarTheme(
            bgcolor="#000000", indicator_color="transparent",
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