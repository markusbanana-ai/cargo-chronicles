"""Writes docs/data/insights.json: situation rules for the per-article reading guide.

Fields per rule
  id     unique id
  m      keywords that signal the situation (word* = prefix, =ABC = exact capitals)
  req    optional list of keyword groups; each group must also match somewhere
  x      optional keywords that cancel the rule
  lang   optional: only for articles in this language ("no"/"en")
  seg    sections where the rule is most relevant (small score boost)
  t, b   title and body
  up/dn  optional direction variants {t, b}; picked when the headline says rising/falling
  w      what to watch next
  terms  glossary ids shown as chips
  go     links: "tool:rates", "map:sea/hormuz", "map:road/E39" ...
  c      optional course topic the situation belongs to (shown as a small label)
"""
import json, sys
from pathlib import Path

R = []
def rule(**k): R.append(k)

# ------------------------------------------------------------------ freight markets
rule(id="bdi", seg=["freight"], m=["baltic dry", "=BDI", "dry index", "baltic index"],
     t="The Baltic Dry Index moved",
     b="The BDI is a daily average of dry bulk time-charter rates for Capesize, Panamax and Supramax ships, published by the Baltic Exchange. It is a price for ships, not for cargo, so it reacts to how tight the fleet is, not only to how much is shipped.",
     up={"t": "The Baltic Dry Index is rising", "b": "More cargo is chasing the same ships, often iron ore and coal into China or grain from South America. Owners earn more per day and asset values tend to follow; charterers and traders pay more to move cargo."},
     dn={"t": "The Baltic Dry Index is falling", "b": "Ships are easier to find than cargo. Owners earn less per day, and if it lasts, older ships get scrapped and second-hand values soften. Charterers can lock in cheaper period cover."},
     w="Check which size moved: Capesize (iron ore) swings far more than Supramax (grain, minor bulks), so one big move in Capes can drive the whole index.",
     terms=["bdi", "capesize", "tce", "baltic-exchange"], go=["tool:rates", "map:sea/route/c5"])

rule(id="capesize", seg=["freight"], m=["capesize*", "iron ore", "vale", "pilbara", "simandou", "=C5", "=C3", "=C5TC", "valemax"],
     t="Capesize and iron ore",
     b="Capesizes (about 180,000 dwt) mostly carry iron ore and coal. Two routes set the tone: C5 West Australia–China, about 3,600 miles, and C3 Brazil–China, about 11,000 miles. Cargo from Brazil uses three times the ship-days per tonne, so a shift from Australian to Brazilian ore lifts demand for ships even if China imports the same tonnes.",
     up={"t": "Capesize rates are rising", "b": "Often driven by more long-haul Brazilian ore (more ton-miles) or Chinese restocking. Capesize earnings move fastest of all bulk sizes because the fleet is concentrated on few cargoes."},
     dn={"t": "Capesize rates are falling", "b": "Typical causes: weaker Chinese steel output, rain or maintenance cutting Brazilian exports, or more ships delivered. Short-haul C5 cargoes tie up fewer ships, so a shift towards Australia also softens rates."},
     w="Watch Chinese steel production, Brazilian export volumes and the C3/C5 spread: a widening spread signals tight Atlantic tonnage.",
     terms=["capesize", "ton-miles", "dry-bulk"], go=["map:sea/route/c3", "tool:rates"])

rule(id="panamax-grain", seg=["freight"], m=["panamax*", "kamsarmax*", "grain*", "soybean*", "corn", "wheat", "coal", "supramax*", "ultramax*", "handysize*", "minor bulk*", "=P5TC", "=P4TC"],
     x=["capesize"],
     t="Mid-size bulkers: grain and coal",
     b="Panamax/Kamsarmax ships (75–85,000 dwt) carry grain, coal and other bulk; Supramax/Ultramax (50–64,000 dwt) carry the widest mix and often have their own cranes. Grain is seasonal: South American soybeans peak in spring, US Gulf grain in autumn, and long voyages to China add ton-miles.",
     up={"t": "Mid-size bulk rates are rising", "b": "Harvest season, low water in rivers or canals, or extra coal imports in a heatwave can all tighten Panamax and Supramax supply. These sizes react more slowly than Capesize but stay up longer."},
     dn={"t": "Mid-size bulk rates are falling", "b": "Often a seasonal gap between harvests or weaker coal buying. Because these ships switch between many cargoes, rates rarely collapse as fast as Capesize."},
     w="Watch the Panama Canal draft limits and the grain export calendar.",
     terms=["panamax", "supramax", "dry-bulk", "ton-miles"], go=["map:sea/route/grain", "tool:rates"])

rule(id="tanker-rates", seg=["freight"], m=["vlcc*", "suezmax*", "aframax*", "crude tanker*", "tanker rate*", "tanker market", "tanker earnings", "=TD3C", "=TD20", "=TD25", "crude carrier*"],
     t="Crude tanker earnings",
     b="Crude tanker rates are quoted in Worldscale points (WS) or as a lump sum, then converted to time-charter equivalent (TCE, USD per day) so different routes compare. VLCCs (2 million barrels) dominate long-haul Middle East–Asia trade; Suezmax and Aframax serve Atlantic and regional routes.",
     up={"t": "Crude tanker rates are rising", "b": "Long-haul exports (US Gulf or Brazil to Asia), rerouting around a chokepoint, sanctions that push trade onto fewer compliant ships, and floating storage all absorb tonnage. Higher TCE lifts second-hand values and makes lenders comfortable."},
     dn={"t": "Crude tanker rates are falling", "b": "OPEC+ cuts, refinery maintenance, shorter-haul trade or ships returning from storage free up tonnage. Owners slow down to save fuel, which quietly removes some supply again."},
     w="Watch OPEC+ output decisions, Chinese crude imports and the size of the orderbook against ships over 20 years old.",
     terms=["vlcc", "suezmax", "aframax", "worldscale", "tce"], go=["map:sea/route/td3c", "tool:voyage"])

rule(id="product-tankers", seg=["freight"], m=["product tanker*", "clean tanker*", "=MR", "=LR1", "=LR2", "jet fuel", "gasoil", "naphtha", "refined product*", "refinery", "refineries", "=TC2", "=TC14"],
     t="Product tankers and refinery shifts",
     b="Product tankers (MR about 50,000 dwt; LR1/LR2 larger) carry refined fuels. Demand depends on where refineries sit versus where fuel is used: new export refineries in the Middle East and Asia, and closures in Europe, lengthen voyages. MRs often triangulate (Europe–US–Europe) to avoid sailing empty.",
     w="Watch refinery closures in Europe and California and diesel arbitrage between the US Gulf and Europe.",
     terms=["product-tanker", "ballast", "ton-miles"], go=["map:sea/route/mr-triangle", "tool:voyage"])

rule(id="container-rates", seg=["freight"], m=["container index", "=WCI", "=SCFI", "=CCFI", "drewry", "freightos", "=FBX", "spot rate*", "box rate*", "container rate*", "freight rate*", "ocean rate*", "xeneta"],
     req=[["container*", "box*", "=WCI", "=SCFI", "drewry", "freightos", "=FBX", "=TEU", "liner*", "xeneta"]],
     t="Container spot rates",
     b="Indices like Drewry WCI, SCFI and Freightos FBX track what shippers pay per 40-foot container (FEU) on the spot market. Most big shippers have annual contracts, so spot is the marginal price; carriers manage it by adjusting capacity (blank sailings) rather than by changing ship numbers.",
     up={"t": "Container rates are rising", "b": "Usually capacity has been removed (blank sailings, longer Cape routings, congestion) or demand is front-loaded before tariffs or peak season. Carriers' profits jump quickly, and shippers start pushing for contract rates instead."},
     dn={"t": "Container rates are falling", "b": "New ships keep arriving, so when demand pauses the carriers fight for cargo. Watch for more blank sailings: that is the carriers' main tool to stop the slide."},
     w="Compare Asia–Europe with transpacific: they move for different reasons (Red Sea routing versus US tariffs).",
     terms=["container-index", "teu", "blank-sailing", "liner"], go=["map:sea/route/asia-europe", "tool:rates"])

rule(id="container-fleet", seg=["freight", "finance"], m=["containership*", "container ship*", "boxship*", "=TEU", "neopanamax", "feeder*"],
     req=[["order*", "newbuild*", "deliver*", "invest*", "christen*", "contract*", "acquir*", "fleet"]],
     t="New container capacity",
     b="Container lines ordered heavily after their record 2021–22 profits, and those ships are still arriving. Each new large ship adds capacity on the main east–west lanes, and the older ships cascade down to smaller trades. More capacity than cargo means pressure on freight rates unless ships are slowed, rerouted or scrapped.",
     w="Watch the orderbook as a share of the fleet and whether ships are still going around the Cape of Good Hope; that routing alone absorbs a large slice of capacity.",
     terms=["orderbook", "teu", "newbuilding", "liner"], go=["tool:rates", "map:sea/route/asia-europe"])

rule(id="newbuilding", seg=["freight", "finance"], m=["newbuild*", "orders", "ordered", "order for", "orderbook", "shipyard order*", "contract for", "keel", "delivered", "delivery of", "christen*"],
     req=[["ship*", "vessel*", "tanker*", "bulker*", "carrier*", "yard*", "vlcc*", "containership*", "boxship*"]],
     x=["truck*", "lastebil*", "volvo", "scania"],
     t="New ships ordered or delivered",
     b="A newbuilding takes two to four years from order to delivery, so today's orders decide fleet supply years ahead. Owners order when rates and second-hand prices are high, which is why order booms often end in overcapacity. Payment is typically in instalments, protected by yard refund guarantees.",
     w="Compare the orderbook with the share of the fleet over 20 years old: that is the real growth once scrapping is counted.",
     terms=["newbuilding", "orderbook", "refund-guarantee"], go=["tool:rates"])

