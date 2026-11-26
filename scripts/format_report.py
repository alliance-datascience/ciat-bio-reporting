#!/usr/bin/env python3
"""Format a document (.docx or .md) with a Word template (.dotx or .docx).

Commands:
  inspect <template>                Styles, cover, table of contents and back pages it detects.
  structure <input>                 How the input document will be read, block by block.
  apply --template --input --output [options]
  check <result.docx>               Leftover sample text, foreign styles, counts.

Requires python-docx >= 1.0. Built for the CGIAR Report-<Program> templates, but accepts
any template with --start-text, --end-text and --replace.
"""
import argparse
import io
import os
import re
import sys
import tempfile
import zipfile

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.section import Section
    from docx.shared import Emu
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    from docx.text.run import Run
except ImportError:
    sys.exit("python-docx is missing. Install it with: python3 -m pip install --user python-docx")

COVER = {"document title": "title", "date": "date", "document description": "description"}
BACK_PAGE_LABELS = {"back page", "subtitle", "with programs", "extra text if needed"}
LOREM = re.compile(r"\b(lorem|ipsum|olorrorem|quiaspis|volorisquam|porerum|omnimollabo|"
                   r"temperibus|rehendit|perferiae|moluptam)\b", re.I)

# Role -> candidate style names, normalized (no leading "_", no parentheses).
ROLES = {
    "title": ["title"],
    "subtitle": ["subtitle"],
    "h1": ["heading 1"],
    "h2": ["heading 2"],
    "h3": ["body heading", "heading 3"],
    "intro": ["body intro"],
    "body": ["body text", "normal"],
    "bullet1": ["body bullet 1", "list bullet"],
    "bullet2": ["body bullet 2", "list bullet 2"],
    "num1": ["body bullet numbered 1", "list number"],
    "num2": ["body bullet numbered 2", "list number 2"],
    "quote": ["quote"],
    "caption": ["caption source footnote", "caption"],
    "source": ["source"],
}
HEADING_ROLES = ("title", "subtitle", "h1", "h2", "h3")
# Front and back matter that stays unnumbered (English, Spanish, French, Portuguese).
UNNUMBERED = re.compile(
    r"^(executive summary|summary|abstract|acknowledg|references|bibliograph|annex|appendix|"
    r"acronyms|abbreviations|contents|foreword|preface|"
    r"resumen|agradecimiento|referencias|bibliograf|anexo|apéndice|siglas|acrónimos|contenido|"
    r"índice|prólogo|prefacio|"
    r"résumé|remerciements|références|annexe|sigles|sommaire|avant-propos|préface|"
    r"resumo|agradecimentos|referências|apêndice|sumário|prefácio)", re.I)
MANUAL_NUMBER = re.compile(r"^\s*((\d+\.)*\d+\.?|[IVXLC]+\.|[A-Z]\.)\s+")


# ---------------------------------------------------------------- XML helpers

def open_doc(path):
    """Open .docx or .dotx (python-docx rejects .dotx: patch the content type in a copy)."""
    low = path.lower()
    if low.endswith(".dotm") or low.endswith(".docm"):
        sys.exit("Macro-enabled templates (.dotm/.docm) are not supported. Save it as .dotx or .docx.")
    if low.endswith(".dotx"):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == "[Content_Types].xml":
                    data = data.replace(b"wordprocessingml.template.main+xml",
                                        b"wordprocessingml.document.main+xml")
                zout.writestr(item, data)
        return Document(tmp.name)
    return Document(path)


def text_of(el):
    """All visible text of an element, text boxes included."""
    return "".join(el.xpath(".//w:t/text()"))


def norm(name):
    n = (name or "").lower().strip().lstrip("_").strip()
    n = re.sub(r"\(.*?\)", "", n)
    return re.sub(r"\s+", " ", n).strip()


def has_sectpr(el):
    return el.tag == qn("w:p") and bool(el.xpath("./w:pPr/w:sectPr"))


def has_page_break(el):
    return el.tag == qn("w:p") and bool(
        el.xpath('.//w:br[@w:type="page"]') or el.xpath("./w:pPr/w:pageBreakBefore"))


def is_separator(el):
    return (el.tag == qn("w:p") and not text_of(el).strip() and not el.xpath(".//w:drawing")
            and (has_sectpr(el) or has_page_break(el)))


def body_elements(doc):
    return [e for e in doc.element.body.iterchildren() if e.tag != qn("w:sectPr")]


def clear_paragraph(p_el):
    for t in p_el.xpath(".//w:t"):
        t.text = ""


