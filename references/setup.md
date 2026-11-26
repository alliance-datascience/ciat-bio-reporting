# Setup check

Run this once per session, before the first task, and only for what the user needs (formatting, TIP, or both).

## 1. Is Python there?

Try, in this order, until one answers with a version:

```bash
python3 --version      # macOS, Linux
py --version           # Windows
python --version       # Windows, other setups
```

Use whichever answers for every later command (`PY` below). If none answers, Python is missing: go to step 3.

## 2. Run the check

```bash
PY scripts/check_setup.py --need format|tip|both
```

It prints OK, MISSING, OPTIONAL or CHECK per item and, for anything missing, the install command for this operating system. Exit code 1 means something required is missing.

For TIP, also check the browser yourself: call the Claude in Chrome tab tool. If it fails, the extension is missing or not connected. Then open https://tip.alliance.cgiar.org/Dashboard: if it asks for a login, the user signs in themselves.

## What is required

| Item | Needed for | Required? | Admin rights usually needed? |
|---|---|---|---|
| Python 3.8 or newer | Formatting | Yes | Often yes on managed computers |
| python-docx 1.0 or newer | Formatting | Yes | No (`--user` install), unless pip is blocked |
| Shortcut to the CGIAR "2. Word templates" folder in OneDrive | Formatting with CGIAR templates | Yes | No: the user does it in SharePoint |
| A converter: Microsoft Word (Windows), textutil (macOS, built in) or LibreOffice | Converting .doc/.rtf/.odt and making previews | Optional | Only for installing LibreOffice |
| Google Chrome with the Claude in Chrome extension | TIP | Yes | Sometimes, depending on IT policy |
| Access to TIP with the user's CGIAR account | TIP | Yes | No |

## 3. If something is missing

Items that need no admin rights (the OneDrive shortcut, signing in to TIP): explain to the user how to do it and continue.

For software, ask with AskUserQuestion: "Do you have administrator rights on this computer?"
- Yes, help me install: show the exact install command from check_setup.py, run it after the user approves, and run the check again.
- I'm not sure: try first the installs that do not need admin (`PY -m pip install --user python-docx`). If that or anything else fails with a permission or policy error, go to the email.
- No: write the email below.

Never try to work around IT restrictions (no portable installs from unofficial sources, no disabling security settings).

## 4. Email to IT

Write the draft in the user's language, filled in with what check_setup.py reported as missing and the operating system it printed. Show it in the chat for the user to copy and send. Claude does not send it.

```
To: Alliance-IT Support (Alliance Bioversity-CIAT) <Alliance-ITsupport@cgiar.org>
Subject: Software installation request: <list of missing items>

Dear IT Support team,

I would like to request the installation of the following software on my work computer, which I need to prepare and submit knowledge products (reports, briefs and other outputs) to TIP and CGSpace using the official CGIAR templates:

- <item 1, e.g. Python 3.12 (python.org)>
- <item 2, e.g. the python-docx library for Python>
- <item 3, e.g. LibreOffice (optional, to convert older Word files)>

Computer details:
- Operating system: <e.g. Windows 11 / macOS 15>
- Computer name or asset tag: <the user fills this in>

I do not have administrator rights on this computer, so I cannot install them myself.

Thank you very much,
<Name>
<Unit / team>
```

If the user prefers, offer a mailto link with the subject filled in, so it opens in their email program.

Once IT installs the software, run step 2 again before continuing.