rule(id="snp", seg=["finance", "freight"], m=["sale and purchase", "=S&P", "second-hand", "secondhand", "en bloc", "acquir*", "acquisition", "takeover", "merger", "combination with", "buys", "bought", "sold", "sells", "sale of"],
     req=[["ship*", "vessel*", "fleet", "tanker*", "bulker*", "vlcc*", "carrier*", "shipping", "seaways", "rederi*", "owner*"]],
     x=["insurance", "underwrit*"],
     t="Ships changing hands",
     b="There are two ways to value a ship. The market approach uses recent sales of similar ships (broker valuations). The income approach discounts expected earnings (TCE minus OPEX) over the remaining life plus the scrap value at the end, using the cost of capital; lenders call this the long-term asset value. When prices are far above that value, the buyer is betting on higher rates for longer, which is an asset play. Banks use the same values to test the minimum value clause.",
     w="Compare the price with the latest broker valuation, a newbuilding of the same type, and what today's long-run rates justify: a buyer paying close to newbuilding price expects a long strong market.",
     terms=["sale-purchase", "ltav", "vmc", "asset-play"], go=["tool:valuation", "tool:voyage"], c="Ship valuation and sale & purchase")

rule(id="scrapping", seg=["freight", "finance"], m=["scrap*", "demolition", "recycl*", "shipbreak*", "breakers", "=LDT", "alang", "chittagong", "gadani"],
     t="Ships sent for recycling",
     b="Old ships are sold for steel at a price per light displacement tonne (LDT). Scrapping is supply leaving the fleet: high scrapping in a weak market helps rates recover. Scrap value (LDT × steel price) is also the residual value at the end of a ship's life in a valuation and the floor for an old ship's price, which matters when lenders value collateral.",
     w="Watch how many ships are over 20 years old; low freight rates plus new emission rules usually push more of them out.",
     terms=["recycling", "ltav", "nav"], go=["tool:rates", "tool:valuation"], c="Ship valuation and sale & purchase")

rule(id="hormuz", seg=["freight", "insurance"], m=["hormuz", "persian gulf", "arabian gulf", "gulf of oman", "=MEG", "iran*", "fujairah", "kharg"],
     t="The Strait of Hormuz",
     b="About a fifth of the world's oil consumption passes Hormuz, mostly to Asia (EIA, 2023). Unlike Suez there is no sea detour; only pipelines in Saudi Arabia and the UAE can bypass it, with limited spare capacity. Disruption hits tanker rates, oil prices and war-risk premiums at the same time.",
     w="Watch tanker transit counts, war-risk quotes as % of hull value per transit, and whether Saudi crude is shifted to the Red Sea port of Yanbu.",
     terms=["chokepoint", "war-risk", "listed-areas", "vlcc"], go=["map:sea/hormuz", "tool:effects"])

rule(id="red-sea", seg=["freight", "insurance"], m=["red sea", "suez", "houthi*", "bab el-mandeb", "bab-el-mandeb", "gulf of aden", "yemen*", "cape of good hope", "rerout*"],
     t="Red Sea and Suez routing",
     b="Asia–Europe trade normally goes through Bab el-Mandeb and the Suez Canal. Going around the Cape of Good Hope instead adds roughly 3,000–3,500 nautical miles and 10–14 days. The same cargo then needs more ship-days, which absorbs fleet capacity and lifts rates, while fuel and crew costs per voyage rise.",
     w="Watch Suez Canal transit numbers and carriers' statements about returning; a large-scale return would release capacity and push container rates down.",
     terms=["chokepoint", "ton-miles", "war-risk", "listed-areas"], go=["map:sea/red-sea", "tool:rates"])

rule(id="panama", seg=["freight"], m=["panama canal", "panama", "gatun", "neopanamax", "canal draft", "draft restriction*"],
     t="The Panama Canal",
     b="The canal links the US Gulf and East Coast with Asia. It runs on fresh water from Gatun Lake, so droughts force draft limits and fewer daily transits. Ships that cannot book a slot wait, pay auction prices, or take the longer route via Suez or the Cape, which adds ton-miles and cost.",
     w="Watch Gatun Lake water levels and LNG and grain routings from the US Gulf to Asia.",
     terms=["chokepoint", "ton-miles"], go=["map:sea/panama", "map:sea/route/blng3"])

rule(id="black-sea", seg=["freight", "insurance"], m=["black sea", "odesa", "odessa", "novorossiysk", "romania*", "bulgaria*", "constanta", "ukrain*", "bosporus", "turkish strait*", "kerch"],
     t="Black Sea risk",
     b="The Black Sea exports grain from Ukraine and Russia and oil from Russia and Kazakhstan (CPC), all leaving through the Turkish Straits. Attacks on ships or ports raise war-risk premiums, make some owners refuse the area, and push charterers to pay a premium for willing tonnage.",
     w="Watch war-risk premium quotes for Black Sea calls, crew safety incidents and grain export volumes.",
     terms=["war-risk", "listed-areas", "chokepoint"], go=["map:sea/bosporus"])

rule(id="sanctions", seg=["insurance", "freight", "finance"], m=["sanction*", "shadow fleet", "dark fleet", "price cap", "=OFAC", "stateless", "false flag*", "blacklist*", "embargo*", "blockade*"],
     t="Sanctions and the shadow fleet",
     b="Sanctions bar Western banks, insurers and service providers from certain trades. Ships carrying sanctioned cargo lose access to International Group P&I cover and mainstream finance, so the trade moves to an older 'shadow fleet' with opaque ownership and weaker insurance. That splits the market: compliant ships lose cargo, shadow ships earn premiums, and spill risks rise.",
     w="Watch new vessel listings by the EU, UK and US, and ship-to-ship transfers in open waters.",
     terms=["sanctions", "shadow-fleet", "ig", "pi"], go=["tool:effects"], c="Geopolitics and shipping")

rule(id="war-risk", seg=["insurance"], m=["drone*", "missile*", "attack*", "struck", "strikes", "strike on", "strike near", "strike", "seiz*", "hijack*", "pirat*", "boarded", "sea mine*", "limpet*", "explosive*"],
     x=["port strike*", "dock strike*", "workers strike", "streik*", "carrier strike group", "dronesentral"],
     t="Attacks on ships: who pays?",
     b="Ordinary hull and P&I cover excludes war, so owners buy separate war-risk cover. When an area is declared high-risk (Lloyd's Joint War Committee 'listed areas'), insurers charge an additional premium for each transit, quoted as a percentage of hull value, and can cancel cover at short notice. In July 2026, quotes for Hormuz were reported at 2–6% of hull value per transit (Insurance Business, citing Marsh): about USD 6 million for a USD 100 million tanker.",
     w="Watch whether the area is added to the listed areas, how premiums move, and whether crews refuse to sail (seafarers can have the right to decline warlike areas). Lenders also care: the loan requires the ship to be insured, and mortgagee's interest insurance protects the bank if the owner's cover fails.",
     terms=["war-risk", "listed-areas", "hm", "mii"], go=["map:sea/hormuz", "tool:voyage"], c="Marine insurance")

rule(id="casualty", seg=["insurance"], m=["fire", "fires", "ablaze", "blaze", "explosion", "grounding", "grounded", "aground", "collision*", "collided", "sank", "sinks", "sinking", "sunk", "ashore", "beached", "capsiz*", "flood*", "engine failure", "blackout", "grunnstøt*", "kollisjon*", "brann", "forlis"],
     x=["fire service"],
     t="A ship casualty",
     b="Several covers react at once. Hull and machinery (H&M) pays for damage to the ship itself; P&I covers liabilities to others, such as pollution, wreck removal, crew injury and damage to other ships or docks. If cargo and ship are saved by a deliberate sacrifice or expense, general average makes cargo owners share the cost. Salvors are paid under 'no cure, no pay', often on Lloyd's Open Form.",
     w="Watch whether general average is declared (cargo owners must then post security) and whether the ship becomes a constructive total loss.",
     terms=["hm", "pi", "ga", "salvage", "total-loss"], go=[], c="Marine insurance")

rule(id="salvage", seg=["insurance"], m=["salvage*", "salvor*", "wreck*", "refloat*", "towed", "towing", "lloyd's open form", "=LOF", "=SCOPIC"],
     t="Salvage and wreck removal",
     b="Salvors are rewarded for saving property under 'no cure, no pay' (often Lloyd's Open Form). If pollution threatens and the ship cannot be saved, SCOPIC pays salvors their costs plus a margin, funded by P&I. Removing a wreck ordered by a coastal state is a P&I liability and can cost hundreds of millions.",
     w="Watch who pays: hull underwriters (property saved), cargo (via general average) or the P&I club (wreck and pollution).",
     terms=["salvage", "ga", "pi"], go=[])

rule(id="cyber-gps", seg=["insurance"], m=["gps", "=GNSS", "jamming", "spoofing", "cyber*", "ransomware", "extortion", "hack*", "data breach*"],
     t="Navigation and cyber risk",
     b="Jammed or spoofed GPS makes ships report false positions and raises collision and grounding risk, especially near conflict zones. Cyber attacks on shipping companies are often excluded from standard marine policies (the 'cyber exclusion clause'), so owners need specific cover.",
     w="Watch whether insurers write back cyber cover and whether authorities issue navigation warnings for the area.",
     terms=["hm", "pi", "ais"], go=[])

rule(id="pi-renewal", seg=["insurance"], m=["=P&I", "p&i club*", "general increase", "renewal*", "gard", "skuld", "international group", "=IG", "mutual*", "nordic association"],
     t="P&I clubs and renewals",
     b="P&I clubs are mutual insurers owned by shipowners. Every year on 20 February they set a 'general increase' on premiums based on claims, investment returns and reinsurance costs. The 12 International Group clubs share large claims and buy one of the world's largest reinsurance programmes together. Gard and Skuld are Norwegian members.",
     w="Watch the general increase percentage and large-claim trends (fires on car carriers and big container ships drive them).",
     terms=["pi-club", "ig", "call", "reinsurance"], go=[])

rule(id="ins-market", seg=["insurance"], m=["underwrit*", "insurer*", "reinsur*", "premium*", "loss ratio", "combined ratio", "capacity", "lloyd's", "syndicate*", "=MGA", "broker*"],
     req=[["insur*", "underwrit*", "lloyd's", "marine", "cargo", "hull", "syndicate*", "=MGA", "reinsur*"]],
     t="The marine insurance market",
     b="Marine insurance prices move in cycles: after big losses, capacity leaves and premiums harden; after good years, new capital arrives and rates soften. Underwriters judge each risk by the ship's age, class, flag, trading area and the owner's claims record. A combined ratio above 100% means claims and costs exceed premiums.",
     w="Watch combined ratios from the Nordic insurers and Lloyd's, and who is adding or withdrawing capacity.",
     terms=["underwriter", "combined-ratio", "reinsurance", "lloyds"], go=[])

