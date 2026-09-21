# Air pollution, Abu Dhabi: from a cited implication graph to Clean Cabin

AGRL130 Innovation, Entrepreneurship and Sustainability, IIT Delhi Abu Dhabi. Karthik Nambiar, Sumedh Nitin Jamsandekar, Paul Tiju Thomas.

- `index.html`, `data/site.json`: the week 3 site, five animated slides (the need, the mind map, the filters, applied, Clean Cabin). Static, no build step, libraries from unpkg.
- `report.pdf`: the week 3 paper, 16 pages.
- `week2/index.html`: the week 2 site as it was, the 43-node demonstration graph.
- `analysis/graph/`: the 160-node evidence graph (`nodes.csv`, `edges-lane*.csv`, `sources-lane*.md`), the decomposition (`decompose.py`), weight perturbation (`perturb.py`), inclusion robustness (`dropout.py`).
- `analysis/solutions/`: the 332 interventions with gates and scores (`solutions.csv`, `inventory.py`, `build.py`), SMAA over the weights (`robustness.py`) and over the scores (`scorejitter.py`).
- `analysis/report/`: the paper's LaTeX source, bibliography, figure script (`figures.py`) and figures.
- `build-data.py`: writes `data/site.json` from `analysis/`.

Rebuild: `python analysis/report/figures.py`, `tectonic analysis/report/main.tex`, `python build-data.py`.
