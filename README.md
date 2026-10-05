# AGRL130: from Abu Dhabi's air pollution to Dry Rooms

AGRL130 Innovation, Entrepreneurship and Sustainability, IIT Delhi Abu Dhabi. Karthik Nambiar, Sumedh Nitin Jamsandekar, Paul Tiju.

- `index.html`, `data/weather.json`: the week 5 site: a scroll-driven Three.js walkthrough of the system (racks, hot loop, exchanger, filter, coil, desiccant wheel, electrical room), then the problem, evidence, prior art, market, a live cost model that recomputes the moisture load hour by hour and reproduces the paper's Table 2, and the demand test. Static, no build step, d3 and three from unpkg.
- `report.pdf`: the week 5 paper, 13 pages.
- `analysis/week5/build_weather.py`: writes `data/weather.json` from the TMYx 2011 to 2025 files for Abu Dhabi and Dubai International (`analysis/week5/epw/`, from climate.onebuilding.org) and prints the Table 2 check.
- `week3/index.html`, `week3/report.pdf`: the week 3 site and paper, Clean Cabin, reading `data/site.json`.
- `week2/index.html`: the week 2 site, the 43-node demonstration graph.
- `analysis/graph/`, `analysis/solutions/`, `analysis/report/`: the week 3 evidence graph, the 332 interventions and scoring, and the week 3 paper's LaTeX source.
- `build-data.py`: writes `data/site.json` for week 3 from `analysis/`.

Rebuild week 5: `python analysis/week5/build_weather.py`. Rebuild week 3: `python analysis/report/figures.py`, `tectonic analysis/report/main.tex`, `python build-data.py`.