rule(id="legal", seg=["insurance", "finance", "road"], m=["court", "ruling", "lawsuit", "verdict", "jury", "arbitration", "appeal*", "judge*", "sued", "settlement", "breach", "dømt*", "rettssak", "lagmannsrett*", "høyesterett"],
     t="A legal dispute",
     b="Shipping disputes usually turn on the contract: a charter party, a bill of lading or a shipbuilding contract, most often under English law with London arbitration. Owners can insure their legal costs through freight, demurrage and defence (FD&D) cover. For road transport, CMR rules decide the carrier's liability for lost or damaged goods.",
     w="Watch what the ruling says about who bears the risk: it often changes standard contract wording afterwards.",
     terms=["fdd", "charter-party", "cmr"], go=[])

rule(id="congestion", seg=["freight", "road"], m=["congestion", "congested", "waiting time*", "queue*", "backlog", "delays", "delayed", "dwell", "bottleneck*", "extra week", "waiting", "kø", "forsinkelse*"],
     x=["backlog to", "backlog of", "backlog uptick", "order backlog"],
     t="Congestion and waiting",
     b="Ships or trucks waiting in a queue are not moving cargo, so congestion removes capacity just like scrapping would. That lifts freight rates and triggers demurrage (the charterer pays the owner for extra waiting time) or detention charges on containers and trucks.",
     up={"t": "Waiting times are getting longer", "b": "Effective capacity shrinks: rates rise, demurrage and detention bills grow, and shippers start ordering earlier, which adds to the peak."},
     dn={"t": "Congestion is easing", "b": "Ships and equipment are released back into the market. Expect rates to soften a few weeks later unless demand picks up."},
     w="Watch average waiting days and how many ships are idle at anchor.",
     terms=["congestion", "demurrage", "dnd"], go=["tool:rates"])

rule(id="ports", seg=["freight", "road"], m=["terminal", "port of", "port authority", "concession", "berth*", "quay*", "dredg*", "yard tractor*", "havn*", "kai", "throughput", "port volume*", "cargo record*", "long beach", "los angeles", "rotterdam", "antwerp", "hamburg", "savannah", "ningbo", "singapore"],
     x=["airport"],
     t="Port and terminal investment",
     b="Ports compete for cargo with depth (for bigger ships), crane productivity and hinterland links by rail and road. New capacity takes years and is often financed by terminal operators, carriers or infrastructure funds on long concessions. For trucking, terminal opening hours and gate systems decide turnaround times.",
     w="Watch who owns the terminal: carrier-owned terminals pull that carrier's cargo with them.",
     terms=["transshipment", "thc", "dwell"], go=[])

rule(id="bunkers", seg=["freight"], m=["bunker*", "=BAF", "=VLSFO", "=HSFO", "=MGO", "fuel oil", "marine fuel*", "lng bunkering", "methanol", "biofuel*", "=B24", "=B30"],
     t="Ship fuel (bunkers)",
     b="Fuel is usually the largest voyage cost. On a voyage charter the owner pays it; on a time charter the charterer does, which is why fuel-efficient ships earn higher time-charter rates. Burn rises roughly with the cube of speed, so expensive fuel makes ships slow down, which in turn absorbs fleet capacity.",
     up={"t": "Ship fuel is getting more expensive", "b": "Owners on voyage charters see TCE fall unless freight rates rise too. Ships slow down to save fuel, which ties up more ships and can support rates."},
     dn={"t": "Ship fuel is getting cheaper", "b": "Voyage costs fall and TCE improves at the same freight rate. Ships can afford to speed up, which adds effective supply."},
     w="Try it: change the bunker price in the voyage calculator and watch the best speed change.",
     terms=["bunkers", "slow-steaming", "tce"], go=["tool:voyage"])

rule(id="oil-price", seg=["freight", "offshore", "road"], m=["oil price*", "brent", "=WTI", "crude price*", "opec*", "barrel*", "oljepris*", "oil market"],
     x=["vlcc", "tanker rate*"],
     t="The oil price",
     b="Oil feeds through to almost every part of transport: bunker and diesel prices, oil companies' spending on offshore work, and tanker demand. A price change caused by lost supply (for example a chokepoint) usually raises tanker rates too, while a price fall caused by weak demand hurts both.",
     up={"t": "Oil prices are rising", "b": "Fuel costs rise for ships and trucks within weeks. Oil companies earn more, which over time supports offshore investment, rigs and supply-vessel demand in the North Sea."},
     dn={"t": "Oil prices are falling", "b": "Fuel gets cheaper for hauliers and shipowners, but oil companies may cut drilling and offshore projects, which hits rigs and supply vessels."},
     w="Compare Brent with the diesel price at the pump: taxes and refining margins mean they do not move one-for-one.",
     terms=["bunkers", "pro-diesel", "contango"], go=["tool:effects", "tool:markets"])

rule(id="emissions", seg=["freight", "finance", "road"], m=["=ETS", "eu ets", "fueleu", "fuel eu", "=IMO", "net-zero", "net zero", "carbon*", "=CII", "=EEXI", "emission*", "decarboni*", "greenhouse", "=CO2", "klima*", "utslipp*"],
     t="Emission rules and carbon cost",
     b="Shipping to and from EU ports pays for CO2 under the EU ETS (full emissions within the EU, half on voyages in or out), and FuelEU Maritime sets a falling limit on fuel greenhouse intensity. IMO is working on a global framework. For lenders, the Poseidon Principles compare loan portfolios with climate targets, so a ship's emissions now affect its financing and resale value.",
     w="Watch the EUA carbon price and how charter parties split carbon costs between owner and charterer.",
     terms=["eu-ets", "fueleu", "cii", "imo-nzf"], go=["tool:voyage"], c="Sustainability and regulation")

rule(id="green-tech", seg=["freight", "finance", "road"], m=["ammonia", "hydrogen*", "dual-fuel", "dual fuel", "wind-assist*", "rotor sail*", "battery*", "electric*", "zero-emission", "methanol-ready", "low-emission", "fuel cell*", "biogas", "=HVO"],
     t="New fuels and technology",
     b="A ship ordered today will sail into the 2050s, so owners hedge with dual-fuel engines or 'ready' designs. Green ships cost more up front; the payback depends on fuel prices, carbon costs and whether charterers pay a premium. Banks offer cheaper green or sustainability-linked loans, but a ship on the wrong fuel risks a lower resale value.",
     w="Watch whether charterers sign long contracts for green ships: that is what makes the extra capital cost financeable.",
     terms=["dual-fuel", "wtw", "stranded-asset", "newbuilding"], go=["tool:voyage"], c="Sustainability and regulation")

rule(id="ship-finance", seg=["finance"], req=[["ship*", "vessel*", "fleet", "rig", "rigs", "tanker*", "bulker*", "offshore", "shipping", "rederi*", "=FPSO", "carrier*", "container*", "newbuild*", "owner*", "maritime", "seaways", "drilling"]], m=["loan*", "financing", "finance facility", "credit facility", "refinanc*", "bond*", "lender*", "bank*", "sale-and-leaseback", "leaseback", "leasing", "=SOFR", "margin", "debt", "equity", "share issue", "private placement", "=IPO"],
     x=["central bank*", "world bank", "norges bank", "riverbank*", "bankrupt*"],
     t="How the deal is financed",
     b="Shipping is capital-heavy, so the funding source matters. Banks lend against a mortgage on the ship, typically 50–65% of its value, with a minimum value clause and cash covenants; bonds (often in Oslo), leasing and export credit fill gaps when banks pull back. Lenders judge the borrower by the five Cs: character (track record), capacity (cash flow against debt service), capital (equity at risk), collateral (the ship, charters and insurances) and covenants (the right to act early).",
     w="Look for the margin over SOFR, the tenor and the balloon: a high margin or short tenor signals that lenders see more risk.",
     terms=["five-cs", "vmc", "dscr", "balloon", "sofr", "syndicated-loan"], go=["tool:valuation"], c="Bank finance and credit analysis")

rule(id="sustainable-finance", seg=["finance"], m=["sustainability-linked", "green loan*", "green bond*", "poseidon principles", "=ESG", "transition finance", "=KPI-linked"],
     t="Green and sustainability-linked finance",
     b="In a sustainability-linked loan the margin steps down if the borrower hits agreed targets (for example carbon intensity) and up if it misses. Green loans and bonds can only fund qualifying assets. Banks signed up to the Poseidon Principles report how their shipping loans align with climate targets.",
     w="Check what the targets are and who verifies them; weak targets make the label cosmetic.",
     terms=["sll", "poseidon", "cii"], go=[], c="Sustainable finance")

rule(id="results", seg=["finance", "offshore"], m=["results", "quarter*", "=Q1", "=Q2", "=Q3", "=Q4", "=EBITDA", "profit*", "revenue*", "earnings", "dividend*", "guidance", "net income", "resultat*", "kvartal*", "utbytte"],
     x=["tce", "earnings per day"],
     t="Company results",
     b="For a shipowner, read results in three steps: average TCE earned versus cash breakeven (OPEX, interest and instalments per day), how much of next quarter is already fixed, and net asset value (fleet market value minus net debt). Shares often trade at a discount or premium to NAV, which tells you whether the market believes current ship values. High-dividend owners pay out most free cash flow, so dividends move with the freight market.",
     w="Check contract coverage for the next quarter and whether the company buys or sells ships: that signals what management expects.",
     terms=["ebitda", "breakeven", "nav", "dividend"], go=["tool:voyage", "tool:valuation"], c="Shipping equity and company analysis")

