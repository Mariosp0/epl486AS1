"""Shared helpers: loading the tool outputs and building the class graph."""
import csv
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Analysed system: its folder holds data/, results/, ai/, report/ and
# project.json. Default: guava/ (override with PROJECT=<folder>).
PROJECT_DIR = os.path.normpath(os.path.join(ROOT, os.environ.get("PROJECT", "guava")))
DATA = os.path.join(PROJECT_DIR, "data")
RESULTS = os.path.join(PROJECT_DIR, "results")
_cfg_path = os.path.join(PROJECT_DIR, "project.json")
CONFIG = json.load(open(_cfg_path))
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
    """Return (noise set, sig dict, w dict) at top-level granularity from JNode.

    JNode writes ';'-separated rows: name;Noise;NoiseSuspect;SIG;w with decimal
    commas. A top-level class takes the maximum SIG of its class files and is
    noise if any of its class files is flagged as noise by JNode. JNode's own
    flag is used as is: if JNode flags no class, the version has no noise
    classes (A2 = A1 and A4 = A3 for that version).
    """
    noise, sig, w = set(), {}, {}
    with open(os.path.join(DATA, "noise", f"{version}.csv")) as f:
        next(f)
        for line in f:
            parts = line.strip().split(";")
            if len(parts) < 5:
                continue
            name = top_level(parts[0])
            if parts[1].strip() == "1":
                noise.add(name)
            sig[name] = max(sig.get(name, 0.0), float(parts[3].replace(",", ".")))
            w[name] = max(w.get(name, 0.0), float(parts[4].replace(",", ".")))
    return noise, sig, w


def populations(version):
    """Class populations used by every architecture of one version.

    nodes     - top-level classes that appear in the DependencyExtractor output
    edges     - distinct top-level class dependencies (no self-dependencies)
    connected - classes with at least one dependency; population of A1, A3,
                PKG and AI (an isolated class carries no structural information)
    noise     - JNode noise classes among the connected classes
    nn_nodes  - connected classes minus noise; population of A2, A4,
                PKG_nonoise and AI (no noise). Classes that lose all their
                dependencies when the noise is removed are KEPT (they become
                isolated classes of the reduced graph).
    e_nn      - dependencies between nn_nodes
    """
    nodes, dep, raw = load_dependencies(version)
    edges = set(dep)
    connected = sorted({c for e in edges for c in e})
    noise = load_noise(version)[0] & set(connected)
    nn_nodes = sorted(set(connected) - noise)
    e_nn = {(s, d) for s, d in edges if s not in noise and d not in noise}
    return {"nodes": nodes, "raw": raw, "edges": edges, "connected": connected,
            "noise": noise, "nn_nodes": nn_nodes, "e_nn": e_nn}


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
