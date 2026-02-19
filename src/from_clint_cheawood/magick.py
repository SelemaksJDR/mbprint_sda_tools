"""Wrapper autour d'ImageMagick pour les opérations sur les images."""

import subprocess
import sys
from pathlib import Path


def run_magick(*args: str) -> str:
    """Execute une commande ImageMagick et retourne la sortie standard.

    Raises:
        RuntimeError: Si la commande echoue.
    """
    cmd = ["magick", *args]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"La commande 'magick {' '.join(args[:2])}...' a echoue "
            f"(code {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout.strip()


def get_image_dimensions(image_path: str | Path) -> tuple[int, int]:
    """Retourne (largeur, hauteur) d'une image via ImageMagick identify."""
    output = run_magick("identify", "-format", "%w %h", str(image_path))
    w, h = output.split()
    return int(w), int(h)