rule(id="contracts", seg=["offshore", "freight", "finance"], m=["backlog", "contract*", "award*", "charter*", "extension", "firm period", "option*", "secures", "wins", "lands", "scope of work", "keeps busy", "time charter", "kontrakt*"],
     x=["truck*", "lastebil*", "concession tender"],
     t="Contracts and backlog",
     b="A contract turns a volatile market into predictable cash flow. Backlog (firm contracts times the day rate) is what lenders and investors value most, because it shows how much revenue is secured. Options give the charterer the right, not the duty, to extend, so they count for less.",
     w="Compare the day rate with the latest fixtures and check how long the firm period is.",
     terms=["backlog", "time-charter", "dayrate", "charter-backed"], go=[])

rule(id="rigs", seg=["offshore"], m=["rig", "rigs", "drillship*", "jack-up*", "jackup*", "semisub*", "semi-submersible*", "dayrate*", "~utili[sz]ation", "drilling"],
     t="The drilling rig market",
     b="Rigs are hired by oil companies at a dayrate. Dayrates follow utilisation: above roughly 85–90%, owners gain pricing power and rates climb fast; below, idle rigs are stacked or scrapped. Rig work in Norway also drives demand for supply vessels and bases along the coast, including around Bergen.",
     w="Watch utilisation for harsh-environment semisubs, the type most used in the Norwegian North Sea.",
     terms=["rig", "dayrate", "backlog", "utilisation"], go=[])

rule(id="osv", seg=["offshore"], m=["=PSV", "=AHTS", "=CSV", "=CSOV", "subsea", "construction vessel*", "=ROV", "supply vessel*", "=DOF", "solstad", "havila", "eidesvik", "offshore vessel*", "=OSV"],
     t="Offshore vessels",
     b="Platform supply vessels (PSV) carry cargo to installations, anchor handlers (AHTS) move rigs, and construction vessels (CSV) install subsea equipment with cranes and ROVs. Few new OSVs have been ordered for a decade, so a busy North Sea or offshore wind season tightens the market quickly. Many owners and bases are in Western Norway.",
     w="Watch spot rates for North Sea PSVs and AHTS, especially in summer when rig moves and construction work peak.",
     terms=["psv", "ahts", "csv", "rov", "dp"], go=[])

rule(id="offshore-wind", seg=["offshore"], m=["offshore wind", "wind farm*", "turbine*", "inter-array", "export cable*", "monopile*", "floating wind", "havvind*", "=WTIV"],
     t="Offshore wind logistics",
     b="Building a wind farm needs installation vessels (WTIVs) for foundations and turbines, cable-lay vessels, and service vessels (CSOVs) that house technicians for years of maintenance. Projects depend on subsidies or auction prices, so interest rates and steel costs decide whether they go ahead.",
     w="Watch auction results and cancellations: each decision moves vessel demand years ahead.",
     terms=["offshore-wind", "csov", "inter-array"], go=[])

rule(id="oil-gas-projects", seg=["offshore"], m=["discovery", "discoveries", "oilfield*", "gas field*", "=FPSO", "=FID", "~licen[cs]e[sd]?", "acreage", "exploration", "exploration well*", "appraisal well*", "wildcat", "tieback*", "plays", "funn", "olje", "gassfelt"],
     t="Oil and gas projects",
     b="A discovery is the start of a long chain: appraisal, a final investment decision (FID), then years of construction and decades of production. In Norway small finds are usually tied back to existing platforms, which keeps supply bases, helicopters and supply vessels busy.",
     w="Watch for the FID: before it, a project is an option, not a commitment.",
     terms=["fpso", "tieback", "ep"], go=[])

rule(id="decom", seg=["offshore"], m=["decommission*", "plug and abandon*", "=P&A", "removal", "fjerning", "disposal"],
     t="Decommissioning",
     b="Old fields must be plugged and platforms removed. On the Norwegian shelf the state shares much of the cost through the tax system. Heavy-lift vessels lift topsides out, and the steel is often recycled at Norwegian yards.",
     w="Watch which fields get removal orders; work comes in campaigns that keep heavy-lift and supply vessels busy.",
     terms=["decommissioning"], go=[])

rule(id="lng", seg=["freight", "offshore"], m=["=LNG", "regas*", "liquefaction", "=FSRU", "lng carrier*", "lng tanker*", "melkøya", "hammerfest"],
     x=["lng bunkering", "lng-fuelled", "lng-powered", "bunkered"],
     t="LNG trade",
     b="LNG carriers move gas cooled to −162 °C from export plants (US, Qatar, Australia, Norway's Hammerfest) to Europe and Asia. US cargoes to Asia must choose between the Panama Canal, Suez or the Cape, so canal problems lengthen voyages. Many new carriers are delivering, which has weighed on spot rates.",
     w="Watch the price gap between Asian (JKM) and European (TTF) gas: it decides where flexible US cargoes go.",
     terms=["lng-carrier", "lng", "ton-miles"], go=["map:sea/route/blng3"])

rule(id="lpg", seg=["freight"], m=["=LPG", "=VLGC", "propane", "butane", "ammonia carrier*"],
     t="LPG shipping",
     b="Very large gas carriers (VLGCs) mainly carry propane and butane from the US Gulf and the Middle East to Asia. US exports have grown fast, and long voyages to Asia via Panama or the Cape absorb many ship-days.",
     w="Watch the US–Asia propane price spread and Panama Canal slots.",
     terms=["lpg"], go=["map:sea/panama"])

rule(id="arctic", seg=["freight"], m=["northern sea route", "=NSR", "arctic", "svalbard", "ice class", "ice-class", "polar"],
     t="Arctic routes",
     b="The Northern Sea Route along Russia's coast can cut Asia–Europe distance substantially in summer, but it needs ice-class ships, Russian permits and expensive insurance, and is affected by sanctions. It remains a niche, seasonal route.",
     w="Watch the length of the ice-free season and which flags still use it.",
     terms=["chokepoint"], go=["map:sea/route/asia-europe"])

rule(id="detention", seg=["insurance", "freight"], req=[["ship*", "vessel*", "tanker*", "bulker*", "carrier*", "crew", "port state", "=PSC", "master", "flag*", "freighter*", "boxship*"]], m=["detain*", "detention", "arrest*", "port state control", "=PSC", "inspection*", "impound*"],
     x=["detention charge*", "demurrage and detention"],
     t="Ships detained or arrested",
     b="Port State Control can detain substandard ships until defects are fixed, which hurts the owner's record and future inspection rate. A ship can also be arrested by creditors to secure a claim; lenders protect themselves with a mortgage and mortgagee's interest insurance in case the owner's cover fails.",
     w="Watch whether the flag or class society is named: repeated detentions push flags onto blacklists.",
     terms=["psc", "flag-state", "class-society"], go=[])

rule(id="crew", seg=["insurance"], m=["crew*", "seafarer*", "sailors", "crew change", "overboard", "abandon*", "=MLC", "mannskap*", "sjøfolk"],
     t="Seafarers",
     b="Crew injury, illness, repatriation and death are among the largest P&I claim categories. The Maritime Labour Convention (MLC) sets minimum rights, and owners must hold financial security against abandoning crews.",
     w="Watch who covers the cost: P&I for liabilities, war-risk crew cover for attacks.",
     terms=["pi", "mlc"], go=[])

rule(id="liner-ops", seg=["freight"], m=["blank sailing*", "schedule reliab*", "transit time*", "port omission*", "service*", "loop*", "alliance*", "gemini", "premier alliance"],
     req=[["container*", "liner*", "carrier*", "service*", "maersk", "msc", "cma cgm", "hapag", "cosco", "evergreen", "hmm", "arkas", "zim"]],
     t="Liner services and capacity management",
     b="Container lines run fixed weekly loops. To defend rates, they cancel individual sailings (blank sailings), skip ports, or restructure alliances; to win share, they add services. Schedule reliability tells shippers how often ships arrive on time.",
     w="Watch announced blank sailings for the next four weeks: they lead spot rates.",
     terms=["liner", "blank-sailing", "port-omission"], go=["tool:rates"])

rule(id="tariffs", seg=["freight", "road"], m=["tariff*", "trade war", "import duties", "duties on", "=USTR", "port fee*", "section 301", "import tax*", "customs duty", "trade deal*"],
     x=["tariffavtale*", "tariffoppgjør*"],
     t="Tariffs and trade policy",
     b="Tariffs change what is traded and where. Importers often rush cargo before a tariff starts (front-loading), which lifts freight rates briefly, then volumes drop. Trade diverted through third countries can add ton-miles. Fees on Chinese-built or -operated ships in US ports also change which ships serve which trades.",
     w="Watch for front-loading: high volumes just before a deadline are often borrowed from later months.",
     terms=["ton-miles", "incoterms"], go=["tool:effects"])

rule(id="shipbuilding", seg=["freight", "finance"], m=["shipbuilding", "shipyard*", "yard*", "hanwha", "hd hyundai", "samsung heavy", "fincantieri", "austal", "cssc", "ship block*", "hull block*", "verft*"],
     x=["yard tractor*"],
     t="Shipyard capacity",
     b="Yard capacity limits how fast the fleet can grow. When the big yards in China, Korea and Japan are full for years, newbuilding prices rise and owners turn to second-hand ships instead. Governments in the US and Europe now subsidise yards for security reasons.",
     w="Watch the earliest available delivery slot: a long wait protects today's ships from new competition.",
     terms=["newbuilding", "orderbook", "refund-guarantee"], go=[])

rule(id="norway-maritime", seg=["freight", "finance"], req=[["norway", "norwegian", "norsk*", "norge", "norges", "rederiforbundet", "=NIS", "tonnasjeskatt", "nor-shipping", "enova"]], m=["rederiforbundet", "tonnasjeskatt", "tonnage tax", "=NIS", "norsk internasjonalt skipsregister", "maritim*", "sjøfart*", "nor-shipping", "skipsfart*"],
     t="Norwegian maritime policy",
     b="Norway is a large shipping nation with its own international register (NIS) and a tonnage tax regime, where companies pay tax based on fleet size instead of profit. Changes to these rules, or to support for green shipping through Enova, directly affect Norwegian owners' competitiveness.",
     w="Watch the state budget and the Norwegian Shipowners' Association's response.",
     terms=["flag-state"], go=[])

