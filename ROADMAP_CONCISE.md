# Roadmap


## Team 

Yuqi Lei and Muhammed Bah. 
Team name: WhatsTheCancerType

## Topic

Colorectal polyps could be conventional adenoma and serrated lesions, and while some become cancer, most stay the form. We want to know 2 things:
1. what the epithelium is actually doing differently once a polyp has formed, and how much of that change is common to both routes.
2. What are the marker genes that decides if a normal tissue turns into a polyp, and which kind of polyp?

## Data

HTAN Vanderbilt, atlas HTA11. We are only using the level 3 and 4 data that doesn't require a dbGaP access (for MxIF it is level 2). The core is the single-cell RNA release: 121 specidmens from
55 donors, covering normal mucosa, tubular and tubulovillous adenomas, serrated
lesions and hyperplastic polyps. We will train and test on 49 donors from this set, that are welly paired:
There are 28 donors that have both a normal sample and a conventional polyp, and 21 both a normal sample and a serrated lesion, so we can compare a polyp against the same person's healthy tissue instead of against other people. For tissue context we use the MxIF images, working from the authors' already-segmented cell tables on OSF. The open exome calls are a possible extra if they turn out to be usable (currently unavailable due to some "governance issue"). We don't use the Raw sequencing since that needs a dbGaP request.

## Question

Which epithelial genes separate a polyp from the same donor's normal
mucosa, how much of those genes are shared between the conventional and serrated
routes rather than specific to one, and are they consistant across different donors?

## Analyses

First we label epithelial cell states, so we can tell a change in cell mixture
apart from a change inside a cell type. Then we measure, donor by donor, how the
state mixture shifts from normal to polyp. Then we pseudobulk each specimen by
state and test expression against that donor's own normal (probably needs to use Optimal Transport to find the coupling), fitting the two routes separately, and read the results through pathway enrichment. Finally we compare the two route signatures against each other and count how many donors each effect actually holds in. The MxIF tables tell us where the resulting programs sit in the tissue, and the 10X Visium can be used to verify if the marker genes actually resides within the abnormal (adenoma, or tumor) regions.

## Steps

0. Literature review. Check if there are existed methods in this study, and what results they generated. Our research should start upon theirs.
1. Audit the cell metadata first and confirm the donor pairing really exists in the
files, since so far we have only checked the portal's records, and we are not sure if all data are accessible. 
2. Quality check, annotation, and the paired abundance and expression tests, then the comparison between routes
3. Marker gene selection and validation. We will build modal (end to end, statistic or mix) to select genes, and verify them by the 10X Visium and MxIF modalities, and check the robustness. 

