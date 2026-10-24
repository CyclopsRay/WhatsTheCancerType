"""Next step 3 — from healthy to polyp: a flow that moves one person's healthy cells into each route.

Space: 30 PCs of log-normalised HVGs (genes chosen once per object; the PCA is refitted in every
fold on the training people only), divided by the training cloud's overall SD.
Training pairs come from our step-4 matching, made one-sided: for each training person and route,
entropic optimal transport from that person's healthy cells to their own polyp cells, with
every polyp cell required to be reached (hard target) and the healthy side free to give more or
less mass (KL-relaxed, rho = 1). Healthy cells that feed many polyp cells get a growth weight
> 1, so new cell types can be produced by a few healthy cells growing.
  flow    MLP v(x, t, route), flow matching on pairs sampled from the coupling; Euler, 20 steps
  growth  MLP log-weight(x, route), regressed on each healthy cell's transported mass
Leave-one-person-out test: from the held-out person's healthy cells alone, predict each route's
polyp and compare with that person's real polyp (energy distance, weighted; lower is better).
Baselines: identity (the healthy cells unchanged), mean shift (healthy + the training average
displacement of the route), population (other people's polyp cells of that route).
Composition: share of predicted cells a kNN classifier (training cells, published labels) calls
the route's new state (ASC / SSC), against the real share.
Route check: is the right route's prediction closer to the real polyp than the wrong route's?
Snapshots, not time: the flow is a best guess at the change, not a watched trajectory.

Writes OUT_DIR/flow_people.tsv, flow_summary.tsv and FIG_DIR/fig20_flow.png.

Usage: python polyp_flow.py DATA_DIR CELLS_DIR OUT_DIR FIG_DIR [--test]
"""
import sys
import zlib
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier

from next_common import OBJECTS, NEW_STATE, INK, MUTED, ROUTE_COLOR, SEED, load_object, lognorm, pick_hvg, style_axes

ROUTES = ["conventional", "serrated"]
N_PC, N_SIDE, N_PAIRS = 30, 1500, 20000
MIN_NORMAL, MIN_POLYP = 100, 50
EPS, RHO, SIGMA = 0.05, 1.0, 0.05
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def pick(ix, n, seed):
    return ix if len(ix) <= n else np.sort(np.random.default_rng(seed).choice(ix, n, replace=False))


def seed_of(*parts):
    return zlib.crc32("|".join(map(str, parts)).encode()) % 100000


