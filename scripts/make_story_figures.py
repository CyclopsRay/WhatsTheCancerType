"""Plain-language figures for the talk (no cohort or cell-state codes on the figure).

fig8_new_cells.png: per person, share of the route's new cell type in healthy lining
vs polyp, DIS and VAL pooled (one line = one person).
fig11-14, fig17 (need derived/label_free from label_free_view.sh and crypt_axis_scores.sh):
one person's own map; polyp cells with no healthy look-alike; healthy vs polyp cells
coloured by person; per-person stem vs mature gene scores.

Usage: python make_story_figures.py DERIVED_DIR FIG_DIR
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

INK, MUTED, GRID = "#1d1a29", "#6e6980", "#d9d6e0"
ROUTES = [("conventional", "ASC", "#2a78d6", "Conventional polyps", "adenoma-type cells"),
          ("serrated", "SSC", "#eb6834", "Serrated polyps", "serrated-type cells")]


def per_person(pb_dir, route, state):
    rows = []
    for obj in ["DIS", "VAL"]:
        spec = pd.read_csv(pb_dir / f"{obj}_specimens.tsv", sep="\t").set_index("HTAN Specimen ID")
        comp = pd.read_csv(pb_dir / f"{obj}_composition.tsv", sep="\t", index_col=0)
        frac = 100 * comp.div(comp.sum(1), axis=0)[state]
        for d, s in spec.groupby("donor_id"):
            p, n = s.index[s.route == route], s.index[s.route == "normal"]
            if len(p) and len(n):
                rows.append((frac[n].mean(), frac[p].mean()))
    return pd.DataFrame(rows, columns=["normal", "polyp"])


def main(derived, fig_dir):
    pb_dir = Path(derived) / "pseudobulk"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 15,
                         "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), dpi=200)
    for ax, (route, state, color, title, cell) in zip(axes, ROUTES):
        df = per_person(pb_dir, route, state)
        up = int((df.polyp > df.normal).sum())
        for _, r in df.iterrows():
            ax.plot([0, 1], [r.normal, r.polyp], color=color, lw=2, alpha=0.85,
                    marker="o", ms=8, mec="white", mew=1.5)
        ax.set_xticks([0, 1], ["healthy lining", "polyp"], fontsize=16, color=INK)
        ax.set_xlim(-0.25, 1.25)
        ax.set_ylim(0, 80)
        ax.set_ylabel(f"% {cell}", color=INK, fontsize=16)
        ax.yaxis.grid(True, color=GRID, lw=1)
        ax.set_axisbelow(True)
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        ax.set_title(f"{title}: up in {up} of {len(df)} people", loc="left",
                     fontsize=18, color=INK, pad=14)
    fig.tight_layout(w_pad=4)
    out = Path(fig_dir) / "fig8_new_cells.png"
    fig.savefig(out, facecolor="white")
    print(out)


TISSUE = [("normal", "#b4b0bf", "healthy lining"), ("conventional", "#2a78d6", "conventional polyp"),
          ("serrated", "#eb6834", "serrated polyp")]
ACCENT, BACK = "#a8365c", "#e4e1ea"


def no_axes(ax):
    ax.set_axis_off()
    ax.set_aspect("equal", adjustable="datalim")


def fig_one_person(lf, fig_dir):
    """fig11: one person's own map (HTA11_6801), coloured by which sample each cell came from."""
    d = pd.read_csv(lf / "person_6801_embedding.tsv.gz", sep="\t").sample(frac=1, random_state=0)
    fig, ax = plt.subplots(figsize=(8, 7.4), dpi=200)
    ax.scatter(d.umap1, d.umap2, s=7, c=d.route.map({r: c for r, c, _ in TISSUE}), lw=0, rasterized=True)
    for r, c, lab in TISSUE:
        ax.scatter([], [], s=140, c=c, label=lab)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3, frameon=False, fontsize=16,
              handletextpad=0.2, columnspacing=1.2)
    no_axes(ax)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig11_one_person_map.png", facecolor="white")
    plt.close(fig)


def fig_lookalike(lf, fig_dir, obj="DIS"):
    """fig12: everyone's map; polyp cells whose 30 nearest cells hold <= 5 % healthy cells."""
    d = pd.read_csv(lf / f"{obj}_embedding.tsv.gz", sep="\t")
    far = (d.route != "normal") & (d.nbr_normal <= 0.05)
    fig, ax = plt.subplots(figsize=(8, 7.4), dpi=200)
    ax.scatter(d.umap1[~far], d.umap2[~far], s=0.6, c=BACK, lw=0, rasterized=True)
    ax.scatter(d.umap1[far], d.umap2[far], s=0.6, c=ACCENT, lw=0, rasterized=True)
    ax.scatter([], [], s=140, c=ACCENT, label="polyp cell with no healthy look-alike")
    ax.scatter([], [], s=140, c=BACK, label="every other cell")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=2, frameon=False, fontsize=16,
              handletextpad=0.2, columnspacing=1.2)
    no_axes(ax)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig12_no_lookalike.png", facecolor="white")
    plt.close(fig)


