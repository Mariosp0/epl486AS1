#!/usr/bin/env python3
"""How well do JNode's noise classes match the most used classes (fan-in)?

Per version: mean fan-in of noise vs other classes, how many of the 30 classes
with the highest fan-in are flagged as noise, and the top-level packages of
the noise classes. Output: results/noise_vs_fanin.csv
"""
import os
import statistics as st
from collections import Counter

from common import CONFIG, RESULTS, load_dependencies, load_noise, package, short, versions, write_csv


def main():
    rows = []
    for v in versions():
        _, dep, _ = load_dependencies(v)
        noise, _, _, _ = load_noise(v)
        conn = {c for e in dep for c in e}
        noise &= conn
        fin = Counter(d for _, d in dep)
        top = [c for c, _ in fin.most_common(30)]
        depth = CONFIG.get("package_depth", 1)
        pk = Counter(".".join(short(package(c)).split(".")[:depth]) for c in noise)
        rows.append({
            "version": v,
            "noise": len(noise),
            "mean_fanin_noise": round(st.mean(fin[c] for c in noise), 2),
            "mean_fanin_other": round(st.mean(fin[c] for c in conn - noise), 2),
            "top30_fanin_flagged": sum(c in noise for c in top),
            "top30_fanin_missed": " ".join(c.rsplit(".", 1)[1] for c in top if c not in noise),
            "noise_top_packages": " ".join(f"{p}:{n}" for p, n in pk.most_common(6)),
        })
    write_csv(os.path.join(RESULTS, "noise_vs_fanin.csv"), rows)
    for r in rows:
        print(r["version"], r["noise"], r["mean_fanin_noise"], r["mean_fanin_other"], r["top30_fanin_flagged"])


if __name__ == "__main__":
    main()
