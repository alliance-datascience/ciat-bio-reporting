---
name: ciat-bio-reporting
description: Alliance Bioversity-CIAT reporting assistant. Formats reports (Word, Markdown, HTML) with CGIAR Science Program, Accelerator or project Word templates, makes the final PDF, and fills in TIP (tip.alliance.cgiar.org) submissions of any output (reports, datasets, repositories, platforms, links); the user clicks submit. Use for "format this report", "Science Program template", "submit to TIP / CGSpace", "formatea este reporte", "súbelo a TIP", "soumettre à TIP".
---

# TIP reporting assistant

Reply in the user's language. Ask only what the material does not answer; reuse answers. When several options are valid (template, back page, route, numbering), show them with AskUserQuestion and let the user choose. Not everything is a report, and not everything belongs to a Science Program.

## Rules

- TIP: Claude fills in the form; the user clicks the final submit. Never click it, even if asked.
- Never type passwords; the user signs in.
- CGSpace takes only final or published products. Say so if it is a draft.
- Never invent metadata. Never share files outside TIP without permission.
- `PY` = `python3` (macOS, Linux) or `py` / `python` (Windows). Scripts are in `scripts/`, paths relative to this folder.

## Saving tokens

- Read a reference only when you reach its step, and only that one.
- Browser: read the TIP form with the helpers in `scripts/tip_helpers.js` (compact JSON), not with read_page, get_page_text or screenshots. Take a screenshot only when the user reports something visual.
- Long documents: extract fields with a subagent that returns only the fields.
- Trust script output; do not reopen files you just wrote. Look at a PDF page image only if a script reports a problem.

## Step 0. Need and requirements

Unless the request says it, ask: format a document, submit to TIP, or both. Then run `PY scripts/check_setup.py --need format|tip|both`. If nothing is MISSING, continue. If something is missing, read [references/setup.md](references/setup.md).

## Step 1. Output type

| Output | Format? | TIP route |
|---|---|---|
| Report, brief, manual, paper, chapter | Yes, unless final | CGSpace: /CgspaceSubmission/create (PDF, up to 20 MB per file) |
| Presentation, poster, infographic | No | CGSpace |
| Video, audio | No | CGSpace, link only |
| Tool, platform, website, dashboard | No | CGSpace, Digital Tools, type Website or Software, link |
| Software, code, repository | No | CGSpace, type Software or Source Code, link (and DOI) |
| Dataset | No | /DataverseSubmission (data files and data dictionary; the data team publishes in Harvard Dataverse) |
| Innovation, capacity-sharing event, outcome (OICR), policy change | No | /Innovation/star, /CapDev/star, /OICR/star, /Policy/star (not mapped) |

If unclear, show the options. Links and repositories go straight to Step 3.

## Step 2. Formatting

1. Already final (PDF or final Word)? Go to Step 3.
2. Science Program or Accelerator: ask which one. Another project: ask for its template; if none, offer the general options. Lists and download: [references/templates.md](references/templates.md). Download only the template needed, with permission.
3. Format and check: [references/formatting.md](references/formatting.md).
4. Deliver the Word file; the user reviews and approves it.
5. After approval only: `PY scripts/convert.py to-pdf "<file.docx>"`. TIP receives the PDF.

## Step 3. TIP

CGSpace: [references/tip-cgspace.md](references/tip-cgspace.md). Other routes are not mapped: open the route in Chrome, read the fields with JavaScript without saving, and guide the user.

1. Extract what you can from the document or link.
2. Ask what is missing in one AskUserQuestion round.
3. Show the full table of values; wait for the go-ahead.
4. Fill in, verify, show the summary, and tell the user which button to click.
5. Mention TIP's internal deadline if it applies.

## Step 4. Lessons learned (always, at the end)

Even if the session ended early or failed: draft short lessons (what failed or confused, workarounds, unknown TIP fields or errors, template quirks, done by hand, OS and Word or LibreOffice; or "everything worked"). Never include document content, people's names or emails, submission IDs, project codes, paths with user names, passwords or tokens. Then ask with AskUserQuestion whether to share them with the maintainer, Lizeth Llanos: by email / as a GitHub issue / not now. Show the exact text first; send nothing without the user's OK on it.

- Email: draft only, the user sends it. To: Lizeth Llanos <l.llanos@cgiar.org>. Subject: "ciat-bio-reporting: lessons learned from a session".
- Issue (public repository): `gh issue create --repo alliance-datascience/ciat-bio-reporting --title "Lessons learned: <summary>" --body-file <file>`. Without `gh`, give the user https://github.com/alliance-datascience/ciat-bio-reporting/issues/new and the text.
