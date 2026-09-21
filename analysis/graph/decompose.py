#!/usr/bin/env python3
"""Near-decomposability search on the AGRL130 implication graph.

Reads nodes.csv and edges-lane*.csv, builds a weighted directed graph (ordinal
weights 1 to 3, duplicate pairs keep the max), then scores candidate modules by
the Simon-Ando leakage ratios:

  W_in(S)        sum of weights of edges inside S
  eps_out(S)     weight leaving S / W_in(S)                (all outbound coupling)
  eps_transfer(S) weight leaving S that lands on a driver, pressure or state node
                  / W_in(S)                                (footprint transfer proper)
  eps_in(S)      weight entering S / W_in(S)               (dependence on what we do not control)
  eps_sym(S)     (weight leaving S + weight entering S) / W_in(S), the Simon-Ando off-block
                  coupling in both directions, the ranking criterion

Candidates come from three generators: Louvain communities (directed modularity),
unions of adjacent communities, and Andersen-Chung-Lang sweeps of a personalised
PageRank vector seeded at every exposure and effect node. A module qualifies when
it holds at least one lever (A) and one outcome (X or E) and carries at most half
of the system's internal coupling (a module is a part). Sensitivity: every
ordinal weight is bumped one level up or down at random, and the top module's
membership stability is reported as mean Jaccard over the trials.

Usage: decompose.py [--seed N] [--trials N] [--out results.md]
"""
import argparse, csv, glob, itertools, json, os, random
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))


def load(here=HERE):
    nodes = {r["id"]: r for r in csv.DictReader(open(os.path.join(here, "nodes.csv")))}
    rows = []
    for f in sorted(glob.glob(os.path.join(here, "edges-lane*.csv"))):
        rows += [r for r in csv.DictReader(l for l in open(f) if not l.startswith("#"))]
    return nodes, rows


def build(nodes, rows, weights=None):
    G = nx.DiGraph()
    for nid, r in nodes.items():
        G.add_node(nid, layer=r["layer"], label=r["label"])
    for i, r in enumerate(rows):
        w = weights[i] if weights is not None else int(r["weight"])
        u, v = r["src"], r["dst"]
        if u == v:
            continue
        if G.has_edge(u, v):
            G[u][v]["w"] = max(G[u][v]["w"], w)
            G[u][v]["n"] += 1
        else:
            G.add_edge(u, v, w=w, n=1)
    return G


def leak(G, S):
    S = set(S)
    w_in = sum(d["w"] for u, v, d in G.edges(data=True) if u in S and v in S)
    w_out = sum(d["w"] for u, v, d in G.edges(data=True) if u in S and v not in S)
    w_tr = sum(d["w"] for u, v, d in G.edges(data=True)
               if u in S and v not in S and G.nodes[v]["layer"] in ("driver", "pressure", "state"))
    w_inb = sum(d["w"] for u, v, d in G.edges(data=True) if u not in S and v in S)
    if w_in == 0:
        return None
    return dict(n=len(S), W_in=w_in, eps_out=w_out / w_in, eps_transfer=w_tr / w_in, eps_in=w_inb / w_in,
                eps_sym=(w_out + w_inb) / w_in,
                levers=sorted(x for x in S if G.nodes[x]["layer"] == "action"),
                outcomes=sorted(x for x in S if G.nodes[x]["layer"] in ("exposure", "effect")))


def qualifies(m, w_total=None):
    """A module is a part of the system: lever and outcome inside, at least 4 nodes,
    and at most half of the system's internal coupling (otherwise the whole graph wins with zero leakage)."""
    if m is None or not m["levers"] or not m["outcomes"] or m["n"] < 4:
        return False
    if w_total is not None and m["W_in"] > 0.5 * w_total:
        return False
    return True


def total_weight(G):
    return sum(d["w"] for _, _, d in G.edges(data=True))


def louvain_modules(G, seed):
    U = G  # networkx louvain handles DiGraph with directed modularity
    comms = nx.community.louvain_communities(U, weight="w", seed=seed, resolution=1.0)
    comms = [set(c) for c in comms if len(c) >= 2]
    cands = list(comms)
    # unions of adjacent communities
    for a, b in itertools.combinations(range(len(comms)), 2):
        if any(G.has_edge(u, v) or G.has_edge(v, u) for u in comms[a] for v in comms[b]):
            cands.append(comms[a] | comms[b])
    return comms, cands


