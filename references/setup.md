# Missing requirements

Read only when `check_setup.py` reports MISSING. If no `python3`, `py` or `python --version` answers, Python is missing. If several Pythons exist (macOS: Homebrew and the system one), the skill uses the first `python3` on the PATH; install python-docx for that one (`python3 -c "import sys; print(sys.executable)"`).

| Item | For | Admin rights? |
|---|---|---|
| Python 3.8+ | Formatting | Often, on managed computers |
| python-docx 1.0+ | Formatting | No: `PY -m pip install --user python-docx`. Homebrew Python (macOS) and recent Linux refuse it ("externally-managed-environment", PEP 668): add `--break-system-packages`; with `--user` it installs only in the user's folder, not in the system packages. check_setup.py prints the right command |
| Microsoft Word, textutil (macOS) or LibreOffice | Conversion, PDF | Only to install LibreOffice |
| Chrome with Claude in Chrome | TIP | Sometimes |
| TIP access (CGIAR account) | TIP | No |

TIP: if the Chrome tab tool fails, the extension is missing or disconnected. If TIP asks to sign in, the user does it.

Ask with AskUserQuestion: "Do you have administrator rights on this computer?"
- Yes: show the install command check_setup.py printed, run it after the user approves, check again.
- Not sure: try the `--user` installs; on a permission or policy error, go to the email.
- No: the email.

Never work around IT restrictions.

Email (draft in the user's language, with the missing items and the OS check_setup.py printed; the user sends it, Claude never does; offer a mailto link if they prefer):

```
To: Alliance-IT Support (Alliance Bioversity-CIAT) <Alliance-ITsupport@cgiar.org>
Subject: Software installation request: <items>

Dear IT Support team,

I would like to request the installation of the following software on my work computer. I need it to prepare and submit knowledge products to TIP and CGSpace with the official CGIAR templates:

- <item, e.g. Python 3.12 (python.org)>
- <item, e.g. the python-docx library for Python>

Operating system: <OS>
Computer name or asset tag: <fill in>

I do not have administrator rights, so I cannot install them myself.

Thank you very much,
<Name>
```
