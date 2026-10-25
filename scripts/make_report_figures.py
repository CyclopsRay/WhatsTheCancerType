"""Progress-report figures: five composites, figures/report_fig{1..5}.png.

Usage: make_report_figures.py DERIVED FIGDIR
Fig 1 pipeline schematic (synthetic shapes only); Fig 2 data at a glance (fig10, fig17, fig8);
Fig 3 genes (fig3, fig4); Fig 4 anomaly v2 depth-adjusted scores (new) + fig14; Fig 5 flow per
person (new) + Visium sections where the own reference beats the other (new). Fig 5 parts are also
written as report_panel_{flow,visium}.png.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, Ellipse, Polygon, Rectangle

INK, MUTED, GRID = "#1d1a29", "#6e6980", "#d9d6e0"
CONV, SERR, HEALTHY, FAINT = "#2a78d6", "#eb6834", "#9a95a8", "#e4e1ea"
ROUTE_COLOR = {"conventional": CONV, "serrated": SERR}
PURITY = LinearSegmentedColormap.from_list("purity", ["#e6e2ec", "#a8365c", "#4a1428"])
SECTIONS = ["8270_1_HTA11_07862", "8270_2_HTA11_10711", "8270_3_HTA11_07663"]


def style():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED,
                         "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                         "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                         "savefig.facecolor": "white", "figure.facecolor": "white"})


def tag(ax, letter):
    ax.text(-0.02, 1.02, letter, transform=ax.transAxes, fontsize=13, fontweight="bold", va="bottom",
            ha="right")


def image(ax, path, crop_top=0):
    ax.imshow(plt.imread(path)[crop_top:])
    ax.set_axis_off()


GENE = LinearSegmentedColormap.from_list("gene", ["#f4f2f7", "#9a95a8", "#1d1a29"])
STROMA, NORMAL_EPI = "#f3eef1", "#b4b0bf"


def arrow(ax, xy, xytext, color=MUTED, lw=1.4, style="-|>", rad=0.0):
    ax.annotate("", xy=xy, xytext=xytext, arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                mutation_scale=12, shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}"))


def gene_strip(ax, x0, y, values, marked, edge, w=0.36, h=0.62):
    for i, v in enumerate(values):
        ax.add_patch(Rectangle((x0 + i * w, y - h / 2), w * 0.92, h, fc=GENE(v), ec="none"))
        if i in marked:
            ax.add_patch(Rectangle((x0 + i * w, y - h / 2), w * 0.92, h, fc="none", ec=edge, lw=1.6))


def vae_panel(ax):
    """Healthy-only VAE: healthy cells come back as they went in, polyp cells come back healthy."""
    rng = np.random.default_rng(1)
    n_genes, x_in, x_out = 12, 0.9, 13.6
    base = rng.uniform(0.12, 0.75, n_genes)
    rows = [(6.5, HEALTHY, []), (5.5, HEALTHY, []), (3.1, CONV, [1, 4, 5, 9]), (2.1, SERR, [2, 7, 8, 10])]
    for y, color, changed in rows:
        cell = np.clip(base + rng.normal(0, 0.04, n_genes), 0, 1)
        for g in changed:
            cell[g] = 0.98 if base[g] < 0.45 else 0.03
        rebuilt = np.clip(base + rng.normal(0, 0.04, n_genes), 0, 1)
        if not changed:
            rebuilt = np.clip(cell + rng.normal(0, 0.03, n_genes), 0, 1)
        gene_strip(ax, x_in, y, cell, changed, color)
        gene_strip(ax, x_out, y, rebuilt, changed, color)
        ax.add_patch(Circle((x_in - 0.45, y), 0.2, fc=color, ec="none"))
        err = np.abs(cell - rebuilt).sum()
        ax.add_patch(Rectangle((18.3, y - 0.22), 0.45 * err, 0.44, fc=color, ec="none"))
        arrow(ax, (5.95, y * 0.55 + 4.3 * 0.45), (x_in + n_genes * 0.36 + 0.15, y), lw=0.9)
        arrow(ax, (x_out - 0.15, y), (12.65, y * 0.55 + 4.3 * 0.45), lw=0.9)
    ax.add_patch(Polygon([(6.0, 1.3), (6.0, 7.3), (8.6, 5.3), (8.6, 3.3)], fc=FAINT, ec=MUTED, lw=1))
    ax.add_patch(Polygon([(10.0, 3.3), (10.0, 5.3), (12.6, 7.3), (12.6, 1.3)], fc=FAINT, ec=MUTED, lw=1))
    for zy in np.linspace(3.6, 5.0, 4):
        ax.add_patch(Circle((9.3, zy), 0.2, fc="white", ec=INK, lw=1))
    ax.text(7.3, 4.3, "encoder", ha="center", va="center", fontsize=7, color=INK)
    ax.text(11.3, 4.3, "decoder", ha="center", va="center", fontsize=7, color=INK)
    ax.text(x_in + 2.15, 7.45, "cells in", ha="center", fontsize=8)
    ax.text(x_out + 2.15, 7.45, "cells rebuilt", ha="center", fontsize=8)
    ax.text(18.5, 7.45, "error", ha="left", fontsize=8)
    ax.text(x_in - 0.75, 6.0, "healthy", rotation=90, ha="right", va="center", fontsize=8, color=INK)
    ax.text(x_in - 0.75, 2.6, "polyp", rotation=90, ha="right", va="center", fontsize=8, color=INK)
    ax.set_xlim(-0.6, 21.6)
    ax.set_ylim(0.2, 8.1)


def band(t, end):
    """Centre line of one manifold branch, t in [0, 1]: shared trunk, then a curve to `end`."""
    x = -0.5 + t * (end[0] + 0.5)
    y = end[1] * np.clip((t - 0.35) / 0.65, 0, 1) ** 1.6
    return x, y


def ot_panel(ax):
    """Unbalanced OT pairs healthy with polyp cells; a flow learns the path along the manifold."""
    rng = np.random.default_rng(7)
    ends = {CONV: (11.0, 2.3), SERR: (11.0, -2.3)}
    t = np.linspace(0, 1, 200)
    for lw, color in [(30, GRID), (27, "#f4f2f7")]:
        for end in ends.values():
            x, y = band(t, end)
            ax.plot(x, y, color=color, lw=lw, solid_capstyle="round", zorder=0)
    hx, hy = rng.normal(0.4, 0.55, 26), rng.normal(0, 0.32, 26)
    mass = rng.gamma(1.6, 0.6, 26)
    for color, end in ends.items():
        px = rng.normal(end[0] - 0.4, 0.45, 14)
        py = rng.normal(end[1], 0.3, 14)
        ax.scatter(px, py, s=26, c=color, lw=0, zorder=3)
        for i in rng.choice(26, 4, replace=False):
            j = rng.integers(14)
            ax.plot([hx[i], px[j]], [hy[i], py[j]], color=color, lw=0.7, ls=(0, (3, 2)), alpha=0.45, zorder=1)
        x, y = band(np.linspace(0.12, 0.88, 50), end)
        ax.plot(x, y, color=color, lw=2.4, zorder=2)
        arrow(ax, (x[-1], y[-1]), (x[-4], y[-4]), color=color, lw=2.4)
    ax.scatter(hx, hy, s=14 + 46 * mass, c=HEALTHY, lw=0.6, ec="white", zorder=3)
    ax.scatter([hx[3]], [hy[3]], s=60, fc="white", ec=HEALTHY, lw=1.2, zorder=4)
    ax.text(0.4, -1.25, "healthy lining", ha="center", fontsize=8, color=INK)
    ax.text(11.6, 2.3, "conventional\npolyp", va="center", fontsize=8)
    ax.text(11.6, -2.3, "serrated\npolyp", va="center", fontsize=8)
    ax.set_xlim(-2.0, 14.2)
    ax.set_ylim(-3.3, 3.3)


def surface(x):
    return 8.0 + 1.3 * np.exp(-((x - 8.0) / 1.9) ** 2)


def spatial_panel(ax):
    """Tissue with normal and polyp crypts under the spot grid; one spot split into cell types."""
    rng = np.random.default_rng(5)
    xs = np.linspace(0.2, 12.8, 300)
    tissue = ax.fill_between(xs, 0.9, surface(xs), color=STROMA, lw=0, zorder=0)
    clip = tissue.get_paths()[0]
    ax.plot(xs, surface(xs), color=MUTED, lw=1, zorder=1)
    normal = list(np.arange(0.8, 5.4, 0.7)) + list(np.arange(11.0, 12.6, 0.7))
    for cx in normal:
        ax.plot([cx, cx], [surface(cx) - 0.05, 3.2], color=NORMAL_EPI, lw=7, solid_capstyle="round", zorder=1)
        ax.plot([cx, cx], [surface(cx) - 0.15, 3.35], color="white", lw=1.6, zorder=1)
    for k, cx in enumerate(np.arange(5.95, 10.3, 0.72)):
        yy = np.linspace(surface(cx) - 0.25, 2.3, 40)
        xx = cx + 0.07 * np.sin(yy * 1.6 + k)
        for color, lw in [(CONV, 6), ("white", 1.4)]:
            line, = ax.plot(xx, yy, color=color, lw=lw, solid_capstyle="round", zorder=1)
            line.set_clip_path(clip, ax.transData)
        if k % 3 == 1:
            bx_, by_ = xx[24], yy[24]
            for color, lw in [(CONV, 5), ("white", 1.2)]:
                line, = ax.plot([bx_, bx_ + 0.3], [by_, by_ - 1.0], color=color, lw=lw,
                                solid_capstyle="round", zorder=1)
                line.set_clip_path(clip, ax.transData)
    for row, gy in enumerate(np.arange(1.4, 9.6, 0.87)):
        for gx in np.arange(0.6 + 0.5 * (row % 2), 12.6, 1.0):
            if gy < surface(gx) - 0.25:
                ax.add_patch(Circle((gx, gy), 0.4, fc="none", ec=INK, lw=0.5, alpha=0.4, zorder=2))
    ox = np.linspace(5.5, 10.5, 60)
    bottom = 2.3 - 0.6 * np.sin(np.linspace(0, np.pi, 60))
    outline = np.r_[np.c_[ox, surface(ox) + 0.15], np.c_[ox[::-1], bottom]]
    ax.add_patch(Polygon(outline, closed=True, fill=False, ls="--", lw=1.2, ec=INK, zorder=2))
    row = round((6.6 - 1.4) / 0.87)
    offset = 0.6 + 0.5 * (row % 2)
    spot = (offset + round(8.0 - offset), 1.4 + 0.87 * row)
    ax.add_patch(Circle(spot, 0.42, fc="none", ec=INK, lw=1.8, zorder=3))

    zc, zr = (17.0, 5.6), 2.6
    ax.plot([spot[0] + 0.3, zc[0] - 1.7], [spot[1] + 0.3, zc[1] + 2.0], color=MUTED, lw=0.8)
    ax.plot([spot[0] + 0.3, zc[0] - 1.7], [spot[1] - 0.3, zc[1] - 2.0], color=MUTED, lw=0.8)
    ax.add_patch(Circle(zc, zr, fc="white", ec=INK, lw=1.6, zorder=3))
    cells = [CONV] * 5 + ["#6e6980"] * 2 + [NORMAL_EPI] * 2 + ["#d8c7d0"] * 3
    angles = np.linspace(0, 2 * np.pi, len(cells), endpoint=False) + 0.3
    radii = np.where(np.arange(len(cells)) % 2 == 0, 1.55, 0.75)
    for c, a, r in zip(cells, angles, radii):
        p = (zc[0] + r * np.cos(a), zc[1] + r * np.sin(a))
        ax.add_patch(Circle(p, 0.48, fc=c, ec="white", lw=1, alpha=0.9, zorder=4))
        ax.add_patch(Circle(p, 0.16, fc=INK, ec="none", alpha=0.55, zorder=5))

    bx = 21.9
    mid = (zc[0] + zr + bx) / 2
    rx, ry = rng.normal(mid, 0.5, 70), rng.normal(1.9, 0.38, 70)
    ax.scatter(rx, ry, s=9, c=rng.choice([CONV, "#6e6980", NORMAL_EPI, "#d8c7d0"], 70), lw=0, zorder=3)
    arrow(ax, (mid, 5.35), (mid, 2.8), lw=1.2)
    arrow(ax, (bx - 0.35, 5.6), (zc[0] + zr + 0.2, 5.6), lw=1.4)
    ax.text(mid, 5.9, "DestVI", ha="center", fontsize=9.5, color=INK)

    shares = [(CONV, 0.42, "ASC"), ("#6e6980", 0.17, "stem"), (NORMAL_EPI, 0.16, "mature"),
              ("#d8c7d0", 0.25, "other")]
    y0 = 3.0
    for c, v, name in shares:
        ax.add_patch(Rectangle((bx, y0), 0.9, 5.2 * v, fc=c, ec="white", lw=1.5))
        ax.text(bx + 1.1, y0 + 2.6 * v, f"{name} {v:.0%}", va="center", fontsize=8.5)
        y0 += 5.2 * v

    arrow(ax, (27.3, 5.6), (25.9, 5.6), lw=1.4)
    gx, gy = np.meshgrid(np.arange(-9, 10), np.arange(-7, 8))
    gx = gx + 0.5 * (gy % 2)
    keep = (gx / 9.2) ** 2 + (gy / 7.2) ** 2 < 1
    gx, gy = gx[keep], gy[keep]
    purity = np.clip(1 - np.hypot((gx - 2.5) / 5.5, gy / 5.2), 0, 1) * 0.85 + rng.uniform(0, 0.12, gx.size)
    ax.scatter(30.3 + gx * 0.29, 5.6 + gy * 0.29 * 0.87, s=11, c=purity, cmap=PURITY, vmin=0, vmax=1, lw=0)
    ax.add_patch(Ellipse((31.03, 5.6), 3.3, 3.2, fill=False, ls="--", lw=1.1, ec=INK))
    ax.set_xlim(-0.2, 33.2)
    ax.set_ylim(0, 10.2)


def fig1(D, F):
    """Pipeline: detect and predict side by side, map below."""
    fig = plt.figure(figsize=(10, 5.6))
    gs = fig.add_gridspec(2, 2, height_ratios=[2.0, 3.0], width_ratios=[22.2 / 7.9, 16.2 / 6.6],
                          hspace=0.08, wspace=0.06)
    with plt.rc_context({"font.size": 8}):
        for spec, (draw, letter, title) in zip([gs[0, 0], gs[0, 1], gs[1, :]], [
                (vae_panel, "a", "Detect"), (ot_panel, "b", "Predict"), (spatial_panel, "c", "Map")]):
            ax = fig.add_subplot(spec)
            draw(ax)
            ax.set_aspect("equal")
            ax.set_anchor("W")
            ax.set_axis_off()
            ax.set_title(title, fontsize=11, loc="left")
            tag(ax, letter)
    return fig


def fig2(D, F):
    """Data at a glance: label-free map, two people's polyps next to their lining, new-cell shares."""
    fig = plt.figure(figsize=(10, 6.1))
    gs = fig.add_gridspec(2, 2, height_ratios=[3.6, 2.4], width_ratios=[2800 / 1440, 2600 / 1040],
                          hspace=0.06, wspace=0.04)
    ax = fig.add_subplot(gs[0, :])
    image(ax, F / "fig10_label_free_DIS.png", crop_top=80)
    tag(ax, "a")
    for i, (name, letter) in enumerate([("fig17_person_highlight.png", "b"), ("fig8_new_cells.png", "c")]):
        ax = fig.add_subplot(gs[1, i])
        image(ax, F / name)
        tag(ax, letter)
    return fig


