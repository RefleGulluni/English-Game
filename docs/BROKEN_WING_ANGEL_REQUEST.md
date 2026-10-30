# 发给：Codex 角色设计组 — 碎翼天使（喷泉的一个变体）

日期：2026-10-30。需求方：Claude（程序），用户拍板（用户：“okok”）。
先读：`docs/PIXEL_ASSET_PIPELINE.md`（尤其“要拼接 / 要配套的零件以同家族已有零件为底子改出来”）、`docs/CEMETERY_ENTRY_PROPS_REQUEST.md` 里 `fountain_dry_01` 那一行（你们当时怎么做的）。

## 0. 背景

- 游戏现在能完整走通第一条“学词路线”：玩家在墓园里一路碰到 **SHATTER（打碎）** 这个词四次，最后学会它（`docs/FIRST_WORD_ROUTE_SHATTER.md`）。
- 第二次碰到它是在第 2 个房间：一座干涸的喷泉，中间立着哀悼天使。玩家走近按 E，读到：*The angel keeps one wing. … It was **shattered**.*，然后从三个意思里选对“打碎”。
- **问题**：房间里用的是你们做的入口喷泉 `art/cemetery_v3/props/fountain_dry_01.png`（已通过，入口素材的质量标准），天使的翅膀是**完整的**。文字说“碎了”，画面里却没碎，玩家对不上。
- 这一次要一个**翅膀被打碎的版本**，让玩家亲眼看到“shattered”是什么样子。

## 1. 要做的

| 文件 | 是什么 |
|---|---|
| `art/cemetery_v3/props/fountain_broken_wing_01.png` | 喷泉 + 碎翼天使，**画布 256×256，和 `fountain_dry_01` 同一个原点（底边中心）** |
| `art/cemetery_v3/props/fountain_broken_wing_01_base.png` | 底座贴花；如果池子没有改动，可以直接复制 `fountain_dry_01_base.png`，在 QA 里写明 |

**以 `fountain_dry_01.png` 为底子改，不重新生成整件。** 只改这几处：

1. **翅膀碎了**：看得见的那只翅膀（画面右侧）在**大约一半处断掉**。断口是**参差的、新鲜的碎茬**：断面颜色比风化的表面浅一点（里面的石头没被风吹黑），能看出是“一下子碎成很多块”，不是“慢慢风化掉”。剩下的半截翅膀保持原来的羽毛画法。
2. **碎片落在池子里**：天使脚下、池底的泥上散着 **5～9 块大小不一的石头碎片**（大的约 6～10 px，小的 1～3 px），有一两块大的还能看出羽毛的纹路。碎片要像**刚掉下来不久**：比池底的泥和落叶干净、浅一些，但不能比天使的脸和骨头亮。
3. **其余一律不动**：池子、池沿缺口、天使的身体和脸、底座、苔藓、颜色，**逐像素保持原样**。新画的部分颜色从原图里取（可以加两三个“新鲜断面”的浅石色）。

**不要的**：翅膀整只消失（要能看出“这里原来有翅膀”）；碎片飞在空中；裂纹发光；饱和青蓝（那是语言专用）；镜像、旋转。

## 2. 交付

| 文件 | 内容 |
|---|---|
| `fountain_broken_wing_01.png`、`_base.png` | 本体 + 底座 |
| `qc/fountain_broken_wing_01_compare_6x.png` | 左：原版 `fountain_dry_01`，右：碎翼版，6 倍并排 |
| `qc/fountain_broken_wing_01_vs_hero_2x.png` | 碎翼版 + 主角 `art/character_design/hero_B1_front_straight.png` 站在池前，2 倍 |
| `qc/fountain_broken_wing_01_QA.md` | 改了哪些像素（大概范围）、新加了几种颜色、`pixel_check.py` 数字；**没做到或拿不准的地方如实写出** |
| manifest | 照常登记一行 |

**不要修改 `fountain_dry_01.png` 和它的 `_base`**：入口房间还在用完整版。

完成后停下，等用户验收：Claude 会把第 2 个房间的喷泉换成碎翼版，截图给用户看。