def set_text(p_el, new):
    ts = p_el.xpath(".//w:t")
    if not ts:
        return False
    ts[0].text = new
    ts[0].set(qn("xml:space"), "preserve")
    for t in ts[1:]:
        t.text = ""
    return True


def parse_pairs(items):
    out = {}
    for pair in items or []:
        k, _, v = pair.rpartition("=")
        out[k.strip()] = v.strip()
    return out


# ---------------------------------------------------------------- template

def resolve_styles(doc):
    """Role -> style name. Prefers brand styles starting with "_"."""
    brand, other = {}, {}
    for st in doc.styles:
        try:
            if st.type != 1:  # 1 = paragraph
                continue
        except Exception:
            continue
        target = brand if (st.name or "").strip().startswith("_") else other
        target.setdefault(norm(st.name), st.name)
    res = {}
    for role, cands in ROLES.items():
        res[role] = None
        for source in (brand, other):
            for c in cands:
                if c in source:
                    res[role] = source[c]
                    break
            if res[role]:
                break
    return res


def table_style(doc, els, start, end):
    for el in els[start:end]:
        if el.tag == qn("w:tbl"):
            v = el.xpath("./w:tblPr/w:tblStyle/@w:val")
            if v:
                for st in doc.styles:
                    if st.style_id == v[0]:
                        return st.name
    for st in doc.styles:
        try:
            if st.type == 3 and st.name not in ("Normal Table", "Table Normal"):
                if st.name.startswith("_") or "cgiar" in st.name.lower():
                    return st.name
        except Exception:
            pass
    for st in doc.styles:
        try:
            if st.type == 3 and st.name == "Table Grid":
                return st.name
        except Exception:
            pass
    return None


def toc_end(els):
    """Index of the last element of the table of contents (TOC), or None."""
    for i, el in enumerate(els):
        if el.tag == qn("w:sdt") and el.xpath('.//w:docPartGallery[@w:val="Table of Contents"]'):
            return i
    depth, inside = 0, False
    for i, el in enumerate(els):
        for node in el.iter(qn("w:fldChar"), qn("w:instrText")):
            if node.tag == qn("w:instrText") and re.match(r"\s*TOC\b", node.text or ""):
                inside = True
            elif node.tag == qn("w:fldChar"):
                kind = node.get(qn("w:fldCharType"))
                if kind == "begin":
                    depth += 1
                elif kind == "end":
                    depth -= 1
                    if inside and depth == 0:
                        return i
    return None


def clear_toc(els):
    """Erase the result text of the TOC field (the template's sample entries)."""
    depth, toc_depth, in_result = 0, None, False
    for el in els:
        for p in el.iter(qn("w:p")):
            style = p.xpath("./w:pPr/w:pStyle/@w:val")
            if style and re.match(r"(?i)^toc\d", style[0]):
                clear_paragraph(p)
        for node in el.iter(qn("w:fldChar"), qn("w:instrText"), qn("w:t")):
            if node.tag == qn("w:fldChar"):
                kind = node.get(qn("w:fldCharType"))
                if kind == "begin":
                    depth += 1
                elif kind == "separate" and toc_depth == depth:
                    in_result = True
                elif kind == "end":
                    if toc_depth == depth:
                        toc_depth, in_result = None, False
                    depth -= 1
            elif node.tag == qn("w:instrText"):
                if re.match(r"\s*TOC\b", node.text or ""):
                    toc_depth = depth
            elif in_result:
                node.text = ""


def detect(doc, start_text=None, end_text=None):
    els = body_elements(doc)
    txt = [text_of(e) for e in els]
    info = {"els": els, "cover": [], "toc": None, "back_pages": []}

    for i in range(min(40, len(els))):
        for p in els[i].iter(qn("w:p")):
            if text_of(p).strip().lower() in COVER:
                info["cover"].append((i, text_of(p).strip()))

    if start_text:
        cand = [i for i, t in enumerate(txt) if start_text.lower() in t.lower()]
        if not cand:
            sys.exit("--start-text not found in the template: %r" % start_text)
        start = cand[0]
    else:
        info["toc"] = toc_end(els)
        if info["toc"] is not None:
            start = info["toc"] + 1
        elif info["cover"]:
            start = max(i for i, _ in info["cover"]) + 1
        else:
            start = 0
        while start < len(els) and is_separator(els[start]):
            start += 1

    if end_text:
        cand = [i for i in range(start, len(els)) if end_text.lower() in txt[i].lower()]
        if not cand:
            sys.exit("--end-text not found in the template: %r" % end_text)
        marks = cand[:1]
    else:
        marks = [i for i in range(start, len(els)) if re.search(r"\bback page\b", txt[i], re.I)]

    # Each back page starts right after the last separator before its marker.
    blocks, frm = [], start
    for m in marks:
        seps = [j for j in range(frm, m) if is_separator(els[j])]
        blocks.append(seps[-1] + 1 if seps else m)
        frm = m + 1
    end = blocks[0] if blocks else len(els)
    for k, b in enumerate(blocks):
        upto = blocks[k + 1] if k + 1 < len(blocks) else len(els)
        programs = any("with programs" in txt[j].lower() for j in range(b, upto))
        info["back_pages"].append({"from": b, "to": upto, "programs": programs})
    info["start"], info["end"] = start, end
    return info


