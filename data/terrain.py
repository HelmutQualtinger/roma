"""Build a smoothed heightmap (8 m grid, ±1200 m) from Terrarium elevation tiles in tiles/ and add it to scene.json/scene.js."""
import json, math, base64
import numpy as np
from PIL import Image

sc = json.load(open('scene.json')); LAT0, LON0 = sc['origin']
KX = 111320 * math.cos(math.radians(41.8902)); KY = 110574
Z, N = 15, 2 ** 15
HALF, STEP = 1200, 8
tiles = [l.strip() for l in open('tiles/list.txt')]
xs = sorted({int(t.split('/')[1]) for t in tiles}); ys = sorted({int(t.split('/')[2]) for t in tiles})
mosaic = np.zeros((len(ys) * 256, len(xs) * 256))
for t in tiles:
    _, x, y = map(int, t.split('/'))
    a = np.asarray(Image.open(f'tiles/{Z}_{x}_{y}.png').convert('RGB')).astype(float)
    mosaic[(y - ys[0]) * 256:(y - ys[0] + 1) * 256, (x - xs[0]) * 256:(x - xs[0] + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768

g = np.arange(-HALF, HALF + STEP, STEP); n = len(g)
X, Y = np.meshgrid(g, g)                      # Y = north metres, rows from south to north
lon = LON0 + X / KX; lat = LAT0 + Y / KY
px = ((lon + 180) / 360 * N - xs[0]) * 256 - 0.5
py = ((1 - np.arcsinh(np.tan(np.radians(lat))) / math.pi) / 2 * N - ys[0]) * 256 - 0.5
x0 = np.floor(px).astype(int); y0 = np.floor(py).astype(int); fx = px - x0; fy = py - y0
m = lambda yy, xx: mosaic[yy, xx]
H = (m(y0, x0) * (1 - fx) * (1 - fy) + m(y0, x0 + 1) * fx * (1 - fy) + m(y0 + 1, x0) * (1 - fx) * fy + m(y0 + 1, x0 + 1) * fx * fy)

# morphological opening (min then max over 88 m) strips the building heights that SRTM still contains (DSM -> DTM)
from numpy.lib.stride_tricks import sliding_window_view as win
R = 5
H = win(np.pad(H, R, mode='edge'), (2 * R + 1, 2 * R + 1)).min(axis=(2, 3))
H = win(np.pad(H, R, mode='edge'), (2 * R + 1, 2 * R + 1)).max(axis=(2, 3))
# gaussian blur (sigma 24 m) removes SRTM noise and building bumps but keeps the hills
k = np.exp(-0.5 * (np.arange(-9, 10) * STEP / 24) ** 2); k /= k.sum()
pad = np.pad(H, 9, mode='edge')
H = np.apply_along_axis(lambda r: np.convolve(r, k, 'valid'), 1, pad)
H = np.apply_along_axis(lambda c: np.convolve(c, k, 'valid'), 0, H)

# level platforms for the two procedural monuments
A = sc['colosseum']['angle']; U = X * math.cos(A) + Y * math.sin(A); V = -X * math.sin(A) + Y * math.cos(A)
e = (U / 100) ** 2 + (V / 84) ** 2
ring = (e > 1.6) & (e < 2.6); hc = float(np.percentile(H[ring], 25))
w = np.clip((e - 1.6) / 1.6, 0, 1); w = w * w * (3 - 2 * w)
H = hc * (1 - w) + H * w

# Vittoriano: SRTM keeps the 135 m monument as a bump; clamp terrain inside its footprint below the model's terraces
VX, VY, VR = -789, 522, 0.305
dx, dy = X - VX, Y - VY; LX = dx * math.cos(VR) + dy * math.sin(VR); LD = dx * math.sin(VR) - dy * math.cos(VR)
plaza = (np.abs(LX) < 40) & (LD > -110) & (LD < -60); hf = float(np.percentile(H[plaza], 15))
inside = np.clip(1 - np.maximum(np.abs(LX) - 62, -LD - 45) / 45, 0, 1)        # 1 inside footprint, fades out over 25 m
cap = hf + np.clip(LD, 0, None) * 0.3
H = np.where(H > cap, H * (1 - inside) + cap * inside, H)
H = np.where((LD < 0) & (inside > 0), H * (1 - inside) + hf * inside, H)
print('vittoriano plaza', round(hf, 1))
# Roads: SRTM shows the excavated fora and building blocks, not the street surface. Smooth heights along the
# street network (Laplacian diffusion over OSM nodes, ~140 m) and burn that surface back into the terrain.
def hgrid(x, y):
    fx = np.clip((x + HALF) / STEP, 0, n - 1.001); fy = np.clip((y + HALF) / STEP, 0, n - 1.001)
    j = int(fx); i = int(fy); a = fx - j; b = fy - i
    return (H[i, j] * (1 - a) + H[i, j + 1] * a) * (1 - b) + (H[i + 1, j] * (1 - a) + H[i + 1, j + 1] * a) * b
WID = {'primary': 13, 'secondary': 11, 'tertiary': 9, 'unclassified': 7, 'residential': 7, 'living_street': 6, 'service': 4.5,
       'pedestrian': 8, 'footway': 2.5, 'path': 2, 'cycleway': 2.5, 'track': 3, 'trunk': 14}
osm = json.load(open('osm.json'))
P, E, nid = [], [], {}                                  # densified road points, edges, OSM node -> point index
def pid(key, xy):
    if key not in nid: nid[key] = len(P); P.append([*xy, 0.0, 0.0])
    return nid[key]
for el in osm['elements']:
    t = el.get('tags', {}); w = WID.get(t.get('highway'))
    if el['type'] != 'way' or not w or t.get('area') == 'yes' or t.get('tunnel') == 'yes' or t.get('layer', '0').startswith('-'): continue
    xy = [((g['lon'] - LON0) * KX, (g['lat'] - LAT0) * KY) for g in el['geometry']]
    if not any(abs(x) < HALF and abs(y) < HALF for x, y in xy): continue
    prev = pid(el['nodes'][0], xy[0])
    for k in range(1, len(xy)):
        (x0, y0), (x1, y1) = xy[k - 1], xy[k]; m = max(1, int(math.hypot(x1 - x0, y1 - y0) / 8))
        for q in range(1, m + 1):
            cur = pid(el['nodes'][k], xy[k]) if q == m else pid((el['id'], k, q), (x0 + (x1 - x0) * q / m, y0 + (y1 - y0) * q / m))
            E.append((prev, cur)); prev = cur
    for i in {nid[nn] for nn in el['nodes']} | set(): P[i][3] = max(P[i][3], w)
P = np.array(P); E = np.array(E)
P[:, 3] = np.maximum(P[:, 3], 3)
h = np.array([hgrid(x, y) for x, y in P[:, :2]])
deg = np.bincount(E.ravel(), minlength=len(P)).astype(float)
for _ in range(300):
    acc = np.bincount(E[:, 0], weights=h[E[:, 1]], minlength=len(P)) + np.bincount(E[:, 1], weights=h[E[:, 0]], minlength=len(P))
    h = np.where(deg > 0, 0.5 * h + 0.5 * acc / np.maximum(deg, 1), h)
acc = np.zeros_like(H); wsum = np.zeros_like(H); wmax = np.zeros_like(H)
for (x, y, _, w), hr in zip(P, h):
    r = w / 2 + 14; i0, i1 = int((y - r + HALF) / STEP), int((y + r + HALF) / STEP) + 1; j0, j1 = int((x - r + HALF) / STEP), int((x + r + HALF) / STEP) + 1
    i0, j0 = max(i0, 0), max(j0, 0); i1, j1 = min(i1, n - 1), min(j1, n - 1)
    if i0 > i1 or j0 > j1: continue
    d = np.hypot(X[i0:i1 + 1, j0:j1 + 1] - x, Y[i0:i1 + 1, j0:j1 + 1] - y)
    ww = np.clip(1 - (d - (w / 2 + 4)) / 10, 0, 1)
    acc[i0:i1 + 1, j0:j1 + 1] += ww * hr; wsum[i0:i1 + 1, j0:j1 + 1] += ww
    wmax[i0:i1 + 1, j0:j1 + 1] = np.maximum(wmax[i0:i1 + 1, j0:j1 + 1], ww)
wmax *= np.clip((e - 1.3) / 0.3, 0, 1)                 # keep the Colosseum platform level
H = np.where(wsum > 0, H * (1 - wmax) + acc / np.maximum(wsum, 1e-9) * wmax, H)

print('colosseum', round(hc, 1), 'min', round(H.min(), 1), 'max', round(H.max(), 1))
for name, (la, lo) in {'Piazza Venezia': (41.8960, 12.4826), 'Campidoglio': (41.8934, 12.4828), 'Palatin': (41.8894, 12.4875),
                       'Colle Oppio': (41.8930, 12.4955), 'Celio': (41.8860, 12.4930), 'Fori Imperiali mid': (41.8925, 12.4880)}.items():
    i = int(round(((la - LAT0) * KY + HALF) / STEP)); j = int(round(((lo - LON0) * KX + HALF) / STEP))
    print(name, round(H[i, j], 1))
q = np.round(H * 10).astype('<i2')
sc['terrain'] = {'half': HALF, 'step': STEP, 'n': n, 'dm': base64.b64encode(q.tobytes()).decode()}
s = json.dumps(sc, separators=(',', ':'), ensure_ascii=False)
open('scene.json', 'w').write(s); open('../scene.js', 'w').write('window.SCENE=' + s + ';')
print(len(s) // 1024, 'KB')
