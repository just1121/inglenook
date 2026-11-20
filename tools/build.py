#!/usr/bin/env python3
"""Rebuild the flipbook page images from a PDF.

Usage:
    python3 tools/build.py /path/to/brochure.pdf [--single-file out.html]

Writes pages/pN-1400.jpg, pages/pN-2800.jpg, pages/pN-thumb.jpg and
pages/manifest.js next to index.html. Never touches book.js.

Rendering uses pdftoppm (Poppler) if it is on PATH, otherwise PyMuPDF
if it is installed. JPEG encoding uses Pillow if available, otherwise
pdftoppm's own JPEG output. Works with Python 3.9+ and the standard
library; Pillow and PyMuPDF are optional.
"""

import argparse
import base64
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "pages")

SIZES = {"2800": 2800, "1400": 1400, "thumb": 320}
# Byte budgets per encoded page. Quality steps down until a page fits.
BUDGET = {"2800": 900_000, "1400": 350_000, "thumb": 40_000}
QUALITY_STEPS = {
    "2800": [90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70],
    "1400": [90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70],
    "thumb": [80, 76, 72, 68],
}

try:
    from PIL import Image  # type: ignore
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

try:
    import fitz  # type: ignore  # PyMuPDF
    HAVE_FITZ = True
except Exception:
    HAVE_FITZ = False

HAVE_PDFTOPPM = shutil.which("pdftoppm") is not None
HAVE_PDFINFO = shutil.which("pdfinfo") is not None


def die(msg):
    print("error: " + msg, file=sys.stderr)
    sys.exit(1)


def install_hint():
    return (
        "No PDF renderer found. Install Poppler, which provides pdftoppm:\n"
        "  macOS:          brew install poppler\n"
        "  Debian/Ubuntu:  sudo apt install poppler-utils\n"
        "or install PyMuPDF:  python3 -m pip install pymupdf\n"
        "Pillow is recommended for better JPEGs:  python3 -m pip install pillow"
    )


def run(cmd):
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True).stdout


def pdf_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


# ---------------------------------------------------------------- page info

def page_info_poppler(pdf, tmp):
    """Return (count, [(w_pt, h_pt), ...])."""
    if HAVE_PDFINFO:
        out = run(["pdfinfo", pdf])
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        if m:
            n = int(m.group(1))
            out = run(["pdfinfo", "-f", "1", "-l", str(n), pdf])
            sizes = [(float(a), float(b)) for a, b in
                     re.findall(r"^Page\s+\d+\s+size:\s+([\d.]+)\s+x\s+([\d.]+)", out, re.M)]
            if len(sizes) == n:
                return n, sizes
    # Fallback: a 72 dpi render gives the size in points.
    d = os.path.join(tmp, "info")
    os.makedirs(d, exist_ok=True)
    run(["pdftoppm", "-r", "72", "-png", pdf, os.path.join(d, "i")])
    files = sorted(os.listdir(d), key=lambda s: int(re.findall(r"\d+", s)[-1]))
    sizes = [png_size(os.path.join(d, f)) for f in files]
    return len(files), [(float(w), float(h)) for w, h in sizes]


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    import struct
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def page_info_fitz(pdf):
    doc = fitz.open(pdf)
    sizes = [(p.rect.width, p.rect.height) for p in doc]
    return len(sizes), sizes


# ---------------------------------------------------------------- rendering

def render_png(pdf, page, width, tmp):
    """Render one page to a PNG exactly `width` px wide, return its path."""
    out = os.path.join(tmp, "r%d-%d" % (page, width))
    if HAVE_PDFTOPPM:
        run(["pdftoppm", "-f", str(page), "-l", str(page), "-singlefile",
             "-png", "-scale-to-x", str(width), "-scale-to-y", "-1",
             "-aa", "yes", "-aaVector", "yes", pdf, out])
        return out + ".png"
    doc = fitz.open(pdf)
    p = doc[page - 1]
    zoom = width / p.rect.width
    pix = p.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    pix.save(out + ".png")
    return out + ".png"


def encode_pillow(img, key):
    """Encode with the highest quality step that fits the budget."""
    data = b""
    for q in QUALITY_STEPS[key]:
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=q, progressive=True, optimize=True,
                 subsampling=0)
        data = buf.getvalue()
        if len(data) <= BUDGET[key]:
            return data, q
    return data, QUALITY_STEPS[key][-1]


def encode_pdftoppm(pdf, page, width, key, tmp):
    """Fallback without Pillow: let pdftoppm write the JPEG directly."""
    out = os.path.join(tmp, "j%d-%s" % (page, key))
    data, q = b"", 0
    for q in QUALITY_STEPS[key]:
        run(["pdftoppm", "-f", str(page), "-l", str(page), "-singlefile",
             "-jpeg", "-jpegopt", "quality=%d,progressive=y,optimize=y" % q,
             "-scale-to-x", str(width), "-scale-to-y", "-1", pdf, out])
        with open(out + ".jpg", "rb") as f:
            data = f.read()
        if len(data) <= BUDGET[key]:
            break
    return data, q


