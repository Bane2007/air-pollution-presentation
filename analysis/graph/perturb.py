#!/usr/bin/env python3
"""Perturbation and seed stability for every separable block, dumped per trial.

Same experiment as decompose.py's sensitivity section (global seed 0, every ordinal
weight bumped one level up or down, Louvain seed t+1 per trial) but evaluated for all
four qualifying blocks with eps_sym below 1 at once, and written row by row so the
report's figures use the raw trials. Run from the graph venv (leidenalg not needed).

Writes trials.csv   trial, block, n, jaccard, rank            one row per trial per block
       winners.csv  trial, winner_n, winner_eps, winner_members
       seeds.csv    seed, block, jaccard                      50 Louvain seeds, fixed weights
"""
import csv, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decompose import load, build, blocks_at, leak, jaccard

HERE = os.path.dirname(os.path.abspath(__file__))
TRIALS = 200
nodes, rows = load()
G = build(nodes, rows)
res = json.load(open(os.path.join(HERE, "results.json")))
blocks = [(i + 1, set(m["members"])) for i, m in enumerate(res) if m["qualifies"] and m["eps_sym"] < 1.0]
assert len(blocks) == 4, blocks

def qualifying(Gp, comms):
    out = []
    for c in comms:
        m = leak(Gp, c)
        if m and m["levers"] and m["outcomes"]:
            m["members"] = sorted(c)
            out.append(m)
    out.sort(key=lambda m: (round(m["eps_sym"], 4), -m["n"]))
    return out

random.seed(0)
tr = csv.writer(open(os.path.join(HERE, "trials.csv"), "w", newline=""))
tr.writerow(["trial", "block", "n", "jaccard", "rank"])
wn = csv.writer(open(os.path.join(HERE, "winners.csv"), "w", newline=""))
wn.writerow(["trial", "winner_n", "winner_eps", "winner_members"])
for t in range(TRIALS):
    ws = [min(3, max(1, int(r["weight"]) + random.choice((-1, 1)))) for r in rows]
    Gp = build(nodes, rows, ws)
    cs, _ = blocks_at(Gp, 1.0, 0 + t + 1)
    q = qualifying(Gp, cs)
    for bid, S in blocks:
        jall = max(jaccard(c, S) for c in cs)                      # membership stability, any block (as decompose.py)
        j = [jaccard(m["members"], S) for m in q]
        best = max(range(len(j)), key=lambda i: j[i])             # rank of the best-matching qualifying block
        tr.writerow([t, bid, len(S), f"{jall:.4f}", best + 1])
    w = q[0]
    wn.writerow([t, w["n"], f"{w['eps_sym']:.4f}", " ".join(w["members"])])
sd = csv.writer(open(os.path.join(HERE, "seeds.csv"), "w", newline=""))
sd.writerow(["seed", "block", "jaccard"])
for s in range(1, 51):
    cs, _ = blocks_at(G, 1.0, s)
    for bid, S in blocks:
        sd.writerow([s, bid, f"{max(jaccard(c, S) for c in cs):.4f}"])
print("done")
