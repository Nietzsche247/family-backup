#!/usr/bin/env python3
"""WILSON MATTER - pass 2, 2026-07-29.
Adds the counsel note (txt + pdf), builds one bookmarked all-in-one PDF,
regenerates MANIFEST.txt by hashing everything present, rebuilds the zip.
Run after wilson_counsel_pdf.py."""
import hashlib, sys, zipfile
from pathlib import Path
sys.path.insert(0, r"C:\Users\aaron\clawd-shared")
from wilson_counsel_pdf import (OUT, OUT_E, OUT_I, OUT_A, ZIP, RUN, CAPTION,
                                EMLS, sha, make_doc, S_T, S_S, S_H, S_B, S_C)
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer
from pypdf import PdfWriter, PdfReader

NOTE_TXT = OUT / f"COUNSEL_NOTE_{RUN}.txt"
NOTE_PDF = OUT / f"COUNSEL_NOTE_{RUN}.pdf"
ALL = OUT / f"WILSON_ALL_IN_ONE_{RUN}.pdf"

SECTIONS = [
 ("1. WHAT YOU ASKED FOR, AND WHERE IT IS", [
  "The eight .eml sources you could not open are rendered as PDF in "
  "emails_as_pdf\\. The image request is addressed in images\\.",
  "If folders are inconvenient, WILSON_ALL_IN_ONE_" + RUN + ".pdf contains "
  "the whole set in one bookmarked document: this note, then each email in "
  "source order, then the image exhibits. Nothing else needs to be opened.",
  "The .eml files remain the evidence and are retained unaltered. Each PDF "
  "carries its native filename and native SHA-256 on its first page and the "
  "complete verbatim header block at the end, so any rendering can be checked "
  "against the native it came from."]),
 ("2. WHY TWO OF THE EMAILS LOOK EMPTY", [
  "SRC-0121 has a 37-character body: \"David, Please see attached document.\" "
  "SRC-0102 has a 77-character body. In both, the substance was attached "
  "rather than typed, so a rendering of the email alone shows almost nothing. "
  "This is a property of the originals, not of the conversion.",
  "Every attachment is extracted to attachments\\. Most were already produced "
  "under their own source numbers, so in several cases you already have the "
  "document and only the link between the two was missing. The cross-reference "
  "is in README_FOR_COUNSEL.txt and in the manifest."]),
 ("3. THE IMAGE REQUEST", [
  "SRC-0123_img_6.png is 796 x 25 pixels and 468 bytes. It is a near-blank "
  "narrow strip, consistent with a spacer or divider element in the email "
  "rather than content. There is nothing in it to enlarge, which is likely why "
  "it would not display or print usefully.",
  "Because the intended exhibit may have been a different image, all seven "
  "images extracted from SRC-0123 are included, each on its own page at "
  "maximum page fit, with native pixel dimensions printed on the page. They "
  "can be referred to by number. The native PNGs are included alongside.",
  "One note on a neighbouring file: SRC-0123_img_5.png is also a narrow strip "
  "but does contain a readable line of text, so it should not be skipped on "
  "the assumption that narrow means blank.",
  "No enhancement, sharpening, interpolation or upscaling has been applied to "
  "any image, and none will be applied without your instruction. Interpolation "
  "would add no detail that is not in the native, and an enhanced enlargement "
  "invites argument about the enlargement itself. Where a native is too small "
  "to read, that is a fact about the native and is stated as one."]),
 ("4. ONE ITEM IN THE SET YOU SHOULD BE AWARE OF", [
  "Among the attachments to SRC-0102 is a file named "
  "\"Garrahan _ REVISED DESIGN IMAGES - 10_23_23.pdf\", 482,219 bytes. It "
  "concerns a client other than Wilson.",
  "It is present because it was attached to an email Omni sent to Wilson on "
  "2025-09-10. Wilson has therefore held it since that date. It is included "
  "here as part of the native as sent; removing an attachment from an email we "
  "sent would alter the document.",
  "It has not been assigned its own source number. We will assign one unless "
  "you direct otherwise. Flagged in case its presence in the set, or the fact "
  "that it concerns a third party, bears on how you want it handled. We make "
  "no determination either way.",
  "Context on the circumstances of that transmission is available from Michael "
  "Baker directly. It is not recorded in the workbook because it is not yet "
  "supported by a document, and the workbook does not carry unsourced "
  "accounts as record."]),
 ("5. WHICH COPY GOVERNS", [
  "The copy of Wilson.xlsx held here is the working copy of record. Anything "
  "sent to you is a dated snapshot: this set is WILSON_counsel_pdf_" + RUN +
  ".zip, and every file in it is hashed in MANIFEST.txt. A file that does not "
  "match those hashes did not come from us in that form.",
  "If you have annotated or edited your copy of the workbook, please send the "
  "comments, a list, or a redline rather than the edited file. Entries are made "
  "on this side against preserved sources, which is what keeps the "
  "single-entry rule and the audits meaningful. Two independently edited "
  "workbooks would leave neither authoritative.",
  "Counsel Status remains UNREVIEWED and record state remains DRAFT "
  "throughout, by design. Nothing in this set makes a legal determination."]),
 ("6. AVAILABLE ON REQUEST", [
  "Any attachment as a standalone file. The native .eml for any source. Any "
  "document in a different format or reorganised differently. The full "
  "SRC-0130 Google Vault container, approximately 1.39 GB, by secure transfer.",
  "If any file in this set still will not open, say which one and it will be "
  "reissued in whatever format is easiest."])]


