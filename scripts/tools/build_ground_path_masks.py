"""Builds the 15 corner tiles for the cemetery path terrain as one 128×128 atlas.

The art group paints the path *material* (a big seamless texture); this script draws only the
*shape*: where the path is, its wet rim, and a few stray pebbles. Every pixel inside the path is
pure white, and the path shader replaces white with the path texture sampled at world position,
so the inside of a path never repeats on a 32 px grid.

Why the shapes always join: each tile's field is the bilinear blend of its four corners plus a
noise that repeats every 32 px, plus a per-tile noise that fades to zero at the tile's edges.
Along an edge only the two corners on that edge and the shared 32 px noise matter, so any two
tiles that agree on those corners meet without a step, wherever they come from in the atlas.

Layout: the de Bruijn 4×4 corner layout from docs/CEMETERY_GROUND_TRANSITION_REQUEST.md (the mmmm
cell stays empty; the full-path cell needs no variants, the texture does that). A JSON next to the PNG lists the
corners of every cell for the Godot TileSet builder.

    python3 scripts/tools/build_ground_path_masks.py
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
RIM = [(50, 52, 45, 255), (56, 58, 50, 255)]  # trodden-in wet mud along the edge
PEBBLES = [(108, 106, 96, 255), (92, 90, 80, 255), (122, 119, 108, 255)]
EDGE_NOISE = 0.20  # how far the 32 px periodic noise pushes the edge
TILE_NOISE = 0.22  # per-tile wobble, zero at the tile border
RIM_BAND = 0.07  # field values just above the threshold become rim
PEBBLE_BAND = 0.16  # field values just below the threshold may get a pebble


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


def periodic_noise() -> list[list[float]]:
    coarse = value_noise(TILE, 8, 3)
    fine = value_noise(TILE, 2, 4)
    return [[coarse[y][x] * 0.75 + fine[y][x] * 0.25 for x in range(TILE)] for y in range(TILE)]


def draw_tile(corners: tuple[int, int, int, int], seed: int, shared: list[list[float]]) -> Image.Image:
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
            elif f >= 0.5 + RIM_BAND:
                px[x, y] = INSIDE
            elif f >= 0.5:
                # a broken rim, not an outline: about two thirds of the edge pixels are wet mud
                px[x, y] = RIM[(x * 7 + y * 3 + seed) % 2] if rng.random() < 0.7 else INSIDE
            elif f >= 0.5 - PEBBLE_BAND and rng.random() < 0.10:
                px[x, y] = rng.choice(PEBBLES)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shared = periodic_noise()
    atlas = Image.new("RGBA", (TILE * 4, TILE * 4), (0, 0, 0, 0))
    cells = []
    for r in range(4):
        for c in range(4):
            corners = (LAYOUT[r][c], LAYOUT[r][(c + 1) % 4], LAYOUT[(r + 1) % 4][c], LAYOUT[(r + 1) % 4][(c + 1) % 4])
            if corners == (0, 0, 0, 0):
                continue
            atlas.paste(draw_tile(corners, r * 4 + c, shared), (c * TILE, r * TILE))
            cells.append({"x": c, "y": r, "tl": corners[0], "tr": corners[1], "bl": corners[2], "br": corners[3]})
    atlas.save(OUT_DIR / "ground_path_masks_01.png")
    (OUT_DIR / "ground_path_masks_01.json").write_text(json.dumps({"tile": TILE, "cells": cells}, indent=1))
    print(f"wrote {len(cells)} tiles to {OUT_DIR}")


if __name__ == "__main__":
    main()
