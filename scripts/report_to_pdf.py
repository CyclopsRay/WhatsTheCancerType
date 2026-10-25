#!/usr/bin/env python3
"""Render the progress report Markdown, figures included, to PDF.

Handles what draft_v1.md uses: headings, paragraphs, numbered lists, images
(![alt](path), resolved against the Markdown file), inline **bold**, *italic*
and `code`, and HTML comments (dropped). Captions (paragraphs starting with
**Figure) and the reference list are set smaller. A figure that almost fits the rest of a page is
shrunk (to no less than 72 %) rather than pushed to the next page. Prints the page count.

Usage: report_to_pdf.py INPUT.md [OUTPUT.pdf]
Requires fpdf2, pypdf and pillow (on this cluster: /nfs-stor/$USER/venvs/hta11-doc). The STIX
fonts come from $REPORT_FONT_DIR, else matplotlib's bundled copy, so elsewhere:
    pip install fpdf2 pypdf pillow matplotlib
"""
import os
import re
import sys
from pathlib import Path

from fpdf import FPDF
from pypdf import PdfReader

CLUSTER_FONTS = "/nfs-stor/yuqi.lei/envs/promotervi/lib/python3.10/site-packages/matplotlib/mpl-data/fonts/ttf"
BODY, SMALL, H1, H2 = 11, 9.5, 15, 12.5
LEADING = 1.3


def inline(text):
    """Translate Markdown inline marks to fpdf2's markdown mode (** bold, __ italic)."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"(?<![*\w])\*(?!\*)([^*]+?)\*(?![*\w])", r"__\1__", text)


def blocks(md):
    """Yield (kind, text) blocks; list items keep their indented continuation lines."""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    kind, buf = None, []
    for raw in md.splitlines() + [""]:
        line = raw.rstrip()
        image = re.match(r"^!\[[^\]]*\]\(([^)]+)\)$", line.strip())
        if not line.strip() or image or line.startswith("#") or re.match(r"^\d+\.\s", line):
            if buf:
                yield kind, " ".join(buf)
            kind, buf = None, []
        if image:
            yield "img", image.group(1)
        elif line.startswith("## "):
            yield "h2", line[3:]
        elif line.startswith("# "):
            yield "h1", line[2:]
        elif re.match(r"^\d+\.\s", line):
            kind, buf = "ol", [line.strip()]
        elif line.strip():
            kind = kind or "p"
            buf.append(line.strip())


def font_dir():
    """First directory holding STIXGeneral.ttf: $REPORT_FONT_DIR, matplotlib's, this cluster's."""
    candidates = [os.environ.get("REPORT_FONT_DIR")]
    try:
        import matplotlib
        candidates.append(str(Path(matplotlib.get_data_path()) / "fonts" / "ttf"))
    except ImportError:
        pass
    candidates.append(CLUSTER_FONTS)
    for c in candidates:
        if c and (Path(c) / "STIXGeneral.ttf").exists():
            return Path(c)
    sys.exit("STIX fonts not found: pip install matplotlib, or set REPORT_FONT_DIR")


def render(src, dest):
    pdf = FPDF(format="A4", unit="mm")
    fonts = font_dir()
    for style, name in [("", "STIXGeneral"), ("B", "STIXGeneralBol"), ("I", "STIXGeneralItalic"),
                        ("BI", "STIXGeneralBolIta")]:
        pdf.add_font("Serif", style, str(fonts / f"{name}.ttf"))
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(18, 16, 18)
    pdf.add_page()
    pdf.set_text_color(20, 20, 20)
    width = pdf.w - pdf.l_margin - pdf.r_margin
    in_refs, previous = False, None

    def text(body, size, indent=0):
        pdf.set_font("Serif", "", size)
        pdf.set_x(pdf.l_margin + indent)
        pdf.multi_cell(width - indent, size * LEADING / 2.83, inline(body), markdown=True,
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(size * 0.18)

    for kind, body in blocks(src.read_text()):
        if kind == "h1":
            pdf.set_font("Serif", "B", H1)
            pdf.multi_cell(width, H1 * 0.5, body, align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        elif kind == "h2":
            in_refs = body.strip() == "References"
            pdf.ln(2.5)
            pdf.set_font("Serif", "B", H2)
            pdf.multi_cell(width, H2 * 0.5, body, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif kind == "img":
            path = (src.parent / body).resolve()
            w_px, h_px = PdfImageSize.of(path)
            w = width
            room = pdf.h - pdf.b_margin - pdf.get_y() - 24
            if w * h_px / w_px > room:
                if room >= 0.72 * w * h_px / w_px:
                    w = room * w_px / h_px
                else:
                    pdf.add_page()
            pdf.image(str(path), x=pdf.l_margin + (width - w) / 2, w=w)
            pdf.ln(1.5)
        elif kind == "ol":
            number, _, rest = body.partition(" ")
            size = SMALL if in_refs else BODY
            pdf.set_font("Serif", "", size)
            if pdf.get_y() + 2 * size * LEADING / 2.83 > pdf.h - pdf.b_margin:
                pdf.add_page()
            y = pdf.get_y()
            pdf.cell(7, size * LEADING / 2.83, number)
            pdf.set_y(y)
            text(rest, size, indent=7)
        elif kind == "p":
            caption = body.startswith("**Figure")
            if previous == "h1":
                pdf.set_font("Serif", "", BODY)
                pdf.multi_cell(width, BODY * 0.55, body, align="C", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)
            else:
                text(body, SMALL if caption or in_refs else BODY)
                if caption:
                    pdf.ln(2)
        previous = kind
    pdf.output(str(dest))
    return len(PdfReader(str(dest)).pages)


class PdfImageSize:
    @staticmethod
    def of(path):
        from PIL import Image
        with Image.open(path) as im:
            return im.size


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    source = Path(sys.argv[1])
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else source.with_suffix(".pdf")
    pages = render(source, target)
    print(f"{target}  ({pages} pages)")
