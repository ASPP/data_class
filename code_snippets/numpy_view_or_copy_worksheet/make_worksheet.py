"""Generate the 'view or copy?' fill-by-hand worksheet (HTML + PDF).

Companion handout for exercises/numpy_view_or_copy/. Students fill in the
array metadata by hand and decide, for each operation, whether the result is
a view of `x` or a copy.

Styled to match the ASPP NumPy slides: grey metadata tables, light-blue
array-layout cells, monospace code. Output is 2 A4 pages, i.e. one
double-sided sheet.

The array layouts are computed with NumPy from the actual operations, so they
cannot drift from the solution notebook. To change the exercises, edit
OPERATIONS below and re-run; adjust SPLIT_AFTER to rebalance the two pages.

Usage:  python make_worksheet.py        (requires numpy + weasyprint)
"""

from pathlib import Path

import numpy as np
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
OUT_HTML = HERE / "view_or_copy_worksheet.html"
OUT_PDF = HERE / "view_or_copy_worksheet.pdf"
OUT_HTML_SOL = HERE / "view_or_copy_worksheet_solution.html"
OUT_PDF_SOL = HERE / "view_or_copy_worksheet_solution.pdf"

x = np.arange(12).reshape(3, 4).copy()
ITEMSIZE = x.itemsize  # 8 bytes for int64

# (source code shown to students, callable producing y, optional comment,
#  explanation printed on the solution sheet only)
OPERATIONS = [
    (
        "y = x.reshape((6, 2))",
        lambda x: x.reshape((6, 2)),
        None,
        "x is contiguous and the elements are needed in the same order, so only the "
        "shape/strides bookkeeping changes: walk 2 items (16 bytes) per row, 1 item "
        "(8 bytes) per column.",
    ),
    (
        "y = x[::2, :]",
        lambda x: x[::2, :],
        None,
        "A basic slice: keep every other row by doubling the row stride to 2&times;32 = "
        "64 bytes. Regular steps are exactly what strides can express.",
    ),
    (
        "y = x[[1, 2, 0], [1, 1, 2]]",
        lambda x: x[[1, 2, 0], [1, 1, 2]],
        None,
        "Fancy indexing picks elements at byte offsets 40, 72, 16 &mdash; not a "
        "constant step, so no single stride can reach them. NumPy must gather them "
        "into a new block.",
    ),
    (
        "y = x[[0, 2], :]",
        lambda x: x[[0, 2], :],
        "get the first and third row",
        "Careful: rows 0 and 2 <i>are</i> evenly spaced, so a view would be "
        "expressible here (it is what <span class='mono'>x[::2, :]</span> returns). "
        "But this is fancy indexing, and NumPy always copies for fancy indexing "
        "&mdash; it does not inspect the index list to see whether it happens to be "
        "regular. The rule is about the <i>kind</i> of indexing, not the particular "
        "values.",
    ),
    (
        "y = x.ravel()",
        lambda x: x.ravel(),
        None,
        "x is C-contiguous, so reading the block straight through in memory order "
        "already gives the flattened array: a 1-D view with an 8-byte stride.",
    ),
    (
        "y = x.T",
        lambda x: x.T,
        None,
        "Transposing just swaps the two strides: step 8 bytes down a column and 32 "
        "bytes across a row. No data moves &mdash; the result is simply non-contiguous.",
    ),
    (
        "y = x.T.ravel()",
        lambda x: x.T.ravel(),
        None,
        "Flattening x.T needs the elements in the order 0, 4, 8, 1, 5, 9, ... i.e. "
        "byte offsets 0, 32, 64, 8, ... That jumps backwards, so it is not a constant "
        "step and no stride can produce it. A copy is unavoidable.",
    ),
]

# rows on page 1 after the example row -> keeps the two pages balanced
SPLIT_AFTER = 4

FIELDS = ["dtype", "ndim", "shape", "strides"]


