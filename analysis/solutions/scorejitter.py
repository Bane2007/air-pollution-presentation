#!/usr/bin/env python3
"""SMAA over scores as well as weights. Each of the 232 x 11 scores is a judgement; a draw moves
every score by -1, 0 or +1 with equal probability (clipped to 1..5) and, in the joint scheme, also
draws the weights from the flat Dirichlet. 10,000 draws, seed 0. Writes scorejitter.json."""
import csv, json
import numpy as np
C = ["User","Feasibility","Implementability","Usability","Market","Impact","Measurability","Time","Novelty","Cure","Transfer"]
W0 = np.array([1,2,2,1,1,3,2,1,2,2,1], float)
rows = [r for r in csv.DictReader(open("solutions.csv")) if r["gates"] == "through"]
X = np.array([[float(r[c]) for c in C] for r in rows]); ids = [r["id"] for r in rows]; k = ids.index("P4-71")
rng = np.random.default_rng(0); N = 10000; out = {"draws": N}
for name, jitter_p in (("scores_pm1_stated_weights", 1.0), ("scores_pm1_uniform_weights", 1.0), ("scores_half_pm1_uniform_weights", 0.5)):
    r1 = 0; ranks = []
    W = rng.dirichlet(np.ones(11), N) * W0.sum() if "uniform" in name else np.tile(W0, (N, 1))
    for d in range(N):
        J = rng.integers(-1, 2, size=X.shape) * (rng.random(X.shape) < jitter_p)
        Xd = np.clip(X + J, 1, 5); s = Xd @ W[d]
        rk = int((s > s[k]).sum()) + 1; ranks.append(rk); r1 += rk == 1
    ranks = np.array(ranks)
    out[name] = {"rank1": r1 / N, "top3": float((ranks <= 3).mean()), "top10": float((ranks <= 10).mean()), "median_rank": float(np.median(ranks)), "p90_rank": float(np.percentile(ranks, 90))}
    print(name, out[name])
json.dump(out, open("scorejitter.json", "w"), indent=1)