rule(id="security-spend", seg=["freight"], m=["navy", "naval", "unmanned", "=USV", "frigate*", "warship*", "~defen[cs]e", "carrier strike group", "nato"],
     t="Security at sea",
     b="Naval escorts and patrols lower the risk of attacks, which can reduce war-risk premiums and bring owners back to an area. Navies are also becoming customers for shipyards and unmanned vessels, which competes with commercial orders for yard capacity.",
     w="Watch whether escorts lead to more transits; owners and insurers follow evidence, not announcements.",
     terms=["war-risk", "listed-areas"], go=["map:sea/red-sea"])

rule(id="weather", seg=["freight", "road", "insurance"], m=["hurricane*", "typhoon*", "storm*", "cyclone*", "fog", "uvær", "flom", "ekstremvær", "snow*", "snø*", "ice", "is på"],
     x=["ice class", "ice-class"],
     t="Weather disruption",
     b="Storms close ports and roads, and ships wait or reroute: capacity disappears for days. On land, Norwegian mountain passes close or switch to convoy driving in bad weather, adding hours to a trip. Insurers see weather as a frequency risk for cargo damage and groundings.",
     w="Watch the backlog afterwards: ports and roads need days to clear the queue, which can lift rates locally.",
     terms=["congestion", "laytime"], go=["map:road"])

# ------------------------------------------------------------------ road transport
rule(id="diesel", seg=["road"], m=["diesel*", "drivstoff*", "veibruksavgift*", "road usage tax", "dieselbrøl*", "fuel surcharge*", "dieseltillegg", "pump price*", "fuel price*", "fuel cost*", "drivstoffpris*"],
     t="Diesel and fuel costs for trucks",
     b="For a Norwegian haulier, fuel and the driver's wage are the two largest costs of a trip. Contracts often include a fuel clause or surcharge that adjusts the price monthly, so hauliers with fixed prices and no clause carry the risk. Norway's road usage tax on diesel is set in the state budget each autumn.",
     up={"t": "Diesel is getting more expensive", "b": "Hauliers without a fuel clause lose margin immediately; those with one pass it on after a lag. Customers then push for electric or HVO alternatives, and road loses some ground to rail and sea on long distances."},
     dn={"t": "Diesel is getting cheaper", "b": "Margins improve for hauliers on fixed prices; fuel surcharges fall back. Cheaper diesel weakens the cost case for electric trucks in the short run."},
     w="Try it: change the diesel price in the truck trip calculator and see the share of fuel in the trip cost.",
     terms=["road-tax", "fuel-surcharge", "pro-diesel"], go=["tool:truck"])

rule(id="tolls", seg=["road"], m=["bompeng*", "bomring*", "bomstasjon*", "autopass", "vegprising", "road pricing", "toll road*", "road toll*", "ferjepris*", "ferry price*", "ferjetakst*"],
     t="Tolls and ferry prices",
     b="Tolls in Norway often charge heavy vehicles two to three times the car rate, with discounts for zero-emission trucks in many projects. On routes with ferries, such as the E39 along the west coast, ferry tickets add a large and fixed cost per trip. Who pays depends on the contract: tolls are usually passed on to the customer.",
     w="Try it: compare the toll share of a Bergen–Oslo trip with Bergen–Stavanger in the truck calculator.",
     terms=["autopass", "road-tax"], go=["tool:truck", "map:road/E39"])

rule(id="customs", lang="no", seg=["road"], m=["toll", "tollvesen*", "tolldeklar*", "tollkontroll*", "tollstasjon*", "digitoll", "grensepassering*", "svinesund"],
     t="Customs at the border",
     b="Norway is outside the EU customs union, so every truck crossing to Sweden or Finland needs customs declarations. Digitoll requires the goods to be reported electronically before the truck arrives, and missing paperwork means waiting at the border. Most freight by road to Europe passes Svinesund on the E6.",
     w="Watch queues and system problems at Svinesund and Ørje: one hour of waiting costs the haulier a driver hour and can break the driving-time plan.",
     terms=["digitoll", "customs-transit"], go=["map:road/E6", "tool:truck"])

rule(id="budget-policy", seg=["road"], m=["statsbudsjett*", "state budget", "støre", "regjering*", "minister*", "stortinget", "=NTP", "nasjonal transportplan", "samferdsel*", "politiker*", "parliament", "government"],
     t="Politics and the state budget",
     b="The government presents the state budget each October and Parliament settles it before Christmas. It sets the road usage tax on fuel, toll and ferry support, and money for road building in the National Transport Plan (NTP). Industry organisations like NLF lobby on all of these.",
     w="Watch the final budget agreement in December: what the government proposes in October often changes in the negotiations.",
     terms=["road-tax"], go=["tool:effects"])

rule(id="electric-trucks", seg=["road"], m=["el-lastebil*", "elektrisk lastebil*", "electric truck*", "battery-electric", "=BEV", "hydrogen truck*", "lading*", "ladeanlegg*", "ladestasjon*", "charging", "megawatt charging", "=MCS", "enova", "nullutslipp*", "zero-emission truck*"],
     x=["bill of lading"],
     t="Electric trucks: does it pay?",
     b="Electric trucks cost more to buy but less to run, especially in Norway with cheap power, toll discounts and Enova grants. The deal breakers are range, charging time against the driver's breaks, and the battery's weight eating into payload. Regional distribution switches first; long-haul over mountain passes comes later.",
     w="Watch charging on main corridors like the E6, E16 and E39: high-power truck charging along a route decides whether long-haul electric works.",
     terms=["electric-truck", "mcs", "driving-rest"], go=["tool:truck"])

rule(id="autonomous", seg=["road"], m=["driverless", "autonomous", "self-driving", "selvkjørende", "waabi", "aurora", "kodiak", "robotruck*", "automation"],
     t="Self-driving trucks",
     b="The driver is one of the largest costs per trip and is limited by driving-time rules. Autonomous trucks promise to cut both, starting on simple motorway corridors in the US. In Norway, weather, narrow roads and ferries make it harder, and the rules are not yet in place.",
     w="Watch where they run without a safety driver, and on which kinds of roads.",
     terms=["driving-rest"], go=["tool:truck"])

rule(id="drivers", seg=["road"], m=["sjåfør*", "driver shortage", "truck driver*", "driver pay", "driver wage*", "lærling*", "apprentice*", "wage*", "lønn", "lønna", "lønnsnivå*", "lønnsvekst", "minstelønn*", "best betalte", "allmenngjør*", "tariffavtale*", "yrkessjåfør*", "yrkeskompetanse"],
     x=["driverless"],
     t="Drivers and wages",
     b="Wages are the largest single cost in Norwegian road transport. Minimum pay for drivers in goods transport is set by general application of the collective agreement, which also covers foreign drivers doing work in Norway. A shortage of qualified drivers pushes wages up and limits how fast hauliers can grow.",
     w="Watch the age profile of drivers and the number of new apprentices: the gap decides future capacity.",
     terms=["driver-cpc", "posting", "driving-rest"], go=["tool:truck"])

rule(id="cabotage", seg=["road"], m=["kabotasje", "cabotage", "utenlandske", "foreign truck*", "foreign haulier*", "social dumping", "sosial dumping", "mobility package", "mobilitetspakken", "utekontroll*"],
     t="Foreign trucks and cabotage",
     b="Cabotage is a foreign haulier carrying goods between two places in Norway after an international trip. EU/EEA rules limit it to three trips within seven days, followed by a cooling-off period, and posted drivers must be paid Norwegian minimum wages. Norwegian hauliers argue weak enforcement lets foreign trucks undercut prices.",
     w="Watch control statistics from roadside checks: the share of foreign trucks with errors drives political pressure.",
     terms=["cabotage", "mobility-package", "posting"], go=["map:road/E6"])

rule(id="closures", seg=["road"], req=[["road*", "veg*", "vei*", "~[Rr]v\\.? ?\\d+", "~E ?\\d{1,3}", "fjell*", "mountain pass*", "truck*", "lastebil*", "trafikk*", "tunnel*", "bru", "brua", "stengt", "stenger", "kolonne*", "omkjøring*"]], m=["stengt", "stenger", "stengning*", "kolonne*", "fjellovergang*", "road closure*", "closed", "ras", "skred*", "avalanche*", "hemsedalsfjellet", "haukeli*", "filefjell*", "hardangervidda", "dovrefjell", "saltfjellet", "strynefjellet", "omkjøring*", "detour*", "tunnel*"],
     x=["closed deal", "closed the acquisition"],
     t="Road closures and detours",
     b="Norway has few east–west roads across the mountains, so one closed pass sends trucks on long detours. Each extra hour costs a driver hour and diesel, and can break the driving-time plan, forcing an extra rest. In winter, passes like Haukelifjell, Hemsedalsfjellet and Hardangervidda run convoys or close in bad weather.",
     w="See the alternatives on the road map, then price the detour in the truck calculator.",
     terms=["driving-rest", "bruksklasse"], go=["map:road", "tool:truck"])

rule(id="ferries-e39", seg=["road"], m=["ferje*", "ferge*", "ferry", "ferries", "=E39", "ferjefri*", "bru", "brua", "bruer", "bridge*", "rogfast", "hordfast", "fjordkryss*", "undersjøisk*", "color line", "fjord line", "holland norway", "stena line"],
     t="Ferries and the coastal road",
     b="Ferries are part of Norway's road network. The E39 from Kristiansand to Trondheim still has several crossings, each adding waiting time and a ticket per truck, which is why projects like Rogfast and Hordfast aim to replace them. Ro-ro ferries to Denmark, Germany and the Netherlands also carry trailers without a driver, which saves driver hours and driving-time breaks on the long route south.",
     w="Compare driving time per kilometre on the E39 with the E6: the difference is mostly ferries.",
     terms=["roro", "driving-rest"], go=["map:road/E39", "tool:truck"])

rule(id="road-safety", seg=["road"], req=[["truck*", "lastebil*", "sjåfør*", "driver*", "vogntog*", "tungtransport*", "kjøretøy*", "road*", "veg*", "vei*", "trafikk*"]], m=["kontroll*", "tachograph*", "fartsskriver*", "kjøre- og hviletid*", "driving time*", "hours of service", "=ELD", "dekk*", "vinterdekk*", "kjetting*", "bremse*", "ulykke*", "dødsulykke*", "accident*", "crash*", "rollover", "killed", "fatal*", "safety"],
     t="Safety rules and controls",
     b="EU/EEA driving-time rules limit daily driving to 9 hours (twice a week 10) with a 45-minute break after 4.5 hours, recorded by the tachograph. In Norway, winter tyres and chains are mandatory for heavy vehicles in winter conditions. Breaches mean fines for the driver and can cost the company its operator licence.",
     w="Watch where controls find the most errors: that is where enforcement is tightening.",
     terms=["driving-rest", "tachograph", "operator-licence"], go=["tool:truck"])

