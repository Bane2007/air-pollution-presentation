import importlib.util, collections, csv, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
spec=importlib.util.spec_from_file_location("inv","inventory.py"); inv=importlib.util.module_from_spec(spec); spec.loader.exec_module(inv)
spec2=importlib.util.spec_from_file_location("ext","extra.py"); ext=importlib.util.module_from_spec(spec2); spec2.loader.exec_module(ext)
X=ext.X; PX=ext.PX; W2=ext.W2; C2=list(W2)
S=inv.S; W=inv.WEIGHTS; C=inv.COLS; PR=inv.PROBLEMS
def score(sc, x=None):
    base=sum(v*W[c] for v,c in zip(sc,C))
    return base + (sum(v*W2[c] for v,c in zip(x,C2)) if x else 0)
CLS={"SRC":"cut the source","PATH":"cut the path","RCPT":"cut receptor time or intake","DEC":"change the decision"}
GATE=["G1 reach","G2 semester","G3 additive","G4 no law change"]
# problem-level rubric
PSC={"P1":(4,3,2,3,4,5,4,3),"P2":(4,4,4,4,3,2,5,5),"P3":(5,4,4,4,3,1,3,5),"P4":(4,4,3,4,4,3,5,4),"P5":(4,3,2,3,3,4,3,3)}  # P3, P4 revised 04:10: gate air effect under sensor noise, cabin ratio measurable
rows=[]
n=collections.Counter()
for p,edge,cls,text,gates,sc in S:
    n[p]+=1
    r={"id":f"{p}-{n[p]:02d}","problem":p,"problem_name":PR[p][0],"edge":edge,"class":CLS[cls],"solution":text}
    for g,v in zip(GATE,gates): r[g]={"Y":"pass","V":"pass, to verify","N":"fail"}[v]
    r["gates"]="through" if sc else "out"
    x=None
    if sc and r["problem"]=="P3" and sc[C.index("Measurability")]==5 and r["id"] not in ("P3-25","P3-26","P3-27","P3-28","P3-29","P3-30","P3-43","P3-44","P3-61","P3-62"):
        sc=list(sc); sc[C.index("Measurability")]=3; sc=tuple(sc)   # 04:10 pre-mortem F19: gate air change is under low-cost sensor noise, behaviour is countable
    if sc:
        x=X[r["id"]]
        if x[3] is not None:
            sc=list(sc); sc[C.index("Impact")]=x[3]; sc=tuple(sc)
    for c in C: r[c]=sc[C.index(c)] if sc else ""
    for c in C2: r[c]=x[C2.index(c)] if sc else ""
    r["round 1 score (max 65)"]=score(sc) if sc else ""
    r["weighted score (max 90)"]=score(sc,x[:3]) if sc else ""
    rows.append(r)
