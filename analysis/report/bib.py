#!/usr/bin/env python3
"""Build refs.bib from the Crossref records fetched by refs.py, plus the grey sources
(government releases, reports, product pages) with the URL each was read at."""
import json, re, html
d = json.load(open("data/crossref.json"))
PICK = {"Pueblo2009": 0, "EST2011": 0, "Klein2007": 0, "Meadows1999": 0, "Zwicky1969": 0, "KeeneyRaiffa1976": 0, "Kumar2022": 0}
recs = {k: v for k, v in d.items() if not k.startswith("Q_")}
for k, i in PICK.items(): recs[k] = d["Q_" + k][i]
def clean(t):
    t = html.unescape(re.sub(r"<[^>]+>", "", t)); t = re.sub(r"\s+", " ", t).strip()
    t = t.replace("\u2014", ": ").replace("\u2013", " to ")   # house rule: no dashes as punctuation
    return t.replace("&", r"\&").replace("%", r"\%")
def authors(m):
    out = []
    for a in m.get("author", []):
        if "family" in a:
            fam, giv = a["family"], a.get("given", "")
            if fam.isupper(): fam, giv = fam.title(), giv.title()
            out.append(f"{fam}, {giv}".strip(", "))
        elif "name" in a: out.append("{" + a["name"] + "}")
    return " and ".join(out)
L = []
for k, m in recs.items():
    yr = m.get("published-print", {}).get("date-parts", [[None]])[0][0] or m.get("issued", {}).get("date-parts", [[None]])[0][0]
    title = clean(m["title"][0]) if m.get("title") else ""
    cont = clean(m["container-title"][0]) if m.get("container-title") else ""
    typ = m.get("type", "")
    f = {"title": "{" + title + "}", "year": yr, "doi": m["DOI"]}
    au = authors(m)
    if au: f["author"] = au
    if typ in ("journal-article", "proceedings-article"):
        entry = "article"; f["journal"] = cont
        for a, b in (("volume", "volume"), ("issue", "number"), ("page", "pages")):
            if m.get(a): f[b] = m[a].replace("-", "--") if b == "pages" else m[a]
    elif typ in ("book", "monograph", "edited-book", "reference-book"):
        entry = "book"; f["publisher"] = clean(m.get("publisher", ""))
    elif typ == "book-chapter":
        entry = "incollection"; f["booktitle"] = cont; f["publisher"] = clean(m.get("publisher", ""))
        if m.get("page"): f["pages"] = m["page"].replace("-", "--")
    elif typ == "report":
        entry = "techreport"; f["institution"] = clean(m.get("publisher", ""))
    else:
        entry = "misc"; f["howpublished"] = cont or clean(m.get("publisher", ""))
    # hand fixes
    if k == "Austin2019": entry = "techreport"; f["institution"] = "National Bureau of Economic Research"; f["number"] = "Working Paper 25641"; f.pop("howpublished", None)
    if k == "Klein2007": f["note"] = "Reprinted from Harvard Business Review 85(9), 2007"
    if k == "Meadows1999": f["author"] = "Meadows, Donella H."; f["note"] = "First issued by the Sustainability Institute, 1999"
    if k == "AndoSimon1961": f["pages"] = "111--138"
    if k == "Jaccard1912": f["title"] = "{The distribution of the flora in the alpine zone}"
    if k == "Corvalan1999": f["title"] = "{Health, environment and sustainable development: identifying links and indicators to promote action}"
    if k == "BeltonStewart2002": f["author"] = "Belton, Valerie and Stewart, Theodor J."; f["publisher"] = "Springer"
    if k == "Triantaphyllou2000": f["author"] = "Triantaphyllou, Evangelos"; f["publisher"] = "Springer"
    L.append("@%s{%s,\n%s\n}" % (entry, k, ",\n".join(f"  {a} = {{{b}}}" if a != "year" else f"  {a} = {b}" for a, b in f.items())))