rule(id="trucks-oem", seg=["road"], m=["volvo", "scania", "daimler", "mercedes", "=MAN", "iveco", "=DAF", "renault trucks", "kenworth", "peterbilt", "freightliner", "lastebil*", "importør*", "trailer*", "semitrailer*", "kögel", "schmitz", "drivlin*", "powertrain*", "modellserie*"],
     req=[["truck*", "lastebil*", "trailer*", "semitrailer*", "launch*", "model*", "modell*", "drivlin*", "importør*", "kögel", "schmitz", "volvo", "scania"]],
     t="Trucks and trailers",
     b="A truck is a capital investment the haulier depreciates over about five to eight years. Fuel use, uptime and resale value decide the total cost of ownership more than the purchase price. New models, especially electric ones, are compared on range, payload and charging speed.",
     w="Watch second-hand truck prices: they show whether diesel trucks keep their value as electric ones arrive.",
     terms=["electric-truck", "vogntog", "modulvogntog"], go=["tool:truck"])

rule(id="us-trucking", lang="en", seg=["road"], m=["truckload", "=TL", "=LTL", "linehaul", "tender rejection*", "freight recession", "load-to-truck", "=DAT", "trucking", "spot market", "contract rate*"],
     req=[["truck*", "=TL", "=LTL", "linehaul", "trucking"]],
     t="US trucking market",
     b="US trucking is split into truckload (one customer per truck) and less-than-truckload (shared trucks via terminals). Spot rates react first, contract rates follow months later. A rising tender rejection rate means carriers refuse contract loads to take better-paid spot work, an early sign of a tighter market.",
     up={"t": "US truck rates are rising", "b": "Capacity is tightening, often after carriers exit during a downturn. Contract rates usually follow within one or two quarters."},
     dn={"t": "US truck rates are falling", "b": "More trucks than loads. Small carriers with thin margins exit first, which eventually tightens the market again."},
     w="The same cycle exists in Norway, just smaller: watch NLF's cost index against freight prices.",
     terms=["ftl", "ltl", "spot-market"], go=["tool:truck"])

rule(id="fraud", seg=["road", "insurance"], m=["fraud*", "double broker*", "cargo theft", "theft", "stolen", "tyveri*", "svindel*", "verdict", "scam*"],
     t="Fraud and theft",
     b="Cargo theft and fake carriers ('double brokering') are a growing problem in road freight. Under CMR the carrier is liable for loss up to a weight-based limit, so high-value goods need separate cargo insurance. Checking the carrier's identity and licence is the shipper's first defence.",
     w="Watch whether courts hold brokers liable for the carriers they hire: that changes how freight is subcontracted.",
     terms=["cmr", "cargo-insurance", "forwarder"], go=[])

rule(id="rail", seg=["road"], m=["intermodal", "rail*", "jernbane*", "godstog*", "cargonet", "alnabru", "railway*", "freight train*"],
     t="Rail versus road",
     b="Rail competes with trucks on long distances, such as Oslo–Bergen, Oslo–Trondheim and Oslo–Narvik, while trucks do the first and last mile. Rail wins on cost per tonne when trains are full and on time; when the line is closed or capacity is short, cargo moves back to road.",
     w="Watch reliability on the Bergen line and the Dovre line: each closure pushes freight back onto the E16 and E6.",
     terms=["intermodal", "last-mile"], go=["map:road"])

rule(id="logistics-deals", seg=["road"], m=["acquir*", "acquisition", "merger", "partnership", "kjøper", "oppkjøp*", "fusjon*", "samarbeid*", "deal"],
     req=[["logistic*", "transport*", "freight", "truck*", "haulier*", "carrier*", "speditør*", "lastebil*", "3pl", "warehouse*", "lager"]],
     x=["ship*", "vessel*", "rig*"],
     t="Consolidation in logistics",
     b="Logistics is fragmented: many small hauliers, a few large forwarders. Large players buy smaller ones to get density on routes and customers, which lowers cost per shipment. For small hauliers, a big customer or partner can be both a lifeline and a price squeeze.",
     w="Watch which routes or customer groups the buyer gains: that is usually the point of the deal.",
     terms=["3pl", "forwarder"], go=[])

rule(id="last-mile", seg=["road"], m=["distribusjon*", "avisdistribusjon", "distribution", "pakke*", "parcel*", "last mile", "last-mile", "e-commerce", "netthandel*", "posten", "postnord", "helthjem", "budbil*", "varebil*", "van", "vans", "levering*"],
     req=[["distribusjon*", "avisdistribusjon", "parcel*", "pakke*", "netthandel*", "e-commerce", "van", "vans", "varebil*", "budbil*", "posten", "postnord", "helthjem", "last mile", "last-mile", "avis*"]],
     t="Distribution and last mile",
     b="The last mile is the most expensive part of a delivery per kilo, because vans stop often and carry little. Density decides profitability: more parcels per stop and per route. City rules on zero-emission zones and loading times are pushing vans and small trucks to electric first.",
     w="Watch parcel volumes and delivery prices from Posten/Bring and competitors.",
     terms=["last-mile", "cross-docking"], go=["tool:truck"])

rule(id="seafood", seg=["road"], m=["sjømat*", "laks", "laksen", "lakse*", "salmon", "seafood", "fiskeeksport*", "oppdrett*", "aquaculture"],
     t="Seafood: Norway's big road export",
     b="Fresh salmon is one of Norway's largest exports, and most of it leaves by truck towards Europe, much of it over the E6 at Svinesund. It is time-critical: the fish must reach markets within days, so hauliers drive in teams and pay for speed. Changes in salmon volumes move demand for reefer trucks on the long routes south.",
     w="Watch harvest volumes and border waiting times; a slow border costs freshness and money.",
     terms=["reefer", "driving-rest"], go=["map:road/E6"])

rule(id="interest-fx", seg=["finance", "road"], m=["interest rate*", "rente", "renten", "renteheving*", "rentekutt*", "norges bank", "=Fed", "federal reserve", "inflation", "inflasjon", "kronekurs*", "weak krone", "svak krone", "currency", "valuta*", "exchange rate*"],
     t="Interest rates and currency",
     b="Ships are bought with debt and earn in US dollars, so higher interest rates raise financing costs and lower asset values (future earnings are discounted harder). A weak krone helps Norwegian exporters and shipowners with NOK costs, but makes imported trucks, parts and fuel more expensive for hauliers.",
     w="Watch the spread between ship earnings and financing cost: when it narrows, fewer ships are ordered.",
     terms=["sofr", "nibor", "basis-point"], go=["tool:markets"])

rule(id="china", seg=["freight"], m=["china", "chinese", "beijing"],
     req=[["steel", "property", "import*", "export*", "demand", "stimulus", "ore", "coal", "economy", "growth", "factory", "factories", "manufactur*"]],
     t="China's demand",
     b="China imports most of the world's seaborne iron ore and a large share of its coal and crude, so its steel output and energy policy steer dry bulk and tanker demand. Stimulus for construction lifts ore imports; a property slump weakens them.",
     w="Watch monthly steel output and port stockpiles of iron ore.",
     terms=["dry-bulk", "ton-miles"], go=["map:sea/route/c5", "tool:rates"])

rule(id="port-strikes", seg=["freight", "road"], m=["port strike*", "dock strike*", "dockworker*", "longshore*", "=ILA", "=ILWU", "walkout", "streik*", "workers strike", "industrial action"],
     t="Strikes and labour action",
     b="Even a short port strike leaves a backlog of ships that takes weeks to clear, which works like a sudden capacity cut: rates rise and cargo is diverted. In Norway, strikes in transport or at terminals can stop distribution within days.",
     w="Watch the length of the backlog after the strike ends, not only the strike itself.",
     terms=["congestion", "demurrage"], go=["tool:rates"])


rule(id="charter-market", seg=["freight", "finance"], m=["contex", "=HARPEX", "charter assessment", "charter rate*", "time charter rate*", "tonnage provider*", "non-operating owner*", "=NOO", "charter market", "period rate*", "1-year t/c", "one-year time charter"],
     t="The container ship charter market",
     b="Container lines own only part of their fleets; the rest is chartered from non-operating owners (many of them German, Greek and Norwegian) on time charters. Indices like ConTex and Harpex track those charter rates. Long, well-paid charters to strong liner companies are what banks and investors finance against.",
     up={"t": "Charter rates for container ships are rising", "b": "Lines need extra ships, often because of longer routings or congestion, and lock them in for years. Owners can refinance and sell older ships at good prices."},
     dn={"t": "Charter rates for container ships are falling", "b": "Lines return ships at the end of charters instead of renewing. Older ships go idle or to scrap; owners with long fixed charters are protected until those contracts end."},
     w="Look at the charter length as well as the rate: a short charter at a high rate carries more re-letting risk.",
     terms=["time-charter", "charter-backed", "liner"], go=["tool:voyage"])

rule(id="people", seg=["road", "freight", "finance", "insurance", "offshore"], m=["names", "appoints", "appointed", "new head", "new ceo", "=CEO", "steps down", "retire*", "chief executive", "chairman", "ny sjef", "ny daglig leder", "ansetter", "tiltrer", "går av"],
     t="A change at the top",
     b="Leadership news matters when it signals a change of strategy. A new chief executive often reviews the business within the first year: selling assets, renewing the fleet or entering new markets. In insurance, senior underwriter moves can shift which risks a market is willing to write.",
     w="Watch the first strategy update after the new leader starts.",
     terms=[], go=[])

