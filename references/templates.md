# Templates

## Where they are

Official source: SharePoint My-CGIAR, folder `SOCOMMS/Brand Assets/Final Assets/2. Word templates`.
Link: https://cgiar.sharepoint.com/sites/My-CGIAR/SOCOMMS/Brand%20Assets/Final%20Assets/2.%20Word%20templates

Each user adds that folder to their OneDrive with "Add shortcut to My files". It then shows up on their computer, on any operating system. `scripts/check_setup.py` finds it and prints its path (line "CGIAR Word templates in OneDrive").

If it does not show up, give the user the link above and explain how to add the shortcut. If a file is cloud-only, open it once or mark it "Always keep on this device" so it downloads.

Each template exists as .dotx and as .docx. The script accepts both; prefer the .dotx when available.

## Science Programs and Accelerators

| Name | Type | File |
|---|---|---|
| Better Diets and Nutrition | Science Program | Report-Better Diets and Nutrition.dotx |
| Breeding for Tomorrow | Science Program | Report-Breeding for Tomorrow.dotx |
| Climate Action | Science Program | Report-Climate Action.dotx |
| Food Frontiers and Security | Science Program | Report-Food Frontiers and Security.dotx |
| Multifunctional Landscapes | Science Program | Report-Multifunctional Landscapes.dotx |
| Policy Innovations | Science Program | Report-Policy Innovations.dotx |
| Scaling for Impact | Science Program | Report-Scaling for Impact.dotx |
| Sustainable Animal and Aquatic Foods | Science Program | Report-Sustainable Animal and Aquatic Foods.dotx |
| Sustainable Farming | Science Program | Report-Sustainable Farming.dotx |
| Capacity Sharing | Accelerator | Report-Capacity Sharing.dotx |
| Digital Transformation | Accelerator | Report-Digital Transformation.dotx |
| Gender Equality and Inclusion | Accelerator | Report-Gender Equality and Inclusion.dotx |
| Genebanks | Accelerator | Report-Genebanks.dotx |

Note: the .docx version of Breeding for Tomorrow is named "Report-Breeding for Timorrow.docx" (typo in SharePoint).

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

Read from Report-Climate Action.docx on 2026-11-26. Assumed to be the same for all 13 (confirm by running `format_report.py inspect` on each the first time):
1. Cover with the sample texts "Document Title", "Date", "Document Description".
2. Table of contents ("Contents").
3. Style sample page: _Title, _Subtitle, _Heading 1, _Heading 2, _Body Intro, _Body Text, _Body Heading, _Body bullet 1 and 2, _Body Bullet numbered 1 and 2, _Stat, _Caption source footnote, _Pullout, _Source, _Quote.
4. Table sample page.
5. Two back pages: "Back Page" and "Back Page With Programs", with Latin filler text.
