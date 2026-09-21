#!/usr/bin/env python3
"""Resolve every citation at Crossref and write refs.bib. Nothing enters the bibliography
that Crossref (or a fetched URL for grey sources) did not return this session."""
import json, re, sys, time, urllib.request, urllib.parse
UA = {"User-Agent": "agrl130-report/1 (mailto:karthikpvnambiar@gmail.com)"}
def get(url):
    for i in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception as e:
            err = e; time.sleep(2)
    print("FAIL", url, err, file=sys.stderr); return None
DOIS = {
 # domain
 "Adar2015": "10.1164/rccm.201410-1924OC", "Azarmi2016": "10.1016/j.atmosenv.2016.04.029", "AdamsRequia2017": "10.1016/j.atmosenv.2017.06.046",
 "Ryan2013": "10.1039/c3em00377a", "Kumar2020": "10.1016/j.scitotenv.2020.138360", "Yuan2020": "10.3390/ijerph17072433",
 "Seagram2019": "10.1177/0361198119825538", "Patel2016": "10.1016/j.scitotenv.2015.10.163", "Nahar2020": "10.1016/j.envpol.2020.115435",
 "AlHurini2024": "10.7759/cureus.74951", "Ferree2024": "10.1093/annweh/wxae062", "Klepeis2001": "10.1038/sj.jea.7500165",
 "Behrentz2005": "10.1080/10473289.2005.10464739", "Sabin2005": "10.1038/sj.jea.7500414", "Kinsey2007": "10.1021/es0625024",
 "Austin2019": "10.3386/w25641", "Gauderman2004": "10.1056/NEJMoa040610", "Gauderman2007": "10.1016/S0140-6736(07)60037-3",
 "Rivas2014": "10.1016/j.envint.2014.04.009", "Thompson2023": "10.1016/j.scitotenv.2022.160234", "Mendoza2022": "10.3390/atmos13050706",
 "Hochstetler2011": "10.1016/j.atmosenv.2010.12.018", "Arar2021": "10.3390/ijerph182212091", "Boniardi2021": "10.1016/j.envpol.2021.116530",
 "Jeong2018": "10.1016/j.scitotenv.2018.04.399", "ZhouLevy2007": "10.1186/1471-2458-7-89", "Karner2010": "10.1021/es100008x",
 "Matthaios2020": "10.1016/j.atmosenv.2020.117810", "Hudda2012": "10.1016/j.atmosenv.2012.05.021", "RichmondBryant2009": "10.1016/j.scitotenv.2009.01.046",
 "Badri2012": "10.4236/ojpm.2012.24071", "DualTracer2011": "10.3155/1047-3289.61.5.494", "EPARebate2023": "10.1038/s41893-023-01088-7",
 # method
 "AndoSimon1961": "10.2307/1909285", "Blondel2008": "10.1088/1742-5468/2008/10/P10008", "LeichtNewman2008": "10.1103/PhysRevLett.100.118703",
 "Traag2019": "10.1038/s41598-019-41695-z", "Clauset2004": "10.1103/PhysRevE.70.066111", "Newman2006": "10.1073/pnas.0601602103",
 "Corvalan1999": "10.1097/00001648-199909000-00036", "Ritchey2006": "10.1057/palgrave.jors.2602177", "Lahdelma1998": "10.1016/S0377-2217(97)00163-X",
 "LahdelmaSalminen2001": "10.1287/opre.49.3.444.11220", "Butler1997": "10.1016/S0377-2217(96)00307-4", "TervonenLahdelma2007": "10.1016/j.ejor.2005.12.037",
 "Mitchell1989": "10.1002/bdm.3960020103", "Ott1982": "10.1016/0160-4120(82)90104-0", "Duan1982": "10.1016/0160-4120(82)90041-1",
 "Jaccard1912": "10.1111/j.1469-8137.1912.tb05611.x", "BeltonStewart2002": "10.1007/978-1-4615-1495-4", "Triantaphyllou2000": "10.1007/978-1-4757-3157-6",
 "Zheng2018": "10.5194/amt-11-4823-2018", "Bennett2002": "10.1021/es0222770",
}
QUERIES = {
 "Simon1962": "Simon The Architecture of Complexity Proceedings of the American Philosophical Society 1962",
 "Chang2010": "Chang dust control unpaved roads surfactant polymer 2010 emission reduction",
 "Pueblo2009": "school bus retrofit crankcase filter diesel oxidation catalyst in-cabin hopanes PAH Pueblo Colorado Atmospheric Environment 2009",
 "EST2011": "in-cabin school bus retrofit tailpipe emissions no unequivocal decrease Environmental Science Technology 2011 45 6475",
 "Klein2007": "Klein Performing a Project Premortem Harvard Business Review 2007",
 "Meadows1999": "Meadows Leverage Points Places to Intervene in a System",
 "KeeneyRaiffa1976": "Keeney Raiffa Decisions with Multiple Objectives Preferences and Value Tradeoffs",
 "Holdgate1979": "Holdgate A Perspective of Environmental Pollution 1979",
 "Zwicky1969": "Zwicky Discovery Invention Research through the Morphological Approach",
 "Kumar2022": "Kumar parent-school initiative to assess and predict air quality around a heavily trafficked school",
}
out = {}
for k, d in DOIS.items():
    j = get("https://api.crossref.org/works/" + urllib.parse.quote(d))
    if j: out[k] = j["message"]; print("OK ", k, "|", j["message"].get("title", [""])[0][:90], "|", j["message"].get("container-title", [""])[:1], j["message"].get("issued", {}).get("date-parts", [[None]])[0][0])
for k, q in QUERIES.items():
    j = get("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(q))
    if j:
        for it in j["message"]["items"]:
            print("Q  ", k, "|", it.get("title", [""])[0][:90], "|", it.get("container-title", [""])[:1], it.get("issued", {}).get("date-parts", [[None]])[0][0], "|", it["DOI"])
        out["Q_" + k] = j["message"]["items"]
json.dump(out, open("data/crossref.json", "w"))
