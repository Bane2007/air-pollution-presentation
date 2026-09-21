#!/usr/bin/env python3
"""Writes data/site.json for the week 3 site from the vault's agrl130 folders.
Needs numpy and networkx. Every number the site shows comes
from here, and every value here comes from the same files the paper's figures.py reads."""
import csv, json, os, sys, collections
import numpy as np

VAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analysis")
G_DIR = os.path.join(VAULT, "graph")
S_DIR = os.path.join(VAULT, "solutions")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "site.json")
sys.path.insert(0, G_DIR)
from decompose import load, build

def rd(p): return list(csv.DictReader(open(p)))

# ---- the graph and the four separable blocks ----
nodes, rows = load(G_DIR)
G = build(nodes, rows)
res = json.load(open(os.path.join(G_DIR, "results.json")))
sep = [m for m in res if m["qualifies"] and m["eps_sym"] < 1.0]
assert len(sep) == 4
block_of = {}
for i, m in enumerate(sep, 1):
    for n in m["members"]: block_of[n] = i
BLOCK_NAME = {1: "outdoor dust and occupational", 2: "school gate and idling", 3: "child and commuter dose", 4: "ambient, near-road, riders"}
graph = {
    "nodes": [{"id": n, "layer": G.nodes[n]["layer"], "label": G.nodes[n]["label"], "def": nodes[n]["definition"], "block": block_of.get(n, 0)} for n in G],
    "edges": [{"s": u, "t": v, "w": d["w"], "n": d["n"]} for u, v, d in G.edges(data=True)],
    "blocks": [{"k": i, "name": BLOCK_NAME[i], "n": m["n"], "W_in": m["W_in"], "eps_sym": round(m["eps_sym"], 3), "eps_out": round(m["eps_out"], 3), "eps_in": round(m["eps_in"], 3)} for i, m in enumerate(sep, 1)],
    "all_blocks": [{"k": i, "n": m["n"], "W_in": m["W_in"], "eps_sym": round(m["eps_sym"], 3), "qualifies": m["qualifies"]} for i, m in enumerate(res, 1)],
    "counts": {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "rows": len(rows),
               "dois": len({r["doi_or_url"] for r in rows if "doi.org" in r["doi_or_url"]}),
               "layers": dict(collections.Counter(nodes[n]["layer"] for n in nodes))},
}

# ---- perturbation: who leaks least, 200 trials ----
T = rd(os.path.join(G_DIR, "trials.csv")); W = rd(os.path.join(G_DIR, "winners.csv"))
rank1 = {i: sum(r["rank"] == "1" for r in T if r["block"] == str(i)) / 200 for i in range(1, 5)}
vend = sum(r["winner_members"] == "A23 D24 P31 S29 X16" for r in W) / 200
jac = {i: float(np.mean([float(r["jaccard"]) for r in T if r["block"] == str(i)])) for i in range(1, 5)}
perturb = {"rank1": rank1, "vendor_chain": vend, "jaccard_mean": jac, "trials": 200}

# ---- exposure loads (impact note, figures.py LOADS and PP, paper Table 3) ----
loads = [
    {"block": 1, "name": "construction workers on site", "L": 16.9, "lo": 13.0, "hi": 20.8, "N": 324879, "h": 8, "dC": "6.5 (5 to 8)",
     "src": "N: SCAD 2024 labour force x 14.1 % construction x 83.4 % outdoors (Al Hurini 2024). dC: Azarmi 2016 fine-fraction increment at a demolition site."},
    {"block": 4, "name": "near-road residents and delivery riders", "L": 7.0, "lo": 3.1, "hi": 18.2, "N": "840,000 + 26,186", "h": "16 + 8", "dC": "0.43 + 6",
     "src": "Residents: 2.8 M x 0.3 within 300 m (unsourced fraction), Seagram 2019 near-road increment x I/O 0.5 (Yuan 2020). Riders: Abu Dhabi Mobility 2024 motorcycles, Patel 2016."},
    {"block": 3, "name": "child commute (bus, car, walk)", "L": 4.47, "lo": 4.3, "hi": 4.7, "N": "237,111 bus + 115,676 car + 43,443 walk", "h": "1.33 / 0.67 / 0.5", "dC": "13 / 3 / 6",
     "src": "Abu Dhabi Mobility 2024 school transport, Badri 2012 mode split, Adar 2015 in-cabin 20 vs roadway 13 vs ambient 7 ug/m3 over 597 trips on 188 buses."},
    {"block": 2, "name": "school gate zone", "L": 0.68, "lo": 0.34, "hi": 1.22, "N": 396230, "h": "0.5 (0.25 to 0.75)", "dC": "3.45 (3.45 to 4.11)",
     "src": "ADCCI 2024 pupils, Adams and Requia 2017 mean drop-off increment across 86 schools, Ryan 2013 at the most-bused school."},
]
per_person = [{"who": "construction worker", "block": 1, "v": 52}, {"who": "delivery rider", "block": 4, "v": 48}, {"who": "pupil on a bus", "block": 3, "v": 17},
              {"who": "near-road resident", "block": 4, "v": 6.8}, {"who": "pupil at the gate", "block": 2, "v": 1.7}]

