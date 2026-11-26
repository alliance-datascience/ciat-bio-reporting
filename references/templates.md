# Templates

## Where they are

Official source: SharePoint My-CGIAR, folder `SOCOMMS/Brand Assets/Final Assets/2. Word templates`.
Folder: https://cgiar.sharepoint.com/sites/My-CGIAR/SOCOMMS/Brand%20Assets/Final%20Assets/2.%20Word%20templates

## Getting the template the user needs

Download only the template the user needs, never the whole folder.

1. Look first in the local template cache and in OneDrive:
   ```bash
   PY scripts/check_setup.py --templates
   ```
   It lists the templates already in `~/.ciat-bio-reporting/templates/` (Windows: `%USERPROFILE%\.ciat-bio-reporting\templates\`) and in a OneDrive shortcut to the folder, if the user has one.
2. If the template is not there, or the SharePoint copy is newer, ask permission to download it, stating the file name, the source (SharePoint My-CGIAR, 2. Word templates) and its size (see the folder listing in the browser).
3. Each template exists as .docx and .dotx. Pick the one modified most recently in SharePoint (the folder listing shows the date). Example: on 2026-11-26, Report-Multifunctional Landscapes.docx (3.65 MB, updated 2026-08-05) was newer than the .dotx (10.1 MB, 2025-07-24).
4. Download it in the user's browser (Claude in Chrome), where they are signed in to CGIAR, by opening:
   ```
   https://cgiar.sharepoint.com/sites/My-CGIAR/_layouts/15/download.aspx?SourceUrl=/sites/My-CGIAR/SOCOMMS/Brand%20Assets/Final%20Assets/2.%20Word%20templates/<file name, URL-encoded>
   ```
   The file lands in the user's Downloads folder. A browser may report an error and still download it: check the Downloads folder before trying again, so there are no duplicates.
5. Move only that file into the template cache, with its original name (without " (1)" suffixes). Never delete or move other files from Downloads.
6. If the browser cannot download it, ask the user to download that one file from the folder link above and tell you where it is.

## Science Programs and Accelerators

| Name | Type | File (without extension) |
|---|---|---|
| Better Diets and Nutrition | Science Program | Report-Better Diets and Nutrition |
| Breeding for Tomorrow | Science Program | Report-Breeding for Tomorrow (.dotx); the .docx is named "Report-Breeding for Timorrow" (typo in SharePoint) |
| Climate Action | Science Program | Report-Climate Action |
| Food Frontiers and Security | Science Program | Report-Food Frontiers and Security |
| Multifunctional Landscapes | Science Program | Report-Multifunctional Landscapes |
| Policy Innovations | Science Program | Report-Policy Innovations |
| Scaling for Impact | Science Program | Report-Scaling for Impact |
| Sustainable Animal and Aquatic Foods | Science Program | Report-Sustainable Animal and Aquatic Foods |
| Sustainable Farming | Science Program | Report-Sustainable Farming |
| Capacity Sharing | Accelerator | Report-Capacity Sharing |
| Digital Transformation | Accelerator | Report-Digital Transformation |
| Gender Equality and Inclusion | Accelerator | Report-Gender Equality and Inclusion |
| Genebanks | Accelerator | Report-Genebanks |

Some programs have their own, more recent variant. If the user is from one of these, show both options and let them choose:
- Climate Action: "CGIAR Climate Action Report Template.dotx" (My-CGIAR, Shared Documents, 2026-09-29).
- Sustainable Farming: "CGIAR Sustainable Farming Reporting Template 2025.dotx" (SFP Leadership Team site, Reporting guidelines).
- Multifunctional Landscapes: "MFL SP report template: Program v5.docx" (MFL site).

## General templates for other projects

When the project has no template of its own, show these options and let the user choose:
1. CGIAR report template.docx (folder 2. Word templates).
2. Draft template for technical reports_V1.dotx (folder 2. Word templates).
3. Alliance Report Template.dotx (Alliance-DMOS site, 2021-08-23 version; may be outdated).
4. A Science Program template, if the work relates to one.
5. Clean, unbranded format: only consistent heading, numbering and table styles (`format_report.py apply` with `--template` pointing to a blank .docx).

## Structure of the Report-<Program> templates

Checked on the real Report-Multifunctional Landscapes.docx on 2026-11-26 (`format_report.py inspect`). Run `inspect` on any other template the first time it is used.

1. Cover: a content control with images, holding the sample texts "Document Title", "Date" and "Document Description" (styles _Cover Title, _Cover Date, _Cover Text).
2. Table of contents: "Contents" heading and a TOC field that lists only "_Title" (`TOC \h \z \t "_Title,1"`). format_report.py rewrites it to list _Heading 1 and _Heading 2 (`--toc-levels`).
3. Style sample page: _Title, _Subtitle, _Heading 1, _Heading 2, _Body Intro, _Body Text, _Body Heading, _Body bullet 1 and 2, _Body Bullet Numbered 1 and 2, _Stat, _Caption, _Pullout, _Source, _Quote.
4. Table sample page, with table style "CGIAR" and table paragraph styles (_Table Title, _Table Column Heading, _Table Body, _Table Subheading, _Table Total).
5. Two back pages, built as tables with images: "Back Page" (simple) and "Back Page With Programs", with Latin filler text.

There are no section breaks: pages are separated because _Title starts a new page. Always pass `--title`, so the content starts on its own page after the table of contents. The footer shows the title of the current section and "Page X of Y"; Word updates it.
