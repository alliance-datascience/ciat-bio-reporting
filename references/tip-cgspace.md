# TIP, CGSpace route

New: https://tip.alliance.cgiar.org/CgspaceSubmission/create. List: /CgspaceSubmission. Deadline (2026 cycle): 2027-01-12 (PRMS 2027-02-12); check the notice, it changes yearly. Data team: alliance-dm@cgiar.org.

## Before filling in

1. Check the user's list and CGSpace for the title (`https://cgspace.cgiar.org/server/api/discover/search/objects?query="<words>"&dsoType=ITEM`). If it exists, ask whether to update it.
2. Reuse project-level values from 2 or 3 accepted items of the same project: `https://cgspace.cgiar.org/server/api/core/items/<uuid>` (cg.authorship.types, cg.contributor.affiliation, cg.contributor.donor, cg.coverage.region, dcterms.accessRights, dcterms.license, dcterms.type, cg.subject.*). Fetch with a script and print only these fields.
3. DOI: use DOI Auto-Complete (`#searchDOI`) and verify every value.

## Page and helpers

- Buttons: Exit Form `#cancel-button`, Save Draft `#draft`, Send to review `#send_final` (user only). /create stores nothing until Save Draft. Ask before Save Draft (it writes to TIP). "Autosaved HH:MM" is only a browser save.
- Load `scripts/tip_helpers.js` about 3 s after each page load. To avoid pasting the whole file every time, serve it once per session, `PY scripts/serve_file.py scripts/tip_helpers.js --port 8799 --minutes 120` (background), and load it with `(0, eval)(await (await fetch('http://127.0.0.1:8799/file')).text())`; if that fails (not yet tested on TIP), paste the file. Read state with `formState()` (filled values) and `missingRequired()` (required labels still empty); do not use read_page, get_page_text or screenshots on this form.
- Plain lists: `setSel(id, [exact option texts])`. Text: `setText(id, value)`. Server-search lists (authors `#find_author`, affiliations `orgSelect()`, project `#find_project`, sponsors `sponsorSelect()`, AGROVOC `#selectAgrovoc`): `s2pick(sel, query, text => test)`.
- IDs: `first_name01` title, `authorship_field`, `p_collection`, `p_type`, `c_author`, `abstract_field`, `date_publication` (YYYY-MM-DD), `languages`, `countries`, `regions`, `open_access`, `usage_rigth` (sic), `alliance_subject`, `impact_area_field`, `lever_field`, `portfolio_programs_accelerators`, `selectAgrovoc`, `selectAgrovocES`, `fileupload`.
- Authors: `findOrAdd("Surname, Firstname", institution)` reuses staff or External records before adding one. Directory names can differ ("Mendez Alzate, Andres Camilo"); match by email and tell the user.
- Files: `#fileupload` is outside the form and is sent on Save Draft. Up to 10 MB and inside the session folders: browser file upload. Otherwise, with the user's OK: `PY scripts/serve_file.py "<file>" --port 8765` in the background (127.0.0.1, one file, stops after 3 min), one port per file, then `attachServed([[8765, "name.pdf"], ...])`. Saving 12 MB takes about 60 s.
- Calls over 45 s: `runInBackground(() => ...)` and read `window.__job` later. After saving, open /CgspaceSubmission/update/<id> and run `verifyDraft(expectedBytes)`.

## Traps

- Selecting the project sets "contributes to a Science Program?" and ToC mapping to Yes. Run `noScienceProgram()` (if the user said no) right before every Save Draft or Send; otherwise saving fails with "Select the High Level Output...". TIP re-sets it on every reload.
- Science Program (CGIAR portfolio) is not the Lever (Alliance area, `lever_field`, filled from authors). Ask about the Science Program separately; never infer it.
- Affiliation "International Center for Tropical Agriculture" fills country Kenya: tell the user.
- Same-name sponsors in several countries (DFAT Ireland and Australia): pick the document's country.
- Peer review is disabled for Reports. Year needs a full date; if only a year is known, use the PDF creation date and say so.
- Infographics: collection "Posters, Presentations and Infographics", type "Infographic". Spanish is "Spanish, Castilian". Two language versions: one submission with both files and languages (user's choice once).
- AGROVOC may store the preferred label ("capacity development" becomes "Capacity building").
- Send to review: open each draft in its own tab, `noScienceProgram()`, `missingRequired()` must be empty, then the user clicks. "Similar Institutions Found" is not readable by script: guide from the user's screenshot; pick a general or Americas CIAT record, never "Compagnie Industrielle d'Applications Thermiques", same choice in every submission. Status then shows "Review Pending".

## Fields

E = extract from the document, A = ask, E/A = extract and confirm. * = required.

A. General: Title* E; Authors* E/A ("Surname, Firstname", publication order); Affiliations E/A; Authorship Types* A; Main Collection* E/A; Publication Type* E/A; Corresponding Author* A; Abstract E; Year* E; Online date E; Languages* E; Country, Region E; Member contact A.

B. Access and focus: Portfolio component type* A; Project A; Contributes to a Science Program?* A (known if a Program template was used); Primary Science Program, High Level Output, Indicator, Quantitative contribution* if it contributes A (never guess); Science Writing edited A; Impact or evaluative study?* A; Externally peer-reviewed?* A; Accessibility* A; Usage Rights* A; Sponsors E/A; Levers, Programs, Collections A (only if the user says); Subjects* (`alliance_subject`, 64 fixed terms) E/A, propose and let the user choose; SDGs auto from project, review; Impact Area A (accepted items help); Notes A; DOI, Preprint E.

C. AGROVOC English* E/A (propose, user confirms); AGROVOC Spanish E/A; Files (20 MB each; links have none).

D. Intellectual property A: owner (CIAT, Bioversity, both, third parties), legal restrictions, commercialization potential, further development.

E. Information Team: library only, do not fill. F. Share: optional, ask.
