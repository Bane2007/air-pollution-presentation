#!/usr/bin/env python3
"""Every figure of the report, from the data on disk. Run with ~/.venvs/ml/bin/python.
Reads ../agrl130-graph (graph, blocks, trials) and ../agrl130-solutions (funnel, SMAA).
Writes figures/figN-*.pdf (vector, for LaTeX) and figures/figN-*.png (220 dpi preview)."""
import csv, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
G_DIR = os.path.join(HERE, "..", "graph")
S_DIR = os.path.join(HERE, "..", "solutions")
OUT = os.path.join(HERE, "figures")
sys.path.insert(0, G_DIR)
from decompose import load, build, PROBLEMS

# palette: four separable blocks, validated all-pairs (dataviz validator, light surface)
BLK = {1: "#2a78d6", 2: "#eb6834", 3: "#1baf7a", 4: "#4a3aa7"}
PROB = {"P1": ("#2a78d6", ""), "P2": ("#2a78d6", "////"), "P3": ("#eb6834", ""), "P4": ("#1baf7a", ""), "P5": ("#4a3aa7", "")}
PNAME = {"P1": "P1 construction", "P2": "P2 vendors", "P3": "P3 school gate", "P4": "P4 child commute", "P5": "P5 near-road, riders"}
GREY, INK, INK2, GRID = "#b8b6ae", "#0b0b0b", "#52514e", "#e6e5e0"
fam = "TeX Gyre Pagella" if any(f.name == "TeX Gyre Pagella" for f in font_manager.fontManager.ttflist) else "DejaVu Serif"
plt.rcParams.update({"font.family": fam, "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5, "legend.fontsize": 7.5, "axes.edgecolor": INK2, "axes.linewidth": 0.6, "xtick.color": INK2,
    "ytick.color": INK2, "axes.labelcolor": INK, "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": GRID, "grid.linewidth": 0.5, "legend.frameon": False, "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02})
CM = 1 / 2.54
def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".pdf")); fig.savefig(os.path.join(OUT, name + ".png"), dpi=220); plt.close(fig); print("wrote", name)
def rd(p): return list(csv.DictReader(open(p)))

nodes, rows = load(G_DIR)
G = build(nodes, rows)
res = json.load(open(os.path.join(G_DIR, "results.json")))
sep = [m for m in res if m["qualifies"] and m["eps_sym"] < 1.0]
block_of = {}
for i, m in enumerate(sep, 1):
    for n in m["members"]: block_of[n] = i
BLOCK_NAME = {1: "outdoor dust and occupational", 2: "school gate and idling", 3: "child and commuter dose", 4: "ambient, near-road, riders"}

# ---------- fig 1: the graph by DPSEEA layer, the four separable blocks coloured ----------
def fig1():
    order = ["action", "driver", "pressure", "state", "exposure", "effect"]
    xs = {l: i for i, l in enumerate(order)}
    pos = {}
    for l in order:
        ids = [n for n in G if G.nodes[n]["layer"] == l]
        ids.sort(key=lambda n: (block_of.get(n, 9), n))
        for k, n in enumerate(ids):
            pos[n] = (xs[l], -(k - (len(ids) - 1) / 2))
    fig, ax = plt.subplots(figsize=(16 * CM, 20 * CM))
    for u, v, d in G.edges(data=True):
        bu, bv = block_of.get(u), block_of.get(v)
        col, a, z = (BLK[bu], 0.55, 2) if (bu and bu == bv) else (GREY, 0.18, 1)
        (x0, y0), (x1, y1) = pos[u], pos[v]
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=z,
                    arrowprops=dict(arrowstyle="-", color=col, alpha=a, lw=0.25 * d["w"], shrinkA=3, shrinkB=3,
                                    connectionstyle="arc3,rad=0.12" if x1 > x0 else "arc3,rad=-0.25"))
    for n, (x, y) in pos.items():
        b = block_of.get(n)
        ax.scatter([x], [y], s=34, color=BLK[b] if b else "#ffffff", edgecolor=BLK[b] if b else GREY, lw=0.6, zorder=3)
        ax.text(x, y, n, ha="center", va="center", fontsize=4.3, color="#ffffff" if b else INK2, zorder=4)
    for l, i in xs.items():
        ax.text(i, max(y for _, y in pos.values()) + 1.6, l, ha="center", va="bottom", fontsize=8.5, color=INK)
    ys = [y for _, y in pos.values()]
    ax.set_xlim(-0.6, len(order) - 0.4); ax.set_ylim(min(ys) - 4.6, max(ys) + 2.6); ax.axis("off")
    handles = [Line2D([], [], marker="o", ls="", color=BLK[i], ms=6, label=f"block {i}: {BLOCK_NAME[i]} (n = {sep[i-1]['n']}, ε = {sep[i-1]['eps_sym']:.2f})") for i in BLK]
    handles.append(Line2D([], [], marker="o", ls="", mfc="#ffffff", mec=GREY, ms=6, label="other blocks and isolated nodes"))
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=2, handletextpad=0.3, columnspacing=1.2)
    save(fig, "fig1-graph")

