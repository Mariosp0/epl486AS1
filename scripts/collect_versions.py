#!/usr/bin/env python3
"""Phase 2 - data acquisition.

For every analysed Spring AI release this script
  1. downloads the release BOM (spring-ai-bom) from Maven Central or the
     Spring milestone repository,
  2. downloads the binary jar of every org.springframework.ai module the BOM
     lists (starters and test utilities carry no production code and are
     skipped, see EXCLUDE),
  3. merges all org/springframework/ai/**.class files into a single jar
     data/jars/spring-ai-<version>.jar placed under data/workspace/<version>/bin
     (the layout JNode expects),
  4. records per-version facts in data/versions.csv.

Usage: python3 scripts/collect_versions.py [version ...]
"""
import csv
import io
import os
import re
import sys
import time
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPOS = ["https://repo1.maven.org/maven2", "https://repo.spring.io/milestone"]
GROUP = "org/springframework/ai"
NS = {"m": "http://maven.apache.org/POM/4.0.0"}
EXCLUDE = re.compile(r"(starter|^spring-ai-test$|-docs$|^spring-ai-bom$)")
CACHE = os.path.join(ROOT, "data", "cache")

# Feature releases analysed (see docs/phase1_project_selection.md for the
# cleaning rationale: patch releases x.y.z (z>0) and release candidates are
# excluded because they only carry bug fixes).
VERSIONS = [
    "0.8.0",
    "1.0.0-M1", "1.0.0-M2", "1.0.0-M3", "1.0.0-M4", "1.0.0-M5", "1.0.0-M6",
    "1.0.0-M7", "1.0.0-M8", "1.0.0",
    "1.1.0-M1", "1.1.0-M2", "1.1.0-M3", "1.1.0-M4", "1.1.0",
    "2.0.0-M1", "2.0.0-M2", "2.0.0-M3", "2.0.0-M4", "2.0.0-M5", "2.0.0-M6",
    "2.0.0-M7", "2.0.0-M8", "2.0.0",
    "2.1.0-M1",
]


def fetch(path):
    """Return (bytes, repo) for a repository-relative path, cached on disk."""
    local = os.path.join(CACHE, path)
    if os.path.exists(local):
        with open(local, "rb") as f:
            return f.read(), "cache"
    for repo in REPOS:
        for attempt in range(4):
            try:
                with urllib.request.urlopen(f"{repo}/{path}", timeout=60) as r:
                    data = r.read()
                os.makedirs(os.path.dirname(local), exist_ok=True)
                with open(local, "wb") as f:
                    f.write(data)
                return data, repo
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    break
                time.sleep(2 ** attempt)
            except Exception:
                time.sleep(2 ** attempt)
    return None, None


def bom_artifacts(version):
    data, repo = fetch(f"{GROUP}/spring-ai-bom/{version}/spring-ai-bom-{version}.pom")
    if data is None:
        raise RuntimeError(f"BOM for {version} not found")
    tree = ET.fromstring(data)
    arts = set()
    for dep in tree.iterfind(".//m:dependencyManagement/m:dependencies/m:dependency", NS):
        g = dep.findtext("m:groupId", namespaces=NS)
        a = dep.findtext("m:artifactId", namespaces=NS)
        t = dep.findtext("m:type", default="jar", namespaces=NS)
        if g in ("org.springframework.ai", "${project.groupId}") and t == "jar":
            arts.add(a)
    return sorted(arts)


def collect(version):
    arts = [a for a in bom_artifacts(version) if not EXCLUDE.search(a)]

    def get(a):
        data, _ = fetch(f"{GROUP}/{a}/{version}/{a}-{version}.jar")
        return a, data

    with ThreadPoolExecutor(8) as ex:
        jars = list(ex.map(get, arts))

    bin_dir = os.path.join(ROOT, "data", "workspace", version, "bin")
    os.makedirs(bin_dir, exist_ok=True)
    out = os.path.join(bin_dir, f"spring-ai-{version}.jar")
    seen = {}
    modules = []
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for a, data in jars:
            if data is None:
                continue
            n = 0
            with zipfile.ZipFile(io.BytesIO(data)) as src:
                for name in src.namelist():
                    if name.startswith("org/springframework/ai/") and name.endswith(".class") \
                            and "module-info" not in name and "package-info" not in name:
                        if name in seen:  # split package duplicates: keep first
                            continue
                        seen[name] = a
                        z.writestr(name, src.read(name))
                        n += 1
            if n:
                modules.append((a, n))
    classes = list(seen)
    top = [c for c in classes if "$" not in c.rsplit("/", 1)[-1]]
    pkgs = {c.rsplit("/", 1)[0] for c in classes}
    with open(os.path.join(ROOT, "data", "modules", f"{version}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["module", "class_files"])
        w.writerows(modules)
    return {
        "version": version,
        "bom_artifacts": len(arts),
        "modules_with_code": len(modules),
        "packages": len(pkgs),
        "class_files": len(classes),
        "top_level_classes": len(top),
        "jar": os.path.relpath(out, ROOT),
    }


def main():
    versions = sys.argv[1:] or VERSIONS
    os.makedirs(os.path.join(ROOT, "data", "modules"), exist_ok=True)
    path = os.path.join(ROOT, "data", "versions.csv")
    rows = {}
    if os.path.exists(path):
        with open(path) as f:
            rows = {r["version"]: r for r in csv.DictReader(f)}
    for v in versions:
        r = collect(v)
        print(r, flush=True)
        rows[v] = r
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(next(iter(rows.values())).keys()))
        w.writeheader()
        for v in VERSIONS:
            if v in rows:
                w.writerow(rows[v])


if __name__ == "__main__":
    main()
