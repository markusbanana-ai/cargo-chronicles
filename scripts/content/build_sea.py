"""Writes docs/data/sea.json for the shipping route map.

Routes follow Baltic Exchange route definitions where one exists (TD3C, C5 ...), checked
against the Baltic Exchange weekly report (via DCN, 20 March 2026). Chokepoint volumes are
from EIA, World Oil Transit Chokepoints (June 2024, 2023 data). Waypoints are hand-placed
along the usual sea lanes; distances are great-circle sums, so they are approximate.
"""
import json, math, sys
from pathlib import Path

# ------------------------------------------------------------------ waypoints (lon, lat)
P = dict(
    # Gulf and Indian Ocean
    RAS_TANURA=(50.2, 26.7), RAS_LAFFAN=(51.6, 25.95), PG1=(51.6, 27.0), PG2=(54.0, 26.5),
    HORMUZ=(56.45, 26.5), GOO=(57.8, 25.1), ARAB=(61.5, 21.5), ARAB2=(70.0, 12.0), DONDRA=(80.8, 5.3),
    FUJAIRAH=(56.6, 25.1), YANBU=(38.0, 24.0),
    MAL_W=(95.0, 6.4), MAL1=(98.3, 4.7), MAL2=(100.9, 2.6), SING=(103.8, 1.15), SING_E=(104.6, 1.4),
    SCS1=(106.5, 4.5), SCS2=(109.5, 10.0), SCS3=(113.0, 16.0), SCS4=(116.5, 20.3),
    TS1=(118.9, 23.1), TS2=(120.5, 25.6), ECS=(122.4, 28.0), NINGBO=(122.2, 29.85), SHANGHAI=(122.15, 30.6),
    LUZON=(121.2, 20.6), RYUKYU=(124.8, 25.2), JP1=(130.5, 30.6), JP2=(136.5, 33.0), JP3=(139.5, 34.6), TOKYO=(139.85, 35.35),
    YS1=(123.4, 33.3), YS2=(121.6, 35.4), QINGDAO=(120.4, 36.0),
    # Red Sea and Suez
    ADEN_E=(54.5, 13.6), ADEN=(48.0, 12.4), BAB=(43.35, 12.65), RS1=(41.6, 14.9), RS2=(38.9, 19.4), RS3=(36.6, 23.4),
    RS4=(34.4, 27.2), GOS=(33.0, 28.9), SUEZ=(32.55, 29.95), PORT_SAID=(32.35, 31.4),
    MED1=(26.0, 33.9), MED2=(19.0, 35.3), SICILY=(11.7, 37.25), MED3=(7.0, 37.7), MED4=(1.0, 36.8),
    TYR1=(12.5, 39.0), TYR2=(10.6, 42.2), GENOA=(8.9, 44.35),
    GIB=(-5.6, 35.95), STV=(-9.6, 36.9), FIN=(-10.0, 43.3), USH=(-6.0, 48.6), CH1=(-2.0, 50.0), DOVER=(1.45, 51.0),
    RTM_OFF=(3.6, 51.97), ROTTERDAM=(4.05, 51.98),
    # Cape route
    IND1=(85.0, -2.0), IND2=(72.0, -18.0), IND3=(52.0, -31.0), AGUL=(20.0, -35.4), CGH=(17.6, -34.4), SATL1=(13.0, -28.0),
    SATL2=(4.0, -14.0), SATL3=(-8.0, -2.0), NATL1=(-19.0, 12.0), NATL2=(-19.5, 26.5), NATL3=(-13.5, 37.5),
    MADA_E=(52.5, -14.0), MADA_S=(48.5, -28.5),
    # Atlantic and Gulf of Mexico
    HOUSTON=(-94.7, 29.3), SABINE=(-93.85, 29.65), NOLA=(-89.4, 28.9), GOM=(-90.0, 26.6), FS1=(-83.6, 24.0), FS2=(-80.6, 24.25),
    FS3=(-79.75, 25.6), FS4=(-79.5, 27.8), ATL1=(-76.0, 32.0), ATL2=(-60.0, 40.5), ATL3=(-35.0, 46.2), ATL4=(-15.0, 48.8),
    NY=(-73.95, 40.45), NYO=(-72.0, 39.8), HAT=(-74.6, 35.0), SE_US=(-79.0, 31.0),
    YUC=(-85.8, 21.6), CARIB1=(-84.0, 17.5), CARIB2=(-81.0, 12.5), COLON=(-79.92, 9.42), BALBOA=(-79.55, 8.85),
    PAN_P=(-79.6, 7.2), PAC0=(-86.0, 9.5), PAC1=(-100.0, 15.0), PAC2=(-120.0, 23.0), PAC3=(-145.0, 31.0), PAC4=(-170.0, 33.5),
    PAC5=(165.0, 34.0), PAC6=(147.0, 34.0),
    WIND1=(-75.8, 15.5), WIND=(-73.9, 20.0), BAHAMA=(-72.6, 22.6), ATLW=(-72.5, 31.0),
    LA=(-118.3, 33.65), TP1=(128.5, 30.4), TP2=(134.0, 32.0), TP3=(150.0, 38.0), TP4=(180.0, 42.5), TP5=(-150.0, 41.0), TP6=(-128.0, 36.0),
    CP0=(125.0, 29.0), CP1=(140.0, 26.0), CP2=(165.0, 22.0), CP3=(-165.0, 18.0), CP4=(-135.0, 13.0), CP5=(-105.0, 9.5),
    # South Atlantic / Brazil / West Africa
    TUBARAO=(-40.25, -20.3), SANTOS=(-46.3, -24.05), BR1=(-36.0, -25.0), BR2=(-12.0, -33.0), BR3=(8.0, -36.0),
    BONNY=(7.0, 4.15), WAF1=(4.5, 1.0), WAF2=(-8.0, 3.8), WAF3=(-17.5, 10.0),
    # Indonesia / Australia
    LOMBOK_S=(115.75, -9.6), LOMBOK=(115.72, -8.45), MAK1=(117.9, -4.3), MAK2=(118.7, 0.0), CEL1=(120.5, 3.2), CEL2=(124.2, 4.6),
    MOLU=(125.9, 4.6), PHS1=(127.3, 6.8), PHS2=(126.6, 13.0), PHS3=(124.3, 20.5), ECS2=(123.7, 27.0),
    HEDLAND=(118.6, -20.2), WA1=(117.5, -15.5), GLAD=(151.35, -23.8), AUS1=(153.6, -22.8), AUS2=(157.5, -18.0),
    SOL=(164.0, -12.0), SOL2=(165.0, -4.0), MIC=(155.0, 6.0), MIC2=(146.0, 18.0), JPS=(141.0, 30.0),
    SAMARINDA=(117.4, -0.9), JAVA1=(114.0, -4.5), KARIM=(108.5, -2.5), BANGKA=(106.0, -1.2), KRISHNA=(80.3, 14.25), BAY=(86.0, 9.0),
    # North Sea and Norway
    HOUND=(-3.37, 56.0), FORTH=(-2.2, 56.1), NS1=(2.0, 55.3), NS2=(7.0, 54.0), JADE=(7.9, 53.85), WHV=(8.12, 53.55),
    MONGSTAD=(5.02, 60.81), FEDJE=(4.55, 60.72), NOR1=(3.9, 59.8), NOR2=(3.2, 57.5), NS3=(3.0, 54.5), NS4=(3.3, 52.6),
    HAMMERFEST=(23.62, 70.68), HF1=(22.5, 71.2), HF2=(16.5, 70.4), HF3=(11.0, 68.0), HF4=(7.0, 64.5), HF5=(4.0, 61.5),
)
for k, v in P.items():
    assert -180 <= v[0] <= 180 and -90 <= v[1] <= 90, k