# ---------------------------------------------------------------- reading the input

def list_format(src, p):
    if not p._p.xpath("./w:pPr/w:numPr"):
        return None
    ilvl = p._p.xpath("./w:pPr/w:numPr/w:ilvl/@w:val")
    numid = p._p.xpath("./w:pPr/w:numPr/w:numId/@w:val")
    level = int(ilvl[0]) if ilvl else 0
    fmt = "bullet"
    try:
        numbering = src.part.numbering_part.element
        abs_id = numbering.xpath('./w:num[@w:numId="%s"]/w:abstractNumId/@w:val' % numid[0])
        f = numbering.xpath('./w:abstractNum[@w:abstractNumId="%s"]/w:lvl[@w:ilvl="%d"]/w:numFmt/@w:val'
                            % (abs_id[0], level))
        fmt = f[0] if f else "bullet"
    except Exception:
        pass
    return ("bullet" if fmt == "bullet" else "num"), level


def paragraph_role(src, p, mapping):
    name = p.style.name if p.style is not None else ""
    if name in mapping:
        return mapping[name]
    n = norm(name)
    if n.startswith("toc"):
        return "skip"
    if n == "title":
        return "title"
    if n == "subtitle":
        return "subtitle"
    m = re.match(r"heading (\d)", n)
    if m:
        return {1: "h1", 2: "h2"}.get(int(m.group(1)), "h3")
    if "quote" in n:
        return "quote"
    if "caption" in n:
        return "caption"
    lst = list_format(src, p)
    if "list bullet" in n or (lst and lst[0] == "bullet"):
        level = lst[1] if lst else (1 if n.endswith("2") else 0)
        return "bullet2" if level > 0 else "bullet1"
    if "list number" in n or (lst and lst[0] == "num"):
        level = lst[1] if lst else (1 if n.endswith("2") else 0)
        return "num2" if level > 0 else "num1"
    return "body"


def run_dict(run, link=None):
    cstyle = run.style.name if run.style is not None else ""
    return {
        "text": run.text,
        "b": bool(run.bold) or cstyle in ("Strong", "Strong Emphasis"),
        "i": bool(run.italic) or cstyle == "Emphasis",
        "u": bool(run.underline) and not link,
        "sup": bool(run.font.superscript),
        "sub": bool(run.font.subscript),
        "code": False,
        "link": link,
    }


def plain_run(text):
    return {"text": text, "b": False, "i": False, "u": False, "sup": False, "sub": False,
            "code": False, "link": None}


def run_images(src, run, stats):
    out = []
    for rid in run._r.xpath(".//a:blip/@r:embed"):
        try:
            blob = src.part.related_parts[rid].blob
            cx = run._r.xpath(".//wp:extent/@cx")
            out.append({"t": "img", "blob": blob, "cx": int(cx[0]) if cx else None})
        except Exception:
            stats["lost_images"] += 1
    return out


def paragraph_blocks(src, p, mapping, stats):
    role = paragraph_role(src, p, mapping)
    if role == "skip":
        return []
    stats["footnotes"] += len(p._p.xpath(".//w:footnoteReference"))
    stats["text_boxes"] += len(p._p.xpath(".//w:txbxContent"))
    runs, imgs = [], []
    for item in p.iter_inner_content():
        if isinstance(item, Run):
            imgs += run_images(src, item, stats)
            if item.text:
                runs.append(run_dict(item))
        else:  # Hyperlink
            url = item.url if getattr(item, "address", "") else None
            for r in item.runs:
                imgs += run_images(src, r, stats)
                if r.text:
                    runs.append(run_dict(r, link=url))
    out = []
    if "".join(r["text"] for r in runs).strip():
        out.append({"t": "par", "role": role, "runs": runs})
    return out + imgs


