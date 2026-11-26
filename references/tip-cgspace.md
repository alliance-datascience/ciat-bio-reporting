# TIP, CGSpace route

Form mapped on 2026-11-26 by reading an existing submission (read only).

- New submission: https://tip.alliance.cgiar.org/CgspaceSubmission/create
- User's submissions: https://tip.alliance.cgiar.org/CgspaceSubmission (filters Draft, Review Pending, Complete, Cancelled, Shared With Me)
- Internal deadline for knowledge products of the 2026 cycle: 2027-01-12. The PRMS deadline is 2027-02-12. Check the notice on the page; it changes every year.
- Data team contact: alliance-dm@cgiar.org

## Before starting

1. Check the user's submission list to make sure the output is not already in TIP (search by title). If it is, ask whether they want to update it instead of creating a new one.
2. If the output has a DOI, use the form's DOI Auto-Complete tool and then verify every autocompleted value: they remain editable in TIP and can be wrong.
3. Form buttons (checked 2026-11-26 on /CgspaceSubmission/create): **Exit Form** (`#cancel-button`), **Save Draft** (`#draft`) and **Send to review** (`#send_final`, the final submit: only the user clicks it). Opening /create does not create a draft; nothing is stored until Save Draft or Send to review. The DOI Auto-Complete box (`#searchDOI`) is at the top of General Information. There is also a Generate Citation button (`#generate-citation`). A new submission shows five tabs; "Information Team" only appears on existing submissions.
4. Before Save Draft, ask the user: saving a draft stores the submission in TIP under their name (visible to them in the Draft filter). It is safer than leaving the form half-filled, but it is still a write to TIP.
5. While you type, the form shows "Autosaved HH:MM:SS". That is a local browser save, not a TIP draft: the submission count in /CgspaceSubmission does not change. Until Save Draft or Send to review, the filled form lives only in that browser tab. Check the count (fetch /CgspaceSubmission and read "N Submission") instead of trusting the label.

## Filling tips (learned 2026-11-26, first real run)

- `scripts/tip_helpers.js` has tested helpers (s2pick, setSel, setText, addExt, noScienceProgram, attachServed, verifyDraft). Load it into the page with the javascript tool after each navigation, once the page has loaded for about 3 seconds.
- The browser tool's file upload only reads files inside the session's folders. For files elsewhere (OneDrive project folders), use `scripts/serve_file.py` plus `attachServed`, whatever the size.
- Infographics: Main Collection "Posters, Presentations and Infographics", Publication Type "Infographic". Spanish is listed as "Spanish, Castilian". When the same product exists in two languages, the user chose one submission with both PDFs and both languages.
- Several files in one submission: run one `serve_file.py` per file on different ports (`--port 8765`, `8766`...) and pass them all to `attachServed([[port, name], ...])`. Two 12 MB files took about 2 minutes to save ("Please wait" stays on screen meanwhile).
- The javascript tool stops waiting after 45 seconds (the page keeps running). Start long steps with `runInBackground(...)` and read `window.__job` after waiting; check file sizes with `storedFileSizes()` (HEAD requests) instead of downloading the files.
- Partner authors may already exist in TIP as External records (e.g. 'Surname, Firstname - External - INSTITUTION'). Search first and reuse them; add a new external author only when nothing matches.