def acl_sweeps(G, alpha=0.15, max_size=45):
    """Andersen-Chung-Lang style sweep on personalised PageRank from each outcome seed."""
    Uw = G.to_undirected()
    for u, v, d in Uw.edges(data=True):
        d["w"] = max(G[u][v]["w"] if G.has_edge(u, v) else 0, G[v][u]["w"] if G.has_edge(v, u) else 0)
    deg = dict(Uw.degree(weight="w"))
    cands = []
    wt = total_weight(G)
    seeds = [n for n, d in G.nodes(data=True) if d["layer"] in ("exposure", "effect") and deg.get(n, 0) > 0]
    for s in seeds:
        pr = nx.pagerank(Uw, alpha=1 - alpha, personalization={s: 1.0}, weight="w")
        order = sorted((n for n in pr if deg.get(n, 0) > 0), key=lambda n: -pr[n] / deg[n])
        best = None
        for k in range(4, min(max_size, len(order)) + 1):
            S = set(order[:k])
            m = leak(G, S)
            if qualifies(m, wt) and (best is None or m["eps_sym"] < best[0]):
                best = (m["eps_sym"], S)
        if best:
            cands.append(best[1])
    return cands


def rank(G, cands):
    seen, out = set(), []
    wt = total_weight(G)
    for S in cands:
        key = frozenset(S)
        if key in seen:
            continue
        seen.add(key)
        m = leak(G, S)
        if qualifies(m, wt):
            m["members"] = sorted(S)
            out.append(m)
    # primary order: symmetric leakage (Simon-Ando epsilon, both directions), larger modules break ties
    out.sort(key=lambda m: (round(m["eps_sym"], 4), -m["n"]))
    return out


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def blocks_at(G, res, seed):
    comms = nx.community.louvain_communities(G, weight="w", seed=seed, resolution=res)
    Q = nx.community.modularity(G, comms, weight="w", resolution=res)
    return [set(c) for c in comms], Q


# The problems the class raised on 14 Sep plus two from the literature, as node sets, for the fairness table.
PROBLEMS = {
    "school gate (ours)": "D14 D15 P05 S20 X04 X06 A04 A05 A07 A18 A20",
    "classroom air (another group)": "X10 S26 S32 S33 E20 A15 A27",
    "bus AC idling (another group)": "D26 P32 S31 X19 A26",
    "AC electricity (another group)": "D05 D06 P07 P08 P09 A09 A10 A21",
    "delivery riders (another group)": "D23 S28 X15 A22 E18",
    "street vendors (another group)": "D24 P31 S29 X16 A23",
    "construction dust (another group)": "D09 P16 P17 S30 X17 E19 A12 A24 X14",
    "chiller coil dust (another group)": "S34 P33 A28",
    "near-road residents (literature)": "D25 X18 A25 S18",
}


def leiden_blocks(G):
    """Cross-check partition: Leiden on the same directed weighted graph (leidenalg, modularity)."""
    try:
        import igraph as ig, leidenalg as la
    except ImportError:
        return None
    idx = {n: i for i, n in enumerate(G.nodes())}
    g = ig.Graph(n=len(idx), edges=[(idx[u], idx[v]) for u, v in G.edges()], directed=True)
    g.es["weight"] = [G[u][v]["w"] for u, v in G.edges()]
    part = la.find_partition(g, la.ModularityVertexPartition, weights="weight", seed=0)
    names = list(G.nodes())
    return [set(names[i] for i in c) for c in part]


def greedy_blocks(G):
    """Cross-check partition: deterministic greedy modularity on the undirected projection."""
    U = nx.Graph()
    U.add_nodes_from(G.nodes(data=True))
    for u, v, d in G.edges(data=True):
        if U.has_edge(u, v):
            U[u][v]["w"] += d["w"]
        else:
            U.add_edge(u, v, w=d["w"])
    return [set(c) for c in nx.community.greedy_modularity_communities(U, weight="w")]