def table_block(src, tbl):
    rows, grid = [], []
    for row in tbl.rows:
        cells, ids = [], []
        for cell in row.cells:
            ids.append(cell._tc)  # the element itself; id() of lxml proxies gets reused
            parts = []
            for k, p in enumerate(cell.paragraphs):
                rs = [run_dict(x) for x in p.runs if x.text]
                if k and rs:
                    rs[0] = dict(rs[0], text="\n" + rs[0]["text"])
                parts += rs
            cells.append(parts)
        rows.append(cells)
        grid.append(ids)
    return {"t": "table", "rows": rows, "grid": grid}


def read_docx(path, mapping, stats):
    src = Document(path)
    blocks = []

    def walk(container):
        for el in container.iterchildren():
            if el.tag == qn("w:p"):
                blocks.extend(paragraph_blocks(src, Paragraph(el, src), mapping, stats))
            elif el.tag == qn("w:tbl"):
                blocks.append(table_block(src, Table(el, src)))
            elif el.tag == qn("w:sdt"):
                if el.xpath('.//w:docPartGallery[@w:val="Table of Contents"]'):
                    continue
                c = el.find(qn("w:sdtContent"))
                if c is not None:
                    walk(c)

    walk(src.element.body)
    return blocks


INLINE = re.compile(r"(\*\*.+?\*\*|__.+?__|\*.+?\*|_.+?_|`.+?`|\[[^\]]+\]\([^)]+\))")


def md_runs(md):
    runs = []
    for part in INLINE.split(md):
        if not part:
            continue
        r = plain_run(part)
        if (part.startswith("**") and part.endswith("**")) or (part.startswith("__") and part.endswith("__")):
            r["text"], r["b"] = part[2:-2], True
        elif len(part) > 1 and part[0] == part[-1] and part[0] in "*_":
            r["text"], r["i"] = part[1:-1], True
        elif part.startswith("`"):
            r["text"], r["code"] = part[1:-1], True
        elif part.startswith("["):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", part)
            r["text"], r["link"] = m.group(1), m.group(2)
        runs.append(r)
    return runs


def read_md(path, stats):
    base = os.path.dirname(os.path.abspath(path))
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    h1s = [l for l in lines if re.match(r"^#\s", l)]
    first = next((l for l in lines if l.strip()), "")
    h1_is_title = len(h1s) == 1 and re.match(r"^#\s", first)
    table_sep = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")

    blocks, para, i = [], [], 0

    def flush():
        if para:
            blocks.append({"t": "par", "role": "body", "runs": md_runs(" ".join(para))})
            del para[:]

    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if s.startswith("```"):
            flush()
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                r = plain_run(lines[i])
                r["code"] = True
                blocks.append({"t": "par", "role": "body", "runs": [r]})
                i += 1
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", l)
        if m:
            flush()
            n = len(m.group(1))
            if h1_is_title:
                role = "title" if n == 1 else {2: "h1", 3: "h2"}.get(n, "h3")
            else:
                role = {1: "h1", 2: "h2"}.get(n, "h3")
            blocks.append({"t": "par", "role": role, "runs": md_runs(m.group(2))})
        elif s.startswith("|") and i + 1 < len(lines) and table_sep.match(lines[i + 1]) and "-" in lines[i + 1]:
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not table_sep.match(lines[i]):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    rows.append([md_runs(c) for c in cells])
                i += 1
            ncol = max(len(r) for r in rows)
            rows = [r + [[] for _ in range(ncol - len(r))] for r in rows]
            grid = [[(r, c) for c in range(ncol)] for r in range(len(rows))]
            blocks.append({"t": "table", "rows": rows, "grid": grid})
            continue
        elif re.match(r"^!\[[^\]]*\]\([^)]+\)\s*$", s):
            flush()
            m = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)", s)
            img = os.path.join(base, m.group(2))
            if os.path.exists(img):
                with open(img, "rb") as f:
                    blocks.append({"t": "img", "blob": f.read(), "cx": None})
                if m.group(1).strip():
                    blocks.append({"t": "par", "role": "caption", "runs": md_runs(m.group(1))})
            else:
                stats["lost_images"] += 1
        elif re.match(r"^\s*[-*+]\s+", l):
            flush()
            indent = len(l) - len(l.lstrip())
            blocks.append({"t": "par", "role": "bullet2" if indent >= 2 else "bullet1",
                           "runs": md_runs(re.sub(r"^\s*[-*+]\s+", "", l))})
        elif re.match(r"^\s*\d+[.)]\s+", l):
            flush()
            indent = len(l) - len(l.lstrip())
            blocks.append({"t": "par", "role": "num2" if indent >= 2 else "num1",
                           "runs": md_runs(re.sub(r"^\s*\d+[.)]\s+", "", l))})
        elif s.startswith(">"):
            flush()
            blocks.append({"t": "par", "role": "quote", "runs": md_runs(s.lstrip("> "))})
        elif not s or re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            flush()
        else:
            para.append(s)
        i += 1
    flush()
    return blocks


