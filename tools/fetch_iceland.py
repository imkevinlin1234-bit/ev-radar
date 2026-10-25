"""從 OpenStreetMap（Overpass）下載冰島的景點、超市、超商、加油站，存成 tools/raw_iceland.json。
用法：python tools/fetch_iceland.py"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

Q = """[out:json][timeout:180];
area["ISO3166-1"="IS"][admin_level=2]->.is;
(
  nwr["tourism"~"^(attraction|viewpoint|museum|gallery)$"]["name"](area.is);
  nwr["natural"~"^(waterfall|geyser|hot_spring|volcano|glacier|beach|cave_entrance|arch|crater)$"]["name"](area.is);
  nwr["waterway"="waterfall"]["name"](area.is);
  nwr["amenity"="public_bath"]["name"](area.is);
  nwr["leisure"="swimming_pool"]["name"]["access"!~"private|customers"](area.is);
  nwr["historic"]["name"]["wikidata"](area.is);
  nwr["shop"~"^(supermarket|convenience)$"](area.is);
  nwr["amenity"="fuel"](area.is);
);
out center tags;"""
MIRRORS = ["https://maps.mail.ru/osm/tools/overpass/api/interpreter", "https://overpass-api.de/api/interpreter",
           "https://overpass.private.coffee/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
out = Path(__file__).with_name("raw_iceland.json")
for round_ in range(3):
    for u in MIRRORS:
        try:
            req = urllib.request.Request(u, data=urllib.parse.urlencode({"data": Q}).encode(), headers={"User-Agent": "ev-radar-iceland-build/1.0"})
            t = time.time(); raw = urllib.request.urlopen(req, timeout=200).read()
            j = json.loads(raw); out.write_bytes(raw)
            print(f"OK {u} {len(j['elements'])} elements {len(raw)//1024} KB {time.time()-t:.0f}s"); sys.exit(0)
        except Exception as e:
            print(f"fail {u}: {e}", flush=True)
    time.sleep(20)
sys.exit(1)
