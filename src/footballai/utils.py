from __future__ import annotations

import re
import unicodedata


def slugify(text: str) -> str:
    """'Man. City FC' -> 'man-city-fc' (ASCII, URL/file safe)."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
