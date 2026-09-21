# Anchor: two planted blocks joined by one weak edge. The ranked top module must be one block with eps_transfer = 1/W_in.
import sys, random
sys.path.insert(0, '/home/karth/obsidian/brain/outputs/agrl130-graph')
import decompose as d
nodes = {}
rows = []
def add(nid, layer): nodes[nid] = dict(id=nid, layer=layer, label=nid)
# block A: driver, pressure, state, exposure, action, dense; block B: same shape
for blk in ('A', 'B'):
    ids = [f'{blk}{i}' for i in range(6)]
    layers = ['driver', 'pressure', 'state', 'exposure', 'effect', 'action']
    for i, l in zip(ids, layers): add(i, l)
    for u in ids:
        for v in ids:
            if u != v and random.random() < 0.7:
                rows.append(dict(src=u, dst=v, weight='3'))
rows.append(dict(src='A2', dst='B1', weight='1'))  # the single weak coupling, lands on a pressure node
G = d.build(nodes, rows)
comms, cands = d.louvain_modules(G, 0)
cands += d.acl_sweeps(G)
r = d.rank(G, cands)
top = r[0]
print('top members', top['members'], 'eps_transfer', round(top['eps_transfer'], 4), 'eps_out', round(top['eps_out'], 4), 'W_in', top['W_in'])
assert set(top['members']) in (set(f'A{i}' for i in range(6)), set(f'B{i}' for i in range(6))), 'planted block not recovered'
expected = 1 / top['W_in'] if set(top['members']) == set(f'A{i}' for i in range(6)) else 0.0
assert abs(top['eps_transfer'] - expected) < 1e-9, (top['eps_transfer'], expected)
print('ANCHOR OK: planted block recovered, leakage equals the one weak edge over W_in')
