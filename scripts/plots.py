#!/usr/bin/env python3
"""Figures for the report (results/figures/*.png)."""
import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import CONFIG, DATA, RESULTS  # noqa: E402

FIG = os.path.join(RESULTS, "figures")
# Validated categorical palette (fixed order) + neutral for the reference.
COLORS = {"A1": "#2a78d6", "A2": "#eb6834", "A3": "#1baf7a", "A4": "#eda100",
          "PKG": "#8a8984", "PKG_nonoise": "#8a8984", "AI": "#4a3aa7"}
LABELS = {"A1": "A1 ACDC (full)", "A2": "A2 ACDC (no noise)",
          "A3": "A3 k-means (full)", "A4": "A4 k-means (no noise)",
          "PKG": "Packages (reference)"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
GA = set(CONFIG.get("highlight_versions", []))

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False,
    "figure.dpi": 150, "savefig.bbox": "tight",
})


def read(name):
    with open(os.path.join(RESULTS, name)) as f:
        return list(csv.DictReader(f))


def setup(ax, versions, ylabel, title):
    ax.set_xticks(range(len(versions)))
    ax.set_xticklabels(versions, rotation=60, ha="right", fontsize=7)
    for i, v in enumerate(versions):
        if v in GA:
            ax.axvline(i, color=GRID, lw=1.2, zorder=0)
            ax.get_xticklabels()[i].set_fontweight("bold")
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=10, color=INK)


def line(ax, xs, ys, key, label=None, dashed=False):
    ax.plot(xs, ys, color=COLORS.get(key, INK), lw=2, marker="o", ms=4,
            ls="--" if dashed else "-", label=label or LABELS.get(key, key))


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(os.path.join(FIG, name))
    plt.close(fig)


