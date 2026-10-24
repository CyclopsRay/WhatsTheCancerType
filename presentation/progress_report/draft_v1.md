# Reading Each Polyp Against Its Own Healthy Lining: Detecting, Predicting and Mapping the Two Routes of Colorectal Precancer

Yuqi Lei, Muhammed Bah

<!-- Placeholders: [TBD: ...] = running experiment or figure still to be made. Word count is in the
     note below the references. -->

## Abstract

Colorectal cancer grows out of two kinds of polyp, conventional adenomas and serrated lesions.
Marker genes can label typical polyps of each kind, but they do not generalise to atypical polyps
and cannot describe how a polyp changes as it climbs the mutation ladder. Another problem is that current single-cell atlases pool many people's profile together and cannot generate individual gene expression polyp reports. Therefore, We read every polyp
against the same person's healthy lining, and build model to tackle these problems. First, we train a reconstruction model of healthy lining alone that separates the polyps from healthy lining cells using single cell gene expression [TBD:
confirm with anomaly v2]. Then, we predict the polyp from healthy lining by training a flow learned on other people
moves a new person's healthy cells toward their polyp along the correct route. Last, we map polyp purity
and route in tissue, where the person's own cells find adenoma cells that other people's cells miss.

## 1. Introduction

Most colorectal cancers begin as polyps, and polyps follow one of two routes. Conventional
adenomas start with loss of APC and climb a well-known ladder of mutations (1). Serrated lesions
start with BRAF activation and widespread gene silencing (2). They give rise to about 10–30 % of
colorectal cancers [TBD: cite review]. Because they are flat and pale, they are easier to miss at
colonoscopy. Telling the two routes apart, cell by cell and in the tissue itself, is therefore
central to early detection.

Single-cell atlases have mapped both routes. Chen et al. (3) defined an adenoma-specific cell
(ASC) that grows from crypt stem cells ("bottom-up") and a serrated-specific cell (SSC) that arises
from mature cells through metaplasia ("top-down"). Becker et al. (4) described a stem-like
continuum from polyp to cancer, Heiser et al. (5) followed tumour evolution in space, and Islam et
al. (6) showed that some polyps start from several founder cells. Mutations alone do not mark a
polyp: healthy crypts already carry cancer-gene mutations by middle age (7).

These studies compare groups of people, yet each person brings their own genetics, age, colon site
and sample handling. In the atlas, seven of every ten neighbours of a polyp cell come from the same
person, so a pooled comparison mixes polyp and person. Most analyses also rest on marker genes.
Markers label typical polyps well, but they do not generalise to atypical ones, such as lesions
with few of the expected new cells or an adenoma that also carries the serrated programme. A fixed
label also cannot describe how a polyp changes as it climbs the mutation ladder. Healthy reference
atlases can isolate disease-altered cells without labels (8); we bring this idea to precancer,
within each person.

We therefore anchor every analysis to the person and move from detection to prediction to
mapping. We first ask which polyp cells differ from the same person's healthy lining, with the
published labels and with a label-free model of healthy lining, and which changes belong to one
route. We then ask whether a model learned on other people can turn a new person's healthy cells
into their polyp along the right route, describing the change rather than only its end point.
Finally, we place single cells onto tissue to measure how pure each spot is and which route it follows.

## 2. Methods

**Data.** HTAN Vanderbilt epithelial single-cell objects (3): a discovery set (DIS; 65,088 cells,
62 specimens) and an independent validation set (VAL; 57,723 cells, 59 specimens), with the
authors' nine cell-state labels. 19 people have healthy lining and a conventional polyp (tubular /
tubulovillous adenoma), 15 a serrated one (hyperplastic polyp / sessile serrated lesion). Seven
Visium polyp sections come from six people, all with single-cell data [TBD: confirm source, likely (5)].

