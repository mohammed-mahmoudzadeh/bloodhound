"""Fast folder statistics — count files and total size."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FolderInfo:
    files: int = 0
    dirs: int = 0
    total_bytes: int = 0

    @property
    def files_display(self) -> str:
        return f"{self.files} file{'s' if self.files != 1 else ''}"

    @property
    def size_display(self) -> str:
        n = self.total_bytes
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < 1024:
                if unit == "B":
                    return f"{int(n)} B"
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} PB"

    @property
    def summary(self) -> str:
        if self.files == 0:
            return "Empty folder"
        return f"{self.files_display} · {self.size_display}"

    @property
    def summary_hidden_count(self) -> str:
        """If there are too many files, only show the size to avoid clutter."""
        if self.files == 0:
            return "Empty folder"
        if self.files > 1000:
            return self.size_display
        return f"{self.files_display} · {self.size_display}"


def scan_folder(path: str | Path, max_entries: int = 50000) -> FolderInfo:
    """Count files and total size in a folder.

    Stops early after `max_entries` files to keep it fast on huge trees.
    Returns a FolderInfo (0/0/0 if path invalid).
    """
    info = FolderInfo()
    try:
        root = Path(path)
        if not root.exists() or not root.is_dir():
            return info

        stack = [root]
        scanned = 0
        while stack and scanned < max_entries:
            current = stack.pop()
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        scanned += 1
                        if scanned >= max_entries:
                            break
                        try:
                            if entry.is_dir(follow_symlinks=False):
                                info.dirs += 1
                                stack.append(entry.path)
                            elif entry.is_file(follow_symlinks=False):
                                info.files += 1
                                try:
                                    info.total_bytes += entry.stat(
                                        follow_symlinks=False).st_size
                                except OSError:
                                    pass
                        except OSError:
                            continue
            except (PermissionError, OSError):
                continue
    except Exception:
        pass

    return info