"""Writes docs/data/roadinfo.json: what each main road is for, and the places that matter for
trucks (mountain passes, ferries, border crossings, freight hubs, ferry links to the continent).
Coordinates are approximate (lon, lat). Traffic numbers come from roads.json (NVDB), not from here."""
import json, sys
from pathlib import Path

ROADS = {
    "E6": dict(name="E6", title="Svinesund – Oslo – Trondheim – Kirkenes", role="Norway's backbone: Svinesund (Swedish border) – Oslo – Hamar – Lillehammer – Dovrefjell – Trondheim – Mo i Rana – Narvik – Alta – Kirkenes.",
               freight="Most road freight to and from Europe crosses the border at Svinesund on the E6, including fresh salmon heading south. North of Trondheim it is the only through road, so a closure on Dovrefjell or Saltfjellet cuts the country in two for trucks.",
               kw=["e6", "e 6", "svinesund", "dovrefjell", "saltfjellet", "gudbrandsdalen"], truck="custom"),
    "E18": dict(name="E18", title="Ørje – Oslo – Kristiansand", role="Ørje (Swedish border) – Oslo – Drammen – Porsgrunn – Arendal – Kristiansand along the south coast.",
                freight="Links Oslo with the south coast ports (Larvik, Kristiansand) and with Stockholm via Ørje. Very heavy traffic around Oslo and Drammen.",
                kw=["e18", "e 18", "ørje", "vestfold", "telemark"], truck="custom"),
    "E39": dict(name="E39", title="Kristiansand – Stavanger – Bergen – Trondheim", role="The coastal road Kristiansand – Stavanger – Bergen – Førde – Ålesund – Molde – Trondheim.",
                freight="Bergen's link to Stavanger and the north. Several ferry crossings make trips slow and costly per kilometre; Rogfast (a subsea tunnel under construction) will replace the ferry north of Stavanger, and the plan is to remove more ferries over time.",
                kw=["e39", "e 39", "ferjefri", "rogfast", "hordfast", "kyststamvegen"], truck="bgo-svg"),
    "E16": dict(name="E16", title="Bergen – Lærdal – Oslo – Sweden", role="Bergen – Voss – Lærdal – Filefjell – Valdres – Hønefoss – Oslo – Kongsvinger – Sweden.",
                freight="The main year-round truck route between Bergen and Oslo, because Filefjell is lower and closes less often than Haukelifjell and Hardangervidda. It includes Lærdalstunnelen, 24.5 km long. East of Oslo it carries timber and goods to and from Sweden.",
                kw=["e16", "e 16", "filefjell", "lærdalstunnelen", "valdres", "voss"], truck="bgo-osl"),
    "E134": dict(name="E134", title="Drammen – Haukeli – Haugesund", role="Drammen – Kongsberg – Notodden – Haukelifjell – Haugesund.",
                 freight="The southern east–west route between Oslo and the west coast, and the main road for Haugesund and Sunnhordland. Haukelifjell runs convoys or closes in winter storms, which sends trucks over to the E16.",
                 kw=["e134", "e 134", "haukeli", "haukelifjell"], truck="custom"),
    "E136": dict(name="E136", title="Dombås – Ålesund", role="Dombås (E6) – Romsdalen – Åndalsnes – Ålesund.",
                 freight="Connects Møre's industry, shipyards and seafood exporters with the E6.",
                 kw=["e136", "e 136", "romsdalen"], truck="custom"),
    "E10": dict(name="E10", title="Lofoten – Narvik – Sweden", role="Å in Lofoten – Svolvær – Narvik – Bjørnfjell (Swedish border) – Kiruna.",
                freight="Lofoten's seafood road and Narvik's link to Sweden. The Ofoten ore railway runs alongside it to Narvik port.",
                kw=["e10", "e 10", "lofoten", "bjørnfjell", "narvik"], truck="custom"),
    "E8": dict(name="E8", title="Tromsø – Finland", role="Tromsø – Skibotn – Kilpisjärvi (Finnish border).",
               freight="Tromsø's route to Finland. Much seafood from Troms goes this way by truck to Finland and on to Europe.",
               kw=["e8", "e 8", "skibotn", "kilpisjärvi"], truck="custom"),
    "E14": dict(name="E14", title="Trondheim – Sweden", role="Stjørdal – Meråker – Storlien (Swedish border).",
                freight="Trondheim's road to Sweden, Östersund and Sundsvall.", kw=["e14", "e 14", "meråker", "storlien"], truck="custom"),
    "E12": dict(name="E12", title="Mo i Rana – Sweden", role="Mo i Rana – Umbukta (Swedish border).", freight="Links Helgeland with northern Sweden.", kw=["e12", "e 12", "umbukta"], truck="custom"),
    "Rv7": dict(name="Rv7", title="Hønefoss – Hardangervidda – Granvin", role="Hønefoss – Gol – Geilo – Hardangervidda – Eidfjord – Granvin.",
                freight="The shortest road between Oslo and Bergen in summer, but the crossing of Hardangervidda often closes or runs convoys in winter, so many trucks choose the E16.",
                kw=["rv7", "rv. 7", "riksvei 7", "hardangervidda", "geilo"], truck="custom"),
    "Rv52": dict(name="Rv52", title="Gol – Hemsedalsfjellet – Borlaug", role="Gol – Hemsedal – Hemsedalsfjellet – Borlaug (E16).",
                 freight="A shortcut between Hallingdal and Lærdal used by trucks between Oslo and Western Norway; a mountain pass exposed to winter closures.",
                 kw=["rv52", "rv. 52", "riksvei 52", "hemsedal", "hemsedalsfjellet"], truck="custom"),
    "Rv2": dict(name="Rv2", title="Kongsvinger – Elverum", role="Kongsvinger – Elverum.", freight="Links the forest districts of Innlandet with the E16 and Sweden.", kw=["rv2", "rv. 2", "riksvei 2"], truck="custom"),
    "Rv3": dict(name="Rv3", title="Østerdalen: Elverum – Ulsberg", role="Elverum – Østerdalen – Ulsberg (E6).",
                freight="The trucks' alternative to the E6 between Oslo and Trondheim, avoiding Dovrefjell. It has one of the highest shares of heavy vehicles of any main road.",
                kw=["rv3", "rv. 3", "riksvei 3", "østerdalen"], truck="custom"),
    "Rv4": dict(name="Rv4", title="Oslo – Gjøvik", role="Oslo – Hadeland – Gjøvik.", freight="Oslo's road north on the west side of Mjøsa.", kw=["rv4", "rv. 4", "riksvei 4", "gjøvik"], truck="custom"),
    "Rv5": dict(name="Rv5", title="Florø – Førde – Lærdal", role="Florø – Førde – Fjærland – Sogndal – Lærdal.", freight="Sunnfjord's link to the E16 and Eastern Norway.", kw=["rv5", "rv. 5", "riksvei 5", "førde", "florø"], truck="custom"),
    "Rv9": dict(name="Rv9", title="Kristiansand – Setesdal – Haukeli", role="Kristiansand – Setesdal – Haukeli (E134).", freight="Kristiansand's road north to the E134.", kw=["rv9", "rv. 9", "riksvei 9", "setesdal"], truck="custom"),
    "Rv13": dict(name="Rv13", title="Ryfylke – Hardanger – Vik", role="Ryfylke – Odda – Kinsarvik – Voss – Vik.", freight="Fjord and ferry road through Ryfylke and Hardanger; slow, but it serves industry in Odda and fish farming.", kw=["rv13", "rv. 13", "riksvei 13", "ryfylke", "odda"], truck="custom"),
    "Rv15": dict(name="Rv15", title="Otta – Strynefjellet – Måløy", role="Otta (E6) – Strynefjellet – Stryn – Måløy.", freight="Seafood from Nordfjord and Måløy to the E6. Strynefjellet is exposed in winter.", kw=["rv15", "rv. 15", "riksvei 15", "strynefjellet", "måløy"], truck="custom"),
}

