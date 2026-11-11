from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import build  # noqa: E402


def test_pages_build_contains_only_site_assets() -> None:
    output = build()
    assert (output / "index.html").is_file()
    assert (output / "styles.css").is_file()
    assert (output / "app.js").is_file()
    assert (output / "assets/fuse.min.mjs").is_file()
    assert len(list((output / "data").glob("*.json"))) == 7
    assert not (output / "README.md").exists()
    assert not (output / "schema").exists()
