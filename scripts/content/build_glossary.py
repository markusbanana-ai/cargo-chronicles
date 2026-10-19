# Source for docs/data/glossary.json
# m: match strings. "=" prefix = case-sensitive, "~" prefix = regex (case-sensitive), otherwise case-insensitive.
import json, sys

CATS = {
    "road": "Road transport",
    "charter": "Chartering & contracts",
    "market": "Freight markets & ships",
    "finance": "Ship finance",
    "insurance": "Marine insurance",
    "offshore": "Offshore & energy",
    "reg": "Regulation & compliance",
    "trade": "Trade, ports & logistics",
    "email": "Email & everyday abbreviations",
}

G = []
def T(id, term, cat, d, ex=None, no=None, full=None, m=None, hl=True, core=()):
    G.append({k: v for k, v in dict(id=id, term=term, full=full, cat=cat, def_=d, ex=ex, no=no,
             m=m if m is not None else [term], hl=hl, core=list(core)).items() if v not in (None, [], ())})

# ---------------- ROAD ----------------
T("cabotage", "Cabotage", "road",
  "Domestic transport inside a country carried out by a haulier registered in another country. In the EU/EEA it is only allowed in limited form: EU rules permit up to three cabotage trips within seven days after an international delivery, followed by a waiting period before new cabotage in the same country.",
  "A Lithuanian truck delivers a load from Germany to Bergen, then carries a load from Bergen to Ålesund before leaving Norway. The Bergen–Ålesund trip is cabotage.",
  no="Kabotasje", m=["cabotage", "kabotasje", "kabotasjekjøring"], core=["road"])
T("driving-rest", "Driving and rest times", "road",
  "EU rules (Regulation 561/2006, also applied in Norway) that limit truck driving: max 9 hours a day (10 hours twice a week), 56 hours a week and 90 hours over two weeks; a 45-minute break after 4.5 hours of driving; and at least 11 hours of daily rest (reducible to 9 hours three times between weekly rests). In the US the equivalent is called hours of service (HOS), with different limits.",
  "Bergen–Oslo is roughly 7–8 hours of driving. It is legal in one day, but the driver must take a 45-minute break on the way (it can be split into 15 + 30 minutes).",
  no="Kjøre- og hviletid", m=["driving and rest times", "driving times", "driving time", "rest rules", "hours of service", "hours-of-service", "=HOS", "kjøre- og hviletid", "kjøre- og hviletidsreglene", "hviletid", "hviletidsreglene"], core=["road"])
T("tachograph", "Tachograph", "road",
  "Device in the truck that records driving time, rest, speed and distance, linked to the driver's card. Authorities read it to check driving and rest times. Under the EU Mobility Package, vans over 2.5 tonnes used in international transport are also brought under tachograph rules.",
  "At a roadside check, Statens vegvesen downloads the driver card data for the past weeks and finds a missing daily rest. Both driver and company can be fined.",
  no="Fartsskriver", m=["tachograph", "tachographs", "smart tachograph", "fartsskriver", "fartsskrivere", "fartsskriveren"])
T("rest-area", "Truck rest area", "road",
  "A parking area where truck drivers can take their legally required daily or weekly rest, with toilets and room for long vehicles. Norway has too few on key routes, which makes it hard to follow the rest rules.",
  "If Statens vegvesen builds 50 new rest spaces along the E16, drivers between Bergen and Oslo can stop when their driving time runs out instead of searching for a legal place to park.",
  no="Døgnhvileplass", m=["døgnhvileplass", "døgnhvileplasser", "døgnhvile", "dognhvileplasser", "hvileplass", "hvileplasser", "rest area", "rest areas", "truck stop", "truck stops"])
T("modulvogntog", "Modular vehicle combination", "road",
  "A longer and heavier truck combination (up to 25.25 m and 60 tonnes in Norway) allowed only on approved roads. Two modular trucks can carry roughly as much as three regular ones, which lowers cost and emissions per tonne.",
  "Letting modular trucks through the E6 tunnels in Sørfold means north–south freight in Norway no longer has to detour via Sweden or Lofoten.",
  no="Modulvogntog", m=["modulvogntog", "modular truck", "modular trucks", "modular vehicle combination", "=EMS", "longer and heavier vehicles"])
T("vogntog", "Truck-trailer combination", "road",
  "A truck (tractor unit or rigid truck) pulling one or more trailers. The most common long-haul setup is a tractor unit with a semitrailer.",
  "A tractor with a 13.6 m semitrailer can carry 33 euro pallets on one deck.",
  no="Vogntog / trekkvogn med semitrailer", m=["vogntog", "semitrailer", "semitrailers", "semi-trailer", "semi-trailers", "trekkvogn", "tractor unit", "articulated lorry", "articulated lorries"])
T("bruksklasse", "Road class (BK)", "road",
  "Norwegian classification of roads by the axle load, total weight and length they allow, for example BK10/50 (10 t axle load, 50 t total) or BK10/60. Weaker county roads may have lower classes, which limits what trucks can deliver there.",
  "A 70-tonne transformer cannot use a BK10/50 road without a special permit (dispensasjon) and possibly bridge reinforcement.",
  no="Bruksklasse", m=["bruksklasse", "bruksklassen", "=BK10/50", "=BK10/60", "=BK10", "=BKT8"])
T("axle-load", "Axle load", "road",
  "The weight carried by one axle. Roads and bridges are rated for a maximum axle load, which often decides how much a truck may carry even when its total weight is below the limit.",
  "In spring, thaw restrictions (telerestriksjoner) can cut the allowed axle load on a county road for several weeks, so a haulier must split loads or use other routes.",
  no="Aksellast", m=["axle load", "axle loads", "axle weight", "aksellast", "telerestriksjoner"])
T("ftl", "FTL", "road",
  "Full truckload: a shipment that fills or books a whole truck for one customer, going directly from loading to unloading without passing a terminal.",
  "A factory in Sandnes sends 33 pallets to one warehouse in Oslo. That is one FTL.",
  full="Full truckload", no="Komplette laster", m=["=FTL", "full truckload", "full truck load", "truckload"])
T("ltl", "LTL / groupage", "road",
  "Less than truckload: shipments too small to fill a truck are combined with other customers' goods, usually sorted through terminals, and priced per kg, pallet or loading metre. Groupage and part load (partilast) are related European terms.",
  "Three pallets from Bergen to Trondheim go as groupage: collected, sorted at a terminal and delivered together with other freight.",
  full="Less than truckload", no="Stykkgods / samlast / partilast", m=["=LTL", "less than truckload", "less-than-truckload", "groupage", "part load", "part loads", "partilast", "stykkgods", "samlast"], core=["road"])
T("ldm", "Loading metre (LDM)", "road",
  "Unit for how much trailer floor length a shipment takes, regardless of weight. One loading metre is one metre of a 2.4 m wide trailer; a standard semitrailer has 13.6 loading metres.",
  "One euro pallet (1.2 × 0.8 m) takes 0.4 ldm, so 33 pallets fill a 13.6 m trailer. A customer booking 4 ldm is buying space for about 10 pallets.",
  no="Lastemeter", m=["loading metre", "loading metres", "loading meter", "loading meters", "lastemeter", "=LDM", "=ldm"], core=["road"])
T("euro-pallet", "Euro pallet", "road",
  "Standard wooden pallet measuring 1200 × 800 mm. The basic unit for pricing and planning road freight in Europe.",
  "A customer asking for space for 10 euro pallets needs about 4 loading metres.",
  no="EUR-pall", m=["euro pallet", "euro pallets", "=EUR pallet", "EUR-pall", "europall", "europaller", "EUR-paller"])
T("cmr", "CMR", "road",
  "The 1956 convention on contracts for international road transport, and the consignment note (CMR waybill) used with it. Unless more is agreed, the carrier's liability for lost or damaged goods is limited to 8.33 SDR per kg gross weight.",
  "A 1,000 kg pallet of electronics worth NOK 2 million is lost on a trip from Germany. The haulier is liable for about 8,330 SDR (roughly NOK 110,000 at recent exchange rates), so the owner needs cargo insurance for the rest.",
  full="Convention on the Contract for the International Carriage of Goods by Road", no="CMR-fraktbrev", m=["=CMR", "CMR waybill", "CMR convention", "fraktbrev"], core=["road"])
T("adr", "ADR", "road",
  "European rules for carrying dangerous goods by road: packaging, labelling, vehicle equipment, documents and driver training (ADR certificate). Vehicles show orange plates with a hazard number on top and a UN number below.",
  "A tank truck carrying diesel shows 30 over 1202 on its orange plate: 30 means flammable liquid, 1202 is diesel/gas oil.",
  full="Agreement concerning the International Carriage of Dangerous Goods by Road", no="ADR / farlig gods", m=["=ADR", "dangerous goods", "farlig gods", "hazmat"], core=["road"])
T("un-number", "UN number", "road",
  "Four-digit code identifying a dangerous substance in transport, used for road, sea and air.",
  "UN 1203 is petrol, UN 1202 is diesel/gas oil and UN 1965 is LPG.",
  no="UN-nummer", m=["UN number", "UN numbers", "UN-nummer", "~UN ?\\d{4}"])
T("autopass", "AutoPASS (road tolls)", "road",
  "Norway's electronic toll system. Vehicles over 3.5 tonnes used in business must carry an AutoPASS tag, and heavy vehicles pay much higher toll rates than cars.",
  "A distribution truck passing several toll points around Bergen each day pays heavy-vehicle rates every time, which becomes a real share of the route cost.",
  no="Bompenger / bombrikke", m=["AutoPASS", "bompenger", "bompengar", "bomstasjon", "bomstasjoner", "bombrikke", "road toll", "road tolls", "toll road", "toll roads"])
T("road-tax", "Road usage tax on fuel", "road",
  "Norwegian excise duty on diesel and petrol used on roads. Together with the CO2 tax it makes up a large share of the pump price, so tax changes hit hauliers' costs directly.",
  "A truck using 40,000 litres of diesel a year saves about NOK 40,000 if fuel taxes are cut by NOK 1 per litre.",
  no="Veibruksavgift / dieselavgift", m=["veibruksavgift", "veibruksavgiften", "dieselavgift", "dieselavgiften", "dieselavgiftene", "dieselavgiftslettelsene", "fuel duty", "fuel tax", "fuel taxes", "diesel tax", "diesel taxes"], core=["road"])
T("pro-diesel", "Professional diesel", "road",
  "A scheme where commercial hauliers get part of the fuel tax back, so they pay less than private motorists. Some EU countries (for example Belgium and France) have one; Norwegian truck owners have asked for a similar arrangement.",
  "A refund of NOK 2 per litre would give a haulier with ten trucks, each using 40,000 litres a year, NOK 800,000 back.",
  no="Proff diesel", m=["proff diesel", "professional diesel"])
T("fuel-surcharge", "Fuel surcharge / diesel clause", "road",
  "A contract term that adjusts the freight price when diesel prices move, usually monthly against an index. Without it, the haulier carries all the fuel price risk.",
  "A truck using 0.35 litres per km: every NOK 1 rise in the litre price adds NOK 0.35 per km. On a 400 km job that is NOK 140 the clause passes on to the customer.",
  no="Dieselklausul / drivstofftillegg", m=["fuel surcharge", "fuel surcharges", "diesel clause", "dieselklausul", "drivstofftillegg"], core=["road"])
T("backhaul", "Backhaul / return load", "road",
  "A load carried on the way back after a delivery, so the truck does not drive empty. When more goods flow into a region than out of it, backhauls are scarce and prices rise in the busy direction.",
  "If trucks arrive full in a town but find few loads out, a carrier prices the inbound trip higher to cover the empty return.",
  no="Returlast", m=["backhaul", "backhauls", "return load", "return loads", "returlast", "returlaster"])
T("empty-running", "Empty running", "road",
  "Kilometres driven without cargo. A major cost driver that good planning and freight exchanges try to reduce.",
  "A truck that drives 1,000 km loaded and 300 km empty has 23% empty running.",
  no="Tomkjøring", m=["empty running", "empty miles", "empty kilometres", "tomkjøring"])
T("driver-cpc", "Driver CPC (YSK)", "road",
  "Certificate of Professional Competence that commercial truck and bus drivers in the EU/EEA need, renewed with 35 hours of training every five years.",
  "A driver whose YSK has expired cannot drive commercially until the 35-hour course is done, even with a valid licence.",
  full="Certificate of Professional Competence", no="Yrkessjåførkompetanse (YSK)", m=["=YSK", "yrkessjåførkompetanse", "driver CPC", "yrkessjåfør", "yrkessjåfører"])
T("operator-licence", "Haulage licence", "road",
  "Permit a company needs to carry goods for others for payment. Requires good repute, sound finances and professional competence.",
  "A new company in Bergen must hold a goods licence before taking paid jobs with trucks over 3.5 tonnes.",
  no="Løyve (godsløyve)", m=["løyve", "løyver", "godsløyve", "operator licence", "operator license", "haulage licence"])
T("abnormal-load", "Abnormal load / special transport", "road",
  "Cargo that exceeds normal size or weight limits, such as transformers, rig equipment or wind turbine blades. Needs a special permit (dispensasjon), route planning and often escort vehicles.",
  "Moving a 120-tonne transformer from Ågotnes to a substation can require a route survey, escort cars, police help and night-time driving.",
  no="Spesialtransport", m=["abnormal load", "abnormal loads", "special transport", "spesialtransport", "oversize load", "oversized load", "oversized cargo", "heavy haulage", "dispensasjon"], core=["road"])
T("escort-vehicle", "Escort vehicle", "road",
  "A vehicle that travels with an oversized load to warn other traffic and guide the truck through narrow points. The permit decides when escorts are required.",
  "A very wide load on a narrow two-lane road needs escort cars in front and behind so oncoming traffic can be stopped in time.",
  no="Følgebil", m=["escort vehicle", "escort vehicles", "escort car", "escort cars", "følgebil", "følgebiler", "pilot car"])
T("route-survey", "Route survey", "road",
  "A check of the planned route for an oversized load: bridges, tunnels, height clearances, curves, roundabouts and overhead lines.",
  "Before moving a 6 m tall module from Haugesund, the survey finds a tunnel that is too low, and the convoy is rerouted.",
  no="Ruteundersøkelse", m=["route survey", "route surveys", "ruteundersøkelse"])
