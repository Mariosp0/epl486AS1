#!/usr/bin/env python3
"""Development activity between the analysed releases (Lehman's law 4,
conservation of organisational stability: is the work rate constant?).

Counts commits and distinct authors on the history between consecutive
analysed tags. Usage: [PROJECT=..] python3 scripts/activity.py <git clone>
Output: results/activity.csv
"""
import csv
import datetime as dt
import os
import subprocess
import sys

from common import DATA, RESULTS, versions, write_csv


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                          check=True).stdout


def main():
    repo = sys.argv[1]
    vs = versions()
    with open(os.path.join(DATA, "tags.csv")) as f:
        date = {r["tag"]: r["date"] for r in csv.DictReader(f)}
    rows = []
    for a, b in zip(vs, vs[1:]):
        log = git(repo, "log", "--format=%ae", f"v{a}..v{b}").split()
        days = (dt.date.fromisoformat(date[b]) - dt.date.fromisoformat(date[a])).days
        rows.append({"from": a, "to": b, "days": days, "commits": len(log),
                     "authors": len(set(log)),
                     "commits_per_month": round(len(log) / max(days, 1) * 30.44, 1)})
        print(rows[-1])
    write_csv(os.path.join(RESULTS, "activity.csv"), rows)


if __name__ == "__main__":
    main()
