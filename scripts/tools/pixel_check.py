#!/usr/bin/env python3
"""像素素材检查：和主角 B1 比精致程度，并核对真像素规格。

用法（在仓库根目录）：
    python3 scripts/tools/pixel_check.py art/cemetery_v3/props/*.png
    python3 scripts/tools/pixel_check.py --hero 某个新角色.png ...   # 换一个对照标准

每个文件输出：尺寸、透明度是否只有 0/255、不透明颜色数、相邻像素换色比例、
饱和青蓝像素数、最低不透明行（看原点 / 着地）。最后一行是对照标准（默认主角 B1）。
判读见 docs/PIXEL_ASSET_PIPELINE.md §4。需要 Pillow（pip install pillow）。
"""
import argparse
import colorsys
import sys

from PIL import Image

HERO = "art/character_design/hero_B1_front_straight.png"


def measure(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    alphas = set()
    colors = set()
    pairs = changes = cyan = 0
    lowest = -1
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            alphas.add(a)
            if a == 0:
                continue
            lowest = max(lowest, y)
            colors.add((r, g, b))
            hue, sat, val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # 饱和青蓝是语言层专用色，世界素材里不应出现
            if 160 <= hue * 360 <= 260 and sat >= 0.35 and val > 0.3:
                cyan += 1
            # 只算水平相邻、两边都完全不透明的像素对
            if x + 1 < w and px[x + 1, y][3] == 255 and a == 255:
                pairs += 1
                changes += px[x + 1, y][:3] != (r, g, b)
    return {
        "size": f"{w}x{h}",
        "alpha_ok": alphas <= {0, 255},
        "colors": len(colors),
        "change": round(changes / pairs * 100) if pairs else 0,
        "cyan": cyan,
        "lowest": lowest,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+")
    parser.add_argument("--hero", default=HERO, help="对照标准，默认主角 B1")
    args = parser.parse_args()
    print(f"{'文件':<56} {'尺寸':>9} {'透明':>4} {'颜色':>4} {'换色%':>5} {'青蓝':>4} {'最低行':>5}")
    rows = [(f, measure(f)) for f in args.files] + [("对照：" + args.hero, measure(args.hero))]
    bad = False
    for f, m in rows:
        # 对照行不标记：主角书上的青蓝印记是 Lexicon 符号，本来就该有
        flag = "" if f.startswith("对照") or (m["alpha_ok"] and m["cyan"] == 0) else "  ← 检查"
        bad = bad or flag != ""
        print(f"{f[-56:]:<56} {m['size']:>9} {'OK' if m['alpha_ok'] else '半透明':>4} {m['colors']:>4} {m['change']:>5} {m['cyan']:>4} {m['lowest']:>5}{flag}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
