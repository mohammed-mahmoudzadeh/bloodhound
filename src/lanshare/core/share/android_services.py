"""Android-specific services: Battery Optimization exemption & Foreground Service."""
from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

try:
    from jnius import autoclass, cast
    JNIUS_AVAILABLE = True
except ImportError:
    JNIUS_AVAILABLE = False


def _get_activity():
    if not JNIUS_AVAILABLE:
        return None
    try:
        activity_host_class = os.getenv("MAIN_ACTIVITY_HOST_CLASS_NAME")
        if activity_host_class:
            host = autoclass(activity_host_class)
            return host.mActivity
        from android import mActivity
        return mActivity
    except Exception as e:
        logger.error(f"Failed to get Activity: {e}")
        return None

def is_ignoring_battery_optimizations() -> bool:
    """Check if the app is currently exempt from battery optimization."""
    if not JNIUS_AVAILABLE:
        return False
    try:
        PowerManager = autoclass("android.os.PowerManager")
        Context = autoclass("android.content.Context")
        Build = autoclass("android.os.Build$VERSION")
        if Build.SDK_INT < 23:
            return True
        activity = _get_activity()
        if not activity:
            return False
        context = activity.getApplicationContext()
        package_name = context.getPackageName()
        power_manager = cast(
            "android.os.PowerManager",
            context.getSystemService(Context.POWER_SERVICE),
        )
        return power_manager is not None and power_manager.isIgnoringBatteryOptimizations(package_name)
    except Exception as ex:
        logger.error(f"Failed to check battery optimization status: {ex}")
        return False

def has_storage_permission() -> bool:
    """Check if the app has MANAGE_EXTERNAL_STORAGE permission."""
    if not JNIUS_AVAILABLE:
        return False
    try:
        Environment = autoclass("android.os.Environment")
        return Environment.isExternalStorageManager()
    except Exception as ex:
        logger.error(f"Failed to check storage permission: {ex}")
        return False

def open_battery_optimization_dialog() -> bool:
    """Open the battery optimization exemption dialog.

    Returns True if a dialog/screen was successfully launched.
    The caller must re-check the status after a delay.
    """
    if not JNIUS_AVAILABLE:
        logger.warning("pyjnius not available; cannot open battery dialog.")
        return False

    try:
        Settings = autoclass("android.provider.Settings")
        Intent = autoclass("android.content.Intent")
        Uri = autoclass("android.net.Uri")
        Build = autoclass("android.os.Build$VERSION")
        PackageManager = autoclass("android.content.pm.PackageManager")

        if Build.SDK_INT < 23:
            return False

        activity = _get_activity()
        if not activity:
            logger.error("Could not get Activity to launch intent.")
            return False

        package_name = activity.getPackageName()

        if is_ignoring_battery_optimizations():
            logger.info("App is already exempt from battery optimization.")
            return True

        # Attempt 1: Direct exemption dialog
        direct_intent = Intent()
        direct_intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
        direct_intent.setData(Uri.parse(f"package:{package_name}"))

        resolve_info = activity.getPackageManager().resolveActivity(
            direct_intent, PackageManager.MATCH_DEFAULT_ONLY
        )

        if resolve_info is not None:
            activity.startActivity(direct_intent)
            logger.info("Battery optimization exemption dialog launched.")
            return True
        else:
            logger.warning("Direct exemption intent not supported. Using fallback.")

            # Attempt 2: General battery settings list
            fallback_intent = Intent()
            fallback_intent.setAction(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS)

            resolve_fallback = activity.getPackageManager().resolveActivity(
                fallback_intent, PackageManager.MATCH_DEFAULT_ONLY
            )
            if resolve_fallback is not None:
                activity.startActivity(fallback_intent)
                logger.info("Fallback battery settings screen opened.")
                return True
            else:
                logger.error("No battery settings activity found.")
                return False

    except Exception as ex:
        logger.error(f"Failed to open battery dialog: {ex}")
        return False


def start_foreground_service() -> bool:
    """Start a foreground service to keep the Flask server alive."""
    if not JNIUS_AVAILABLE:
        return False

    try:
        from flet_android_background import BackgroundTask

        async def _start():
            task = BackgroundTask()
            await task.start(work=lambda: None)

        logger.info("Foreground service start requested.")
        return _start
    except ImportError:
        logger.error("flet-android-background not installed.")
        return False
    except Exception as ex:
        logger.error(f"Failed to start foreground service: {ex}")
        return False
