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
    dens = [int(r["class_dependencies"]) / int(r["connected_classes"]) for r in size]
    line(axs[1], x, dens, "A3", "deps / connected class")
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
        ("mq", "MQ = mean cohesion − mean coupling", "mq.png"),
        ("cohesion", "Cohesion (mean intra-connectivity)", "cohesion.png"),
        ("coupling", "Coupling (mean inter-connectivity)", "coupling.png"),
        ("clusters", "Number of clusters", "clusters.png"),
    ]:
        fig, ax = plt.subplots(figsize=(7.5, 3.6))
        for a in archs:
            line(ax, x, [float(by[(v, a)][key]) for v in vs], a, dashed=a == "PKG")
        setup(ax, vs, key, title)
        ax.set_ylim(0)
        ax.legend(fontsize=7, ncol=3, loc="upper left", bbox_to_anchor=(0, -0.28))
        save(fig, fname)

    ks = read("kselection.csv")
    latest = vs[-1]
    chosen = {r["arch"]: int(r["clusters"]) for r in met if r["version"] == latest}
    fig, ax = plt.subplots(figsize=(6, 3.2))
    for a in ("A3", "A4"):
        rows = [r for r in ks if r["version"] == latest and r["arch"] == a]
        line(ax, [int(r["k"]) for r in rows], [float(r["inertia"]) for r in rows], a)
        ax.axvline(chosen[a], color=COLORS[a], lw=1, ls=":")
    ax.set_title(f"Elbow method: k-means inertia ({latest})", loc="left", fontsize=10)
    ax.set_xlabel("k")
    ax.set_ylabel("inertia (within-cluster sum of squares)")
    ax.legend(fontsize=7)
    save(fig, "kselection_latest.png")

    p = os.path.join(RESULTS, "acdc_params.csv")
    if os.path.exists(p):
        rows = read("acdc_params.csv")
        fig, ax = plt.subplots(figsize=(6, 3))
        for pat, key in (("bso", "A1"), ("so", "A3"), ("bs", "A2")):
            rr = [r for r in rows if r["patterns"] == pat and r["graph"] == "full"]
            line(ax, [int(r["max_cluster_size"]) for r in rr],
                 [float(r["mq"]) for r in rr], key, f"patterns={pat}")
        ax.set_xlabel("ACDC max cluster size (SubGraph pattern)")
        ax.set_ylabel("MQ")
        ax.set_title(f"ACDC parameter experiment ({latest}, full system)", loc="left", fontsize=10)
        ax.legend(fontsize=7)
        save(fig, "acdc_params.png")


