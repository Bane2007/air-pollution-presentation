# Decomposition results (seed 0, resolution 1.0, 200 sensitivity trials)

Graph: 160 nodes, 337 distinct edges from 418 cited rows, total internal weight 720, 5 isolated nodes.

## Fairness: nodes per candidate problem

| problem | nodes in the graph | ids |
|---|---|---|
| school gate (ours) | 11 | D14 D15 P05 S20 X04 X06 A04 A05 A07 A18 A20 |
| classroom air (another group) | 7 | X10 S26 S32 S33 E20 A15 A27 |
| bus AC idling (another group) | 5 | D26 P32 S31 X19 A26 |
| AC electricity (another group) | 8 | D05 D06 P07 P08 P09 A09 A10 A21 |
| delivery riders (another group) | 5 | D23 S28 X15 A22 E18 |
| street vendors (another group) | 5 | D24 P31 S29 X16 A23 |
| construction dust (another group) | 9 | D09 P16 P17 S30 X17 E19 A12 A24 X14 |
| chiller coil dust (another group) | 3 | S34 P33 A28 |
| near-road residents (literature) | 4 | D25 X18 A25 S18 |

Round 1 (112 nodes) gave the school problem 15 dedicated nodes and the other class problems 0 to 3, and lanes 3 and 5 were told to treat school studies as the highest-value evidence. Round 2 added 48 nodes for the competing problems and the round 1 proposals with neutral lane prompts. This table is the state after round 2.

## Blocks (directed Louvain, Q = 0.604, 14 blocks incl. singletons)

A block qualifies as a problem module when it holds at least one lever (A) and one outcome (X or E). Qualifying blocks first, ranked by symmetric leakage eps_sym.

| rank | qualifies | pareto | n | W_in | eps_sym | eps_out | eps_in | eps_transfer | levers | outcomes | members |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | yes | yes | 17 | 56 | 0.375 | 0.250 | 0.125 | 0.214 | A12 A23 A24 | E18 E19 X14 X16 X17 | A12 A23 A24 D09 D16 D18 D24 E18 E19 P16 P31 S16 S29 S30 X14 X16 X17 |
| 2 | yes | yes | 20 | 63 | 0.556 | 0.365 | 0.190 | 0.143 | A05 A07 A15 A18 A26 A27 | E14 X10 | A05 A07 A15 A18 A26 A27 D04 D14 D15 D26 E14 P05 P32 S07 S08 S13 S20 S21 S26 X10 |
| 3 | yes |  | 19 | 62 | 0.823 | 0.290 | 0.532 | 0.081 | A04 A13 A14 A17 A20 | E05 E06 X03 X04 X05 X06 X07 X08 X09 X11 X13 X19 | A04 A13 A14 A17 A20 E05 E06 P30 S22 X03 X04 X05 X06 X07 X08 X09 X11 X13 X19 |
| 4 | yes | yes | 23 | 91 | 0.934 | 0.363 | 0.571 | 0.066 | A16 A22 A25 | E01 E02 E03 E07 E11 E12 E16 E17 X01 X02 X12 X15 X18 | A16 A22 A25 D23 D25 E01 E02 E03 E07 E11 E12 E16 E17 S01 S09 S17 S18 S28 X01 X02 X12 X15 X18 |
| 5 | yes |  | 16 | 60 | 1.350 | 0.633 | 0.717 | 0.350 | A28 | E04 E08 E10 | A28 E04 E08 E10 P04 P18 P19 P33 S02 S12 S14 S15 S19 S25 S27 S34 |
| 6 | no |  | 2 | 1 | 0.000 | 0.000 | 0.000 | 0.000 |  |  | D11 P21 |
| 7 | no |  | 26 | 89 | 0.258 | 0.124 | 0.135 | 0.101 | A09 A10 A11 A21 |  | A09 A10 A11 A21 D01 D02 D05 D06 D07 D08 D17 D19 D20 D21 P07 P08 P09 P10 P11 P12 P13 P15 P24 P25 P26 S23 |
| 8 | no |  | 28 | 104 | 0.548 | 0.423 | 0.125 | 0.298 | A01 A02 A03 A06 A08 A19 |  | A01 A02 A03 A06 A08 A19 D03 D10 D12 D13 D22 P01 P02 P03 P06 P14 P20 P27 P28 P29 S03 S04 S05 S06 S10 S11 S24 S31 |
| 9 | no |  | 4 | 12 | 0.917 | 0.083 | 0.833 | 0.000 |  | E09 E20 | E09 E20 S32 S33 |

