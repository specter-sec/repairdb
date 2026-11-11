#!/usr/bin/env python3
"""Prepare a clean GitHub Pages artifact from checked-in static assets."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_site"
FILES = ["index.html", "styles.css", "app.js"]
DIRS = ["data", "assets"]


def build() -> Path:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    for filename in FILES:
        shutil.copy2(ROOT / filename, OUTPUT / filename)
    for dirname in DIRS:
        shutil.copytree(ROOT / dirname, OUTPUT / dirname)
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(f"Static site prepared at {build()}")