# ---------- fig 2: leakage against internal coupling, every block ----------
def fig2():
    names = {1: "1 outdoor dust,\noccupational", 2: "2 school gate,\nidling", 3: "3 child and\ncommuter dose", 4: "4 ambient, near-road,\nriders",
             5: "5 dust, PM10,\ncoil fouling", 6: "6 (2 nodes)", 7: "7 energy, cooling,\nindustry", 8: "8 traffic emissions,\nfleet levers", 9: "9 classroom CO2"}
    fig, ax = plt.subplots(figsize=(10 * CM, 7.5 * CM))
    ax.axhline(1.0, color=INK2, lw=0.6, ls=(0, (3, 2)) if False else "-", alpha=0.5)
    ax.text(1.5, 1.02, r"$\varepsilon = 1$: as coupled outside as inside", fontsize=7, color=INK2, va="bottom")
    for i, m in enumerate(res, 1):
        b = i if i <= 4 else None
        q = m["qualifies"]
        ax.scatter(m["W_in"], m["eps_sym"], s=14 + 3.2 * m["n"], color=(BLK[b] if b else ("#ffffff")), edgecolor=(BLK[b] if b else INK2),
                   lw=0.7, zorder=3, alpha=0.95 if b else 1.0, marker="o" if q else "s")
        dx, dy = (4, 0.02)
        if i in (7,): dy = 0.05
        if i in (2,): dy = 0.05
        if i in (6,): dy = 0.04
        if i in (1,): dy = -0.14
        if i in (5,): dx, dy = 5, -0.05
        ax.text(m["W_in"] + dx, m["eps_sym"] + dy, names[i], fontsize=6.5, color=INK, va="bottom")
    ax.set_xlabel(r"internal coupling $W_{\mathrm{in}}$ (sum of edge weights inside the block)")
    ax.set_ylabel(r"symmetric leakage $\varepsilon_{\mathrm{sym}}$")
    ax.set_xlim(-2, 125); ax.set_ylim(-0.05, 1.5); ax.grid(axis="y")
    ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="#ffffff", mec=INK2, label="holds a lever and an outcome"),
                       Line2D([], [], marker="s", ls="", mfc="#ffffff", mec=INK2, label="does not qualify")], loc="lower right")
    save(fig, "fig2-leakage")