def path(*names):
    return [list(P[n]) for n in names]

def nm(pts):
    R = 3440.065
    tot = 0.0
    for (lo1, la1), (lo2, la2) in zip(pts, pts[1:]):
        p1, p2 = math.radians(la1), math.radians(la2)
        dl = math.radians(lo2 - lo1)
        a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        tot += 2 * R * math.asin(math.sqrt(a))
    return round(tot)

# shared legs
GULF_OUT = ["PG1", "PG2", "HORMUZ", "GOO"]
GULF_TO_MALACCA = GULF_OUT + ["ARAB", "ARAB2", "DONDRA", "MAL_W", "MAL1", "MAL2", "SING", "SING_E"]
SCS_TO_TAIWAN = ["SCS1", "SCS2", "SCS3", "SCS4", "TS1", "TS2", "ECS"]
SCS_TO_JAPAN = ["SCS1", "SCS2", "SCS3", "SCS4", "LUZON", "RYUKYU", "JP1", "JP2", "JP3", "TOKYO"]
CHINA_SOUTH = ["ECS", "TS2", "TS1", "SCS4", "SCS3", "SCS2", "SCS1", "SING_E", "SING", "MAL2", "MAL1", "MAL_W", "DONDRA"]
SUEZ_NORTH = ["ADEN_E", "ADEN", "BAB", "RS1", "RS2", "RS3", "RS4", "GOS", "SUEZ", "PORT_SAID", "MED1", "MED2", "SICILY"]
MED_TO_RTM = ["MED3", "MED4", "GIB", "STV", "FIN", "USH", "CH1", "DOVER", "RTM_OFF", "ROTTERDAM"]
CAPE_FROM_ASIA = ["IND2", "IND3", "AGUL", "CGH", "SATL1", "SATL2", "SATL3", "NATL1", "NATL2", "NATL3", "FIN", "USH", "CH1", "DOVER", "RTM_OFF", "ROTTERDAM"]
EUR_FROM_WAF = ["WAF1", "WAF2", "WAF3", "NATL1", "NATL2", "NATL3", "FIN", "USH", "CH1", "DOVER", "RTM_OFF", "ROTTERDAM"]
USG_TO_EUR = ["GOM", "FS1", "FS2", "FS3", "FS4", "ATL1", "ATL2", "ATL3", "ATL4", "USH", "CH1", "DOVER", "RTM_OFF", "ROTTERDAM"]
USG_TO_PANAMA = ["GOM", "YUC", "CARIB1", "CARIB2", "COLON", "BALBOA", "PAN_P"]
PAN_TO_JAPAN = ["PAC0", "PAC1", "PAC2", "PAC3", "PAC4", "PAC5", "PAC6", "JP3", "TOKYO"]
INDO_TO_CHINA = ["LOMBOK_S", "LOMBOK", "MAK1", "MAK2", "CEL1", "CEL2", "MOLU", "PHS1", "PHS2", "PHS3", "ECS2", "YS1", "YS2", "QINGDAO"]
ATL_TO_CAPE = ["BR1", "BR2", "BR3", "AGUL"]

