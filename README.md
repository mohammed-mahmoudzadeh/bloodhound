<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="src/assets/logo_dark.png">
    <source media="(prefers-color-scheme: light)" srcset="src/assets/logo_light.png">
    <img src="src/assets/logo_light.png" alt="BitBeagle logo" width="120" height="120">
  </picture>
</p>

<h1 align="center">BitBeagle</h1>

<p align="center">
  <strong>Share files. Stay local. Keep it simple.</strong>
</p>

<p align="center">
  A modern, cross-platform file-sharing application that turns any folder on your device into a browsable, streamable web library — over your local network.
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python"></a>
  <a href="https://flet.dev/"><img src="https://img.shields.io/badge/Flet-1.0.4-02569B.svg" alt="Flet"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-3.0-3BABC3.svg" alt="Flask"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/platform-Android%20%7C%20Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg" alt="Platforms">
  <a href="https://github.com/mohammed-mahmoudzadeh/bitbeagle/stargazers"><img src="https://img.shields.io/github/stars/mohammed-mahmoudzadeh/bitbeagle?style=social" alt="Stars"></a>
  <a href="https://github.com/mohammed-mahmoudzadeh/bitbeagle/network/members"><img src="https://img.shields.io/github/forks/mohammed-mahmoudzadeh/bitbeagle?style=social" alt="Forks"></a>
</p>

---

## 📖 Overview

Moving files between devices shouldn't require uploading them to a cloud service or creating an account.

**BitBeagle** runs a lightweight web server on your device and lets other devices on your local network access the files you choose to share. Open the generated address in a browser and browse your files directly — no cloud, no accounts, no hassle.

Built with **Python**, **Flet** (Flutter for Python), and **Flask**, it combines a native-style application interface with a fast HTTP file server, plus a standalone CLI for headless environments.

### Which mode should I use?

| Mode | Best for |
|------|----------|
| **GUI (Flet)** | Desktop and mobile app with dashboard, activity log, and settings |
| **CLI (headless)** | Terminals, servers, scripts, and environments without a display |

Both modes share the same Flask file-browser backend.

---

## 📸 Screenshots

<p align="center">
  <a href="docs/screenshots/">
    <img src="https://img.shields.io/badge/📸_View_Screenshots-docs%2Fscreenshots-blue?style=for-the-badge" alt="View Screenshots">
  </a>
</p>

> Curious what BitBeagle looks like? Browse the full gallery in [`docs/screenshots/`](docs/screenshots/).
---

## ✨ Features

### 🖥️ Application (Flet)

- **Modern, minimal UI** — clean monochrome design with automatic light/dark theme support.
- **Animated splash screen** — branded launch screen with smart timing (first launch of the day shows longer).
- **Dashboard** — start/stop the server, pick a folder, choose a network interface.
- **Activity log** — real-time view of server events.
- **Settings** — theme, device name, default port.
- **Adaptive layout** — responds to desktop, tablet, and mobile sizes.
- **Automatic theme sync** — status bar and system chrome match the app theme.

### 🌐 Web File Browser

- **Directory browsing** — navigate the shared folder tree.
- **Recursive search** — find files across nested directories instantly.
- **Video streaming** — full HTTP Range request support for playback and smooth seeking without re-downloading.
- **Thumbnails** — automatic previews for images and videos (via FFmpeg).
- **Live updates** — Server-Sent Events (SSE) notify browsers of file changes.
- **Inline previews** — images, videos, audio, PDFs, and text files open directly in the browser.
- **Responsive UI** — works on phones, tablets, and desktops.
- **Resume playback** — remember where you left off in videos and audio.

### ⌨️ Headless CLI

Run the file-sharing server directly from a terminal — no GUI required.

```bash
bitbeagle --dir /path/to/folder
```

Perfect for:

· Terminal-based workflows
· Servers and lightweight deployments
· Environments without a display
· Automation and scripts

🤖 Android Integration

· Storage permission handling via flet-permission-handler.
· Battery optimization exemption — keep the server alive in the background.
· Foreground service support — survives Android's app lifecycle.
· Native splash screen — matches the app's branding.
· Adaptive icons — follows Android's icon guidelines.

---

🚀 Quick Start

Prerequisites

· Python 3.10 or newer
· FFmpeg (optional — for thumbnails and video probing)
· pip (latest version recommended)

Installation

```bash
# 1. Clone the repository
git clone https://github.com/mohammed-mahmoudzadeh/bitbeagle.git
cd bitbeagle

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\Activate.ps1        # Windows PowerShell

# 3. Install dependencies (includes the CLI entry point)
pip install -e .

# 4. (Optional) Add desktop extras for MediaInfo support
pip install -e ".[desktop]"
```

Launch the GUI Application

```bash
flet run
```