cols=list(rows[0].keys())
with open("solutions.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
# ranks
for p in PR:
    pr=[r for r in rows if r["problem"]==p and r["gates"]=="through"]
    pr.sort(key=lambda r:(-r["weighted score (max 90)"], -r["Cure"], r["class"]!="cut the source", -r["Impact"]))
    for i,r in enumerate(pr,1): r["rank in problem"]=i
allp=[r for r in rows if r["gates"]=="through"]; allp.sort(key=lambda r:(-r["weighted score (max 90)"], -r["Cure"], r["class"]!="cut the source", -r["Impact"]))
for i,r in enumerate(allp,1): r["rank overall"]=i
wb=Workbook(); H=Font(bold=True); fill=PatternFill("solid",fgColor="DDDDDD")
def sheet(name, header, data, widths=None):
    ws=wb.create_sheet(name) if wb.sheetnames!=["Sheet"] else wb.active; ws.title=name
    ws.append(header)
    for c in ws[1]: c.font=H; c.fill=fill
    for d in data: ws.append(d)
    if widths:
        for col,wd in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",widths): ws.column_dimensions[col].width=wd
    ws.freeze_panes="A2"
    return ws
sheet("Problems",["id","problem","need statement with boundary","PM2.5 exposure load, M person-ug/m3-h per day (option A)"]+C+C2+["weighted (max 90)","solutions","through gates"],
      [[p,PR[p][0],PR[p][1],PR[p][2] if PR[p][2] is not None else "not computed, vendor count missing"]+list(PSC[p])+list(PX[p])+[score(PSC[p],PX[p]),n[p],sum(1 for r in rows if r["problem"]==p and r["gates"]=="through")] for p in PR],
      [5,34,90,22]+[12]*11+[14,10,12])
sheet("Solutions",cols+["rank in problem","rank overall"],[[r.get(c,"") for c in cols+["rank in problem","rank overall"]] for r in rows],[8,6,30,10,24,80,10,10,14,14,9]+[11]*8+[14,10,10])
sheet("Ranked",["rank overall","rank in problem","problem","class","solution","edge"]+C+C2+["round 1 (max 65)","weighted (max 90)"],[[r["rank overall"],r["rank in problem"],r["problem_name"],r["class"],r["solution"],r["edge"]]+[r[c] for c in C]+[r[c] for c in C2]+[r["round 1 score (max 65)"],r["weighted score (max 90)"]] for r in allp],[8,8,30,24,80,10]+[11]*11+[12,12])
rub=[["Gates, binary, applied to every solution",""],
 ["G1 reach","A student group can get to the user or the site to pilot it this term (a school, a market, a compound, a site fence viewed from the public side)."],
 ["G2 semester","An effect can be produced and measured by December with instruments we can borrow or buy (low-cost PM sensors, a hand-held counter)."],
 ["G3 additive","Not already the standing rule or product in Abu Dhabi. 'To verify' marks the ones we have not checked at source."],
 ["G4 no law change","Can be piloted without an emirate-level rule or zoning change."],
 ["",""],["Scored filters, 1 to 5, weight in brackets, max 90 (round 2 added novelty, cure, transfer after the round 1 top rows were purifiers)",""],
 ["User (1)","Does the exposed person want it and benefit directly. 5 = they ask for it, 1 = imposed with no felt benefit."],
 ["Feasibility (2)","Can it be built or done with our resources and skills this term. 5 = off the shelf, 1 = needs an organisation we are not."],
 ["Implementability (2)","How many actors must say yes. 5 = one person, 3 = one institution, 1 = a regulator plus an industry."],
 ["Usability (1)","Does it keep working without behaviour change or maintenance. 5 = passive, 1 = needs daily discipline."],
 ["Market and business (1)","Is there a buyer and a scalable product or service. 5 = clear buyer and repeatable, 1 = none."],
 ["Impact (3)","Share of the problem's exposure load removed, at scale. 5 = removes most of the load for everyone in the microenvironment, 3 = a large share for a subgroup or a modest share for all, 1 = marginal."],
 ["Measurability (2)","Can we show the effect with an instrument at the site within weeks. 5 = a before-after reading at one point, 1 = only a survey."],
 ["Time to effect (1)","5 = the day it is installed, 3 = a term, 1 = years."],
 ["Novelty (2)","5 = nothing does this, a startup could own it; 4 = exists elsewhere, not here, needs adaptation; 3 = known practice in a new combination or setting; 2 = straight transfer of a known practice; 1 = commodity product or standard rule."],
 ["Cure (2)","Root cause, not symptom. 5 = removes the emission or the exposure-producing behaviour for everyone in the microenvironment; 4 = removes most of it at the source; 3 = blocks the path for everyone; 2 = shields a subgroup or shortens their time; 1 = shields one receptor, source untouched."],
 ["Transfer (1)","The graph's eps_transfer at solution level. 5 = nothing moved elsewhere; 4 = small energy or materials cost; 3 = ongoing consumable or energy; 2 = the burden moves to another group or place; 1 = both."],
 ["Pre-mortem rescoring (04:10)","P3-81, P3-21, P3-22 rescored after outputs/agrl130 - Review - Pre-mortem: engine-off staging is not available in Gulf heat, just-in-time relocates the wait, the gate effect is under low-cost sensor noise, the car-call product exists abroad (iSchoolRide). P4-71 Clean Cabin added and scored on the same rubric."],
 ["Impact correction","Round 1 scored classroom filtration on the school block as if it removed the gate load. It removes the classroom carry-over term only, so P3-25 to P3-30, P3-43, P3-44, P3-61, P3-62 are reset to Impact 2."],
 ["Tie rule","Equal scores: the higher Cure score, then the solution that cuts the source over one that protects the receptor, then the higher Impact score. Round 3 (03:30): P3-81 gate orchestration added after the bus majority was verified, same rubric, ranks first on cure at equal 79 because it covers both vehicle classes."],
 ["Instructor's families","User, feasibility, implementability, usability, market and business (Ashu Verma, 14 Sep). Our additions: impact, measurability, time to effect, novelty, cure, transfer."]]
sheet("Rubric",["filter","definition"],rub,[26,120])
funnel=[[p,PR[p][0],n[p],sum(1 for r in rows if r["problem"]==p and r["gates"]=="through"),next(r["solution"] for r in allp if r["problem"]==p),next(r["weighted score (max 90)"] for r in allp if r["problem"]==p)] for p in PR]
sheet("Funnel",["id","problem","solutions generated","through the gates","top solution","score"],funnel,[5,34,12,12,90,8])
sheet("Method",["step","what"],[["1","Five problems from the near-decomposability result (block 1 split into workers and vendors). Each has a need statement with its boundary."],
 ["2","Every solution is derived from a cited edge of its problem block (outputs/agrl130-graph), in four mechanism classes: cut the source, cut the path, cut receptor time or intake, change the decision. 'Every solution explored' means every internal edge is covered."],
 ["3","Four binary gates first, then the eleven scored filters on the survivors, weights stated in Rubric. Round 1 had eight and surfaced purifiers; novelty, cure and transfer were added and the school-block filtration impact corrected."],
 ["4","The same eight filters score the five problems once, with the option A exposure load as the Impact evidence."],
 ["5","Funnel: 332 generated, 232 through the gates, top five per problem, one pick. Round 4 (04:10): P4-71 Clean Cabin added after the pre-mortem of gate orchestration (outputs/agrl130 - Review - Pre-mortem), scored on the same rubric."]],[5,140])
wb.save("AGRL130 Week 3 Solutions and Filters.xlsx")
json.dump({p:[[r["rank in problem"],r["weighted score (max 90)"],r["round 1 score (max 65)"],r["class"],r["solution"]] for r in allp if r["problem"]==p][:8] for p in PR}, open("top.json","w"), indent=1)
print("through", len(allp), "of", len(rows)); print(funnel)
print("problem scores", {p:score(PSC[p],PX[p]) for p in PR})
for r in allp[:15]: print(r["rank overall"], r["weighted score (max 90)"], r["round 1 score (max 65)"], r["problem"], r["class"], r["solution"][:80])
