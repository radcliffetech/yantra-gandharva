import logging
import os
import platform
import subprocess

logger = logging.getLogger(__name__)


def open_file_if_possible(path):
    if not os.path.exists(path):
        return
    try:
        if platform.system() == "Darwin":
            subprocess.run(["open", path])
        elif platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", path])
    except Exception as e:
        logger.warning(f"Could not open {path}: {e}")