def sqdist(A, B):
    return torch.clamp((A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T, min=0)


def semi_uot(C, eps=EPS, rho=RHO, n_iter=3000, tol=1e-6):
    """Log-domain Sinkhorn; source marginal KL-relaxed (rho), target marginal exact."""
    n, m = C.shape
    loga, logb = -np.log(n), -np.log(m)
    f, g = torch.zeros(n, device=DEV), torch.zeros(m, device=DEV)
    tau = rho / (rho + eps)
    for it in range(n_iter):
        f = -tau * eps * torch.logsumexp((g[None, :] - C) / eps + logb, dim=1)
        g_new = -eps * torch.logsumexp((f[:, None] - C) / eps + loga, dim=0)
        if it % 20 == 0 and (g_new - g).abs().max() < tol:
            g = g_new
            break
        g = g_new
    return torch.exp((f[:, None] + g[None, :] - C) / eps + loga + logb)


def mlp(d_in, d_out, h=256):
    return torch.nn.Sequential(torch.nn.Linear(d_in, h), torch.nn.SiLU(), torch.nn.Linear(h, h), torch.nn.SiLU(),
                               torch.nn.Linear(h, h), torch.nn.SiLU(), torch.nn.Linear(h, d_out)).to(DEV)


def onehot(route, n):
    r = torch.zeros(n, 2, device=DEV)
    r[:, ROUTES.index(route)] = 1
    return r


def train_flow(x0, x1, rid, steps):
    net = mlp(N_PC + 3, N_PC)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    R = torch.nn.functional.one_hot(rid, 2).float()
    for _ in range(steps):
        b = torch.randint(0, len(x0), (1024,), device=DEV)
        t = torch.rand(1024, 1, device=DEV)
        xt = (1 - t) * x0[b] + t * x1[b] + SIGMA * torch.randn_like(x0[b])
        loss = ((net(torch.cat([xt, t, R[b]], 1)) - (x1[b] - x0[b])) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sched.step()
    return net, float(loss)


def train_growth(xg, rg, yg, steps):
    net = mlp(N_PC + 2, 1, h=128)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    R = torch.nn.functional.one_hot(rg, 2).float()
    for _ in range(steps):
        b = torch.randint(0, len(xg), (1024,), device=DEV)
        loss = ((net(torch.cat([xg[b], R[b]], 1)).squeeze(1) - yg[b]) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return net


@torch.no_grad()
def push(net, x0, route, n_steps=20):
    x, R = x0.clone(), onehot(route, len(x0))
    for k in range(n_steps):
        t = torch.full((len(x), 1), k / n_steps, device=DEV)
        x = x + net(torch.cat([x, t, R], 1)) / n_steps
    return x


def energy(X, Y, wx=None, wy=None):
    wx = torch.full((len(X),), 1 / len(X), device=DEV) if wx is None else wx / wx.sum()
    wy = torch.full((len(Y),), 1 / len(Y), device=DEV) if wy is None else wy / wy.sum()
    d = lambda A, B: torch.sqrt(sqdist(A, B) + 1e-9)
    return float(2 * wx @ d(X, Y) @ wy - wx @ d(X, X) @ wx - wy @ d(Y, Y) @ wy)


def run_fold(L, obs, p, pairs, test):
    train = np.where(obs.donor_id.to_numpy() != p)[0]
    sub = pick(train, 30000, seed_of(p, "pca"))
    Lt = L[sub]
    mu, sd = Lt.mean(0), Lt.std(0) + 1e-6
    pca = PCA(N_PC, random_state=SEED).fit(np.clip((Lt - mu) / sd, -10, 10))
    E = pca.transform(np.clip((L - mu) / sd, -10, 10))
    E = E / np.sqrt((E[train] ** 2).sum(1).mean())
    Et = torch.tensor(E, dtype=torch.float32, device=DEV)
    route_arr, donor_arr, state = obs.route.to_numpy(), obs.donor_id.to_numpy(), obs.Cell_Type.to_numpy()
    i, j = np.random.default_rng(seed_of(p)).integers(0, len(train), (2, 20000))
    scale = float(np.median(((E[train[i]] - E[train[j]]) ** 2).sum(1)))

    x0s, x1s, rids, xg, rg, yg = [], [], [], [], [], []
    for q, route in pairs:
        if q == p:
            continue
        src = pick(np.where((donor_arr == q) & (route_arr == "normal"))[0], N_SIDE, seed_of(q, route, 0))
        tgt = pick(np.where((donor_arr == q) & (route_arr == route))[0], N_SIDE, seed_of(q, route, 1))
        P = semi_uot(sqdist(Et[src], Et[tgt]) / scale)
        mass = P.sum(1) * len(src)
        flat = torch.multinomial(P.flatten() / P.sum(), N_PAIRS // 4 if test else N_PAIRS, replacement=True)
        x0s.append(Et[src][flat // len(tgt)]); x1s.append(Et[tgt][flat % len(tgt)])
        rids.append(torch.full((len(flat),), ROUTES.index(route), device=DEV))
        xg.append(Et[src]); rg.append(torch.full((len(src),), ROUTES.index(route), device=DEV))
        yg.append(torch.log(mass.clamp(1e-3, 1e3)))
    x0, x1, rid = torch.cat(x0s), torch.cat(x1s), torch.cat(rids)
    flow, loss = train_flow(x0, x1, rid, 300 if test else 4000)
    growth = train_growth(torch.cat(xg), torch.cat(rg), torch.cat(yg), 200 if test else 2000)
    shift = {r: (x1[rid == k] - x0[rid == k]).mean(0) for k, r in enumerate(ROUTES)}
    knn = KNeighborsClassifier(15).fit(E[pick(train, 40000, seed_of(p, "knn"))],
                                       state[pick(train, 40000, seed_of(p, "knn"))])

    h = pick(np.where((donor_arr == p) & (route_arr == "normal"))[0], N_SIDE, seed_of(p, "h"))
    xh = Et[h]
    preds = {}
    for route in ROUTES:
        xf = push(flow, xh, route)
        with torch.no_grad():
            w = torch.exp(growth(torch.cat([xh, onehot(route, len(xh))], 1)).squeeze(1).clamp(-5, 5))
        popi = pick(np.where((donor_arr != p) & (route_arr == route))[0], N_SIDE, seed_of(p, route, "pop"))
        preds[route] = {"identity": (xh, None), "mean shift": (xh + shift[route], None),
                        "population": (Et[popi], None), "flow": (xf, None), "flow + growth": (xf, w)}
    rows = []
    for route in ROUTES:
        real = np.where((donor_arr == p) & (route_arr == route))[0]
        if len(real) < MIN_POLYP:
            continue
        xr = Et[pick(real, N_SIDE, seed_of(p, route, "real"))]
        new = NEW_STATE[route]
        row = dict(donor=p, route=route, n_healthy=len(h), n_polyp=len(real),
                   real_new_share=round(float((state[real] == new).mean()), 3), flow_loss=round(loss, 4))
        for name, (Y, w) in preds[route].items():
            row[f"ed_{name}"] = round(energy(Y, xr, w, None), 4)
            lab = knn.predict(Y.cpu().numpy())
            ww = np.ones(len(lab)) if w is None else w.cpu().numpy()
            row[f"new_share_{name}"] = round(float(ww[lab == new].sum() / ww.sum()), 3)
        other = ROUTES[1 - ROUTES.index(route)]
        Y, w = preds[other]["flow + growth"]
        row["ed_flow_wrong_route"] = round(energy(Y, xr, w, None), 4)
        rows.append(row)
    return rows


def main(data_dir, cells_dir, out_dir, fig_dir, test=False):
    out_dir, fig_dir = Path(out_dir), Path(fig_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(SEED)
    print("device", DEV, flush=True)
    tag = "_test" if test else ""
    rows = []
    for obj in OBJECTS:
        X, obs, names = load_object(data_dir, cells_dir, obj)
        hv = pick_hvg(X, names)
        L = lognorm(X[:, hv]).toarray()
        counts = obs.groupby(["donor_id", "route"]).size().unstack(fill_value=0)
        pairs = [(d, r) for d, c in counts.iterrows() for r in ROUTES
                 if c.get("normal", 0) >= MIN_NORMAL and c.get(r, 0) >= MIN_POLYP]
        people = sorted({d for d, _ in pairs})
        if test:
            people = people[:2]
        print(obj, "person-route pairs", len(pairs), "held-out people", len(people), flush=True)
        for p in people:
            for r in run_fold(L, obs, p, pairs, test):
                r["object"] = obj
                rows.append(r)
                print(r, flush=True)
    t = pd.DataFrame(rows)
    t.to_csv(out_dir / f"flow_people{tag}.tsv", sep="\t", index=False)
    summary(t, out_dir, tag)
    figure(t, fig_dir, tag)


METHODS = ["identity", "mean shift", "population", "flow", "flow + growth"]


def summary(t, out_dir, tag):
    rows = []
    for route, g in list(t.groupby("route")) + [("both", t)]:
        r = dict(route=route, n=len(g))
        for m in METHODS:
            r[f"median_ed_{m}"] = round(g[f"ed_{m}"].median(), 4)
            r[f"flowgrowth_beats_{m}"] = int((g["ed_flow + growth"] < g[f"ed_{m}"]).sum()) if m != "flow + growth" else None
            r[f"newshare_corr_{m}"] = round(np.corrcoef(g[f"new_share_{m}"], g.real_new_share)[0, 1], 3) if len(g) > 2 else None
        r["right_route_closer"] = int((g["ed_flow + growth"] < g.ed_flow_wrong_route).sum())
        rows.append(r)
    s = pd.DataFrame(rows)
    s.to_csv(out_dir / f"flow_summary{tag}.tsv", sep="\t", index=False)
    pd.set_option("display.width", 250)
    print(s.T.to_string())


def figure(t, fig_dir, tag):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=200)
    ax = axes[0]
    for _, r in t.iterrows():
        base = r["ed_identity"]
        ax.plot(range(len(METHODS)), [r[f"ed_{m}"] / base for m in METHODS], color=ROUTE_COLOR[r.route],
                alpha=0.45, lw=1, marker="o", ms=3)
    for route in ROUTES:
        g = t[t.route == route]
        ax.plot(range(len(METHODS)), [(g[f"ed_{m}"] / g.ed_identity).median() for m in METHODS],
                color=ROUTE_COLOR[route], lw=3, label=f"{route} ({len(g)} people)")
    ax.set_yscale("log")
    ax.set_yticks([0.25, 0.5, 1, 2, 4, 8], ["0.25", "0.5", "1", "2", "4", "8"])
    ax.minorticks_off()
    ax.axhline(1, color=MUTED, lw=1, ls="--")
    ax.set_xticks(range(len(METHODS)), METHODS, rotation=15)
    ax.set_ylabel("distance to the real polyp\n(relative to unchanged healthy cells)")
    ax.set_title("Predicting a left-out person's polyp", color=INK, loc="left")
    ax.legend(frameon=False)
    style_axes(ax)
    ax = axes[1]
    for route in ROUTES:
        g = t[t.route == route]
        ax.scatter(g.real_new_share, g["new_share_flow + growth"], color=ROUTE_COLOR[route], s=40,
                   label=f"flow + growth, {route}")
        ax.scatter(g.real_new_share, g["new_share_population"], facecolor="none", edgecolor=ROUTE_COLOR[route],
                   s=40, label=f"population, {route}")
    lim = max(t.real_new_share.max(), t["new_share_flow + growth"].max(), t.new_share_population.max()) + 0.05
    ax.plot([0, lim], [0, lim], color=MUTED, lw=1, ls="--")
    ax.set_xlabel("real share of polyp-only cells (ASC / SSC)")
    ax.set_ylabel("predicted share")
    ax.set_title("Does the prediction make the new cells?", color=INK, loc="left")
    ax.legend(frameon=False, fontsize=10)
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(Path(fig_dir) / f"fig20_flow{tag}.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--test"]
    main(*a[:4], test="--test" in sys.argv)