rule(id="digital", seg=["road", "freight"], m=["=AI", "artificial intelligence", "kunstig intelligens", "software", "digitali?*", "digiti?*", "digital*", "platform*", "=TMS", "visibility", "tracking", "app", "automat*", "data", "booking process", "load matching", "freight tech", "algorithm*"],
     x=["data breach*"],
     req=[["truck*", "fleet*", "freight", "logistic*", "shipment*", "carrier*", "shipper*", "transport*", "lastebil*", "frakt*", "booking*", "load*", "warehouse*", "lager*"]],
     t="Digital tools in logistics",
     b="Most software in transport tries to do one of three things: fill trucks and ships better (less empty running), cut admin per shipment (booking, documents, invoicing), or give customers live tracking. The gains are real but small per trip, so they matter most for large fleets with thin margins.",
     w="Ask which cost line the tool actually cuts, and by how much per trip.",
     terms=["empty-running", "backhaul", "3pl"], go=["tool:truck"])

rule(id="payment", seg=["road"], m=["betaling*", "betalingsfrist*", "faktura*", "likviditet*", "pengene", "payment terms", "cash flow", "late payment*", "konkurs*", "bankrupt*", "insolven*", "chapter 11", "oppbud"],
     t="Getting paid: cash flow in trucking",
     b="Hauliers pay drivers, fuel and tolls straight away but often wait 30–90 days for the customer to pay. With thin margins, long payment terms squeeze cash, and a customer's bankruptcy can take down a small haulier. Some sell invoices to a factoring company to get paid faster, at a cost.",
     w="Watch bankruptcy numbers in transport: they rise when costs jump faster than freight prices.",
     terms=["fuel-surcharge"], go=["tool:truck"])

rule(id="warehouse", seg=["road"], m=["lager", "lageret", "hovedlager*", "sentrallager*", "warehouse*", "distribution cent*", "logistikksenter*", "godsterminal*", "logistikkterminal*", "solcelle*", "solar", "kraftverk", "batteri*"],
     req=[["lager", "lageret", "hovedlager*", "sentrallager*", "warehouse*", "distribution cent*", "logistikksenter*", "godsterminal*", "logistikkterminal*"]],
     t="Warehouses and terminals",
     b="Where a warehouse sits decides how far trucks drive: most Norwegian distribution starts from the Oslo area, with regional terminals in Bergen, Stavanger, Trondheim and the north. Large roofs now carry solar panels and batteries that also feed charging for electric trucks, turning terminals into small power stations.",
     w="Watch where new terminals are built: they shift truck traffic onto specific roads for decades.",
     terms=["cross-docking", "3pl", "electric-truck"], go=["map:road"])

rule(id="cold-chain", seg=["road", "freight"], m=["cold chain", "cold-chain", "reefer*", "temperature-controlled", "kjøle*", "frys*", "termo*", "pharma*"],
     t="Temperature-controlled transport",
     b="Food, fish and medicine need an unbroken cold chain, using reefer trucks and containers with their own cooling units. Pharma adds strict documentation (Good Distribution Practice). Rates are higher than for dry freight because the equipment costs more and delays are expensive.",
     w="Watch reefer capacity before seafood and holiday peaks.",
     terms=["reefer"], go=["map:road/E6"])

rule(id="nlf", lang="no", seg=["road"], m=["=NLF", "lastebileierforbund*", "=NHO LT", "nho logistikk", "transportbedrift*", "bransjeorganisasjon*"],
     t="Who speaks for the hauliers",
     b="Norges Lastebileier-Forbund (NLF) represents Norwegian trucking companies, many of them small; NHO Logistikk og Transport represents larger firms. They lobby on diesel tax, tolls, cabotage enforcement and driver training, and NLF publishes a cost index for road transport that many contracts use for price adjustment.",
     w="Compare their demands with what ends up in the state budget.",
     terms=["road-tax", "cabotage"], go=["tool:truck"])

# ------------------------------------------------------------------ course topics: finance, credit, sustainability
NOT_ROAD = ["truck*", "trucking", "lastebil*", "haulier*", "hauler*", "transportør*", "=LTL", "freight broker*", "3pl", "parcel*"]
SHIPWORDS = ["ship*", "vessel*", "rig", "rigs", "tanker*", "bulker*", "offshore", "shipping", "rederi*", "=FPSO", "carrier*", "containership*", "boxship*", "newbuild*", "shipowner*", "maritime", "seaways", "drilling", "driller*", "seadrill", "borr", "odfjell", "frontline", "hafnia", "torm", "golden ocean", "dof", "solstad"]

rule(id="distress", seg=["finance", "offshore"], req=[SHIPWORDS], x=NOT_ROAD,
     m=["restructur*", "standstill", "forbearance", "chapter 11", "debt-for-equity", "debt for equity", "bondholder*", "creditor*", "covenant breach*", "covenant waiver*", "waiver*", "default*", "missed payment*", "missed coupon*", "insolven*", "bankrupt*", "konkurs*", "rekonstruksjon*", "haircut*", "amend and extend", "liquidity crunch"],
     t="Debt trouble: who gets paid first?",
     b="When earnings fall below cash break-even, a loan moves from normal to watch list, then forbearance and possibly default. Banks rarely want to sell a ship into a weak market at a low price, so they often agree a standstill or amend-and-extend instead. If that fails, the order matters: maritime liens such as crew wages and salvage rank ahead of the mortgage, secured lenders come before bondholders, and shareholders come last. In a debt-for-equity swap, lenders become owners and old shareholders are diluted; US Chapter 11 lets a company keep trading while it does this.",
     w="Check how many months of cash the company has, whether lenders or bondholders end up with shares, and whether the ships are sold or kept.",
     terms=["default", "restructuring", "maritime-lien", "chapter-11", "pd-lgd"], go=["tool:valuation"], c="Credit risk and restructuring")

rule(id="hy-bonds", seg=["finance", "offshore"], req=[SHIPWORDS],
     m=["bond*", "nordic bond*", "high-yield", "high yield", "senior secured", "unsecured", "coupon*", "tap issue", "bond issue", "obligasjon*", "pareto", "nordic trustee", "callable", "call option", "bond trustee", "credit rating*", "investment grade", "downgrade*", "upgrade*"],
     x=["central bank*"] + NOT_ROAD,
     t="Shipping bonds",
     b="The Oslo (Nordic) high-yield market lets shipping and offshore companies borrow from investors instead of banks, usually for three to five years with a coupon far above bank margins and no instalments. In return, bond terms set covenants such as minimum liquidity, maximum NIBD/EBITDA, interest cover and often a minimum value clause, and a bond trustee acts for all bondholders. A bond trading below par means investors demand a higher yield, which is the market saying the credit risk has risen.",
     w="Compare the coupon with SOFR plus a bank margin, check whether the bond is secured on ships, and watch the price: a fall well below par often comes before a restructuring.",
     terms=["bond", "bond-trustee", "credit-rating", "nibd-ebitda", "dscr"], go=["tool:valuation"], c="Bond finance")

rule(id="leasing", seg=["finance"], req=[SHIPWORDS], x=NOT_ROAD + ["trailer*"], m=["sale-and-leaseback", "sale and leaseback", "leaseback*", "leasing", "lessor*", "lease financing", "bareboat charter*", "=IFRS 16", "finance lease", "operating lease", "=SFL", "chinese lease*", "chinese leasing"],
     t="Sale-leaseback and leasing",
     b="In a sale-leaseback the owner sells the ship to a lessor, often a Chinese leasing house or a company like SFL, and charters it back on bareboat terms, usually with options or an obligation to buy it back. The owner gets more money up front than a bank would lend and a longer repayment profile, but pays a higher implied interest rate and gives up ownership until the buy-back. With a buy-back obligation the deal is normally treated as debt in the accounts, not a sale. For the lessor, the charterer's credit is the real risk.",
     w="Look at the implied cost compared with a bank loan, the purchase option prices and the length of the bareboat charter.",
     terms=["sale-leaseback", "lease", "bareboat", "capital-structure"], go=["tool:valuation"], c="Leasing")

rule(id="convertibles", seg=["finance", "offshore"], m=["convertible*", "conversion price", "mezzanine", "preferred equity", "hybrid bond*", "junior debt", "subordinated"],
     t="Convertibles and other in-between capital",
     b="Between senior bank debt and equity sits mezzanine capital: junior loans, preferred shares and convertible bonds. A convertible pays a low coupon because investors get the right to swap into shares if the price rises. It is cheaper than straight debt when the company is seen as risky and growing, but it can dilute shareholders later. Offshore drillers have used convertibles to raise money when banks would not lend.",
     w="Compare the conversion price with today's share price: the further above, the less dilution existing shareholders should expect.",
     terms=["convertible", "mezzanine", "capital-structure"], go=[], c="Capital structure and hybrid finance")

rule(id="export-credit", seg=["finance"], m=["export credit*", "=ECA", "=ECAs", "eksfin", "=CIRR", "=KEXIM", "=K-SURE", "=KSURE", "=Sinosure", "=GIEK", "export finance", "eksportfinans*", "eksportkreditt*", "=OECD"],
     req=[SHIPWORDS + ["yard*", "verft*"]],
     t="Export credit for ships",
     b="Export credit agencies, such as Eksfin in Norway, lend or guarantee loans to help buyers order ships or equipment from their country. Under the OECD rules for ships they can cover up to 80% of the contract price, repaid over up to 12 years, often at a fixed CIRR rate, with commercial banks taking part alongside. It makes long, cheap funding available for newbuildings that banks alone would finance on shorter terms.",
     w="Check which country's yard or equipment qualifies, the share covered by the agency, and whether the rate is fixed (CIRR) or floating.",
     terms=["eca", "cirr", "newbuilding", "refund-guarantee"], go=[], c="Export credit and newbuilding finance")

rule(id="mna", seg=["finance"], req=[SHIPWORDS],
     m=["merger", "merge*", "takeover*", "tender offer", "offer premium", "bid premium", "all-share", "share-for-share", "combination", "combine*", "acquir* stake", "stake in", "bid for", "synerg*", "fusjon*", "oppkjøp*", "consolidat*"],
     x=["cargo consolidation", "less than container load"] + NOT_ROAD,
     t="Mergers: does 1 + 1 make more than 2?",
     b="A merger creates value only if the combined company is worth more than the two apart. Value created is the synergies (lower overhead, better fleet use, chartering power, cheaper finance) minus the premium the buyer pays the target's shareholders. In shipping the synergies are often modest, so many deals are all-share mergers priced on net asset value, and the target's shareholders usually capture most of the gain.",
     w="Check the premium against the target's share price and NAV, how the deal is paid for (cash or shares), and what synergies management promises.",
     terms=["mna", "nav", "ipo"], go=[], c="Shipping equity and M&A")

