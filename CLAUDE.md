# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page Three.js 3D model of central Rome: a 2 × 2 km area around the Colosseum, built from OpenStreetMap data and SRTM terrain. It contains a procedural Colosseum, a procedural Vittoriano (Altare della Patria) and an animated bike ride: Piazza Venezia → Circo Massimo → around the Colosseum → Via dei Fori Imperiali → back, drawn on the ground as a neon line. During the ride a HUD shows gradient, speed, power and altitude. UI text is in German.

## Commands

Open the page with `open roma3d.html`. It needs no server: `scene.js` is a classic script and Three.js r0.165 loads from jsDelivr via an importmap.

Regenerate the scene data. Run the steps in this order, because each one rewrites `data/scene.json` and `scene.js`, and `process.py` drops the keys the later steps add:
```
cd data && python3 process.py && python3 route.py osm.json scene.json ../scene.js && python3 terrain.py
```
`terrain.py` needs numpy and Pillow, and reads the Terrarium elevation tiles in `data/tiles/` (zoom 15, listed in `tiles/list.txt`). `osm.json` is a raw Overpass `out geom` dump and is the only input to `process.py`.

To check visually without a GPU, take a headless Chrome screenshot. The URL hash picks a view (`#ge`, `#close`, `#top`, `#venezia`). `?t=<seconds>#ride` starts the ride and fast-forwards it by that many seconds:
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist --user-data-dir=<tmp> --window-size=1400,900 --virtual-time-budget=60000 --screenshot=<out.png> "file://$PWD/roma3d.html?t=60#ride"
```
Add `?info` to the URL to log `renderer.info.render` (draw calls, triangles) once on the third frame. Under headless virtual time the FPS counter reads 0 and frame `dt` can be 0, so never let displayed values depend on a non-empty integration loop.

## Data pipeline (`data/`)

- **`process.py`:** projects lat/lon to local metres. The origin is the Colosseum centroid (OSM relation 1834818). x = east, y = north, `KX = 111320·cos(41.8902°)`, `KY = 110574`; the JS uses the same constants. It emits compact `buildings`, `roads` and `areas` (flat `[x,y,…]` rings). It also emits `colosseum.angle`, the major-axis angle fitted from the footprint, and `origin`. Facade and roof colours come from OSM tags, or from a hash-seeded palette.
- **`route.py`:** Dijkstra over the OSM highway graph. Car roads cost ×1 and pedestrian/foot ways cost more, so the ride stays on asphalt. Waypoints go around the Colosseum. It strips U-turn spikes and stores `route`.
- **`terrain.py`:** turns the SRTM DSM into a DTM-like heightmap in these steps:
  1. A morphological opening removes buildings.
  2. A gaussian blur smooths the result.
  3. The terrain is clamped under the Vittoriano footprint.
  4. A level platform is made around the Colosseum.
  5. Laplacian-smoothed street heights are burned back in, because SRTM shows the excavated fora rather than the road surface.

  The result is stored as base64 Int16 decimetres in `terrain` (8 m grid, ±1200 m).

## `roma3d.html` architecture

Everything is one module script, split into sections marked `// ---------- … ----------`. Key cross-cutting conventions:

- **Coordinates:** data coords (east, north) map to Three as `(x, height, -north)` via `P3()`. Procedural groups use their own local frames and are placed with `position`/`rotation.y`:
  - Colosseum: u along the major axis, v along the minor axis.
  - Vittoriano (`VIT`, `vitLocal()`): X along the facade, D (local z) toward the back.
- **Heights:** `asl(x,y)` samples the heightmap. `gh(x,y)` returns the render height relative to the Colosseum (`BASE`), faded to `HEDGE` at the border. Everything placed on the ground must use `gh`: buildings (base `hc`/`hb`), densified road ribbons (`+0.3`), trees, labels, the bike and the camera.
- **Geometry:** `Geo` accumulates non-indexed triangles with vertex colours and UVs. Materials are `DoubleSide` and normals come from `computeVertexNormals`, so winding doesn't matter. `Tiled` buckets geometry into 250 m tiles so that the camera and shadow frustum culling work. City meshes must stay tiled, and trees are per-tile `InstancedMesh`es.
- **Textures:** all generated on canvases at startup (facades, shops, masonry, Colosseum arcade bay, marble). Land use (parks, archaeological areas) is painted onto the terrain texture `LAND`, not built as geometry.
- **Shadows:** `renderer.shadowMap.autoUpdate = false`. `setShadow('overview')` renders an 8K map over the whole area once. `setShadow('ride', center)` renders a 4K map over ±220 m that follows the rider, snapped to the texel grid. Anything that changes the scene must request `renderer.shadowMap.needsUpdate`.
- **Ride:** `route` is a CatmullRom curve built from `S.route` with rounded corners.
  - `placeBike` derives the heading from a ±2 m chord, smooths it, and sets lean (v²κ/g) and pitch (grade).
  - `rideStep` integrates speed from power: `PHYS`, `powerAt()`, 190 W target, coasting and braking near `vMax`.
  - The camera is rigidly offset from the rider. Only its yaw trails the heading, so the distance stays constant.
  - The elevation and grade profiles (`PROF`/`GRADE`, 2 m samples) feed the HUD (`#stats`, `#prof` canvas).
- **Rendering cost:** the city uses `MeshLambertMaterial` (`lam()`). `MeshStandardMaterial` (`mat()`) is kept only for marble, gold and bronze. There is no logarithmic depth buffer; instead the camera near/far and the fog switch between overview (3–9000 m) and ride (0.5–2600 m), and roads use `polygonOffset`. Static scene objects have `matrixAutoUpdate` off. Only the bike, the sun and the camera update their matrices.
- **Performance:** adaptive pixel ratio (between 1 and the device pixel ratio, targeting about 60 fps) and the FPS counter (`#fps`) live in the animation loop. The screenshot buttons render at 4K/8K with pixel ratio 1.