# ---- the inventory, gates, rubric ----
S = rd(os.path.join(S_DIR, "solutions.csv"))
C = ["User", "Feasibility", "Implementability", "Usability", "Market", "Impact", "Measurability", "Time", "Novelty", "Cure", "Transfer"]
W0 = [1, 2, 2, 1, 1, 3, 2, 1, 2, 2, 1]
GATES = ["G1 reach", "G2 semester", "G3 additive", "G4 no law change"]
def first_fail(r):
    for k, g in enumerate(GATES):
        if r[g] == "fail": return k + 1
    return 0
solutions = [{"id": r["id"], "p": r["problem"], "edge": r["edge"], "cls": r["class"], "text": r["solution"], "fail": first_fail(r),
              "s": [int(float(r[c])) for c in C] if r["gates"] == "through" else None,
              "ws": float(r["weighted score (max 90)"]) if r["gates"] == "through" else None,
              "r1": float(r["round 1 score (max 65)"]) if r["gates"] == "through" else None} for r in S]
through = [s for s in solutions if s["fail"] == 0]
assert len(through) == 232 and len(solutions) == 332
gate_counts = []
alive = list(solutions)
for k in range(1, 5):
    alive = [s for s in alive if s["fail"] != k]
    gate_counts.append(len(alive))
problems = [
    {"id": "P1", "name": "construction workers and site neighbours", "block": 1, "L": "16.9"},
    {"id": "P2", "name": "street food vendors", "block": 1, "L": "no count"},
    {"id": "P3", "name": "school gate and idling", "block": 2, "L": "0.68"},
    {"id": "P4", "name": "child commute and daily dose", "block": 3, "L": "4.47"},
    {"id": "P5", "name": "near-road residents and delivery riders", "block": 4, "L": "7.0"},
]
for p in problems:
    p["generated"] = sum(1 for s in solutions if s["p"] == p["id"])
    p["through"] = sum(1 for s in through if s["p"] == p["id"])
    p["edges"] = len({s["edge"] for s in solutions if s["p"] == p["id"]})
    p["top"] = max(s["ws"] for s in through if s["p"] == p["id"])
rubric = [
    {"c": "user", "w": 1, "who": "instructor", "five": "the exposed person asks for it", "one": "imposed with no felt benefit"},
    {"c": "feasibility", "w": 2, "who": "instructor", "five": "built or done with our resources this term", "one": "needs an organisation we are not"},
    {"c": "implementability", "w": 2, "who": "instructor", "five": "one person must say yes", "one": "a regulator plus an industry"},
    {"c": "usability", "w": 1, "who": "instructor", "five": "passive, no behaviour change", "one": "needs daily discipline"},
    {"c": "market and business", "w": 1, "who": "instructor", "five": "clear buyer, repeatable", "one": "none"},
    {"c": "impact", "w": 3, "who": "ours", "five": "removes most of the block's load for everyone in the microenvironment", "one": "marginal"},
    {"c": "measurability", "w": 2, "who": "ours", "five": "a before-and-after reading at one point", "one": "only a survey"},
    {"c": "time to effect", "w": 1, "who": "ours", "five": "the day it is installed", "one": "years"},
    {"c": "novelty", "w": 2, "who": "source", "five": "nothing does this, a startup could own it", "one": "commodity product or standard rule"},
    {"c": "cure", "w": 2, "who": "source", "five": "removes the emission or the behaviour for everyone", "one": "shields one receptor, source untouched"},
    {"c": "transfer", "w": 1, "who": "source", "five": "nothing moved elsewhere", "one": "burden moved to another group, to energy or waste"},
]
gates = [
    {"id": "G1", "name": "reach", "rule": "the group can get to the user or the site this term"},
    {"id": "G2", "name": "semester", "rule": "an effect can be produced and measured by December with instruments the group can borrow or buy"},
    {"id": "G3", "name": "additive", "rule": "not already the standing rule or product in Abu Dhabi"},
    {"id": "G4", "name": "no law change", "rule": "needs no regulator, no new law"},
]