def layout_html(a):
    """Render an array as a grid of light-blue cells, like the slides."""
    rows = np.atleast_2d(a)
    cells = "\n".join(
        "<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>" for row in rows
    )
    return f'<table class="layout"><tbody>{cells}</tbody></table>'


def meta_html(a=None):
    """Metadata table: filled in if `a` is given, blank otherwise."""
    if a is None:
        vals = [""] * len(FIELDS)
    else:
        vals = [str(a.dtype), str(a.ndim), str(a.shape), str(a.strides)]
    rows = "\n".join(
        f'<tr><th>{f}</th><td class="{"filled" if v else "blank"}">{v}</td></tr>'
        for f, v in zip(FIELDS, vals)
    )
    return f'<table class="meta"><tbody>{rows}</tbody></table>'


def checkbox_html(answer=None):
    """Tick boxes: view / copy. Ticks the right one when `answer` is given."""
    def box(label):
        ticked = answer == label
        mark = "&#10007;" if ticked else "&nbsp;"
        cls = " ticked" if ticked else ""
        return (
            f'<div class="cb{cls}"><span class="box">{mark}</span>'
            f'<span class="cblabel">{label}</span></div>'
        )
    return box("view") + box("copy")


def memblock_html():
    """The single memory block shared by x and all its views."""
    vals = "".join(f"<td>{v}</td>" for v in x.ravel())
    offs = "".join(f"<td>{i * ITEMSIZE}</td>" for i in range(x.size))
    return f"""<div class="memblock">
      <div class="memlabel">The one memory block behind <span class="mono">x</span>
        &mdash; {x.size} items of <span class="mono">{x.dtype}</span>,
        {ITEMSIZE} bytes each:</div>
      <table class="membuf">
        <tr class="vals">{vals}</tr>
        <tr class="offs">{offs}</tr>
      </table>
      <div class="memnote">second row = byte offset of each item from the start of the block</div>
    </div>"""


def row_html(code, layout, meta, checks, comment=None, example=False, newpage=False,
             why=None):
    note = f'<div class="comment"># {comment}</div>' if comment else ""
    tag = '<div class="egtag">worked example</div>' if example else ""
    classes = (
        (["example"] if example else [])
        + (["newpage"] if newpage else [])
        + (["hasexplain"] if why else [])
    )
    cls = f' class="{" ".join(classes)}"' if classes else ""
    explain = (
        f'    <tr class="whyrow"><td colspan="4" class="why"><b>Why:</b> {why}</td></tr>'
        if why else ""
    )
    return f"""    <tr{cls}>
      <td class="c-op">{tag}<div class="code">{code}</div>{note}</td>
      <td class="c-layout">{layout}</td>
      <td class="c-meta">{meta}</td>
      <td class="c-check">{checks}</td>
    </tr>
{explain}"""


def build_rows(solution):
    """Rows for the worksheet (solution=False) or the answer key (solution=True)."""
    out = [
        row_html(
            "x",
            layout_html(x),
            meta_html(x),
            '<div class="nacheck">&mdash;</div>',
            comment="the original array",
            example=True,
        )
    ]
    for i, (code, fn, comment, why) in enumerate(OPERATIONS):
        y = fn(x)
        is_view = y.base is x
        out.append(
            row_html(
                code,
                layout_html(y),
                meta_html(y if solution else None),
                checkbox_html("view" if is_view else "copy") if solution
                else checkbox_html(),
                comment,
                newpage=(i == SPLIT_AFTER) if not solution else False,
                why=why if solution else None,
            )
        )
    return out

