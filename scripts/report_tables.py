#!/usr/bin/env python3
"""Phase 5 - render report/report.md from report/report_src.md.

Every {{NAME}} placeholder in the source is replaced by a Markdown table (or
number) generated from the result CSVs, so the report never contains
hand-copied numbers.
"""
import csv
import os
import re

from common import DATA, PROJECT_DIR, RESULTS, short


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def main():
    vers = read(os.path.join(DATA, "versions.csv"))
    tags = {r["tag"]: r for r in read(os.path.join(DATA, "tags.csv"))}
    size = {r["version"]: r for r in read(os.path.join(RESULTS, "size.csv"))}
    met = read(os.path.join(RESULTS, "metrics.csv"))
    by = {(m["version"], m["arch"]): m for m in met}
    ncp = os.path.join(RESULTS, "noise_comparison.csv")
    nc = {r["version"]: r for r in read(ncp)} if os.path.exists(ncp) else None
    vs = [v["version"] for v in vers]
    t = {}

    rows, prev = [], None
    for v in vers:
        s = size[v["version"]]
        top = int(v["top_level_classes"])
        growth = f"{100 * (top - prev) / prev:+.1f}%" if prev else "–"
        prev = top
        mod = [v["modules_with_code"]] if "modules_with_code" in v else []
        rows.append([v["version"], tags[v["version"]]["date"]] + mod +
                    [v["packages"], v["class_files"], top, growth,
                     s["class_dependencies"],
                     f"{int(s['class_dependencies']) / int(s['classes']):.2f}"])
    t["TABLE_SIZE"] = table(["Version", "Date"] + (["Modules"] if "modules_with_code" in vers[0] else [])
                            + ["Packages", "Class files", "Top-level classes", "Δ classes",
                               "Dependencies", "Deps/class"], rows)

    rows = []
    for v in vs:
        s = size[v]
        cmp_ = [nc[v]["jnode3_noise"], nc[v]["jnode4_noise"], nc[v]["jaccard"]] if nc else []
        rows.append([v, s["connected_classes"], s["isolated_classes"], s["noise_classes"],
                     s["noise_pct"] + "%"] + cmp_ + [
                     "yes" if s["noise_fallback"] == "True" else ""])
    t["TABLE_NOISE"] = table(["Version", "Connected classes", "Isolated", "Noise (top-level)",
                              "Noise %"] +
                             (["JNode-3 noise files", "JNode-4 noise files", "Jaccard 3 vs 4"] if nc else [])
                             + ["Fallback"], rows)

    def arch_table(key, fmt="{}"):
        rows = []
        for v in vs:
            rows.append([v] + [fmt.format(float(by[(v, a)][key])) for a in
                               ("A1", "A2", "A3", "A4", "PKG")])
        return table(["Version", "A1 ACDC", "A2 ACDC−noise", "A3 k-means",
                      "A4 k-means−noise", "Packages"], rows)

    t["TABLE_K"] = arch_table("clusters", "{:.0f}")
    t["TABLE_MQ"] = arch_table("mq", "{:.4f}")
    t["TABLE_COH"] = arch_table("cohesion", "{:.4f}")
    t["TABLE_COUP"] = arch_table("coupling", "{:.5f}")

    def mean(a, key):
        xs = [float(by[(v, a)][key]) for v in vs]
        return sum(xs) / len(xs)

    mojo = {r["version"]: r for r in read(os.path.join(RESULTS, "mojofm.csv"))}
    rows = []
    for a, name in (("A1", "A1 ACDC (full)"), ("A2", "A2 ACDC (no noise)"),
                    ("A3", "A3 k-means (full)"), ("A4", "A4 k-means (no noise)"),
                    ("PKG", "Packages (full)"), ("PKG_nonoise", "Packages (no noise)")):
        mj = (f"{sum(float(mojo[v][f'{a}_vs_PKG']) for v in vs) / len(vs):.1f}"
              if a.startswith("A") else "–")
        rows.append([name, f"{mean(a, 'clusters'):.0f}", f"{mean(a, 'max_cluster'):.0f}",
                     f"{mean(a, 'cohesion'):.4f}", f"{mean(a, 'coupling'):.5f}",
                     f"{mean(a, 'mq'):.4f}", mj])
    t["TABLE_MEANS"] = table(["Architecture", "k", "Largest cluster", "Cohesion", "Coupling",
                              "MQ", "MoJoFM to packages (%)"], rows)

    ai = read(os.path.join(RESULTS, "ai_metrics.csv"))
    latest = vs[-1]
    rows = []
    for name, m in [("AI (P3), full", ai[0]), ("AI (P3), no noise", ai[1])] + \
                   [(n, by[(latest, a)]) for n, a in (("A1 ACDC", "A1"), ("A2 ACDC−noise", "A2"),
                                                      ("A3 k-means", "A3"), ("A4 k-means−noise", "A4"),
                                                      ("Packages", "PKG"))]:
        rows.append([name, m["clusters"], m["max_cluster"], m["cohesion"], m["coupling"], m["mq"]])
    t["TABLE_AI"] = table([f"Architecture ({latest})", "k", "Largest", "Cohesion", "Coupling",
                           "MQ"], rows)
    t["TABLE_AI_COMP"] = table(["Component", "Classes"],
                               [[r["component"], r["classes"]] for r in
                                read(os.path.join(RESULTS, "ai_components.csv"))])

    rows = [[r["graph"], r["patterns"], r["max_cluster_size"], r["clusters"], r["max_cluster"],
             r["cohesion"], r["coupling"], r["mq"]]
            for r in read(os.path.join(RESULTS, "acdc_params.csv"))]
    t["TABLE_ACDC"] = table(["Graph", "Patterns", "Max size", "k", "Largest", "Cohesion",
                             "Coupling", "MQ"], rows)

    mcp = os.path.join(RESULTS, "module_changes.csv")
    if os.path.exists(mcp):
        rows = [[r["to"], r["modules"], r["added"], r["removed"]] for r in read(mcp)]
        t["TABLE_MODCHANGES"] = table(["Version", "Modules", "Added", "Removed"], rows)
    pcp = os.path.join(RESULTS, "package_changes.csv")
    if os.path.exists(pcp):
        rows = [[r["to"], r["packages"], r["added"], r["removed"], r["classes_added"],
                 r["classes_removed"]] for r in read(pcp)]
        t["TABLE_PKGCHANGES"] = table(["Version", "Packages", "Pkgs added", "Pkgs removed",
                                       "Classes added", "Classes removed"], rows)

    def opt(name):
        p = os.path.join(RESULTS, name)
        return read(p) if os.path.exists(p) else None

    rows = opt("mojofm.csv")
    if rows:
        t["TABLE_MOJO"] = table(["Version", "A1 → PKG", "A2 → PKG", "A3 → PKG", "A4 → PKG"],
                                [[r["version"], r["A1_vs_PKG"], r["A2_vs_PKG"], r["A3_vs_PKG"],
                                  r["A4_vs_PKG"]] for r in rows])
        last = rows[-1]
        t["TABLE_MOJO_AI"] = table(["MoJoFM (%) to the AI architecture", "A1", "A2", "A3", "A4",
                                    "Packages"],
                                   [[latest] + [last[f"{a}_vs_AI"] for a in
                                                ("A1", "A2", "A3", "A4", "PKG")]])
    rows = opt("mojofm_stability.csv")
    if rows:
        t["TABLE_MOJO_STAB"] = table(["Version (vs previous)", "A1", "A2", "A3", "A4"],
                                     [[r["to"], r["A1"], r["A2"], r["A3"], r["A4"]] for r in rows])
    rows = opt("bunch_noise.csv")
    if rows:
        t["TABLE_BUNCH"] = table(["Version", "Bunch (>3·avg)", "JNode", "Both", "Jaccard",
                                  "MQ System", "MQ JNode", "MQ Bunch", "MoJoFM System",
                                  "MoJoFM JNode", "MoJoFM Bunch"],
                                 [[r["version"], r["bunch_noise"], r["jnode_noise"], r["common"],
                                   r["jaccard"], f"{float(r['mq_A1_system']):.3f}",
                                   f"{float(r['mq_A2_jnode']):.3f}", f"{float(r['mq_A2_bunch']):.3f}",
                                   r["mojofm_A1_system"], r["mojofm_A2_jnode"], r["mojofm_A2_bunch"]]
                                  for r in rows])
    rows = opt("smells.csv")
    if rows:
        t["TABLE_SMELLS"] = table(["Version", "Cyclic pkgs %", "Cyclic classes %", "Hub-like %",
                                   "Unstable dep. %", "God comp.", "God components"],
                                  [[r["version"], r["cyclic_packages_pct"], r["cyclic_classes_pct"],
                                    r["hub_like_pct"], r["unstable_dep_pct"], r["god_components"],
                                    " ".join(short(n) for n in r["god_component_names"].split()[:6])
                                    + (" …" if len(r["god_component_names"].split()) > 6 else "")]
                                   for r in rows])
    rows = opt("dependency_changes.csv")
    if rows:
        t["TABLE_DEPCHANGES"] = table(["Version", "Dependencies", "Added", "Removed"],
                                      [[r["to"], r["dependencies"], r["added"], r["removed"]]
                                       for r in rows])
    rows = opt("activity.csv")
    if rows:
        t["TABLE_ACTIVITY"] = table(["From", "To", "Days", "Commits", "Authors", "Commits/month"],
                                    [[r["from"], r["to"], r["days"], r["commits"], r["authors"],
                                      r["commits_per_month"]] for r in rows])

    src = open(os.path.join(PROJECT_DIR, "report", "report_src.md")).read()
    missing = set(re.findall(r"\{\{(\w+)\}\}", src)) - set(t)
    if missing:
        raise SystemExit(f"unknown placeholders: {missing}")
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: t[m.group(1)], src)
    with open(os.path.join(PROJECT_DIR, "report", "report.md"), "w") as f:
        f.write(out)
    print("report/report.md written")


if __name__ == "__main__":
    main()
