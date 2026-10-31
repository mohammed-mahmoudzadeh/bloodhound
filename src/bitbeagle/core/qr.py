"""QR code generation — SVG based (no pillow dependency)."""
from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path


def make_qr_data_uri(url: str) -> str | None:
    """Generate a QR code as a data URI (base64 SVG).

    Always uses black modules on a white background for maximum scanner compatibility.
    The SVG itself has a white background so it works in both light and dark themes.
    """
    try:
        import qrcode
        import qrcode.image.svg
        from qrcode.constants import ERROR_CORRECT_M
    except ImportError:
        return None

    try:
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=2,
            image_factory=factory,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image()

        buf = BytesIO()
        img.save(buf)
        svg_bytes = buf.getvalue()

        b64 = base64.b64encode(svg_bytes).decode("ascii")
        return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return None


def image_as_data_uri(filename: str) -> str | None:
    """Load an asset image and return it as a base64 data URI."""
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent.parent / "assets" / filename,
        here.parent.parent / "assets" / filename,
        Path.cwd() / "assets" / filename,
        Path.cwd() / "src" / "assets" / filename,
    ]

    for path in candidates:
        if path.is_file():
            try:
                with open(path, "rb") as f:
                    data = f.read()
                ext = path.suffix.lower().lstrip(".")
                mime = {
                    "png": "image/png",
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "svg": "image/svg+xml",
                    "webp": "image/webp",
                }.get(ext, "image/png")
                b64 = base64.b64encode(data).decode("ascii")
                return f"data:{mime};base64,{b64}"
            except Exception:
                continue

    return None