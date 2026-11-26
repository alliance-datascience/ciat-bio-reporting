# ciat-bio-reporting

A Claude Code skill for Alliance of Bioversity International and CIAT staff that:

1. Formats reports (Word, Markdown, or older Word/OpenDocument files) with the official CGIAR Science Program or Accelerator Word template, another project's template, or a clean unbranded format.
2. Guides the submission of any knowledge product to the Alliance TIP platform (https://tip.alliance.cgiar.org): reports, briefs, presentations, digital tools, platforms, links, repositories, software and datasets. Claude fills in the form; the user always clicks the final submit button.

It replies in the language the user writes in and works on Windows, macOS and Linux.

## Install

Clone this repository into your Claude Code skills folder (you need access to the alliance-datascience organization):

```bash
# macOS / Linux
git clone https://github.com/alliance-datascience/ciat-bio-reporting.git ~/.claude/skills/ciat-bio-reporting
```

```powershell
# Windows (PowerShell)
git clone https://github.com/alliance-datascience/ciat-bio-reporting.git "$env:USERPROFILE\.claude\skills\ciat-bio-reporting"
```

To update later, run `git pull` inside that folder. To use it in a single project only, clone it into `<project>/.claude/skills/ciat-bio-reporting` instead.

Then, in Claude Code, type `/ciat-bio-reporting` or ask, for example, "format this report with the Climate Action template" or "submit this repository to TIP".

## Requirements

The skill checks these at the start (`scripts/check_setup.py`) and, if something is missing, helps install it or drafts a request to Alliance IT Support.

- Python 3.8 or newer, with python-docx 1.0 or newer.
- Access to the CGIAR "2. Word templates" folder (SharePoint My-CGIAR, SOCOMMS/Brand Assets/Final Assets). The skill downloads only the template you need, with your permission, into `~/.ciat-bio-reporting/templates/`.
- Optional: Microsoft Word (Windows), textutil (macOS, built in) or LibreOffice, to convert older files and preview results.
- For TIP: Google Chrome with the Claude in Chrome extension, and a CGIAR account with access to TIP.

## Contents

```
SKILL.md                  Entry point: the guided flow
references/setup.md       Requirements check, install help, email to IT
references/tip-routes.md  Which TIP route each output type uses
references/templates.md   Where the templates are and which to offer
references/formatting.md  How to format a document
references/tip-cgspace.md TIP CGSpace form fields and how to fill them
scripts/check_setup.py    Requirements check (standard library only)
scripts/convert.py        Cross-platform conversion and preview (standard library only)
scripts/format_report.py  Applies a Word template to a .docx or .md document
scripts/serve_file.py     Serves one local file to the TIP page for large uploads (127.0.0.1 only, auto-stops)
```

## Status

- Formatting: tested with the real Report-Multifunctional Landscapes template (2026-11-26). Other templates are expected to share its structure; `inspect` confirms it on first use.
- TIP: CGSpace form mapped and tested on 2026-11-26 up to a saved draft with a 12.6 MB PDF attached. Dataverse, Innovation Dev, Capacity Sharing, OICR and Policy Change routes are not mapped yet.

## Known limitations

- Footnotes and text boxes in the source document are not copied (the script reports them).
- Separate numbered lists may not restart at 1.

## Maintainers

Alliance of Bioversity International and CIAT, Data Science team. Report issues in this repository.