# ---------- fig 3: perturbation trials ----------
def fig3():
    T = rd(os.path.join(G_DIR, "trials.csv")); W = rd(os.path.join(G_DIR, "winners.csv"))
    fig, (a, b) = plt.subplots(1, 2, figsize=(16 * CM, 6.5 * CM), gridspec_kw={"width_ratios": [1.35, 1]})
    rng = np.random.default_rng(1)
    for i in range(1, 5):
        j = np.array([float(r["jaccard"]) for r in T if r["block"] == str(i)])
        x = i + rng.uniform(-0.22, 0.22, len(j))
        a.scatter(x, j, s=6, color=BLK[i], alpha=0.35, lw=0, zorder=2)
        a.plot([i - 0.3, i + 0.3], [j.mean()] * 2, color=INK, lw=1.2, zorder=3)
        a.text(i, 1.04, f"mean {j.mean():.2f}\n≥ 0.6 in {100*(j>=0.6).mean():.0f} %", ha="center", va="bottom", fontsize=6.8, color=INK2)
    a.axhline(0.6, color=INK2, lw=0.5, alpha=0.5)
    a.set_xticks([1, 2, 3, 4]); a.set_xticklabels([f"block {i}" for i in range(1, 5)])
    a.set_ylabel("Jaccard, best-matching block"); a.set_ylim(0, 1.22); a.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0]); a.grid(axis="y")
    a.set_title("(a) membership stability, 200 weight perturbations", loc="left")
    import collections
    c = collections.Counter(r["winner_members"] for r in W)
    r1 = {i: 100 * sum(r["rank"] == "1" for r in T if r["block"] == str(i)) / 200 for i in range(1, 5)}
    vend = 100 * c["A23 D24 P31 S29 X16"] / 200
    labels = [f"block {i}" for i in range(1, 5)] + ["vendor chain\n(5 nodes)"]
    vals = [r1[i] for i in range(1, 5)] + [vend]
    cols = [BLK[i] for i in range(1, 5)] + [GREY]
    bars = b.barh(labels[::-1], vals[::-1], color=cols[::-1], height=0.62)
    for bar, v in zip(bars, vals[::-1]):
        b.text(v + 1, bar.get_y() + bar.get_height() / 2, f"{v:.0f} %", va="center", fontsize=7.5, color=INK)
    b.set_xlim(0, 50); b.set_xlabel("share of trials in which the block leaks least"); b.grid(axis="x")
    b.set_title("(b) who leaks least under perturbation", loc="left")
    save(fig, "fig3-perturbation")

# ---------- fig 4: coverage, nodes per candidate problem in the final graph ----------
def fig4():
    data = []
    for name, ids in PROBLEMS.items():
        ids = ids.split()
        data.append((name.replace(" (ours)", " (this group)").replace(" (another group)", "").replace(" (literature)", " (from the literature)"),
                     sum(1 for i in ids if i in nodes)))
    data.sort(key=lambda d: d[1])
    fig, ax = plt.subplots(figsize=(9 * CM, 5.6 * CM))
    for k, (n, b) in enumerate(data):
        ax.barh(k, b, color=BLK[1], height=0.6)
        ax.text(b + 0.25, k, str(b), va="center", fontsize=7.5, color=INK)
    ax.set_yticks(range(len(data))); ax.set_yticklabels([d[0] for d in data], fontsize=7.5)
    ax.set_xlabel("nodes in the graph that belong to the problem"); ax.set_xlim(0, 13); ax.grid(axis="x")
    save(fig, "fig4-coverage")

