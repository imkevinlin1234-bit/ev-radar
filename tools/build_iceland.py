"""把 tools/raw_iceland.json（fetch_iceland.py 下載的 OSM 原始資料）整理成 App 用的 data/iceland-poi.json。
用法：python tools/build_iceland.py"""
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
raw = json.loads((ROOT / "tools" / "raw_iceland.json").read_text(encoding="utf-8"))["elements"]

def classify(t):
    """回傳 (分類, 子類型)；None 表示不要"""
    if t.get("shop") == "supermarket": return "market", "supermarket"
    if t.get("shop") == "convenience": return "conv", "convenience"
    if t.get("amenity") == "fuel": return "fuel", "fuel"
    n = t.get("natural")
    if n == "waterfall" or t.get("waterway") == "waterfall": return "fall", "waterfall"
    if n == "hot_spring" or t.get("amenity") == "public_bath": return "hot", n or "public_bath"
    if t.get("leisure") == "swimming_pool": return "hot", "pool"
    if n in ("geyser", "volcano", "glacier", "beach", "cave_entrance", "arch", "crater"): return "nature", n
    tour = t.get("tourism")
    if tour == "viewpoint": return "view", "viewpoint"
    if tour in ("museum", "gallery"): return "sight", tour
    if tour == "attraction": return "sight", "attraction"
    if t.get("historic"): return "sight", "historic"
    return None

def addr(t):
    street = " ".join(x for x in (t.get("addr:street"), t.get("addr:housenumber")) if x)
    city = " ".join(x for x in (t.get("addr:postcode"), t.get("addr:city") or t.get("addr:place")) if x)
    return ", ".join(x for x in (street, city) if x)

items = []
for e in raw:
    t = e.get("tags", {})
    lat = e.get("lat", e.get("center", {}).get("lat")); lng = e.get("lon", e.get("center", {}).get("lon"))
    if lat is None: continue
    c = classify(t)
    if not c: continue
    cat, sub = c
    name = t.get("name") or t.get("brand") or ""
    if cat in ("market", "conv", "fuel") and not name: name = {"market": "超市", "conv": "商店", "fuel": "加油站"}[cat]
    if not name: continue
    o = {"i": e["type"][0] + str(e["id"]), "c": cat, "s": sub, "la": round(lat, 5), "lo": round(lng, 5), "n": name}
    for k, src in (("e", "name:en"), ("z", "name:zh"), ("b", "brand"), ("oh", "opening_hours"), ("ph", "phone"), ("ph", "contact:phone"),
                   ("w", "website"), ("w", "contact:website"), ("wd", "wikidata"), ("wp", "wikipedia"), ("f", "fee"), ("ch", "charge"),
                   ("de", "description:en"), ("de", "description"), ("ac", "access"), ("ele", "ele"), ("op", "operator")):
        v = t.get(src)
        if v and k not in o and not (k == "e" and v == name): o[k] = v[:300]
    a = addr(t)
    if a: o["a"] = a
    if cat == "fuel":
        extras = [x for x, k in (("商店", "shop"), ("洗車", "car_wash"), ("廁所", "toilets")) if t.get(k) not in (None, "no")]
        if t.get("self_service") == "yes" or t.get("automated") == "yes": extras.append("自助")
        if t.get("fuel:diesel") == "yes": extras.append("柴油")
        if extras: o["x"] = "、".join(extras)
    items.append(o)

# 同名、同分類、相距 300 m 內的（例如瀑布同時有點和線）只留一個，優先留有維基資料的
def dist(a, b):
    r = math.pi / 180; x = (b["lo"] - a["lo"]) * r * math.cos((a["la"] + b["la"]) / 2 * r); y = (b["la"] - a["la"]) * r
    return 6371000 * math.hypot(x, y)
items.sort(key=lambda o: (0 if o.get("wd") else 1, o["i"]))
kept, seen = [], {}
for o in items:
    key = (o["c"], o["n"].lower())
    if any(dist(o, k) < 300 for k in seen.get(key, [])): continue
    seen.setdefault(key, []).append(o); kept.append(o)

out = ROOT / "data" / "iceland-poi.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"built": __import__("datetime").date.today().isoformat(), "items": kept}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
from collections import Counter
print(len(kept), "items", out.stat().st_size // 1024, "KB", dict(Counter(o["c"] for o in kept)))
print("有營業時間：", dict(Counter(o["c"] for o in kept if o.get("oh"))))
