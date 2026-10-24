"""Tissue pictures of one conventional and one serrated polyp for the talk.

Crops the H&E image stored with each OSF Visium capture and outlines the spots the
pathologist marked as polyp (`adenoma`, `adenoma_border`) in the route colour.
No axes or text on the picture; labels live on the slide. Turned 90 degrees clockwise
so both sit landscape in one slide row.

fig9_he_conventional.png: 8270_1 (HTA11_07862, TA/TVA, sigmoid), left tissue piece.
fig9_he_serrated.png:     8270_5 (HTA11_06134, SSL/HP, sigmoid), whole strip.

Usage: python make_he_panels.py ST_MASTER_DIR FIG_DIR
"""
import sys
from pathlib import Path

import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage

# capture, output name, route colour, crop box in hires pixels (x0, x1, y0, y1)
PANELS = [("8270_1_HTA11_07862", "fig9_he_conventional.png", "#2a78d6", (205, 640, 610, 1470)),
          ("8270_5_HTA11_06134", "fig9_he_serrated.png", "#eb6834", (470, 1130, 370, 1190))]
POLYP = {"adenoma", "adenoma_border"}


def load(path):
    h = h5py.File(path, "r")
    lib = list(h["uns/spatial"].keys())[0]
    img = np.clip(h[f"uns/spatial/{lib}/images/hires"][:], 0, 1)
    sf = h[f"uns/spatial/{lib}/scalefactors"]
    xy = h["obsm/spatial"][:] * sf["tissue_hires_scalef"][()]
    radius = sf["spot_diameter_fullres"][()] * sf["tissue_hires_scalef"][()] / 2
    g = h["obs/pathology_annotation"]
    cats = np.array([c.decode() if isinstance(c, bytes) else c for c in g["categories"][:]])
    return img, xy, radius, cats[g["codes"][:]]


def polyp_mask(shape, xy, radius, labels):
    """Disc per polyp spot, closed so neighbouring spots (100 um apart) merge into one region."""
    yy, xx = np.mgrid[:shape[0], :shape[1]]
    mask = np.zeros(shape[:2], bool)
    for x, y in xy[np.isin(labels, list(POLYP))]:
        mask |= (xx - x) ** 2 + (yy - y) ** 2 <= (2.2 * radius) ** 2
    return ndimage.binary_fill_holes(ndimage.binary_closing(mask, iterations=6))


def main(st_dir, fig_dir):
    for capture, name, color, (x0, x1, y0, y1) in PANELS:
        img, xy, radius, labels = load(Path(st_dir) / f"{capture}_master.h5ad")
        img, xy = img[y0:y1, x0:x1], xy - [x0, y0]
        mask = polyp_mask(img.shape, xy, radius, labels)
        img, mask = np.rot90(img, -1), np.rot90(mask, -1)
        fig = plt.figure(figsize=(img.shape[1] / 100, img.shape[0] / 100), dpi=200)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img)
        ax.contour(mask, levels=[0.5], colors=[color], linewidths=2.2, linestyles="--")
        ax.set_axis_off()
        fig.savefig(Path(fig_dir) / name, dpi=200, facecolor="white")
        plt.close(fig)
        print(name, img.shape, int(np.isin(labels, list(POLYP)).sum()), "polyp spots")


def route_gene_panels(st_dir, fig_dir, spots_tsv, k=7):
    """fig16: the two slide-2 slices, spots coloured by their route's textbook gene score.

    Score = z of the route's marker set from visium_marker_calls.py (Wnt genes for the
    conventional slice, stomach-like genes for the serrated one), averaged over each spot and its
    6 nearest neighbours; dashed line = pathologist's polyp outline.
    """
    from matplotlib.colors import LinearSegmentedColormap
    from sklearn.neighbors import NearestNeighbors
    import pandas as pd
    spots = pd.read_csv(spots_tsv, sep="\t", index_col=0)
    sets = {"#2a78d6": "z_conventional", "#eb6834": "z_serrated"}
    # conventional: whole slice (polyp piece + two healthy pieces), not rotated;
    # serrated: the slide-2 crop, rotated as there
    views = [(PANELS[0][0], PANELS[0][1], PANELS[0][2], None, False), PANELS[1] + (True,)]
    for capture, name, color, box, turn in views:
        img, xy, radius, labels = load(Path(st_dir) / f"{capture}_master.h5ad")
        if box is None:
            m = 3 * radius
            box = (int(max(xy[:, 0].min() - m, 0)), int(min(xy[:, 0].max() + m, img.shape[1])),
                   int(max(xy[:, 1].min() - m, 0)), int(min(xy[:, 1].max() + m, img.shape[0])))
        x0, x1, y0, y1 = box
        s = spots[spots.capture == capture]
        assert len(s) == len(xy)
        idx = NearestNeighbors(n_neighbors=k).fit(xy).kneighbors(xy, return_distance=False)
        score = s[sets[color]].to_numpy()[idx].mean(1)
        mask = polyp_mask(img.shape, xy, radius, labels)
        img, xy, mask = img[y0:y1, x0:x1], xy - [x0, y0], mask[y0:y1, x0:x1]
        inside = (xy[:, 0] >= 0) & (xy[:, 0] < x1 - x0) & (xy[:, 1] >= 0) & (xy[:, 1] < y1 - y0)
        rx, ry = xy[:, 0], xy[:, 1]
        if turn:  # 90 deg clockwise: (x, y) -> (H - 1 - y, x)
            H = img.shape[0]
            img, mask = np.rot90(img, -1), np.rot90(mask, -1)
            rx, ry = H - 1 - xy[:, 1], xy[:, 0]
        gray = img[..., :3].mean(-1)
        cmap = LinearSegmentedColormap.from_list("route", ["#f4f2f7", color])
        vmax = np.quantile(score, 0.95)
        fig = plt.figure(figsize=(img.shape[1] / 100, img.shape[0] / 100), dpi=200)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(gray, cmap="gray", vmin=0, vmax=1, alpha=0.45)
        ax.scatter(rx[inside], ry[inside], s=(radius * 1.6) ** 2 / 4, c=np.clip(score[inside], 0, vmax),
                   cmap=cmap, vmin=0, vmax=vmax, lw=0)
        ax.contour(mask, levels=[0.5], colors=["#1d1a29"], linewidths=2.0, linestyles="--")
        ax.set_xlim(0, img.shape[1]); ax.set_ylim(img.shape[0], 0)
        ax.set_axis_off()
        out = name.replace("fig9_he_", "fig16_genes_")
        fig.savefig(Path(fig_dir) / out, dpi=200, facecolor="white")
        plt.close(fig)
        print(out, "spots shown", int(inside.sum()))


if __name__ == "__main__":
    main(*sys.argv[1:3])
    if len(sys.argv) > 3:
        route_gene_panels(*sys.argv[1:4])
