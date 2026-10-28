"""Network interface discovery (Android + desktop)."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from typing import List, Tuple

IS_ANDROID = (
    sys.platform == "android"
    or "ANDROID_ARGUMENT" in os.environ
    or "ANDROID_BOOTLOGO" in os.environ
)


def _label_for_iface(name: str) -> str:
    """Friendly label for a Linux/Android network interface name."""
    n = name.lower()

    # Hotspot / AP
    if n.startswith(("swlan", "ap", "softap")):
        return "Hotspot"

    # Wi-Fi — covers wlan0, wlp2s0, wls1, wlx..., wlo1
    if n.startswith(("wl", "wlan", "wlp", "wls", "wlo", "wlx")):
        return "Wi-Fi"

    # Cellular
    if n.startswith(("rmnet", "ccmni", "pdp", "wwan", "rmnet_data")):
        return "Cellular"

    # VPN / tunnel
    if n.startswith(("tun", "tap", "ppp", "wg")):
        return "VPN"

    # Wi-Fi Direct
    if n.startswith("p2p"):
        return "Wi-Fi Direct"

    # Ethernet — covers eth0, enp3s0, eno1, ens33, enx...
    if n.startswith(("eth", "enp", "eno", "ens", "enx")):
        return "Ethernet"

    # Loopback
    if n in ("lo", "lo0"):
        return "Loopback"

    return name


def _ip_android_termux():
    try:
        r = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            info = json.loads(r.stdout)
            ip = info.get("ip") or info.get("ip_address")
            if ip and ip != "0.0.0.0":
                return ip
    except Exception:
        pass
    return None


def _ip_udp_fallback():
    """UDP socket trick — no traffic sent, just route lookup."""
    for target in ("10.255.255.255", "8.8.8.8", "1.1.1.1"):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            s.connect((target, 1))
            ip = s.getsockname()[0]
            s.close()
            if ip and not ip.startswith("127."):
                return ip
        except Exception:
            continue
    return None


def get_all_ips() -> List[Tuple[str, str]]:
    """Return list of (label, ip) for every available IPv4 interface."""
    results: List[Tuple[str, str]] = []
    seen = set()

    def _add(label, ip):
        if ip and ip not in seen:
            seen.add(ip)
            results.append((label, ip))

    _add("All Interfaces", "0.0.0.0")
    _add("Localhost", "127.0.0.1")

    if IS_ANDROID:
        try:
            from jnius import autoclass  # type: ignore
            NI = autoclass("java.net.NetworkInterface")
            Inet4 = autoclass("java.net.Inet4Address")
            ifaces = NI.getNetworkInterfaces()
            while ifaces.hasMoreElements():
                iface = ifaces.nextElement()
                try:
                    if not iface.isUp():
                        continue
                except Exception:
                    continue
                name = str(iface.getName())
                if name == "lo":
                    continue
                addrs = iface.getInetAddresses()
                while addrs.hasMoreElements():
                    addr = addrs.nextElement()
                    try:
                        if not isinstance(addr, Inet4):
                            continue
                        if addr.isLoopbackAddress():
                            continue
                    except Exception:
                        continue
                    _add(_label_for_iface(name), str(addr.getHostAddress()))
        except Exception:
            pass

        if not any(ip not in ("0.0.0.0", "127.0.0.1") for _, ip in results):
            _add("Wi-Fi", _ip_android_termux())
        if not any(ip not in ("0.0.0.0", "127.0.0.1") for _, ip in results):
            _add("Primary", _ip_udp_fallback())
    else:
        try:
            import ifaddr  # type: ignore
            for adapter in ifaddr.get_adapters():
                label = _label_for_iface(adapter.nice_name)
                for ip in adapter.ips:
                    if isinstance(ip.ip, str) and "." in ip.ip:
                        _add(label, ip.ip)
        except Exception:
            pass

        if not any(ip not in ("0.0.0.0", "127.0.0.1") for _, ip in results):
            fallback = _ip_udp_fallback()
            if fallback:
                _add("Primary", fallback)

    return results


def get_primary_ip() -> str:
    all_ips = get_all_ips()
    for pref in ("Wi-Fi", "Hotspot", "Ethernet"):
        for label, ip in all_ips:
            if label == pref and ip not in ("0.0.0.0", "127.0.0.1"):
                return ip
    for _, ip in all_ips:
        if ip not in ("0.0.0.0", "127.0.0.1"):
            return ip
    return "127.0.0.1"
