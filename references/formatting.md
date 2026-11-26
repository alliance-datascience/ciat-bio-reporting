# Formatting a document with a template

The script is `scripts/format_report.py` (Python 3.8+ with python-docx). Paths are relative to this skill's folder. `PY` below means `python3` on macOS and Linux, `py` (or `python`) on Windows. Requirements are checked first with setup.md.

## 1. Prepare the input

| What the user brings | What to do |
|---|---|
| .docx | Use as is |
| .md | Use as is; images with relative paths are looked up next to the .md |
| .html, .htm (a web page or HTML report) | Use as is. h2 becomes a level-1 heading, h3 level 2, card titles (a short text box opening a card) level 3; "Section 05"-style labels are dropped and number badges (1, 01) are prefixed to the next heading. Navigation, side bars, footers, forms and embedded frames are skipped. Leave out other parts with `--html-skip <element id>` and `--html-skip-containing "<text>"` (only drops single text boxes, never whole sections). Ask the user which web-only parts (forms, buttons, "click here") do not belong in the report |
| .doc, .rtf, .odt | Convert first: `PY scripts/convert.py to-docx "<file>"`. It uses Word (Windows), textutil (macOS) or LibreOffice. If none is available, ask the user to open the file and save it as .docx |
| Google Doc | Ask them to download it as .docx |
| PDF | Ask: do they have the original Word? If not, is the PDF ready to submit as is? Converting PDF to Word loses structure; do not do it without saying so |
| Text pasted in the chat | Save it as .md in a working folder and continue |

Never modify the user's original file. The output goes next to the original with the template suffix, for example `Final_report_ClimateAction.docx`.

## 2. Choose the template

See templates.md: look for it locally and, if needed, download only that template. If the template is new in this session, inspect it first:

```bash
PY scripts/format_report.py inspect "<template.dotx>"
```

It lists the styles and the cover, table of contents and back-page markers it found, and the ones missing. If something is missing, tell the user before going on.

For another project's template shared by the user, inspection is mandatory: confirm with them which style is the title, which are the headings and where the body starts.

## 3. Ask for the options (one AskUserQuestion round)

- Heading numbering: number automatically (1., 1.1 on the first two levels; summary, references, annexes and similar stay unnumbered), removing any manual numbering / remove all numbering / keep the document's own numbering.
- Back page (Report-<Program> templates only): with program logos / simple / no back page.
- Cover: title, date and description. Propose the document's title, the date as "Month YYYY" and a one-line description taken from the summary; the user confirms or corrects.

Before applying, check how the document will be read:

```bash
PY scripts/format_report.py structure "<document>"
```

If headings are not detected (the document uses its own styles, or only bold text), pass the mapping with `--map "Style name=h1"` (roles: title, subtitle, h1, h2, h3, body, bullet1, bullet2, num1, num2, quote, caption, source).

## 4. Apply

```bash
PY scripts/format_report.py apply \
  --template "<template>" \
  --input "<document.docx|.md>" \
  --output "<result.docx>" \
  --title "<title>" --date "<date>" --description "<description>" \
  --numbering auto|none|original \
  --back-page programs|simple|none
  --toc-levels 2          (heading levels in the table of contents; 0 keeps the template's own TOC)
```

What it does:
- Fills in the cover and keeps the template's table of contents.
- Removes the sample pages (styles, tables, Latin filler).
- Brings the content over with the template styles: titles, headings, paragraphs, bullets, numbered lists, quotes, captions, tables, images, bold, italics and links.
- Points the table of contents at the report's heading styles (h1 and h2 by default), because some brand templates list only their "_Title" style there (MFL does). After saving, Microsoft Word fills in the table of contents and page numbers (macOS: AppleScript; Windows: COM), so the user never sees an "update fields?" prompt. Without Word, or with `--no-word`, the file asks to update fields when opened. `PY scripts/convert.py refresh <file.docx>` does the same for a file edited later.

For another project's template without the CGIAR markers, use `--start-text` (first sample paragraph to replace), `--end-text` (first paragraph to keep at the end) and `--replace "sample text=new text"` for its cover.

## 5. Check before delivering

```bash
PY scripts/format_report.py check "<result.docx>"
PY scripts/convert.py preview "<result.docx>" --outdir "<working folder>"
```

`check` lists leftover sample text, paragraphs with styles that are not from the template, empty headings and the count of headings, tables and images. Compare with the original: no content may be lost. `preview` makes a PDF (Word or LibreOffice) or, on macOS without them, a thumbnail of the first page; look at it with the Read tool. If no preview tool is available, skip it and ask the user to look at the file.

## Checking that no content was lost

For HTML or long documents, compare sentences: extract the text of the source (without headings and labels) and check that every sentence of more than 30 characters appears in the result. Report what is missing and why (intentionally skipped, or lost). A text filter that is too broad can drop real content: on 2026-11-26 "record your response" also removed an About paragraph; the precise phrase fixed it.

## Known limitations (2026-11-26)

- Footnotes and text boxes from the original document are not copied; the script counts them and warns. They have to be moved by hand.
- Numbered lists follow the template style's numbering; separate lists may not restart at 1.
- Tested with the real Report-Multifunctional Landscapes template, from .docx, .md and a real HTML document (MOSAIC Vision & Foundations). Run `inspect` on any other template the first time and adjust if something is not detected.

## 6. Deliver

Tell the user where the file is. When Microsoft Word is installed, `apply` has already filled in the table of contents and page numbers, so the file opens with no prompt. Only if the output said "Microsoft Word not available", tell them Word will ask whether to update fields and they should answer yes. Point out anything that could not be mapped (for example text boxes or footnotes) so they review it by hand, and ask them to review and approve the Word file. They may edit it in Word; the PDF is made from the file as they leave it.

## 7. PDF for TIP (after the user approves the Word file)

Only after the user says the Word file is good. Ask them to close it in Word first, so their last edits are saved.

```
PY scripts/convert.py to-pdf "<result.docx>"            # writes <result>.pdf next to it; --output to choose
```

- macOS and Windows: Microsoft Word opens a temporary copy, updates the table of contents and fields, and exports the PDF. The user's Word file is not modified. No dialogs: the copy has no "update fields?" flag, alerts are off, and on macOS the work happens inside Word's own sandbox folder (~/Library/Containers/com.microsoft.Word/Data/tmp), so Word never asks for file access. The only dialog left is macOS's one-time security question the very first time (allow Terminal, or the Claude app, to control Microsoft Word); it cannot be skipped by a script, and after the user accepts it never appears again.
- Without Word: LibreOffice converts it but does not update the table of contents; the script warns. Check the TOC, or ask the user to export from Word (File > Save As > PDF).
- The script warns if the PDF is over 20 MB (TIP's limit per file).

Read the first pages of the PDF (Read tool with `pages`) and check the cover, that the table of contents lists the sections with page numbers, and the first content page. Tell the user where the PDF is, then ask whether to submit it to TIP (SKILL.md Step 3), uploading the PDF.