def build_note():
    with open(NOTE_TXT, "w", encoding="utf-8") as fh:
        fh.write(f"WILSON MATTER - NOTE ACCOMPANYING THE {RUN} CONVERSION SET\n")
        fh.write(f"{CAPTION}\n")
        fh.write("Prepared by Omni Pool Builders & Design LLC.\n")
        fh.write("Clerical work product. No legal determinations. UNREVIEWED.\n")
        fh.write("=" * 72 + "\n")
        for head, paras in SECTIONS:
            fh.write(f"\n{head}\n")
            for p in paras:
                words, line = p.split(), ""
                for w in words:
                    if len(line) + len(w) + 1 > 72:
                        fh.write(line + "\n")
                        line = w
                    else:
                        line = f"{line} {w}".strip()
                fh.write(line + "\n\n")

    doc = make_doc(NOTE_PDF, "NOTE", f"COUNSEL_NOTE_{RUN}")
    fl = [Paragraph(f"Wilson matter &mdash; note accompanying the {RUN} "
                    f"conversion set", S_T),
          Paragraph(CAPTION, S_S),
          Paragraph("Prepared by Omni Pool Builders &amp; Design LLC. Clerical "
                    "work product. No legal determinations are made in this "
                    "document. Counsel Status UNREVIEWED throughout.", S_S),
          Spacer(1, 12)]
    for head, paras in SECTIONS:
        fl.append(Paragraph(head, S_H))
        for p in paras:
            fl.append(Paragraph(p.replace("&", "&amp;"), S_B))
            fl.append(Spacer(1, 5))
    doc.build(fl)
    print(f"WROTE  {NOTE_TXT.name}")
    print(f"WROTE  {NOTE_PDF.name}")


def build_all_in_one():
    parts = [(f"Note to counsel, {RUN}", NOTE_PDF)]
    for src, name in EMLS:
        p = OUT_E / f"{Path(name).stem}.pdf"
        if p.is_file():
            parts.append((f"{src}  {Path(name).stem[9:]}", p))
    ip = OUT_I / f"SRC-0123_IMAGES_PRINT_{RUN}.pdf"
    if ip.is_file():
        parts.append(("SRC-0123  image exhibits, all seven", ip))

    w = PdfWriter()
    for title, p in parts:
        start = len(w.pages)
        for pg in PdfReader(str(p)).pages:
            w.add_page(pg)
        w.add_outline_item(title, start)
    with open(ALL, "wb") as fh:
        w.write(fh)
    print(f"WROTE  {ALL.name}  ({len(w.pages)} pages, "
          f"{len(parts)} bookmarked sections)")
    return len(w.pages)


def rebuild_manifest():
    files = sorted(p for p in OUT.rglob("*")
                   if p.is_file() and p.name != "MANIFEST.txt")
    mp = OUT / "MANIFEST.txt"
    with open(mp, "w", encoding="utf-8") as fh:
        fh.write(f"WILSON COUNSEL SET - MANIFEST - {RUN}\n{CAPTION}\n")
        fh.write("Every file in this package, with its SHA-256.\n")
        fh.write("=" * 72 + "\n\n")
        for p in files:
            fh.write(f"{p.relative_to(OUT).as_posix()}\n")
            fh.write(f"    bytes : {p.stat().st_size:,}\n")
            fh.write(f"    sha256: {sha(p)}\n\n")
        fh.write(f"files: {len(files)}\n")
    print(f"WROTE  MANIFEST.txt  ({len(files)} files hashed)")


def rebuild_zip():
    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(OUT))
    bad = zipfile.ZipFile(ZIP).testzip()
    print(f"\nZip         : {ZIP}")
    print(f"Zip SHA-256 : {sha(ZIP)}")
    print(f"Zip bytes   : {ZIP.stat().st_size:,}")
    print(f"Zip integrity bad-file check: {bad}")


if __name__ == "__main__":
    build_note()
    pages = build_all_in_one()
    rebuild_manifest()
    rebuild_zip()
    print(f"\nSingle file to send if they want only one: "
          f"{ALL.name}  ({pages} pages)")
