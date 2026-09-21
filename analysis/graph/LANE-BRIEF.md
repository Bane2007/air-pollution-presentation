# Lane brief, AGRL130 implication graph edge harvesting (2026-09-20)

Purpose: a cited causal graph of air pollution for Abu Dhabi, scaffolded on DPSEEA (driver, pressure, state, exposure, effect, action). The primary runs a near-decomposability analysis on it to find the problem module. Your lane owns one edge family. Node list: `outputs/agrl130-graph/nodes.csv` (id, layer, label, definition, unit, scope). Reference nodes by id only.

## Your outputs, your files only
- `outputs/agrl130-graph/edges-<lane>.csv`, header exactly:
  `src,dst,sign,weight,share,tier,scope,citation,doi_or_url,fetched,evidence`
- `outputs/agrl130-graph/sources-<lane>.md`: one line per source, citation, DOI or URL, what it was used for, tier, `fetched: yes`, the date-time fetched.
- `outputs/agrl130-graph/proposed-nodes-<lane>.csv` (same header as nodes.csv plus `citation`): nodes the sources show are missing. Propose, do not use them as edge endpoints.
Write after every 5 edges. Rewrite your own file fully each time (you are its only writer). Last line of edges-<lane>.csv when done: a comment row `# STATUS: complete, N edges, M sources`.

## Columns
- `sign`: `+` more src gives more dst, `-` more src gives less dst.
- `weight`, ordinal, the rule: **3** the source identifies src as the dominant or primary driver of dst, or a quantified contribution of 30 % or more. **2** a substantial documented contribution, 10 to 30 %, or "major but not primary". **1** documented and minor, under 10 %, or only the mechanism is shown.
- `share`: the measured fraction if the source gives one for the UAE, Abu Dhabi or the Gulf, else blank. Global shares go in `evidence`, not here.
- `tier`: **1** systematic review, meta-analysis, WHO or equivalent guideline synthesis. **2** primary measured study. **3** modelling study, emission inventory, official statistics or technical report. **4** grey literature, news, agency web page.
- `scope`: `abu_dhabi`, `uae`, `gulf`, `global`, the geography of the evidence. Prefer Abu Dhabi, then UAE, then Gulf, then global. A global edge with a local confirmation gets two rows.
- `citation`: `Surname Year, short title`. `doi_or_url`: the DOI or the URL fetched. `fetched`: `yes` only after the abstract, page or PDF text was read this session.
- `evidence`: one sentence, what the source states that supports the edge, with the number if it gives one. No interpretation.

## Rules
- Every source fetched this session via semanticscholar, arxiv, pubmed, WebFetch, WebSearch or scrapling. A source remembered but not fetched is not written.
- The source must state the relation between the two nodes. A source that discusses both nodes without linking them does not support the edge.
- Every edge in your family with real evidence gets a row. Do not pad with edges the evidence does not support. Target 30 to 45 edges per lane, quality over count.
- Every row is a claim the group will defend in front of the instructor. Write nothing you could not read back to a reviewer.
- No em dashes, no semicolons, plain sentences.
- No compute. Shell only for `curl` of a PDF and `pdftotext`.
- Report back in under 150 words: edge count, source count, the three strongest edges, any node you proposed, anything you could not source.

## Lanes
- `lane1-driver-pressure`: edges D→P, D→D and D→S (drivers to emissions, drivers to each other, drivers to meteorology).
- `lane2-pressure-state`: edges P→S and S→S (emissions to ambient concentrations, atmospheric chemistry, meteorology, near-road gradient, school gate, indoor and in-vehicle).
- `lane3-state-exposure`: edges S→X and X→X (concentrations to exposure and dose, time-activity, microenvironments, disparity).
- `lane4-exposure-effect`: edges X→E, S→E where the literature states it that way, and E→E (health, cost, absenteeism, climate).
- `lane5-actions`: edges A→D, A→P, A→S, A→X (every lever and the nodes it acts on), with the measured effect size where a study or evaluation gives one.

## Round 2 lanes (2026-09-20 20:10), fairness round
The first round gave the school problem 15 dedicated nodes and the other problems the class raised 0 to 3. Round 2 gives every candidate problem comparable node detail. `nodes.csv` now holds 160 nodes. Each round 2 lane owns a set of NEW node ids and writes every evidenced edge that touches them, in either direction, to any node in the file (new or old). Same columns, same weight rule, same fetch rule. Do not prioritise any problem over another.
- `lane6-outdoor-occupational`: D23 D24 D25 P31 S28 S29 S30 X14 X15 X16 X17 X18 E18 E19 A22 A23 A24 A25
- `lane7-buildings-vehicles`: D26 P30 P32 P33 S26 S31 S32 S33 S34 X19 E20 A21 A26 A27 A28
- `lane8-proposed-nodes`: D19 D20 D21 D22 P27 P28 P29 S24 S25 S27 X13 E16 E17 A19 A20