def fig3(D, F):
    fig = plt.figure(figsize=(10, 3.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1445 / 935, 1659 / 780], wspace=0.04)
    for i, (name, letter) in enumerate([("fig3_route_compare_DIS_all.png", "a"),
                                        ("fig4_replication.png", "b")]):
        ax = fig.add_subplot(gs[0, i])
        image(ax, F / name)
        tag(ax, letter)
    return fig


def strip(ax, values, x, color, rng):
    v = np.asarray(values)
    v = v[~np.isnan(v)]
    ax.scatter(x + rng.uniform(-0.12, 0.12, v.size), v, s=22, c=color, lw=0.6, ec="white", zorder=3)
    ax.plot([x - 0.22, x + 0.22], [np.median(v)] * 2, color=INK, lw=2, zorder=4)
    ax.text(x + 0.26, np.median(v), f"{np.median(v):.2f}", va="center", fontsize=9)


def fig4(D, F):
    a = pd.read_csv(D / "anomaly/recon_depth_adjusted.tsv", sep="\t")
    a = a[a.kind == "detected"]
    rng = np.random.default_rng(0)
    fig = plt.figure(figsize=(10, 4.3))
    gs = fig.add_gridspec(1, 3, width_ratios=[0.7, 0.7, 1.4], wspace=0.3)
    for i, (route, cell) in enumerate([("conventional", "ASC"), ("serrated", "SSC")]):
        ax = fig.add_subplot(gs[0, i])
        r = a[a.route == route]
        strip(ax, r.auroc_new_recon_adj, 0, ROUTE_COLOR[route], rng)
        strip(ax, r.auroc_new_latent, 1, ROUTE_COLOR[route], rng)
        ax.axhline(0.5, color=MUTED, ls="--", lw=1)
        ax.set_xticks([0, 1], ["rebuild\nerror", "hidden-layer\ndistance"], fontsize=9)
        ax.set_xlim(-0.5, 1.6)
        ax.set_ylim(0, 1.02)
        ax.set_title(f"{route.capitalize()} polyps\n{cell} vs other polyp cells", fontsize=10, loc="left")
        if i == 0:
            ax.set_ylabel("AUROC (one dot per person)")
            tag(ax, "a")
    ax = fig.add_subplot(gs[0, 2])
    image(ax, F / "fig14_stem_mature.png")
    tag(ax, "b")
    return fig