T("mcs", "Megawatt charging (MCS)", "road",
  "Fast-charging standard for heavy electric trucks with power above 1 MW, so a truck can add a large share of its range during the driver's 45-minute break.",
  "A truck with a 600 kWh battery charging at 1 MW could refill most of it during the mandatory break.",
  no="Megawattlading", m=["megawatt charging", "megawattlading", "=MCS"])
T("electric-truck", "Electric truck", "road",
  "Battery-powered truck. Lower energy and maintenance costs than diesel, but higher purchase price, heavier batteries and dependence on charging along the route.",
  "Norwegian hauliers often start with electric trucks on city distribution, where daily distances are short and depot charging covers most needs.",
  no="Elektrisk lastebil / el-lastebil", m=["electric truck", "electric trucks", "e-truck", "e-trucks", "el-lastebil", "el-lastebiler", "elektrisk lastebil", "elektriske lastebiler", "battery-electric truck", "battery-electric trucks"])

# ---------------- CHARTERING ----------------
T("charter-party", "Charter party (C/P)", "charter",
  "The contract between a shipowner and a charterer for the use of a ship. Standard forms (Gencon, NYPE, Shelltime and others) are used as the base and amended with extra clauses.",
  "A fixture recap might read: 'Gencon 94 C/P, otherwise as per last'. It means the standard Gencon form with the same extra terms as the previous deal.",
  no="Certeparti", m=["charter party", "charter parties", "charterparty", "charterparties", "=C/P", "certeparti"], core=["freight"])
T("voyage-charter", "Voyage charter", "charter",
  "The ship is hired to carry a cargo from A to B for a freight per tonne or a lump sum. The owner pays bunkers, port costs and crew; the charterer pays demurrage if loading or discharging takes longer than agreed.",
  "A Supramax is fixed to carry 55,000 t of grain from Brazil to Egypt at USD 38 per tonne: freight of about USD 2.1 million.",
  no="Reisebefraktning", m=["voyage charter", "voyage charters", "voyage-charter", "spot charter"], core=["freight"])
T("time-charter", "Time charter (T/C)", "charter",
  "The charterer hires the ship for a period (days to years) at a daily hire rate, decides where it trades and pays bunkers and port costs. The owner still runs the ship and pays crew, maintenance and insurance.",
  "A VLCC fixed on a one-year time charter at USD 60,000 per day earns the owner about USD 21.9 million over the year.",
  no="Tidsbefraktning", m=["time charter", "time charters", "time-charter", "time-chartered", "=T/C", "time-charter contract"], core=["freight"])
T("tct", "Trip time charter (TCT)", "charter",
  "A time charter for a single voyage: paid per day, but the length is decided by the trip.",
  "'TCT via Black Sea, redelivery Skaw, USD 18,500/day' means daily hire for one trip ending off Skagen.",
  m=["trip time charter", "trip charter", "=TCT"])
T("bareboat", "Bareboat charter", "charter",
  "The charterer takes over the ship as if owning it: provides the crew, maintenance and insurance, and pays hire for a long period. Common in financing deals.",
  "A Chinese leasing company buys a tanker and bareboat charters it back to the seller for 10 years with an option to buy it back.",
  no="Bareboat-befraktning", m=["bareboat", "bareboat charter", "bareboat charters", "demise charter", "=BBC charter"])
T("coa", "Contract of affreightment (COA)", "charter",
  "An agreement to carry a set volume of cargo over a period, for example 10 shipments a year. The owner decides which ship performs each shipment.",
  "A COA to move 600,000 t of iron ore a year from Northern Norway to Rotterdam in eight shipments.",
  m=["contract of affreightment", "contracts of affreightment", "=COA", "=COAs"])
T("laytime", "Laytime", "charter",
  "Time the charterer is allowed for loading and discharging without paying extra, set in the charter party as a number of days or a loading rate.",
  "Loading 50,000 t at 10,000 t per weather working day gives 5 days of laytime.",
  no="Liggetid", m=["laytime", "liggetid"], core=["freight"])
T("demurrage", "Demurrage", "charter",
  "Compensation the charterer pays the shipowner when loading or discharging takes longer than the agreed laytime, at a daily rate. In container shipping, demurrage instead means a fee for leaving a container too long in the terminal.",
  "Exceeding laytime by 2 days and 6 hours with demurrage at USD 20,000/day pro rata costs the charterer USD 45,000.",
  no="Overliggedagspenger", m=["demurrage", "overliggedagspenger", "=DEM"], core=["freight"])
T("despatch", "Despatch", "charter",
  "The reverse of demurrage: money the owner pays the charterer for finishing cargo work faster than the allowed laytime, often at half the demurrage rate.",
  "Finishing one day early with despatch at USD 10,000/day earns the charterer USD 10,000.",
  m=["despatch", "dispatch money", "=DHD"])
T("laycan", "Laycan", "charter",
  "The date window in which the ship must arrive ready to load (laydays and cancelling). Early arrival need not be accepted; late arrival lets the charterer cancel.",
  "'Laycan 20–25 November Narvik' means the ship must tender notice of readiness in Narvik between those dates.",
  m=["laycan", "laydays", "laydays/cancelling"])
T("nor", "NOR", "charter",
  "Notice of readiness: the master's formal notice that the ship has arrived and is ready to load or discharge. Laytime normally starts after a set notice time following a valid NOR.",
  "NOR tendered 08:00 Monday with 6 hours' notice time: laytime starts counting at 14:00.",
  full="Notice of readiness", m=["notice of readiness", "=NOR"])
T("sof", "SOF", "charter",
  "Statement of facts: the port log of all key times during a call (arrival, NOR, berthing, start and stop of cargo work, delays). Used to calculate laytime and demurrage.",
  "The SOF shows that rain stopped loading for 9 hours, which does not count as laytime on a weather working day basis.",
  full="Statement of facts", m=["statement of facts", "=SOF"])
T("off-hire", "Off-hire", "charter",
  "Periods under a time charter when the ship cannot perform (breakdown, crew problems, dry-docking), so the charterer stops paying hire.",
  "An engine failure keeps the ship idle for 3 days. At USD 25,000/day the owner loses USD 75,000 of hire.",
  m=["off-hire", "off hire", "offhire"])
T("fixture", "Fixture", "charter",
  "A concluded charter deal. Broker reports list fixtures with ship size, cargo, route, rate and charterer.",
  "A reported fixture might read: 'Capesize, 170,000 t iron ore, Tubarão to Qingdao, USD 24.50/t'.",
  m=["fixture", "fixtures", "fixture recap", "clean recap"])
T("subjects", "Subjects (subs)", "charter",
  "Conditions that must be lifted before a fixture becomes binding, such as board approval or the receiver's approval of the ship. 'On subs' means agreed but not yet firm.",
  "A ship 'fixed on subs' can still fall through if the receiver rejects the vessel.",
  m=["on subs", "subs lifted", "subjects lifted"])
T("shipbroker", "Shipbroker", "charter",
  "Intermediary who negotiates deals between shipowners and charterers (chartering) or between buyers and sellers of ships (sale and purchase), paid by commission—typically 1.25% of freight or about 1% of a ship sale.",
  "Fearnleys, Clarksons and Banchero Costa publish weekly market reports based on what their brokers see in the market.",
  no="Skipsmegler", m=["shipbroker", "shipbrokers", "shipbroking", "ship broker", "ship brokers", "skipsmegler", "skipsmeglere", "skipsmegling", "broker's report", "brokers report"], core=["freight"])
T("commission", "Address commission and brokerage", "charter",
  "Commissions deducted from freight or hire. Address commission goes back to the charterer (often 2.5–3.75%), brokerage goes to the brokers (often 1.25%).",
  "On USD 1 million of freight with 3.75% total commission, the owner receives USD 962,500.",
  m=["address commission", "=ADCOM", "brokerage commission"])
T("operator", "Operator / disponent owner", "charter",
  "A company that charters in ships and trades them as if it owned them, earning the difference between the hire it pays and what the ships earn.",
  "An operator takes a Supramax for one year at USD 14,000/day and re-lets it on trips averaging USD 16,000/day, a margin of USD 2,000 per day.",
  m=["disponent owner", "disponent owners", "tonnage provider"])
T("bimco", "BIMCO", "charter",
  "The largest international shipping association. It drafts standard contracts and clauses (Gencon, Supplytime, Barecon and others) used across the industry.",
  "BIMCO's war risk clauses (CONWARTIME for time charters, VOYWAR for voyage charters) decide whether a ship must sail into an area that has become dangerous.",
  m=["=BIMCO", "=CONWARTIME", "=VOYWAR"])
T("cp-forms", "Standard charter forms", "charter",
  "Pre-printed contracts used as the base for charters: Gencon (voyage, dry cargo), NYPE (time charter, dry cargo), Shelltime and BPTIME (tanker time charter), Asbatankvoy (tanker voyage), Barecon (bareboat) and Supplytime (offshore vessels).",
  "Because both sides start from Gencon, they only need to negotiate the rider clauses that differ from the standard text.",
  m=["Gencon", "=NYPE", "Shelltime", "=BPTIME", "Asbatankvoy", "Barecon", "Supplytime"])
T("worldscale", "Worldscale (WS)", "charter",
  "Freight rate system for tankers. Each route has a flat rate (WS 100) in USD per tonne, published yearly, and deals are quoted as a percentage of it.",
  "If the flat rate Middle East–China is USD 20/t and a VLCC is fixed at WS 60, the freight is USD 12 per tonne.",
  m=["Worldscale", "~WS ?\\d{2,3}"])
T("ballast", "Ballast and laden legs", "charter",
  "Laden: sailing with cargo. Ballast: sailing empty to the next loading port, with ballast water for stability. Ballast legs earn nothing, so the whole round voyage decides profitability.",
  "A tanker that discharges in China often sails four to five weeks in ballast back to the Middle East or the US Gulf.",
  m=["in ballast", "ballast leg", "ballast legs", "ballasting", "laden leg", "laden voyage"])

# ---------------- FREIGHT MARKETS & SHIPS ----------------
T("dry-bulk", "Dry bulk", "market",
  "Unpackaged dry cargo shipped in large volumes: iron ore, coal, grain, bauxite and fertiliser. Carried by bulk carriers grouped by size.",
  "Iron ore from Brazil and Australia to China is the largest dry bulk trade by volume.",
  no="Tørrbulk", m=["dry bulk", "drybulk", "dry-bulk", "bulk carrier", "bulk carriers", "bulker", "bulkers", "tørrbulk"], core=["freight"])
T("capesize", "Capesize", "market",
  "The largest common bulk carriers (about 160,000–210,000 dwt), too big for the old Panama Canal, so they sail around the Cape of Good Hope or Cape Horn. They mainly carry iron ore and coal and are the most volatile segment.",
  "Capesize rates can double or halve within weeks when Chinese iron ore imports change.",
  m=["capesize", "capesizes", "=Capes", "Newcastlemax", "=VLOC", "VLOCs"])
T("panamax", "Panamax / Kamsarmax", "market",
  "Mid-sized bulk carriers of about 65,000–85,000 dwt, originally sized for the old Panama Canal locks. Kamsarmax (about 82,000 dwt) is the modern standard. They carry coal, grain and minerals.",
  "Grain from the US Gulf to China often moves on Panamax or Kamsarmax ships.",
  m=["panamax", "panamaxes", "kamsarmax", "kamsarmaxes", "post-panamax"])
T("supramax", "Supramax / Ultramax", "market",
  "Bulk carriers of about 50,000–66,000 dwt with their own cranes (geared), so they can load and discharge in ports without shore equipment.",
  "A 61,000 dwt Ultramax can load steel coils in a port that has no cranes of its own.",
  m=["supramax", "supramaxes", "ultramax", "ultramaxes", "handymax"])
T("handysize", "Handysize", "market",
  "Small bulk carriers (about 10,000–40,000 dwt) serving smaller ports and minor bulk trades such as logs, steel and fertiliser.",
  "Logs and steel products from smaller ports often move on handysize ships.",
  m=["handysize", "handysizes"])
T("vlcc", "VLCC", "market",
  "Very large crude carrier: a crude oil tanker of about 300,000 dwt carrying roughly 2 million barrels. The workhorse of long-haul crude trades such as Middle East–China.",
  "At USD 100 per barrel, one full VLCC cargo is worth about USD 200 million.",
  full="Very large crude carrier", m=["=VLCC", "=VLCCs", "very large crude carrier", "supertanker", "supertankers", "=ULCC"], core=["freight"])
T("suezmax", "Suezmax", "market",
  "Crude tanker of about 150,000–160,000 dwt (about 1 million barrels), the largest size that can pass the Suez Canal fully loaded.",
  "Crude from West Africa to Europe often moves on Suezmaxes.",
  m=["suezmax", "suezmaxes"])
T("aframax", "Aframax", "market",
  "Tanker of about 80,000–120,000 dwt, common in shorter regional trades such as the North Sea, Baltic and Mediterranean. The coated version for refined products is called LR2.",
  "Crude from Norwegian fields to European refineries often moves on Aframaxes.",
  m=["aframax", "aframaxes"])
T("product-tanker", "Product tanker (MR, LR1, LR2)", "market",
  "Tankers with coated tanks that carry refined products such as diesel, jet fuel and naphtha. Sizes: MR about 45,000–55,000 dwt, LR1 about 70,000–80,000 dwt, LR2 about 110,000 dwt.",
  "Diesel from India to Europe typically moves on LR1 or LR2 tankers.",
  m=["product tanker", "product tankers", "products tanker", "clean tanker", "clean tankers", "=LR1", "=LR2", "=MR tanker", "=MR tankers", "=MRs"])
T("teu", "TEU", "market",
  "Twenty-foot equivalent unit: the standard measure of container capacity and volume. A 20-foot container is 1 TEU; a 40-foot container is 2 TEU (also called 1 FEU).",
  "A 24,000 TEU ship can carry about 12,000 forty-foot containers.",
  full="Twenty-foot equivalent unit", m=["=TEU", "=TEUs", "=FEU", "=FEUs", "twenty-foot equivalent"], core=["freight"])
T("liner", "Liner shipping", "market",
  "Ships running fixed, published schedules between ports—mainly container shipping—and selling space to many customers, like a bus route. The opposite of tramp shipping.",
  "Maersk, MSC and Hapag-Lloyd are liner carriers.",
  no="Linjefart", m=["liner shipping", "liner carrier", "liner carriers", "linjefart", "container line", "container lines", "boxship", "boxships", "containership", "containerships", "container ship", "container ships"])
