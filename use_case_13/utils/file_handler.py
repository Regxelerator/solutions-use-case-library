from pathlib import Path
from typing import Iterator, Iterable

__all__ = ["ensure_dir", "iter_xml_files"]


def ensure_dir(path: Path | str) -> Path:
    """Ensure that a directory exists at the given path. Create it (and parents) if needed.

    Args:
        path: Directory path as a string or Path object.

    Returns:
        Path object to the directory.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def iter_xml_files(root: Path | str) -> Iterable[Path]:
    """Yield all XML files recursively under the given root directory.

    Args:
        root: Root directory to search, as a string or Path.

    Yields:
        Path objects to each found XML file.
    """
    yield from Path(root).rglob("*.xml")