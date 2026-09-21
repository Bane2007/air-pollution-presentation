# Round 2 filters, 2026-09-21 03:10, after Karth's objection that purifiers topped round 1.
# Per surviving solution id: (Novelty, Cure, Transfer, Impact override or None).
# Novelty (w2): 5 nothing does this, a startup could own it; 4 exists elsewhere, not here, needs adaptation; 3 known practice in a new combination or setting; 2 straight transfer of a known practice; 1 commodity product or standard rule.
# Cure (w2): 5 removes the emission or the exposure-producing behaviour for everyone in the microenvironment; 4 removes most of it at the source; 3 blocks the path for everyone; 2 shields a subgroup or shortens their time; 1 shields one receptor, source untouched.
# Transfer (w1, the graph's eps_transfer at solution level): 5 nothing moved elsewhere; 4 small energy or materials cost; 3 ongoing consumable or energy; 2 the burden moves to another group or place; 1 both.
# Impact override: round 1 scored classroom filtration on the school block as if it removed the gate load; it removes only the classroom carry-over term, so those rows are reset to 2.
X = {
"P1-01":(2,4,3,None),"P1-02":(2,4,3,None),"P1-03":(1,3,4,None),"P1-04":(1,3,3,None),"P1-06":(1,4,4,None),"P1-07":(2,4,4,None),"P1-10":(1,3,5,None),
"P1-12":(4,4,3,None),"P1-13":(2,3,3,None),"P1-16":(1,1,2,None),"P1-17":(2,1,3,None),"P1-18":(2,2,4,None),"P1-20":(3,3,5,None),"P1-21":(4,2,4,None),
"P1-23":(3,2,5,None),"P1-25":(4,4,3,None),"P1-27":(2,3,3,None),"P1-28":(1,3,4,None),"P1-32":(3,2,5,None),"P1-33":(2,1,3,None),"P1-34":(2,2,5,None),
"P1-35":(3,1,4,None),"P1-36":(3,2,4,None),"P1-37":(1,3,5,None),"P1-38":(3,2,5,None),"P1-39":(3,2,4,None),"P1-40":(2,2,5,None),"P1-41":(2,1,2,None),
"P1-42":(3,2,4,None),"P1-44":(1,1,5,None),"P1-46":(1,1,5,None),"P1-48":(1,2,5,None),"P1-51":(3,2,5,None),"P1-54":(2,2,5,None),"P1-56":(3,2,4,None),
"P1-58":(4,2,5,None),"P1-59":(3,2,4,None),"P1-60":(1,2,3,None),
"P2-01":(2,5,3,None),"P2-02":(3,5,3,None),"P2-03":(2,4,4,None),"P2-04":(1,3,5,None),"P2-06":(2,4,3,None),"P2-07":(5,5,4,None),"P2-08":(2,3,3,None),
"P2-09":(3,3,3,None),"P2-10":(3,3,3,None),"P2-11":(1,3,3,None),"P2-12":(3,2,5,None),"P2-14":(2,2,5,None),"P2-15":(3,2,5,None),"P2-16":(2,2,5,None),
"P2-17":(1,1,2,None),"P2-18":(1,1,2,None),"P2-19":(1,2,4,None),"P2-23":(3,3,5,None),"P2-24":(2,3,5,None),"P2-25":(4,4,4,None),"P2-26":(4,4,3,None),
"P2-27":(2,3,5,None),"P2-28":(2,3,3,None),"P2-29":(3,2,4,None),"P2-30":(2,2,2,None),"P2-31":(3,2,5,None),"P2-32":(2,2,5,None),"P2-34":(1,1,5,None),
"P2-35":(1,2,5,None),"P2-36":(1,1,5,None),"P2-37":(4,3,5,None),"P2-39":(3,4,3,None),"P2-40":(3,2,4,None),"P2-41":(2,5,3,None),"P2-42":(3,3,3,None),
"P2-43":(3,3,3,None),"P2-44":(3,2,5,None),"P2-45":(3,3,5,None),"P2-46":(3,5,3,None),"P2-47":(2,1,5,None),"P2-49":(2,3,5,None),"P2-50":(3,2,5,None),
"P3-01":(1,4,5,None),"P3-02":(1,3,5,None),"P3-03":(2,4,5,None),"P3-04":(2,4,5,None),"P3-05":(3,4,4,None),"P3-06":(1,3,5,None),"P3-08":(4,4,5,None),
"P3-09":(2,4,5,None),"P3-10":(2,4,5,None),"P3-11":(3,5,2,None),"P3-12":(2,4,2,None),"P3-13":(2,4,5,None),"P3-14":(2,4,5,None),"P3-15":(2,3,3,None),
"P3-16":(2,4,5,None),"P3-18":(3,4,3,None),"P3-19":(1,2,4,None),"P3-21":(2,4,3,None),"P3-22":(2,4,3,None),"P3-23":(2,4,2,None),"P3-24":(2,4,5,None),
"P3-25":(1,1,2,2),"P3-26":(1,1,3,2),"P3-27":(2,1,3,2),"P3-28":(1,1,4,2),"P3-29":(2,1,2,2),"P3-30":(3,1,3,2),"P3-33":(2,2,5,None),"P3-34":(2,4,5,None),
"P3-37":(2,4,3,None),"P3-38":(3,4,5,None),"P3-40":(3,4,5,None),"P3-41":(2,4,5,None),"P3-43":(2,1,3,2),"P3-44":(3,1,4,2),"P3-47":(3,4,4,None),
"P3-48":(1,3,5,None),"P3-50":(1,3,5,None),"P3-52":(2,4,5,None),"P3-53":(2,4,5,None),"P3-54":(1,3,5,None),"P3-55":(2,3,5,None),"P3-56":(2,3,3,None),
"P3-59":(4,3,5,None),"P3-60":(2,1,5,None),"P3-61":(1,1,5,2),"P3-62":(1,1,5,2),"P3-63":(2,1,3,None),"P3-64":(1,3,4,None),"P3-65":(1,3,5,None),
"P3-66":(1,4,5,None),"P3-67":(2,1,5,None),"P3-68":(2,2,5,None),"P3-69":(3,3,4,None),"P3-70":(2,2,5,None),"P3-73":(3,2,4,None),"P3-74":(3,4,5,None),
"P3-76":(2,4,4,None),"P3-77":(2,3,5,None),"P3-78":(1,1,5,None),"P3-80":(3,3,3,None),"P3-81":(3,4,3,None),
"P4-01":(2,4,4,None),"P4-03":(3,3,5,None),"P4-04":(2,3,4,None),"P4-05":(1,2,5,None),"P4-06":(2,1,3,None),"P4-07":(4,3,4,None),"P4-08":(3,2,5,None),
"P4-09":(3,2,5,None),"P4-10":(4,2,5,None),"P4-11":(3,2,5,None),"P4-12":(2,2,4,None),"P4-13":(4,2,4,None),"P4-14":(2,2,5,None),"P4-15":(1,1,5,None),
"P4-16":(1,1,5,None),"P4-17":(1,1,5,None),"P4-19":(2,4,4,None),"P4-23":(3,2,5,None),"P4-24":(2,4,5,None),"P4-25":(2,4,5,None),"P4-26":(2,4,5,None),
"P4-27":(2,4,4,None),"P4-28":(1,3,4,None),"P4-29":(1,4,5,None),"P4-30":(1,1,2,None),"P4-31":(2,3,5,None),"P4-32":(1,2,5,None),"P4-33":(1,2,5,None),
"P4-34":(1,1,3,None),"P4-35":(2,2,5,None),"P4-36":(2,2,5,None),"P4-37":(3,3,5,None),"P4-38":(2,2,5,None),"P4-39":(1,2,4,None),"P4-41":(3,3,5,None),
"P4-42":(2,3,3,None),"P4-43":(2,2,4,None),"P4-44":(2,3,4,None),"P4-45":(2,2,5,None),"P4-46":(2,2,4,None),"P4-47":(2,2,5,None),"P4-48":(2,1,5,None),
"P4-49":(1,1,5,None),"P4-50":(2,2,5,None),"P4-51":(3,2,4,None),"P4-52":(3,3,5,None),"P4-53":(3,2,5,None),"P4-54":(2,1,4,None),"P4-55":(1,1,3,None),
"P4-56":(1,1,2,None),"P4-57":(3,4,5,None),"P4-58":(2,4,5,None),"P4-59":(3,3,5,None),"P4-60":(2,3,5,None),"P4-62":(1,2,5,None),"P4-63":(3,2,5,None),
"P4-64":(2,1,3,None),"P4-65":(3,2,4,None),"P4-66":(4,3,5,None),"P4-69":(2,2,5,None),"P4-70":(2,2,4,None),"P4-71":(4,4,5,None),
"P5-05":(1,1,2,None),"P5-06":(3,2,4,None),"P5-07":(4,3,4,None),"P5-08":(2,1,3,None),"P5-10":(3,1,3,None),"P5-13":(1,1,5,None),"P5-14":(4,2,4,None),
"P5-15":(4,3,3,None),"P5-24":(2,3,5,None),"P5-28":(2,1,2,None),"P5-33":(1,1,2,None),"P5-34":(1,1,3,None),"P5-35":(2,1,5,None),"P5-36":(3,2,5,None),
"P5-37":(2,2,5,None),"P5-38":(2,2,5,None),"P5-39":(3,1,4,None),"P5-45":(2,1,2,None),"P5-47":(1,1,5,None),"P5-54":(3,2,4,None),"P5-55":(2,1,5,None),
"P5-64":(2,2,5,None),"P5-65":(2,2,5,None),"P5-66":(1,1,5,None),"P5-67":(4,3,4,None),"P5-68":(2,1,3,None),"P5-69":(1,1,5,None),"P5-70":(3,2,5,None),
}
# problem-level potential on the same three filters
PX = {"P1":(4,4,4),"P2":(4,5,3),"P3":(3,4,3),"P4":(4,4,5),"P5":(4,3,4)}  # P3 and P4 revised 04:10 after the pre-mortem
W2 = {"Novelty":2,"Cure":2,"Transfer":1}
