#!/usr/bin/env python3
"""
make_manifest.py
================
Regenerates data/weeks/manifest.json from the weekly Excel files present in
data/weeks/. Run this after adding (or removing) a weekly file, then commit &
push so all viewers see the updated history.

USAGE
-----
    python make_manifest.py

The manifest is a simple JSON list of filenames, sorted by the week-ending date
parsed from each filename. Filenames must contain the week, e.g.
    CTR_PS_22.05.2026-28.05.2026.xlsx     (range — later date is week-ending)
    CTR_PS_28.05.2026.xlsx                (single week-ending date)
Both DD.MM.YYYY and YYYY-MM-DD are understood; separators . - _ / space all work.
"""
import json
import os
import re
import sys

WEEKS_DIR = os.path.join(os.path.dirname(__file__), "data", "weeks")
EXTS = (".xlsx", ".xls", ".csv", ".json")


def week_end(fn):
    base = os.path.splitext(fn)[0]
    dates = []
    for d, mo, y in re.findall(r"(\d{1,2})[.\-_/ ](\d{1,2})[.\-_/ ](\d{2,4})", base):
        y = int(y); y += 2000 if y < 100 else 0
        d, mo = int(d), int(mo)
        if 1 <= d <= 31 and 1 <= mo <= 12 and 2000 <= y <= 2100:
            dates.append((y, mo, d))
    for y, mo, d in re.findall(r"(\d{4})[.\-_/ ](\d{1,2})[.\-_/ ](\d{1,2})", base):
        y, mo, d = int(y), int(mo), int(d)
        if 1 <= d <= 31 and 1 <= mo <= 12 and 2000 <= y <= 2100:
            dates.append((y, mo, d))
    if not dates:
        return (9999, 99, 99)  # undated files sort last
    return max(dates)


def main():
    if not os.path.isdir(WEEKS_DIR):
        sys.exit("Missing folder: " + WEEKS_DIR)
    files = [f for f in os.listdir(WEEKS_DIR)
             if f.lower().endswith(EXTS) and f.lower() != "manifest.json"]
    files.sort(key=week_end)
    out = os.path.join(WEEKS_DIR, "manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=2)
    print("Wrote %s with %d week(s):" % (out, len(files)))
    for f in files:
        print("  -", f)


if __name__ == "__main__":
    main()
