# Pearl of the Orient 東方之珠 — Hong Kong Tycoon 1970–2025

A turn-based strategy game: start in 1970 Hong Kong and build a property, finance and gambling empire
through 55 years of real history — typhoons, the 1973 crash, the 1983 peg, the handover, the Asian
Financial Crisis, SARS and more.

**Play:** open `hk-tycoon.html` in a browser. It is a single self-contained file.

## Real data

| Series | Source |
|---|---|
| District populations 1981–2021 | Census & Statistics Department censuses and by-censuses (1971 estimated) |
| District boundaries (map) | 2021 Population Census district boundaries, CSDI portal |
| Property prices and rents | Rating & Valuation Department price index (1980–2025) and regional average prices/rents (1986–2025) |
| Hang Seng Index | Year-end closes 1970–2025 |
| Interest rates | HKMA best lending rate (1971–2025) |
| Inflation | C&SD consumer price index (1975–2025) |

Estimated values are marked in the game's Sources screen. People, rival tycoons and Miss Hong Kong
winners are fictional.

## Rebuilding the data

Run from the project folder (Python with `xlrd` and `shapely`; Node for the simulator):

```
python tools/build_pop.py    # district populations -> hk-district-population.csv
python tools/build_mkt.py    # market series        -> hk-market-data.csv
python tools/build_map.py    # district outlines, embedded into hk-tycoon.html
node tools/sim.js 5          # headless balance simulator (bot strategies)
```

Raw downloads are in `data/raw/`.