Or directly:

```bash
python src/main.py
```

First-time setup:

1. Click Pick folder and choose the directory you want to share.
2. Select the network interface (auto-detected).
3. Click Start Server.
4. Open the displayed URL on another device on the same network.

---

⌨️ CLI Usage

After pip install -e ., the bitbeagle command is available on your PATH:

```bash
bitbeagle --dir ~/Documents
```

If you prefer to run from source without installing:

```bash
# Linux / macOS
PYTHONPATH=src python -m bitbeagle.core.share --dir /path/to/folder

# Windows PowerShell
$env:PYTHONPATH = "src"
python -m bitbeagle.core.share --dir "C:\path\to\folder"
```

CLI options

Flag Short Description
--dir -d Directory to share (required)
--port -p Port to listen on (default: 8000)
--host -H Bind address (default: 0.0.0.0)
--no-thumbs — Disable thumbnail generation
--debug — Enable Flask debug mode ⚠️ unsafe on shared networks — see Security

Bash completion

A completion script is included at completion/bitbeagle. To install it manually:

```bash
# System-wide (requires sudo)
sudo cp completion/bitbeagle /etc/bash_completion.d/

# Per-user
mkdir -p ~/.local/share/bash-completion/completions
cp completion/bitbeagle ~/.local/share/bash-completion/completions/
```

Then reload your shell:

```bash
source ~/.bashrc
```

Note: pip install does not install the completion script automatically. Install it manually using the commands above.

---

📱 Build for Android

Requirements

· Flet ≥ 1.0.4
· Flutter SDK ≥ 3.x
· Android SDK — Platform, Build-Tools, and Platform-Tools
· Java JDK 17 (required by Gradle)
· ANDROID_HOME and ANDROID_SDK_ROOT environment variables set
· Accepted SDK licenses (sdkmanager --licenses)

Note: Flet's Android build bundles its own Python interpreter (typically 3.11 or 3.12 depending on Flet version). Make sure requires-python in pyproject.toml is compatible with the version Flet ships — check the Flet docs before changing it.

Build the APK

```bash
flet build apk --arch arm64-v8a
```

Output: build/apk/app-release.apk

Install on device

```bash
adb install build/apk/app-release.apk
```

Android permissions, icons, and splash screens are configured in pyproject.toml. Runtime storage permissions are handled by the app.

---

📁 Project Layout

```
bitbeagle/
├── pyproject.toml              # Build config, dependencies, Android settings
├── requirements.txt            # Pinned Python dependencies
├── completion/
│   └── bitbeagle              # Bash CLI completion
└── src/
    ├── main.py                 # Flet entry point
    ├── assets/                 # Icons and splash images
    │   ├── icon.png
    │   ├── logo_dark.png
    │   ├── logo_light.png
    │   └── splash_android*.png
    └── bitbeagle/
        ├── app.py              # Flet UI shell
        ├── state.py            # Shared application state
        ├── settings_store.py   # Local settings persistence
        ├── theme/              # Colors, typography, spacing tokens
        ├── components/         # Reusable UI components
        ├── views/              # Dashboard, Activity, Settings
        └── core/
            ├── server.py       # Flask server lifecycle wrapper
            ├── network.py      # IPv4 interface discovery
            └── share/          # Flask web app
                ├── __main__.py # CLI entry point
                ├── routes.py   # URL rules
                ├── files.py    # File serving (Range, ETag)
                ├── search.py   # Recursive search
                ├── thumbs.py   # Thumbnail generation
                ├── watcher.py  # SSE filesystem watcher
                ├── templates/  # HTML templates
                └── static/     # CSS and JS
```

Key files

Path Responsibility
pyproject.toml Build config, app metadata, dependencies, Android settings
src/main.py Application entry point
src/bitbeagle/app.py Flet UI shell and rendering lifecycle
src/bitbeagle/state.py Shared application state
src/bitbeagle/theme/ Design tokens (colors, typography, spacing)
src/bitbeagle/components/ Reusable UI components
src/bitbeagle/views/ Dashboard, Activity, Settings views
src/bitbeagle/core/server.py Flask server lifecycle wrapper
src/bitbeagle/core/network.py IPv4 interface discovery
src/bitbeagle/core/share/ Flask routes, templates, static assets, streaming, thumbnails, watcher

---

⚙️ Configuration

Network interfaces

BitBeagle auto-detects available IPv4 interfaces. You can choose:

Address Behavior
0.0.0.0 Listen on all IPv4 interfaces
192.168.x.x Listen on a specific LAN interface (recommended)
Hotspot IP Allow connections through a mobile hotspot

Tip: For security, bind to a specific LAN address rather than 0.0.0.0 when possible. This prevents exposure on other networks (e.g., public Wi-Fi).