def qualifying_rank(G, comms, S):
    """Rank of the block best matching S among qualifying blocks (1 = leaks least), and the winner's members."""
    scored = []
    for c in comms:
        m = leak(G, c)
        if m and m["levers"] and m["outcomes"]:
            m["members"] = sorted(c)
            scored.append(m)
    scored.sort(key=lambda m: (round(m["eps_sym"], 4), -m["n"]))
    if not scored:
        return None, None
    best = max(range(len(scored)), key=lambda i: jaccard(scored[i]["members"], S))
    return best + 1, scored[0]["members"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--resolution", type=float, default=1.0)
    ap.add_argument("--out", default=os.path.join(HERE, "results.md"))
    ap.add_argument("--module", default="", help="space-separated node ids to study instead of the Pareto pick")
    args = ap.parse_args()
    random.seed(args.seed)
    nodes, rows = load()
    G = build(nodes, rows)
    wt = total_weight(G)
    L = []
    L.append(f"# Decomposition results (seed {args.seed}, resolution {args.resolution}, {args.trials} sensitivity trials)\n")
    L.append(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} distinct edges from {len(rows)} cited rows, "
             f"total internal weight {wt}, {sum(1 for n in G if G.degree(n) == 0)} isolated nodes.\n")

    L.append("## Fairness: nodes per candidate problem\n")
    L.append("| problem | nodes in the graph | ids |")
    L.append("|---|---|---|")
    for name, ids in PROBLEMS.items():
        present = [i for i in ids.split() if i in nodes]
        L.append(f"| {name} | {len(present)} | {' '.join(present)} |")
    L.append("")
    L.append("Round 1 (112 nodes) gave the school problem 15 dedicated nodes and the other class problems 0 to 3, and lanes 3 and 5 "
             "were told to treat school studies as the highest-value evidence. Round 2 added 48 nodes for the competing problems "
             "and the round 1 proposals with neutral lane prompts. This table is the state after round 2.\n")

    # 1. partition into blocks (directed Louvain modularity), score every block
    comms, Q = blocks_at(G, args.resolution, args.seed)
    scored = []
    for c in comms:
        m = leak(G, c)
        if m is None:
            continue
        m["members"] = sorted(c)
        m["qualifies"] = bool(m["levers"] and m["outcomes"])
        scored.append(m)
    scored.sort(key=lambda m: (not m["qualifies"], round(m["eps_sym"], 4), -m["n"]))
    # Pareto front over qualifying blocks: low leakage against high internal coupling (size of the problem)
    qual = [m for m in scored if m["qualifies"]]
    for m in qual:
        m["pareto"] = not any(o["eps_sym"] < m["eps_sym"] and o["W_in"] > m["W_in"] for o in qual)
    L.append(f"## Blocks (directed Louvain, Q = {Q:.3f}, {len(comms)} blocks incl. singletons)\n")
    L.append("A block qualifies as a problem module when it holds at least one lever (A) and one outcome (X or E). "
             "Qualifying blocks first, ranked by symmetric leakage eps_sym.\n")
    L.append("| rank | qualifies | pareto | n | W_in | eps_sym | eps_out | eps_in | eps_transfer | levers | outcomes | members |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for i, m in enumerate(scored, 1):
        L.append(f"| {i} | {'yes' if m['qualifies'] else 'no'} | {'yes' if m.get('pareto') else ''} | {m['n']} | {m['W_in']} | {m['eps_sym']:.3f} | {m['eps_out']:.3f} | "
                 f"{m['eps_in']:.3f} | {m['eps_transfer']:.3f} | {' '.join(m['levers'])} | {' '.join(m['outcomes'])} | {' '.join(m['members'])} |")
    L.append("")
    # separable candidates: qualifying blocks whose internal coupling exceeds their total external coupling (eps_sym < 1).
    # The decomposition yields this menu. Choosing among them is an impact and feasibility judgement made outside the graph.
    sep = [m for m in qual if m["eps_sym"] < 1.0]
    L.append("## Separable problem candidates (qualifying blocks with eps_sym below 1)\n")
    for m in sep:
        L.append(f"- eps_sym {m['eps_sym']:.3f}, n {m['n']}, W_in {m['W_in']}, levers {' '.join(m['levers'])}, outcomes {' '.join(m['outcomes'])}")
    L.append("")
    # the module studied in detail below: --module <ids>, else the lowest-leakage qualifying block
    if args.module:
        S = set(args.module.split())
        top = leak(G, S); top["members"] = sorted(S)
    else:
        top = qual[0]
        S = set(top["members"])
    L.append("## Module studied in detail\n")
    L.append(f"eps_sym {top['eps_sym']:.3f}, eps_out {top['eps_out']:.3f}, eps_in {top['eps_in']:.3f}, eps_transfer {top['eps_transfer']:.3f}, n {top['n']}, W_in {top['W_in']}\n")
    for n in top["members"]:
        L.append(f"- {n} {nodes[n]['label']} ({nodes[n]['layer']})")
    L.append("")
    L.append("### Internal edges\n")
    for u, v, d in sorted(G.edges(data=True), key=lambda e: -e[2]["w"]):
        if u in S and v in S:
            L.append(f"- {u} → {v} (w {d['w']}, {d['n']} source row{'s' if d['n'] > 1 else ''}): {nodes[u]['label']} → {nodes[v]['label']}")
    L.append("")
    L.append("### Boundary edges (what leaks in and out)\n")
    for u, v, d in sorted(G.edges(data=True), key=lambda e: -e[2]["w"]):
        if (u in S) != (v in S):
            arrow = "out" if u in S else "in"
            L.append(f"- {arrow} {u} → {v} (w {d['w']}): {nodes[u]['label']} → {nodes[v]['label']}")
    L.append("")

    # 2. resolution sweep: does the module hold at coarser and finer partitions
    L.append("## Resolution sweep (best-matching block to the problem module)\n")
    for res in (0.6, 0.8, 1.0, 1.2, 1.5):
        cs, q = blocks_at(G, res, args.seed)
        best = max(cs, key=lambda c: jaccard(c, S))
        m = leak(G, best)
        L.append(f"- resolution {res}: Q = {q:.3f}, {len(cs)} blocks, best match Jaccard {jaccard(best, S):.2f}, "
                 f"n = {len(best)}, eps_sym {m['eps_sym']:.3f}")
    L.append("")

    # 2b. cross-check partitions from two other algorithms
    L.append("## Cross-check partitions\n")
    for name, cs in (("Leiden, directed modularity (leidenalg)", leiden_blocks(G)),
                     ("Greedy modularity, undirected projection (Clauset-Newman-Moore)", greedy_blocks(G))):
        if cs is None:
            L.append(f"- {name}: not available")
            continue
        best = max(cs, key=lambda c: jaccard(c, S))
        m = leak(G, best)
        rk, winner = qualifying_rank(G, cs, S)
        L.append(f"- {name}: {len(cs)} blocks, best match to the module Jaccard {jaccard(best, S):.2f} (n = {len(best)}, "
                 f"eps_sym {m['eps_sym']:.3f}), that block ranks {rk} among qualifying blocks" +
                 ("" if rk == 1 else f", the leader there is {' '.join(winner)}"))
    L.append("")

    # 3. sensitivity: weights bumped one ordinal level, and Louvain seeds
    jw, rank1, winners = [], 0, {}
    for t in range(args.trials):
        ws = [min(3, max(1, int(r["weight"]) + random.choice((-1, 1)))) for r in rows]
        Gp = build(nodes, rows, ws)
        cs, _ = blocks_at(Gp, args.resolution, args.seed + t + 1)
        jw.append(max(jaccard(c, S) for c in cs))
        rk, winner = qualifying_rank(Gp, cs, S)
        if rk == 1:
            rank1 += 1
        elif winner:
            key = " ".join(winner)
            winners[key] = winners.get(key, 0) + 1
    js = []
    for sd in range(1, 51):
        cs, _ = blocks_at(G, args.resolution, sd)
        js.append(max(jaccard(c, S) for c in cs))
    L.append("## Sensitivity\n")
    L.append(f"- Every ordinal weight bumped one level up or down at random, {args.trials} reruns: the module's best-matching block "
             f"has mean Jaccard {sum(jw)/len(jw):.3f} (min {min(jw):.2f}), Jaccard 0.6 or better in {100*sum(j >= 0.6 for j in jw)/len(jw):.0f} % of reruns.")
    L.append(f"- In those reruns the module's block is the lowest-leakage qualifying block in {100*rank1/args.trials:.0f} % of cases." +
             (" Blocks that beat it, with counts: " + "; ".join(f"[{k}] {v}" for k, v in sorted(winners.items(), key=lambda kv: -kv[1])[:3]) if winners else ""))
    L.append(f"- Fixed weights, 50 Louvain seeds: mean Jaccard {sum(js)/len(js):.3f} (min {min(js):.2f}), "
             f"0.8 or better in {100*sum(j >= 0.8 for j in js)/len(js):.0f} % of seeds.")
    L.append("")
    open(args.out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    json.dump(scored, open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