**Step 1 — Detect.** *Composition:* per person, each cell state's share in the polyp minus the
lining (Wilcoxon signed-rank). *Genes:* per-specimen pseudobulk (≥ 30 cells) tested with PyDESeq2
(9) as `~ person + condition`, so each polyp is compared only with its own lining (10); hits have
adjusted p < 0.05 and |log2 fold change| > 1. Route-specific genes are hits in one route that also
differ between routes (BH < 0.05). DIS hits are re-tested in VAL. *Label-free:* in 33 person ×
route tests, a variational autoencoder (11) is trained on other people's healthy cells only, and
each held-out cell is scored by how badly it is reconstructed (negative-binomial deviance per
count) [TBD: final score and gene set]. Polyp cells are compared with the person's own healthy
cells (AUROC, AUPRC).

**Step 2 — Predict.** In 30 principal components, unbalanced optimal transport (12) pairs each
training person's healthy cells with their own polyp cells, and a flow-matching network (13) learns
the movement. A held-out person's healthy cells are moved by the flow and compared with their real
polyp (energy distance), against unchanged cells and the other route's flow.

**Step 3 — Map.** DestVI (14) splits each Visium spot into cell types with the person's own single
cells as reference. *Purity* is the per-spot share of polyp-only cells (ASC + SSC); a section's
*route* is the dominant one. Comparisons: an other-people reference and textbook marker genes (Wnt
targets; MUC5AC, TFF1, ANXA10). Pathologist annotations are the ground truth.

## 3. Preliminary Results

**Polyps are read best against their own lining.** Each polyp is closest to its own person's
healthy lining in 21 of 36 cases (1.7 expected by chance). Pairing lowers the standard error of
gene effects by about 16 %.

**Each route adds its own new cell type.** ASC rises in 16 of 19 conventional polyps and SSC in
13 of 15 serrated polyps (Fig. 1). In the median polyp they make up 24–48 % (ASC) and 17–22 %
(SSC) of the epithelium, while healthy lining has almost none.

**Shared and route-specific genes replicate.** In DIS, 224 genes change the same way in both routes
(up: MUC5AC, REG4; down: AQP8, CLCA4). There are 53 conventional-specific genes, led by Wnt targets
(ASCL2, NKD1, MMP7), and 68 serrated-specific genes (TFF1, TFF2, ANXA1) (Fig. 2a). In VAL, 99 %
(conventional) and 97 % (serrated) of DIS hits change in the same direction (Fig. 2b). Wnt
signalling is enriched only in conventional polyps (NES +1.96 DIS, +1.64 VAL), and TNF-α signalling
only in serrated polyps (+2.06, +1.83).

