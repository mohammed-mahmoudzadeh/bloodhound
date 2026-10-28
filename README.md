# BloodHound

**Share files. Stay local. Keep it simple.**

BloodHound is a cross-platform file-sharing application that turns a folder on your device into a browsable, streamable web library over your local network.

Built with **Python, Flet, and Flask**, it combines a native-style application interface with a lightweight web server, plus a standalone CLI for headless environments.


<p align="center">
  <a href="https://github.com/mohammed-mahmoudzadeh/bloodhound">
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://flet.dev">
    <img src="https://img.shields.io/badge/UI-Flet-00B0FF?style=flat-square&logo=flutter&logoColor=white" alt="Flet">
  </a>
  <a href="https://flask.palletsprojects.com">
    <img src="https://img.shields.io/badge/Server-Flask-3BABC3?style=flat-square&logo=flask&logoColor=white" alt="Flask">
  </a>
  <img src="https://img.shields.io/badge/Platform-Android%20%7C%20Windows%20%7C%20Linux%20%7C%20macOS-64748b?style=flat-square" alt="Platforms">
  <a href="https://github.com/mohammed-mahmoudzadeh/bloodhound/stargazers">
    <img src="https://img.shields.io/github/stars/mohammed-mahmoudzadeh/bloodhound?style=flat-square" alt="GitHub Stars">
  </a>
</p>

---

## Why BloodHound?

Moving files between devices shouldn't require uploading them to a cloud service or creating an account.

BloodHound runs a web server on your device and lets other devices on your local network access the files you choose to share. Open the generated address in a browser and browse your files directly.

- **Local-first sharing** — serve files directly from your device over your local network.
- **Two ways to run** — use the graphical application or launch the standalone CLI.
- **Browser-based access** — access shared files from phones, tablets, and computers.
- **Video streaming** — support HTTP Range requests for compatible playback and seeking.
- **Live updates** — receive file-system changes through Server-Sent Events.
- **Cross-platform foundation** — Flet provides the application UI, while Flask handles HTTP requests.

## Features

### Application

| Feature | Description |
|---|---|
| Dashboard | Manage the sharing server and its settings. |
| Activity | Access the application's activity view. |
| Settings | Configure available application preferences. |
| Network discovery | Discover available IPv4 interfaces. |
| Adaptive UI | Build the interface with reusable Flet components and centralized design tokens. |

### Web file browser

| Feature | Description |
|---|---|
| Directory browsing | Navigate the shared directory tree. |
| Recursive search | Find files across nested directories. |
| Video streaming | Support HTTP Range requests for compatible clients. |
| Thumbnails | Generate previews where supported. |
| Live updates | Use Server-Sent Events (SSE) for file-system notifications. |
| Modular frontend | Keep HTML, CSS, and JavaScript separate from Python routes. |

### Headless CLI

Run the file-sharing server directly from a terminal without launching the Flet interface.

```bash
bloodhound --dir /path/to/folder
```

The CLI is useful for terminal-based workflows, lightweight deployments, and environments where a graphical interface is unnecessary.

### Android integration

- Android-specific storage permission handling.
- Battery optimization exemption support.
- Foreground service support.
- Android build configuration managed through `pyproject.toml`.

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/mohammed-mahmoudzadeh/bloodhound.git
cd bloodhound
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Launch the application

```bash
python src/main.py
```

Once the application opens:

1. Select the folder you want to share.
2. Configure the available server settings.
3. Start the server.
4. Open the displayed address on another device connected to the same local network.

The exact launch command may differ if the project's configured entry point changes.

## CLI Usage

BloodHound includes a standalone Flask file-browser package with its own module entry point.

### Run from source

From the repository root:

```bash
PYTHONPATH=src python -m bloodhound.core.share --dir /path/to/folder
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m bloodhound.core.share --dir "C:\path\to\folder"
```

### Run an installed command

If the package's console entry point is configured and installed:

```bash
bloodhound --dir ~/Documents
```

Windows:

```powershell
bloodhound --dir "C:\Users\YourUser\Documents"
```

The server's actual bind address and port depend on the current CLI implementation and configuration. Use the address reported by the running process to connect from another device.

### Bash completion

The repository includes a Bash completion script:

```text
completion/bloodhound
```

The configured installation process installs it to:

```text
/etc/bash_completion.d/bloodhound
```

After installation, reload the Bash completion configuration or open a new shell.

## Build for Android

BloodHound uses Flet's build tooling to package the application for Android.

### Requirements

- Flutter SDK
- Android SDK and required build tools
- Python dependencies from the project configuration

### Build an APK

Run the following command from the repository root:

```bash
flet build apk --arch arm64-v8a
```

The expected output path for the current configuration is:

```text
build/apk/app-release.apk
```

Check the build output for the actual artifact location.