# ------------------------------------------------------------------ chokepoints
CHOKE = [
    dict(id="hormuz", name="Strait of Hormuz", at=P["HORMUZ"], kw=["hormuz", "persian gulf", "arabian gulf", "gulf of oman", "iran"],
         flow="20.9 million barrels of oil a day in 2023: more than a quarter of seaborne oil trade and about a fifth of world oil consumption (EIA). Most goes to Asia. Qatar's LNG exports also pass here.",
         note="The only sea exit from the Persian Gulf. Deep and wide enough for the largest tankers, with separate inbound and outbound lanes.",
         bypass="No sea detour. Saudi Arabia's East–West pipeline to Yanbu on the Red Sea (5 million b/d) and the UAE pipeline to Fujairah (1.5 million b/d) can carry part of the oil; EIA estimated about 2.6 million b/d of spare pipeline capacity.",
         insurance="A Joint War Committee listed area. In March 2026 (JWLA-033) London insurers extended the listed areas to Bahrain, Djibouti, Kuwait, Oman and Qatar. In July 2026, war-risk quotes for a Hormuz transit were reported at 2–6% of hull value (Insurance Business, citing Marsh).",
         closable=True, alt_kind="pipeline"),
    dict(id="bab-el-mandeb", name="Bab el-Mandeb", at=P["BAB"], kw=["bab el-mandeb", "bab-el-mandeb", "red sea", "houthi*", "gulf of aden", "yemen*"],
         flow="8.6 million barrels of oil a day in 2023 (EIA). Together with Suez and the SUMED pipeline, about 11% of seaborne oil trade, plus most Asia–Europe container trade.",
         note="The southern gate of the Red Sea, between Yemen and Djibouti. Houthi attacks on ships from late 2023 made most container lines and many tankers sail around Africa instead.",
         bypass="Around the Cape of Good Hope. For Asia–North Europe this adds roughly 3,000–3,500 nautical miles and 10–14 days.",
         insurance="Part of the Joint War Committee listed areas (southern Red Sea and Gulf of Aden), so every transit needs an additional war-risk premium, and some owners and crews refuse it.",
         closable=True, alt_kind="cape"),
    dict(id="suez", name="Suez Canal", at=P["SUEZ"], kw=["suez*", "sumed", "port said"],
         flow="8.8 million barrels of oil a day in 2023 including the SUMED pipeline (EIA). Asia–Europe container and car-carrier trade depends on it.",
         note="A sea-level canal without locks, about 190 km long. The canal authority charges transit dues based on the ship's Suez Canal tonnage; 'Suezmax' is the largest tanker that can pass fully laden.",
         bypass="The SUMED pipeline (2.5 million b/d) carries crude from the Red Sea to the Mediterranean. Otherwise around the Cape of Good Hope.",
         insurance="Groundings and blockages here are hull and P&I events; the 2021 Ever Given grounding blocked the canal for six days and led to a large general average and salvage claim.",
         closable=True, alt_kind="cape"),
    dict(id="malacca", name="Strait of Malacca", at=P["MAL2"], kw=["malacca", "singapore strait"],
         flow="23.7 million barrels of oil a day in 2023, the largest oil chokepoint (EIA), plus most trade between Europe, the Gulf and East Asia.",
         note="Narrow and shallow in the Singapore Strait, with heavy traffic. 'Malaccamax' is the largest ship that can pass; the deepest-loaded ships use the deeper Lombok and Makassar straits instead.",
         bypass="Through Indonesia via the Lombok or Sunda straits, which adds distance. A Myanmar–China pipeline carries a small volume of oil.",
         insurance="High traffic density makes collision and grounding the main risks; piracy incidents are mostly petty theft at anchor.",
         closable=True, alt_kind="lombok"),
    dict(id="panama", name="Panama Canal", at=P["COLON"], kw=["panama*", "gatun", "neopanamax"],
         flow="2.1 million barrels of oil a day in the year to September 2023, about 3% of seaborne oil (EIA), plus large volumes of US grain, LPG and LNG to Asia and container traffic to the US East Coast.",
         note="Lock canal fed by fresh water from Gatun Lake. Drought in 2023–24 forced draft limits and fewer transits. The Neopanamax locks (2016) take far bigger ships than the old 'Panamax' size.",
         bypass="Via the Suez Canal or the Cape of Good Hope, or around South America; the detours can add thousands of miles. A trans-Panama pipeline carries some crude.",
         insurance="Delays mean demurrage and lost time rather than physical damage; who pays depends on the charter party.",
         closable=True, alt_kind="cape"),
    dict(id="bosporus", name="Turkish Straits", at=(29.05, 41.1), kw=["bosporus", "bosphorus", "dardanelles", "turkish strait*", "black sea"],
         flow="3.4 million barrels of oil a day in 2023, slightly more than half crude (EIA), plus grain from Ukraine and Russia.",
         note="The only sea link between the Black Sea and the Mediterranean. The Bosporus is less than half a nautical mile wide at its narrowest; Türkiye controls traffic under the Montreux Convention.",
         bypass="No sea alternative for Black Sea ports. The Baku–Tbilisi–Ceyhan pipeline carries Caspian crude around it.",
         insurance="Black Sea calls carry war-risk premiums because of attacks on ships and ports in the war in Ukraine.",
         closable=True, alt_kind="none"),
    dict(id="danish", name="Danish Straits", at=(11.0, 55.4), kw=["danish strait*", "great belt", "øresund", "baltic sea", "skagerrak", "kattegat"],
         flow="4.9 million barrels of oil a day in 2023, mostly Russian exports from Baltic ports (EIA).",
         note="The Great Belt, Little Belt and Øresund connect the Baltic with the North Sea. The deepest route limits draught, so the largest tankers cannot load fully in the Baltic. Many shadow-fleet tankers pass here, close to Norway.",
         bypass="The Kiel Canal for small ships only.",
         insurance="Coastal states check insurance documents of tankers passing, a response to uninsured shadow-fleet ships.",
         closable=False),
    dict(id="cape", name="Cape of Good Hope", at=P["CGH"], kw=["cape of good hope", "around africa", "cape route", "rerout*"],
         flow="About 6 million barrels of oil a day in 2023, about 8% of seaborne oil (EIA), and the main detour when the Red Sea is avoided.",
         note="Not a chokepoint but the alternative route between the Atlantic and Indian oceans, with rough winter weather. Capesize bulk carriers and VLCCs too big for Suez sail here anyway.",
         bypass="This is the bypass. EIA estimates that closing Suez and SUMED adds about 15 days from the Arabian Sea to Europe.",
         insurance="Heavy-weather damage to ships and cargo is a classic hull and cargo claim on this route.",
         closable=False),
    dict(id="gibraltar", name="Strait of Gibraltar", at=P["GIB"], kw=["gibraltar", "strait of gibraltar"],
         flow="The Mediterranean's link to the Atlantic, used by all Suez traffic heading to northern Europe and the Americas.",
         note="About 14 km wide at the narrowest point, with a traffic separation scheme.",
         bypass="None needed in practice.", insurance="", closable=False),
    dict(id="dover", name="Dover Strait", at=P["DOVER"], kw=["english channel", "dover strait"],
         flow="One of the busiest shipping lanes in the world, leading to Rotterdam, Antwerp and Hamburg.",
         note="Ships follow a traffic separation scheme. Ferries crossing the lanes make collision risk a constant issue.",
         bypass="North of Scotland, much longer.", insurance="", closable=False),
    dict(id="lombok", name="Lombok Strait", at=P["LOMBOK"], kw=["lombok", "makassar"],
         flow="The deep-water alternative to Malacca for the largest bulk carriers and tankers between Australia, Brazil and China.",
         note="Deep enough for fully laden VLOCs and VLCCs. Iron ore from Brazil and Western Australia often passes here.",
         bypass="Malacca or Sunda for smaller ships.", insurance="", closable=False),
]