POIS = [
    # mountain passes
    dict(id="haukelifjell", kind="pass", name="Haukelifjell", road="E134", at=(7.2, 59.82), text="High mountain pass on the E134. In winter storms it runs convoys (kolonnekjøring) or closes, sometimes for days."),
    dict(id="hardangervidda", kind="pass", name="Hardangervidda", road="Rv7", at=(7.7, 60.42), text="Long crossing of the plateau on Rv7. Frequently closed or convoy-only in winter, so trucks usually choose the E16."),
    dict(id="filefjell", kind="pass", name="Filefjell", road="E16", at=(8.35, 61.16), text="The E16 crossing between Valdres and Lærdal. Lower and more sheltered than the alternatives, which is why it is the main winter truck route Bergen–Oslo."),
    dict(id="hemsedalsfjellet", kind="pass", name="Hemsedalsfjellet", road="Rv52", at=(8.25, 61.02), text="Rv52 between Hemsedal and Borlaug. Exposed to winter closures."),
    dict(id="dovrefjell", kind="pass", name="Dovrefjell", road="E6", at=(9.55, 62.3), text="The E6 over Dovre between Dombås and Oppdal. A closure here sends trucks between Oslo and Trondheim over Rv3 in Østerdalen."),
    dict(id="saltfjellet", kind="pass", name="Saltfjellet", road="E6", at=(15.35, 66.6), text="The E6 across the Arctic Circle. There is no alternative road through Norway, so closures stop north–south truck traffic or force detours through Sweden."),
    dict(id="strynefjellet", kind="pass", name="Strynefjellet", road="Rv15", at=(7.35, 61.95), text="Rv15 between Stryn and Grotli. Exposed in winter."),
    # ferries on E39
    dict(id="mortavika", kind="ferry", name="Mortavika–Arsvågen", road="E39", at=(5.65, 59.25), text="The E39 ferry north of Stavanger. Rogfast, a subsea tunnel under construction, will replace it."),
    dict(id="halhjem", kind="ferry", name="Halhjem–Sandvikvåg", road="E39", at=(5.35, 60.05), text="The E39 ferry south of Bergen across Bjørnafjorden. Hordfast is the planned fixed link."),
    dict(id="lavik", kind="ferry", name="Oppedal–Lavik", road="E39", at=(5.53, 61.07), text="The E39 crossing of Sognefjorden."),
    dict(id="anda", kind="ferry", name="Anda–Lote", road="E39", at=(6.1, 61.86), text="The E39 crossing of Nordfjord."),
    dict(id="festoya", kind="ferry", name="Festøya–Solavågen", road="E39", at=(6.36, 62.42), text="The E39 ferry south of Ålesund."),
    dict(id="molde", kind="ferry", name="Molde–Vestnes", road="E39", at=(7.05, 62.68), text="The E39 crossing of Romsdalsfjorden."),
    dict(id="halsa", kind="ferry", name="Halsa–Kanestraum", road="E39", at=(8.25, 63.06), text="The E39 ferry between Nordmøre and Trøndelag."),
    # border crossings
    dict(id="svinesund", kind="border", name="Svinesund", road="E6", at=(11.25, 59.09), text="Norway's busiest road border crossing and its main customs post for trucks to and from Europe. Goods must be declared in advance (Digitoll)."),
    dict(id="orje", kind="border", name="Ørje", road="E18", at=(11.65, 59.48), text="E18 border crossing towards Karlstad and Stockholm."),
    dict(id="magnor", kind="border", name="Magnor", road="E16", at=(12.2, 59.95), text="E16 border crossing east of Kongsvinger."),
    dict(id="storlien", kind="border", name="Storlien", road="E14", at=(12.1, 63.32), text="E14 border crossing from Trøndelag to Sweden."),
    dict(id="bjornfjell", kind="border", name="Bjørnfjell", road="E10", at=(18.1, 68.43), text="E10 border crossing between Narvik and Kiruna."),
    dict(id="kilpisjarvi", kind="border", name="Kilpisjärvi", road="E8", at=(20.8, 69.03), text="E8 border crossing to Finland."),
    # freight hubs
    dict(id="alnabru", kind="hub", name="Alnabru (Oslo)", road=None, at=(10.84, 59.93), text="Norway's largest rail freight terminal, where containers and trailers move between train and truck."),
    dict(id="bergen", kind="hub", name="Bergen", road=None, at=(5.32, 60.39), text="Port and logistics hub; supply base at CCB Ågotnes and the oil terminal at Mongstad to the north."),
    dict(id="stavanger", kind="hub", name="Stavanger (Risavika)", road=None, at=(5.6, 58.92), text="Port and offshore supply hub for the oil industry."),
    dict(id="trondheim", kind="hub", name="Trondheim", road=None, at=(10.4, 63.43), text="Gateway between southern and northern Norway; rail to the north (Nordlandsbanen) starts here."),
    dict(id="kristiansand", kind="hub", name="Kristiansand", road=None, at=(8.0, 58.15), text="Ferry port to Denmark and the Netherlands for trailers and cars."),
    dict(id="narvik", kind="hub", name="Narvik", road=None, at=(17.42, 68.44), text="Ore port and rail link to Sweden; a hub for freight to northern Norway."),
    dict(id="alesund", kind="hub", name="Ålesund", road=None, at=(6.15, 62.47), text="Seafood exports and maritime industry."),
]

