# 方案：X = 1 - minmax(单位利润 π=P*r)，Y = minmax(月销量 U)
# 用法：
#   uv run python scripts/make_bcg.py --in data/bcg_raw.csv --out out

import argparse
import math
import os
import pandas as pd
import matplotlib.pyplot as plt

# ---- 中文字体（Windows 优先用雅黑；若无则尝试黑体）----
import matplotlib
matplotlib.rcParams["font.family"] = ["Microsoft YaHei", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

def minmax(s):
    smin, smax = float(s.min()), float(s.max())
    if math.isclose(smax, smin):
        return (s * 0 + 0.5)  # 避免除0：全相等时给 0.5
    return (s - smin) / (smax - smin)


def main(in_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    df = pd.read_csv(in_path)

    # 字段名假设：商品ID, 商品名, 月销量, 平均价格, 毛利率
    df["单位利润"] = df["平均价格"] * df["毛利率"]           # π = P * r
    df["销售额(元)"] = df["月销量"] * df["平均价格"]          # 气泡大小
    baseX = minmax(df["单位利润"])
    df["X"] = 1 - baseX                                      # 左高右低
    df["Y"] = minmax(df["月销量"])                           # 上高下低

    # 分割线（中位数）
    x_mid = df["X"].median()
    y_mid = df["Y"].median()

    # 象限分类（含义可按业务调整）
    def classify(x, y):
        if x <= x_mid and y >= y_mid:
            return "明星（高利润×高销量）"
        if x > x_mid and y >= y_mid:
            return "金牛（薄利多销）"
        if x <= x_mid and y < y_mid:
            return "潜力/利基（高利润×低销量）"
        return "瘦狗（低利润×低销量）"

    df["象限"] = [classify(x, y) for x, y in zip(df["X"], df["Y"])]
    df["象限"] = df["象限"].astype(str)   
    # 保留三位小数（数值列）
    for col in ["单位利润", "销售额(元)", "X", "Y"]:
        df[col] = df[col].round(3)

    # 保存含坐标与象限的数据
    out_csv = os.path.join(out_dir, "bcg_with_indices.csv")
    cols = ["商品ID", "商品名", "月销量", "平均价格", "毛利率", "单位利润", "销售额(元)", "X", "Y", "象限"]
    df[cols].to_csv(out_csv, index=False, encoding="utf-8-sig")

    # ---- 绘图 ----
    fig, ax = plt.subplots(figsize=(8, 6), dpi=160)

    # 尺寸按销售额缩放，并做下限裁剪
    sizes = (df["销售额(元)"] / df["销售额(元)"].max() * 800).clip(lower=50)

    # 留边，避免裁切
    x_lo, x_hi = df["X"].min() - 0.05, df["X"].max() + 0.05
    y_lo, y_hi = df["Y"].min() - 0.05, df["Y"].max() + 0.05
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)

    # 背景象限着色（淡色）
    quad_bg = {
        "明星（高利润×高销量）"     : ("#2ca02c", (x_lo, y_mid, x_mid - x_lo, y_hi - y_mid)),  # 左上
        "金牛（薄利多销）"         : ("#1f77b4", (x_mid, y_mid, x_hi - x_mid, y_hi - y_mid)),  # 右上
        "潜力/利基（高利润×低销量）": ("#ff7f0e", (x_lo, y_lo, x_mid - x_lo, y_mid - y_lo)),    # 左下
        "瘦狗（低利润×低销量）"     : ("#d62728", (x_mid, y_lo, x_hi - x_mid, y_mid - y_lo)),    # 右下
    }
    for label, (color, rect) in quad_bg.items():
        ax.add_patch(Rectangle((rect[0], rect[1]), rect[2], rect[3],
                               facecolor=color, alpha=0.06, zorder=0, linewidth=0))

    # 画分割线
    ax.axvline(x_mid, linestyle="--", linewidth=1, color="#7f7f7f", zorder=1)
    ax.axhline(y_mid, linestyle="--", linewidth=1, color="#7f7f7f", zorder=1)

    # 每个象限的散点颜色与图例
    palette = {
        "明星（高利润×高销量）"     : "#2ca02c",
        "金牛（薄利多销）"         : "#1f77b4",
        "潜力/利基（高利润×低销量）": "#ff7f0e",
        "瘦狗（低利润×低销量）"     : "#d62728",
    }

    # 分组绘制，自动生成图例
    for label, g in df.groupby("象限"):
        ax.scatter(g["X"], g["Y"],
                   s=(g["销售额(元)"] / df["销售额(元)"].max() * 800).clip(lower=50),
                   alpha=0.75, c=palette[str(label)],
                   edgecolors="white", linewidths=0.5, label=label, zorder=2)

    # 数据点文字标注
    for _, row in df.iterrows():
        ax.text(row["X"] + 0.01, row["Y"] + 0.01, str(row["商品名"]),
                fontsize=8, color="#333333", zorder=3)

    # 象限中心文字（进一步解释）
    ax.text((x_lo + x_mid) / 2, (y_mid + y_hi) / 2, "明星\n(高利×高销)",
            ha="center", va="center", fontsize=10, color="#2ca02c", alpha=0.85, zorder=1)
    ax.text((x_mid + x_hi) / 2, (y_mid + y_hi) / 2, "金牛\n(薄利多销)",
            ha="center", va="center", fontsize=10, color="#1f77b4", alpha=0.85, zorder=1)
    ax.text((x_lo + x_mid) / 2, (y_lo + y_mid) / 2, "潜力/利基\n(高利×低销)",
            ha="center", va="center", fontsize=10, color="#ff7f0e", alpha=0.85, zorder=1)
    ax.text((x_mid + x_hi) / 2, (y_lo + y_mid) / 2, "瘦狗\n(低利×低销)",
            ha="center", va="center", fontsize=10, color="#d62728", alpha=0.85, zorder=1)

    # 轴与标题
    ax.set_xlabel("价格&利润（左高右低，X = 1 - minmax(单位利润)）")
    ax.set_ylabel("需求&销量（Y = minmax(月销量)）")
    ax.set_title("四象限气泡图")


    

    # 图例说明(会覆盖自动生成的图例)
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='明星（高利×高销）',
            markerfacecolor='#2ca02c', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='金牛（薄利多销）',
            markerfacecolor='#1f77b4', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='潜力/利基（高利×低销）',
            markerfacecolor='#ff7f0e', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='瘦狗（低利×低销）',
            markerfacecolor='#d62728', markersize=10),
    ]

    ax.legend(handles=legend_elements, title="象限含义",
          loc="upper left", bbox_to_anchor=(1.02, 1),
          frameon=False, markerscale=1.4, borderaxespad=0.)

    out_png = os.path.join(out_dir, "bcg_plot.png")
    plt.tight_layout()
    plt.savefig(out_png, bbox_inches="tight")
    print(f"已生成：\n- {out_csv}\n- {out_png}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True, help="输入原始CSV路径（含：月销量/平均价格/毛利率）")
    ap.add_argument("--out", dest="out_dir", default="out", help="输出目录")
    args = ap.parse_args()
    main(args.in_path, args.out_dir)