# ---------- fig 5: exposure loads and per-person intensity ----------
LOADS = [  # block term, load M person-ug/m3-h per day, low, high  (impact note, 2026-09-21)
    ("construction workers on site", 1, 16.9, 13.0, 20.8),
    ("near-road residents and riders", 4, 7.0, 3.1, 18.2),
    ("child commute (bus, car, walk)", 3, 4.47, 4.3, 4.7),
    ("school gate zone", 2, 0.68, 0.34, 1.22),
]
PP = [("construction worker", 1, 52), ("delivery rider", 4, 48), ("pupil on a bus", 3, 17), ("near-road resident", 4, 6.8), ("pupil at the gate", 2, 1.7)]
def fig5():
    fig, (a, b) = plt.subplots(1, 2, figsize=(16 * CM, 5.8 * CM), gridspec_kw={"width_ratios": [1.25, 1]})
    for k, (n, blk, v, lo, hi) in enumerate(LOADS[::-1]):
        a.plot([lo, hi], [k, k], color=BLK[blk], lw=1.4, alpha=0.5, solid_capstyle="butt", zorder=2)
        a.scatter([v], [k], s=36, color=BLK[blk], zorder=3)
        a.text(hi * 1.15, k, f"{v:.3g}  ({lo:.3g} to {hi:.3g})", va="center", fontsize=7, color=INK2)
    a.set_yticks(range(4)); a.set_yticklabels([d[0] for d in LOADS[::-1]])
    a.set_xscale("log"); a.set_xlim(0.2, 200); fig.subplots_adjust(wspace=0.55); a.set_xlabel("exposure load L, million person·µg/m³·h per day (log axis)"); a.grid(axis="x")
    a.set_title("(a) block load with its stated range", loc="left")
    for k, (n, blk, v) in enumerate(PP[::-1]):
        b.barh(k, v, color=BLK[blk], height=0.62)
        b.text(v + 1, k, f"{v:g}", va="center", fontsize=7.5, color=INK)
    b.set_yticks(range(5)); b.set_yticklabels([d[0] for d in PP[::-1]]); b.set_xlim(0, 62)
    b.set_xlabel("µg/m³·h per person per day"); b.grid(axis="x"); b.set_title("(b) intensity per exposed person", loc="left")
    save(fig, "fig5-loads")

# ---------- fig 6: the funnel ----------
def fig6():
    S = rd(os.path.join(S_DIR, "solutions.csv"))
    probs = ["P1", "P2", "P3", "P4", "P5"]
    gen = {p: sum(1 for r in S if r["problem"] == p) for p in probs}
    thr = {p: sum(1 for r in S if r["problem"] == p and r["gates"] == "through") for p in probs}
    top = {p: max((float(r["weighted score (max 90)"]) for r in S if r["problem"] == p and r["gates"] == "through")) for p in probs}
    fig, (a, b) = plt.subplots(1, 2, figsize=(16 * CM, 6 * CM), gridspec_kw={"width_ratios": [1.9, 1]})
    x = np.arange(5)
    for i, p in enumerate(probs):
        col, h = PROB[p]
        a.bar(i - 0.19, gen[p], 0.36, facecolor="#ffffff", edgecolor=col, lw=0.9, hatch=h if h else None)
        a.bar(i + 0.19, thr[p], 0.36, color=col, hatch=h if h else None, edgecolor="#ffffff" if h else col, lw=0.4)
        a.text(i - 0.19, gen[p] + 1.5, str(gen[p]), ha="center", fontsize=7, color=INK2)
        a.text(i + 0.19, thr[p] + 1.5, str(thr[p]), ha="center", fontsize=7, color=INK)
    a.set_xticks(x); a.set_xticklabels(["P1\nconstruction", "P2\nvendors", "P3\nschool\ngate", "P4\ncommute", "P5\nnear-road", ], fontsize=6.8); fig.subplots_adjust(wspace=0.7)
    a.set_ylabel("solutions"); a.set_ylim(0, 112); a.grid(axis="y")
    a.legend(handles=[Patch(facecolor="#ffffff", edgecolor=INK2, label="generated (332)"), Patch(facecolor=INK2, label="through the four gates (232)")], loc="upper right")
    a.set_title("(a) generated and surviving, per problem", loc="left")
    classes = ["cut the source", "cut the path", "cut receptor time or intake", "change the decision"]
    g = [sum(1 for r in S if r["class"] == c) for c in classes]; t = [sum(1 for r in S if r["class"] == c and r["gates"] == "through") for c in classes]
    y = np.arange(4)
    b.barh(y + 0.19, g[::-1], 0.36, facecolor="#ffffff", edgecolor=INK2, lw=0.9)
    b.barh(y - 0.19, t[::-1], 0.36, color=INK2)
    for k in range(4):
        b.text(g[::-1][k] + 1.5, k + 0.19, f"{g[::-1][k]}", va="center", fontsize=7, color=INK2)
        b.text(t[::-1][k] + 1.5, k - 0.19, f"{t[::-1][k]}  ({100*t[::-1][k]/g[::-1][k]:.0f} %)", va="center", fontsize=7, color=INK)
    b.set_yticks(y); b.set_yticklabels(["change the\ndecision", "cut receptor\ntime or intake", "cut the path", "cut the source"]); b.set_xlim(0, 150); b.set_xlabel("solutions"); b.grid(axis="x")
    b.set_title("(b) by mechanism class, and the share that passes", loc="left")
    save(fig, "fig6-funnel")