# ------------------------------------------------------------------ routes
R = []
def route(**k):
    k["pts"] = path(*k.pop("legs"))
    k["nm"] = nm(k["pts"])
    alts = {}
    for cid, a in (k.get("alts") or {}).items():
        pts = path(*a["legs"])
        alts[cid] = {"pts": pts, "nm": nm(pts), "note": a["note"]}
    if alts:
        k["alts"] = alts
    for leg in k.get("legs_extra", []):
        leg["pts"] = path(*leg.pop("legs"))
        leg["nm"] = nm(leg["pts"])
    R.append(k)

TANKER_QUOTE = "Worldscale points (WS), a percentage of a published flat rate in USD per tonne for each route. Brokers convert WS to time-charter equivalent (TCE, USD per day) to compare routes."

route(id="td3c", code="TD3C", market="crude", name="Middle East Gulf → China", ship="VLCC", size="270,000 t crude (about 2 million barrels)",
      frm="Ras Tanura, Saudi Arabia", to="Ningbo, China", speed=13, ballast=12.5, port_days=5, quote=TANKER_QUOTE,
      legs=["RAS_TANURA"] + GULF_TO_MALACCA + SCS_TO_TAIWAN + ["NINGBO"], via=["hormuz", "malacca"],
      alts={"hormuz": {"legs": ["YANBU", "RS3", "RS2", "RS1", "BAB", "ADEN", "ADEN_E", "ARAB2", "DONDRA", "MAL_W", "MAL1", "MAL2", "SING", "SING_E"] + SCS_TO_TAIWAN + ["NINGBO"],
                       "note": "Only part of the oil can reach Yanbu on the Red Sea by pipeline; from there the voyage passes Bab el-Mandeb instead of Hormuz."},
            "malacca": {"legs": ["RAS_TANURA"] + GULF_OUT + ["ARAB", "ARAB2", "DONDRA", "IND1", "LOMBOK_S", "LOMBOK", "MAK1", "MAK2", "CEL1", "CEL2", "MOLU", "PHS1", "PHS2", "PHS3", "ECS2", "ECS", "NINGBO"],
                        "note": "Via Lombok and Makassar instead of Malacca."}},
      moves=["Middle East export volumes and OPEC+ decisions", "Chinese crude imports and stockbuilding", "Tension around Hormuz (risk premium and war-risk insurance)", "Ships returning from long-haul Atlantic trades"],
      course="The benchmark route for VLCC earnings and therefore for VLCC values in sale and purchase. Lenders compare TD3C TCE with the ship's cash breakeven. A transit of Hormuz requires additional war-risk cover, and a VLCC's P&I club stands behind any oil pollution claim.",
      voyage=dict(cargo=270000, freight=16, cons=62),
      kw=["vlcc*", "td3c", "middle east gulf"])
route(id="td15", code="TD15", market="crude", name="West Africa → China", ship="VLCC", size="260,000 t crude",
      frm="Bonny, Nigeria", to="Ningbo, China", speed=13, ballast=12.5, port_days=5, quote=TANKER_QUOTE,
      legs=["BONNY", "SATL2", "SATL1", "CGH", "AGUL", "IND3", "MAL_W", "MAL1", "MAL2", "SING", "SING_E"] + SCS_TO_TAIWAN + ["NINGBO"], via=["cape", "malacca"],
      moves=["Nigerian and Angolan export volumes", "Chinese demand for light sweet crude", "Competition from US and Brazilian barrels"],
      course="A long-haul route: about twice the distance of TD3C, so each cargo ties up a VLCC for much longer. More long-haul cargoes mean more ton-miles and tighter VLCC supply.",
      voyage=dict(cargo=260000, freight=22, cons=62),
      kw=["west africa*", "nigeria*", "angola*", "td15"])
route(id="td22", code="TD22", market="crude", name="US Gulf → China", ship="VLCC", size="270,000 t crude",
      frm="Houston area (US Gulf)", to="Ningbo, China", speed=13, ballast=12.5, port_days=6, quote="Lump sum in USD for the whole voyage, converted to TCE.",
      legs=["HOUSTON", "GOM", "FS1", "FS2", "FS3", "FS4", "SATL3", "SATL2", "SATL1", "CGH", "AGUL", "IND3", "MAL_W", "MAL1", "MAL2", "SING", "SING_E"] + SCS_TO_TAIWAN + ["NINGBO"], via=["cape", "malacca"],
      moves=["The price spread between US WTI and Middle East crude", "Chinese trade policy towards US oil", "US export terminal capacity (VLCCs often load by lightering offshore)"],
      course="One of the longest crude voyages: a classic ton-mile story. When US crude flows to Asia, VLCC demand rises far more than the export volume alone suggests.",
      voyage=dict(cargo=270000, freight=30, cons=62),
      kw=["us crude exports", "us gulf", "td22", "wti"])
