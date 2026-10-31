"""Standalone CLI entry point for the BitBeagle Flask server."""
from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path

try:
    import argcomplete
    HAS_ARGCOMPLETE = True
except ImportError:
    HAS_ARGCOMPLETE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from . import create_app
from .config import (
    DEFAULT_PORT, PORT_MIN, PORT_MAX, 
    get_port, MEDIAINFO_BIN, FFPROBE_BIN, THUMB_SIZE_IMG
)
from .network import list_network_interfaces
from .thumbs import ensure_thumb_dir

console = Console() if HAS_RICH else None


def _print_banner_rich(share_dir: Path, host: str, port: int, no_thumbs: bool) -> None:
    """Print a clean, structured startup banner matching the requested layout."""
    console.print()

    # Header
    header = Table(show_header=False, box=box.SIMPLE, padding=(0, 0))
    header.add_column("Title")
    header.add_row("[bold white]Shared Files[/bold white] [dim]— local web server[/dim]")
    
    # Top border
    console.print("─" * 60, style="dim")
    console.print(header)
    
    # Info rows
    info = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    info.add_column("Key", style="white")
    info.add_column("Value", style="cyan")
    
    info.add_row("Directory", str(share_dir))
    info.add_row("Port", str(port))
    
    # MediaInfo status
    if MEDIAINFO_BIN:
        info.add_row("MediaInfo", "[green]installed[/green]")
    else:
        info.add_row("MediaInfo", "[red]not installed[/red]")
        
    # Thumbnails
    if no_thumbs:
        info.add_row("Thumbnails", "[red]disabled[/red]")
    else:
        info.add_row("Thumbnails", "[green]enabled[/green]")
        
    # Static features (these are always true based on the project architecture)
    info.add_row("Live updates", "[green]SSE enabled[/green]")
    info.add_row("Search", "[green]recursive[/green]")
    info.add_row("Streaming", "[green]tuned for video[/green]")
    
    console.print(info)
    
    # URLs
    console.print()
    console.print("[white]Open in browser:[/white]")
    
    interfaces = list_network_interfaces()
    has_iface = False
    for name, ip in interfaces:
        if ip in ("0.0.0.0",):
            continue
        label = f"[{name}]" if name not in ("local",) else ""
        # Use localhost for 127.0.0.1, but still show the IP if it's something else
        if ip == "127.0.0.1":
            console.print(f"  [cyan]http://127.0.0.1:{port}/[/cyan]")
        else:
            console.print(f"  [cyan]http://{ip}:{port}/[/cyan]  [dim]{label}[/dim]")
        has_iface = True

    if not has_iface:
        console.print(f"  [cyan]http://127.0.0.1:{port}/[/cyan]")

    # Footer
    console.print()
    console.print("[dim]Press Ctrl+C to stop[/dim]")
    console.print("─" * 60, style="dim")
    console.print()


def _print_banner_plain(share_dir: Path, host: str, port: int) -> None:
    """Fallback plain-text banner."""
    print()
    print("─" * 60)
    print("Shared Files — local web server")
    print("─" * 60)
    print(f"Directory    {share_dir}")
    print(f"Port         {port}")
    print("Press Ctrl+C to stop")
    print("─" * 60)
    print()


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bitbeagle",
        description="Run the BitBeagle Flask server standalone (without Flet UI).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Use a custom completer for --dir to suggest directories
    def dir_completer(prefix, **kwargs):
        return (d for d in os.listdir('.') if d.startswith(prefix) and os.path.isdir(d))

    parser.add_argument(
        "--dir", "-d", dest="share_dir", required=True,
        help="Directory to share (required).",
        metavar="SHARE_DIR"
    ).completer = dir_completer

    parser.add_argument(
        "--port", "-p", type=int, default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})."
    )
    parser.add_argument(
        "--host", "-H", default="0.0.0.0",
        help="Bind address (default: 0.0.0.0)."
    )
    parser.add_argument(
        "--no-thumbs", action="store_true",
        help="Disable thumbnail generation."
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable Flask debug mode (auto-reload)."
    )

    # Enable Tab autocomplete if argcomplete is installed
    if HAS_ARGCOMPLETE:
        argcomplete.autocomplete(parser)

    args = parser.parse_args(argv)

    if not (PORT_MIN <= args.port <= PORT_MAX):
        parser.error(f"--port must be between {PORT_MIN} and {PORT_MAX} (got {args.port}).")

    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    share_path = Path(args.share_dir).expanduser().resolve()
    if not share_path.exists() or not share_path.is_dir():
        msg = f"Directory not found or not a directory: {share_path}"
        if HAS_RICH:
            console.print(f"[red]{msg}[/red]")
        else:
            print(f"error: {msg}", file=sys.stderr)
        return 1

    if not args.no_thumbs:
        ensure_thumb_dir()

    if HAS_RICH:
        _print_banner_rich(share_path, args.host, args.port, args.no_thumbs)
    else:
        _print_banner_plain(share_path, args.host, args.port)

    app = create_app(share_dir=str(share_path), port=args.port)

    try:
        app.run(
            host=args.host,
            port=args.port,
            threaded=True,
            debug=args.debug,
            use_reloader=args.debug,
        )
    except KeyboardInterrupt:
        if HAS_RICH:
            console.print("\n[yellow]Stopped by user.[/yellow]")
        else:
            print("\nStopped by user.")
        return 0
    except OSError as ex:
        if HAS_RICH:
            console.print(f"[red]OS Error:[/red] {ex}")
        else:
            print(f"error: {ex}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())