Port

Default port is 8000. You can change it from the Dashboard or Settings.

Choose a port between 1024 and 65535 that isn't already in use.

Shared directory

The selected folder becomes the root of the web file browser. The app must have read access to the folder and its contents.

Android permissions

The following permissions are requested (configured in pyproject.toml):

· INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE
· READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO
· MANAGE_EXTERNAL_STORAGE
· FOREGROUND_SERVICE, FOREGROUND_SERVICE_DATA_SYNC
· POST_NOTIFICATIONS
· REQUEST_IGNORE_BATTERY_OPTIMIZATIONS

Grant these when prompted. The app also offers a Battery Exemption button in the Dashboard.

⚠️ Note for Play Store distribution: MANAGE_EXTERNAL_STORAGE is restricted by Google Play for new apps. If you plan to publish on Play Store, you'll need to migrate to Scoped Storage / SAF (Storage Access Framework) instead.

Optional dependencies

· FFmpeg — for thumbnail generation and video quality detection. If missing, thumbnails are skipped (video streaming still works).
· MediaInfo — used by pymediainfo on desktop for more accurate video probing. Install with pip install -e ".[desktop]".

---

🔒 Security Considerations

BitBeagle has no built-in authentication. Anyone who can reach the server URL and port can browse and download shared files. Treat it as a trusted-LAN tool.

· ✅ Share only folders you intend to expose on your LAN.
· ✅ Bind to a specific LAN interface when possible.
· ✅ Use a firewall to restrict access.
· ✅ Close the server when you're done.
· ❌ Do not expose BitBeagle directly to the internet.
· ❌ Do not share sensitive directories on untrusted networks.

Additional notes

· No TLS — traffic is plain HTTP. Do not use on untrusted networks (public Wi-Fi, hotel LANs, co-working spaces).
· No CORS — browsers block cross-origin reads; other websites cannot fetch your files via JavaScript even if they know the URL.
· Symlinks — the server resolves paths and rejects those that escape the shared root. See core/share/files.py when auditing.
· --debug flag — Flask's debug mode enables Werkzeug's interactive debugger, which permits remote code execution. Use only on 127.0.0.1 or a trusted host.

If you need remote access, use a VPN (like WireGuard or Tailscale) rather than opening ports on your router.

---

🛠️ Troubleshooting

The server won't start

· Check that the port is free (try lsof -i :8000 on Linux/macOS).
· Ensure the shared folder exists and is readable.
· Check the Activity log in the app for details.

Files don't appear in the browser

· Confirm that the folder was selected correctly.
· Refresh the browser page.
· Check that the server is still running.

Android: server stops in background

· Grant "All files access" permission.
· Enable battery optimization exemption (button in Dashboard).
· Keep the app in recent apps (don't swipe it away).

Video won't play in browser

· Make sure the format is supported (MP4/H.264 is the safest).
· Try a different browser (Chrome / Edge / Firefox).
· Check the Activity log for streaming errors.

Bash completion not working

· Confirm the script was copied to a directory on your $BASH_COMPLETION_USER_DIR path (see Bash completion).
· Run source ~/.bashrc or open a new terminal.

---

💬 Community

· GitHub Discussions — ask questions, share ideas
· GitHub Issues — report bugs

---

🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository.
2. Create a branch: git checkout -b feature/my-feature.
3. Make your changes — follow the existing code style (English comments, no deprecated APIs).
4. Test your changes locally (desktop + Android if possible).
5. Commit with a clear message: git commit -m "feat: add my feature".
6. Push and open a Pull Request.

Coding standards

· All code comments and docstrings in English.
· Follow Flet 1.0.4 conventions (no deprecated APIs).
· Keep the modular architecture (core/, views/, components/, theme/).

Reporting bugs

Please include:

· OS and version (e.g., Android 13, Ubuntu 22.04)
· Device model (if Android)
· Steps to reproduce
· Expected vs. actual behavior
· Relevant logs from the Activity view

---

📄 License

This project is licensed under the MIT License — see the LICENSE file for details.

---

🙏 Acknowledgements

· Flet — Python UI framework that powers the app.
· Flask — lightweight web server.
· Werkzeug — WSGI toolkit.
· Rich — beautiful terminal output for the CLI.
· qrcode — QR code generation for quick pairing.
· The open-source community for inspiration and countless helpful libraries.

---

<p align="center">
  <em>Made with care for the local-first community.</em>
</p>

<p align="center">
  <a href="https://github.com/mohammed-mahmoudzadeh/bitbeagle/issues">Report Bug</a>
  ·
  <a href="https://github.com/mohammed-mahmoudzadeh/bitbeagle/issues">Request Feature</a>
  ·
  <a href="#bitbeagle">Back to top</a>
</p>
