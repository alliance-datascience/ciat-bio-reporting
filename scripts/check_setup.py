#!/usr/bin/env python3
"""Check whether this computer has what the ciat-bio-reporting skill needs. Standard library only.

Usage:  check_setup.py [--need format|tip|both]

Prints one line per requirement (OK, MISSING or OPTIONAL) and, for anything missing, the
install command for this operating system. Exit code 0 if every required item is present,
1 otherwise. Chrome and the Claude in Chrome extension (needed for TIP) cannot be checked
from here: the skill checks them by calling the browser tools.
"""
import argparse
import glob
import os
import platform
import shutil
import sys

SYSTEM = platform.system()
PY = "py" if SYSTEM == "Windows" else "python3"
MIN_PY = (3, 8)


def python_docx():
    try:
        import docx  # noqa: F401
    except ImportError:
        return None
    try:
        from importlib.metadata import version
        return version("python-docx")
    except Exception:
        return getattr(sys.modules.get("docx"), "__version__", "unknown")


def onedrive_roots():
    roots = []
    home = os.path.expanduser("~")
    if SYSTEM == "Darwin":
        roots += glob.glob(os.path.join(home, "Library", "CloudStorage", "OneDrive*"))
    for var in ("OneDriveCommercial", "OneDrive", "OneDriveConsumer"):
        if os.environ.get(var):
            roots.append(os.environ[var])
    roots += glob.glob(os.path.join(home, "OneDrive*"))
    seen, out = set(), []
    for r in roots:
        r = os.path.abspath(r)
        if r not in seen and os.path.isdir(r):
            seen.add(r)
            out.append(r)
    return out


def find_templates(max_depth=5):
    """Folder that holds the Report-<Program> templates, or None. Does not download cloud files."""
    for root in onedrive_roots():
        base_depth = root.rstrip(os.sep).count(os.sep)
        for dirpath, dirnames, filenames in os.walk(root):
            if dirpath.count(os.sep) - base_depth >= max_depth:
                dirnames[:] = []
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "node_modules"]
            if any(f.startswith("Report-") and f.lower().endswith((".dotx", ".docx")) for f in filenames) \
                    and "word templates" in dirpath.lower():
                return dirpath
    return None


def converter():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import convert
    if SYSTEM == "Darwin" and shutil.which("textutil"):
        return "textutil (built in)"
    if convert.find_word_windows():
        return "Microsoft Word"
    if convert.find_soffice():
        return "LibreOffice"
    return None


def install_hint(item):
    hints = {
        "python": {
            "Windows": "winget install Python.Python.3.12   (or the python.org installer, option 'Install for me only')",
            "Darwin": "xcode-select --install   (or the python.org installer)",
            "Linux": "sudo apt install python3 python3-pip",
        },
        "python-docx": {
            "Windows": "py -m pip install --user python-docx",
            "Darwin": "python3 -m pip install --user python-docx",
            "Linux": "python3 -m pip install --user python-docx",
        },
        "converter": {
            "Windows": "Microsoft Word is usually installed; otherwise: winget install TheDocumentFoundation.LibreOffice",
            "Darwin": "textutil is built in; for previews: brew install --cask libreoffice",
            "Linux": "sudo apt install libreoffice-writer",
        },
    }
    return hints[item].get(SYSTEM, hints[item]["Linux"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--need", choices=["format", "tip", "both"], default="both")
    a = ap.parse_args()

    rows, missing = [], []
    print("System: %s %s, Python %s" % (SYSTEM, platform.release(), platform.python_version()))

    ok_py = sys.version_info[:2] >= MIN_PY
    rows.append(("OK" if ok_py else "MISSING", "Python >= %d.%d" % MIN_PY, platform.python_version()))
    if not ok_py:
        missing.append(("Python %d.%d or newer" % MIN_PY, install_hint("python")))

    if a.need in ("format", "both"):
        v = python_docx()
        good = v is not None and (v == "unknown" or int(v.split(".")[0]) >= 1)
        rows.append(("OK" if good else "MISSING", "python-docx >= 1.0", v or "not installed"))
        if not good:
            missing.append(("python-docx", install_hint("python-docx")))

        t = find_templates()
        rows.append(("OK" if t else "MISSING", "CGIAR Word templates in OneDrive", t or "not found"))
        if not t:
            missing.append(("Shortcut to the CGIAR '2. Word templates' folder in OneDrive",
                            "No install needed: open https://cgiar.sharepoint.com/sites/My-CGIAR/SOCOMMS/"
                            "Brand%20Assets/Final%20Assets/2.%20Word%20templates and click 'Add shortcut to My files'"))

        c = converter()
        rows.append(("OK" if c else "OPTIONAL", "Converter for .doc/.rtf/.odt and previews",
                     c or "none (" + install_hint("converter") + ")"))

    if a.need in ("tip", "both"):
        rows.append(("CHECK", "Google Chrome + Claude in Chrome extension", "checked by the skill"))
        rows.append(("CHECK", "TIP access (tip.alliance.cgiar.org, CGIAR account)", "checked by the skill"))

    for status, item, detail in rows:
        print("%-8s %-48s %s" % (status, item, detail))
    if missing:
        print("\nMissing:")
        for item, hint in missing:
            print("- %s\n    %s" % (item, hint))
        sys.exit(1)
    print("\nEverything required is in place.")


if __name__ == "__main__":
    main()