T("tramp", "Tramp shipping", "market",
  "Ships without fixed routes that are chartered wherever the cargo is (dry bulk, tankers). Rates are set in the spot market.",
  "A bulk carrier discharging in Rotterdam may next load coal in Colombia or grain in the Black Sea, depending on which fixture pays best.",
  m=["tramp shipping", "tramp trade"])
T("blank-sailing", "Blank sailing", "market",
  "A scheduled liner voyage that the carrier cancels, usually to remove capacity when demand is weak and support freight rates.",
  "Cancelling 10% of Asia–Europe sailings in a quiet week cuts supply and slows the fall in spot rates.",
  m=["blank sailing", "blank sailings", "cancelled sailings"])
T("port-omission", "Port omission", "market",
  "A container ship skipping a scheduled port call, often to recover from delays. The cargo is moved via another port instead.",
  "If a ship skips Genoa, import containers are discharged in Valencia and carried on by the next ship in the service.",
  m=["omission", "omissions", "port omission", "port omissions", "skips port", "skip calls"])
T("container-index", "Container freight indices", "market",
  "Published indices tracking the spot price for shipping a container on major routes, such as the SCFI (Shanghai), Drewry's WCI and Freightos' FBX.",
  "If the index for Shanghai–Rotterdam rises from USD 2,000 to USD 3,000 per FEU, importers pay 50% more on new spot bookings.",
  m=["=SCFI", "=WCI", "=FBX", "World Container Index", "container index"])
T("lng-carrier", "LNG carrier", "market",
  "Ship carrying liquefied natural gas at about −162 °C in insulated tanks. The standard size today is about 174,000 cubic metres.",
  "Gas from Hammerfest LNG reaches buyers in Europe and Asia on LNG carriers.",
  m=["LNG carrier", "LNG carriers", "LNG vessel", "LNG vessels", "LNG ship", "LNG ships", "LNG shipping"], core=["freight"])
T("lpg", "LPG / VLGC", "market",
  "LPG (propane and butane) is shipped liquefied by pressure or cooling. The largest LPG ships are VLGCs (very large gas carriers) of about 84,000–90,000 cubic metres.",
  "US LPG exports to Asia are mostly carried on VLGCs.",
  m=["=LPG", "=VLGC", "=VLGCs", "liquefied petroleum gas", "=VLAC", "=VLACs"])
T("car-carrier", "Car carrier (PCTC)", "market",
  "Roll-on/roll-off ship with internal decks and ramps for cars, trucks and machinery. PCTC means pure car and truck carrier.",
  "Chinese car exports to Europe have created strong demand for PCTCs.",
  m=["car carrier", "car carriers", "=PCTC", "=PCTCs", "vehicle carrier", "vehicle carriers"])
T("bdi", "Baltic Dry Index (BDI)", "market",
  "Daily index from the Baltic Exchange combining time charter rates for Capesize, Panamax and Supramax bulk carriers. A broad gauge of dry bulk freight levels.",
  "A BDI falling seven days in a row usually reflects weaker Capesize demand, often linked to iron ore.",
  m=["Baltic Dry Index", "=BDI", "Baltic Dry"], core=["freight"])
T("baltic-exchange", "Baltic Exchange", "market",
  "London-based organisation that publishes daily freight assessments and indices for dry bulk and tanker routes, based on brokers' reports. Also used to settle FFAs.",
  "Many index-linked time charters pay the average of the relevant Baltic Exchange routes.",
  m=["Baltic Exchange"])
T("tce", "TCE", "market",
  "Time charter equivalent: a voyage's earnings converted to a daily rate. (Freight − voyage costs such as bunkers, port costs and commission) ÷ voyage days. Lets you compare voyage charters with time charters.",
  "USD 1.32 million net freight minus USD 0.74 million voyage costs over 36 days gives a TCE of about USD 16,100 per day.",
  full="Time charter equivalent", m=["=TCE", "time charter equivalent", "time-charter equivalent", "TCE rate", "TCE rates", "TCE earnings"], core=["freight", "finance"])
T("spot-market", "Spot market", "market",
  "Market for single-voyage deals at today's price. Spot rates react quickly to news, while period rates show where the market expects things to go.",
  "A tanker owner with every ship in the spot market gains most when rates spike, but has no protection when they crash.",
  m=["spot market", "spot markets", "spot rate", "spot rates", "spot freight"], core=["freight"])
T("period-market", "Period market", "market",
  "Time charters lasting months or years. Period rates reflect expectations about future spot rates.",
  "When one-year VLCC charters are fixed above the current spot rate, owners expect the market to strengthen.",
  m=["period market", "period rates", "period rate", "period charter", "period charters", "one-year charter", "1-year charter"])
T("ffa", "FFA", "market",
  "Forward freight agreement: a financial contract to buy or sell freight at an agreed rate for a future period, settled in cash against Baltic Exchange indices. Used to hedge or speculate.",
  "A grain trader worried about higher Panamax rates buys Q1 FFAs at USD 15,000/day. If the index averages USD 18,000, the trader receives the difference.",
  full="Forward freight agreement", m=["=FFA", "=FFAs", "forward freight agreement", "forward freight agreements", "freight derivatives"])
T("ton-miles", "Ton-miles", "market",
  "Cargo volume multiplied by distance sailed. The real measure of shipping demand: longer routes tie up more ships even if cargo volumes stay the same.",
  "Ships diverting around the Cape of Good Hope instead of using Suez sail roughly a third further on Asia–Europe, so ton-mile demand rises without any extra cargo.",
  m=["ton-miles", "ton-mile", "tonne-miles", "tonne-mile", "ton miles", "tonnemiles"], core=["freight"])
T("utilisation", "Fleet utilisation", "market",
  "The share of fleet capacity needed to carry current demand. Above roughly 85–90%, small changes in demand cause large rate spikes because almost no spare ships exist.",
  "That is why freight rates can triple in a few weeks while cargo volumes change only a few percent.",
  m=["fleet utilisation", "fleet utilization", "vessel utilisation", "vessel utilization"])
T("orderbook", "Orderbook", "market",
  "Ships ordered but not yet delivered, often shown as a percentage of the existing fleet. A large orderbook means more supply is coming, which can pressure future rates.",
  "An orderbook of 15% of the fleet delivered over three years adds about 5% supply a year before scrapping.",
  m=["orderbook", "orderbooks", "order book", "orderbook-to-fleet"], core=["freight", "finance"])
T("newbuilding", "Newbuilding", "market",
  "A ship ordered from a shipyard. Paid in instalments during construction and typically delivered two to four years after ordering when yards are busy.",
  "Six tankers ordered now for delivery in 2029–2030 will not add to supply for years.",
  no="Nybygg", m=["newbuilding", "newbuildings", "newbuild", "newbuilds", "nybygg", "nybygging"])
T("sale-purchase", "Sale and purchase (S&P)", "market",
  "The market for buying and selling secondhand ships, handled by S&P brokers. Prices follow earnings, so strong rates make even older ships valuable.",
  "Selling a 2011-built Suezmax at a large book gain shows secondhand prices are high compared with what the owner paid.",
  m=["=S&P", "sale and purchase", "secondhand", "second-hand", "secondhand market", "secondhand prices", "=MOA", "Norwegian Saleform"])
T("recycling", "Ship recycling (demolition)", "market",
  "Selling old ships to yards—mainly in India, Bangladesh, Pakistan and Turkey—that cut them up for steel. Prices are quoted per light displacement tonne (LDT). Strong freight markets mean fewer ships are scrapped.",
  "A ship of 15,000 LDT sold at USD 450 per LDT brings about USD 6.75 million.",
  m=["ship recycling", "recycling markets", "demolition", "scrapping", "scrapped", "=LDT", "light displacement", "cash buyer", "cash buyers"])
T("contango", "Contango", "market",
  "When oil for future delivery costs more than oil today. If the gap is wide enough, traders store oil on tankers (floating storage) to sell later, which takes tankers out of service and lifts rates.",
  "If oil six months ahead is USD 6 per barrel higher, storing 2 million barrels on a VLCC earns USD 12 million before charter and financing costs.",
  m=["contango", "floating storage"])
T("backwardation", "Backwardation", "market",
  "When oil today is more expensive than oil for future delivery. Encourages selling quickly from storage and usually signals a tight market.",
  "Strong backwardation in diesel makes long voyages risky for traders, because the cargo may be worth less on arrival.",
  m=["backwardation", "backwardated"])
T("mean-reversion", "Shipping cycle and mean reversion", "market",
  "Freight rates and ship prices swing in long cycles: high rates bring orders, new ships arrive two to three years later, and rates fall. Because supply eventually adjusts, rates tend to return towards a long-run average (mean reversion). Valuations and lenders assume this rather than today's rate lasting forever.",
  "After a year at USD 80,000 a day, a VLCC owner should not expect that rate for 20 years; a bank values the ship on rates closer to the long-run average.",
  m=["mean reversion", "mean-reverting", "mean reverting", "shipping cycle", "shipping cycles", "market cycle", "freight cycle", "supercycle", "super cycle", "long-run average", "long-term average", "historical average"])
T("term-structure", "Term structure and forward curve", "market",
  "How rates vary with contract length: spot versus one-year, three-year time charter and FFA prices for future months. If period rates are below spot, the market expects rates to fall (backwardation); if above, it expects a rise (contango).",
  "Spot Capesize earns USD 30,000 a day but the one-year time charter is USD 22,000: the curve is in backwardation.",
  m=["term structure", "forward curve", "forward curves", "FFA curve", "one-year time charter", "1-year TC", "one-year TC"])
T("slow-steaming", "Slow steaming", "market",
  "Deliberately sailing slower to save fuel. Fuel use per day rises roughly with the cube of speed, so a 10% speed cut saves about 27% fuel per day (about 19% per voyage, since the trip takes longer). It also reduces effective fleet capacity.",
  "When bunker or emission costs rise, ships slow down. That ties up more ships for the same cargo and can support freight rates.",
  m=["slow steaming", "slow-steaming", "slow down", "speed reduction"])
T("shadow-fleet", "Shadow fleet", "market",
  "Tankers, often old and with unclear ownership and insurance, that carry sanctioned oil (for example Russian, Iranian or Venezuelan) outside Western services. Raises safety, pollution and insurance concerns.",
  "European navies boarding shadow fleet tankers is part of efforts to enforce sanctions at sea.",
  m=["shadow fleet", "shadow-fleet", "dark fleet"], core=["freight", "insurance"])
T("ais", "AIS", "market",
  "Automatic identification system: radio broadcasts of a ship's identity, position, speed and course. Used for safety and tracking. Switching it off ('going dark') is a red flag for sanctions evasion.",
  "Analysts count AIS signals to see how many tankers transit the Strait of Hormuz each day.",
  full="Automatic identification system", m=["=AIS", "going dark", "goes dark", "go dark", "automatic identification system"])
T("chokepoint", "Chokepoint", "market",
  "Narrow sea passage that a large share of world trade must pass: the Strait of Hormuz, Bab el-Mandeb and the Suez Canal, the Panama Canal, the Strait of Malacca and the Bosporus. Disruptions force longer routes or stop trade altogether.",
  "About a fifth of global oil consumption normally passes Hormuz, so attacks there move oil prices and tanker rates at the same time.",
  m=["chokepoint", "chokepoints", "choke point", "choke points", "Strait of Hormuz", "Hormuz", "Bab el-Mandeb", "Bab al-Mandeb", "Bab al-Mandab", "Suez Canal", "Panama Canal", "Red Sea", "Strait of Malacca", "Bosporus"], core=["freight"])
T("bunkers", "Bunkers", "market",
  "Ship fuel. Main grades are VLSFO (very low sulphur fuel oil, max 0.5% sulphur), HSFO (high sulphur fuel, for ships with scrubbers) and MGO (marine gasoil). Fuel is often the largest voyage cost.",
  "A Capesize burning 35 t per day at sea pays about USD 21,000 a day for fuel at USD 600 per tonne.",
  no="Bunkers / skipsdrivstoff", m=["bunker", "bunkers", "bunkering", "bunker prices", "=VLSFO", "=HSFO", "=MGO", "marine fuel", "marine fuels", "ship fuel"], core=["freight"])
T("scrubber", "Scrubber", "market",
  "Exhaust gas cleaning system that lets a ship burn cheaper high-sulphur fuel while meeting sulphur limits. Pays off most when the price gap between VLSFO and HSFO is wide.",
  "With a USD 120 per tonne price gap and 30 t per day consumption, a scrubber saves USD 3,600 a day.",
  m=["scrubber", "scrubbers", "scrubber-fitted"])
T("dwt", "Deadweight (dwt)", "market",
  "How much weight a ship can carry—cargo, fuel, water, stores and crew—in metric tonnes. The usual size measure for bulk carriers and tankers.",
  "A 61,446 dwt Ultramax might load around 58,000 t of cargo after fuel and stores.",
  m=["deadweight", "=dwt", "=DWT"])
T("gt", "Gross tonnage", "market",
  "A measure of a ship's enclosed volume, not its weight. Used for port dues, registration and to decide which rules apply.",
  "The EU emissions trading rules apply to ships of 5,000 gross tonnage and above.",
  m=["gross tonnage"])
T("imo-number", "IMO number", "market",
  "Seven-digit number that permanently identifies a ship, even if it is renamed or reflagged.",
  "Writing 'Lady Mariia (IMO 9220641)' lets readers track the ship in databases even if its name changes later.",
  m=["IMO number", "IMO numbers", "~IMO \\d{7}"])
T("flag-state", "Flag state", "market",
  "The country where a ship is registered; its laws and inspections apply on board. Open registries such as Panama, Liberia and the Marshall Islands register ships from anywhere. Reflagging means moving a ship to another register.",
  "When Panama strikes sanctioned tankers from its register, they lose their flag, which makes insurance and port calls very difficult.",
  m=["flag state", "flag states", "reflag", "reflags", "reflagged", "reflagging", "open registry", "open registries", "flag of convenience", "flags of convenience", "=NIS", "Norwegian International Ship Register", "ship registry"])
T("class-society", "Classification society", "reg",
  "Organisation such as DNV, ABS or Lloyd's Register that sets technical rules for ships, surveys them and issues class certificates. Without class, a ship can't get insurance or finance.",
  "DNV, headquartered at Høvik outside Oslo, is one of the largest classification societies.",
  m=["classification society", "classification societies", "class society", "class societies", "=DNV", "=ABS", "Lloyd's Register", "=ClassNK", "=RINA", "Bureau Veritas"])

