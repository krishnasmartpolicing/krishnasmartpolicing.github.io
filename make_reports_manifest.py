#!/usr/bin/env python3
"""
make_reports_manifest.py
========================
Regenerates reports/manifest.json from whatever files are sitting in the
reports/ folder. Run by the "Build reports manifest" GitHub Action after you
add (or remove) a report, then committed automatically — so publishing a
report on the static site is just: drop the file into reports/ and commit.

Each entry records: display name, URL, size (bytes) and upload date (the
file's last git-commit date). The dashboard's "Other Reports" tab reads this.
"""
import json
import os
import subprocess
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(ROOT, "reports")
SKIP = {"manifest.json"}
ALLOWED = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
           ".png", ".jpg", ".jpeg", ".gif", ".webp")


def git_date(relpath):
    """Last commit date for a file (ISO-8601), or None if unavailable."""
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", "--", relpath],
            cwd=ROOT, stderr=subprocess.DEVNULL,
        ).decode().strip()
        return out or None
    except Exception:
        return None


def main():
    if not os.path.isdir(REPORTS_DIR):
        print("No reports/ folder found — nothing to do.")
        return
    items = []
    for fn in sorted(os.listdir(REPORTS_DIR)):
        if fn in SKIP or fn.startswith("."):
            continue
        if not fn.lower().endswith(ALLOWED):
            continue
        full = os.path.join(REPORTS_DIR, fn)
        if not os.path.isfile(full):
            continue
        rel = "reports/" + fn
        items.append({
            "name": fn,
            "url": "reports/" + urllib.parse.quote(fn),
            "size": os.path.getsize(full),
            "date": git_date(rel),
        })
    # newest first (entries without a date sort last)
    items.sort(key=lambda x: (x["date"] or ""), reverse=True)
    out = os.path.join(REPORTS_DIR, "manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print("Wrote %s with %d report(s):" % (out, len(items)))
    for it in items:
        print("  -", it["name"])


if __name__ == "__main__":
    main()