CSS = """
@page {
  size: A4 portrait;
  margin: 11mm 10mm 11mm 10mm;
  @bottom-left { content: "Aug 2026, CC BY-SA 4.0"; font-family: Helvetica, Arial, sans-serif;
                 font-size: 7pt; color: #9a9a9a; }
  @bottom-right { content: counter(page); font-family: Helvetica, Arial, sans-serif;
                  font-size: 8pt; color: #9a9a9a; }
}
body { font-family: Helvetica, Arial, sans-serif; font-size: 9pt; color: #000; margin: 0; }

h1 { font-size: 14pt; margin: 0 0 2mm 0; }
.intro { font-size: 8.5pt; color: #222; margin: 0 0 3.5mm 0; }
.intro ol { margin: 1.2mm 0 0 0; padding-left: 5.5mm; }
.intro li { margin-bottom: 1.2mm; }
code, .mono { font-family: "DejaVu Sans Mono", Courier, monospace; }

/* shared memory block, sits in the repeating table header */
.memblock { margin: 0 0 3mm 0; }
.memlabel { font-size: 8pt; color: #222; margin-bottom: 1.2mm; font-weight: normal; }
table.membuf { border-collapse: collapse; }
table.membuf td {
  font-family: "DejaVu Sans Mono", Courier, monospace; font-size: 7.5pt;
  text-align: center; width: 11mm; padding: 0.7mm 0;
}
table.membuf tr.vals td {
  font-weight: bold; color: #1f3864; background: #dce6f5; border: 0.5pt solid #b4c6e7;
}
table.membuf tr.offs td { font-size: 6.5pt; color: #8a8a8a; border: none; padding-top: 0.5mm; }
.memnote { font-size: 6.5pt; color: #9a9a9a; margin-top: 0.4mm; }

table.sheet { width: 100%; border-collapse: collapse; }
table.sheet > thead { display: table-header-group; }
th.memcell { text-align: left; font-weight: normal; padding: 0; }
tr.colheads th {
  font-size: 9.5pt; text-align: left; padding: 0 0 1.5mm 0; vertical-align: bottom;
  border-bottom: 0.6pt solid #cfcfcf;
}
th.h-op     { color: #000; }
th.h-layout { color: #8faadc; }
th.h-meta   { color: #8a8a8a; }
th.h-check  { color: #000; }

table.sheet > tbody > tr { page-break-inside: avoid; }
table.sheet > tbody > tr.newpage { page-break-before: always; }
table.sheet > tbody > tr > td {
  vertical-align: top; padding: 3.4mm 2mm 3.4mm 0;
  border-bottom: 0.4pt dotted #d0d0d0;
}
td.c-op     { width: 52mm; white-space: nowrap; }
td.c-layout { width: 74mm; }
td.c-meta   { width: 46mm; }
td.c-check  { width: 20mm; white-space: nowrap; }

tr.example > td { background: #fbfbfb; }
.egtag { font-size: 6.5pt; text-transform: uppercase; letter-spacing: 0.4pt;
         color: #b0b0b0; margin-bottom: 0.8mm; }
.code { font-family: "DejaVu Sans Mono", Courier, monospace; font-size: 9pt; }
.comment { font-family: "DejaVu Sans Mono", Courier, monospace; font-size: 7.5pt;
           color: #8a8a8a; margin-top: 0.8mm; }
.nacheck { color: #c0c0c0; font-size: 9pt; }

/* light-blue array layout, as on the slides */
table.layout { border-collapse: collapse; }
table.layout td {
  font-family: "DejaVu Sans Mono", Courier, monospace; font-size: 7.5pt; font-weight: bold;
  color: #1f3864; background: #dce6f5; border: 0.5pt solid #b4c6e7;
  text-align: center; min-width: 5.2mm; padding: 0.7mm 0.8mm;
}

/* grey metadata table, as on the slides */
table.meta { border-collapse: collapse; width: 44mm; }
table.meta th {
  font-family: "DejaVu Sans Mono", Courier, monospace; font-size: 7.5pt; font-weight: bold;
  text-align: left; background: #e8e8e8; border: 0.5pt solid #7f7f7f;
  padding: 0.7mm 1.2mm; width: 15mm;
}
table.meta td {
  font-family: "DejaVu Sans Mono", Courier, monospace; font-size: 7.5pt;
  border: 0.5pt solid #7f7f7f; padding: 0.7mm 1.2mm; background: #fff;
}
table.meta td.blank { height: 6.4mm; }

.cb { margin-bottom: 1.8mm; }
.box { display: inline-block; width: 3.6mm; height: 3.6mm; border: 0.7pt solid #555;
       text-align: center; font-size: 7.5pt; line-height: 3.6mm; margin-right: 1.6mm;
       vertical-align: middle; }
.cblabel { font-family: "DejaVu Sans Mono", Courier, monospace; font-size: 8pt;
           vertical-align: middle; }

/* --- solution sheet only --- */
.cb.ticked .box { border-color: #c00000; color: #c00000; font-weight: bold; }
.cb.ticked .cblabel { color: #c00000; font-weight: bold; }
table.meta td.filled { color: #c00000; }
tr.whyrow > td.why {
  font-size: 7.5pt; color: #333; line-height: 1.35;
  padding: 0 20mm 3.2mm 0; border-bottom: 0.4pt dotted #d0d0d0;
  vertical-align: top;
}
tr.whyrow > td.why b { color: #000; }
.answer { color: #c00000; font-weight: bold; }
.keyrule { margin-top: 1.6mm; padding: 1.4mm 1.8mm; background: #f4f4f4;
           border-left: 1.2pt solid #b0b0b0; font-size: 8pt; }
/* keep an operation row glued to its explanation */
table.sheet > tbody > tr.hasexplain > td { border-bottom: none; padding-bottom: 1.4mm; }
table.sheet > tbody > tr.hasexplain { page-break-after: avoid; }
"""