# ---- lambda sweep, SMAA ----
lam = rd(os.path.join(S_DIR, "lambda.csv"))
rob = json.load(open(os.path.join(S_DIR, "robustness.json")))
top = [i for i, _ in rob["top10_baseline"]]
Sid = {s["id"]: s for s in solutions}
def series(i):
    x = np.array(Sid[i]["s"], float); w = np.array(W0, float)
    return [round(float(x @ np.r_[w[:8], w[8:] * float(r["lambda"])]), 2) for r in lam]
lambda_sweep = {"lambda": [float(r["lambda"]) for r in lam], "rows": {i: series(i) for i in top[:5] + ["P5-33"]}}
sm = rd(os.path.join(S_DIR, "smaa.csv"))
smaa_uniform = [[0.0] * 10 for _ in range(10)]
for r in sm:
    if r["scheme"] == "uniform": smaa_uniform[top.index(r["row"])][int(r["rank"]) - 1] = float(r["acceptability"])

# ---- the exact 10,000 uniform draws, replayed in the browser to the paper's 86.0 % ----
X = np.array([[float(v) for v in s["s"]] for s in through]); ids = [s["id"] for s in through]
W0a = np.array(W0, float)
rng = np.random.default_rng(0); N = 10000
rng.dirichlet(W0a, N); rng.uniform(0.5 * W0a, 1.5 * W0a, (N, 11))          # consumed in this order by robustness.py
Wu = rng.dirichlet(np.ones(11), N) * W0a.sum()
winners = (X @ Wu.T).argmax(axis=0)
pick = ids.index("P4-71")
share = float((winners == pick).mean())
assert abs(share - rob["rank1"]["uniform"]["P4-71"]) < 1e-9, (share, rob["rank1"]["uniform"]["P4-71"])
win_ids = sorted(set(winners.tolist()), key=lambda j: -(winners == j).sum())
win_index = {j: k for k, j in enumerate(win_ids)}
smaa = {"draws": N, "scheme": "uniform Dirichlet(1,...,1), seed 0, weights scaled to sum 18", "winner_ids": [ids[j] for j in win_ids],
        "winner_seq": "".join(chr(48 + win_index[j]) for j in winners.tolist()),
        "weights_sample": np.round(Wu[:400], 2).tolist(), "rank1": rob["rank1"], "central": rob["central_weights"]["uniform"],
        "leave_one_out_first_in_all": all(v["pick_rank"] == 1 for v in rob["leave_one_out"].values()),
        "round1_tie": rob["round1_rubric_on_final"], "uniform_matrix": smaa_uniform, "top10": rob["top10_baseline"]}

# ---- failure modes (figures.py MODES, review note titles, paper Table 4 rules) ----
MODES = [
 ("F1","heat","fatal","removed","Engine-off staging is not available in the Gulf, the idle is the air conditioning","never ask anyone to sit in the heat with the engine off"),
 ("F2","heat","fatal","removed","A just-in-time call relocates the wait, it does not remove it","remove the emission, not the place it happens"),
 ("F3","heat","major","removed","The child is moved outdoors earlier",""),("F4","heat","major","open","Dust days and the hot months",""),
 ("F5","traffic","fatal","removed","The call system only exists at dismissal, the morning is a throughput queue","act on both sessions of the day"),
 ("F6","traffic","major","n/a","Kerb geometry",""),("F7","traffic","major","n/a","Bus slots fight route variance and boarding time",""),
 ("F8","traffic","major","removed","Siblings",""),("F9","traffic","minor","remains","Restart pulses",""),
 ("F10","people","major","removed","The hired driver",""),("F11","people","major","removed","Arrive-early culture is a rational strategy",""),
 ("F12","people","minor","removed","Gaming the tap",""),("F13","people","minor","n/a","Marshals",""),
 ("F14","rules","major","removed","The gate road is a public road",""),("F15","rules","major","removed","ADEK's transport policy is a safety system with named rules",""),
 ("F16","rules","fatal","removed","Children's location data, no school signs that with a student group in a term","no parent, driver or app in the loop"),
 ("F17","rules","major","remains","206 operators, the contract is not the school's to rewrite",""),("F18","rules","minor","open","Procurement and liability",""),
 ("F19","instrument","fatal","removed","The gate effect is below the noise of what the group can afford","measure inside a closed volume, paired with the air outside the same bus, before and after"),
 ("F20","instrument","major","removed","The arterial next door",""),("F21","instrument","major","removed","Confounds in the term",""),
 ("F22","mechanism","major","removed","Sealed, air-conditioned classrooms",""),("F23","mechanism","major","removed","Total emissions may not fall",""),
 ("F24","mechanism","major","removed","The bigger term is the bus cabin",""),
 ("F25","market","major","removed","The car half already exists as a product",""),("F26","market","major","remains","Nobody buys air, the grade makes the buyer",""),
 ("F27","market","minor","open","Defensibility",""),("F28","market","minor","remains","A student team, one term, no company",""),
 ("F29","course","major","open","The instructor's question",""),
]
fmea = [{"id": f, "layer": l, "sev": s, "state": st, "title": t, "rule": r} for f, l, s, st, t, r in MODES]
assert len(fmea) == 29 and sum(m["sev"] == "fatal" for m in fmea) == 5

