# Formatting with a template

Script: `scripts/format_report.py`. Never modify the user's file; write `<name>_<Program>.docx` next to it.

## 1. Input

- .docx, .md (images relative to the .md), .html/.htm: use as is.
- HTML: h2 becomes h1, h3 h2, card titles h3; "Section 05" labels are dropped; number badges prefix the next heading; nav, footers, forms and iframes are skipped. Ask which web-only parts (forms, buttons) to leave out, then use `--html-skip <id>` or `--html-skip-containing "<exact phrase>"` (drops single text boxes only; a broad phrase can drop real paragraphs).
- .doc, .rtf, .odt: `PY scripts/convert.py to-docx "<file>"`. Google Doc: ask for a .docx download. Pasted text: save as .md.
- PDF: ask for the original Word; converting a PDF loses structure.

## 2. Template

A template used for the first time: `PY scripts/format_report.py inspect "<template>"`. If markers are missing (cover, TOC, back pages), tell the user. For a project's own template, confirm with the user which styles are title and headings.

## 3. Options (one AskUserQuestion round)

- Numbering: auto (1., 1.1; summary, references, annexes unnumbered) / none / keep the document's.
- Back page (Report-<Program>): with program logos / simple / none.
- Cover: propose title, date "Month YYYY" and a one-line description; the user confirms.

If headings may not be detected, run `structure "<document>"` and pass `--map "Style name=h1"` (roles: title, subtitle, h1, h2, h3, body, bullet1, bullet2, num1, num2, quote, caption, source).

## 4. Apply and check

```
PY scripts/format_report.py apply --template "<template>" --input "<document>" --output "<result.docx>" \
  --title "<title>" --date "<date>" --description "<description>" \
  --numbering auto|none|original --back-page programs|simple|none
PY scripts/format_report.py check "<result.docx>"
```

- `apply` removes the sample pages, applies the template styles to headings, lists, tables, images and links, and points the table of contents at h1 and h2 (`--toc-levels 0-3`). Then Microsoft Word fills in the TOC and page numbers, so the file opens with no prompt. Without Word (or with `--no-word`) the file asks to update fields; tell the user to answer yes.
- Other templates without CGIAR markers: `--start-text`, `--end-text`, `--replace "sample=new"`.
- `check` reports leftover sample text, off-template styles, empty headings and counts (`--list` prints the headings). Compare the counts with `structure` of the input. For HTML or long inputs, check that every source sentence over 30 characters is in the result, and report anything missing.
- Not copied (the script warns): footnotes and text boxes. Separate numbered lists may not restart at 1.

## 5. Deliver, then PDF

Give the path and what could not be mapped; the user reviews and approves the Word file (they may edit it). After approval, ask them to close it in Word, then:

```
PY scripts/convert.py to-pdf "<result.docx>"
```

Word updates the TOC and fields in a temporary copy and exports the PDF, with no dialogs (on macOS only the one-time permission to control Word, which no script can skip). Without Word, LibreOffice is used and the TOC is not updated; the script warns. It prints the page count and warns if the PDF is over 20 MB (TIP's limit). Then offer Step 3 with the PDF. `PY scripts/convert.py refresh "<file.docx>"` updates the TOC of a Word file edited later.
