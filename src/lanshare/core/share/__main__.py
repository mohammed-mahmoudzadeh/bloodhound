"""CLI: python -m lanshare.core.share --dir . --port 8000"""
from __future__ import annotations

import argparse
from pathlib import Path

from . import create_app
from .config import (
    MEDIAINFO_BIN, FFMPEG_BIN,
    get_share_dir, get_port, get_thumb_dir,
)
from .network import list_network_interfaces
from .server import run_tuned_server


def parse_args():
    parser = argparse.ArgumentParser(
        description="Share the current (or specified) directory over the web."
    )
    parser.add_argument("-d", "--dir", default=None,
                        help="Directory to share (default: current working directory).")
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Port to listen on (default: 8000).")
    parser.add_argument("--host", default="0.0.0.0",
                        help="Interface to bind (default: 0.0.0.0).")
    return parser.parse_args()


def main():
    args = parse_args()

    share = Path(args.dir).expanduser().resolve() if args.dir else Path.cwd().resolve()
    if not share.exists() or not share.is_dir():
        raise SystemExit(f"Error: not a directory: {share}")

    app = create_app(share_dir=share, port=args.port)

    share_dir = get_share_dir()
    port = get_port()
    thumb_dir = get_thumb_dir()

    ifaces = list_network_interfaces()

    RESET = "\033[0m"
    DIM   = "\033[2m"
    BOLD  = "\033[1m"
    GREEN = "\033[32m"
    CYAN  = "\033[36m"

    W = 52
    line = DIM + "─" * W + RESET

    def fmt_row(label, value, color=""):
        return f"  {DIM}{label:<12}{RESET} {color}{value}{RESET}"

    print()
    print(line)
    print(f"  {BOLD}Shared Files{RESET} {DIM}— local web server{RESET}")
    print(line)
    print()
    print(fmt_row("Directory", str(share_dir), CYAN))
    print(fmt_row("Port",      str(port),      CYAN))
    if MEDIAINFO_BIN:
        print(fmt_row("MediaInfo", "ready", GREEN))
    else:
        print(fmt_row("MediaInfo", "not installed", "\033[33m"))
    if FFMPEG_BIN and thumb_dir:
        print(fmt_row("Thumbnails", "enabled", GREEN))
    else:
        print(fmt_row("Thumbnails", "ffmpeg not found", "\033[33m"))
    print(fmt_row("Live updates", "SSE enabled", GREEN))
    print(fmt_row("Search", "recursive", GREEN))
    print(fmt_row("Streaming", "tuned for video", GREEN))
    print()
    print(f"  {DIM}Open in browser:{RESET}")
    print(f"    {GREEN}http://127.0.0.1:{port}/{RESET}")
    if ifaces:
        for name, ip in ifaces:
            print(f"    {GREEN}http://{ip}:{port}/{RESET}  {DIM}[{name}]{RESET}")
    else:
        print(f"    {DIM}(no external interface detected){RESET}")
    print()
    print(f"  {DIM}Press Ctrl+C to stop{RESET}")
    print(line)
    print()

    run_tuned_server(app, args.host, port)


if __name__ == "__main__":
    main()
