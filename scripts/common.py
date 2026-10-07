"""Shared helpers: loading the tool outputs and building the class graph."""
import csv
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Which analysed system: PROJECT=guava -> guava/{data,results,ai,report}.
# Default "." keeps the Spring AI layout at the repository root.
PROJECT_DIR = os.path.normpath(os.path.join(ROOT, os.environ.get("PROJECT", ".")))
DATA = os.path.join(PROJECT_DIR, "data")
RESULTS = os.path.join(PROJECT_DIR, "results")
_cfg_path = os.path.join(PROJECT_DIR, "project.json")
CONFIG = json.load(open(_cfg_path)) if os.path.exists(_cfg_path) else {
    "name": "Spring AI", "prefix": "org.springframework.ai.",
    "highlight_versions": ["0.8.0", "1.0.0", "1.1.0", "2.0.0"]}
PREFIX = CONFIG["prefix"]
NAME = CONFIG["name"]


def short(name):
    """Strip the project's package prefix (for display)."""
    return name[len(PREFIX):] if name.startswith(PREFIX) else name


def versions():
    with open(os.path.join(DATA, "versions.csv")) as f:
        return [r["version"] for r in csv.DictReader(f)]


def top_level(name):
    """Map an inner/anonymous class (A$B, A$1) to its top-level class A."""
    return name.split("$", 1)[0]


def load_dependencies(version):
    """Return {(src, dst): {type: times}} at top-level-class granularity.

    DependencyExtractor reports class-file level dependencies (inner classes
    included). Architecture recovery is done at compilation-unit level, so
    inner classes are folded into their enclosing top-level class and the
    resulting self-dependencies are dropped.
    """
    edges = defaultdict(lambda: defaultdict(int))
    nodes = set()
    raw = 0
    with open(os.path.join(DATA, "dependencies", f"{version}.csv")) as f:
        for r in csv.DictReader(f):
            raw += 1
            s, d = top_level(r["dependeeClass"]), top_level(r["dependencyClass"])
            nodes.add(s)
            nodes.add(d)
            if s != d:
                edges[(s, d)][r["DependencyType"]] += int(r["Times"])
    return nodes, edges, raw


def load_noise(version):
    """Return (noise set, sig dict) at top-level granularity from JNode output.

    JNode writes ';'-separated rows: name;Noise;NoiseSuspect;SIG;w with decimal
    commas. A top-level class takes the maximum SIG of its class files and is
    noise if any of its class files is flagged as noise.

    Fallback: JNode flags a class when its min-max normalised SIG is
    >= mean + 1 std. When SIG is concentrated near its maximum this limit can
    exceed 1.0 and *no* class is flagged (happens for 0.8.0). In that case the
    limit is clamped to the maximum SIG, i.e. the classes with the highest
    significance are taken as noise. Returns (noise, sig, w, used_fallback).
    """
    noise, sig, w = set(), {}, {}
    rows = []
    with open(os.path.join(DATA, "noise", f"{version}.csv")) as f:
        next(f)
        for line in f:
            parts = line.strip().split(";")
            if len(parts) < 5:
                continue
            name = top_level(parts[0])
            s = float(parts[3].replace(",", "."))
            rows.append((name, s, parts[1].strip() == "1"))
            sig[name] = max(sig.get(name, 0.0), s)
            w[name] = max(w.get(name, 0.0), float(parts[4].replace(",", ".")))
    noise = {n for n, _, flag in rows if flag}
    fallback = not noise
    if fallback:
        vals = [s for _, s, _ in rows]
        mean = sum(vals) / len(vals)
        std = (sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
        limit = min(mean + std, max(vals))
        noise = {n for n, s, _ in rows if s >= limit}
    return noise, sig, w, fallback


def package(name):
    return name.rsplit(".", 1)[0]


def write_csv(path, rows, fields=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = list(rows)
    fields = fields or list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
