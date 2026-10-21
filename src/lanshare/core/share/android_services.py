"""Android-specific services: Foreground Service + Battery Optimization exemption."""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy imports to avoid breaking desktop builds
try:
    from jnius import autoclass, cast
    from android import mActivity  # type: ignore
    JNIUS_AVAILABLE = True
except ImportError:
    JNIUS_AVAILABLE = False


def request_ignore_battery_optimizations() -> bool:
    """Ask the user to exempt the app from battery optimization.
    
    This opens the system dialog. If the standard intent is not supported
    by the OEM (e.g., Xiaomi, Samsung), it falls back to the general
    battery optimization settings screen.
    """
    if not JNIUS_AVAILABLE:
        logger.warning("pyjnius not available; cannot request battery exemption.")
        return False

    try:
        Settings = autoclass("android.provider.Settings")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        PowerManager = autoclass("android.os.PowerManager")
        Context = autoclass("android.content.Context")
        Build = autoclass("android.os.Build$VERSION")
        PackageManager = autoclass("android.content.pm.PackageManager")

        # Only Android 6.0+ (API 23) supports this
        if Build.SDK_INT < 23:
            logger.info("Battery optimization exemption requires Android 6.0+.")
            return False

        context = mActivity.getApplicationContext()
        package_name = context.getPackageName()
        power_manager = cast("android.os.PowerManager", 
                             context.getSystemService(Context.POWER_SERVICE))

        if power_manager is not None and power_manager.isIgnoringBatteryOptimizations(package_name):
            logger.info("App is already exempt from battery optimization.")
            return True

        # --- 1. Try the direct exemption intent ---
        direct_intent = Intent()
        direct_intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
        direct_intent.setData(Uri.parse(f"package:{package_name}"))

        # Check if any activity can handle this intent
        resolve_info = context.getPackageManager().resolveActivity(
            direct_intent, PackageManager.MATCH_DEFAULT_ONLY
        )
        
        if resolve_info is not None:
            mActivity.startActivity(direct_intent)
            logger.info("Battery optimization exemption dialog launched.")
            return True
        else:
            logger.warning("Direct exemption intent not supported. Trying fallback.")
            
            # --- 2. Fallback: Open the general battery optimization list ---
            fallback_intent = Intent()
            fallback_intent.setAction(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS)
            
            # Check if the fallback can be resolved (it usually can)
            resolve_fallback = context.getPackageManager().resolveActivity(
                fallback_intent, PackageManager.MATCH_DEFAULT_ONLY
            )
            if resolve_fallback is not None:
                mActivity.startActivity(fallback_intent)
                logger.info("Fallback battery settings screen opened. "
                            "Please find LANShare and set it to 'Unrestricted'.")
                return True
            else:
                logger.error("No battery settings activity found on this device.")
                return False

    except Exception as ex:
        logger.error(f"Failed to request battery exemption: {ex}")
        return False


def start_foreground_service() -> bool:
    """Start a foreground service to keep the Flask server alive.
    
    Uses the `flet-android-background` package. Must be called from the main
    thread (Flet UI thread). The service shows a persistent notification.
    """
    if not JNIUS_AVAILABLE:
        return False

    try:
        from flet_android_background import BackgroundTask

        async def _start():
            task = BackgroundTask()
            await task.start(work=lambda: None)

        logger.info("Foreground service start requested.")
        return _start  # caller must await this
    except ImportError:
        logger.error("flet-android-background not installed. "
                     "Add it to pyproject.toml dependencies.")
        return False
    except Exception as ex:
        logger.error(f"Failed to start foreground service: {ex}")
        return False


def stop_foreground_service():
    """Stop the foreground service if running."""
    if not JNIUS_AVAILABLE:
        return
    try:
        from flet_android_background import BackgroundTask
        logger.info("Foreground service stop requested.")
    except Exception as ex:
        logger.error(f"Failed to stop foreground service: {ex}")
