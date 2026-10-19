<div align="center">

# 📡 LANShare

### Share files over your local network — from Android or desktop.

*A lightweight, elegant web interface for turning any folder into a browsable, streamable library.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flet](https://img.shields.io/badge/Flet-1.0.4-00B0FF?style=for-the-badge&logo=flutter&logoColor=white)](https://flet.dev)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

[![Platform](https://img.shields.io/badge/Platform-Android%20%7C%20Linux%20%7C%20Windows%20%7C%20macOS-lightgrey?style=for-the-badge)](#-build-for-android)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=for-the-badge)](CONTRIBUTING.md)
[![Made with ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red?style=for-the-badge)](#)

[Features](#-features) · [Quick Start](#-quick-start) · [Screenshots](#-screenshots) · [Build for Android](#-build-for-android) · [Architecture](#-architecture) · [License](#-license)

</div>

---

## ✨ Why LANShare?

Turn any folder into a shareable web library in **one tap**. No cloud, no accounts, no setup — everything stays on your local network.

- 🚀 **Zero config** — pick a folder, hit start, share the link.
- 🔒 **Private by design** — files never leave your Wi-Fi.
- 🎨 **Beautiful UI** — responsive, light/dark, crafted for desktop *and* phone.
- 🎬 **Rich previews** — images, video, audio, PDF, and text render in-browser.
- 📱 **Works everywhere** — Android app + desktop builds from a single codebase.

---

## 🚀 Features

| | Feature | Description |
|---|---|---|
| ⚡ | **One-tap server** | Start/stop from the app — no terminal required. |
| 🧭 | **Adaptive layout** | Sidebar on desktop, bottom nav on mobile. |
| 🌗 | **Light / Dark / Auto** | Full theme system, remembers your choice. |
| 🖼️ | **Media previews** | Images, video, audio, PDF, and text open inline. |
| 🏷️ | **Video quality badges** | Auto-detected via `mediainfo` / `ffprobe` (1080p · FHD, etc.). |
| 🔍 | **Grid / List + Search** | Live filtering with instant view switching. |
| 📲 | **QR code** | Scan to connect from any phone on the network. |
| 🤖 | **Android-aware** | Storage permission handling + `MANAGE_EXTERNAL_STORAGE`. |
| 🛑 | **Safe shutdown** | Auto-stops on window close or disconnect. |
| 🔌 | **Interface selection** | Bind to Wi-Fi, hotspot, Ethernet, or all interfaces. |

---

## 📸 Screenshots

<div align="center">

| Dashboard | Web UI |
|:-:|:-:|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Web UI](docs/screenshots/webui.png) |

| Video Preview | Mobile |
|:-:|:-:|
| ![Video](docs/screenshots/video.png) | ![Mobile](docs/screenshots/mobile.png) |

</div>

> 💡 Add your screenshots to `docs/screenshots/` and update the paths above.

---

## 🏁 Quick Start

### 1. Clone

```bash
git clone https://github.com/<you>/lanshare.git
cd lanshare
```

2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run

```bash
PYTHONPATH=src python -m lanshare.main
```

On Windows:

```bat
set PYTHONPATH=src
python -m lanshare.main
```

Then:

1. Click Pick folder (or Share all on Android).
2. Tap Start Server.
3. Open the shown URL — or scan the QR code — from any device on your network.

---

🤖 Build for Android

```bash
flet build apk --arch arm64-v8a
```

Output: build/apk/app-release.apk

Requires the Flutter SDK and Android SDK. See the Flet build docs for details.

---

🏗️ Architecture

LANShare is split into a Flet UI shell and a Flask file server that runs in a background thread.

```
┌─────────────────────────────────────────────────────────────┐
│                        Flet UI (app shell)                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ Dashboard  │  │  Activity  │  │  Settings  │             │
│  └────────────┘  └────────────┘  └────────────┘             │
│                                                             │
│         AppState ◄──────► Render loop (adaptive)            │
└───────────────────────┬─────────────────────────────────────┘
                        │ start() / stop()
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                FlaskServer (daemon thread)                  │
│         ThreadedWSGIServer(bind_host, port, app)            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask web app (share.py)                  │
│    browse() · previews · search · quality probing · QR      │
└───────────────────────┬─────────────────────────────────────┘
                        │ http://<LAN-IP>:<port>
                        ▼
              📱 Any device on your Wi-Fi
```

Request lifecycle

1. Flet shell gathers interfaces via core/network.py and renders the UI.
2. Tapping Start Server → FlaskServer.start() binds a ThreadedWSGIServer.
3. A phone opens http://192.168.x.x:8000 → browse() renders the file list.
4. File clicks stream via send_file(conditional=True) (supports range requests for video).
5. Stop / window close / disconnect → shutdown() + server_close().

---

📁 Project Layout

```
lanshare/
├── pyproject.toml          # build config, Android permissions, icons
├── requirements.txt        # pinned dependencies
├── README.md
├── LICENSE
├── pip.conf                # mirror config (Aliyun + pypi.flet.dev)
└── src/
    ├── main.py             # entry point
    ├── assets/             # icon, splash
    └── lanshare/
        ├── __init__.py
        ├── app.py          # Flet app shell, splash, render loop
        ├── config.py       # env flags & constants
        ├── state.py        # AppState dataclass
        ├── theme/          # design tokens (colors, typography, spacing)
        ├── components/     # reusable UI primitives
        ├── views/          # dashboard, activity, settings
        └── core/
            ├── server.py       # FlaskServer wrapper
            ├── share.py        # Flask file-browser app
            ├── network.py      # IPv4 interface discovery
            ├── permissions.py  # Android permission handling
            ├── qr.py           # SVG QR + asset data URIs
            └── fileinfo.py     # fast folder statistics
```

---

🧰 Tech Stack

Layer Technology
UI framework Flet 1.0.4 (Flutter under the hood)
Web server Flask 3.x + Werkzeug
QR generation qrcode (SVG backend)
Network discovery ifaddr (desktop), pyjnius (Android)
Video probing mediainfo / ffprobe (optional)
Packaging flet build apk

---

⚙️ Configuration

Ports

Default port is 8000. Change it on the Dashboard (valid range: 1024–65535).

Interfaces

The Dashboard dropdown lists every detected IPv4 interface:

Label Example Notes
All Interfaces 0.0.0.0 Default — reachable on any network
Wi-Fi 192.168.1.42 Bind to a specific Wi-Fi adapter
Hotspot 192.168.43.1 Android tethering
Ethernet 10.0.0.5 Wired LAN

Android permissions

Declared in pyproject.toml:

```toml
[tool.flet.android.permission]
"android.permission.INTERNET" = true
"android.permission.ACCESS_NETWORK_STATE" = true
"android.permission.ACCESS_WIFI_STATE" = true
"android.permission.READ_MEDIA_IMAGES" = true
"android.permission.READ_MEDIA_VIDEO" = true
"android.permission.READ_MEDIA_AUDIO" = true
"android.permission.MANAGE_EXTERNAL_STORAGE" = true
```

Use the in-app Permissions button to grant storage access.

---

❓ FAQ

<details>
<summary><b>Other devices can't connect — what's wrong?</b></summary>

1. Make sure both devices are on the same Wi-Fi network.
2. Check that the server is Online (green chip).
3. Some routers block client-to-client traffic (AP isolation) — disable it.
4. On Windows, allow Python through the firewall on first run.
5. Try binding to a specific interface instead of 0.0.0.0.

</details>

<details>
<summary><b>Videos won't play in the browser.</b></summary>

Browsers support a limited set of codecs. mp4 (H.264/AAC) and webm (VP8/VP9) are the safest.
For .mkv / .mov, LANShare serves them with a compatible MIME type, but playback depends on the browser.

</details>

<details>
<summary><b>Quality badges don't appear.</b></summary>

Video quality requires mediainfo or ffprobe to be installed and on your PATH:

```bash
# Debian / Ubuntu
sudo apt install mediainfo

# macOS
brew install mediainfo

# Windows
winget install MediaInfo.MediaInfo
```

</details>

<details>
<summary><b>Port 8000 is busy.</b></summary>

Change the port in the Dashboard (e.g. 8080, 9000) and start again.

</details>

<details>
<summary><b>Can I use this over the internet?</b></summary>

LANShare is designed for local networks only. Exposing it publicly requires a reverse proxy, TLS, and authentication — none of which are built in.

</details>

---

🗺️ Roadmap

☐ Upload support from the web UI
☐ Multi-folder sharing
☐ Optional basic authentication
☐ File rename / delete actions
☐ PWA install for the web UI
☐ Desktop installers (.exe, .dmg, .AppImage)

---

🤝 Contributing

Contributions are welcome! Please:

1. Fork the repo and create a feature branch: git checkout -b feat/my-feature
2. Follow existing code style (PEP 8, type hints where useful).
3. Keep UI changes consistent with the design tokens in theme/.
4. Open a PR with a clear description and screenshots if applicable.

---

🐛 Reporting Bugs

When filing an issue, please include:

· OS + version (Android / Linux / Windows / macOS)
· Python version (python --version)
· Flet version (pip show flet)
· Steps to reproduce
· Relevant logs from the Activity tab

---

📄 License

This project is licensed under the MIT License — see LICENSE for details.

You are free to use, modify, and distribute it, including for commercial purposes, as long as the copyright notice is preserved.

---

<div align="center">

Built with Flet + Flask

⭐ If LANShare is useful to you, consider giving it a star — it helps others find it.

⬆ Back to top

</div>

