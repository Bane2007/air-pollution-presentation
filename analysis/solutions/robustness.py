#!/usr/bin/env python3
"""Rank acceptability of the funnel's top rows under weight uncertainty (SMAA-2 style).

Reads solutions.csv (the 232 rows through the gates, eleven 1-to-5 scores). Three weight
distributions, 10,000 draws each, seed 0:
  centred   Dirichlet(alpha = w0), mean equal to the stated weights, sd about half the mean
  pm50      each weight uniform on [0.5 w0, 1.5 w0], independent
  uniform   Dirichlet(1, ..., 1), no preference information at all (classic SMAA)
For every draw the weighted sum ranks all 232 rows; the rank acceptability index b_i^r is
the share of draws in which row i holds rank r. Also: leave-one-criterion-out winners, the
round 1 rubric (eight criteria) applied to the final inventory, and a sweep of the scale
factor lambda on the three criteria added in round 2 (novelty, cure, transfer).

Writes smaa.csv (row, scheme, rank, acceptability), lambda.csv, robustness.json.
"""
import csv, json
import numpy as np

C = ["User","Feasibility","Implementability","Usability","Market","Impact","Measurability","Time","Novelty","Cure","Transfer"]
W0 = np.array([1,2,2,1,1,3,2,1,2,2,1], float)
R1 = C[:8]                       # round 1 criteria, weights W0[:8], max 65
rows = [r for r in csv.DictReader(open("solutions.csv")) if r["gates"] == "through"]
X = np.array([[float(r[c]) for c in C] for r in rows])       # 232 x 11
ids = [r["id"] for r in rows]
name = {r["id"]: r["solution"] for r in rows}
base = X @ W0
order0 = np.argsort(-base, kind="stable")
top = [ids[i] for i in order0[:10]]
rng = np.random.default_rng(0)
N = 10000
schemes = {
    "centred": rng.dirichlet(W0, N) * W0.sum(),
    "pm50": rng.uniform(0.5 * W0, 1.5 * W0, (N, len(C))),
    "uniform": rng.dirichlet(np.ones(len(C)), N) * W0.sum(),
}
out = {"n_rows": len(rows), "draws": N, "top10_baseline": [(i, float(base[ids.index(i)])) for i in top], "rank1": {}, "central_weights": {}}
sm = csv.writer(open("smaa.csv", "w", newline="")); sm.writerow(["row", "scheme", "rank", "acceptability"])
for sname, Wd in schemes.items():
    S = X @ Wd.T                                   # 232 x N
    rk = (-S).argsort(axis=0).argsort(axis=0) + 1  # rank of each row per draw
    acc = {}
    for i in top:
        k = ids.index(i)
        for r in range(1, 11):
            a = float((rk[k] == r).mean())
            sm.writerow([i, sname, r, f"{a:.4f}"])
        acc[i] = float((rk[k] == 1).mean())
    out["rank1"][sname] = acc
    # central weight vector for the pick: mean of the draws in which it ranks first (SMAA-2)
    k = ids.index(top[0]); win = rk[k] == 1
    out["central_weights"][sname] = dict(zip(C, (Wd[win].mean(axis=0) / Wd[win].mean(axis=0).sum() * W0.sum()).round(2).tolist())) if win.any() else None
    # who else wins, share of draws
    w1 = (rk == 1).mean(axis=1)
    out.setdefault("winners", {})[sname] = {ids[j]: float(w1[j]) for j in np.argsort(-w1)[:8] if w1[j] > 0}
# leave one criterion out
loo = {}
for j, c in enumerate(C):
    w = W0.copy(); w[j] = 0
    s = X @ w; o = np.argsort(-s, kind="stable")
    loo[c] = {"winner": ids[o[0]], "winner_score": float(s[o[0]]), "pick_rank": int(np.where(o == ids.index(top[0]))[0][0] + 1), "pick_score": float(s[ids.index(top[0])])}
out["leave_one_out"] = loo
# round 1 rubric on the final inventory
s1 = X[:, :8] @ W0[:8]; o1 = np.argsort(-s1, kind="stable")
out["round1_rubric_on_final"] = {"top5": [(ids[i], float(s1[i])) for i in o1[:5]], "pick_rank": int(np.where(o1 == ids.index(top[0]))[0][0] + 1), "pick_score": float(s1[ids.index(top[0])])}
# lambda sweep on novelty, cure, transfer
lam = csv.writer(open("lambda.csv", "w", newline="")); lam.writerow(["lambda", "winner", "winner_score"] + top[:5])
for L in np.round(np.arange(0, 2.01, 0.05), 2):
    w = W0.copy(); w[8:] *= L
    s = X @ w; o = np.argsort(-s, kind="stable")
    lam.writerow([L, ids[o[0]], f"{s[o[0]]:.2f}"] + [f"{s[ids.index(i)]:.2f}" for i in top[:5]])
json.dump(out, open("robustness.json", "w"), indent=1)
print(json.dumps(out["rank1"], indent=1)); print("LOO", {c: (v["winner"], v["pick_rank"]) for c, v in loo.items()})
print("round1 on final", out["round1_rubric_on_final"]); print("winners", out["winners"])