def read_input(path, mapping, stats):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return read_docx(path, mapping, stats)
    if ext in (".md", ".markdown", ".txt"):
        return read_md(path, stats)
    sys.exit("Unsupported input format: %s. Convert it to .docx first (see references/formatting.md)." % ext)


def new_stats():
    return {"lost_images": 0, "footnotes": 0, "text_boxes": 0, "unnumbered": [], "by_role": {},
            "tables": 0, "images": 0, "warnings": [], "roles_without_style": []}


# ---------------------------------------------------------------- numbering

def number_headings(blocks, mode, stats):
    """auto: 1., 1.1 on level 1 and 2 headings (removes manual numbering).
    none: removes manual numbering. original: leaves everything as is.
    Summary, references, annexes and similar stay unnumbered, and so do their subheadings."""
    if mode == "original":
        return
    c1 = c2 = 0
    numbered = False
    for b in blocks:
        if b["t"] != "par" or b["role"] not in ("h1", "h2", "h3") or not b["runs"]:
            continue
        first = b["runs"][0]
        first["text"] = MANUAL_NUMBER.sub("", first["text"], count=1)
        if mode != "auto" or b["role"] == "h3":
            continue  # level 3 (_Body Heading) stays unnumbered
        clean = "".join(r["text"] for r in b["runs"]).strip()
        if b["role"] == "h1":
            if UNNUMBERED.match(clean):
                numbered = False
                stats["unnumbered"].append(clean[:50])
                continue
            c1, c2, numbered = c1 + 1, 0, True
            label = "%d. " % c1
        else:
            if not numbered:
                continue
            c2 += 1
            label = "%d.%d " % (c1, c2)
        first["text"] = label + first["text"]


# ---------------------------------------------------------------- writing