def main():
    size = read("size.csv")
    vs = [r["version"] for r in size]
    x = range(len(vs))

    with open(os.path.join(DATA, "versions.csv")) as f:
        vrows = {r["version"]: r for r in csv.DictReader(f)}
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    line(ax, x, [int(vrows[v]["class_files"]) for v in vs], "A2",
         "All class files (incl. inner/anonymous)")
    line(ax, x, [int(vrows[v]["top_level_classes"]) for v in vs], "A1", "Top-level classes")
    setup(ax, vs, "classes", "Size: classes per version")
    ax.set_ylim(0)
    ax.legend(fontsize=7, loc="lower right")
    save(fig, "size_classes.png")

    with open(os.path.join(DATA, "versions.csv")) as f:
        vinfo = {r["version"]: r for r in csv.DictReader(f)}
    has_modules = "modules_with_code" in next(iter(vinfo.values()))
    fig, axs = plt.subplots(1, 2 if has_modules else 1, figsize=(9 if has_modules else 5, 3.2),
                            squeeze=False)
    axs = axs[0]
    line(axs[0], x, [int(r["packages"]) for r in size], "A1", "Packages")
    setup(axs[0], vs, "packages", "Packages per version")
    if has_modules:
        line(axs[1], x, [int(vinfo[v]["modules_with_code"]) for v in vs], "A2", "Maven modules")
        setup(axs[1], vs, "modules", "Maven modules with code per version")
    for a in axs:
        a.set_ylim(0)
    save(fig, "size_packages_modules.png" if has_modules else "size_packages.png")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    line(axs[0], x, [int(r["class_dependencies"]) for r in size], "A1", "dependencies")
    setup(axs[0], vs, "class dependencies", "Class-to-class dependencies")
    dens = [int(r["class_dependencies"]) / int(r["classes"]) for r in size]
    line(axs[1], x, dens, "A3", "deps / class")
    setup(axs[1], vs, "dependencies per class", "Dependency density")
    for a in axs:
        a.set_ylim(0)
    save(fig, "dependencies.png")

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    line(axs[0], x, [int(r["noise_classes"]) for r in size], "A2", "noise classes")
    setup(axs[0], vs, "classes", "Widely-used (noise) classes")
    line(axs[1], x, [float(r["noise_pct"]) for r in size], "A2", "% of classes")
    setup(axs[1], vs, "% of connected classes", "Noise classes (%)")
    for a in axs:
        a.set_ylim(0)
    save(fig, "noise.png")

    met = read("metrics.csv")
    by = {(r["version"], r["arch"]): r for r in met}
    archs = ["A1", "A2", "A3", "A4", "PKG"]
    for key, title, fname in [
        ("turbo_mq_norm", "Normalised TurboMQ (TurboMQ / #clusters)", "mq_turbo_norm.png"),
        ("turbo_mq", "TurboMQ", "mq_turbo.png"),
        ("basic_mq", "BasicMQ (cohesion - coupling)", "mq_basic.png"),
        ("cohesion", "Cohesion (mean intra-connectivity)", "cohesion.png"),
        ("coupling", "Coupling (mean inter-connectivity)", "coupling.png"),
        ("intra_ratio", "Share of dependencies inside clusters", "intra_ratio.png"),
        ("clusters", "Number of clusters", "clusters.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7.5, 3.6))
        for a in archs:
            line(ax, x, [float(by[(v, a)][key]) for v in vs], a, dashed=a == "PKG")
        setup(ax, vs, key, title)
        if key not in ("basic_mq",):
            ax.set_ylim(0)
        ax.legend(fontsize=7, ncol=3, loc="upper left", bbox_to_anchor=(0, -0.28))
        save(fig, fname)

    stab = read("stability.csv")
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    xs = range(len(stab))
    for a in ("A1", "A2", "A3", "A4"):
        line(ax, xs, [float(r[a]) for r in stab], a)
    setup(ax, [r["to"] for r in stab], "ARI vs previous version",
          "Architectural stability between consecutive versions")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7, ncol=3, loc="upper left", bbox_to_anchor=(0, -0.28))
    save(fig, "stability.png")

    ks = read("kselection.csv")
    latest = vs[-1]
    chosen = {r["arch"]: int(r["clusters"]) for r in met if r["version"] == latest}
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.2))
    for a in ("A3", "A4"):
        rows = [r for r in ks if r["version"] == latest and r["arch"] == a]
        kk = [int(r["k"]) for r in rows]
        line(axs[0], kk, [float(r["inertia"]) for r in rows], a)
        line(axs[1], kk, [float(r["silhouette"]) for r in rows], a)
        for ax in axs:
            ax.axvline(chosen[a], color=COLORS[a], lw=1, ls=":")
    axs[0].set_title(f"Elbow: k-means inertia ({latest})", loc="left", fontsize=10)
    axs[1].set_title(f"Silhouette (cosine) ({latest})", loc="left", fontsize=10)
    for ax in axs:
        ax.set_xlabel("k")
        ax.legend(fontsize=7)
    axs[0].set_ylabel("inertia")
    axs[1].set_ylabel("silhouette")
    save(fig, "kselection_latest.png")

    p = os.path.join(RESULTS, "acdc_params.csv")
    if os.path.exists(p):
        rows = read("acdc_params.csv")
        fig, ax = plt.subplots(figsize=(6, 3))
        for pat, key in (("bso", "A1"), ("so", "A3"), ("bs", "A2")):
            rr = [r for r in rows if r["patterns"] == pat and r["graph"] == "full"]
            line(ax, [int(r["max_cluster_size"]) for r in rr],
                 [float(r["turbo_mq_norm"]) for r in rr], key, f"patterns={pat}")
        ax.set_xlabel("ACDC max cluster size (SubGraph pattern)")
        ax.set_ylabel("TurboMQ / k")
        ax.set_title(f"ACDC parameter experiment ({latest}, full system)", loc="left", fontsize=10)
        ax.legend(fontsize=7)
        save(fig, "acdc_params.png")


if __name__ == "__main__":
    main()
