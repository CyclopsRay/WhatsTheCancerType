# Presentation sources

- Midterm deck (Thu 2026-10-22, 3–5 min, 13 slides): https://claude.ai/artifact/VVPjMSC6a5dnFAbnEYHG7G
  — slide sources mirrored in `midterm_deck/project/`; figures are `figures/fig*.png`
  (fig8 and fig11–14 are plain-language talk figures from `scripts/make_story_figures.py`; fig9 are the slide-2 H&E panels; fig16 the same slices coloured by route genes, from `make_he_panels.py` with a third argument).
  Third-party cover images and their licences: `midterm_deck/images/CREDITS.md`. Built to the `slide-storytelling` skill.
- Polyp Fingerprint Explorer (pick a person, linked from slide 8): https://claude.ai/artifact/Xi6uWPxrpUKZcgz9LL3YDH — built by `scripts/make_person_explorer.py DERIVED person_explorer/template.html OUT.html`.
- Project arms console: https://claude.ai/artifact/EAd4sS1nSVmPepYoRBhZpF — source `console/index.html`.
- Progress report: text `progress_report/draft_v1.md`, PDF `progress_report/progress_report.pdf`
  (A4, 5 pages + references). Figures `figures/report_fig1–5.png` are committed, so the PDF can be
  rebuilt anywhere from the repository root:

  ```bash
  pip install fpdf2 pypdf pillow matplotlib      # matplotlib only supplies the STIX fonts
  python scripts/report_to_pdf.py presentation/progress_report/draft_v1.md my_report.pdf
  ```

  Edit a copy of the Markdown for your own version; images are resolved relative to the Markdown
  file, so keep the copy in `presentation/progress_report/`. The script prints the page count.
  Redrawing the figures needs the derived data on the cluster (`scripts/make_report_figures.py`).

Both artifacts are private until shared from the page's Share menu.
