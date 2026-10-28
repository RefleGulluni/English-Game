"""Builds the 15 corner tiles of each painted ground terrain (path, grass, paving) as one 128×128 atlas.

The art group paints the path *material* (a big seamless texture); this script draws only the
*shape*: where the path is, its wet rim, and a few stray pebbles. Every pixel inside the path is
pure white, and the path shader replaces white with the path texture sampled at world position,
so the inside of a path never repeats on a 32 px grid. Each terrain has its own edge style: the
path gets a broken wet-mud rim and stray pebbles, grass gets blade tips poking out into the mud,
paving gets sunken mud along the slab edge and 2×2 chips of broken slab.

Why the shapes always join: each tile's field is the bilinear blend of its four corners plus a
noise that repeats every 32 px, plus a per-tile noise that fades to zero at the tile's edges.
Along an edge only the two corners on that edge and the shared 32 px noise matter, so any two
tiles that agree on those corners meet without a step, wherever they come from in the atlas.

Layout: the de Bruijn 4×4 corner layout from docs/CEMETERY_GROUND_TRANSITION_REQUEST.md (the mmmm
cell stays empty; the full-path cell needs no variants, the texture does that). A JSON next to the PNG lists the
corners of every cell for the Godot TileSet builder.

    python3 scripts/tools/build_ground_path_masks.py

Full method: docs/GROUND_TERRAIN_METHOD.md.
"""
import json
import math
import random
from pathlib import Path

from PIL import Image

OUT_DIR = Path("art/cemetery_v3/ground/transitions/masks")
TILE = 32
LAYOUT = [[0, 0, 0, 1], [0, 0, 1, 0], [1, 0, 1, 1], [0, 1, 1, 1]]  # corner values on a 4×4 torus
INSIDE = (255, 255, 255, 255)  # replaced by the path texture in the shader
EDGE_NOISE = 0.20  # how far the 32 px periodic noise pushes the edge
TILE_NOISE = 0.22  # per-tile wobble, zero at the tile border
## Per terrain: output name, noise seed (so grass and paths don't share edge shapes), the rim drawn
## just inside the edge, and the bits scattered just outside it.
STYLES = {
    "path": {
        "file": "ground_path_masks_01", "seed": 0,
        "rim": [(50, 52, 45, 255), (56, 58, 50, 255)], "rim_band": 0.07, "rim_chance": 0.7,  # trodden-in wet mud
        "outside": [(108, 106, 96, 255), (92, 90, 80, 255), (122, 119, 108, 255)],  # stray pebbles
        "outside_band": 0.16, "outside_chance": 0.10, "blade": False,
    },
    "grass": {
        "file": "ground_grass_masks_01", "seed": 40,
        "rim": [], "rim_band": 0.0, "rim_chance": 0.0,
        "outside": [(106, 102, 76, 255), (80, 84, 60, 255), (60, 66, 48, 255)],  # blade tips, colours from grass_texture_01
        "outside_band": 0.13, "outside_chance": 0.22, "blade": True,
    },
    "paving": {
        "file": "ground_paving_masks_01", "seed": 80,
        "rim": [(63, 62, 57, 255), (74, 72, 64, 255)], "rim_band": 0.06, "rim_chance": 0.55,  # mud where the slab edge sank
        "outside": [(97, 96, 94, 255), (83, 82, 80, 255), (110, 109, 107, 255)],  # broken-off slab chips, from paving_texture_01
        "outside_band": 0.18, "outside_chance": 0.07, "blade": False, "chunk": True,
    },
}


