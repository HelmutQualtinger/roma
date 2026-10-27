"""Shortest bike route on the OSM road graph, preferring asphalt (car roads) over paved footways."""
import json, math, heapq, sys
d = json.load(open(sys.argv[1])); sc = json.load(open(sys.argv[2]))
LAT0, LON0 = sc['origin']; KX = 111320 * math.cos(math.radians(41.8902)); KY = 110574
CAR = {'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'living_street', 'service', 'primary_link', 'secondary_link', 'tertiary_link', 'trunk'}
SOFT = {'pedestrian': 2.5, 'cycleway': 1.5, 'footway': 3.5, 'path': 4}
pos, adj, asph = {}, {}, {}
for e in d['elements']:
    t = e.get('tags', {}); hw = t.get('highway')
    if e['type'] != 'way' or not hw or t.get('area') == 'yes' or t.get('tunnel') == 'yes' or t.get('layer', '0').startswith('-'): continue
    if hw in CAR: w = 1.0
    elif hw in SOFT: w = SOFT[hw]
    else: continue
    if t.get('access') in ('private', 'no') and hw == 'service': continue
    for n, g in zip(e['nodes'], e['geometry']): pos[n] = ((g['lon'] - LON0) * KX, (g['lat'] - LAT0) * KY)
    for a, b in zip(e['nodes'], e['nodes'][1:]):
        L = math.dist(pos[a], pos[b]) * w
        adj.setdefault(a, []).append((b, L)); adj.setdefault(b, []).append((a, L))
        asph[(a, b)] = asph[(b, a)] = hw in CAR
def near(p, car=True):
    cands = [n for n in adj if not car or any(asph[(n, m)] for m, _ in adj[n])]
    return min(cands, key=lambda n: math.dist(pos[n], p))
def path(a, b):
    dist, prev, q = {a: 0}, {}, [(0, a)]
    while q:
        du, u = heapq.heappop(q)
        if u == b: break
        if du > dist[u]: continue
        for v, w in adj[u]:
            if du + w < dist.get(v, 1e18): dist[v] = du + w; prev[v] = u; heapq.heappush(q, (du + w, v))
    out = [b]
    while out[-1] != a: out.append(prev[out[-1]])
    return out[::-1]
# Piazza Venezia -> Via del Teatro di Marcello -> Circo Massimo (Via dei Cerchi) -> Porta Capena -> Via di San Gregorio
# -> around the Colosseum (south, east, north) -> Via dei Fori Imperiali -> Piazza Venezia
WP = [(-805, 585), (-900, 330), (-940, -80), (-757, -238), (-570, -375), (-294, -577), (-200, -330),
      (60, -130), (165, 0), (-110, 100), (-805, 585)]
nodes = [near(p) for p in WP]
full = [nodes[0]]
for a, b in zip(nodes, nodes[1:]): full += path(a, b)[1:]
pts = [pos[n] for n in full]
clean = [pts[0]]
for p in pts[1:]:
    if math.dist(p, clean[-1]) > 2.5: clean.append(p)
def turn(a, b, c):
    h1 = math.atan2(b[1] - a[1], b[0] - a[0]); h2 = math.atan2(c[1] - b[1], c[0] - b[0])
    return abs(math.atan2(math.sin(h2 - h1), math.cos(h2 - h1)))
changed = True
while changed:                      # drop dead-end spikes (waypoint stubs, one-way carriageway switches)
    changed = False
    for i in range(1, len(clean) - 1):
        if turn(clean[i - 1], clean[i], clean[i + 1]) > math.radians(100):
            del clean[i]; changed = True; break
L = sum(math.dist(a, b) for a, b in zip(clean, clean[1:]))
on = sum(math.dist(pos[a], pos[b]) for a, b in zip(full, full[1:]) if asph.get((a, b)))
print(f'{len(clean)} pts, {L:.0f} m, asphalt {on / L * 100:.0f}%', [tuple(round(c) for c in pos[n]) for n in nodes])
sc['route'] = [round(v, 1) for p in clean for v in p]
s = json.dumps(sc, separators=(',', ':'), ensure_ascii=False)
open(sys.argv[2], 'w').write(s); open(sys.argv[3], 'w').write('window.SCENE=' + s + ';')
