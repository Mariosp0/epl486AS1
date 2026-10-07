#!/usr/bin/env python3
"""Compare the noise classes of the original JNode (3-decimal CR model,
data/noise_jnode3/) with the precision-fixed JNode (4 decimals, data/noise/).

JNode rounds CR-model weights to 3 decimals; with more than 2,000 class files
the initial weight 1/n rounds to 0, every SIG becomes 0 and no class is
flagged. The 4-decimal variant avoids this. This script quantifies how much the
extra precision changes the result on the versions where the original worked.
Output: results/noise_comparison.csv
"""
import os

from common import DATA, RESULTS, versions, write_csv


def flagged(path):
    out, sig_nonzero = set(), False
    with open(path) as f:
        next(f)
        for line in f:
            p = line.strip().split(";")
            if p[1] == "1":
                out.add(p[0])
            if float(p[3].replace(",", ".")) > 0:
                sig_nonzero = True
    return out, sig_nonzero


def main():
    rows = []
    for v in versions():
        a, ok = flagged(os.path.join(DATA, "noise_jnode3", f"{v}.csv"))
        b, _ = flagged(os.path.join(DATA, "noise", f"{v}.csv"))
        union = a | b
        rows.append({
            "version": v,
            "jnode3_noise": len(a),
            "jnode3_degenerate": not ok or not a,
            "jnode4_noise": len(b),
            "common": len(a & b),
            "jaccard": round(len(a & b) / len(union), 4) if union else 1.0,
        })
        print(rows[-1])
    write_csv(os.path.join(RESULTS, "noise_comparison.csv"), rows)


if __name__ == "__main__":
    main()