# ferry and sea links that carry trailers (schematic)
LINKS = [
    dict(id="kiel", name="Oslo–Kiel (Color Line)", pts=[(10.73, 59.9), (10.6, 59.3), (10.8, 58.5), (11.0, 57.6), (10.6, 56.8), (10.9, 55.6), (10.3, 54.6), (10.15, 54.32)]),
    dict(id="hirtshals-krs", name="Kristiansand–Hirtshals", pts=[(8.0, 58.15), (9.0, 57.85), (9.96, 57.59)]),
    dict(id="hirtshals-lvk", name="Larvik–Hirtshals", pts=[(10.04, 59.05), (10.0, 58.3), (9.96, 57.59)]),
    dict(id="hirtshals-bgo", name="Bergen–Stavanger–Hirtshals (Fjord Line)", pts=[(5.32, 60.4), (4.9, 59.9), (5.4, 59.2), (5.73, 58.97), (6.6, 58.3), (8.5, 57.75), (9.96, 57.59)]),
    dict(id="eemshaven", name="Kristiansand–Eemshaven (Holland Norway Lines)", pts=[(8.0, 58.15), (7.5, 57.0), (6.8, 55.3), (6.83, 53.45)]),
    dict(id="stromstad", name="Sandefjord–Strömstad", pts=[(10.22, 59.13), (10.6, 59.0), (11.17, 58.94)]),
]
# main roads in Sweden, Finland and Denmark for context (no traffic data shown)
NORDIC = [
    dict(id="se-e6", name="E6 Svinesund–Gothenburg–Malmö", pts=[(11.25, 59.09), (11.33, 58.35), (11.95, 57.7), (12.4, 57.15), (12.85, 56.67), (12.7, 56.05), (13.0, 55.6)]),
    dict(id="se-e18", name="E18 Ørje–Karlstad–Stockholm", pts=[(11.65, 59.48), (13.5, 59.38), (15.2, 59.27), (16.55, 59.61), (18.06, 59.33)]),
    dict(id="se-e20", name="E20 Gothenburg–Stockholm", pts=[(11.95, 57.7), (12.55, 57.93), (13.85, 58.39), (15.2, 59.27)]),
    dict(id="se-e4", name="E4 Helsingborg–Stockholm–Haparanda", pts=[(12.7, 56.05), (14.16, 57.78), (16.2, 58.59), (18.06, 59.33), (17.14, 60.67), (17.3, 62.39), (20.26, 63.83), (21.0, 64.75), (22.15, 65.58), (24.14, 65.84)]),
    dict(id="se-e14", name="E14 Storlien–Östersund–Sundsvall", pts=[(12.1, 63.32), (14.64, 63.18), (17.3, 62.39)]),
    dict(id="se-e10", name="E10 Bjørnfjell–Kiruna–Luleå", pts=[(18.1, 68.43), (20.22, 67.86), (21.68, 66.6), (22.15, 65.58)]),
    dict(id="se-e16", name="E16/E45 Magnor–Torsby", pts=[(12.2, 59.95), (13.0, 60.13)]),
    dict(id="fi-e8", name="E8 Kilpisjärvi–Tornio", pts=[(20.8, 69.03), (23.0, 68.0), (23.7, 67.0), (24.14, 65.84)]),
    dict(id="dk-oresund", name="Øresund link Malmö–Copenhagen", pts=[(13.0, 55.6), (12.57, 55.68)]),
    dict(id="dk-e20", name="E20 Copenhagen–Odense–Kolding", pts=[(12.57, 55.68), (11.9, 55.45), (10.39, 55.4), (9.47, 55.49)]),
    dict(id="dk-e45", name="E45 Frederikshavn–Aarhus–German border", pts=[(10.54, 57.44), (9.92, 57.05), (10.2, 56.15), (9.75, 55.85), (9.47, 55.49), (9.36, 54.82)]),
    dict(id="dk-hirtshals", name="Hirtshals–Aalborg", pts=[(9.96, 57.59), (9.92, 57.05)]),
]

out = Path(sys.argv[1]) / "roadinfo.json"
out.write_text(json.dumps({"roads": ROADS, "pois": POIS, "links": LINKS, "nordic": NORDIC}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(out, out.stat().st_size // 1024, "KB")