- Every list is a select2. Plain lists (authorship, collection, type, languages, countries, regions, corresponding author, open access, usage rights) can be set with jQuery: `jQuery('#id').val([...]).trigger('change')`, choosing option values by their exact text. IDs: `first_name01` (title), `authorship_field`, `p_collection`, `p_type`, `c_author`, `abstract_field`, `date_publication` (YYYY-MM-DD), `languages`, `countries`, `regions`, `open_access`, `usage_rigth` (sic), `selectAgrovoc`, `selectAgrovocES`, `fileupload`.
- Search lists (authors `find_author`, affiliations, project `find_project`, sponsors, AGROVOC) load results from the server: open with `jQuery(sel).select2('open')`, type at least 3 letters, read `.select2-results__option`, move with Down until `.select2-results__option--highlighted` is the right one, then press Return. Verify before each Return.
- Staff directory names can differ from the document: e.g. "Wanjiku, Beatrice" is "Githu, Beatrice Wanjiku"; "Méndez, Andrés Camilo" is "Mendez Alzate, Andres Camilo" (External, found by searching the given names). Match by email when in doubt, and tell the user about the difference.
- Choosing "International Center for Tropical Agriculture" as affiliation fills country Kenya and the Kenya office website from TIP's registry; point it out to the user.
- Sponsors with the same name exist in several countries (Department of Foreign Affairs and Trade: Ireland and Australia). Pick by the country stated in the document.
- "Has it been externally peer-reviewed?" is disabled for Reports.
- The year field needs a full date. If the user only gives a year, the PDF metadata creation date (pypdf `reader.metadata`) is evidence-based; say which date you used.
- File upload: the file input `#fileupload` is outside the Save Draft form; the page sends the file with the draft (POST /saveSubmission) when Save Draft is clicked, so attach files before saving. Files up to 10 MB: use the browser tool's file upload. Larger files (most Canva PDFs are 9 to 13 MB): with the user's OK, run `PY scripts/serve_file.py "<file>"` in the background (127.0.0.1 only, one file, stops after 3 minutes) and follow its docstring to put the file in `#fileupload` from the page; or ask the user to attach it. A 12.6 MB PDF took about 60 seconds to save. Then open the draft and confirm the stored file has the same size as the original (fetch the "Download File" link and compare bytes).
- On reload, TIP sets "Does this result contribute to a Science Program or Accelerator?" back to Yes and the ToC mapping to Yes when the project is linked to a program. Before every Save Draft or Send to review, set the contribution to what the user said again; otherwise saving fails with "Select the High Level Output for the Theory of Change mapping".
- Do not set a Research Lever or "edited by Science Writing" unless the user says so (both optional).
- Selecting a project auto-completes fields from the project record (marked with a light-bulb icon). A project "Contributing to CGIAR Portfolio" ticks "Science Program(s) and Accelerator(s)" with its program, sets "Does this result contribute...?" to Yes and the detailed ToC mapping to Yes. Save Draft then fails with "Select the High Level Output for the Theory of Change mapping". Re-check these after choosing the project and set them to what the user said: answering "No" to the contribution question hides the ToC mapping, while the program stays tagged as the project's association.
- Science Program is not the same as Lever. "CGIAR Climate Action science program" belongs to the CGIAR 2025-2030 portfolio (fields "Science Program(s) and Accelerator(s)" and "Does this result contribute...?"). "Lever3: Climate Action" is the Alliance's internal research area the staff belong to (field "Research Levers and Platforms", `lever_field`, and the "Lever3" tag next to staff authors). TIP fills the Lever from the authors. Never infer one from the other: ask about the Science Program separately. If the user says the output does not contribute to a Science Program, remove the program the project auto-filled (untick "Science Program(s) and Accelerator(s)" and clear its selection). On reload TIP may tick that box again from the project, but with no program selected, which is fine.
- AGROVOC terms can be stored with their preferred label (e.g. "capacity development" was saved as "Capacity building").
- After Save Draft the page goes back to the submission list; the new draft is at the top with status Draft. Open /CgspaceSubmission/update/<id> and read the fields again on the loaded page (authors and corresponding author are filled by JavaScript, so a raw fetch of the HTML does not show them).

## Patterns from accepted submissions

Look at two or three items of the same project already in CGSpace and reuse their project-level values (they were accepted by the library). The CGSpace REST API returns an item's full metadata without signing in:

```
https://cgspace.cgiar.org/server/api/core/items/<item uuid from the cgspace.cgiar.org/items/<uuid> link>
```

Useful fields: cg.authorship.types, cg.contributor.affiliation, cg.contributor.donor, cg.identifier.project, cg.coverage.region, dcterms.accessRights, dcterms.license, dcterms.type, cg.subject.*. To check for duplicates, search `https://cgspace.cgiar.org/server/api/discover/search/objects?query="<title words>"&dsoType=ITEM`.

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
