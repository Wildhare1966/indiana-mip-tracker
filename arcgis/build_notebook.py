#!/usr/bin/env python3
"""Convert sync_tracked_projects.py (with `# %%` cell markers) into a valid
nbformat v4 .ipynb for ArcGIS Online Notebooks.

Markers:
    # %%              -> a code cell starts
    # %% [markdown]   -> a markdown cell starts (lines have their leading "# " stripped)

Usage:  python build_notebook.py [source.py] [out.ipynb]
"""
import json
import sys


def parse_cells(text):
    cells = []
    kind, buf = None, []

    def flush():
        if kind is None:
            return
        src = "\n".join(buf).strip("\n")
        if kind == "markdown":
            src = "\n".join(
                ln[2:] if ln.startswith("# ") else (ln[1:] if ln == "#" else ln)
                for ln in src.split("\n")
            )
        if src.strip():
            cells.append((kind, src))

    for line in text.split("\n"):
        stripped = line.rstrip("\n")
        if stripped.startswith("# %%"):
            flush()
            kind = "markdown" if "[markdown]" in stripped else "code"
            buf = []
        else:
            buf.append(stripped)
    flush()
    return cells


def to_nb(cells):
    nb_cells = []
    for i, (kind, src) in enumerate(cells):
        lines = src.split("\n")
        source = [ln + "\n" for ln in lines[:-1]] + [lines[-1]] if lines else []
        cell_id = "cell-%02d" % i          # required by nbformat 4.5 (minor 5)
        if kind == "markdown":
            nb_cells.append({"cell_type": "markdown", "id": cell_id,
                             "metadata": {}, "source": source})
        else:
            nb_cells.append({
                "cell_type": "code", "id": cell_id, "metadata": {},
                "execution_count": None, "outputs": [], "source": source,
            })
    return {
        "cells": nb_cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "sync_tracked_projects.py"
    out = sys.argv[2] if len(sys.argv) > 2 else "sync_tracked_projects.ipynb"
    with open(src, "r", encoding="utf-8") as f:
        text = f.read()
    nb = to_nb(parse_cells(text))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Wrote %s (%d cells)" % (out, len(nb["cells"])))


if __name__ == "__main__":
    main()