Android permissions and application metadata are configured in `pyproject.toml`. Runtime storage permissions and relevant system settings must be handled on the target device.

## Architecture

BloodHound separates the graphical interface from the HTTP file-sharing layer. Both the GUI and the standalone CLI use the Flask file-browser package.

```text
                         BloodHound
                            |
              +-------------+--------------+
              |                            |
        Flet Application              Headless CLI
              |                            |
       +------+------+                     |
       |      |      |                  ‌   |
   Dashboard Activity Settings             |
       |                                   |
       +----------------+------------------+
                        |
                  Flask Server
                        |
                Flask File Browser
                        |
          +-------------+-------------+
          |             |             |
        Routes       File Access    Watcher
          |             |             |
      HTML / CSS / JS  Streaming    SSE Events
                        |
                 Local Network
                        |
               Web Browser Clients
```

### Flet application layer

The Flet shell manages the user interface, navigation, shared state, and rendering lifecycle.

### Flask server layer

The Flask server exposes the shared directory over HTTP. The `FlaskServer` wrapper manages the server lifecycle for the graphical application.

### Web interface layer

The browser interface is implemented with HTML templates, CSS, and JavaScript. Python modules handle routing, file access, streaming, thumbnails, and file-system monitoring.

### Streaming and live updates

HTTP Range requests allow compatible clients to request portions of a file, supporting video playback and seeking. Server-Sent Events provide a mechanism for notifying connected browsers about file-system changes.

## Project Layout

```text
bloodhound/
├── pyproject.toml
├── requirements.txt
├── completion/
│   └── bloodhound
└── src/
    ├── main.py
    ├── assets/
    │   └── icons and splash images
    └── bloodhound/
        ├── app.py
        ├── state.py
        ├── theme/
        ├── components/
        ├── views/
        │   ├── dashboard
        │   ├── activity
        │   └── settings
        └── core/
            ├── server.py
            ├── network.py
            ├── share/
            │   ├── __main__.py
            │   ├── templates/
            │   │   └── index.html
            │   ├── static/
            │   │   ├── styles.css
            │   │   └── app.js
            │   └── ...
            └── ...
```

| Path | Responsibility |
|---|---|
| `pyproject.toml` | Build configuration, application metadata, dependencies, and Android settings. |
| `requirements.txt` | Pinned Python dependencies. |
| `completion/bloodhound` | Bash CLI completion definitions. |
| `src/main.py` | Application entry point. |
| `src/assets/` | Icons and splash-screen assets. |
| `src/bloodhound/app.py` | Flet application shell and rendering lifecycle. |
| `src/bloodhound/state.py` | Shared application state. |
| `src/bloodhound/theme/` | Colors, typography, and spacing tokens. |
| `src/bloodhound/components/` | Reusable UI components. |
| `src/bloodhound/views/` | Dashboard, Activity, and Settings views. |
| `src/bloodhound/core/server.py` | Flask server lifecycle wrapper. |
| `src/bloodhound/core/network.py` | IPv4 interface discovery. |
| `src/bloodhound/core/share/` | Flask routes, browser templates, static assets, file access, streaming, thumbnails, and file-system monitoring. |

## Configuration

### Network interfaces

BloodHound discovers IPv4 interfaces that can be used for sharing.

| Bind address | Behavior |
|---|---|
| `0.0.0.0` | Listen on all IPv4 interfaces. |
| A specific LAN address | Listen on a selected network interface. |
| A hotspot address | Allow connections through the hotspot interface when supported by the device and configuration. |

Choose an address that is reachable from the client device. Firewall rules and network isolation settings may affect connectivity.

### Port

The previous application configuration uses port `8000` as the default. Confirm the current implementation if the default has changed.

Choose an available TCP port supported by the application. The GUI provides port configuration where implemented.

### Shared directory

The selected directory is the root of the web file browser.

For CLI usage:

```bash
bloodhound --dir /path/to/folder
```

The process must have permission to read the selected files and traverse the relevant directories.

### Android permissions

Android-specific settings are managed through `pyproject.toml` and the application's permission-handling code.

Depending on the device and Android version, BloodHound may require network access, storage permissions, and appropriate background-execution settings. Grant runtime permissions and system exemptions when prompted.

### Dependencies

Python dependencies are declared in `requirements.txt` and the project configuration. Install them in the active virtual environment when developing from source.

Optional media-inspection tools, if used by the current implementation, must be installed separately and made available on the system `PATH`.

## Security Considerations

BloodHound is designed for local-network file sharing, not unrestricted public exposure.

- Share only directories intended to be accessible over the network.
- Bind to a specific interface when listening on all interfaces is unnecessary.
- Restrict access through host firewall rules when appropriate.
- Avoid exposing the server directly to the public internet without reviewing authentication, authorization, transport security, and deployment requirements.

Actual access controls depend on the current server implementation and configuration.

---