# ---------------- SHIP FINANCE ----------------
T("syndicated-loan", "Syndicated loan", "finance",
  "A large loan provided by a group of banks together and arranged by one or more lead banks, so the risk is spread.",
  "A USD 1 billion facility from eight banks to finance 15 containership newbuildings is a syndicated loan.",
  m=["syndicated loan", "syndicated loans", "syndicated loan facility", "loan facility", "credit facility", "bank syndicate"], core=["finance"])
T("sofr", "SOFR", "finance",
  "Secured Overnight Financing Rate: the US dollar benchmark interest rate that replaced LIBOR. Ship loans are usually priced as SOFR plus a margin.",
  "A loan at SOFR + 1.5% costs about 5.5% a year if SOFR is 4%.",
  full="Secured Overnight Financing Rate", m=["=SOFR", "=LIBOR"], core=["finance"])
T("basis-point", "Basis point (bp)", "finance",
  "One hundredth of a percentage point (0.01%). Loan margins and rate changes are quoted in basis points.",
  "A margin 550 bp lower saves USD 5.5 million a year for every USD 100 million borrowed.",
  m=["basis point", "basis points", "=bp", "=bps", "loan margin", "interest margin"])
T("nibor", "NIBOR", "finance",
  "Norwegian interbank offered rate: the NOK benchmark used for floating-rate loans and bonds in Norway.",
  "A Nordic bond paying NIBOR + 5% pays about 9% a year if NIBOR is 4%.",
  m=["=NIBOR"])
T("ltv", "LTV", "finance",
  "Loan-to-value: the loan as a percentage of the ship's market value. Ship loans often start around 50–65% LTV. If ship values fall, the borrower may have to repay early or add security.",
  "A USD 30 million loan on a ship worth USD 50 million is 60% LTV.",
  full="Loan-to-value", m=["=LTV", "loan-to-value", "loan to value"], core=["finance"])
T("vmc", "Minimum value clause (MVC)", "finance",
  "Loan covenant requiring the ship's market value to stay above a set percentage of the loan, often 125–135%. It is the mirror image of a maximum LTV: a 135% clause means the loan may be at most about 74% of the ship's value. If values fall below the level, the owner must prepay part of the loan or add security within a short deadline.",
  "A USD 21 million loan with a 135% clause requires the ship to be worth at least USD 28.4 million. Bought at USD 35 million, the ship can lose about 19% of its value before the clause is breached.",
  full="Also called value maintenance clause or security cover", m=["minimum value clause", "minimum value covenant", "value maintenance clause", "security cover", "asset cover", "collateral maintenance", "=VMC", "=MVC"], core=["finance"])
T("covenant", "Covenant", "finance",
  "A promise in a loan agreement, such as minimum cash, maximum leverage or value maintenance. Breaching one lets the lender demand repayment.",
  "In a weak market, owners may ask their banks for a covenant waiver to avoid a default.",
  m=["covenant", "covenants", "covenant waiver"])
T("balloon", "Balloon", "finance",
  "The large final repayment when a loan matures, because the instalments did not repay all of it. Usually refinanced or paid by selling the ship.",
  "A seven-year loan of USD 40 million repaying USD 3 million a year leaves a USD 19 million balloon.",
  m=["balloon", "balloon payment", "balloon repayment"])
T("sale-leaseback", "Sale and leaseback", "finance",
  "The owner sells the ship to a financier—often a Chinese leasing company—and charters it back on bareboat terms, usually with options or an obligation to buy it back. An alternative to bank loans.",
  "An owner raises USD 25 million by selling a ship to a lessor and paying bareboat hire for eight years.",
  m=["sale and leaseback", "sale-and-leaseback", "sale-leaseback", "leaseback", "Chinese leasing", "lessor", "lessors", "leasing house"], core=["finance"])
T("ks", "KS (limited partnership)", "finance",
  "Norwegian partnership structure used to fund single ships with equity from many investors plus a bank loan. Widely used in Norwegian shipping booms.",
  "Investors buy units in a single-ship KS that owns one vessel on charter, and the income flows to the partners.",
  no="Kommandittselskap", m=["kommandittselskap", "kommandittselskaper"])
T("bond", "Nordic high-yield bond", "finance",
  "Bonds issued by shipping and offshore companies in the Oslo bond market, often three to five years with floating rates. Faster and more flexible than bank loans, but more expensive. Project bonds are tied to one asset or contract.",
  "An offshore company issues a USD 200 million bond at SOFR + 6% to refinance its vessels.",
  m=["Nordic bond", "Nordic bonds", "high-yield bond", "high yield bond", "bond issue", "project bond", "bond loan", "obligasjonslån", "bond"], core=["finance"])
T("private-placement", "Private placement", "finance",
  "Selling new shares directly to selected investors, common on Euronext Oslo. Quicker than a public offering, but dilutes existing shareholders.",
  "A tanker company raises NOK 500 million in a private placement to pay yard instalments.",
  no="Rettet emisjon", m=["private placement", "private placements", "rettet emisjon", "emisjon", "share issue", "equity raise"])
T("nav", "NAV", "finance",
  "Net asset value: the market value of a shipping company's fleet minus net debt, per share. Comparing the share price with NAV (P/NAV) shows whether the stock is cheap or expensive compared with its ships.",
  "Fleet worth USD 2 billion, net debt USD 0.8 billion and 100 million shares give a NAV of USD 12 per share. A share price of USD 10 is a 17% discount.",
  full="Net asset value", m=["=NAV", "=P/NAV", "net asset value"], core=["finance"])
T("ebitda", "EBITDA", "finance",
  "Earnings before interest, tax, depreciation and amortisation. In shipping, roughly what the ships earn minus operating and administration costs: a measure of cash generated before financing.",
  "TCE income USD 100 million − OPEX USD 35 million − G&A USD 5 million = EBITDA of USD 60 million.",
  m=["=EBITDA"])
T("opex", "OPEX", "finance",
  "Operating expenses: the daily cost of running a ship—crew, maintenance, insurance, stores and lubricants. Fuel is a voyage cost, not OPEX. Roughly USD 6,000–10,000 per day depending on size and type.",
  "A Supramax with OPEX of USD 6,500 per day must earn at least that just to keep running.",
  full="Operating expenses", m=["=OPEX", "=opex", "=Opex", "operating expenses", "running costs", "vessel operating costs"], core=["finance"])
T("breakeven", "Cash breakeven", "finance",
  "The daily rate a ship must earn to cover OPEX, overhead, interest and loan repayments. Above it the ship generates free cash; below it the owner burns cash.",
  "OPEX 7,000 + overhead 1,000 + interest 3,000 + repayments 5,000 = a cash breakeven of USD 16,000 per day.",
  m=["breakeven", "break-even", "cash breakeven", "breakeven rate", "breakeven level"], core=["finance"])
T("refund-guarantee", "Refund guarantee", "finance",
  "Guarantee from the shipyard's bank that the buyer gets its instalments back if the yard fails to deliver. Buyers require it before paying instalments.",
  "If a yard goes bankrupt halfway through a build, the refund guarantee returns the buyer's USD 20 million paid so far.",
  m=["refund guarantee", "refund guarantees"])
T("charter-backed", "Charter-backed financing", "finance",
  "Loans based on a long time charter with a strong charterer. The secure income lowers the lender's risk and the margin.",
  "Because all its newbuildings have long time charters from delivery, a containership owner can borrow at a low margin.",
  m=["charter-backed", "charter backed", "contracted revenue", "charter coverage"])
T("poseidon", "Poseidon Principles", "finance",
  "Framework in which shipping banks measure and report how well their loan portfolios align with IMO climate targets.",
  "A bank that has signed may offer better terms on ships with lower carbon intensity.",
  m=["Poseidon Principles"])
T("eca", "ECA", "finance",
  "Two meanings. (1) Export credit agency: a state agency, such as Eksfin in Norway or KEXIM in Korea, that lends or guarantees to support exports, often for newbuildings. (2) Emission control area: sea areas such as the North Sea and the Baltic with stricter limits on sulphur and NOx emissions.",
  "If the article is about financing, it means the agency. If it is about fuel or sulphur, it means the emission area.",
  m=["=ECA", "=ECAs", "export credit agency", "export credit", "emission control area", "emission control areas", "=SECA", "=Eksfin"])
T("book-gain", "Book gain", "finance",
  "Profit when a ship is sold for more than its depreciated value in the accounts. Common when secondhand prices are high.",
  "Selling a ship carried at USD 20 million for USD 80 million gives a USD 60 million gain.",
  m=["book gain", "capital gain", "capital gains"])
T("impairment", "Impairment", "finance",
  "Writing down a ship's value in the accounts when expected earnings or market values fall below the carrying value. A loss on paper, with no cash leaving the company.",
  "An offshore company impairs its PSV fleet by USD 100 million after a weak market outlook.",
  m=["impairment", "impairments", "write-down", "write-downs"])
T("asset-play", "Asset play", "finance",
  "Buying ships when prices are low to sell when values rise, rather than profiting mainly from operating them.",
  "Buying 10-year-old bulkers at the bottom of a cycle and selling two years later can earn more than the freight they carried.",
  m=["asset play", "asset plays"])
T("dividend", "Dividend yield", "finance",
  "Annual dividends as a percentage of the share price. Many listed shipping companies pay out most of their free cash, so yields swing with freight markets.",
  "A tanker share at NOK 100 paying NOK 12 over the year has a 12% dividend yield.",
  m=["dividend yield", "dividend yields", "dividend payout", "payout ratio"])

T("five-cs", "Five Cs of credit", "finance",
  "The checklist banks use to judge a borrower: character (track record, reputation and management), capacity (cash flow to service the debt), capital (equity in the company and the deal), collateral (the ship, assignments of charters and insurances) and covenants (the promises that let the bank act early). Some versions replace covenants with conditions (the market).",
  "A bank may lend to a well-known owner with a 20-year record at a lower margin than to a new company with the same ship, because character and capital are stronger.",
  m=["five Cs", "5 Cs", "credit analysis", "credit assessment", "credit committee", "credit approval"], core=["finance"])
T("ltav", "Long-term asset value (LTAV)", "finance",
  "A ship's fundamental value: the present value of its expected earnings (charter income minus OPEX) over the rest of its life, plus scrap value, discounted at the cost of capital. Rates are assumed to move from today's level towards a long-run average. Lenders use it to look through short-term swings in market prices.",
  "A 10-year-old feeder earning USD 7,500 a day today, with rates returning to USD 13,000 and a WACC of 6.75%, has an LTAV of about USD 15.5 million (the textbook example).",
  m=["=LTAV", "long-term asset value", "long term asset value", "fundamental value", "fundamental values", "intrinsic value", "discounted cash flow", "=DCF"], core=["finance"])
T("wacc", "WACC", "finance",
  "Weighted average cost of capital: the blended return required by lenders and shareholders, weighted by how much of each is used. It is the discount rate in a ship or company valuation. Cost of equity is often estimated with CAPM.",
  "60% debt at 6.3% and 40% equity at 7.4% give a WACC of about 6.75%.",
  full="Weighted average cost of capital", m=["=WACC", "weighted average cost of capital", "cost of capital", "cost of equity", "cost of debt", "required return"])
T("dscr", "Debt service cover (DSCR)", "finance",
  "Cash flow available for debt service divided by interest plus instalments. Banks often want at least 1.2–1.4. A related bond covenant is interest cover: (TCE income − OPEX) divided by interest only.",
  "A ship generating USD 5.8 million a year with USD 2.3 million of interest and repayments has a DSCR of about 2.5.",
  full="Debt service cover ratio", m=["=DSCR", "debt service cover", "debt service coverage", "debt service coverage ratio", "interest cover", "interest coverage", "interest coverage ratio"])
T("nibd-ebitda", "NIBD/EBITDA", "finance",
  "Net interest-bearing debt divided by EBITDA: how many years of cash earnings it would take to repay the debt. A common leverage covenant in bonds and loans; above about 4–5 is usually seen as high in shipping.",
  "Net debt of USD 600 million and EBITDA of USD 150 million give NIBD/EBITDA of 4.0.",
  m=["=NIBD", "net interest-bearing debt", "net interest bearing debt", "net debt to EBITDA", "net debt/EBITDA", "leverage ratio"])
T("pd-lgd", "PD and LGD", "finance",
  "Probability of default (how likely the borrower is to fail) and loss given default (how much the lender loses if it does, after selling the ship). Expected loss = PD × LGD × exposure. Banks price loans and set capital by these numbers, so a lower LTV (lower LGD) gives a lower margin.",
  "A 2% PD and 30% LGD on a USD 50 million loan give an expected loss of USD 0.3 million a year.",
  m=["probability of default", "loss given default", "=LGD", "expected credit loss", "expected credit losses", "expected loss"])
T("maritime-lien", "Maritime lien and ship arrest", "finance",
  "Some claims attach to the ship itself and rank ahead of the bank's mortgage: crew wages, salvage, port and canal dues, and personal injury or damage caused by the ship. A creditor can have the ship arrested in port until the claim is paid or secured. This is why lenders check that wages and dues are paid.",
  "If an owner stops paying crew and port dues, the ship can be arrested and sold by the court, with the crew paid before the bank.",
  no="Sjøpanterett", m=["maritime lien", "maritime liens", "sjøpanterett", "vessel arrest", "arrest of the ship", "arrest of the vessel", "arrested ship", "arrested vessel", "arrested vessels", "judicial sale"])
T("default", "Event of default", "finance",
  "A breach listed in the loan agreement—a missed payment, a covenant breach, insolvency or a material adverse change—that lets the lender cancel the loan and demand repayment. A cross-default clause makes a default on one loan count as a default on others.",
  "Missing one instalment on a ship loan can, through cross-default, put the owner in default on its bonds as well.",
  m=["event of default", "events of default", "cross-default", "cross default", "payment default", "defaulted", "default on", "in default", "missed payment", "missed coupon", "covenant breach"])
T("restructuring", "Restructuring", "finance",
  "Changing a company's debt when it cannot pay as agreed. Steps range from a standstill (lenders agree not to act for a period) and forbearance (they tolerate a breach) to amend-and-extend, haircuts and a debt-for-equity swap where lenders become owners. In Norway it can be done out of court or through rekonstruksjon.",
  "Bondholders agree to postpone interest for 18 months and convert part of their claims into shares, leaving old shareholders with 10% of the company.",
  no="Rekonstruksjon", m=["restructuring", "debt restructuring", "financial restructuring", "standstill", "standstill agreement", "forbearance", "debt-for-equity", "debt for equity", "debt-to-equity swap", "amend and extend", "amend-and-extend", "haircut", "rekonstruksjon"], core=["finance"])