## Separable problem candidates (qualifying blocks with eps_sym below 1)

- eps_sym 0.375, n 17, W_in 56, levers A12 A23 A24, outcomes E18 E19 X14 X16 X17
- eps_sym 0.556, n 20, W_in 63, levers A05 A07 A15 A18 A26 A27, outcomes E14 X10
- eps_sym 0.823, n 19, W_in 62, levers A04 A13 A14 A17 A20, outcomes E05 E06 X03 X04 X05 X06 X07 X08 X09 X11 X13 X19
- eps_sym 0.934, n 23, W_in 91, levers A16 A22 A25, outcomes E01 E02 E03 E07 E11 E12 E16 E17 X01 X02 X12 X15 X18

## Module studied in detail

eps_sym 0.556, eps_out 0.365, eps_in 0.190, eps_transfer 0.143, n 20, W_in 63

- A05 Anti-idling rules (action)
- A07 School-zone design (action)
- A15 School air filtration (action)
- A18 School siting policy (action)
- A26 Idle-reduction technology (action)
- A27 Classroom ventilation upgrade (action)
- D04 Car ownership (driver)
- D14 School trips by car (driver)
- D15 School siting and road hierarchy (driver)
- D26 Bus fleet idling hours (driver)
- E14 Climate forcing (effect)
- P05 Idling emissions (pressure)
- P32 Idling fuel use (pressure)
- S07 Black carbon (state)
- S08 Ultrafine particles (state)
- S13 Boundary layer and stability (state)
- S20 School-gate concentration (state)
- S21 Indoor infiltration (state)
- S26 Indoor-generated classroom particles (state)
- X10 Classroom exposure (exposure)

### Internal edges

- P05 → S20 (w 3, 2 source rows): Idling emissions → School-gate concentration
- S07 → E14 (w 3, 1 source row): Black carbon → Climate forcing
- A05 → S20 (w 3, 1 source row): Anti-idling rules → School-gate concentration
- A05 → S08 (w 3, 1 source row): Anti-idling rules → Ultrafine particles
- A05 → S07 (w 3, 1 source row): Anti-idling rules → Black carbon
- A15 → X10 (w 3, 1 source row): School air filtration → Classroom exposure
- A15 → S21 (w 3, 1 source row): School air filtration → Indoor infiltration
- A18 → X10 (w 3, 1 source row): School siting policy → Classroom exposure
- D26 → P32 (w 3, 1 source row): Bus fleet idling hours → Idling fuel use
- P32 → P05 (w 3, 1 source row): Idling fuel use → Idling emissions
- S26 → X10 (w 3, 4 source rows): Indoor-generated classroom particles → Classroom exposure
- A26 → P32 (w 3, 1 source row): Idle-reduction technology → Idling fuel use
- A26 → D26 (w 3, 1 source row): Idle-reduction technology → Bus fleet idling hours
- A27 → X10 (w 3, 1 source row): Classroom ventilation upgrade → Classroom exposure
- D04 → D14 (w 2, 1 source row): Car ownership → School trips by car
- D14 → P05 (w 2, 1 source row): School trips by car → Idling emissions
- S08 → X10 (w 2, 1 source row): Ultrafine particles → Classroom exposure
- S13 → S20 (w 2, 1 source row): Boundary layer and stability → School-gate concentration
- S20 → S21 (w 2, 1 source row): School-gate concentration → Indoor infiltration
- S20 → X10 (w 2, 2 source rows): School-gate concentration → Classroom exposure
- A05 → P05 (w 2, 2 source rows): Anti-idling rules → Idling emissions
- A07 → S20 (w 2, 1 source row): School-zone design → School-gate concentration
- A07 → D14 (w 2, 1 source row): School-zone design → School trips by car
- D26 → P05 (w 2, 1 source row): Bus fleet idling hours → Idling emissions
- D15 → D14 (w 1, 1 source row): School siting and road hierarchy → School trips by car