def fig_person_clumps(lf, fig_dir, obj="DIS"):
    """fig13: the same map twice; healthy cells, then polyp cells, coloured by person."""
    d = pd.read_csv(lf / f"{obj}_embedding.tsv.gz", sep="\t").sample(frac=1, random_state=0)
    donors = sorted(d.donor_id.unique())
    pal = plt.get_cmap("tab20")(range(20))
    rng = np.random.default_rng(1)
    cmap = {p: pal[i % 20] for i, p in enumerate(rng.permutation(donors))}
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.6), dpi=200)
    for ax, (polyp, title) in zip(axes, [(False, "Healthy cells"), (True, "Polyp cells")]):
        on = (d.route != "normal") == polyp
        share = d.nbr_same_donor[on].median()
        ax.scatter(d.umap1[~on], d.umap2[~on], s=0.4, c=BACK, lw=0, rasterized=True)
        ax.scatter(d.umap1[on], d.umap2[on], s=0.6, c=[cmap[p] for p in d.donor_id[on]], lw=0, rasterized=True)
        ax.set_title(f"{title}: {round(share * 10)} in 10 neighbours from the same person",
                     fontsize=17, color=INK, loc="left")
        no_axes(ax)
    fig.tight_layout(w_pad=3)
    fig.savefig(fig_dir / "fig13_person_clumps.png", facecolor="white")
    plt.close(fig)


def fig_person_highlight(lf, fig_dir, obj="DIS", people=(("HTA11_696", "conventional"), ("HTA11_411", "serrated"))):
    """fig17: everyone's map; one person's healthy and polyp cells highlighted, per panel."""
    d = pd.read_csv(lf / f"{obj}_embedding.tsv.gz", sep="\t")
    col = dict((r, c) for r, c, _ in TISSUE)
    fig, axes = plt.subplots(1, len(people), figsize=(7 * len(people), 7.2), dpi=200)
    for ax, (donor, route) in zip(axes, people):
        me = d.donor_id == donor
        ax.scatter(d.umap1[~me], d.umap2[~me], s=0.4, c=BACK, lw=0, rasterized=True)
        h, p = d[me & (d.route == "normal")], d[me & (d.route == route)]
        ax.scatter(h.umap1, h.umap2, s=1.6, c="#6e6980", lw=0, rasterized=True)
        ax.scatter(p.umap1, p.umap2, s=1.6, c=col[route], lw=0, rasterized=True)
        ax.scatter([], [], s=120, c="#6e6980", label="this person’s healthy lining")
        ax.scatter([], [], s=120, c=col[route], label=f"this person’s {route} polyp")
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=1, frameon=False, fontsize=16,
                  handletextpad=0.2)
        no_axes(ax)
    fig.tight_layout(w_pad=3)
    fig.savefig(fig_dir / "fig17_person_highlight.png", facecolor="white")
    plt.close(fig)


def fig_stem_mature(lf, fig_dir):
    """fig14: per person, mean stem-gene and mature-gene score of four cell groups (DIS + VAL)."""
    d = pd.concat([pd.read_csv(lf / f"{o}_crypt_scores.tsv.gz", sep="\t") for o in ["DIS", "VAL"]])
    groups = [("normal", "STM", "#6e6980", "healthy stem cells"),
              ("normal", "ABS", "#c9c5d3", "healthy mature absorbing cells"),
              ("conventional", "ASC", "#2a78d6", "adenoma-type cells"),
              ("serrated", "SSC", "#eb6834", "serrated-type cells")]
    g = d.groupby(["donor_id", "route", "Cell_Type"])
    m = g[["stem", "mature"]].mean().assign(n=g.size()).reset_index()
    m = m[m.n >= 20]
    fig, ax = plt.subplots(figsize=(9, 7.4), dpi=200)
    for route, state, color, label in groups:
        s = m[(m.route == route) & (m.Cell_Type == state)]
        ax.scatter(s.stem, s.mature, s=110, c=color, edgecolor="white", lw=1.2, alpha=0.95,
                   label=f"{label} ({len(s)} people)")
    ax.set_xlabel("stem-cell genes  →", fontsize=17, color=INK)
    ax.set_ylabel("mature-cell genes  →", fontsize=17, color=INK)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlim(left=0); ax.set_ylim(bottom=0)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.legend(loc="upper right", frameon=False, fontsize=15, handletextpad=0.2)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig14_stem_mature.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main(*sys.argv[1:3])
    lf, figs = Path(sys.argv[1]) / "label_free", Path(sys.argv[2])
    if lf.exists():
        fig_one_person(lf, figs); fig_lookalike(lf, figs); fig_person_clumps(lf, figs)
        fig_person_highlight(lf, figs)
        if (lf / "DIS_crypt_scores.tsv.gz").exists():
            fig_stem_mature(lf, figs)