rule(id="equity", seg=["finance"], req=[SHIPWORDS], x=["listed area*"] + NOT_ROAD,
     m=["=IPO", "=IPOs", "listing", "listed on", "euronext*", "oslo børs", "stock exchange", "share price*", "shares", "shareholder*", "private placement*", "share issue", "emisjon*", "børsnotering", "=NYSE", "=Nasdaq", "valuation", "investors"],
     t="Shipping shares and new listings",
     b="A shipping share is a leveraged bet on freight rates and ship values, so prices swing much more than the wider market even if beta is not extreme. Investors compare the share price with net asset value (P/NAV) and the dividend yield. New listings and share issues cluster near cycle peaks, when valuations are high: the question for a buyer is whether the market is already pricing in the good times.",
     w="Compare the share price with NAV per share and check what the money raised is for: buying ships at the top of the market is risky.",
     terms=["ipo", "nav", "private-placement", "beta"], go=["tool:valuation"], c="Shipping equity and M&A")

rule(id="hedging", seg=["finance", "freight"], m=["=FFA", "=FFAs", "forward freight", "freight derivative*", "freight futures", "hedg*", "swap", "swaps", "bunker swap*", "=BFA", "interest rate swap*", "fixed rate", "collar*", "=SGX", "=EEX", "paper market"],
     req=[SHIPWORDS + ["freight", "bunker*"]], x=["crew swap*", "hedge fund*"] + NOT_ROAD,
     t="Hedging freight, fuel and interest",
     b="Shipping risk can be partly locked in with derivatives. Forward freight agreements (FFAs) settle against Baltic Exchange route rates, so an owner can sell forward to secure earnings and a charterer can buy to fix costs; most are cleared through exchanges such as SGX or EEX. Bunker swaps fix the fuel price, and interest rate swaps turn a floating SOFR loan into a fixed rate. The catch is basis risk: the ship's actual earnings or route may not match the index used.",
     w="Check what is being hedged and for how long, and whether the index matches the company's real trade.",
     terms=["ffa", "swap", "term-structure", "contango"], go=["tool:rates"], c="Risk management and derivatives")

rule(id="charter-types", seg=["freight", "finance"], m=["voyage charter*", "time charter*", "timecharter*", "bareboat*", "=T/C", "=TC", "period charter*", "contract of affreightment", "=COA", "spot market", "spot exposure", "fixed-rate charter*", "index-linked"],
     t="Which contract, which risk?",
     b="The contract decides who pays what and who carries market risk. In a voyage charter the owner pays fuel, port costs and canal dues and earns freight per tonne; in a time charter the charterer pays those voyage costs and hires the ship per day, while the owner still pays OPEX (crew, maintenance, insurance); in a bareboat charter the charterer also pays OPEX and runs the ship, so the owner only finances it. Time-charter equivalent (TCE) converts all of them to the same daily figure.",
     w="Check the length of the contract and the counterparty: a long time charter to a strong charterer is what banks lend against most willingly.",
     terms=["voyage-charter", "time-charter", "bareboat", "tce"], go=["tool:voyage"], c="Chartering and cash flows")

rule(id="imo-nzf", seg=["freight", "finance"], req=[["emission*", "carbon*", "climate", "greenhouse", "=GHG", "net-zero", "net zero", "levy", "fuel standard", "decarboni*", "klima*", "utslipp*"]],
     m=["net-zero framework", "net zero framework", "=NZF", "=MEPC", "global fuel standard", "carbon levy", "carbon price", "=IMO"],
     t="IMO's global climate framework",
     b="The IMO Net-Zero Framework would set a global limit on the greenhouse gas intensity of ship fuel, measured well-to-wake, that tightens over time. Ships above the limit would pay for the gap and the cleanest ships would be rewarded. Adoption was planned for October 2025 but postponed by a year after opposition led by the United States. Until a global rule applies, the EU ETS and FuelEU Maritime are the carbon costs owners actually pay.",
     w="Watch whether member states adopt the framework, and how charter parties and newbuilding orders respond: a global carbon price makes dual-fuel ships more valuable.",
     terms=["imo-nzf", "wtw", "eu-ets", "fueleu"], go=["tool:voyage"], c="Sustainability and regulation")

rule(id="cii-rating", seg=["freight", "finance"], req=[SHIPWORDS], m=["=CII", "carbon intensity", "=EEXI", "=EEDI", "=SEEMP", "=AER", "=EEOI", "energy efficiency", "efficiency rating*", "carbon rating*"],
     t="Carbon ratings for ships",
     b="Every ship over 5,000 GT gets an annual CII rating from A to E, based on its CO2 per deadweight-mile (AER) compared with a required level that tightens each year (11% below 2019 levels in 2026). A ship rated D three years in a row or E once must add a corrective plan to its SEEMP. Charterers and banks increasingly prefer A–C ships, so a poor rating can cut both earnings and resale value. Slower speed is the quickest fix.",
     w="Check the ship's age and fuel type: older ships with poor ratings face a widening discount as the requirements tighten.",
     terms=["cii", "aer", "seemp", "eexi"], go=["tool:voyage"], c="Sustainability and regulation")

rule(id="stranded", seg=["finance", "freight"], req=[SHIPWORDS], x=NOT_ROAD, m=["stranded", "transition risk*", "climate risk*", "residual value*", "old tonnage", "older ships", "older vessels", "ageing fleet", "aging fleet", "obsolete", "eco ship*", "eco-design*", "two-tier market", "fuel-efficient ship*"],
     t="Will older ships be left behind?",
     b="A ship's value is the present value of what it will earn plus its value at the end. Tighter emission rules and carbon costs raise the running cost of older, less efficient ships, so charterers pay less for them and their values fall. That risk is relative: the old ship may still trade, but at a discount to newer ones. A dual-fuel or efficient design gives the owner an option to stay competitive whichever fuel wins.",
     w="Compare earnings and values for eco and older ships of the same size: a widening gap is transition risk showing up in prices.",
     terms=["stranded-asset", "dual-fuel", "ltav", "poseidon"], go=["tool:valuation"], c="Sustainability and regulation")

rule(id="us-maritime", seg=["freight", "finance"], m=["jones act", "us shipbuilding", "u.s. shipbuilding", "american shipbuilding", "us-built", "u.s.-built", "american-built", "us-flag*", "u.s.-flag*", "ships act", "ships for america", "maritime action plan", "=USTR", "port fee*", "port entry fee*", "section 301", "chinese-built", "chinese-operated"],
     t="US shipping policy",
     b="The Jones Act reserves trade between US ports for US-built, US-owned, US-flagged and US-crewed ships, which keeps domestic shipping expensive. To rebuild US shipbuilding, the US introduced port fees on Chinese-built and Chinese-operated ships under Section 301 in October 2025; China answered with its own fees on US-linked ships. Both were suspended for one year from 10 November 2025 under a trade truce, so unless extended they would apply again from 10 November 2026.",
     w="Watch whether the suspension is extended and which ships are exposed: carriers have been shifting Chinese-built ships away from US services.",
     terms=["jones-act", "flag-state", "liner"], go=["map:sea"], c="Geopolitics and shipping")

# generic fallbacks: used only when fewer than two specific rules match
rule(id="g-road", generic=True, seg=["road"], m=[],
     t="Who pays and who gains?",
     b="For any road transport story, ask how it changes the cost per trip (driver, fuel, tolls, vehicle) or the volume of goods, and whether the haulier can pass the change on to customers. Small hauliers with fixed prices feel cost changes first.",
     w="Price the change in the truck calculator to see how big it really is.",
     terms=["fuel-surcharge", "driving-rest"], go=["tool:truck"])
rule(id="g-freight", generic=True, seg=["freight"], m=[],
     t="Does this change supply or demand for ships?",
     b="Almost every shipping story moves either demand (cargo volume times distance, ton-miles) or supply (ships, speed, waiting time). Rates react sharply when the fleet is nearly fully used and hardly at all when there is spare capacity.",
     w="Try the same change in the freight rate lab.",
     terms=["ton-miles", "utilisation"], go=["tool:rates"])
rule(id="g-finance", generic=True, seg=["finance"], m=[],
     t="Follow the cash flow",
     b="For shipping and offshore companies, ask three questions: how much the assets earn per day versus their breakeven, how much of that income is already contracted, and how the debt is secured. That is how lenders and investors read the news.",
     w="Try the voyage calculator to turn rates into daily earnings.",
     terms=["breakeven", "tce", "covenant"], go=["tool:voyage"])
rule(id="g-insurance", generic=True, seg=["insurance"], m=[],
     t="Which cover responds?",
     b="Marine insurance is split by risk: H&M for the ship, P&I for liabilities to others, war risk for attacks, cargo insurance for the goods and loss of hire for lost earnings. For each incident, ask which covers react and who ends up paying.",
     w="Look for the words 'general average' or 'total loss' in the full article.",
     terms=["hm", "pi", "war-risk", "loh"], go=[])
rule(id="g-offshore", generic=True, seg=["offshore"], m=[],
     t="What does it mean for vessels and bases?",
     b="Offshore news matters for logistics when it creates work: a contract or project means rig time, supply-vessel trips and cargo through supply bases, many of them in Western Norway. Ask when the work starts and how long it lasts.",
     w="Look for start dates and contract length in the full article.",
     terms=["psv", "supply-base", "backlog"], go=[])

ids = [r["id"] for r in R]
assert len(ids) == len(set(ids)), "duplicate ids"
gl = {t["id"] for t in json.load(open(sys.argv[1] + "/glossary.json"))["terms"]}
for r in R:
    for t in r.get("terms", []):
        assert t in gl, (r["id"], t)
out = Path(sys.argv[1]) / "insights.json"
out.write_text(json.dumps({"rules": R}, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(R), "rules ->", out, out.stat().st_size // 1024, "KB")