def add_link(p, r, char_styles):
    r_id = p.part.relate_to(r["link"], RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    if "Hyperlink" in char_styles:
        rs = OxmlElement("w:rStyle")
        rs.set(qn("w:val"), char_styles["Hyperlink"])
        rpr.append(rs)
    else:
        col = OxmlElement("w:color")
        col.set(qn("w:val"), "0563C1")
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rpr.extend([col, u])
    for flag, tag in (("b", "w:b"), ("i", "w:i")):
        if r[flag]:
            rpr.append(OxmlElement(tag))
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = r["text"]
    t.set(qn("xml:space"), "preserve")
    run.append(t)
    h.append(run)
    p._p.append(h)


def write_runs(p, runs, role, char_styles):
    for r in runs:
        if r["link"]:
            add_link(p, r, char_styles)
            continue
        run = p.add_run(r["text"])
        if r["b"] and role not in HEADING_ROLES:
            run.bold = True
        if r["i"]:
            run.italic = True
        if r["u"]:
            run.underline = True
        if r["sup"]:
            run.font.superscript = True
        if r["sub"]:
            run.font.subscript = True
        if r["code"]:
            run.font.name = "Consolas"


def page_break_paragraph():
    p = OxmlElement("w:p")
    r = OxmlElement("w:r")
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    r.append(br)
    p.append(r)
    return p


def apply(a):
    stats = new_stats()
    mapping = parse_pairs(a.map)

    doc = open_doc(a.template)
    styles = resolve_styles(doc)
    char_styles = {}
    for st in doc.styles:
        try:
            if st.type == 2 and norm(st.name) == "hyperlink":
                char_styles["Hyperlink"] = st.style_id
        except Exception:
            pass
    info = detect(doc, a.start_text, a.end_text)
    els = info["els"]
    tstyle = table_style(doc, els, info["start"], info["end"])

    # 1. Cover and replacements.
    values = {"title": a.title, "date": a.date, "description": a.description}
    for el in els[: info["start"]]:
        for p in el.iter(qn("w:p")):
            t = text_of(p).strip()
            key = COVER.get(t.lower())
            if key:
                if values[key]:
                    set_text(p, values[key])
                else:
                    stats["warnings"].append("Cover: sample text %r left in place (missing --%s)." % (t, key))
    for pair in a.replace or []:
        old, _, new = pair.partition("=")
        n = 0
        for p in doc.element.body.iter(qn("w:p")):
            if text_of(p).strip() == old.strip():
                set_text(p, new)
                n += 1
        if not n:
            stats["warnings"].append("--replace: %r not found." % old)

    # 2. Table of contents: clear sample entries and ask Word to update fields on open.
    clear_toc(els[: info["start"]])
    for fc in doc.element.body.iter(qn("w:fldChar")):
        if fc.get(qn("w:fldCharType")) == "begin":
            fc.set(qn("w:dirty"), "true")
    uf = OxmlElement("w:updateFields")
    uf.set(qn("w:val"), "true")
    doc.settings.element.append(uf)

    # 3. Back pages.
    bps = info["back_pages"]
    remove = []
    if a.back_page == "none":
        remove = bps
    elif len(bps) > 1:
        want_programs = a.back_page == "programs"
        chosen = [b for b in bps if b["programs"] == want_programs]
        if not chosen:
            stats["warnings"].append("No '%s' back page found; kept the first one." % a.back_page)
            chosen = bps[:1]
        remove = [b for b in bps if b is not chosen[0]]
    elif bps and a.back_page == "programs" and not bps[0]["programs"]:
        stats["warnings"].append("The template has a single back page without program logos; kept it.")
    for b in bps:
        if b in remove:
            continue
        for el in els[b["from"]:b["to"]]:
            for p in el.iter(qn("w:p")):
                t = text_of(p).strip().lower()
                if t in BACK_PAGE_LABELS or LOREM.search(t):
                    clear_paragraph(p)
    for b in remove:
        for el in els[b["from"]:b["to"]]:
            el.getparent().remove(el)

    # 4. Remove the sample pages.
    end = info["end"]
    # The separator (section end or page break) that closes the body before the back page is
    # kept: it defines the content's header and footer.
    following = [e for e in els[end:] if e.getparent() is not None]
    keep_sep = end < len(els) and end - 1 >= info["start"] and is_separator(els[end - 1])
    for el in els[info["start"]:end - 1 if keep_sep else end]:
        el.getparent().remove(el)
    # Anchor: content is inserted right before this element.
    if keep_sep:
        anchor = els[end - 1]
    elif following:
        anchor = following[0]
        prev = anchor.getprevious()
        if prev is None or not is_separator(prev):
            anchor.addprevious(page_break_paragraph())
        anchor = anchor.getprevious()
    else:
        anchor = doc.element.body.find(qn("w:sectPr"))

    # 5. Content.
    blocks = read_input(a.input, mapping, stats) if a.input else []
    number_headings(blocks, a.numbering, stats)
    if a.title and not any(b["t"] == "par" and b["role"] == "title" for b in blocks[:3]):
        blocks.insert(0, {"t": "par", "role": "title", "runs": [plain_run(a.title)]})

    sect = anchor if anchor.tag == qn("w:sectPr") else (anchor.xpath("./w:pPr/w:sectPr") or [None])[0]
    if sect is None:
        sect = doc.element.body.find(qn("w:sectPr"))
    s = Section(sect, doc.part)
    usable = (s.page_width or Emu(7560000)) - (s.left_margin or 0) - (s.right_margin or 0)

    for b in blocks:
        if b["t"] == "par":
            role = b["role"]
            name = styles.get(role)
            if not name:
                if role not in stats["roles_without_style"]:
                    stats["roles_without_style"].append(role)
                name = styles.get("body")
                if role.startswith("bullet"):
                    b["runs"].insert(0, plain_run("• "))
            p = doc.add_paragraph(style=name) if name else doc.add_paragraph()
            write_runs(p, b["runs"], role, char_styles)
            anchor.addprevious(p._p)
            stats["by_role"][role] = stats["by_role"].get(role, 0) + 1
        elif b["t"] == "img":
            p = doc.add_paragraph(style=styles.get("body")) if styles.get("body") else doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            try:
                width = min(b["cx"] or usable, usable)
                p.add_run().add_picture(io.BytesIO(b["blob"]), width=Emu(int(width)))
                anchor.addprevious(p._p)
                stats["images"] += 1
            except Exception as e:
                p._p.getparent().remove(p._p)
                stats["lost_images"] += 1
                stats["warnings"].append("Image not copied: %s" % e)
        elif b["t"] == "table":
            rows, grid = b["rows"], b["grid"]
            ncol = max(len(r) for r in rows)
            t = doc.add_table(rows=len(rows), cols=ncol)
            if tstyle:
                try:
                    t.style = tstyle
                except Exception:
                    pass
            seen = {}
            for r, row in enumerate(rows):
                for c, cell in enumerate(row):
                    key = grid[r][c]
                    if key in seen:
                        seen[key][1] = (r, c)
                        continue
                    seen[key] = [(r, c), (r, c)]
                    cp = t.cell(r, c).paragraphs[0]
                    if styles.get("body"):
                        cp.style = styles["body"]
                    write_runs(cp, cell, "body", char_styles)
            for (r0, c0), (r1, c1) in seen.values():
                if (r0, c0) != (r1, c1):
                    try:
                        t.cell(r0, c0).merge(t.cell(r1, c1))
                    except Exception:
                        pass
            anchor.addprevious(t._tbl)
            anchor.addprevious(OxmlElement("w:p"))
            stats["tables"] += 1

    # 6. Sections: avoid a blank page at the end.
    body = doc.element.body
    final = body.find(qn("w:sectPr"))
    last = final.getprevious()
    if last is not None and has_sectpr(last) and not text_of(last).strip() and not last.xpath(".//w:drawing"):
        body.replace(final, last.xpath("./w:pPr/w:sectPr")[0])
        body.remove(last)
    elif last is not None and is_separator(last):
        body.remove(last)

    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    doc.save(a.output)

    print("Done: %s" % a.output)
    print("Template: %s" % os.path.basename(a.template))
    print("Blocks by style: %s" % ", ".join("%s=%d" % kv for kv in sorted(stats["by_role"].items())))
    print("Tables: %d  Images: %d" % (stats["tables"], stats["images"]))
    print("Table style: %s" % (tstyle or "none"))
    print("Back pages in template: %d, removed: %d" % (len(bps), len(remove)))
    if stats["unnumbered"]:
        print("Headings left unnumbered: %s" % "; ".join(stats["unnumbered"]))
    problems = []
    if stats["lost_images"]:
        problems.append("%d images were not copied" % stats["lost_images"])
    if stats["footnotes"]:
        problems.append("%d footnotes were not copied (their reference marks are gone)" % stats["footnotes"])
    if stats["text_boxes"]:
        problems.append("%d text boxes were not copied" % stats["text_boxes"])
    if stats["roles_without_style"]:
        problems.append("no template style for: %s (body style used)" % ", ".join(stats["roles_without_style"]))
    for p in problems + stats["warnings"]:
        print("WARNING: " + p)


# ---------------------------------------------------------------- inspect / structure / check

def inspect(path):
    doc = open_doc(path)
    st_map = resolve_styles(doc)
    info = detect(doc)
    els = info["els"]
    kinds = {1: "paragraph", 2: "character", 3: "table", 4: "list"}
    print("Template: %s" % path)
    print("\nBrand styles (starting with _):")
    for st in doc.styles:
        try:
            if (st.name or "").startswith("_"):
                print("  [%s] %s" % (kinds.get(st.type, st.type), st.name))
        except Exception:
            pass
    print("\nRole -> style that will be used:")
    for role in ROLES:
        print("  %-9s %s" % (role, st_map[role] or "MISSING (body style will be used)"))
    print("\nCover (sample texts): %s" % (", ".join(t for _, t in info["cover"]) or "not found"))
    print("Table of contents: %s" % ("yes, ends at element %d" % info["toc"] if info["toc"] is not None else "not found"))
    print("Sample body to replace: elements %d to %d" % (info["start"], info["end"] - 1))
    print("Table style: %s" % (table_style(doc, els, info["start"], info["end"]) or "none"))
    print("Back pages: %d" % len(info["back_pages"]))
    for k, b in enumerate(info["back_pages"]):
        print("  %d) elements %d to %d, %s" % (k + 1, b["from"], b["to"] - 1,
                                              "with programs" if b["programs"] else "simple"))
    print("\nBody elements:")
    for i, el in enumerate(els):
        tag = el.tag.split("}")[1]
        style = el.xpath("./w:pPr/w:pStyle/@w:val")
        flags = []
        if has_sectpr(el):
            flags.append("SECTION-END")
        if has_page_break(el):
            flags.append("PAGE-BREAK")
        if el.xpath(".//w:drawing"):
            flags.append("DRAWING")
        if el.xpath(".//w:txbxContent"):
            flags.append("TEXT-BOX")
        zone = "cover/toc" if i < info["start"] else ("sample" if i < info["end"] else "back page")
        print("  %3d %-4s %-10s %-24s %-24s %s" % (i, tag, zone, (style[0] if style else "")[:24],
                                                   " ".join(flags), text_of(el).strip()[:60]))


def structure(path, map_args):
    stats = new_stats()
    blocks = read_input(path, parse_pairs(map_args), stats)
    count = {}
    for b in blocks:
        if b["t"] == "par":
            count[b["role"]] = count.get(b["role"], 0) + 1
            if b["role"] in HEADING_ROLES or b["role"] == "caption":
                print("  %-8s %s" % (b["role"], "".join(r["text"] for r in b["runs"])[:90]))
        else:
            count[b["t"]] = count.get(b["t"], 0) + 1
    print("\nCount: %s" % ", ".join("%s=%d" % kv for kv in sorted(count.items())))
    print("Unreadable images: %d  Footnotes: %d  Text boxes: %d"
          % (stats["lost_images"], stats["footnotes"], stats["text_boxes"]))
    if not any(r in count for r in ("h1", "h2", "h3")):
        print("WARNING: no headings detected. If the document uses its own heading styles, "
              "pass them with --map \"Style name=h1\".")


def check(path):
    doc = Document(path)
    leftovers, foreign, empty = [], {}, 0
    for p in doc.element.body.iter(qn("w:p")):
        t = text_of(p).strip()
        if t.lower() in COVER or LOREM.search(t) or re.match(r"^_[A-Z][\w ]+\(", t):
            leftovers.append(t[:70])
    # Content only: what comes after the table of contents (cover and TOC belong to the template).
    els = body_elements(doc)
    ti = toc_end(els)
    content = [Paragraph(e, doc._body) for e in els[(ti + 1 if ti is not None else 0):] if e.tag == qn("w:p")]
    for p in content:
        n = p.style.name if p.style is not None else ""
        if p.text.strip() and not n.startswith("_") and not n.lower().startswith(("toc", "header", "footer")):
            foreign[n] = foreign.get(n, 0) + 1
        if n.startswith("_Heading") and not p.text.strip():
            empty += 1
    print("File: %s" % path)
    print("Paragraphs: %d  Tables: %d  Images: %d" % (
        len(doc.paragraphs), len(doc.tables), len(doc.element.body.xpath(".//a:blip"))))
    headings = [p.text.strip()[:70] for p in content
                if p.style is not None and re.match(r"(heading|title|body heading)", norm(p.style.name))
                and p.text.strip()]
    print("Headings (%d):" % len(headings))
    for t in headings:
        print("  " + t)
    if leftovers:
        print("WARNING: sample text left over (%d):" % len(leftovers))
        for t in leftovers[:20]:
            print("  " + t)
    if foreign:
        print("Paragraphs with non-brand styles: %s" % ", ".join("%s=%d" % kv for kv in foreign.items()))
    if empty:
        print("WARNING: %d empty headings" % empty)
    if not leftovers and not empty:
        print("No sample text left over.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("inspect", help="show what the script detects in a template")
    s.add_argument("template")
    s = sub.add_parser("structure", help="show how an input document will be read")
    s.add_argument("input")
    s.add_argument("--map", action="append", help='"Document style=role" (roles: %s)' % ", ".join(ROLES))
    s = sub.add_parser("check", help="review a formatted result")
    s.add_argument("file")
    s = sub.add_parser("apply", help="format a document with a template")
    s.add_argument("--template", required=True)
    s.add_argument("--input")
    s.add_argument("--output", required=True)
    s.add_argument("--title")
    s.add_argument("--date")
    s.add_argument("--description")
    s.add_argument("--numbering", choices=["auto", "none", "original"], default="original")
    s.add_argument("--back-page", choices=["programs", "simple", "none"], default="programs")
    s.add_argument("--map", action="append", help='"Document style=role"')
    s.add_argument("--replace", action="append", help='"sample text=new text" (whole paragraph)')
    s.add_argument("--start-text", help="Text of the first sample paragraph to replace")
    s.add_argument("--end-text", help="Text of the first paragraph to keep at the end")
    a = ap.parse_args()
    if a.cmd == "inspect":
        inspect(a.template)
    elif a.cmd == "structure":
        structure(a.input, a.map)
    elif a.cmd == "check":
        check(a.file)
    else:
        if a.input and os.path.abspath(a.output) == os.path.abspath(a.input):
            sys.exit("The output cannot be the input file.")
        apply(a)


if __name__ == "__main__":
    main()
