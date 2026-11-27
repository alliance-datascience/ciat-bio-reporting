# Templates

Source: SharePoint My-CGIAR, `SOCOMMS/Brand Assets/Final Assets/2. Word templates`
(https://cgiar.sharepoint.com/sites/My-CGIAR/SOCOMMS/Brand%20Assets/Final%20Assets/2.%20Word%20templates).

## Getting one

1. `PY scripts/check_setup.py --templates` lists the local cache (`~/.ciat-bio-reporting/templates/`) and any OneDrive shortcut.
2. If missing, ask permission to download that one file (name, source, size). Each template exists as .docx and .dotx: take the one modified most recently in SharePoint.
3. Open in the user's Chrome (they are signed in): `https://cgiar.sharepoint.com/sites/My-CGIAR/_layouts/15/download.aspx?SourceUrl=/sites/My-CGIAR/SOCOMMS/Brand%20Assets/Final%20Assets/2.%20Word%20templates/<URL-encoded file name>`. The browser may report an error and still download: check Downloads before retrying.
4. Move only that file into the cache, without " (1)" suffixes. If it fails, ask the user to download it.

## Science Programs and Accelerators

File `Report-<Name>`. Science Programs: Better Diets and Nutrition, Breeding for Tomorrow (the .docx is misspelled "Report-Breeding for Timorrow"), Climate Action, Food Frontiers and Security, Multifunctional Landscapes, Policy Innovations, Scaling for Impact, Sustainable Animal and Aquatic Foods, Sustainable Farming. Accelerators: Capacity Sharing, Digital Transformation, Gender Equality and Inclusion, Genebanks.

Program variants (offer both):
- Climate Action: "CGIAR Climate Action Report Template.dotx" (My-CGIAR, Shared Documents).
- Sustainable Farming: "CGIAR Sustainable Farming Reporting Template 2025.dotx" (SFP Leadership Team site).
- Multifunctional Landscapes: "MFL SP report template: Program v5.docx" (MFL site).

## Other projects without a template (offer these)

1. CGIAR report template.docx. 2. Draft template for technical reports_V1.dotx (both in 2. Word templates). 3. Alliance Report Template.dotx (Alliance-DMOS site, 2021, may be outdated). 4. A related Science Program template. 5. Clean format: `--template` pointing to a blank .docx.

## Report-<Program> structure (checked on MFL)

Cover content control with "Document Title", "Date", "Document Description"; "Contents" TOC listing only _Title (the script retargets it); style and table sample pages (styles _Title, _Heading 1/2, _Body Text, _Body Heading, _Body bullet 1/2, _Body Bullet Numbered 1/2, _Quote, _Caption; table style "CGIAR"); two back pages as tables ("Back Page", "Back Page With Programs"). No section breaks: _Title starts a new page, so always pass `--title`.