### Boundary edges (what leaks in and out)

- out S21 → X09 (w 3): Indoor infiltration → Home indoor exposure
- out X10 → X06 (w 3): Classroom exposure → Child inhaled dose
- in A20 → S08 (w 3): School bus clean technology → Ultrafine particles
- out A27 → S33 (w 3): Classroom ventilation upgrade → Classroom ventilation rate
- in S01 → S21 (w 2): Ambient PM2.5 → Indoor infiltration
- in S03 → X10 (w 2): Ambient NO2 → Classroom exposure
- out S07 → E04 (w 2): Black carbon → Childhood asthma
- out S07 → E05 (w 2): Black carbon → Child lung function
- out S07 → E17 (w 2): Black carbon → Adult asthma onset
- out S13 → S03 (w 2): Boundary layer and stability → Ambient NO2
- out S20 → X04 (w 2): School-gate concentration → Child time at gate and commute
- in D03 → P05 (w 1): Private mobility demand → Idling emissions
- in P20 → S07 (w 1): Shipping emissions → Black carbon
- in S02 → X10 (w 1): Ambient PM10 → Classroom exposure
- in A16 → X10 (w 1): Urban greening → Classroom exposure
- out D26 → S31 (w 1): Bus fleet idling hours → Bus stop and depot concentration
- out D26 → S22 (w 1): Bus fleet idling hours → In-vehicle concentration
- out P32 → P25 (w 1): Idling fuel use → Greenhouse gas emissions
- in S25 → S20 (w 1): Road dust resuspension → School-gate concentration
- out A27 → D05 (w 1): Classroom ventilation upgrade → Electricity demand

## Resolution sweep (best-matching block to the problem module)

- resolution 0.6: Q = 0.683, 12 blocks, best match Jaccard 0.47, n = 43, eps_sym 0.378
- resolution 0.8: Q = 0.643, 14 blocks, best match Jaccard 1.00, n = 20, eps_sym 0.556
- resolution 1.0: Q = 0.604, 14 blocks, best match Jaccard 1.00, n = 20, eps_sym 0.556
- resolution 1.2: Q = 0.582, 17 blocks, best match Jaccard 0.70, n = 14, eps_sym 0.595
- resolution 1.5: Q = 0.549, 19 blocks, best match Jaccard 0.70, n = 14, eps_sym 0.595

## Cross-check partitions

- Leiden, directed modularity (leidenalg): 16 blocks, best match to the module Jaccard 0.85 (n = 17, eps_sym 0.556), that block ranks 3 among qualifying blocks, the leader there is A23 D24 P31 S29 X16
- Greedy modularity, undirected projection (Clauset-Newman-Moore): 18 blocks, best match to the module Jaccard 0.95 (n = 19, eps_sym 0.567), that block ranks 2 among qualifying blocks, the leader there is A23 D24 P31 S29 X16

## Sensitivity

- Every ordinal weight bumped one level up or down at random, 200 reruns: the module's best-matching block has mean Jaccard 0.668 (min 0.27), Jaccard 0.6 or better in 66 % of reruns.
- In those reruns the module's block is the lowest-leakage qualifying block in 10 % of cases. Blocks that beat it, with counts: [A23 D24 P31 S29 X16] 67; [A12 A24 P16 S30 X17] 3; [A12 A24 D02 D17 D21 P16 S14 S19 S23 S30 X17] 3
- Fixed weights, 50 Louvain seeds: mean Jaccard 0.727 (min 0.40), 0.8 or better in 22 % of seeds.