route(id="td20", code="TD20", market="crude", name="West Africa → UK-Continent", ship="Suezmax", size="130,000 t crude",
      frm="Bonny, Nigeria", to="Rotterdam", speed=13, ballast=12.5, port_days=4, quote=TANKER_QUOTE,
      legs=["BONNY"] + EUR_FROM_WAF, via=["dover"],
      moves=["European refinery demand", "Nigerian output and outages", "Competition from US and Guyana crude (TD27)"],
      course="Suezmax earnings in the Atlantic basin. Shorter voyages mean less ton-mile demand per cargo than the long-haul routes to Asia.",
      voyage=dict(cargo=130000, freight=14, cons=48),
      kw=["suezmax*", "td20"])
route(id="td25", code="TD25", market="crude", name="US Gulf → UK-Continent", ship="Aframax", size="70,000 t crude",
      frm="Houston", to="Rotterdam", speed=13, ballast=12.5, port_days=4, quote=TANKER_QUOTE,
      legs=["HOUSTON"] + USG_TO_EUR, via=["dover"],
      moves=["US crude exports to Europe", "Hurricane season in the Gulf of Mexico", "The WTI–Brent price spread"],
      course="US crude replaced Russian barrels in Europe after sanctions, which made this a core Aframax trade.",
      voyage=dict(cargo=70000, freight=22, cons=40),
      kw=["aframax*", "td25"])
route(id="td7", code="TD7", market="crude", name="Cross North Sea", ship="Aframax", size="80,000 t crude",
      frm="Hound Point, UK", to="Wilhelmshaven, Germany", speed=13, ballast=12.5, port_days=3, quote=TANKER_QUOTE,
      legs=["HOUND", "FORTH", "NS1", "NS2", "JADE", "WHV"], via=[],
      moves=["North Sea production and field maintenance", "Winter weather delays", "Refinery demand in north-west Europe"],
      course="A short-haul route: port time and weather matter more than sea days. Norwegian and UK crude is priced and shipped on similar terms.",
      voyage=dict(cargo=80000, freight=7, cons=40),
      kw=["north sea", "td7", "hound point"])
route(id="mongstad", code="", market="crude", name="Mongstad → Rotterdam (Norwegian crude)", ship="Aframax / Suezmax", size="80,000–130,000 t crude",
      frm="Mongstad, near Bergen", to="Rotterdam", speed=13, ballast=12.5, port_days=3, quote="Similar to cross-North Sea routes (TD7): Worldscale points.",
      legs=["MONGSTAD", "FEDJE", "NOR1", "NOR2", "NS3", "NS4", "RTM_OFF", "ROTTERDAM"], via=[],
      moves=["Johan Sverdrup and other Norwegian field output", "European refinery demand", "Winter weather in the North Sea"],
      course="Your local export: much of Norway's crude, including Johan Sverdrup, is loaded at Mongstad near Bergen. Short voyages, so port time and weather drive the economics.",
      voyage=dict(cargo=100000, freight=7, cons=44),
      kw=["mongstad", "johan sverdrup", "equinor", "north sea crude"])

route(id="tc20", code="TC20", market="products", name="Middle East Gulf → UK-Continent", ship="LR2 product tanker", size="90,000 t clean products",
      frm="Ruwais/Jubail area", to="Rotterdam", speed=13, ballast=12.5, port_days=4, quote="Lump sum in USD, converted to TCE.",
      legs=["RAS_TANURA"] + GULF_OUT + ["ARAB", "ADEN_E"] + SUEZ_NORTH + MED_TO_RTM, via=["hormuz", "bab-el-mandeb", "suez", "gibraltar", "dover"],
      alts={"bab-el-mandeb": {"legs": ["RAS_TANURA"] + GULF_OUT + ["ARAB", "MADA_E", "MADA_S", "AGUL", "CGH", "SATL1", "SATL2", "SATL3", "NATL1", "NATL2", "NATL3", "FIN", "USH", "CH1", "DOVER", "RTM_OFF", "ROTTERDAM"],
                               "note": "Around the Cape of Good Hope instead of the Red Sea."},
            "suez": {"legs": ["RAS_TANURA"] + GULF_OUT + ["ARAB", "MADA_E", "MADA_S", "AGUL", "CGH", "SATL1", "SATL2", "SATL3", "NATL1", "NATL2", "NATL3", "FIN", "USH", "CH1", "DOVER", "RTM_OFF", "ROTTERDAM"],
                     "note": "Around the Cape of Good Hope instead of Suez."}},
      moves=["Europe's diesel and jet imports after it stopped buying Russian products", "New export refineries in the Middle East", "Red Sea routing"],
      course="Europe now imports more diesel and jet from the Middle East and India. Long voyages around Africa absorbed many LR2s and lifted clean tanker earnings.",
      voyage=dict(cargo=90000, freight=45, cons=42),
      kw=["lr2", "tc20", "clean tanker*", "diesel import*", "jet fuel"])
route(id="mr-triangle", code="TC2 + TC14", market="products", name="Atlantic triangulation (MR)", ship="MR product tanker", size="37,000–38,000 t clean products",
      frm="Rotterdam", to="New York, then US Gulf → Rotterdam", speed=13, ballast=12.5, port_days=8, quote="Worldscale points per leg; the basket is quoted as TCE.",
      legs=["ROTTERDAM", "RTM_OFF", "DOVER", "CH1", "USH", "ATL3", "ATL2", "NYO", "NY"], via=["dover"],
      legs_extra=[{"kind": "ballast", "label": "Short ballast to the US Gulf", "legs": ["NY", "NYO", "HAT", "SE_US", "FS4", "FS3", "FS2", "FS1", "GOM", "HOUSTON"]},
                  {"kind": "laden", "label": "TC14: US Gulf → UK-Continent", "legs": ["HOUSTON"] + USG_TO_EUR}],
      moves=["US East Coast gasoline imports", "European diesel imports from the US Gulf", "How short the ballast leg is between cargoes"],
      course="Triangulation cuts ballast: the ship carries gasoline west, sails a short way empty, then carries diesel east. Less ballast time per laden day lifts the round-trip TCE, which is why the Baltic publishes it as a basket.",
      voyage=dict(cargo=37000, freight=28, cons=24),
      kw=["mr tanker*", "tc2", "tc14", "product tanker*", "gasoline"])