T("chapter-11", "Chapter 11", "finance",
  "US court-supervised reorganisation that lets a company keep operating while it restructures its debts, protected from creditors. New money is often provided as DIP (debtor-in-possession) financing, which ranks first. Seadrill went through Chapter 11 twice (2017 and 2021).",
  "An offshore driller files for Chapter 11 in Texas, keeps its rigs working, and exits a year later with lower debt and new owners.",
  m=["Chapter 11", "Chapter 15", "debtor-in-possession", "debtor in possession", "=DIP", "bankruptcy protection", "creditor protection"])
T("loan-types", "Term loan, RCF and repayment profiles", "finance",
  "A term loan is drawn once and repaid by instalments. A revolving credit facility (RCF) can be drawn, repaid and redrawn. Repayment can be even, front-ended, back-ended, or start after a moratorium, and the profile is often longer than the tenor, which leaves a balloon.",
  "A 7-year loan on a 20-year profile repays 5% a year, so 65% is still outstanding when it matures.",
  m=["term loan", "term loans", "revolving credit facility", "revolving credit facilities", "=RCF", "revolver", "repayment profile", "amortisation profile", "tenor", "moratorium"])
T("capital-structure", "Capital structure", "finance",
  "The mix of debt and equity a company uses. Modigliani–Miller says it does not matter in a perfect market; trade-off theory weighs tax savings against the cost of financial distress; pecking order says firms prefer internal cash, then debt, then new shares. Volatile shipping earnings argue for moderate debt.",
  "A shipowner that paid down debt in a strong market and kept cash is better placed to buy cheap ships in the next downturn.",
  m=["capital structure", "pecking order", "trade-off theory", "Modigliani-Miller", "Modigliani–Miller", "deleveraging", "deleverage"])
T("mezzanine", "Mezzanine finance", "finance",
  "Capital ranking between senior bank debt and equity, such as junior loans, preferred equity or second-lien bonds. It costs more than bank debt but lets the owner use less equity. A typical stack could be 40–55% senior debt, 15–25% mezzanine and the rest equity.",
  "A buyer funds a USD 40 million ship with USD 20 million senior loan, USD 8 million mezzanine at 12% and USD 12 million equity.",
  m=["mezzanine", "junior debt", "junior loan", "subordinated", "second lien", "second-lien", "preferred equity", "preference shares", "hybrid capital", "hybrid bond"])
T("convertible", "Convertible bond", "finance",
  "A bond the holder can exchange for shares at a set conversion price. Investors accept a lower coupon in return for the upside if the shares rise; for the company it is cheaper debt now and possible dilution later.",
  "A driller issues a USD 250 million convertible at 5.75% with a conversion price 30% above today's share price.",
  m=["convertible bond", "convertible bonds", "convertible notes", "convertible loan", "conversion price", "convertibles"])
T("lease", "Finance and operating lease", "finance",
  "A finance lease transfers most of the risk and reward of owning the ship to the lessee (often with a purchase obligation); an operating lease is closer to renting. Under IFRS 16 lessees put almost all leases longer than 12 months on the balance sheet as a right-of-use asset and a lease liability.",
  "After a sale-leaseback with a buy-back obligation, the seller usually keeps the ship on its balance sheet as a financing, not a sale.",
  m=["finance lease", "financial lease", "operating lease", "operating leases", "=IFRS 16", "lease liability", "lease liabilities", "right-of-use", "lease financing", "bareboat lease"])
T("bond-trustee", "Bond trustee", "finance",
  "Represents all bondholders: checks covenants, calls bondholder meetings and acts if the issuer defaults. Nordic Trustee fills this role in most Nordic bonds. Bondholders can vote on changes, so a restructuring needs a majority.",
  "Nordic Trustee summons a bondholder meeting to vote on deferring the next two interest payments.",
  m=["bond trustee", "Nordic Trustee", "bondholder meeting", "bondholders' meeting", "written resolution", "bondholders", "bond terms"])
T("credit-rating", "Credit rating (investment grade vs high yield)", "finance",
  "An agency's opinion of how likely an issuer is to pay. BBB− and above is investment grade; below that is high yield, with higher interest. Recovery ratings estimate how much lenders get back after a default. Most shipping bonds are unrated or high yield.",
  "An upgrade from BB to BBB− lets a company sell bonds to investors who may only buy investment grade, often cutting its interest cost.",
  m=["credit rating", "credit ratings", "investment grade", "investment-grade", "high yield", "high-yield", "junk bond", "rating downgrade", "rating upgrade", "recovery rating", "=Moody's", "Fitch Ratings", "S&P Global Ratings"])
T("swap", "Interest rate swap", "finance",
  "An agreement to exchange floating interest payments for fixed ones (or the reverse). Owners with SOFR loans use swaps, caps and collars to limit how much higher rates can cost them. A cross-currency swap also exchanges currencies, for example NOK bond payments into USD.",
  "An owner with a USD 100 million SOFR loan swaps it to a fixed 4%, so a rise in SOFR no longer raises its interest bill.",
  m=["interest rate swap", "interest rate swaps", "interest rate hedge", "interest rate hedging", "swap rate", "fixed-for-floating", "interest rate cap", "rate cap", "collar", "cross-currency swap", "cross currency swap", "currency swap", "currency swaps"])
T("mna", "Mergers and synergies", "finance",
  "When two shipping companies combine, the deal makes sense if the combined value exceeds the parts: value created = synergies (lower costs, better fleet use) minus the premium paid to the target's shareholders. Many shipping deals are all-share mergers.",
  "A buyer pays a 20% premium for a USD 1 billion target. The deal creates value only if synergies are worth more than USD 200 million.",
  m=["merger", "mergers", "takeover", "takeovers", "takeover bid", "offer premium", "bid premium", "all-share", "share-for-share", "tender offer", "synergies", "fusjon", "oppkjøp"])
T("ipo", "IPO and listing", "finance",
  "An initial public offering sells shares to the public and lists the company on a stock exchange, such as Euronext Oslo (Oslo Børs), Euronext Growth or the New York exchanges. It raises equity and makes shares tradable; many shipping IPOs come when rates and valuations are high.",
  "A tanker owner lists on Euronext Growth Oslo, raising USD 150 million to pay for newbuildings.",
  m=["=IPO", "=IPOs", "initial public offering", "Euronext Growth", "Euronext Oslo", "Oslo Børs", "Oslo Stock Exchange", "Euronext Expand", "stock listing", "dual listing", "børsnotering"])
T("beta", "Beta and CAPM", "finance",
  "Beta measures how much a share moves with the overall stock market. In CAPM, cost of equity = risk-free rate + beta × market risk premium. Shipping betas are often near or above 1 and rise in bad markets. The Sharpe ratio compares return with volatility.",
  "With a 4% risk-free rate, beta 1.2 and a 5% market premium, the cost of equity is 10%.",
  m=["equity beta", "stock beta", "=CAPM", "Sharpe ratio", "risk-adjusted return", "risk-adjusted returns", "market risk premium", "systematic risk"])
T("tonnage-tax", "Tonnage tax", "finance",
  "A tax regime where shipping companies pay a small tax based on fleet size (net tonnage) instead of tax on profits. Norway and most EU countries offer it. That is why ship valuations are often done before tax.",
  "A Norwegian owner earning USD 100 million pays tonnage tax measured in thousands of kroner per ship, not 22% of profit.",
  no="Rederiskatt / tonnasjeskatt", m=["tonnage tax", "tonnage taxation", "tonnasjeskatt", "rederiskatt", "rederiskatteordningen"])
T("cirr", "Export credit rules (OECD, CIRR)", "finance",
  "Export credit agencies follow the OECD Arrangement and its Ship Sector Understanding: up to 80% of the contract price, repaid over up to 12 years, and often at a fixed CIRR rate (commercial interest reference rate). Commercial banks usually provide a share alongside. In Norway, Eksfin offers loans and guarantees for ships built at Norwegian yards or with Norwegian equipment.",
  "An owner ordering an offshore vessel in Norway finances 80% with an Eksfin-guaranteed loan over 12 years and pays 20% from equity.",
  m=["=CIRR", "OECD Arrangement", "Ship Sector Understanding", "commercial interest reference rate", "Export Finance Norway", "eksportkreditt", "export credit guarantee", "export credit guarantees"])
T("sll", "Sustainability-linked loan", "finance",
  "A loan whose margin goes up or down, often by a few basis points, depending on whether the borrower hits agreed sustainability targets, such as carbon intensity. A green loan or green bond instead restricts what the money can be used for.",
  "A margin of SOFR + 1.80% falls by 0.05% if the fleet meets its CO2 target and rises by 0.05% if it does not.",
  m=["sustainability-linked", "sustainability linked", "=SLL", "green loan", "green loans", "green bond", "green bonds", "green financing", "green finance", "blue bond", "social bond", "transition finance"])
T("stranded-asset", "Stranded asset and transition risk", "finance",
  "Transition risk is the chance that climate rules, carbon prices or charterer demands cut the value of existing ships. A ship becomes a stranded asset if it loses value or earnings long before the end of its expected life. The risk is relative: an older, less efficient ship loses against newer ones even if all ships still trade.",
  "If fuel rules make a 15-year-old ship USD 4,000 a day more expensive to run than a dual-fuel newbuilding, charterers pay less for it and its value falls.",
  m=["stranded asset", "stranded assets", "stranding", "transition risk", "transition risks", "climate risk", "climate risks", "climate-related risk", "physical risk"])

# ---------------- MARINE INSURANCE ----------------
T("hm", "Hull & Machinery (H&M)", "insurance",
  "Insurance for physical damage to or loss of the ship itself: hull, engine and equipment. Under the Nordic Marine Insurance Plan it also covers collision liability.",
  "If a ship grounds and damages its propeller, the repair cost above the deductible is a hull claim.",
  no="Kaskoforsikring", m=["=H&M", "hull and machinery", "hull & machinery", "hull insurance", "hull insurer", "hull insurers", "hull claim", "hull claims", "kaskoforsikring", "kasko", "Marine Hull"], core=["insurance"])
T("pi", "P&I", "insurance",
  "Protection and indemnity: insurance for the shipowner's liabilities to others—crew injury, pollution, wreck removal, cargo damage and collision damage not covered by hull insurance. Mostly provided by mutual P&I clubs.",
  "When a ship spills oil after a grounding, the clean-up cost is typically a P&I claim.",
  full="Protection and indemnity", m=["=P&I", "protection and indemnity", "protection & indemnity"], core=["insurance"])
T("pi-club", "P&I club", "insurance",
  "Mutual insurance association owned by its shipowner members. Members pay premiums (calls) and share each other's claims; large claims are pooled between clubs.",
  "Gard in Arendal and Skuld in Oslo are Norwegian P&I clubs.",
  m=["P&I club", "P&I clubs", "=P&I Club", "mutual insurer", "mutual insurers", "=Gard", "=Skuld", "Steamship Mutual", "NorthStandard", "UK P&I", "Swedish Club", "West of England", "American Club", "Japan P&I"], core=["insurance"])
T("ig", "International Group of P&I Clubs (IG)", "insurance",
  "The group of the largest P&I clubs, together insuring around 90% of the world's ocean-going tonnage and sharing large claims through a pool and a joint reinsurance programme.",
  "A 'non-IG' club is one outside this group. It may be cheaper, but some ports and charterers demand IG cover.",
  m=["International Group", "=IG club", "=IG clubs", "=non-IG", "=IG"])
T("call", "Call (P&I premium)", "insurance",
  "The premium a P&I club member pays. The advance call is paid up front; a general increase raises all members' calls for the coming policy year, which renews on 20 February.",
  "A 5% general increase on an annual call of USD 300,000 adds USD 15,000.",
  m=["advance call", "general increase", "supplementary call", "release call", "P&I renewal"])
T("deductible", "Deductible", "insurance",
  "The part of each claim the insured pays before the insurance pays. Higher deductibles mean lower premiums.",
  "With a USD 150,000 deductible, a USD 400,000 engine damage gives an insurance payout of USD 250,000.",
  no="Egenandel", m=["deductible", "deductibles", "egenandel"])
T("war-risk", "War risk insurance", "insurance",
  "Covers the ship against war, terrorism, piracy, mines and similar perils that ordinary hull and P&I policies exclude. For high-risk listed areas, insurers charge an additional premium per voyage, often as a percentage of the ship's value.",
  "An additional premium of 1% on a USD 100 million tanker costs USD 1 million for one call in a listed area.",
  no="Krigsforsikring", m=["war risk", "war risks", "war-risk", "war risk insurance", "war-risk insurance", "war risk premium", "war risk premiums", "additional premium", "additional premiums", "krigsforsikring", "=DNK"], core=["insurance"])
T("listed-areas", "Listed areas (JWC)", "insurance",
  "High-risk sea areas listed by the Joint War Committee of the London insurance market. Entering one usually means notifying war risk insurers and paying an additional premium.",
  "Parts of the Gulf, the Red Sea and the Black Sea have been listed areas in recent years.",
  m=["listed area", "listed areas", "Joint War Committee", "=JWC"])
T("loh", "Loss of hire (LOH)", "insurance",
  "Covers the owner's lost income when the ship is out of service after damage covered by hull insurance, after a waiting period such as 14 days.",
  "A ship idle for 44 days after a fire, with a 14-day deductible and USD 20,000 per day insured, receives USD 600,000.",
  m=["loss of hire", "=LOH"])
T("iv", "Increased value (IV)", "insurance",
  "Additional insurance that pays on a total loss, covering the gap between the hull's insured value and the owner's real loss.",
  "A ship insured at USD 40 million for hull plus USD 10 million IV pays out USD 50 million if it is lost.",
  m=["increased value"])
T("mii", "Mortgagee's interest insurance (MII)", "insurance",
  "Insurance bought by (or for) the lending bank that pays if the owner's own insurance fails to pay, for example because the owner breached a warranty or concealed something. It protects the bank's loan, not the owner. MAP (additional perils) covers pollution liabilities the bank could face.",
  "A ship sinks but the hull insurer refuses to pay because the owner broke a trading warranty. The bank's MII pays up to the outstanding loan.",
  m=["mortgagee's interest", "mortgagees interest", "mortgagee interest", "=MII", "=MAPI", "=MAP cover", "lender's insurance"])
