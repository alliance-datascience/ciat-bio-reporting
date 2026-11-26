# TIP, CGSpace route

Form mapped on 2026-11-26 by reading an existing submission (read only).

- New submission: https://tip.alliance.cgiar.org/CgspaceSubmission/create
- User's submissions: https://tip.alliance.cgiar.org/CgspaceSubmission (filters Draft, Review Pending, Complete, Cancelled, Shared With Me)
- Internal deadline for knowledge products of the 2026 cycle: 2027-01-12. The PRMS deadline is 2027-02-12. Check the notice on the page; it changes every year.
- Data team contact: alliance-dm@cgiar.org

## Before starting

1. Check the user's submission list to make sure the output is not already in TIP (search by title). If it is, ask whether they want to update it instead of creating a new one.
2. If the output has a DOI, use the form's DOI Auto-Complete tool and then verify every autocompleted value: they remain editable in TIP and can be wrong.
3. [To confirm on the first real use] Which buttons the new form has (save draft, next, submit). Read them with JavaScript without clicking and record them here.

## Fields by tab

Source: E = extract from the document or link; A = ask the user; E/A = extract and confirm.

### A. General Information (#section-A-container)
| Field | Required | Source | Notes |
|---|---|---|---|
| Title | Yes | E | |
| Author(s) | Yes | E/A | Format "Surname, Firstname", in publication order. Staff search (3 letters minimum); external authors with "Add External Or Corporate Author" |
| Organizations Affiliated to the Authors | No | E/A | Full name, country, website, acronym |
| Authorship Types | Yes | A | CGIAR single centre, CGIAR multi-centre, CGIAR and developing country institute, CGIAR and advanced research institute, Not CGIAR developing country institute, Not CGIAR international institute, Consultant |
| Main Collection: Alliance Bioversity CIAT | Yes | E/A | Reports, Journal Articles, Policy and Research Briefs, Posters Presentations and Infographics, Books Manuals and Guides, Datasets, Digital Tools, Scientific Multimedia, Working and Discussion Papers, among others |
| Publication Type | Yes | E/A | Report, Brief, Software, Source Code, Website, Dataset, Presentation, Poster, Video, Manual, Working Paper, among others |
| Corresponding Author | Yes | A | |
| Abstract | No | E | |
| Year of Publication | Yes | E | |
| Online Publication Date | No | E | |
| Languages | Yes | E | |
| Country, Region | No | E | Countries or regions where the work took place |
| Member's contact information | No | A | Staff only |

### B. Access, Sponsor and Research Focus (#section-B-container)
| Field | Required | Source | Notes |
|---|---|---|---|
| CGIAR portfolio component types | Yes | A | Science Programs and Accelerators, project, historical structure (Initiative, CRP) or not applicable |
| Project(s) | No | A | |
| Does this result contribute to a Science Program or Accelerator? | Yes | A | If the document was formatted with a Science Program template, this is already known |
| Primary Science Program | Yes if it contributes | A | Reuse the program chosen for formatting |
| High Level Output, Indicator, Quantitative contribution | Yes if it contributes | A | The user must know them; do not guess |
| Edited by the Alliance Science Writing team? | No | A | |
| Related to impact or evaluative studies? | Yes | A | If yes, pick the study type (EPIA, adoption, evaluation, synthesis, ex-ante, other) |
| Externally peer-reviewed? | Yes | A | |
| Accessibility | Yes | A | |
| Usage Rights | Yes | A | License |
| Sponsors | No | E/A | Donors |
| Research Levers and Platforms, Programs and Accelerators, Collections | No | A | |
| Notes | No | A | |
| DOI, Preprint | No | E | |

### C. Keywords/Files (#section-C-container)
| Field | Required | Source | Notes |
|---|---|---|---|
| AGROVOC Keywords (English) | Yes | E/A | Propose terms from the AGROVOC vocabulary and let the user confirm |
| AGROVOC Keywords (Spanish) | No | E/A | |
| Files | Depends | User | Up to 20 MB per file. Links and repositories have no file |

### D. Intellectual Property (#section-D-container)
Always A: who owns the rights (CIAT, Bioversity, both, third parties), legal restrictions, commercialization potential, whether it needs further development. When in doubt, the form refers to the Alliance legal team.

### E. Information Team (#section-E-container)
Internal use by the library. Do not fill in.

### F. Share Submission (#section-F-container)
Optional: share the submission with colleagues (user search). Ask.

## How to fill in

- Use the Claude in Chrome tools (find, form_input, computer). The lists are Materialize selects: if form_input does not apply, click the field and pick the visible option.
- After each tab, read the values with JavaScript and compare them with the table the user approved.
- To read fields without the noise of the option lists, extract labels per section (#section-X-container) with JavaScript; get_page_text returns huge country and language lists.
- Do not click the final submit. When done, show the summary and tell the user which button to click.
