# ciat-bio-reporting

A Claude Code skill for Alliance of Bioversity International and CIAT staff that:

1. Formats reports (Word, Markdown, or older Word/OpenDocument files) with the official CGIAR Science Program or Accelerator Word template, another project's template, or a clean unbranded format.
2. Guides the submission of any knowledge product to the Alliance TIP platform (https://tip.alliance.cgiar.org): reports, briefs, presentations, digital tools, platforms, links, repositories, software and datasets. Claude fills in the form; the user always clicks the final submit button.

It replies in the language the user writes in and works on Windows, macOS and Linux.

## Install

Copy the `ciat-bio-reporting` folder to one of:
- `~/.claude/skills/` to use it in every project, or
- `<project>/.claude/skills/` to use it in one project.

Then, in Claude Code, type `/ciat-bio-reporting` or ask, for example, "format this report with the Climate Action template" or "submit this repository to TIP".

## Requirements

The skill checks these at the start (`scripts/check_setup.py`) and, if something is missing, helps install it or drafts a request to Alliance IT Support.

- Python 3.8 or newer, with python-docx 1.0 or newer.
- A OneDrive shortcut to the CGIAR "2. Word templates" folder (SharePoint My-CGIAR, SOCOMMS/Brand Assets/Final Assets).
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
```

## Status

- Formatting: tested with a synthetic template that mimics Report-Climate Action. To be validated with the real templates.
- TIP: CGSpace form mapped; not yet tested end to end. Dataverse, Innovation Dev, Capacity Sharing, OICR and Policy Change routes are not mapped yet.

## Known limitations

- Footnotes and text boxes in the source document are not copied (the script reports them).
- Separate numbered lists may not restart at 1.

## Maintainers

Alliance of Bioversity International and CIAT, Data Science team. Report issues in this repository.