route(id="c5", code="C5", market="drybulk", name="West Australia → China", ship="Capesize", size="170,000 t iron ore",
      frm="Port Hedland / Dampier", to="Qingdao, China", speed=12.5, ballast=12.5, port_days=5, quote="USD per tonne of cargo, converted to TCE. The C5TC index averages five Capesize time-charter routes.",
      legs=["HEDLAND", "WA1"] + INDO_TO_CHINA, via=["lombok"],
      moves=["Chinese steel production and iron ore stocks", "Australian export volumes (cyclones in season)", "The share of long-haul Brazilian ore"],
      course="The highest-volume Capesize route but a short one: a round trip takes about a month. Ore miners also own or charter their own ships, which matters for spot demand.",
      voyage=dict(cargo=170000, freight=10, cons=46),
      kw=["iron ore", "capesize*", "pilbara", "port hedland", "=C5"])
route(id="c3", code="C3", market="drybulk", name="Brazil → China", ship="Capesize", size="160,000 t iron ore",
      frm="Tubarão, Brazil", to="Qingdao, China", speed=12.5, ballast=12.5, port_days=6, quote="USD per tonne of cargo, converted to TCE.",
      legs=["TUBARAO"] + ATL_TO_CAPE + ["LOMBOK_S", "LOMBOK", "MAK1", "MAK2", "CEL1", "CEL2", "MOLU", "PHS1", "PHS2", "PHS3", "ECS2", "YS1", "YS2", "QINGDAO"], via=["cape", "lombok"],
      moves=["Vale's export volumes and the Brazilian rainy season", "Chinese steel demand", "Simandou (Guinea) ore, another long-haul source"],
      course="About three times the distance of C5 for each tonne. A shift of China's ore buying from Australia to Brazil raises Capesize ton-mile demand even if China imports the same tonnes.",
      voyage=dict(cargo=160000, freight=24, cons=46),
      kw=["iron ore", "vale", "tubarão", "tubarao", "capesize*"])
route(id="brazil-soy", code="", market="drybulk", name="Brazil soybeans → China", ship="Kamsarmax", size="about 66,000 t soybeans",
      frm="Santos, Brazil", to="Qingdao, China", speed=12.5, ballast=12.5, port_days=8, quote="USD per tonne; Panamax/Kamsarmax earnings are tracked as a time-charter average (P5TC).",
      legs=["SANTOS"] + ATL_TO_CAPE + ["LOMBOK_S", "LOMBOK", "MAK1", "MAK2", "CEL1", "CEL2", "MOLU", "PHS1", "PHS2", "PHS3", "ECS2", "YS1", "YS2", "QINGDAO"], via=["cape", "lombok"],
      moves=["The Brazilian harvest (peak shipments in spring)", "China's soybean demand for animal feed", "US–China trade policy (US soybeans are the alternative)"],
      course="A seasonal long-haul trade. Port congestion in Brazil during the harvest peak also removes ships from the market for weeks.",
      voyage=dict(cargo=66000, freight=40, cons=30),
      kw=["soybean*", "kamsarmax*", "brazilian grain"])
route(id="usg-grain", code="", market="drybulk", name="US Gulf grain → China via Panama", ship="Panamax / Kamsarmax", size="about 66,000 t grain",
      frm="Mississippi River mouth", to="Qingdao, China", speed=12.5, ballast=12.5, port_days=8, quote="USD per tonne.",
      legs=["NOLA", "GOM", "YUC", "CARIB1", "CARIB2", "COLON", "BALBOA", "PAN_P", "PAC0", "PAC1", "PAC2", "PAC3", "PAC4", "PAC5", "PAC6", "JP3", "JP2", "TP1", "YS1", "YS2", "QINGDAO"], via=["panama"],
      alts={"panama": {"legs": ["NOLA", "GOM", "FS1", "FS2", "FS3", "FS4", "SATL3", "SATL2", "SATL1", "CGH", "AGUL", "IND3", "MAL_W", "MAL1", "MAL2", "SING", "SING_E"] + SCS_TO_TAIWAN + ["YS1", "YS2", "QINGDAO"],
                       "note": "Around the Cape of Good Hope when Panama slots are short."}},
      moves=["The US harvest (peak in autumn)", "Mississippi river levels", "Panama Canal draft limits and slot auctions"],
      course="The clearest example of a canal decision: wait and pay for a Panama slot, or sail much further via the Cape. Who pays for waiting time depends on the charter party.",
      voyage=dict(cargo=66000, freight=50, cons=30),
      kw=["grain", "corn", "soybean*", "mississippi"])
route(id="indo-coal", code="", market="drybulk", name="Indonesia coal → India", ship="Supramax", size="about 55,000 t coal",
      frm="Samarinda, Kalimantan", to="Krishnapatnam, India", speed=12, ballast=12, port_days=7, quote="USD per tonne or time-charter trips.",
      legs=["SAMARINDA", "MAK1", "JAVA1", "KARIM", "BANGKA", "SING_E", "SING", "MAL2", "MAL1", "MAL_W", "BAY", "KRISHNA"], via=["malacca"],
      moves=["Indian power demand (heatwaves)", "Chinese coal import policy", "Indonesian export rules"],
      course="Short, flexible trips for geared Supramaxes that can load at anchor from barges. These ships switch between many cargoes, so rates move more slowly than Capesize.",
      voyage=dict(cargo=55000, freight=12, cons=26),
      kw=["coal", "supramax*"])

