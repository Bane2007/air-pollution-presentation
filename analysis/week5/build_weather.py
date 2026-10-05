"""Writes data/weather.json from the TMYx 2011 to 2025 files for Abu Dhabi and Dubai
International (climate.onebuilding.org), and checks the week 5 report's Table 2.

Per hour: dry bulb and dew point in tenths of a degree, station pressure in Pa.
The site recomputes the moisture load in the browser with the same psychrometrics."""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'data', 'weather.json')
SITES = {
    'abu-dhabi': ('Abu Dhabi International', 'ARE_AZ_Abu.Dhabi.Intl.AP.412170_TMYx.2011-2025.epw'),
    'dubai': ('Dubai International', 'ARE_DU_Dubai.Intl.AP.411940_TMYx.2011-2025.epw'),
}


def psat(t):  # Pa over water, Hyland and Wexler as in the ASHRAE Handbook
    T = t + 273.15
    return math.exp(-5.8002206e3 / T + 1.3914993 - 4.8640239e-2 * T + 4.1764768e-5 * T * T
                    - 1.4452093e-8 * T ** 3 + 6.5459673 * math.log(T))


def w_dp(td, p):
    e = psat(td)
    return 0.621945 * e / (p - e)


def load(name):
    rows = []
    with open(os.path.join(HERE, 'epw', name)) as f:
        for i, line in enumerate(f):
            if i < 8:
                continue
            c = line.split(',')
            rows.append((float(c[6]), float(c[7]), float(c[9])))
    assert len(rows) == 8760, len(rows)
    return rows


def water(rows, target, flow=1000.0):  # kg a year for `flow` m3/h of outside air
    tot = 0.0
    for db, dp, p in rows:
        w, wt = w_dp(dp, p), w_dp(target, p)
        if w > wt:
            v = 287.042 * (db + 273.15) * (1 + 1.607858 * w) / p
            tot += flow / v * (w - wt)
    return tot


out = {}
for key, (label, fname) in SITES.items():
    rows = load(fname)
    out[key] = {
        'name': label,
        'db': [round(r[0] * 10) for r in rows],
        'dp': [round(r[1] * 10) for r in rows],
        'p': [round(r[2]) for r in rows],
    }
    print(label, 'dew point above 15 C:', sum(r[1] > 15 for r in rows), 'h,',
          '15 C:', round(water(rows, 15)), 'kg/yr,', '10 C:', round(water(rows, 10)), 'kg/yr')

with open(OUT, 'w') as f:
    json.dump(out, f, separators=(',', ':'))
print('wrote', os.path.relpath(OUT), os.path.getsize(OUT) // 1024, 'KB')
# report Table 2: Abu Dhabi 32,286 and 55,038, Dubai 41,346 and 66,139 kg/yr
