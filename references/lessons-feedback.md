# Sharing lessons learned with the maintainer

At the end of every session that used this skill (formatting, TIP or both, also when it ended early or with errors), ask the user, with AskUserQuestion, whether they approve sharing the lessons learned in this session with the skill's maintainer, Lizeth Llanos, so the skill improves for everyone. Options:

1. By email (Claude drafts it, the user sends it).
2. As a GitHub issue in https://github.com/alliance-datascience/ciat-bio-reporting (public).
3. Not now.

Ask once, at the end. If the user says "not now", do not insist.

## What to write

Before asking, draft the lessons from this session. Keep them short and useful for fixing the skill:

- What failed or was confusing, and the workaround that worked.
- TIP fields, errors or dialogs the skill did not know about (field label and error text as shown).
- Template quirks (template name, what went wrong).
- What had to be done by hand.
- Operating system, and whether Microsoft Word or LibreOffice was used.
- If everything worked, say so in one line; that is useful too.

Never include: the content of the user's documents, names or emails of authors or colleagues, TIP submission IDs, project codes, file paths that contain user names, passwords, tokens or keys. The GitHub repository is public.

Show the user the full text and wait for their OK before sending or creating anything. They may edit or remove anything.

## By email

Draft only; the user sends it. Claude never sends it.

```
To: Lizeth Llanos <l.llanos@cgiar.org>
Subject: ciat-bio-reporting: lessons learned from a session

Hi Lizeth,

Lessons learned using ciat-bio-reporting on <date> (<what was done: formatting / TIP submission / both>):

1. ...
2. ...

Environment: <Windows / macOS / Linux>, <Word / LibreOffice>.
```

## As a GitHub issue

Only after the user approves the exact text. Save the text to a temporary file and run:

```
gh issue create --repo alliance-datascience/ciat-bio-reporting --title "Lessons learned: <short summary>" --body-file <file>
```

This needs the GitHub CLI (`gh`) signed in with the user's account. If it is not available, give the user the link https://github.com/alliance-datascience/ciat-bio-reporting/issues/new and the text to paste. Tell the user the issue will be public.