**A healthy-only model separates the routes by origin.** [TBD: anomaly v2 numbers — polyp vs own
healthy, per route; top unrebuildable genes.] SSC cells are the least healthy-like cells in the
data [TBD: v2 value; v1: scores above 99 % of the person's own healthy cells]. ASC cells instead sit
next to healthy stem cells. Their stem-gene score equals or exceeds the person's own healthy stem
cells in 11 of 11 people, while SSC cells carry low stem and intermediate mature genes (Fig. 3).
Without using labels, the healthy model thus reproduces the two origins: expansion of an existing
stem state for adenomas, and a state absent from healthy lining for serrated lesions.

**Healthy lining points to the right route.** From a held-out person's healthy cells, the flow
lands closer to the real polyp than the unchanged cells in 23 of 33 tests, and in 20 of 21 polyps
with at least 10 % new cells. The right-route flow beats the wrong-route flow in 25 of 33 (Fig. 4).
In the one person carrying both routes, each flow lands closer to its matching polyp (adenoma 0.17
vs 0.27; serrated 0.14 vs 0.30).

**Tissue maps recover route and purity.** Marker genes call the route of all 7 sections correctly.
With the person's own cells as the reference, DestVI calls 6 of 7, and 5 of 7 with other people's
cells. It finds ASC in two adenomas where the other-people reference finds none (share 0.19 vs
0.00; 0.08 vs 0.00). The share of polyp-only cells separates pathologist-drawn polyp from normal
spots with AUC 0.62–0.85 (Fig. 5) [TBD: purity map panel].

## 4. Preliminary Conclusion and Next Steps

Reading each polyp against the same person's healthy lining recovers the textbook two-route model
from data alone. Each route has its own new cell type and gene programme, and both replicate in an
independent cohort. A model of healthy lining separates the routes by origin without labels. A
person's healthy cells point toward the right route, and the person's own cells sharpen the polyp
map in tissue. Next we will:

1. **Detect:** finish the healthy-only model on all detected genes and report which genes it
   cannot rebuild in each person's polyp.
2. **Predict:** add the person's own healthy cell composition to the flow, and test whether it adds
   information beyond the average polyp of other people.
3. **Map:** turn spot purity into polyp borders and compare them with the pathologist's outline,
   including the lining next to the polyp.
4. **Landmarks:** use the open exome calls to tie each polyp's mutations to its route and purity.

## Figures

**Figure 1. Each route adds its own new cell type.** (a) [TBD: schematic of the three steps —
detect, predict, map — each anchored to one person.] (b) Share of ASC (conventional) and SSC
(serrated) cells in healthy lining and polyp; one line per person. *Source: `figures/fig8_new_cells.png`.*

**Figure 2. Shared and route-specific gene changes.** (a) log2 fold change, polyp vs own lining, in
conventional (x) and serrated (y) polyps; colours mark shared and route-specific genes. (b) DIS
hits re-measured in VAL. *Source: `fig3_route_compare_DIS_all.png`, `fig4_replication.png`.*

**Figure 3. A healthy-only model separates the routes by origin.** (a) [TBD: fig22, anomaly v2,
per-person score and per-cell-type score.] (b) Stem vs mature gene scores per person.
*Source: (b) `fig14_stem_mature.png`.*

**Figure 4. Healthy lining points to the right route.** [TBD: redraw from
`derived/flow/flow_people.tsv` — distance to the real polyp for unchanged cells, right-route flow
and wrong-route flow, one line per held-out person; mark HTA11_6801.]

**Figure 5. Polyp purity and route in tissue.** Pathologist annotation, marker-gene route call, and
ASC / SSC share per spot from DestVI with the person's own reference. [TBD: composite from
`fig15_visium_marker_calls.png` and `fig21_visium_mapping.png`, 3–4 sections.]

## References

<!-- Verify volume/pages before submission; 2 placeholders remain. -->

1. Fearon ER, Vogelstein B. A genetic model for colorectal tumorigenesis. *Cell* 61, 759–767 (1990).
2. Snover DC. Update on the serrated pathway to colorectal carcinoma. *Hum Pathol* 42, 1–10 (2011).
3. Chen B, et al. Differential pre-malignant programs and microenvironment chart distinct paths to
   malignancy in human colorectal polyps. *Cell* 184, 6262–6280 (2021).
4. Becker WR, et al. Single-cell analyses define a continuum of cell state and composition changes
   in the malignant transformation of polyps to colorectal cancer. *Nat Genet* 54, 985–995 (2022).
5. Heiser CN, et al. Molecular cartography uncovers evolutionary and microenvironmental dynamics in
   sporadic colorectal tumors. *Cell* 186, 5620–5637 (2023).
6. Islam M, et al. Temporal recording of mammalian development and precancer. *Nature* 634,
   1187–1195 (2024).
7. Lee-Six H, et al. The landscape of somatic mutation in normal colorectal epithelial cells.
   *Nature* 574, 532–537 (2019).
8. Dann E, et al. Precise identification of cell states altered in disease using healthy
   single-cell references. *Nat Genet* 55, 1998–2008 (2023).
9. Muzellec B, et al. PyDESeq2: a python package for bulk RNA-seq differential expression analysis.
   *Bioinformatics* 39, btad547 (2023).
10. Squair JW, et al. Confronting false discoveries in single-cell differential expression.
    *Nat Commun* 12, 5692 (2021).
11. Lopez R, et al. Deep generative modeling for single-cell transcriptomics. *Nat Methods* 15,
    1053–1058 (2018).
12. Chizat L, et al. Scaling algorithms for unbalanced optimal transport problems. *Math Comput* 87,
    2563–2609 (2018).
13. Lipman Y, et al. Flow matching for generative modeling. *ICLR* (2023).
14. Lopez R, et al. DestVI identifies continuums of cell types in spatial transcriptomics data.
    *Nat Biotechnol* 40, 1360–1369 (2022).
15. [TBD: serrated-pathway review for the 10–30 % figure.]