def value_noise(size: int, cell: int, seed: int) -> list[list[float]]:
    """Smooth noise in [-1, 1] that wraps around a size×size square."""
    rng = random.Random(seed)
    n = size // cell
    grid = [[rng.uniform(-1, 1) for _ in range(n)] for _ in range(n)]

    def smooth(t: float) -> float:
        return t * t * (3 - 2 * t)

    out = []
    for y in range(size):
        row = []
        for x in range(size):
            gx, gy = (x + 0.5) / cell, (y + 0.5) / cell
            x0, y0 = int(math.floor(gx)) % n, int(math.floor(gy)) % n
            x1, y1 = (x0 + 1) % n, (y0 + 1) % n
            tx, ty = smooth(gx - math.floor(gx)), smooth(gy - math.floor(gy))
            top = grid[y0][x0] * (1 - tx) + grid[y0][x1] * tx
            bottom = grid[y1][x0] * (1 - tx) + grid[y1][x1] * tx
            row.append(top * (1 - ty) + bottom * ty)
        out.append(row)
    return out


def periodic_noise(seed: int) -> list[list[float]]:
    coarse = value_noise(TILE, 8, 3 + seed)
    fine = value_noise(TILE, 2, 4 + seed)
    return [[coarse[y][x] * 0.75 + fine[y][x] * 0.25 for x in range(TILE)] for y in range(TILE)]


def draw_tile(corners: tuple[int, int, int, int], seed: int, shared: list[list[float]], style: dict) -> Image.Image:
    tl, tr, bl, br = corners
    own = value_noise(TILE, 8, 100 + seed)
    rng = random.Random(500 + seed)
    img = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    px = img.load()
    for y in range(TILE):
        for x in range(TILE):
            fx, fy = (x + 0.5) / TILE, (y + 0.5) / TILE
            base = tl * (1 - fx) * (1 - fy) + tr * fx * (1 - fy) + bl * (1 - fx) * fy + br * fx * fy
            fade = math.sin(math.pi * fx) * math.sin(math.pi * fy)
            f = base + EDGE_NOISE * shared[y][x] + TILE_NOISE * fade * own[y][x]
            if corners == (1, 1, 1, 1):
                px[x, y] = INSIDE
            elif f >= 0.5 + style["rim_band"]:
                px[x, y] = INSIDE
            elif f >= 0.5:
                # a broken rim, not an outline: only some of the edge pixels get the rim colour
                rim = style["rim"]
                px[x, y] = rim[(x * 7 + y * 3 + seed) % len(rim)] if rim and rng.random() < style["rim_chance"] else INSIDE
            elif f >= 0.5 - style["outside_band"] and rng.random() < style["outside_chance"]:
                px[x, y] = rng.choice(style["outside"])
                if style["blade"] and y > 0 and px[x, y - 1][3] == 0:
                    px[x, y - 1] = px[x, y]  # grass tips are short upright strokes, not dots
                if style.get("chunk") and x + 1 < TILE and y + 1 < TILE:
                    for dx, dy in ((1, 0), (0, 1), (1, 1)):  # stone chips are 2×2 lumps, not single dots
                        if px[x + dx, y + dy][3] == 0:
                            px[x + dx, y + dy] = px[x, y]
    return img


def build(style: dict) -> None:
    shared = periodic_noise(style["seed"])
    atlas = Image.new("RGBA", (TILE * 4, TILE * 4), (0, 0, 0, 0))
    cells = []
    for r in range(4):
        for c in range(4):
            corners = (LAYOUT[r][c], LAYOUT[r][(c + 1) % 4], LAYOUT[(r + 1) % 4][c], LAYOUT[(r + 1) % 4][(c + 1) % 4])
            if corners == (0, 0, 0, 0):
                continue
            atlas.paste(draw_tile(corners, style["seed"] + r * 4 + c, shared, style), (c * TILE, r * TILE))
            cells.append({"x": c, "y": r, "tl": corners[0], "tr": corners[1], "bl": corners[2], "br": corners[3]})
    atlas.save(OUT_DIR / (style["file"] + ".png"))
    (OUT_DIR / (style["file"] + ".json")).write_text(json.dumps({"tile": TILE, "cells": cells}, indent=1))
    print(f"wrote {len(cells)} tiles to {OUT_DIR / style['file']}.png")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for style in STYLES.values():
        build(style)


if __name__ == "__main__":
    main()
