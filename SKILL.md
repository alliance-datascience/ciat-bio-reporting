---
name: ciat-bio-reporting
description: Knowledge-product assistant for Alliance of Bioversity International and CIAT staff. Formats reports (Word, Markdown and others) with the official CGIAR Science Program or Accelerator Word template, or with another project's template, and guides submission to the Alliance TIP platform (tip.alliance.cgiar.org) of any output - reports, briefs, presentations, platforms, digital tools, links, repositories, software, datasets. Fills in the TIP form and leaves the final submit click to the user. Trigger on "format this report", "apply the Climate Action template", "put this in the Science Program template", "submit to TIP", "upload to CGSpace", "I need to report this output", "submit a repository / platform to TIP", /ciat-bio-reporting. ES - "formatea este reporte", "ponlo en la plantilla del Science Program", "súbelo a TIP", "subir a CGSpace". FR - "mettre en forme ce rapport", "soumettre à TIP".
---

# TIP reporting assistant

Guide the user according to what they bring. Do not assume everything is a report, or that everything belongs to a Science Program. Ask only what the material does not answer, and reuse each answer in later steps.

Reply in the language the user writes in. These instructions, the references and the script are in English so colleagues in any country can maintain them.

When there are several valid options (template, back page, TIP route, numbering), show them with AskUserQuestion and let the user choose. Do not choose for them.

## Non-negotiable rules

- In TIP, Claude fills in the form and shows the summary. The user clicks the final submit button. Never click it yourself, even if asked.
- TIP uses the user's own session in their Chrome. Never type passwords; if TIP asks to sign in, ask the user to do it.
- CGSpace only accepts final or published products. If the material is a draft, say so before going further.
- Do not invent metadata. Anything not in the document and not stated by the user is asked.
- Do not upload or share files outside TIP without explicit permission.

This skill works on Windows, macOS and Linux. Use the scripts in `scripts/` instead of operating-system-specific tools, and call Python as `python3` on macOS and Linux, `py` (or `python`) on Windows.

## Step 0. What do you need?

Ask with AskUserQuestion, unless the request already says it:
1. Format a document.
2. Submit something to TIP.
3. Both: format, then submit.

## Step 0b. Check the requirements

Before the first task of the session, follow [references/setup.md](references/setup.md) for what the user needs (formatting, TIP or both). If something is missing, ask whether they have administrator rights on the computer: if yes, help them install it; if not, give them the draft email to Alliance IT Support. Do not continue with a task whose requirements are missing.

## Step 1. What kind of output is it?

Read [references/tip-routes.md](references/tip-routes.md). The output type decides whether formatting applies and which TIP route to use. If the user brings a link or a repository, there is no formatting: go to Step 3.

## Step 2. Formatting (written documents only)

Read [references/formatting.md](references/formatting.md) and follow it. In short:

1. Is it already final (PDF or final Word)? If yes, go to Step 3.
2. Is it from a Science Program or Accelerator, or from another project?
   - Science Program or Accelerator: ask which one (list in [references/templates.md](references/templates.md)) and use its template. Download only that template, with the user's permission, as templates.md explains.
   - Another project: ask whether they have the project's or donor's template. If yes, ask them to share it. If not, show the general template options from references/templates.md and let them choose.
3. Run `scripts/format_report.py` and check the result with its `check` command.
4. Deliver the Word file and ask the user to review it. Do not make the PDF before they approve the Word file.
5. When they approve it, make the PDF with `scripts/convert.py to-pdf` (Word updates the table of contents first), look at the first pages, and ask whether they want to submit the PDF to TIP. TIP receives the PDF, not the Word file.

## Step 3. Submit to TIP

Read [references/tip-cgspace.md](references/tip-cgspace.md) for the CGSpace route. The other routes (Dataverse, Innovation Dev, Capacity Sharing, OICR, Policy Change) are not mapped yet: open the route in Chrome, read the fields with JavaScript without creating drafts, and guide the user step by step with what you see.

1. Extract everything you can from the document or link. For long documents, delegate the extraction to a subagent (Agent) and ask it to return only the fields listed in tip-cgspace.md, each with the quote it came from.
2. Ask for what is missing, grouped in a single AskUserQuestion round when the options are closed.
3. Show the user the full table of what you will fill in and wait for their go-ahead.
4. Fill in the form in Chrome. When done, show the summary and tell the user which button to click to submit.
5. Remind them of TIP's internal deadline if it applies (see tip-cgspace.md).

## Step 4. Share lessons learned (always, at the end)

At the end of every session that used this skill, even if it ended early or with errors, follow [references/lessons-feedback.md](references/lessons-feedback.md): draft the lessons learned (no personal data, no document content, no IDs) and ask whether the user approves sharing them with the maintainer by email or as a GitHub issue. Nothing is sent without their OK on the exact text; emails are only drafted.
