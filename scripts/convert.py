#!/usr/bin/env python3
"""Cross-platform document helpers. Standard library only.

Commands:
  to-docx <file> [--output out.docx]   Convert .doc, .rtf, .odt, .txt or .html to .docx
  preview <file.docx> [--outdir dir]    Make a PDF (or a PNG thumbnail on macOS) to check the result

Converters tried, in order:
  macOS    textutil (built in), then LibreOffice
  Windows  Microsoft Word through PowerShell (no extra install), then LibreOffice
  Linux    LibreOffice
If none is available, the script says so and the user saves the file as .docx by hand.
"""
import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys

SYSTEM = platform.system()  # "Darwin", "Windows", "Linux"


def find_soffice():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    candidates = []
    if SYSTEM == "Darwin":
        candidates = ["/Applications/LibreOffice.app/Contents/MacOS/soffice"]
    elif SYSTEM == "Windows":
        for base in (os.environ.get("ProgramFiles", r"C:\Program Files"),
                     os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
            candidates.append(os.path.join(base, "LibreOffice", "program", "soffice.exe"))
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def find_word_windows():
    if SYSTEM != "Windows":
        return None
    for base in (os.environ.get("ProgramFiles", r"C:\Program Files"),
                 os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
        hits = glob.glob(os.path.join(base, "Microsoft Office", "**", "WINWORD.EXE"), recursive=True)
        if hits:
            return hits[0]
    return None


def word_save_as(src, out, fmt):
    """Windows only: open src in Word through COM and save as out. fmt 16 = docx, 17 = pdf."""
    ps = shutil.which("powershell") or shutil.which("pwsh")
    if not ps:
        return False
    q = lambda p: os.path.abspath(p).replace("'", "''")
    script = ("$w = New-Object -ComObject Word.Application; $w.Visible = $false; "
              "try { $d = $w.Documents.Open('%s', $false, $true); $d.SaveAs2('%s', %d); $d.Close($false) } "
              "finally { $w.Quit() }" % (q(src), q(out), fmt))
    r = subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command", script],
                       capture_output=True, text=True)
    return r.returncode == 0 and os.path.exists(out)


def soffice_convert(src, outdir, target):
    so = find_soffice()
    if not so:
        return None
    r = subprocess.run([so, "--headless", "--convert-to", target, "--outdir", outdir, src],
                       capture_output=True, text=True)
    out = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + "." + target.split(":")[0])
    return out if r.returncode == 0 and os.path.exists(out) else None


def to_docx(src, output=None):
    src = os.path.abspath(src)
    out = os.path.abspath(output or os.path.splitext(src)[0] + ".docx")
    if out == src:
        sys.exit("The output would overwrite the input.")
    if SYSTEM == "Darwin" and shutil.which("textutil"):
        r = subprocess.run(["textutil", "-convert", "docx", src, "-output", out], capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(out):
            return out, "textutil"
    if SYSTEM == "Windows" and find_word_windows() and word_save_as(src, out, 16):
        return out, "Microsoft Word"
    res = soffice_convert(src, os.path.dirname(out), "docx")
    if res:
        if os.path.abspath(res) != out:
            shutil.move(res, out)
        return out, "LibreOffice"
    return None, None


def preview(src, outdir=None):
    src = os.path.abspath(src)
    outdir = os.path.abspath(outdir or os.path.dirname(src))
    os.makedirs(outdir, exist_ok=True)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + ".pdf")
    if SYSTEM == "Windows" and find_word_windows() and word_save_as(src, pdf, 17):
        return pdf, "Microsoft Word (PDF)"
    res = soffice_convert(src, outdir, "pdf")
    if res:
        return res, "LibreOffice (PDF)"
    if SYSTEM == "Darwin" and shutil.which("qlmanage"):
        subprocess.run(["qlmanage", "-t", "-s", "1200", "-o", outdir, src], capture_output=True)
        png = os.path.join(outdir, os.path.basename(src) + ".png")
        if os.path.exists(png):
            return png, "Quick Look (first page only, simplified rendering)"
    return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("to-docx")
    s.add_argument("file")
    s.add_argument("--output")
    s = sub.add_parser("preview")
    s.add_argument("file")
    s.add_argument("--outdir")
    a = ap.parse_args()
    if a.cmd == "to-docx":
        out, tool = to_docx(a.file, a.output)
        if not out:
            sys.exit("No converter available on this computer (%s). Ask the user to open the file in Word "
                     "or LibreOffice and save it as .docx, or see references/setup.md to install LibreOffice."
                     % SYSTEM)
        print("Converted with %s: %s" % (tool, out))
    else:
        out, tool = preview(a.file, a.outdir)
        if not out:
            print("No preview tool available on this computer (%s). Skip the visual check and ask the user "
                  "to open the file and look at it." % SYSTEM)
            return
        print("Preview made with %s: %s" % (tool, out))


if __name__ == "__main__":
    main()