GREY = r"""
@misc{Simon1962, author = {Simon, Herbert A.}, title = {{The architecture of complexity}}, howpublished = {Proceedings of the American Philosophical Society 106(6), 467--482}, year = 1962, note = {Read from cs.brandeis.edu/~cs146a/handouts/papers/simon-complexity.pdf on 20 September 2026}}
@misc{DuguePerez2015, author = {Dugu{\'e}, Nicolas and Perez, Anthony}, title = {{Directed Louvain: maximizing modularity in directed networks}}, howpublished = {Research report hal-01231784, Universit{\'e} d'Orl{\'e}ans}, year = 2015, note = {The directed modularity gain implemented by networkx, resolved 20 September 2026}}
@misc{IEC60812, author = {{International Electrotechnical Commission}}, title = {{IEC 60812:2018} Failure modes and effects analysis ({FMEA} and {FMECA})}, howpublished = {International standard, third edition}, year = 2018}
@misc{ADM2024buses, author = {{Abu Dhabi Mobility}}, title = {{Abu Dhabi Mobility completes its preparations for the school transport sector}}, howpublished = {News release, 25 August 2024, \url{https://admobility.gov.ae/en/news/abu-dhabi-mobility-completes-its-preparations-for-the-school-transport-sector}}, year = 2024, note = {Read 21 September 2026}}
@misc{ADM2024moto, author = {{Abu Dhabi Mobility}}, title = {{The Integrated Transport Centre (Abu Dhabi Mobility) has introduced a new category of commercial motorcycle license plates in Abu Dhabi}}, howpublished = {News release, 27 December 2024, \url{https://admobility.gov.ae/en/news/motorcycle-license}}, year = 2024, note = {Read 21 September 2026}}
@misc{SCAD2025pop, author = {{Statistics Centre Abu Dhabi}}, title = {{Abu Dhabi population in 2024 grows 7.5\% to reach 4.14m}}, howpublished = {Release of 30 June 2025, \url{https://scad.gov.ae/web/guest/w/abu-dhabi-population-in-2024-grows-7-5-to-reach-4-14m}}, year = 2025}
@misc{SCAD2024labour, author = {{Statistics Centre Abu Dhabi}}, title = {{Abu Dhabi Census, labour force 2024}}, howpublished = {\url{https://census.scad.gov.ae/home/labourforce?tab=info&lang=en}}, year = 2024}
@misc{SCAD2020yearbook, author = {{Statistics Centre Abu Dhabi}}, title = {{Statistical Yearbook of Abu Dhabi 2020}}, howpublished = {\url{https://www.scad.gov.ae/web/guest/w/statistical-yearbook-of-abu-dhabi-2020-1}}, year = 2020, note = {Table 5.2.5}}
@misc{SCAD2024air, author = {{Statistics Centre Abu Dhabi}}, title = {{Air Quality Statistics 2024}}, howpublished = {\url{https://www.scad.gov.ae/w/air-quality-statistics-annually-2024}}, year = 2025, note = {Environment Agency Abu Dhabi monitoring data}}}
@misc{ADCCI2024, author = {{Abu Dhabi Chamber of Commerce and Industry}}, title = {{Abu Dhabi Education Data, March 2024}}, howpublished = {Statistical report, \url{https://abudhabichamber.ae/-/media/Project/ADCCIV2/ADCCI/Media-Center---Publications/2024/AD-Education-Data-Statistical-Report-March-2024.pdf}}, year = 2024}
@misc{HEI2022uae, author = {{Health Effects Institute}}, title = {{State of Global Air, country report: United Arab Emirates}}, howpublished = {\url{https://cdn.zevross.com/hei/country-reports/v1/templates/United\%20Arab\%20Emirates.html}}, year = 2022, note = {Population-weighted PM2.5 44 \si{\micro\gram\per\cubic\metre} in 2019}}
@misc{Rowan2008, author = {Martinez-Morett, David and Hesketh, Robert P. and Marchese, Anthony and Bhatia, Krishan}, title = {{In-cabin particulate matter quantification and reduction strategies}}, howpublished = {Final report to the New Jersey Department of Environmental Protection, Rowan University, 4 August 2008, \url{https://dep.nj.gov/wp-content/uploads/stopthesoot/pdf/mdrp/final-report-school-bus.pdf}}, year = 2008}
@misc{AFDC2015, author = {{Alternative Fuels Data Center, US Department of Energy}}, title = {{Idle reduction for heavy-duty trucks}}, howpublished = {Fact sheet, \url{https://afdc.energy.gov/files/u/publication/hdv_idling_2015.pdf}}, year = 2015}
@misc{KT2025adek, author = {{Khaleej Times}}, title = {{New transport policy in Abu Dhabi schools: no child under 15 can walk home alone}}, howpublished = {23 September 2025, \url{https://www.khaleejtimes.com/uae/transport/new-transport-policy-in-abu-dhabi-for-schools}}, year = 2025}
@misc{E247pickup, author = {{Emirates 24|7}}, title = {{UAE} school pickup chaos: why afternoon congestion is worse than mornings, and what parents can do}, howpublished = {15 September 2026, \url{https://www.emirates247.com/uae/uae-school-pickup-chaos-why-afternoon-congestion-is-worse-than-mornings-and-what-parents-can-do/5637}}, year = 2026}
@misc{iSchoolRide, author = {{iSchoolRide}}, title = {{PickupLine}: how {iSchoolRide} works}, howpublished = {\url{https://www.ischoolride.com/How-iSchoolRide-Works}}, year = 2026, note = {Read 21 September 2026}}
@misc{London2021, author = {{Mayor of London}}, title = {{School Streets air quality study}}, howpublished = {\url{https://www.london.gov.uk/WHAT-WE-DO/environment/environment-publications/school-streets-air-quality-study}}, year = 2021}
"""
open("refs.bib", "w").write("\n\n".join(L) + "\n" + GREY)
print(len(L), "crossref entries +", GREY.count("@misc"), "grey")