# ---- prior art (figures.py ART) and the pick ----
prior_art = [
    {"label": "closed-crankcase system, in-cabin ultrafine count, test track, 1 bus", "cite": "Rowan for NJDEP 2008", "lo": 50, "hi": 100, "note": "50 to over 100 %"},
    {"label": "DOC + CCV, in-cabin particles, three US states", "cite": "as cited by Pedde et al. 2023", "lo": 50, "hi": 60, "note": "50 to 60 %"},
    {"label": "CCV + DOC, in-cabin hopanes, PAH, aliphatics, 3 buses on route", "cite": "Trenbath et al. 2009", "lo": 37, "hi": 50, "pt": 43, "note": "37, 43, 50 %"},
    {"label": "ULSD, DOC or CCV, on-board particles, 188 buses, 597 trips", "cite": "Adar et al. 2015", "lo": 10, "hi": 50, "note": "10 to 50 %"},
    {"label": "retrofits, in-cabin particles, tailpipe cut 20 to 94 %", "cite": "Zhang and Zhu 2011", "lo": 0, "hi": 0, "note": "no unequivocal cabin decrease"},
]
pick = {"id": "P4-71", "score": 79, "runner": {"id": "P2-46", "score": 74, "name": "clean cooking zone pilot at one market"},
        "scores": Sid["P4-71"]["s"], "runner_scores": Sid["P2-46"]["s"],
        "scale": {"pupils": 237111, "buses": 8568, "operators": 206, "schools": 672, "minutes": 80, "increment": 13, "pupils_2026": 279000, "buses_2026": 10000, "src_2026": "Abu Dhabi Mobility, reported by Gulf News 30 Aug 2026: more than 10,000 licensed school buses, more than 279,000 pupils"},
        "signal": {"cabin": 20, "ambient": 7, "roadway": 13, "src": "Adar 2015, 597 trips on 188 buses"},
        "self_pollution": "about 50 % of in-cabin PM2.5 is the bus's own with windows closed, over three quarters of that from the crankcase (dual-tracer study, 2011)",
        "pilot": [{"w0": 0, "w1": 3, "label": "diagnose, validate: paired sensors on 10 to 20 buses with the state log, a borrowed black-carbon or particle-number instrument beside them on 2 to 4", "block": 3},
                  {"w0": 3, "w1": 7, "label": "classify the source, repair: leak, open crankcase, intake, roadside background, tailpipe geometry, or none", "block": 1},
                  {"w0": 7, "w1": 12, "label": "verify, grade: re-log the same buses, report and grade per bus", "block": 4}],
        "success": "fixed in advance: for every flagged bus the idle cabin excess after the repair falls, paired and within-bus, into the range of the unflagged buses, and the source found is written down",
        "scorejitter": json.load(open(os.path.join(S_DIR, "scorejitter.json"))),
        "dropout": json.load(open(os.path.join(G_DIR, "dropout.json")))}

site = {"built": "2026-09-21", "graph": graph, "perturb": perturb, "loads": loads, "per_person": per_person, "problems": problems,
        "solutions": solutions, "gate_counts": gate_counts, "gates": gates, "rubric": rubric, "criteria": C, "weights": W0,
        "lambda": lambda_sweep, "smaa": smaa, "fmea": fmea, "prior_art": prior_art, "pick": pick}
json.dump(site, open(OUT, "w"), separators=(",", ":"))
print("wrote", OUT, os.path.getsize(OUT), "bytes; gates", gate_counts, "share", share, "problems", [(p["id"], p["generated"], p["through"], p["edges"]) for p in problems])