def lecture_plots(vs):
    """Figures for MoJoFM, omnipresent classes, smells and Lehman's laws
    (scripts/lecture_metrics.py, scripts/activity.py)."""
    x = range(len(vs))
    p = os.path.join(RESULTS, "mojofm.csv")
    if os.path.exists(p):
        rows = {r["version"]: r for r in read("mojofm.csv")}
        fig, ax = plt.subplots(figsize=(7.5, 3.6))
        for a in ("A1", "A2", "A3", "A4"):
            line(ax, x, [float(rows[v][f"{a}_vs_PKG"]) for v in vs], a)
        setup(ax, vs, "MoJoFM (%)", "MoJoFM to the package structure (100 % = identical)")
        ax.set_ylim(0, 100)
        ax.legend(fontsize=7, ncol=2, loc="upper left", bbox_to_anchor=(0, -0.28))
        save(fig, "mojofm_pkg.png")
    p = os.path.join(RESULTS, "mojofm_stability.csv")
    if os.path.exists(p):
        rows = read("mojofm_stability.csv")
        fig, ax = plt.subplots(figsize=(7.5, 3.6))
        for a in ("A1", "A2", "A3", "A4"):
            line(ax, range(len(rows)), [float(r[a]) for r in rows], a)
        setup(ax, [r["to"] for r in rows], "MoJoFM (%)",
              "MoJoFM between consecutive versions (architectural stability)")
        ax.set_ylim(0, 100)
        ax.legend(fontsize=7, ncol=2, loc="upper left", bbox_to_anchor=(0, -0.28))
        save(fig, "mojofm_stability.png")
    p = os.path.join(RESULTS, "bunch_noise.csv")
    if os.path.exists(p):
        rows = read("bunch_noise.csv")
        fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
        line(axs[0], x, [int(r["jnode_noise"]) for r in rows], "A2", "JNode (Constantinou et al.)")
        line(axs[0], x, [int(r["bunch_noise"]) for r in rows], "A4", "Bunch (in-degree > 3·avg)")
        line(axs[0], x, [int(r["common"]) for r in rows], "PKG", "in both")
        setup(axs[0], vs, "omnipresent classes", "Omnipresent classes: JNode vs Bunch")
        axs[0].set_ylim(0)
        axs[0].legend(fontsize=7)
        line(axs[1], x, [float(r["mojofm_A1_system"]) for r in rows], "A1", "System (A1)")
        line(axs[1], x, [float(r["mojofm_A2_jnode"]) for r in rows], "A2", "Noise: JNode (A2)")
        line(axs[1], x, [float(r["mojofm_A2_bunch"]) for r in rows], "A4", "Noise: Bunch")
        setup(axs[1], vs, "MoJoFM to packages (%)", "ACDC: effect of removing omnipresent classes")
        axs[1].legend(fontsize=7)
        save(fig, "bunch_vs_jnode.png")
    p = os.path.join(RESULTS, "smells.csv")
    if os.path.exists(p):
        rows = read("smells.csv")
        fig, axs = plt.subplots(2, 2, figsize=(9, 6.2))
        panels = [("cyclic_packages_pct", "cyclic_classes_pct", "Cyclic dependency", "% of packages / classes"),
                  ("hub_like_pct", None, "Hub-like dependency", "% of classes"),
                  ("unstable_dep_pct", None, "Unstable dependency", "% of packages"),
                  ("god_components", None, "God component", "number of packages")]
        for ax, (k1, k2, title, yl) in zip(axs.flat, panels):
            line(ax, x, [float(r[k1]) for r in rows], "A1", "packages" if k2 else title)
            if k2:
                line(ax, x, [float(r[k2]) for r in rows], "A2", "classes")
                ax.legend(fontsize=7)
            setup(ax, vs, yl, title)
            ax.set_ylim(0)
        fig.tight_layout()
        save(fig, "smells.png")
    p = os.path.join(RESULTS, "dependency_changes.csv")
    if os.path.exists(p):
        rows = read("dependency_changes.csv")
        fig, ax = plt.subplots(figsize=(7.5, 3.4))
        xs = list(range(len(rows)))
        ax.bar([i - 0.2 for i in xs], [int(r["added"]) for r in rows], 0.4,
               color=COLORS["A4"], label="added")
        ax.bar([i + 0.2 for i in xs], [-int(r["removed"]) for r in rows], 0.4,
               color=COLORS["A1"], label="removed")
        ax.axhline(0, color=MUTED, lw=0.8)
        setup(ax, [r["to"] for r in rows], "class dependencies",
              "Dependencies added / removed per version (law II)")
        ax.legend(fontsize=7)
        save(fig, "dependency_changes.png")
    p = os.path.join(RESULTS, "activity.csv")
    if os.path.exists(p):
        rows = read("activity.csv")
        fig, ax = plt.subplots(figsize=(7.5, 3.2))
        line(ax, range(len(rows)), [float(r["commits_per_month"]) for r in rows], "A3", "commits / month")
        setup(ax, [r["to"] for r in rows], "commits per month",
              "Work rate between analysed releases (law IV)")
        ax.set_ylim(0)
        save(fig, "activity.png")


if __name__ == "__main__":
    main()
    lecture_plots([r["version"] for r in read("size.csv")])
