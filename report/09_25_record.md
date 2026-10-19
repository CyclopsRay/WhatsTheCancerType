# HTA11 — Weekly Record, week ending Friday 2026-09-25

Reporting interval: [2026-09-18T18:00:00+04:00, 2026-09-25T18:00:00+04:00) — Asia/Dubai.

Plans, discussion, decisions, reasoning, and corrections (Chinese or English).

## 2026-09-18 — Access audit closes the "what can we get" question; roadmap implications

AI-assisted brainstorming and evidence notes. Pending team decision by Yuqi Lei
and Muhammed Bah. Not submission prose.

### What prompted this

User asked, in roadmap terms, what HTA11 data is obtainable **without a special
request**. Rather than re-browse the portal, the released manifest was parsed
directly. Numbers are in [09_25_report.md](09_25_report.md), method and derived
tables in [record 005](../record/005_open_access_audit/README.md).

### Decisions this evidence forces

**1. Drop "normal -> adenoma -> CRC" as the main contrast.** The open scRNA
release has 7 CRC specimens at Level 4 (18 donors at Level 3) and 3 donors with
matched normal, against 90 normal / 66 conventional-adenoma / 40 serrated
specimens with 28 and 21 within-donor pairs. The three-stage framing spends the
project's power on its weakest arm. The user's own instinct — normal to polyp —
is the arm the data actually supports. CRC stays in as a *direction check*: score
programs fixed on the polyp contrast in the CRC specimens and report whether they
extend, explicitly as an underpowered descriptive endpoint.

**2. "Under a certain circumstance" should become the conditioning axis, and the
obvious one is route.** Conventional (TA/TVA) versus serrated (SSL/HP) are both
well represented and both paired to matched normal from the same donors. That
turns a plain differential-expression list — which Chen et al. 2021 already
published — into a comparative question with a real answer space: which part of
the normal-to-polyp epithelial program is common to both routes, and which is
route-specific. Candidate axes considered and their standing:

| Axis | Support in open data | Standing |
|---|---|---|
| Route: conventional vs serrated | 28 and 21 paired donors | **recommended primary** |
| Driver genotype (APC/KRAS/BRAF) | 85 donors overlap the open WES VCFs | strong, gated on VCF usability |
| Anatomical site (proximal/distal) | site metadata not yet extracted | unknown; confounded with route |
| Donor field effect in adjacent normal | needs healthy-donor vs lesion-adjacent normal split | interesting, metadata unverified |

Route and site are biologically entangled (serrated lesions are proximal); if the
site field turns out to be populated, the crossing must at least be reported.

**3. The spatial arm should be MxIF-first, not Visium-first.** `ROADMAP.md` and
`PLAN.md` leave this open. Evidence now says Visium carries only 7 polyp captures
and shares 10 participants with scRNA, while MxIF has 28 polyp specimens and
shares 32 participants. The blocker was that HTAN releases MxIF as images only —
but OSF `hftq2` carries 16 per-specimen segmented threshold quantification
tables, so the segmentation cost disappears. Visium's 7 polyp captures remain
useful as an illustrative localization check, not as the powered spatial endpoint.

**4. DNA is back on the table as an option, not as a dependency.** 253 open
Level-3 exome VCFs, 85 donors shared with scRNA. This would make the genotype
axis available. But the filenames are GATK germline-style with no matched-normal
token, so nothing is promised until a few are opened. Keep it as an extension
that can be dropped without changing the main question.

### Proposed question for the team to react to

Draft, for each student to rewrite in their own words:

> Which epithelial transcriptional programs distinguish colorectal polyps from
> matched normal mucosa of the same donor, how much of that program is shared
> between the conventional and serrated routes versus specific to one of them,
> and how consistently does it appear across donors and in tissue context?

It is open-ended, the outcome is quantitative (state abundance, within-state
pseudobulk effect sizes, overlap statistics between two route signatures, donor
consistency counts), and the replication unit is the donor, not the cell.

### Objection to the original phrasing, recorded

"Marker genes that play an important role when normal turns into polyp" fails on
two counts. *Important role* is causal and cross-sectional expression cannot
establish it — the honest verb is "distinguishes" or "is associated with".
And a single ranked gene list from this dataset largely reproduces published
work; the comparative and consistency framing is where this project's own
contribution sits.

### Open questions for the team

- Accept route as the conditioning axis, or prefer driver genotype (higher
  ceiling, gated on the VCF check in Week 1)?
- Pool HP with SSL as "serrated", or keep HP separate? Pooling buys 17 donors.
- Does the course require a second modality or a predictive-ML component? Still
  unanswered and it changes whether the MxIF arm is mandatory.
- Who runs the Week-1 H5AD `obs` audit versus the Synapse/OSF retrieval.

### Still to do before any of this is fixed

Match HTAN biospecimen IDs to the `obs` columns inside the three downloaded
H5ADs. Every count in this entry is portal metadata; the matrices have not been
opened, so the analysis cohort is proposed, not selected.