def flow_panel(D, F):
    f = pd.read_csv(D / "flow/flow_people.tsv", sep="\t")
    cols = [("ed_identity", "healthy,\nunchanged"), ("ed_flow + growth", "predicted,\nright route"),
            ("ed_flow_wrong_route", "predicted,\nwrong route")]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.0), sharey=True)
    for ax, route in zip(axes, ["conventional", "serrated"]):
        r = f[f.route == route]
        for _, p in r.iterrows():
            y = [p[c] for c, _ in cols]
            mark = p.donor == "HTA11_6801"
            ax.plot(range(3), y, color=INK if mark else GRID, lw=1.8 if mark else 1, zorder=3 if mark else 1)
            ax.scatter(range(3), y, s=14, c=[HEALTHY, ROUTE_COLOR[route], HEALTHY], lw=0, zorder=2)
        med = [r[c].median() for c, _ in cols]
        ax.plot(range(3), med, color=ROUTE_COLOR[route], lw=3, zorder=4, label="median")
        ax.set_title(f"{route.capitalize()} polyps (n = {len(r)})", fontsize=10.5, loc="left")
        ax.set_xticks(range(3), [l for _, l in cols], fontsize=9)
        ax.set_xlim(-0.3, 2.7)
        ax.set_ylim(0, 0.74)
    axes[0].set_ylabel("distance to the person's real polyp\n(energy distance, lower = closer)")
    axes[0].legend(frameon=False, loc="upper right", fontsize=9)
    fig.subplots_adjust(wspace=0.15)
    return fig