# ---------- fig 7: score distributions and the slope of ranks from round 1 to round 4 ----------
def fig7():
    S = [r for r in rd(os.path.join(S_DIR, "solutions.csv")) if r["gates"] == "through"]
    probs = ["P1", "P2", "P3", "P4", "P5"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(16 * CM, 7 * CM), gridspec_kw={"width_ratios": [0.75, 1.3]})
    rng = np.random.default_rng(2)
    for i, p in enumerate(probs):
        sc = np.array([float(r["weighted score (max 90)"]) for r in S if r["problem"] == p])
        col, h = PROB[p]
        a.scatter(i + rng.uniform(-0.2, 0.2, len(sc)), sc, s=9, color=col, alpha=0.45 if p != "P2" else 0.3, lw=0, zorder=2)
        q1, med, q3 = np.percentile(sc, [25, 50, 75])
        a.plot([i - 0.28, i + 0.28], [med] * 2, color=INK, lw=1.2, zorder=3)
        a.plot([i, i], [q1, q3], color=INK, lw=0.6, zorder=3)
        top = max(S, key=lambda r: (float(r["weighted score (max 90)"]) if r["problem"] == p else -1))
        a.text(i, sc.max() + 1.2, f"{sc.max():.0f}", ha="center", fontsize=7, color=INK)
    a.set_xticks(range(5)); a.set_xticklabels([p for p in probs]); a.set_ylabel("weighted score, max 90"); a.set_ylim(20, 85); a.grid(axis="y")
    a.set_title("(a) the 232 surviving rows, median and quartiles", loc="left")
    # dumbbell: rank without the three source-side criteria against the full rank, log axis
    r1 = sorted(S, key=lambda r: (-float(r["round 1 score (max 65)"]), r["id"]))
    r4 = sorted(S, key=lambda r: (-float(r["weighted score (max 90)"]), -float(r["Cure"]), r["class"] != "cut the source", -float(r["Impact"])))
    rank1 = {r["id"]: k + 1 for k, r in enumerate(r1)}; rank4 = {r["id"]: k + 1 for k, r in enumerate(r4)}
    show = list(dict.fromkeys([r["id"] for r in r4[:8]] + [r["id"] for r in r1[:8]]))
    show.sort(key=lambda i: rank4[i])
    short = {"P4-71": "Clean Cabin", "P5-33": "HEPA purifiers, road-facing bedrooms", "P5-34": "window sealing, MERV13 on the AC", "P2-01": "LPG conversion at stalls",
             "P2-46": "clean cooking zone pilot", "P4-30": "purifier in the child's bedroom", "P4-34": "HEPA cabin filter, family car", "P4-55": "MERV13 on the home AC",
             "P2-02": "induction grill at stalls", "P4-24": "exhaust-leak inspection, every bus", "P3-09": "engine-off training, hired drivers",
             "P2-07": "solar-battery induction cart", "P1-12": "fenceline PM10 sensors"}
    for k, i in enumerate(show[::-1]):
        col, h = PROB[i[:2]]
        b.plot([rank1[i], rank4[i]], [k, k], color=GRID, lw=2, zorder=1)
        b.scatter([rank1[i]], [k], s=24, facecolor="#ffffff", edgecolor=col, lw=0.9, zorder=3)
        b.scatter([rank4[i]], [k], s=24, color=col, zorder=3)
        b.text(max(rank1[i], rank4[i]) * 1.25, k, f"{rank1[i]} → {rank4[i]}", va="center", fontsize=6.5, color=INK2)
    b.set_yticks(range(len(show))); b.set_yticklabels([f"{short[i]} ({i[:2]})" for i in show[::-1]], fontsize=6.8)
    b.set_xscale("log"); b.set_xlim(0.85, 400); b.set_xticks([1, 2, 5, 10, 20, 50, 100, 200]); b.set_xticklabels(["1", "2", "5", "10", "20", "50", "100", "200"])
    b.set_xlabel("rank among the 232 survivors (log axis)"); b.grid(axis="x")
    b.legend(handles=[Line2D([], [], marker="o", ls="", mfc="#ffffff", mec=INK2, label="without novelty, cure, transfer (8 criteria)"),
                      Line2D([], [], marker="o", ls="", color=INK2, label="all eleven criteria")], loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    b.set_title("(b) criteria ablation: rank with and without the three source-side criteria", loc="left")
    fig.subplots_adjust(wspace=1.05)
    save(fig, "fig7-scores")

# ---------- fig 8: rank acceptability and the lambda sweep ----------
def fig8():
    sm = rd(os.path.join(S_DIR, "smaa.csv")); rob = json.load(open(os.path.join(S_DIR, "robustness.json")))
    lam = rd(os.path.join(S_DIR, "lambda.csv"))
    top = [i for i, _ in rob["top10_baseline"]]
    short = {"P4-71": "Clean Cabin", "P2-46": "clean cooking zone", "P2-02": "induction grill", "P2-01": "LPG conversion", "P3-09": "engine-off training",
             "P4-24": "exhaust-leak inspection", "P1-12": "fenceline sensors", "P1-25": "downwind misting", "P2-07": "shared clean kitchen", "P2-03": "stall hoods"}
    fig, (a, b) = plt.subplots(1, 2, figsize=(16 * CM, 6.5 * CM), gridspec_kw={"width_ratios": [1.15, 1]})
    M = np.zeros((10, 10))
    for r in sm:
        if r["scheme"] == "uniform": M[top.index(r["row"]), int(r["rank"]) - 1] = float(r["acceptability"])
    im = a.imshow(M, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#fcfcfb", "#cde2fb", "#3987e5", "#0d366b"]), vmin=0, vmax=1, aspect="auto")
    for i in range(10):
        for j in range(10):
            if M[i, j] >= 0.03:
                a.text(j, i, f"{100*M[i,j]:.0f}", ha="center", va="center", fontsize=6.3, color="#ffffff" if M[i, j] > 0.5 else INK)
    a.set_xticks(range(10)); a.set_xticklabels([str(k) for k in range(1, 11)]); a.set_xlabel("rank r")
    a.set_yticks(range(10)); a.set_yticklabels([f"{short[i]} ({i[:2]})" for i in top], fontsize=7)
    a.set_title("(a) rank acceptability, uniform weights (% of draws)", loc="left")
    a.spines["left"].set_visible(False); a.spines["bottom"].set_visible(False); a.tick_params(length=0)
    L = np.array([float(r["lambda"]) for r in lam])
    # the best purifier row P5-33 is drawn too, so the separation is visible
    S = {r["id"]: r for r in rd(os.path.join(S_DIR, "solutions.csv"))}
    W0 = np.array([1,2,2,1,1,3,2,1,2,2,1], float); C = ["User","Feasibility","Implementability","Usability","Market","Impact","Measurability","Time","Novelty","Cure","Transfer"]
    def series(i):
        x = np.array([float(S[i][c]) for c in C]); return np.array([x @ np.r_[W0[:8], W0[8:] * l] for l in L])
    lines = [(i, series(i)) for i in top[:5]] + [("P5-33", series("P5-33"))]
    short["P5-33"] = "HEPA purifiers (ties at λ = 0)"
    ys = []
    for i, y in lines:
        col, h = PROB[i[:2]]
        b.plot(L, y, color=col, lw=1.5 if i == "P4-71" else 0.9, alpha=1 if i == "P4-71" else 0.85, ls="-" if i != "P5-33" else (0, (4, 2)))
        ys.append([i, y[-1]])
    ys.sort(key=lambda t: t[1])
    for k in range(1, len(ys)):
        if ys[k][1] - ys[k-1][1] < 2.6: ys[k][1] = ys[k-1][1] + 2.6
    for i, yy in ys: b.text(L[-1] + 0.04, yy, short[i], fontsize=6.3, va="center", color=INK)
    b.axvline(1.0, color=INK2, lw=0.5, alpha=0.6); b.axvline(0.0, color=INK2, lw=0.5, alpha=0.6)
    b.text(0.03, 50.8, "λ = 0\neight criteria", fontsize=6.3, color=INK2, va="bottom"); b.text(1.03, 50.8, "λ = 1\nstated weights", fontsize=6.3, color=INK2, va="bottom")
    b.set_xlim(0, 3.1); b.set_ylim(50, 102); b.set_xticks([0, 0.5, 1, 1.5, 2]); b.set_xlabel("λ, scale on the weights of novelty, cure and transfer"); b.set_ylabel("weighted score"); b.grid(axis="y")
    b.set_title("(b) the top five and the best purifier along λ", loc="left")
    save(fig, "fig8-smaa")

# ---------- fig 9: the pre-mortem matrix ----------
MODES = [  # id, layer, severity, state after the redesign
 ("F1","A heat","fatal","removed"),("F2","A heat","fatal","removed"),("F3","A heat","major","removed"),("F4","A heat","major","open"),
 ("F5","B traffic","fatal","removed"),("F6","B traffic","major","n/a"),("F7","B traffic","major","n/a"),("F8","B traffic","major","removed"),("F9","B traffic","minor","remains"),
 ("F10","C people","major","removed"),("F11","C people","major","removed"),("F12","C people","minor","removed"),("F13","C people","minor","n/a"),
 ("F14","D rules","major","removed"),("F15","D rules","major","removed"),("F16","D rules","fatal","removed"),("F17","D rules","major","remains"),("F18","D rules","minor","open"),
 ("F19","E instrument","fatal","removed"),("F20","E instrument","major","removed"),("F21","E instrument","major","removed"),
 ("F22","F mechanism","major","removed"),("F23","F mechanism","major","removed"),("F24","F mechanism","major","removed"),
 ("F25","G market","major","removed"),("F26","G market","major","remains"),("F27","G market","minor","open"),("F28","G market","minor","remains"),
 ("F29","H course","major","open")]
def fig9():
    sev = {"minor": 0, "major": 1, "fatal": 2}
    st = {"removed": (BLK[3], "o", "does not apply to Clean Cabin"), "remains": (BLK[2], "o", "applies, carried into the pilot"),
          "open": ("#ffffff", "o", "open"), "n/a": ("#ffffff", "s", "specific to the gate design, no counterpart")}
    fig, ax = plt.subplots(figsize=(16 * CM, 5.2 * CM))
    layers = list(dict.fromkeys(m[1] for m in MODES))
    for k, (f, lay, s, state) in enumerate(MODES):
        col, mk, _ = st[state]
        ax.scatter([k], [sev[s]], s=70, color=col, edgecolor=INK2 if state in ("open", "n/a") else col, marker=mk, lw=0.8, zorder=3)
        ax.text(k, -0.55, f[1:], ha="center", va="top", fontsize=6.5, color=INK2)
    # layer bands
    x0 = 0
    for lay in layers:
        n = sum(1 for m in MODES if m[1] == lay)
        ax.axvspan(x0 - 0.5, x0 + n - 0.5, color=GRID if layers.index(lay) % 2 else "#ffffff", alpha=0.55, zorder=0, lw=0)
        ax.text(x0 + (n - 1) / 2, 2.6, lay.replace(" ", "\n", 1), ha="center", va="bottom", fontsize=6.8, color=INK, linespacing=1.1)
        x0 += n
    ax.set_yticks([0, 1, 2]); ax.set_yticklabels(["minor", "major", "fatal"]); ax.set_ylim(-0.9, 3.5); ax.set_xlim(-0.7, 28.7)
    ax.set_xticks([]); ax.spines["bottom"].set_visible(False); ax.set_xlabel("failure mode F1 to F29, grouped by layer", labelpad=2)
    ax.legend(handles=[Line2D([], [], marker=v[1], ls="", color=v[0], mec=INK2 if k in ("open", "n/a") else v[0], ms=7, label=v[2]) for k, v in st.items()],
              loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, handletextpad=0.3, columnspacing=1.3)
    save(fig, "fig9-premortem")

# ---------- fig 10: prior art, effect sizes ----------
ART = [  # label, low, high, point, note
    ("CCVS, in-cabin ultrafine count, test track, 1 bus (Rowan for NJDEP 2008)", 50, 100, None, "50 to over 100 %"),
    ("DOC + CCV, in-cabin particles, three US states (as cited by Pedde et al. 2023)", 50, 60, None, "50 to 60 %"),
    ("CCV + DOC, in-cabin hopanes, PAH, aliphatics, 3 buses on route (Trenbath et al. 2009)", 37, 50, 43, "37, 43, 50 %"),
    ("ULSD, DOC or CCV, on-board particles, 188 buses, 597 trips (Adar et al. 2015)", 10, 50, None, "10 to 50 %"),
    ("retrofits, in-cabin particles, tailpipe cut 20 to 94 % (Zhang and Zhu 2011)", 0, 0, 0, "no unequivocal cabin decrease"),
]
def fig10():
    fig, ax = plt.subplots(figsize=(15 * CM, 5.8 * CM))
    for k, (lab, lo, hi, pt, note) in enumerate(ART[::-1]):
        if lo == hi == 0:
            ax.scatter([0], [k], s=40, facecolor="#ffffff", edgecolor=INK2, lw=0.9, zorder=3)
        else:
            ax.plot([lo, hi], [k, k], color=BLK[3], lw=2.2, solid_capstyle="butt", zorder=2)
            if pt is not None: ax.scatter([pt], [k], s=22, color=INK, zorder=3)
        ax.text(max(hi, 2) + 2.5, k, note, va="center", fontsize=8, color=INK2)
    ax.set_yticks(range(len(ART))); ax.set_yticklabels([a[0] for a in ART[::-1]], fontsize=8)
    ax.set_xlim(-5, 125); ax.set_xlabel("reduction of the in-cabin quantity, % (each row is its own metric, no pooled estimate)"); ax.grid(axis="x")
    ax.axvline(0, color=INK2, lw=0.5)
    save(fig, "fig10-priorart")

# ---------- fig 11: the pick's eleven scores against the runner-up ----------
def fig11():
    S = {r["id"]: r for r in rd(os.path.join(S_DIR, "solutions.csv"))}
    C = ["User", "Feasibility", "Implementability", "Usability", "Market", "Impact", "Measurability", "Time", "Novelty", "Cure", "Transfer"]
    W = [1, 2, 2, 1, 1, 3, 2, 1, 2, 2, 1]
    fig, ax = plt.subplots(figsize=(9 * CM, 6.2 * CM))
    y = np.arange(len(C))[::-1]
    for i, (rid, col, lab, off) in enumerate((("P4-71", BLK[3], "Clean Cabin, 79", 0.17), ("P2-46", BLK[1], "clean cooking zone, 74", -0.17))):
        v = [float(S[rid][c]) for c in C]
        ax.hlines(y + off, 0, v, color=col, lw=1.6, alpha=0.9)
        ax.scatter(v, y + off, s=22, color=col, zorder=3, label=lab)
    ax.set_yticks(y); ax.set_yticklabels([f"{c.lower()} (w {w})" for c, w in zip(C, W)], fontsize=7.5)
    ax.set_xlim(0, 5.6); ax.set_xticks([1, 2, 3, 4, 5]); ax.set_xlabel("score, 1 to 5"); ax.grid(axis="x")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, -0.36), ncol=2, handletextpad=0.3)
    save(fig, "fig11-pickscores")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1:] or ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
    for w in which: globals()["fig" + w]()