def build_pages(pdf, tmp):
    if HAVE_PDFTOPPM:
        count, sizes = page_info_poppler(pdf, tmp)
    elif HAVE_FITZ:
        count, sizes = page_info_fitz(pdf)
    else:
        die(install_hint())
    if count < 1:
        die("the PDF has no pages")

    if not HAVE_PIL:
        print("note: Pillow not found, using pdftoppm JPEG output "
              "(python3 -m pip install pillow for better results)")
        if not HAVE_PDFTOPPM:
            die("PyMuPDF rendering needs Pillow for JPEG encoding.\n" + install_hint())

    os.makedirs(PAGES_DIR, exist_ok=True)
    report = []
    for n in range(1, count + 1):
        row = [n]
        if HAVE_PIL:
            src = Image.open(render_png(pdf, n, SIZES["2800"], tmp)).convert("RGB")
            for key in ("2800", "1400", "thumb"):
                w = SIZES[key]
                img = src if src.width == w else src.resize(
                    (w, max(1, round(src.height * w / src.width))), Image.LANCZOS)
                data, q = encode_pillow(img, key)
                write(os.path.join(PAGES_DIR, "p%d-%s.jpg" % (n, key)), data)
                row.append((key, len(data), q))
        else:
            for key in ("2800", "1400", "thumb"):
                data, q = encode_pdftoppm(pdf, n, SIZES[key], key, tmp)
                write(os.path.join(PAGES_DIR, "p%d-%s.jpg" % (n, key)), data)
                row.append((key, len(data), q))
        report.append(row)
        print("page %d: " % n + ", ".join(
            "%s %d KB q%d" % (k, b // 1024, q) for k, b, q in row[1:]))

    # Remove images left over from a longer previous PDF.
    for f in os.listdir(PAGES_DIR):
        m = re.match(r"p(\d+)-(1400|2800|thumb)\.jpg$", f)
        if m and int(m.group(1)) > count:
            os.remove(os.path.join(PAGES_DIR, f))
    return count, sizes


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


# ---------------------------------------------------------------- manifest

def write_manifest(count, sizes, version):
    w, h = sizes[0]
    manifest = {
        "pages": count,
        "width": round(w, 3),
        "height": round(h, 3),
        "version": version,
    }
    if any(abs(a - w) > 0.5 or abs(b - h) > 0.5 for a, b in sizes):
        print("warning: pages have different sizes; the viewer uses page 1's size for all pages")
    js = ("/* Generated by tools/build.py. Do not edit by hand. */\n"
          "window.FLIPBOOK_MANIFEST = " + json.dumps(manifest, indent=2) + ";\n")
    with open(os.path.join(PAGES_DIR, "manifest.js"), "w", encoding="utf-8") as f:
        f.write(js)
    return js


def check_book_js(count):
    path = os.path.join(ROOT, "book.js")
    if not os.path.exists(path):
        print("warning: book.js not found next to index.html")
        return
    with open(path, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)  # ignore comments
    entries = len(re.findall(r"^\s*alt\s*:", text, re.M))
    if entries != count:
        print("")
        print("WARNING: the PDF has %d pages but book.js describes %d." % (count, entries))
        print("         Update the alt text and transcripts in book.js so every")
        print("         page has one entry, in order.")
        print("")


# ---------------------------------------------------------------- single file

def script_safe(js):
    return js.replace("</script", "<\\/script").replace("<!--", "<\\!--")


def write_single_file(out_path, count, manifest_js):
    with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
        html = f.read()
    with open(os.path.join(ROOT, "book.js"), encoding="utf-8") as f:
        book_js = f.read()
    images = {}
    for n in range(1, count + 1):
        with open(os.path.join(PAGES_DIR, "p%d-1400.jpg" % n), "rb") as f:
            images[str(n)] = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("ascii")
    inline_js = "window.FLIPBOOK_INLINE = " + json.dumps({"images": images}) + ";\n"

    tags = {
        '<script src="book.js"></script>': book_js,
        '<script src="pages/manifest.js"></script>': manifest_js + inline_js,
    }
    for tag, js in tags.items():
        if tag not in html:
            die("index.html is missing the tag %s" % tag)
        html = html.replace(tag, "<script>\n" + script_safe(js) + "</script>", 1)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s (%d KB)" % (out_path, os.path.getsize(out_path) // 1024))


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Rebuild flipbook page images from a PDF.")
    ap.add_argument("pdf", help="path to the brochure PDF")
    ap.add_argument("--single-file", metavar="OUT.html",
                    help="also write a self-contained preview HTML file")
    args = ap.parse_args()

    pdf = os.path.abspath(args.pdf)
    if not os.path.isfile(pdf):
        die("PDF not found: %s" % args.pdf)
    if not HAVE_PDFTOPPM and not HAVE_FITZ:
        die(install_hint())

    version = pdf_hash(pdf)
    with tempfile.TemporaryDirectory(prefix="flipbook-") as tmp:
        count, sizes = build_pages(pdf, tmp)
    manifest_js = write_manifest(count, sizes, version)
    print("wrote pages/manifest.js: %d pages, %.0f x %.0f pt, version %s"
          % (count, sizes[0][0], sizes[0][1], version))
    check_book_js(count)
    if args.single_file:
        write_single_file(os.path.abspath(args.single_file), count, manifest_js)


if __name__ == "__main__":
    main()