route(id="asia-europe", code="FBX11", market="container", name="China → North Europe", ship="Ultra-large container ship", size="about 20,000 TEU",
      frm="Shanghai", to="Rotterdam", speed=16, ballast=16, port_days=14, quote="USD per 40-foot container (FEU) on the spot market; most volume moves on annual contracts.",
      legs=["SHANGHAI", "ECS"] + CHINA_SOUTH[1:] + ["ADEN_E"] + SUEZ_NORTH + MED_TO_RTM, via=["malacca", "bab-el-mandeb", "suez", "gibraltar", "dover"],
      alts={"bab-el-mandeb": {"legs": ["SHANGHAI", "ECS"] + CHINA_SOUTH[1:-1] + CAPE_FROM_ASIA, "note": "Around the Cape of Good Hope, as most container lines have done since early 2024."},
            "suez": {"legs": ["SHANGHAI", "ECS"] + CHINA_SOUTH[1:-1] + CAPE_FROM_ASIA, "note": "Around the Cape of Good Hope instead of Suez."}},
      moves=["Capacity on the trade (new ships, blank sailings)", "Red Sea routing", "European import demand and inventories"],
      course="Container lines run weekly loops, so a longer route needs more ships to keep the same frequency: rerouting via the Cape absorbed a large share of the global fleet. Charter rates for ships from non-operating owners rose with it.",
      kw=["asia-europe", "asia–europe", "north europe", "fbx11", "rotterdam"])
route(id="asia-med", code="FBX13", market="container", name="China → Mediterranean", ship="Large container ship", size="about 15,000 TEU",
      frm="Shanghai", to="Genoa", speed=16, ballast=16, port_days=12, quote="USD per FEU (spot).",
      legs=["SHANGHAI", "ECS"] + CHINA_SOUTH[1:] + ["ADEN_E"] + SUEZ_NORTH[:-1] + ["TYR1", "TYR2", "GENOA"], via=["malacca", "bab-el-mandeb", "suez"],
      alts={"bab-el-mandeb": {"legs": ["SHANGHAI", "ECS"] + CHINA_SOUTH[1:-1] + ["IND2", "IND3", "AGUL", "CGH", "SATL1", "SATL2", "SATL3", "NATL1", "NATL2", "NATL3", "STV", "GIB", "MED4", "MED3", "TYR2", "GENOA"],
                              "note": "Around Africa and into the Mediterranean through Gibraltar: the detour is relatively longer than for North Europe."},
            "suez": {"legs": ["SHANGHAI", "ECS"] + CHINA_SOUTH[1:-1] + ["IND2", "IND3", "AGUL", "CGH", "SATL1", "SATL2", "SATL3", "NATL1", "NATL2", "NATL3", "STV", "GIB", "MED4", "MED3", "TYR2", "GENOA"],
                     "note": "Around Africa and into the Mediterranean through Gibraltar."}},
      moves=["Red Sea routing (the Cape detour hits the Mediterranean hardest)", "Transshipment hubs in the Mediterranean", "Capacity and blank sailings"],
      course="Going around Africa adds more for Mediterranean ports than for Rotterdam, because ships must sail back up to Gibraltar. That is why Mediterranean spot rates rose most in the Red Sea crisis.",
      kw=["mediterranean", "fbx13", "genoa"])
