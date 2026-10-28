"""Web UI — helper module (favicon now loaded from static folder)."""
from __future__ import annotations

# Favicon is now handled directly in index.html via:
# <link rel="icon" type="image/png" href="{{ url_for('static', filename='favicon.png') }}">
FAVICON_SVG = ""