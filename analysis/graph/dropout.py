#!/usr/bin/env python3
"""Inclusion robustness: does the partition survive missing evidence, not just re-weighted evidence?
Three tests against the baseline four blocks (results.json): (a) rebuild on tier 1 and 2 rows only,
(b) 200 trials dropping 10 % and 20 % of the tier 3 and 4 rows at random, (c) leave one source out,
one trial per distinct citation. Same Louvain settings as decompose.py (resolution 1.0), seed per trial.
Writes dropout.csv (test, trial, block, jaccard) and dropout.json (summary)."""
import csv, json, os, random, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decompose import load, build, blocks_at, jaccard
HERE = os.path.dirname(os.path.abspath(__file__))
nodes, rows = load()
res = json.load(open(os.path.join(HERE, "results.json")))
blocks = [(i + 1, set(m["members"])) for i, m in enumerate(res) if m["qualifies"] and m["eps_sym"] < 1.0]
assert len(blocks) == 4
out = csv.writer(open(os.path.join(HERE, "dropout.csv"), "w", newline="")); out.writerow(["test", "trial", "block", "jaccard"])
summ = {}
def score(test, trial, sub, seed):
    G = build(nodes, sub); cs, _ = blocks_at(G, 1.0, seed)
    js = {}
    for bid, S in blocks:
        j = max(jaccard(c, S) for c in cs); js[bid] = j; out.writerow([test, trial, bid, f"{j:.4f}"])
    return js
# (a) tier 1 and 2 only
t12 = [r for r in rows if r["tier"] in ("1", "2")]
summ["tier12_only"] = {"rows": len(t12), "jaccard": score("tier12", 0, t12, 1)}
# (b) random dropout of tier 3 and 4 rows
low = [i for i, r in enumerate(rows) if r["tier"] in ("3", "4")]
for frac in (0.10, 0.20):
    random.seed(int(frac * 100)); acc = collections.defaultdict(list)
    for t in range(200):
        drop = set(random.sample(low, int(round(frac * len(low)))))
        sub = [r for i, r in enumerate(rows) if i not in drop]
        js = score(f"drop{int(frac*100)}", t, sub, t + 1)
        for b, j in js.items(): acc[b].append(j)
    summ[f"drop{int(frac*100)}"] = {"rows_dropped": int(round(frac * len(low))), "of_low_tier": len(low),
        "mean": {b: sum(v) / len(v) for b, v in acc.items()}, "ge06": {b: sum(x >= 0.6 for x in v) / len(v) for b, v in acc.items()}}
# (c) leave one source out
cites = sorted({r["citation"] for r in rows}); acc = collections.defaultdict(list); worst = {}
for k, c in enumerate(cites):
    sub = [r for r in rows if r["citation"] != c]
    js = score("loso", k, sub, 1)
    for b, j in js.items():
        acc[b].append(j)
        if j < worst.get(b, (2, ""))[0]: worst[b] = (j, c)
summ["leave_one_source_out"] = {"sources": len(cites), "mean": {b: sum(v) / len(v) for b, v in acc.items()},
    "min": {b: worst[b][0] for b in worst}, "min_source": {b: worst[b][1] for b in worst}, "ge06": {b: sum(x >= 0.6 for x in v) / len(v) for b, v in acc.items()}}
json.dump(summ, open(os.path.join(HERE, "dropout.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