T("fdd", "FD&D", "insurance",
  "Freight, demurrage and defence: legal-costs insurance, often from P&I clubs, for disputes about charter parties, freight, demurrage and shipbuilding contracts.",
  "An owner disputing a USD 200,000 demurrage claim has its lawyers paid by its FD&D cover.",
  full="Freight, demurrage and defence", m=["=FD&D", "freight, demurrage and defence", "defence cover"])
T("ga", "General average", "insurance",
  "Old principle of shared sacrifice: when ship or cargo is deliberately sacrificed, or extra costs are paid to save the whole voyage (salvage, port of refuge), all parties share the loss in proportion to their values. Governed by the York-Antwerp Rules.",
  "After an engine-room fire, the ship is towed to port. Cargo owners must post general average security before they get their containers.",
  m=["general average", "York-Antwerp Rules", "York Antwerp Rules", "general average declared"], core=["insurance"])
T("salvage", "Salvage", "insurance",
  "Help to a ship in danger from a third party, usually rewarded under 'no cure, no pay' on Lloyd's Open Form (LOF). The reward depends on the values saved and the effort; SCOPIC adds payment for protecting the environment.",
  "A tug that saves a USD 50 million ship and cargo may earn a reward of several million dollars.",
  m=["salvage", "salvor", "salvors", "Lloyd's Open Form", "=LOF", "=SCOPIC", "port of refuge"])
T("total-loss", "Total loss", "insurance",
  "Actual total loss: the ship is destroyed or lost. Constructive total loss (CTL): repairs would cost more than the ship is worth, so insurers pay the insured value instead.",
  "A burned car carrier whose repairs are estimated above its value is declared a constructive total loss.",
  m=["total loss", "total losses", "constructive total loss", "actual total loss", "=CTL"])
T("nordic-plan", "Nordic Marine Insurance Plan", "insurance",
  "Standard conditions for hull, loss of hire and war risk insurance used by Nordic insurers and maintained by Cefor. It differs from English clauses—for example, collision liability sits under hull cover.",
  "Norwegian Hull Club, based in Bergen, is one of the insurers writing hull cover on the Nordic Plan.",
  m=["Nordic Plan", "Nordic Marine Insurance Plan", "Norwegian Plan", "=Cefor", "Norwegian Hull Club"], core=["insurance"])
T("lloyds", "Lloyd's of London", "insurance",
  "The London insurance market where syndicates underwrite risks, including a large share of the world's marine, war and specialty insurance.",
  "War risk cover for a tanker heading into the Gulf is often placed with Lloyd's syndicates.",
  m=["Lloyd's of London", "Lloyd's market", "Lloyd's syndicate", "Lloyd's syndicates"])
T("underwriter", "Underwriter", "insurance",
  "The insurer's specialist who assesses a risk and sets premium and terms; also used for the insurer itself.",
  "After several groundings in a fleet, the hull underwriter raises the deductible at renewal.",
  m=["underwriter", "underwriters", "underwriting"])
T("insurance-broker", "Insurance broker", "insurance",
  "Represents the shipowner when buying insurance: places the risk with underwriters and helps with claims. Large marine brokers include Howden, Lockton, Marsh and Tysers.",
  "A broker shops a fleet's hull renewal across Nordic, London and Asian markets to find the best price.",
  m=["insurance broker", "insurance brokers", "=Howden", "=Lockton", "=Marsh", "=Tysers"])
T("reinsurance", "Reinsurance", "insurance",
  "Insurance for insurers: they pass part of their risk to reinsurers so one large loss does not break them.",
  "A hull insurer covering a USD 300 million LNG carrier may keep USD 50 million of the risk and reinsure the rest.",
  m=["reinsurance", "reinsurer", "reinsurers", "reinsured"])
T("cargo-insurance", "Cargo insurance", "insurance",
  "Covers the cargo owner against loss or damage in transport, usually on the Institute Cargo Clauses: (A) all risks, (B) and (C) named perils only. Needed because carriers' liability is limited.",
  "Under CMR a haulier may pay only about NOK 110,000 for a lost one-tonne pallet. Cargo insurance covers the real value.",
  no="Vareforsikring / transportforsikring", m=["cargo insurance", "cargo insurer", "cargo insurers", "Institute Cargo Clauses", "vareforsikring", "transportforsikring"])
T("subrogation", "Subrogation", "insurance",
  "After paying a claim, the insurer takes over the insured's right to recover the money from whoever caused the loss.",
  "A cargo insurer pays the cargo owner, then claims the money from the carrier under CMR or the bill of lading.",
  no="Regress", m=["subrogation", "subrogated", "regress", "recourse claim"])
T("seaworthiness", "Seaworthiness", "insurance",
  "A ship's fitness for the voyage: hull, equipment, crew, documents and cargo stowage. Unseaworthiness can remove insurance cover or make the carrier liable.",
  "Sending a ship to sea with an untrained crew can make it unseaworthy even if the hull is perfect.",
  no="Sjødyktighet", m=["seaworthiness", "seaworthy", "unseaworthy", "unseaworthiness", "sjødyktighet", "sjødyktig"])
T("combined-ratio", "Combined ratio", "insurance",
  "Claims plus costs divided by premiums. Below 100% the insurer makes an underwriting profit; above 100% it loses money before investment income.",
  "Premiums of 100, claims of 80 and costs of 15 give a combined ratio of 95%.",
  m=["combined ratio", "combined ratios", "loss ratio", "loss ratios"])
T("loi", "Letter of indemnity (LOI)", "insurance",
  "A guarantee given to the carrier so it delivers cargo without the original bill of lading, or at a different port. Risky for the owner, because P&I cover may not apply to such deliveries.",
  "The receiver wants its cargo before the original B/L arrives from the bank, so the charterer issues an LOI to the owner.",
  m=["letter of indemnity", "letters of indemnity", "=LOI", "=LOIs"])
T("lou", "Club letter of undertaking (LOU)", "insurance",
  "A guarantee from a P&I club to a claimant that a claim will be paid if proven, so the ship avoids arrest or is released.",
  "A ship arrested in port after a cargo claim is released once the P&I club issues an LOU.",
  m=["letter of undertaking", "=LOU", "=LOUs", "ship arrest", "arrested"])
T("sanctions", "Sanctions", "reg",
  "Restrictions imposed by the US, EU, UK, UN or Norway on trading with certain countries, companies or ships. Insurers, banks and charterers screen against sanctions lists, and dealing with a sanctioned party can void insurance and financing.",
  "When the US sanctions a tanker, its insurers usually cancel cover and many ports refuse it entry.",
  no="Sanksjoner", m=["sanctions", "sanctioned", "sanktioner", "sanksjoner", "=OFAC", "price cap", "oil price cap"], core=["insurance"])

# ---------------- OFFSHORE ----------------
T("psv", "PSV", "offshore",
  "Platform supply vessel: carries supplies such as pipes, chemicals, fuel, water and food between supply bases and offshore installations. Sized by deck area.",
  "PSVs shuttle from bases such as CCB Ågotnes near Bergen to fields in the North Sea.",
  full="Platform supply vessel", m=["=PSV", "=PSVs", "platform supply vessel", "platform supply vessels", "supply vessel", "supply vessels"], core=["offshore"])
T("ahts", "AHTS", "offshore",
  "Anchor handling tug supply vessel: powerful ship that tows rigs and handles their anchors. Sized by bollard pull in tonnes.",
  "Moving a semi-submersible rig between fields can require two or three AHTS vessels.",
  full="Anchor handling tug supply vessel", m=["=AHTS", "anchor handling", "anchor handler", "anchor handlers", "bollard pull"])
T("csov", "CSOV / SOV", "offshore",
  "(Commissioning) service operation vessel: houses technicians at offshore wind farms for weeks and gets them safely onto turbines via a motion-compensated gangway (walk-to-work).",
  "A CSOV with 120 beds can keep a commissioning team offshore without daily crew-boat trips.",
  full="(Commissioning) service operation vessel", m=["=CSOV", "=CSOVs", "=SOV", "=SOVs", "service operation vessel", "service operation vessels", "walk-to-work", "=W2W"], core=["offshore"])
T("csv", "Subsea construction vessel (CSV)", "offshore",
  "Large vessel with cranes, ROVs and deck space for installing and maintaining subsea equipment. Many also do inspection, maintenance and repair (IMR) work.",
  "A CSV installs a new manifold on the seabed and connects it to existing pipelines.",
  m=["subsea construction vessel", "subsea construction vessels", "=CSV", "=IMR", "inspection, maintenance and repair"])
T("fpso", "FPSO", "offshore",
  "Floating production, storage and offloading unit: a ship-shaped unit that produces oil from subsea wells, stores it and offloads it to shuttle tankers. Often leased from specialists such as SBM Offshore, Yinson or BW Offshore on long contracts.",
  "The Johan Castberg field in the Barents Sea produces through an FPSO.",
  full="Floating production, storage and offloading unit", m=["=FPSO", "=FPSOs", "floating production", "shuttle tanker", "shuttle tankers"], core=["offshore"])
T("fsru", "FSRU / FLNG", "offshore",
  "FSRU: floating storage and regasification unit, an LNG ship that turns LNG back into gas for a country's grid. FLNG: floating liquefaction unit that produces LNG offshore.",
  "Germany used FSRUs to start importing LNG quickly after 2022.",
  m=["=FSRU", "=FSRUs", "=FLNG", "floating LNG", "regasification"])
T("lng", "LNG", "offshore",
  "Liquefied natural gas: natural gas cooled to about −162 °C so it becomes liquid and takes about 600 times less space, so it can be shipped by sea. Also used as ship fuel.",
  "Norwegian gas mostly reaches Europe by pipeline, but Hammerfest LNG ships it as LNG.",
  full="Liquefied natural gas", m=["=LNG", "liquefied natural gas"])
T("rig", "Drilling rig types", "offshore",
  "Mobile offshore drilling units (MODUs): jack-ups stand on legs in shallow water; semi-submersibles float on pontoons and suit harsh areas such as the Norwegian shelf; drillships drill in ultra-deep water.",
  "Harsh-environment semi-subs from contractors such as Transocean and Odfjell Drilling work on the Norwegian shelf.",
  m=["jack-up", "jack-ups", "jackup", "jackups", "semi-submersible", "semi-submersibles", "semi-sub", "semi-subs", "drillship", "drillships", "=MODU", "=MODUs", "drilling rig", "drilling rigs", "rig", "rigs"], core=["offshore"])
T("dayrate", "Dayrate", "offshore",
  "Daily fee paid to hire a rig or offshore vessel. Rises when utilisation is high.",
  "A harsh-environment semi-sub at USD 450,000 per day on a 300-day campaign earns USD 135 million.",
  m=["dayrate", "dayrates", "day rate", "day rates", "day-rate"], core=["offshore"])
T("backlog", "Backlog", "offshore",
  "The value of signed contracts not yet performed. Shows how secure a company's future revenue is.",
  "A USD 1.1 billion rise in backlog means future work is locked in even if the market weakens.",
  no="Ordrereserve", m=["backlog", "backlogs", "order backlog", "contract backlog", "ordrereserve"])
T("decommissioning", "Decommissioning", "offshore",
  "Shutting down and removing offshore installations at the end of a field's life: plugging wells (P&A) and removing platforms, pipelines and subsea equipment.",
  "A Norwegian vessel owner wins a campaign to remove subsea structures from a retired North Sea field.",
  m=["decommissioning", "=P&A", "plug and abandonment", "plugging and abandonment"])
T("tieback", "Subsea tieback", "offshore",
  "A smaller field developed with seabed wells connected by pipelines to a nearby existing platform, instead of building a new one. Cheaper and faster.",
  "Many new Norwegian discoveries near large fields like Gullfaks or Troll are developed as tiebacks.",
  m=["tieback", "tiebacks", "tie-back", "tie-backs", "subsea tieback", "subsea tiebacks"])
T("rov", "ROV", "offshore",
  "Remotely operated vehicle: underwater robot controlled from a ship, used for inspection, construction and repair at depths divers cannot reach.",
  "A work-class ROV closes a valve on a subsea template 300 metres down.",
  full="Remotely operated vehicle", m=["=ROV", "=ROVs", "=WROV", "remotely operated vehicle", "remotely operated vehicles"])
T("dp", "Dynamic positioning (DP)", "offshore",
  "Computer-controlled thrusters that keep a vessel in an exact position without anchors. DP2 and DP3 have redundancy, so one failure will not make the ship drift—required for work close to installations.",
  "A DP2 vessel can hold position next to a platform in rough seas while transferring cargo.",
  m=["dynamic positioning", "=DP2", "=DP3", "DP system"])
T("supply-base", "Supply base", "offshore",
  "Port base where offshore supplies are stored and loaded onto supply vessels. Norwegian examples include CCB Ågotnes and Mongstad near Bergen, Dusavik in Stavanger and Vestbase in Kristiansund.",
  "A haulier delivering drill pipe to CCB Ågotnes links road transport directly to offshore logistics.",
  no="Forsyningsbase", m=["supply base", "supply bases", "forsyningsbase", "forsyningsbaser", "=CCB", "Ågotnes", "Mongstad"], core=["offshore", "road"])
T("inter-array", "Inter-array and export cables", "offshore",
  "Inter-array cables connect the turbines in an offshore wind farm to its substation; export cables bring the power to shore.",
  "Cable-lay vessels install inter-array cables after the turbine foundations are in place.",
  m=["inter-array", "inter-array cable", "inter-array cables", "array cable", "array cables", "export cable", "export cables"])
T("ep", "E&P", "offshore",
  "Exploration and production: the upstream oil and gas business of finding, developing and producing fields. E&P spending drives demand for rigs, supply vessels and subsea vessels.",
  "When oil companies raise E&P budgets, rig dayrates usually follow 6–18 months later.",
  full="Exploration and production", m=["=E&P", "exploration and production", "upstream"])
T("mopu", "MOPU", "offshore",
  "Mobile offshore production unit: a movable production platform, often a converted jack-up, used for smaller fields.",
  "Converting an old jack-up into a MOPU lets a small gas field start production without a new platform.",
  full="Mobile offshore production unit", m=["=MOPU", "=MOPUs"])
T("seismic", "Seismic survey", "offshore",
  "Survey that sends sound pulses into the seabed and records the echoes to map rock layers and find oil, gas or CO2 storage sites.",
  "Seismic data from a survey ship help decide where to drill the next exploration well.",
  m=["seismic", "seismic survey", "seismic surveys", "seismic vessel", "seismic research vessel"])
