"""Convert osm.json (Overpass, out geom) into compact local-metre scene data for roma3d.html."""
import json, math, hashlib

LAT0, LON0 = 41.8902, 12.4922          # approx. Colosseum centre (refined below)
HALF = 1000                            # 2 x 2 km
KX = 111320 * math.cos(math.radians(LAT0))
KY = 110574

def proj(p):
    return ((p['lon'] - LON0) * KX, (p['lat'] - LAT0) * KY)

def h01(i, salt=''):
    return int(hashlib.md5(f'{i}{salt}'.encode()).hexdigest()[:8], 16) / 0xffffffff

def join_rings(ways):
    """Join way segments (lists of points) into closed rings."""
    segs = [list(w) for w in ways if len(w) > 1]
    rings = []
    while segs:
        ring = segs.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, s in enumerate(segs):
                if s[0] == ring[-1]: ring += s[1:]
                elif s[-1] == ring[-1]: ring += s[::-1][1:]
                elif s[-1] == ring[0]: ring = s[:-1] + ring
                elif s[0] == ring[0]: ring = s[::-1][:-1] + ring
                else: continue
                segs.pop(i); changed = True; break
        if len(ring) >= 4 and ring[0] == ring[-1]:
            rings.append(ring)
    return rings

def key(p): return (round(p['lat'], 7), round(p['lon'], 7))

def polys_of(el):
    """Return list of (outer, [holes]) in raw lat/lon tuples."""
    if el['type'] == 'way':
        g = [key(p) for p in el.get('geometry', [])]
        return [(g, [])] if len(g) >= 4 and g[0] == g[-1] else []
    outers = join_rings([[key(p) for p in m.get('geometry', [])] for m in el['members'] if m.get('role') == 'outer' and m['type'] == 'way'])
    inners = join_rings([[key(p) for p in m.get('geometry', [])] for m in el['members'] if m.get('role') == 'inner' and m['type'] == 'way'])
    out = [(o, []) for o in outers]
    for inn in inners:   # assign hole to the outer containing its first point
        for o, hs in out:
            if pip(inn[0], o): hs.append(inn); break
    return out

