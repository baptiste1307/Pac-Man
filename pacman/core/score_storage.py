import os
import sys
from pathlib import Path


def get_score_path(file_name: str | Path = "scores.json") -> Path:
    """
    Get score json file path.

    Args:
        The desired score json file name.

    Returns:
        The score json file path.
    """
    path = Path(file_name)
    if path.is_absolute():
        return path

    if not getattr(sys, "frozen", False):
        return path

    if sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "PacMan"
    elif sys.platform == "win32":
        base_dir = Path(os.getenv("APPDATA", Path.home())) / "PacMan"
    else:
        data_home = os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")
        base_dir = Path(data_home) / "PacMan"

    return base_dir / path.name
