#!/usr/bin/env python3
"""Render a simple Markdown file to PDF.

Handles the subset used by this project's planning documents: ATX headings,
paragraphs, numbered and bulleted lists, and inline **bold** / `code`.
Not a general Markdown implementation.

Usage: md_to_pdf.py INPUT.md [OUTPUT.pdf]
Requires fpdf2 (see /nfs-stor/$USER/venvs/hta11-doc).
"""
import re
import sys
from pathlib import Path

from fpdf import FPDF

BODY, H1, H2, H3 = 10.5, 19, 13.5, 11.5
LEADING = 1.45


def inline(text):
    """Strip markup fpdf2's markdown mode does not understand."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text


def blocks(md):
    """Yield (kind, text) for each block, dropping blank runs."""
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            yield "blank", ""
        elif line.startswith("### "):
            yield "h3", line[4:]
        elif line.startswith("## "):
            yield "h2", line[3:]
        elif line.startswith("# "):
            yield "h1", line[2:]
        elif re.match(r"^\s*\d+[.)]\s+", line):
            yield "ol", line.strip()
        elif re.match(r"^\s*[-*]\s+", line):
            yield "ul", re.sub(r"^\s*[-*]\s+", "", line)
        else:
            yield "p", line.strip()


def render(src: Path, dest: Path):
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(22, 20, 22)
    pdf.add_page()
    pdf.set_text_color(20, 20, 20)

    width = pdf.w - pdf.l_margin - pdf.r_margin
    paragraph = []

    def flush(kind="p"):
        """Emit the buffered paragraph, joining its wrapped source lines."""
        if not paragraph:
            return
        text = inline(" ".join(paragraph))
        paragraph.clear()
        pdf.set_font("Helvetica", "", BODY)
        if kind == "ol":
            marker, _, rest = text.partition(" ")
            pdf.set_x(pdf.l_margin + 6)
            pdf.cell(7, BODY * LEADING / 2.6, marker)
            pdf.multi_cell(width - 13, BODY * LEADING / 2.6, rest,
                           markdown=True, new_x="LMARGIN", new_y="NEXT")
        elif kind == "ul":
            pdf.set_x(pdf.l_margin + 6)
            pdf.cell(4, BODY * LEADING / 2.6, "•")
            pdf.multi_cell(width - 10, BODY * LEADING / 2.6, text,
                           markdown=True, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.multi_cell(width, BODY * LEADING / 2.6, text,
                           markdown=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1.6)

    pending = "p"
    for kind, text in blocks(src.read_text()):
        if kind in ("h1", "h2", "h3"):
            flush(pending)
            size = {"h1": H1, "h2": H2, "h3": H3}[kind]
            pdf.ln(4 if kind != "h1" else 0)
            pdf.set_font("Helvetica", "B", size)
            pdf.multi_cell(width, size * 0.52, inline(text),
                           new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1.8 if kind == "h1" else 1.2)
        elif kind == "blank":
            flush(pending)
            pending = "p"
        elif kind in ("ol", "ul"):
            flush(pending)
            pending = kind
            paragraph.append(text)
        else:
            if pending in ("ol", "ul"):
                paragraph.append(text)
            else:
                pending = "p"
                paragraph.append(text)
    flush(pending)

    pdf.output(str(dest))
    return dest


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    source = Path(sys.argv[1])
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else source.with_suffix(".pdf")
    print(render(source, target))