### Decision taken 2026-09-18 (user)

- **Conditioning axis: route primary, driver genotype as a droppable extension.**
  The paired conventional/serrated contrast is the deliverable; the 85-donor
  scRNA-WES overlap is tested only if the Week-1 VCF spot-check passes.
- **Spatial: MxIF-first**, using the OSF pre-segmented quantification tables.
  Visium's 7 polyp captures are an illustrative endpoint, not the powered one.
- **Three-stage framing dropped** from the main contrast; CRC retained as a
  declared underpowered direction check.
- **Stanford GSE201348 drops** as an external-support cohort — a within-donor
  paired design cannot be replicated there. The access audits in records 002 and
  003 stay as historical evidence.

`ROADMAP.md`, `PLAN.md` and `CLAUDE.md` were rewritten to match. Both students
still write and type their own six answers; the roadmap file is a planning
document, not submission prose.

### 2026-09-18 (later) — `obs` audit, and what it does to the plan

The Week-1 cohort gate is passed: `HTAN Specimen ID` and `donor_id` are in `obs`,
so the paired design is real and not an assumption. Numbers in
[09_25_report.md](09_25_report.md).

Three things changed as a result.

**The paired counts shrank.** 19 and 15, not 28 and 21. The larger numbers belong
to the full six-object Level-4 release; we hold three objects. The design still
works — 19 paired donors is a respectable paired contrast — but the roadmap now
plans against the measured figure and treats the rest as upside. If the Synapse
governance issue clears, the numbers improve and nothing else about the design
changes.

**DIS and VAL are donor-disjoint.** One shared donor, zero shared specimens. The
earlier caution against calling them independent was based on a wrong reading.
This is better than expected: discovery in DIS, validation in VAL, genuinely
independent donors, which is exactly what Week 8 needed.

**The cancer-subtype question is not answerable in this data.** The user proposed
adding "is there a common marker gene that turns polyps into cancer, among
different cancer types". Epithelial objects have no MSS/MSI label at all — one
`UNC` bucket, 7 donors. MSS and MSI-H exist only in the non-epithelial object at
5 and 2 donors. That is not a contrast; it is two anecdotes. Recommendation is to
drop the second question rather than weaken it, and if the subtype angle matters
to the team, move it to the OSF spatial atlas as a separate, clearly-labelled
carcinoma-versus-carcinoma analysis on different donors.

**Site is confounded with donor** — every donor has exactly one `tissue` value.
The good side: matched normal is site-matched to its polyp by construction. The
cost: site effects are only testable between donors, so the route/site
entanglement noted earlier cannot be resolved within donors. Say so rather than
controlling for it.

Minor but will bite: DIS writes `TVA`, VAL writes `TV`. Harmonize before pooling.

### 2026-09-18 — Optimal transport: what it is for in this project

User clarified that the OT idea is not about finding the paired normal specimen
(that is a metadata join on `donor_id`) but about deciding **which cell turns
into which** when comparing normal and adenoma scRNA.

**The correction.** An OT coupling between the normal and adenoma distributions
is a transcriptional correspondence, not ancestry. Waddington-OT reads a coupling
as lineage only under assumptions this data violates: the same population sampled
at successive times, short intervals, continuous movement in expression space.
Here the two samples are simultaneous snapshots of two different tissues,
separated by years of clonal evolution, and the founder clone is in neither
sample. The adenoma epithelium is also genetically distinct (APC loss,
aneuploidy), so the transport crosses a genomic boundary, not only a
transcriptional one. Directional or lineage language on an OT result from this
dataset is not defensible.

**The reframe adopted.** Keep the method, change the question to one it can
answer:

> Does adenoma epithelium contain states with no normal counterpart, or is it a
> redistribution of states already present in normal mucosa?

Use **unbalanced** OT, where unmatched mass is the quantity of interest: high
unmatched mass means genuinely new states, low unmatched mass with a shifted
coupling means the same states in new proportions. The comparative version —
whether the conventional route creates new states while the serrated route
redistributes existing ones, or the reverse — sits directly on the main question
and was not reported by the source papers.

**Secondary benefit.** The pseudobulk plan compares like-for-like states
("adenoma stem-like vs normal stem-like") and currently *assumes* a label means
the same thing in both tissues. The coupling tests that assumption per state
instead of asserting it.

**Placement.** Week 6, beside the shared-vs-route-specific decomposition. **Not
on the critical path** — the pseudobulk DE must stand without it. Tooling:
`moscot` (scanpy-native, supports unbalanced problems, maintained) over the older
`wot`. Fallback if time runs short: scVI or Harmony integration plus
nearest-neighbour matching in the latent space, or plain label transfer.

**Risk to budget for.** Couplings are sensitive to the cost metric and the
unbalancedness parameter; the result needs a sensitivity check. Leave-donor-out
over the 19 paired donors covers it and is already a planned robustness step.