T("ccs", "CCS", "offshore",
  "Carbon capture and storage: capturing CO2 from industry and storing it permanently underground, for example under the North Sea through the Northern Lights project near Bergen.",
  "CO2 is shipped in liquid form to the terminal at Øygarden and piped to a reservoir offshore.",
  full="Carbon capture and storage", m=["=CCS", "carbon capture", "carbon capture and storage", "CO2 storage", "Northern Lights"])
T("offshore-wind", "Offshore wind", "offshore",
  "Wind turbines installed at sea, either on fixed foundations in shallow water or floating in deeper water (as at Hywind Tampen off Norway). Creates demand for installation vessels, CSOVs and cable-lay ships.",
  "A 2.9 GW wind farm needs hundreds of kilometres of cable and years of vessel work.",
  m=["offshore wind", "wind farm", "wind farms", "floating wind", "floating offshore wind", "havvind"], core=["offshore"])

# ---------------- REGULATION ----------------
T("imo", "IMO", "reg",
  "International Maritime Organization: UN agency in London that sets global shipping rules on safety (SOLAS), pollution (MARPOL), emissions and crew training.",
  "Rules on sulphur in ship fuel and the CII carbon rating both come from the IMO.",
  full="International Maritime Organization", m=["=IMO", "International Maritime Organization"], core=["freight"])
T("marpol", "MARPOL", "reg",
  "IMO convention on preventing pollution from ships: oil, chemicals, sewage, garbage and air emissions. Annex VI covers sulphur, NOx and CO2 rules.",
  "The global 0.5% sulphur cap on ship fuel since 2020 comes from MARPOL Annex VI.",
  m=["=MARPOL", "Annex VI"])
T("solas", "SOLAS", "reg",
  "International Convention for the Safety of Life at Sea: minimum standards for construction, fire safety, lifesaving equipment and navigation. Also the source of the container weight rule (VGM).",
  "Lifeboat and fire drill requirements on board come from SOLAS.",
  m=["=SOLAS"])
T("eu-ets", "EU ETS (shipping)", "reg",
  "The EU emissions trading system, which since 2024 includes ships of 5,000 gross tonnage and above. Companies must surrender allowances for their CO2: all emissions on voyages within the EU/EEA and at berth, half on voyages into or out of the EU/EEA. Phased in: 40% of 2024 emissions, 70% of 2025 and 100% from 2026.",
  "A voyage from Rotterdam to New York emitting 3,000 t of CO2 needs allowances for 1,500 t. At EUR 70 per tonne that is EUR 105,000.",
  no="EUs kvotesystem", m=["=EU ETS", "=ETS", "emissions trading", "emission allowances", "carbon allowances", "=EUA", "=EUAs", "kvotehandel", "klimakvoter"], core=["freight"])
T("fueleu", "FuelEU Maritime", "reg",
  "EU regulation from 2025 requiring ships to cut the greenhouse-gas intensity of the energy they use: 2% in 2025, rising step by step to 80% by 2050. Ships can pool surpluses and deficits or pay penalties.",
  "An owner with a biofuel-powered ship can pool its surplus with fossil-fuelled ships to avoid penalties.",
  m=["FuelEU", "FuelEU Maritime", "Fuel EU"])
T("cii", "CII", "reg",
  "Carbon Intensity Indicator: IMO rating from A to E of a ship's yearly CO2 per unit of capacity and distance. Ships rated E, or D three years in a row, need a corrective plan, and charterers increasingly prefer A–C ships.",
  "An older bulker rated D may need to sail slower or fit energy-saving devices to keep charterers interested.",
  full="Carbon Intensity Indicator", m=["=CII", "carbon intensity indicator"])
T("eexi", "EEXI", "reg",
  "Energy Efficiency Existing Ship Index: IMO technical efficiency requirement for existing ships since 2023. Many older ships complied by limiting engine power, which lowers their top speed.",
  "An engine power limit means a 2010-built tanker can no longer speed up much to chase a high-paying cargo.",
  full="Energy Efficiency Existing Ship Index", m=["=EEXI", "engine power limitation", "=EPL"])
T("eedi", "EEDI", "reg",
  "Energy Efficiency Design Index: an IMO requirement that new ships are designed to emit less CO2 per tonne-mile than a reference line, tightened in phases. EEXI applies the same idea to existing ships.",
  "A bulk carrier ordered today must meet a stricter EEDI phase than one ordered ten years ago, often by using a smaller engine or better hull.",
  full="Energy Efficiency Design Index", m=["=EEDI", "Energy Efficiency Design Index"])
T("aer", "AER and EEOI", "reg",
  "Two ways to measure a ship's operational carbon intensity. AER (annual efficiency ratio) divides CO2 by deadweight × distance sailed; it is the basis for most CII ratings. EEOI divides CO2 by cargo actually carried × distance, so it punishes ballast legs.",
  "A ship sailing half the year in ballast has a reasonable AER but a poor EEOI, because it emits CO2 without carrying cargo.",
  m=["=AER", "=EEOI", "annual efficiency ratio", "energy efficiency operational indicator", "carbon intensity"])
T("seemp", "SEEMP and DCS", "reg",
  "The ship energy efficiency management plan every ship must keep, now including its plan to meet CII targets. Under the IMO DCS (and EU MRV), ships report fuel use, distance and hours each year, and the data feeds CII ratings and the EU ETS.",
  "A ship rated D three years in a row must add a corrective action plan to its SEEMP.",
  m=["=SEEMP", "ship energy efficiency management plan", "=DCS", "data collection system", "=MRV", "EU MRV"])
T("imo-nzf", "IMO Net-Zero Framework", "reg",
  "IMO's planned global system to cut shipping emissions: a fuel standard that tightens greenhouse gas intensity limits over time, with payments for ships that miss them and rewards for the cleanest. Its adoption was postponed in October 2025 after strong opposition; talks continue.",
  "If the framework is adopted, an owner running on fossil fuel oil pays for each tonne of CO2-equivalent above the limit, which makes dual-fuel ships more valuable.",
  m=["Net-Zero Framework", "Net Zero Framework", "=NZF", "global fuel standard", "global carbon levy", "GHG pricing", "carbon levy", "=MEPC", "IMO net-zero", "IMO net zero"])
T("wtw", "Well-to-wake", "reg",
  "Counting a fuel's emissions over its whole life: producing and transporting it (well-to-tank) plus burning it on board (tank-to-wake). FuelEU Maritime and the IMO framework use well-to-wake, so fossil LNG or methanol made from natural gas gets less credit than it appears.",
  "Methanol made from natural gas emits more well-to-wake than marine gas oil, even though it burns cleaner on board.",
  m=["well-to-wake", "well to wake", "tank-to-wake", "tank to wake", "well-to-tank", "lifecycle emissions", "life-cycle emissions", "=WtW", "=TtW"])
T("dual-fuel", "Dual-fuel and alternative fuels", "reg",
  "A dual-fuel ship can burn conventional fuel oil and an alternative such as LNG, methanol or ammonia. This keeps options open while green fuel is scarce and expensive, and protects the ship's value as rules tighten.",
  "A dual-fuel methanol containership runs on fuel oil today and can switch when green methanol becomes available or carbon costs rise.",
  m=["dual-fuel", "dual fuel", "methanol-fuelled", "methanol-fueled", "ammonia-fuelled", "ammonia-fueled", "LNG-fuelled", "LNG-fueled", "methanol-ready", "ammonia-ready", "alternative fuel", "alternative fuels", "green methanol", "green ammonia", "e-fuels", "biofuel", "biofuels"])
T("jones-act", "Jones Act", "reg",
  "US law reserving shipping between US ports for ships that are US-built, US-owned, US-flagged and US-crewed. It protects domestic yards and crews but makes US coastal shipping expensive, and it is often debated when fuel or goods are short in places like Puerto Rico.",
  "LNG cannot be shipped from Texas to New England on a foreign LNG carrier, so the region may import LNG from abroad instead.",
  m=["Jones Act", "Merchant Marine Act", "US cabotage"])
T("psc", "Port State Control (PSC)", "reg",
  "Inspections of foreign ships in a country's ports to check they meet international rules. Serious faults lead to detention until fixed.",
  "The Paris MoU, which includes Norway, publishes lists of detained ships; flags with many detentions end up on its black list.",
  m=["port state control", "=PSC", "Paris MoU", "detained", "detention list"])
T("ism", "ISM Code", "reg",
  "International Safety Management Code: every shipping company must have a safety management system, a designated person ashore (DPA) and documented procedures.",
  "After an accident, investigators check whether the company followed its own ISM procedures.",
  m=["ISM Code", "=ISM", "=DPA"])
T("mlc", "MLC", "reg",
  "Maritime Labour Convention: ILO convention setting seafarers' rights to contracts, wages, rest hours, accommodation and repatriation.",
  "Crew stuck on board for months past their contracts is an MLC breach that port inspectors can act on.",
  full="Maritime Labour Convention", m=["=MLC", "Maritime Labour Convention", "seafarers' rights"])
T("mobility-package", "Mobility Package", "reg",
  "EU road transport rules adopted in 2020 covering cabotage, posting of drivers, rest rules, return of vehicles to their home country every eight weeks and tachographs for vans in international transport.",
  "A truck from a Polish haulier working mostly in Western Europe must return to Poland at least every eight weeks.",
  no="Mobilitetspakken", m=["Mobility Package", "mobilitetspakken"], core=["road"])
T("posting", "Posting of drivers", "reg",
  "Rules requiring foreign drivers doing cabotage and some international jobs to be paid at least the host country's wage for that work. In Norway, minimum wages for road freight are set through generally applicable collective agreements (allmenngjøring).",
  "A foreign driver doing cabotage in Norway must get the Norwegian minimum wage for those trips.",
  m=["posting of drivers", "posted drivers", "allmenngjøring", "allmenngjort", "utsendte sjåfører"])
T("digitoll", "Digitoll", "reg",
  "Norwegian Customs' digital system for reporting goods before they cross the border. Carriers must send electronic information in advance, and trucks without it can be held.",
  "If Digitoll goes down, trucks at the border may wait hours while customs falls back to manual procedures.",
  m=["Digitoll", "Tolletaten", "Norwegian Customs"])

# ---------------- TRADE, PORTS & LOGISTICS ----------------
T("incoterms", "Incoterms", "trade",
  "Standard ICC rules (current version Incoterms 2020) that define who pays for transport, insurance and duties, and where the risk passes from seller to buyer.",
  "'FCA Bergen' means the seller hands the goods to the buyer's carrier in Bergen. After that, risk and cost are the buyer's.",
  no="Leveringsbetingelser", m=["Incoterms", "Incoterm", "Incoterms 2020", "leveringsbetingelser", "leveringsbetingelse"], core=["road"])
T("exw", "EXW (Ex Works)", "trade",
  "The seller makes the goods available at its own premises. The buyer handles and pays for everything from loading onwards.",
  "Buying machinery EXW from a factory in Germany means you book and pay the truck from the factory gate.",
  m=["=EXW", "ex works"])
T("fca", "FCA (Free Carrier)", "trade",
  "The seller delivers export-cleared goods to the carrier named by the buyer at an agreed place, where the risk passes. The most used term for road and container freight.",
  "'FCA seller's warehouse, Bergen': risk passes when the goods are loaded onto the buyer's truck.",
  m=["=FCA", "free carrier"])
T("fob", "FOB (Free On Board)", "trade",
  "Sea and inland waterway only: risk passes when the goods are on board the ship at the loading port, and the buyer pays the sea freight. Common for bulk cargo.",
  "Grain bought FOB Santos: the buyer charters the ship and carries the risk once the grain is loaded.",
  m=["=FOB", "free on board"])
T("cif", "CIF / CFR", "trade",
  "Sea only. CFR (cost and freight): the seller pays freight to the destination port. CIF adds minimum insurance paid by the seller. In both, risk passes to the buyer when the goods are loaded on board.",
  "A steel cargo sold CIF Rotterdam: the seller pays the ship, but the buyer carries the risk from loading in Asia.",
  m=["=CIF", "=CFR", "cost, insurance and freight", "cost insurance and freight", "cost and freight"])
T("dap", "DAP / DDP", "trade",
  "DAP (Delivered at Place): the seller carries cost and risk to the named destination, and the buyer pays import duties. DDP (Delivered Duty Paid): the seller also pays import duties and VAT. DPU means delivered and unloaded.",
  "An online seller shipping DDP to Norway must handle Norwegian VAT and customs itself.",
  m=["=DAP", "=DDP", "=DPU", "delivered at place", "delivered duty paid"])
T("bol", "Bill of lading (B/L)", "trade",
  "Document issued by the sea carrier: a receipt for the cargo, evidence of the transport contract and a document of title—whoever holds an original 'to order' B/L can claim the goods. A sea waybill is a non-negotiable alternative.",
  "A bank financing a cargo holds the original B/L until the buyer has paid.",
  no="Konnossement", m=["bill of lading", "bills of lading", "=B/L", "=B/Ls", "konnossement", "=MBL", "=HBL", "sea waybill", "sea waybills"], core=["freight"])
T("shipper-consignee", "Shipper / consignee / notify party", "trade",
  "Shipper: the party sending the goods. Consignee: the receiver named on the transport document. Notify party: who the carrier contacts on arrival, often an agent or customs broker.",
  "On an export from Bergen, the fish exporter is shipper, the importer in Rotterdam is consignee, and its customs agent is notify party.",
  no="Vareeier / avsender / mottaker", m=["shipper", "shippers", "consignee", "consignees", "notify party", "vareeier", "vareeiere", "vareeierne"])
T("forwarder", "Freight forwarder", "trade",
  "Company that organises transport for shippers: books carriers, consolidates cargo and handles documents and customs. May own few or no trucks or ships.",
  "DSV and Kuehne+Nagel are among the world's largest forwarders.",
  no="Speditør", m=["freight forwarder", "freight forwarders", "forwarder", "forwarders", "freight forwarding", "speditør", "speditører", "spedisjon"], core=["road"])
T("nvocc", "NVOCC", "trade",
  "Non-vessel operating common carrier: issues its own (house) bills of lading and sells container transport without owning ships, buying space from shipping lines.",
  "A forwarder acting as NVOCC books 50 containers with a liner and resells the space to small exporters.",
  m=["=NVOCC", "=NVOCCs", "non-vessel operating"])