route(id="transpacific", code="FBX01", market="container", name="China → US West Coast", ship="Large container ship", size="about 14,000 TEU",
      frm="Shanghai", to="Los Angeles / Long Beach", speed=17, ballast=17, port_days=8, quote="USD per FEU (spot).",
      legs=["SHANGHAI", "TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "LA"], via=[],
      moves=["US import demand and inventories", "US tariffs (front-loading before deadlines)", "West Coast port labour and rail links inland"],
      course="The shortest main lane from Asia to the US, sailing a great-circle arc across the North Pacific. Tariff announcements move volumes and rates here first.",
      kw=["transpacific", "trans-pacific", "us west coast", "long beach", "los angeles", "fbx01", "tariff*"])
route(id="china-usec", code="FBX03", market="container", name="China → US East Coast via Panama", ship="Neopanamax container ship", size="about 13,000 TEU",
      frm="Shanghai", to="New York / New Jersey", speed=17, ballast=17, port_days=10, quote="USD per FEU (spot).",
      legs=["SHANGHAI", "CP0", "CP1", "CP2", "CP3", "CP4", "CP5", "PAN_P", "BALBOA", "COLON", "WIND1", "WIND", "BAHAMA", "ATLW", "NYO", "NY"], via=["panama"],
      alts={"panama": {"legs": ["SHANGHAI", "ECS"] + CHINA_SOUTH[1:] + ["ADEN_E"] + SUEZ_NORTH + ["MED3", "MED4", "GIB", "NATL3", "ATL2", "NYO", "NY"],
                       "note": "Via Suez, the main alternative when Panama is restricted (if the Red Sea is open)."}},
      moves=["Panama Canal capacity", "US East Coast imports", "Rail versus all-water routing through the US West Coast"],
      course="Shippers choose between an all-water route via Panama or Suez and the West Coast plus rail. Canal restrictions shift cargo between ports and modes.",
      kw=["us east coast", "new york", "savannah", "fbx03"])

route(id="qatar-lng", code="", market="gas", name="Qatar LNG → Japan", ship="LNG carrier (Q-Flex/Q-Max)", size="about 210,000 cbm",
      frm="Ras Laffan, Qatar", to="Tokyo Bay", speed=17, ballast=17, port_days=3, quote="Mostly long-term charters to the project; spot LNG carrier rates are quoted in USD per day.",
      legs=["RAS_LAFFAN", "PG2", "HORMUZ", "GOO", "ARAB", "ARAB2", "DONDRA", "MAL_W", "MAL1", "MAL2", "SING", "SING_E"] + SCS_TO_JAPAN, via=["hormuz", "malacca"],
      moves=["Asian gas demand and the JKM price", "Hormuz security", "New Qatari capacity (North Field expansion)"],
      course="Qatar's LNG fleet is largely on long-term charters backed by the export project: the kind of charter-backed finance banks like. The voyage passes Hormuz, so war-risk cover is part of the cost.",
      kw=["qatar*", "ras laffan", "q-max", "north field"])
route(id="blng1", code="BLNG1", market="gas", name="Australia → Japan", ship="LNG carrier", size="174,000 cbm",
      frm="Gladstone, Australia", to="Tokyo Bay", speed=17, ballast=17, port_days=3, quote="USD per day (spot TCE).",
      legs=["GLAD", "AUS1", "AUS2", "SOL", "SOL2", "MIC", "MIC2", "JPS", "TOKYO"], via=[],
      moves=["Japanese and Korean winter demand", "Australian plant outages", "New ships delivering into the spot market"],
      course="A short Pacific route compared with US cargoes to Asia, so it needs fewer ship-days per cargo.",
      kw=["australian lng", "gladstone", "blng1"])
route(id="blng2", code="BLNG2", market="gas", name="US Gulf → Continent", ship="LNG carrier", size="174,000 cbm",
      frm="Sabine Pass", to="Rotterdam", speed=17, ballast=17, port_days=3, quote="USD per day (spot TCE).",
      legs=["SABINE"] + USG_TO_EUR, via=["dover"],
      moves=["European gas prices (TTF) against Asian prices (JKM)", "European storage levels before winter", "New US export plants"],
      course="Since 2022 the US has become Europe's largest LNG supplier, replacing Russian pipeline gas.",
      kw=["us lng", "sabine pass", "europe lng", "blng2", "ttf"])
route(id="blng3", code="BLNG3", market="gas", name="US Gulf → Japan via Panama", ship="LNG carrier", size="174,000 cbm",
      frm="Sabine Pass", to="Tokyo Bay", speed=17, ballast=17, port_days=3, quote="USD per day (spot TCE).",
      legs=["SABINE"] + USG_TO_PANAMA + PAN_TO_JAPAN, via=["panama"],
      alts={"panama": {"legs": ["SABINE", "GOM", "FS1", "FS2", "FS3", "FS4", "SATL3", "SATL2", "SATL1", "CGH", "AGUL", "IND3", "MAL_W", "MAL1", "MAL2", "SING", "SING_E"] + SCS_TO_JAPAN,
                       "note": "Around the Cape of Good Hope, as many US cargoes did during the 2023–24 Panama drought."}},
      moves=["The JKM–TTF price spread (Asia versus Europe)", "Panama Canal slots", "Red Sea routing (the Suez alternative)"],
      course="Each US cargo to Asia faces a route choice: Panama, Suez or the Cape. Longer routings absorb LNG carriers and support spot rates.",
      kw=["us lng", "blng3", "lng carrier*"])
route(id="blpg1", code="BLPG1", market="gas", name="Ras Tanura → Chiba (LPG)", ship="VLGC", size="44,000 t LPG",
      frm="Ras Tanura, Saudi Arabia", to="Chiba, Tokyo Bay", speed=16, ballast=16, port_days=4, quote="USD per tonne, converted to TCE.",
      legs=["RAS_TANURA"] + GULF_TO_MALACCA + SCS_TO_JAPAN, via=["hormuz", "malacca"],
      moves=["Middle East LPG export volumes", "Asian petrochemical demand", "Competition from US cargoes"],
      course="VLGCs carry propane and butane. Middle East cargoes compete with US cargoes for Asian buyers.",
      voyage=dict(cargo=44000, freight=90, cons=35),
      kw=["lpg", "vlgc*", "propane", "blpg1"])
route(id="hammerfest", code="", market="gas", name="Hammerfest LNG → Rotterdam", ship="LNG carrier", size="about 145,000–174,000 cbm",
      frm="Melkøya, Hammerfest", to="Rotterdam (Gate terminal)", speed=17, ballast=17, port_days=3, quote="Mostly contracted volumes; spot cargoes priced against TTF.",
      legs=["HAMMERFEST", "HF1", "HF2", "HF3", "HF4", "HF5", "NOR1", "NOR2", "NS3", "NS4", "RTM_OFF", "ROTTERDAM"], via=[],
      moves=["Plant maintenance at Melkøya", "European gas prices (TTF)", "Winter weather along the Norwegian coast"],
      course="Norway's only large LNG export plant. A short route to Europe compared with US or Qatari cargoes.",
      kw=["hammerfest", "melkøya", "snøhvit", "norwegian lng"])

MARKETS = [
    dict(id="crude", name="Crude tankers", seg="freight", sizes="VLCC · Suezmax · Aframax"),
    dict(id="products", name="Product tankers", seg="freight", sizes="LR2 · LR1 · MR"),
    dict(id="drybulk", name="Dry bulk", seg="freight", sizes="Capesize · Panamax/Kamsarmax · Supramax"),
    dict(id="container", name="Containers", seg="freight", sizes="ULCV · Neopanamax · feeder"),
    dict(id="gas", name="Gas (LNG & LPG)", seg="freight", sizes="LNG carrier · VLGC"),
]

# ------------------------------------------------------------------ write and report
for r in R:
    r.pop("legs", None)
data = {
    "source": "Baltic Exchange route definitions (weekly report via DCN, 20 March 2026); EIA World Oil Transit Chokepoints (June 2024); Lloyd's Market Association Joint War Committee (JWLA-033).",
    "markets": MARKETS, "chokepoints": CHOKE, "routes": R,
}
out = Path(sys.argv[1]) / "sea.json"
out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(out, out.stat().st_size // 1024, "KB")
for r in R:
    alts = ", ".join(f"{k}: {v['nm']} nm (+{v['nm'] - r['nm']})" for k, v in (r.get("alts") or {}).items())
    print(f"{r['id']:13} {r['nm']:6} nm  {alts}")