def pip(pt, ring):
    y, x = pt; c = False
    for i in range(len(ring) - 1):
        (y1, x1), (y2, x2) = ring[i], ring[i + 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def loc(ring):
    pts = [((lon - LON0) * KX, (lat - LAT0) * KY) for lat, lon in ring[:-1]]
    return [v for x, y in pts for v in (round(x, 1), round(y, 1))]

def inside(ring):
    return any(abs((lon - LON0) * KX) < HALF and abs((lat - LAT0) * KY) < HALF for lat, lon in ring)

def num(s):
    try: return float(str(s).split(';')[0].replace('m', '').replace(',', '.').strip())
    except Exception: return None

NAMED = {'sand': '#d8c49a', 'white': '#efe9dc', 'yellow': '#e3b660', 'red': '#b8563b', 'orange': '#d8874e',
         'beige': '#e0caa0', 'brown': '#9a6440', 'grey': '#a9a59c', 'gray': '#a9a59c', 'pink': '#e0a090'}
FACADE = ['#d9a066', '#c97b4a', '#e3b778', '#b8563b', '#e8c9a0', '#d48a5c', '#c4a07a', '#e6a96b',
          '#a8462f', '#efd7b0', '#d8b26a', '#cf9474', '#e1bd8f', '#bd6b45', '#f0c987', '#d6a28a']
ROOF_TILE = ['#b5583a', '#a94f34', '#c0673f', '#9e4a30', '#b86245']

d = json.load(open('osm.json'))
els = d['elements']

# Colosseum footprint: centre + orientation from its outline
col = next(e for e in els if e['id'] == 1834818 and e['type'] == 'relation')
cring = polys_of(col)[0][0]
cx = sum(lon for lat, lon in cring[:-1]) / (len(cring) - 1)
cy = sum(lat for lat, lon in cring[:-1]) / (len(cring) - 1)
LAT0, LON0 = cy, cx
pts = [((lon - LON0) * KX, (lat - LAT0) * KY) for lat, lon in cring[:-1]]
sxx = sum(x * x for x, y in pts); syy = sum(y * y for x, y in pts); sxy = sum(x * y for x, y in pts)
angle = 0.5 * math.atan2(2 * sxy, sxx - syy)   # major axis angle (rad, from east, ccw)

def in_colosseum(x, y):
    u = x * math.cos(angle) + y * math.sin(angle); v = -x * math.sin(angle) + y * math.cos(angle)
    return (u / 96) ** 2 + (v / 80) ** 2 < 1

buildings, roads, areas = [], [], []
for e in els:
    t = e.get('tags', {})
    if 'building' in t:
        if e['id'] == 1834818: continue
        b = t['building']
        for outer, holes in polys_of(e):
            if not inside(outer): continue
            o = loc(outer)
            mx = sum(o[0::2]) / (len(o) / 2); my = sum(o[1::2]) / (len(o) / 2)
            if in_colosseum(mx, my): continue
            r = h01(e['id'])
            hgt = num(t.get('height'))
            lv = num(t.get('building:levels'))
            if hgt is None and lv is not None: hgt = lv * 3.6 + 1.5
            ruin = b in ('ruins', 'temple', 'triumphal_arch') or t.get('historic') in ('archaeological_site', 'ruins') or b == 'arch' and t.get('historic')
            if hgt is None:
                if ruin: hgt = 5 + r * 8
                elif b == 'church': hgt = 20 + r * 10
                elif b in ('roof', 'shed', 'kiosk', 'toilets', 'service', 'garage', 'hut'): hgt = 3.5 + r * 2
                elif b == 'arch': hgt = 12
                else: hgt = 14 + round(r * 3) * 3.6
            minh = num(t.get('min_height')) or 0
            if t.get('building:colour') or t.get('colour'):
                c = (t.get('building:colour') or t.get('colour')).lower()
                c = NAMED.get(c, c if c.startswith('#') else None)
            else:
                c = None
            kind = 0
            if ruin:
                kind = 1; c = c or ['#a5634a', '#b9a27f', '#9c5a43', '#c9b38f'][int(r * 4) % 4]
            elif b in ('church', 'cathedral', 'basilica', 'government', 'public', 'university', 'museum'):
                kind = 2; c = c or ['#e8e0cc', '#efe6d2', '#e2d3b4', '#d9c39b'][int(r * 4) % 4]
            c = c or FACADE[int(r * len(FACADE)) % len(FACADE)]
            roof = ROOF_TILE[int(h01(e['id'], 'r') * 5)] if (h01(e['id'], 't') < 0.72 and kind == 0) else ['#cfc6b4', '#bdb5a5', '#d8cfbb'][int(r * 3)]
            if kind == 1: roof = c
            buildings.append({'o': o, 'h': [loc(hh) for hh in holes], 'z': round(hgt, 1), 'm': round(minh, 1), 'c': c, 'r': roof, 'k': kind,
                              **({'n': t['name']} if t.get('name') else {})})
    elif 'highway' in t:
        g = e.get('geometry', [])
        if not g: continue
        hw = t['highway']
        w = {'motorway': 14, 'trunk': 14, 'primary': 13, 'secondary': 11, 'tertiary': 9, 'unclassified': 7, 'residential': 7,
             'living_street': 6, 'service': 4.5, 'pedestrian': 8, 'footway': 2.5, 'path': 2, 'steps': 2.5, 'cycleway': 2.5,
             'track': 3}.get(hw)
        if not w or t.get('area') == 'yes' or t.get('tunnel') == 'yes' or t.get('layer', '0').startswith('-'): continue
        ls = [proj(p) for p in g]
        if not any(abs(x) < HALF and abs(y) < HALF for x, y in ls): continue
        roads.append({'p': [v for x, y in ls for v in (round(x, 1), round(y, 1))], 'w': w,
                      's': 1 if hw in ('footway', 'path', 'steps', 'pedestrian', 'cycleway', 'track') else 0})
    else:
        green = t.get('leisure') in ('park', 'garden', 'pitch') or t.get('landuse') in ('grass', 'forest', 'meadow', 'recreation_ground')
        arch = t.get('historic') == 'archaeological_site'
        if not (green or arch): continue
        for outer, holes in polys_of(e):
            if not inside(outer): continue
            areas.append({'o': loc(outer), 'h': [loc(hh) for hh in holes], 't': 1 if arch and not green else (2 if t.get('landuse') == 'forest' else 0)})

out = {'colosseum': {'angle': round(angle, 4)}, 'origin': [LAT0, LON0], 'half': HALF, 'buildings': buildings, 'roads': roads, 'areas': areas}
s = json.dumps(out, separators=(',', ':'), ensure_ascii=False)
open('scene.json', 'w').write(s)
open('../scene.js', 'w').write('window.SCENE=' + s + ';')
print(len(buildings), 'buildings', len(roads), 'roads', len(areas), 'areas', len(s) // 1024, 'KB', 'angle', math.degrees(angle))
