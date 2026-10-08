#!/usr/bin/env python3
"""Guava - Phase 2 data acquisition.

Guava is a single-artifact library (com.google.guava:guava). For every
selected release this script downloads the binary jar from Maven Central
(the "-jre" flavour from 23.1 on; before that there was a single flavour),
keeps the com/google/** production classes and writes
guava/data/workspace/<v>/bin/guava-<v>.jar (the layout JNode expects),
guava/data/versions.csv and guava/data/packages/<v>.csv.

Usage: python3 guava/scripts/collect_versions.py
"""
import csv
import io
import os
import time
import urllib.request
import zipfile
from collections import Counter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # guava/
DATA = os.path.join(HERE, "data")
CACHE = os.path.join(HERE, "..", "data", "cache", "guava")
REPO = "https://repo1.maven.org/maven2/com/google/guava/guava"

# Sparse selection: every second major release 10.0 ... 32.0 plus the latest
# release at the time of the analysis, 33.7.2 (Sep 2026).
# Rationale in guava/docs/phase1_project_selection.md.
VERSIONS = ["10.0", "12.0", "14.0", "16.0", "18.0", "20.0", "22.0", "24.0",
            "26.0", "28.0", "30.0", "32.0.0", "33.7.2"]


def maven_version(v):
    major = int(v.split(".")[0])
    return v if major <= 22 else f"{v}-jre"


def fetch(v):
    mv = maven_version(v)
    local = os.path.join(CACHE, f"guava-{mv}.jar")
    if not os.path.exists(local):
        os.makedirs(CACHE, exist_ok=True)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(f"{REPO}/{mv}/guava-{mv}.jar", timeout=120) as r:
                    data = r.read()
                break
            except Exception:
                time.sleep(2 ** attempt)
        else:
            raise RuntimeError(f"cannot download guava {mv}")
        with open(local, "wb") as f:
            f.write(data)
    with open(local, "rb") as f:
        return mv, f.read()


def main():
    tags = {r["tag"]: r["date"] for r in csv.DictReader(open(os.path.join(DATA, "tags.csv")))}
    os.makedirs(os.path.join(DATA, "packages"), exist_ok=True)
    rows = []
    for v in VERSIONS:
        mv, data = fetch(v)
        bin_dir = os.path.join(DATA, "workspace", v, "bin")
        os.makedirs(bin_dir, exist_ok=True)
        out = os.path.join(bin_dir, f"guava-{v}.jar")
        classes = []
        with zipfile.ZipFile(io.BytesIO(data)) as src, \
                zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for name in src.namelist():
                if name.startswith("com/google/") and name.endswith(".class") \
                        and "module-info" not in name and "package-info" not in name:
                    z.writestr(name, src.read(name))
                    classes.append(name)
        top = [c for c in classes if "$" not in c.rsplit("/", 1)[-1]]
        pk = Counter(c.rsplit("/", 1)[0].replace("/", ".") for c in top)
        with open(os.path.join(DATA, "packages", f"{v}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["package", "top_level_classes"])
            w.writerows(sorted(pk.items()))
        r = {"version": v, "maven_version": mv, "date": tags[v], "packages": len(pk),
             "class_files": len(classes), "top_level_classes": len(top),
             "jar": os.path.relpath(out, HERE)}
        rows.append(r)
        print(r, flush=True)
    with open(os.path.join(DATA, "versions.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