T("3pl", "3PL / 4PL", "trade",
  "Third-party logistics: an outside company runs warehousing and transport for a business. Fourth-party logistics (4PL) manages the whole supply chain, including other 3PLs, on the customer's behalf.",
  "A retailer outsources its central warehouse near Oslo to a 3PL instead of running it itself.",
  m=["=3PL", "=4PL", "third-party logistics", "contract logistics", "tredjepartslogistikk"])
T("cross-docking", "Cross-docking", "trade",
  "Goods arriving at a terminal are sorted and moved straight onto outgoing vehicles with little or no storage.",
  "Pallets from twenty suppliers are cross-docked overnight onto trucks for each grocery store.",
  m=["cross-docking", "cross docking", "cross-dock", "crossdock", "crossdocking"])
T("last-mile", "Last mile", "trade",
  "The final delivery step to the end customer, often the most expensive part of the journey per parcel.",
  "Parcel lockers cut last-mile cost because one stop serves dozens of customers.",
  m=["last mile", "last-mile", "home delivery", "home deliveries", "hjemlevering", "siste mil"])
T("thc", "THC", "trade",
  "Terminal handling charge: the fee for handling a container at the terminal—lifting it on or off the ship and moving it in the yard—charged at origin and destination.",
  "A THC of USD 455 per 20-foot box at Long Beach adds directly to an importer's landed cost.",
  full="Terminal handling charge", m=["=THC", "=THCs", "terminal handling charge", "terminal handling charges"])
T("baf", "BAF", "trade",
  "Bunker adjustment factor: surcharge on container freight that follows fuel prices, so carriers pass changes in fuel cost on to customers. Emission surcharges for EU ETS work the same way.",
  "If fuel prices rise 20% in a quarter, the BAF on each container goes up at the next adjustment.",
  full="Bunker adjustment factor", m=["=BAF", "bunker adjustment factor", "bunker surcharge", "emission surcharge", "ETS surcharge"])
T("dnd", "Demurrage & detention (containers)", "trade",
  "Container fees: demurrage for leaving a full container in the terminal beyond the free time; detention for keeping the carrier's container outside the terminal too long.",
  "Free time of 5 days and a container collected on day 9 at USD 100 per day costs USD 400 in demurrage.",
  m=["demurrage and detention", "=D&D", "free time", "detention charges"])
T("vgm", "VGM", "trade",
  "Verified gross mass: SOLAS rule that the shipper must declare the verified weight of a packed container before it is loaded on a ship.",
  "Without a VGM before the cut-off, the terminal will not load the container.",
  full="Verified gross mass", m=["=VGM", "verified gross mass"])
T("cut-off", "Cut-off", "trade",
  "Deadline for cargo, documents or VGM before a ship departs. Miss it and the container waits for the next sailing.",
  "Cargo cut-off Thursday 12:00 for a Saturday sailing means the truck must reach the terminal before Thursday noon.",
  m=["cut-off", "cutoff", "cut off time", "closing time"])
T("reefer", "Reefer", "trade",
  "Refrigerated container or trailer with its own cooling unit, used for food, fish and medicines.",
  "Fresh Norwegian salmon leaves in reefer trailers kept just above freezing.",
  no="Kjøletransport / termotransport", m=["reefer", "reefers", "refrigerated", "termotransport", "kjøletransport", "cold chain", "cold storage", "fryselager"])
T("project-cargo", "Project cargo", "trade",
  "Large, heavy or complex cargo for industrial projects—power plants, offshore modules, wind turbines—moved with tailored engineering by road, sea and air. Includes heavy lift and out-of-gauge (OOG) cargo.",
  "A 300-tonne module from a yard in Germany to Ågotnes may combine a heavy-lift ship, self-propelled modular transporters (SPMT) and a road convoy.",
  no="Prosjektlogistikk", m=["project cargo", "project logistics", "prosjektlogistikk", "heavy lift", "heavy-lift", "=OOG", "out of gauge", "out-of-gauge", "=SPMT", "=SPMTs", "breakbulk", "break bulk"], core=["road", "offshore"])
T("roro", "Ro-ro / lo-lo", "trade",
  "Ro-ro (roll-on/roll-off): cargo is driven on and off via ramps—trailers, cars and machinery. Lo-lo (lift-on/lift-off): cargo is lifted by cranes, like containers.",
  "Unaccompanied trailers between Norway and the continent often travel on ro-ro ships while the truck stays home.",
  m=["ro-ro", "roro", "=RoRo", "lo-lo", "lolo", "unaccompanied trailer", "unaccompanied trailers"])
T("intermodal", "Intermodal transport", "trade",
  "Moving goods in one loading unit (container, trailer or swap body) using several modes—truck, rail and ship—without handling the goods themselves.",
  "A trailer goes Bergen–Oslo by train, then to Germany by ship, and a truck makes the final delivery.",
  m=["intermodal", "multimodal", "combined transport", "kombitransport", "rail freight", "godstog", "godstogene", "jernbanefrakt"])
T("transshipment", "Transshipment / feeder", "trade",
  "Moving cargo from one ship to another at a hub port, for example from a large ocean ship to a smaller feeder ship that serves smaller ports such as most Norwegian ones.",
  "Containers for Bergen often come from Asia to Rotterdam or Hamburg and continue on a feeder.",
  m=["transshipment", "transhipment", "feeder", "feeders", "feeder ship", "feeder service", "hub port"])
T("dwell", "Dwell time", "trade",
  "How long cargo or a container stays in a terminal before moving on. Rising dwell times are an early sign of congestion.",
  "Rail dwell times rising at a busy port can delay inland deliveries by days.",
  m=["dwell time", "dwell times"])
T("congestion", "Port congestion", "trade",
  "Ships waiting to berth because terminals are full or slow. Waiting ships are effectively removed from supply, which pushes freight rates up.",
  "During the pandemic, dozens of container ships waited outside Los Angeles, which sent freight rates to record highs.",
  m=["port congestion", "congestion", "congested"], core=["freight"])
T("customs-transit", "Customs transit (T1) / EORI", "trade",
  "Transit (T1) lets goods move under customs control without paying duties until they reach the destination office. EORI is the ID number businesses need for customs in the EU.",
  "A truck from Sweden carries goods to Bergen under a T1 transit, and duties are paid when customs clears them in Bergen.",
  m=["=T1", "transit procedure", "=EORI", "customs transit", "customs clearance", "fortolling"])
T("supply-chain", "Supply chain resilience", "trade",
  "How well a supply chain withstands disruptions such as conflicts, cyberattacks or closed routes, using buffer stock, alternative suppliers and routes.",
  "Norway building larger fuel stocks is a resilience measure: it buys time if imports are disrupted.",
  no="Forsyningssikkerhet / beredskap", m=["supply chain resilience", "forsyningssikkerhet", "beredskap", "beredskapslager", "transportberedskap", "drivstoffberedskap"])

# ---------------- EMAIL & ABBREVIATIONS ----------------
T("eta", "ETA / ETD / ETB", "email",
  "Estimated time of arrival / departure / berthing. ATA and ATD are the actual times. Usually given with date and local time (LT) or UTC.",
  "'ETA Mongstad 15/10 0600 LT, ETB 0900 AGW' means expected arrival at 06:00 local time and berthing at 09:00 if all goes well.",
  m=["=ETA", "=ETD", "=ETB", "=ATA", "=ATD", "=ETAs"])
T("pol-pod", "POL / POD", "email",
  "Port of loading / port of discharge. Careful: in road transport POD usually means proof of delivery, the signed delivery receipt.",
  "'POL Bergen, POD Rotterdam' is a sea shipment. 'Please send POD for the Oslo delivery' asks for the signed receipt.",
  m=["=POL", "=POD", "port of loading", "port of discharge", "proof of delivery"])
T("tba", "TBA / TBC / TBN", "email",
  "To be advised / to be confirmed / to be nominated. 'Vessel TBN' means the ship has not been named yet.",
  "'Laycan 1–5 Dec, vessel TBN' means the dates are agreed and the owner will name the ship later.",
  m=["=TBA", "=TBC", "=TBN"])
T("eod", "EOD / COB / ASAP", "email",
  "End of day / close of business (often around 16:00–17:00 local time) / as soon as possible.",
  "'Please revert by COB Friday' means reply before the end of the working day on Friday.",
  m=["=EOD", "=COB", "=ASAP"])
T("pfa", "PFA / FYI / WRT / PLS", "email",
  "Please find attached / for your information / with regard to / please. Common shorthand in operations emails, along with Rgds or BR (best regards) and TIA (thanks in advance).",
  "'PFA the CMR for today's load, pls confirm receipt. BR' is a typical dispatcher email.",
  m=["=PFA", "=FYI", "=WRT", "=PLS", "=Pls", "=Rgds", "=TIA"])
T("lt-utc", "LT / UTC", "email",
  "Local time / Coordinated Universal Time. Shipping often uses UTC to avoid time-zone confusion. Norway is UTC+1 in winter and UTC+2 in summer.",
  "'ETA 0400 UTC' at Bergen in October is 06:00 local time.",
  m=["=UTC", "=GMT", "local time"])
T("agw", "AGW / WP / WOG", "email",
  "All going well / weather permitting / without guarantee. Signals that a time or figure is an estimate, not a promise.",
  "'ETB tomorrow 0800 AGWWP' means berthing is expected at 08:00 if nothing goes wrong and the weather allows.",
  m=["=AGW", "=WOG", "=AGWWP", "=WP"])
T("shinc", "SHINC / SHEX / SSHEX", "email",
  "Laytime terms: Sundays and holidays included (time counts every day) / Sundays and holidays excepted / Saturdays, Sundays and holidays excepted. Often combined with EIU (even if used) or UU (unless used) to say whether work done on excepted days counts.",
  "'7,000 MT PWWD SHEX UU' means 7,000 tonnes per weather working day, Sundays and holidays excluded unless work is actually done.",
  m=["=SHINC", "=SHEX", "=SSHEX", "=FHEX", "=EIU", "=UU"])
T("wwd", "WWD / PWWD", "email",
  "Weather working day / per weather working day: days on which the weather allows cargo work. Hours lost to rain do not count as laytime.",
  "A grain cargo at 8,000 t PWWD: a rainy day that stops loading does not use up laytime.",
  m=["=WWD", "=PWWD", "weather working day", "weather working days"])
T("wibon", "WIBON / WIPON / WIFPON / WCCON", "email",
  "Whether in berth or not / whether in port or not / whether in free pratique or not / whether customs cleared or not. These let the owner tender NOR and start laytime even while the ship waits for a berth or formalities.",
  "With WIBON, a ship waiting three days at anchor for a berth is already using the charterer's laytime.",
  m=["=WIBON", "=WIPON", "=WIFPON", "=WCCON"])
T("moloo", "MOLOO / MOLCO", "email",
  "More or less in owner's option / in charterer's option: the allowed tolerance on cargo quantity.",
  "'50,000 MT 10% MOLOO' lets the owner load anything from 45,000 to 55,000 tonnes.",
  m=["=MOLOO", "=MOLCO", "=MOLCHOPT"])
T("dwcc", "DWCC", "email",
  "Deadweight cargo capacity: how much cargo the ship can actually load after deducting fuel, water and stores from its deadweight.",
  "A 58,000 dwt ship with 1,800 t of fuel, water and stores has a DWCC of about 56,000 t.",
  m=["=DWCC"])
T("pdpr", "PDPR", "email",
  "Per day pro rata: a daily rate (hire or demurrage) charged proportionally for part days.",
  "Demurrage of USD 20,000 PDPR for 6 hours comes to USD 5,000.",
  m=["=PDPR"])
T("units", "PMT / CBM / BBL", "email",
  "Per metric tonne / cubic metres / barrels (1 barrel = 159 litres). Units you meet in freight quotes and cargo descriptions.",
  "'USD 24.50 PMT' is the freight per tonne; a 'VLCC with 2 million bbls' carries about 318 million litres of crude.",
  m=["=PMT", "=CBM", "=cbm", "=bbls", "=bbl"])
T("oa-abt-bss", "O/A / ABT / BSS", "email",
  "On or about / about / basis. 'BSS 1/1' means based on one loading port and one discharge port.",
  "'Laycan o/a 10 Nov, abt 30,000 MT, bss 1/1 USD 22 PMT' is a compact freight offer.",
  m=["=O/A", "=ABT", "=BSS", "=bss"])
T("rnr", "RNR / P&C", "email",
  "Rate not reported / private and confidential. Market reports use these when the deal terms are kept secret.",
  "'VLCC, MEG/China, RNR' means the fixture happened, but the price was not disclosed.",
  m=["=RNR", "=P&C"])
T("cqd", "CQD", "email",
  "Customary quick despatch: cargo handled as fast as is normal in that port, with no fixed laytime. Often leads to disputes.",
  "Under CQD terms, the owner must prove the port worked slower than usual to claim demurrage.",
  m=["=CQD"])
T("fios", "FIO / FIOS / FIOST", "email",
  "Free in and out (stowed, trimmed): the charterer pays for loading, discharging, stowing and trimming the cargo; the owner pays only for the ship.",
  "A freight of USD 30 PMT FIOS means the cargo owner also pays the stevedores at both ends.",
  m=["=FIO", "=FIOS", "=FIOST", "=FILO", "=LIFO"])
T("delivery-points", "APS / DLOSP / DOP", "email",
  "Delivery and redelivery points in time charters: arrival pilot station / dropping last outward sea pilot / dropping outward pilot. Hire starts or ends when the ship passes that point.",
  "'Delivery DLOSP Rotterdam' means hire starts when the pilot leaves the ship on its way out of Rotterdam.",
  m=["=APS", "=DLOSP", "=DOP"])
T("cve", "CVE", "email",
  "Communications, victualling and entertainment: a monthly lump sum the time charterer pays the owner on top of hire.",
  "'CVE USD 1,500 per month pro rata' is a standard line in a time charter recap.",
  m=["=CVE"])
T("ilohc", "ILOHC", "email",
  "In lieu of hold cleaning: a lump sum the charterer pays instead of cleaning the holds after discharge.",
  "'ILOHC USD 5,000' means the charterer pays USD 5,000 and the crew cleans the holds.",
  m=["=ILOHC"])

# --- checks & output ---
ids = [g["id"] for g in G]
dupes = {i for i in ids if ids.count(i) > 1}
assert not dupes, dupes
out = {"version": 1, "categories": CATS, "terms": []}
for g in G:
    g["def"] = g.pop("def_")
    out["terms"].append(g)
print(len(G), "terms", file=sys.stderr)
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