WORKSHEET_INTRO = """
  Start from <span class="mono">x</span>, shown in the first row. For each operation
  <span class="mono">y = ...</span> below:
  <ol>
    <li><b>Try to fill in the metadata (<span class="mono">dtype</span>,
    <span class="mono">ndim</span>,
    <span class="mono">shape</span>, <span class="mono">strides</span>) that
    would be required to return <span class="mono">y</span> as a view of the same
    memory block as <span class="mono">x</span>.</b> Can it be done?</li>
    <li><b>Now decide: is <span class="mono">y</span> a view of <span class="mono">x</span>,
        or a copy?</b> Base your answer on the outcome of step 1 and what we learned in
        the slides, then tick the box.</li>
  </ol>
"""

SOLUTION_INTRO = """
  Answers in <span class="answer">red</span>, with a short explanation under each row.
  All metadata assumes <span class="mono">int64</span>, i.e. 8 bytes per item, and
  strides are in <b>bytes</b>.
  <div class="keyrule"><b>Rule of thumb:</b> NumPy can return a view whenever the
  elements you asked for sit at a <i>constant step</i> (per axis) in the existing
  memory block &mdash; that is what <span class="mono">strides</span> can express.
  Basic slicing always yields such a pattern, so it gives views; fancy indexing
  (integer or boolean arrays) always copies, even when the indices happen to be
  regularly spaced.</div>
"""


def build_doc(solution):
    title = "Is it a view or a copy? &mdash; solutions" if solution \
        else "Is it a view or a copy?"
    intro = SOLUTION_INTRO if solution else WORKSHEET_INTRO
    rows = build_rows(solution)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>{CSS}</style></head>
<body>
<h1>{title}</h1>
<div class="intro">{intro}</div>

<table class="sheet">
  <thead>
    <tr><th class="memcell" colspan="4">{memblock_html()}</th></tr>
    <tr class="colheads">
      <th class="h-op">NumPy operation</th>
      <th class="h-layout">Array layout of <span class="mono">y</span></th>
      <th class="h-meta">NumPy array metadata</th>
      <th class="h-check">View or copy?</th>
    </tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
</table>
</body></html>
"""


def write(solution, out_html, out_pdf):
    doc = build_doc(solution)
    out_html.write_text(doc)
    HTML(string=doc).write_pdf(out_pdf)
    print("wrote", out_html.name, "and", out_pdf.name, "in", HERE)


write(False, OUT_HTML, OUT_PDF)
write(True, OUT_HTML_SOL, OUT_PDF_SOL)