def visium_panel(D, F):
    marks = pd.read_csv(D / "visium/marker_calls_spots.tsv.gz", sep="\t", index_col=0)
    summ = pd.read_csv(D / "visium_mapping/mapping_summary.tsv", sep="\t").set_index(["capture", "reference"])
    props = {(s, ref): pd.read_csv(D / f"visium_mapping/props_{s}_{ref}.tsv.gz", sep="\t", index_col=0)
             for s in SECTIONS for ref in ("same", "other")}
    vmax = np.nanpercentile(np.concatenate([p.new_share.values for p in props.values()]), 99)
    heads = ["pathologist", "marker-gene route call", "purity, person's own cells",
             "purity, other people's cells"]
    fig, axes = plt.subplots(len(SECTIONS), 4, figsize=(10, 2.2 * len(SECTIONS)))
    for row, s in enumerate(SECTIONS):
        route = summ.loc[(s, "same"), "truth"]
        own = props[(s, "same")]
        m = marks[marks.capture == s].reindex(own.index)
        ann = own.pathology_annotation.map({"adenoma": ROUTE_COLOR[route], "adenoma_border": ROUTE_COLOR[route],
                                            "normal_mucosa": HEALTHY}).fillna(FAINT)
        call = m.call.map({"conventional": CONV, "serrated": SERR, "normal": HEALTHY}).fillna(FAINT)
        size = 9 if len(own) < 400 else 4
        panels = [(ann, None), (call, None), (own.new_share, "c"), (props[(s, "other")].reindex(own.index).new_share, "c")]
        for col, (vals, kind) in enumerate(panels):
            ax = axes[row, col]
            if kind:
                sc = ax.scatter(own.x, own.y, s=size, c=vals, cmap=PURITY, vmin=0, vmax=vmax, lw=0)
            else:
                ax.scatter(own.x, own.y, s=size, c=list(vals), lw=0)
            ax.set_aspect("equal")
            ax.invert_yaxis()
            ax.set_axis_off()
            if row == 0:
                ax.set_title(heads[col], fontsize=10)
        axes[row, 0].text(-0.08, 0.5, f"{summ.loc[(s, 'same'), 'donor']}\n{route}",
                          transform=axes[row, 0].transAxes, rotation=90, ha="right", va="center", fontsize=9.5)
    handles = [plt.Line2D([], [], marker="o", ls="", ms=7, color=c, label=l)
               for c, l in [(CONV, "conventional polyp"), (SERR, "serrated polyp"), (HEALTHY, "normal lining"),
                            (FAINT, "other tissue")]]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.06, 0.0), ncol=2, frameon=False, fontsize=9)
    cax = fig.add_axes([0.58, 0.035, 0.36, 0.012])
    cb = fig.colorbar(sc, cax=cax, orientation="horizontal")
    cb.set_label("share of polyp-only cells (ASC + SSC) per spot", fontsize=9)
    cb.outline.set_visible(False)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.95, bottom=0.09, hspace=0.12, wspace=0.04)
    return fig


def fig5(D, F):
    """Predict and map: flow per person (a) above the Visium sections (b)."""
    parts = []
    for name, make in [("flow", flow_panel), ("visium", visium_panel)]:
        part = make(D, F)
        path = F / f"report_panel_{name}.png"
        part.savefig(path, dpi=200, bbox_inches="tight")
        plt.close(part)
        parts.append(plt.imread(path))
    heights = [10 * p.shape[0] / p.shape[1] for p in parts]
    fig = plt.figure(figsize=(10, sum(heights) + 0.2))
    gs = fig.add_gridspec(2, 1, height_ratios=heights, hspace=0.04)
    for i, (part, letter) in enumerate(zip(parts, "ab")):
        ax = fig.add_subplot(gs[i])
        ax.imshow(part)
        ax.set_axis_off()
        tag(ax, letter)
    return fig


def main():
    D, F = Path(sys.argv[1]), Path(sys.argv[2])
    style()
    for n, make in enumerate([fig1, fig2, fig3, fig4, fig5], start=1):
        fig = make(D, F)
        out = F / f"report_fig{n}.png"
        fig.savefig(out, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print(out)


if __name__ == "__main__":
    main()
