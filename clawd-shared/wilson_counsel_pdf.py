#!/usr/bin/env python3
"""WILSON MATTER - counsel PDF conversion pass, 2026-07-29.
Natives opened READ-ONLY. Every output hashed. No image enhancement."""
import email, email.policy, hashlib, html.parser, shutil, sys, zipfile
from datetime import datetime
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Preformatted, Spacer, Table, TableStyle,
                                Image as RLImage, PageBreak)
from PIL import Image as PILImage

ROOT = Path(r"C:\North_Star_Projects\WILSON_MATTER_WORKING_v1")
KEY = ROOT / "preserved" / "keydocs"
RUN = "2026-07-29"
OUT = ROOT / f"counsel_pdf_{RUN}"
OUT_E = OUT / "emails_as_pdf"
OUT_I = OUT / "images"
OUT_A = OUT / "attachments"
ZIP = ROOT / f"WILSON_counsel_pdf_{RUN}.zip"
CAPTION = ("Wilson v. Omni Pool Builders & Design LLC, et al.  |  "
           "Pima County Superior Court C20264565")
EMLS = [("SRC-0101", "SRC-0101_2025-09-10_Re-Tom.eml"),
        ("SRC-0102", "SRC-0102_2025-09-10_Tom.eml"),
        ("SRC-0103", "SRC-0103_2025-09-11_Re-Tom.eml"),
        ("SRC-0116", "SRC-0116_2026-07-16_Re-List-of-Open-Items.eml"),
        ("SRC-0117", "SRC-0117_2026-01-26_ROC-2026-00144.eml"),
        ("SRC-0118", "SRC-0118_2026-07-19_Wilson-cornered.eml"),
        ("SRC-0121", "SRC-0121_2026-07-17_Warranties-letter.eml"),
        ("SRC-0123", "SRC-0123_2026-07-20_payment-history-reply.eml")]
LOG = []


def log(m):
    line = f"{datetime.now():%H:%M:%S}  {m}"
    print(line)
    LOG.append(line)


def sha(p, chunk=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                return h.hexdigest()
            h.update(b)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class _Strip(html.parser.HTMLParser):
    SKIP = {"script", "style", "head"}
    BRK = {"p", "br", "div", "tr", "li", "h1", "h2", "h3", "h4", "table"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.o = []
        self.s = 0

    def handle_starttag(self, t, a):
        if t in self.SKIP:
            self.s += 1
        elif t in self.BRK:
            self.o.append("\n")
        elif t == "td":
            self.o.append("\t")

    def handle_endtag(self, t):
        if t in self.SKIP and self.s:
            self.s -= 1
        elif t in self.BRK:
            self.o.append("\n")

    def handle_data(self, d):
        if not self.s:
            self.o.append(d)

    def text(self):
        out, blank = [], 0
        for ln in "".join(self.o).splitlines():
            ln = ln.rstrip()
            if ln.strip():
                blank = 0
                out.append(ln)
            else:
                blank += 1
                if blank <= 1:
                    out.append("")
        return "\n".join(out).strip()


def html_to_text(s):
    p = _Strip()
    p.feed(s)
    p.close()
    return p.text()


SS = getSampleStyleSheet()
NAVY = colors.HexColor("#1B2A4A")
S_T = ParagraphStyle("t", parent=SS["Heading1"], fontSize=13, leading=16,
                     spaceAfter=2, textColor=NAVY)
S_S = ParagraphStyle("s", parent=SS["Normal"], fontSize=7.5, leading=10,
                     textColor=colors.HexColor("#555555"))
S_H = ParagraphStyle("h", parent=SS["Heading2"], fontSize=9.5, leading=12,
                     spaceBefore=10, spaceAfter=3, textColor=NAVY)
S_B = ParagraphStyle("b", parent=SS["Normal"], fontSize=9, leading=12.5)
S_M = ParagraphStyle("m", parent=SS["Normal"], fontName="Courier", fontSize=7,
                     leading=8.6)
S_C = ParagraphStyle("c", parent=SS["Normal"], fontSize=7.5, leading=10,
                     textColor=colors.HexColor("#555555"))


def _footer(src, native):
    def draw(c, d):
        c.saveState()
        c.setFont("Helvetica", 6.5)
        c.setFillColor(colors.HexColor("#777777"))
        c.drawString(0.6 * inch, 0.42 * inch,
                     f"{src}  |  native: {native}  |  {CAPTION}")
        c.drawRightString(letter[0] - 0.6 * inch, 0.42 * inch,
                          f"page {c.getPageNumber()}")
        c.setStrokeColor(colors.HexColor("#DDDDDD"))
        c.line(0.6 * inch, 0.58 * inch, letter[0] - 0.6 * inch, 0.58 * inch)
        c.restoreState()
    return draw


def make_doc(path, src, native):
    d = BaseDocTemplate(str(path), pagesize=letter, leftMargin=0.6 * inch,
                        rightMargin=0.6 * inch, topMargin=0.6 * inch,
                        bottomMargin=0.75 * inch, title=f"{src} - {native}",
                        author="Omni Pool Builders & Design LLC")
    f = Frame(d.leftMargin, d.bottomMargin, d.width, d.height, id="f")
    d.addPageTemplates([PageTemplate(id="p", frames=[f],
                                     onPage=_footer(src, native))])
    return d


def kv(rows):
    data = [[Paragraph(f"<b>{esc(k)}</b>", S_B), Paragraph(esc(v), S_B)]
            for k, v in rows]
    t = Table(data, colWidths=[1.15 * inch, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F6F8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def pick_body(msg):
    plain, htm = [], []
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        if part.get_content_maintype() == "multipart":
            continue
        if "attachment" in (part.get("Content-Disposition") or "").lower():
            continue
        try:
            pay = part.get_content()
        except Exception:
            pay = (part.get_payload(decode=True) or b"").decode("utf-8", "replace")
        if not isinstance(pay, str):
            continue
        if part.get_content_type() == "text/plain":
            plain.append(pay)
        elif part.get_content_type() == "text/html":
            htm.append(pay)
    if plain:
        return "\n".join(plain).strip(), "rendered from text/plain part, verbatim"
    if htm:
        return (html_to_text("\n".join(htm)),
                "no text/plain part present; rendered from text/html part, "
                "markup stripped, wording unaltered")
    return "[no readable body part present in native]", "no body part found"


def atts_of(msg):
    out = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        fn = part.get_filename()
        if "attachment" not in (part.get("Content-Disposition") or "").lower() \
                and not fn:
            continue
        raw = part.get_payload(decode=True) or b""
        out.append((fn or "[unnamed]", part.get_content_type(), len(raw),
                    hashlib.sha256(raw).hexdigest() if raw else "n/a"))
    return out


def eml_to_pdf(src, native):
    nsha = sha(native)
    with open(native, "rb") as fh:
        msg = email.message_from_binary_file(fh, policy=email.policy.default)
    body, note = pick_body(msg)
    out = OUT_E / f"{native.stem}.pdf"
    doc = make_doc(out, src, native.name)
    fl = [Paragraph(f"{src}", S_T),
          Paragraph("Working copy rendered from the preserved native email "
                    "file. The native is unaltered and retained. This PDF is a "
                    "rendering for readability and printing; the native .eml "
                    "governs.", S_S), Spacer(1, 5),
          Paragraph(f"native file: <font name='Courier'>{esc(native.name)}</font>"
                    f"<br/>native SHA-256: <font name='Courier'>{nsha}</font>"
                    f"<br/>rendered: {RUN}<br/>body: {esc(note)}", S_S),
          Spacer(1, 10)]
    rows = [("Date", msg.get("Date", "")), ("From", msg.get("From", "")),
            ("To", msg.get("To", ""))]
    for o in ("Cc", "Bcc", "Reply-To"):
        if msg.get(o):
            rows.append((o, msg.get(o)))
    rows += [("Subject", msg.get("Subject", "")),
             ("Message-ID", msg.get("Message-ID", ""))]
    fl.append(kv(rows))
    fl.append(Paragraph("MESSAGE BODY", S_H))
    for blk in body.split("\n\n"):
        if blk.strip():
            fl.append(Paragraph(esc(blk.strip()).replace("\n", "<br/>"), S_B))
            fl.append(Spacer(1, 5))
    a = atts_of(msg)
    if a:
        fl.append(Paragraph("ATTACHMENTS PRESENT IN NATIVE", S_H))
        data = [[Paragraph("<b>File</b>", S_C), Paragraph("<b>Type</b>", S_C),
                 Paragraph("<b>Bytes</b>", S_C), Paragraph("<b>SHA-256</b>", S_C)]]
        for n, ty, bl, h in a:
            data.append([Paragraph(esc(n), S_C), Paragraph(esc(ty), S_C),
                         Paragraph(f"{bl:,}", S_C),
                         Paragraph(f"<font name='Courier' size='6'>{h}</font>", S_C)])
        t = Table(data, colWidths=[1.7 * inch, 1.1 * inch, 0.7 * inch, None])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4F6F8")),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
        fl += [t, Paragraph("Attachment binaries are not embedded in this "
                            "rendering. They remain in the preserved native.", S_C)]
    fl.append(Paragraph("FULL HEADERS, VERBATIM", S_H))
    raw = "\n".join(f"{k}: {v}" for k, v in msg.items())
    for i in range(0, len(raw), 3000):
        fl.append(Preformatted(raw[i:i + 3000], S_M))
    doc.build(fl)
    return out, nsha


def image_pack(imgs):
    """One combined print PDF, all images, each on its own page at max fit."""
    out = OUT_I / f"SRC-0123_IMAGES_PRINT_{RUN}.pdf"
    doc = make_doc(out, "SRC-0123", "SRC-0123_img_1..7.png")
    fl = [Paragraph("SRC-0123 &mdash; image exhibits, print rendering", S_T),
          Paragraph("Every image extracted from the preserved native "
                    "SRC-0123_2026-07-20_payment-history-reply.eml, one per "
                    "page, placed at maximum page fit. <b>No enhancement, "
                    "sharpening, interpolation or upscaling has been applied to "
                    "any image.</b> Natives retained unaltered and included "
                    "alongside this file.", S_S), Spacer(1, 8)]
    data = [[Paragraph("<b>Image</b>", S_C), Paragraph("<b>Pixels</b>", S_C),
             Paragraph("<b>Bytes</b>", S_C), Paragraph("<b>Note</b>", S_C)]]
    for p, w, h in imgs:
        note = ("thin strip, little or no visible content"
                if h <= 30 and p.stat().st_size < 20000 else
                "thin strip" if h <= 30 else "content image")
        data.append([Paragraph(esc(p.name), S_C), Paragraph(f"{w} x {h}", S_C),
                     Paragraph(f"{p.stat().st_size:,}", S_C),
                     Paragraph(note, S_C)])
    t = Table(data, colWidths=[2.1 * inch, 1.0 * inch, 0.8 * inch, None])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DDDDDD")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F4F6F8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    fl += [Paragraph("INVENTORY", S_H), t]
    aw, ah = letter[0] - 1.2 * inch, letter[1] - 2.6 * inch
    for p, w, h in imgs:
        sc = min(aw / w, ah / h)
        fl += [PageBreak(),
               Paragraph(f"{esc(p.name)}", S_T),
               Paragraph(f"native dimensions {w} x {h} pixels, "
                         f"{p.stat().st_size:,} bytes. No enhancement applied. "
                         f"native SHA-256 "
                         f"<font name='Courier' size='6'>{sha(p)}</font>", S_S),
               Spacer(1, 8),
               RLImage(str(p), width=w * sc, height=h * sc)]
    doc.build(fl)
    return out


def preserved_match(size):
    """Return the SRC file in keydocs whose byte size matches, if any."""
    for q in KEY.iterdir():
        if q.is_file() and q.suffix.lower() != ".eml" and q.stat().st_size == size:
            return q.name
    return ""


def extract_atts():
    """Save every real attachment. Inline images already ship in images\\."""
    rows = []
    for src, name in EMLS:
        p = KEY / name
        if not p.is_file():
            continue
        with open(p, "rb") as fh:
            msg = email.message_from_binary_file(fh, policy=email.policy.default)
        i = 0
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            fn = part.get_filename()
            disp = (part.get("Content-Disposition") or "").lower()
            if "attachment" not in disp and not fn:
                continue
            if "inline" in disp and part.get_content_maintype() == "image":
                continue
            raw = part.get_payload(decode=True) or b""
            if not raw:
                continue
            i += 1
            safe = "".join(c if c.isalnum() or c in "-_. " else "_"
                           for c in (fn or f"unnamed_{i}")).strip()
            outp = OUT_A / f"{src}_att{i}_{safe}"
            outp.write_bytes(raw)
            m = preserved_match(len(raw))
            rows.append((src, outp, fn or f"unnamed_{i}", len(raw),
                         hashlib.sha256(raw).hexdigest(), m))
            log(f"ATT    {src} att{i}  {safe}  {len(raw):,}"
                + (f"  == {m}" if m else "  (not separately preserved)"))
    return rows


def main():
    log(f"START  Wilson counsel PDF pass {RUN}")
    if not KEY.is_dir():
        log(f"FATAL  keydocs not found: {KEY}")
        sys.exit(1)
    OUT_E.mkdir(parents=True, exist_ok=True)
    OUT_I.mkdir(parents=True, exist_ok=True)
    OUT_A.mkdir(parents=True, exist_ok=True)
    man, missing = [], []

    for src, name in EMLS:
        p = KEY / name
        if not p.is_file():
            missing.append((src, name))
            log(f"MISS   {src}  {name}")
            continue
        try:
            o, nsha = eml_to_pdf(src, p)
            man.append((src, o, f"PDF working copy of {p.name}", p.name, nsha))
            log(f"WROTE  {o.name}")
        except Exception as e:
            log(f"ERROR  {src}: {e!r}")

    imgs = []
    for p in sorted(KEY.glob("SRC-0123_img_*.png")):
        with PILImage.open(p) as im:
            w, h = im.size
        imgs.append((p, w, h))
        c = OUT_I / p.name
        shutil.copy2(p, c)
        man.append(("SRC-0123", c, f"native image, byte-identical copy, {w}x{h}px",
                    p.name, sha(p)))
        log(f"COPY   {p.name}  {w}x{h}")
    if imgs:
        try:
            o = image_pack(imgs)
            man.append(("SRC-0123", o,
                        "print rendering of all 7 images, no enhancement",
                        "SRC-0123_img_1..7.png", "see per-image pages"))
            log(f"WROTE  {o.name}")
        except Exception as e:
            log(f"ERROR  image pack: {e!r}")

    atts = extract_atts()
    for src, outp, orig, n, h, m in atts:
        note = f"attachment extracted from {src} native, original name '{orig}'"
        note += f", byte-identical to preserved {m}" if m else \
                ", NOT separately preserved elsewhere"
        man.append((src, outp, note, orig, h))

    rd = OUT / "README_FOR_COUNSEL.txt"
    with open(rd, "w", encoding="utf-8") as fh:
        fh.write(f"WILSON MATTER - PDF CONVERSION PASS, {RUN}\n{CAPTION}\n")
        fh.write("=" * 72 + "\n\nWHAT THIS FOLDER IS\n")
        fh.write("The eight requested .eml sources rendered as PDF, plus every\n")
        fh.write("image from SRC-0123 prepared for printing.\n\n")
        fh.write("emails_as_pdf\\   one PDF per requested source\n")
        fh.write("images\\          native PNGs + one combined print PDF\n")
        fh.write("attachments\\     files that were attached to those emails\n\n")
        fh.write("READ THIS FIRST: TWO EMAILS ARE ENVELOPES\n")
        fh.write("SRC-0121 and SRC-0102 have almost no body text. The substance\n")
        fh.write("is in their attachments, so the PDF rendering of the email\n")
        fh.write("alone will look empty. Those attachments are extracted into\n")
        fh.write("attachments\\ and most were already produced under their own\n")
        fh.write("source numbers:\n\n")
        for s, o, orig, n, h, m in atts:
            tag = f"already produced as {m}" if m else "NOT produced elsewhere"
            fh.write(f"  {s} -> {orig}\n        {n:,} bytes, {tag}\n")
        fh.write("\n")
        fh.write("PROVENANCE\n")
        fh.write("The .eml files are the evidence and are retained unaltered in\n")
        fh.write("preserved\\. Each PDF is a rendering for readability. Each PDF\n")
        fh.write("carries its native filename and native SHA-256 on page 1 and\n")
        fh.write("the complete verbatim header block at the end. Attachment\n")
        fh.write("binaries are not embedded; they are inventoried with hashes and\n")
        fh.write("remain in the natives. Any attachment can ship separately on\n")
        fh.write("request.\n\n")
        fh.write("NOTE ON THE IMAGE REQUEST\n")
        fh.write("SRC-0123_img_6.png was requested in a larger format. That file\n")
        fh.write("is 796 x 25 pixels and 468 bytes: a thin strip with little or no\n")
        fh.write("visible content, almost certainly a divider or spacer element\n")
        fh.write("from the email rather than substantive content. Enlarging it\n")
        fh.write("would not make anything legible because there is nothing in it\n")
        fh.write("to enlarge. All seven images from SRC-0123 are therefore\n")
        fh.write("included, each on its own page at maximum page fit with its\n")
        fh.write("native pixel dimensions stated, so the intended exhibit can be\n")
        fh.write("identified by number.\n\n")
        fh.write("No AI upscaling or enhancement was used on any image, and none\n")
        fh.write("should be: it invents detail that is not in the native and would\n")
        fh.write("put the enlargement itself at issue. If a native is too small to\n")
        fh.write("read, that is a fact about the native.\n\n")
        if missing:
            fh.write("REQUESTED BUT NOT LOCATED\n")
            for s, n in missing:
                fh.write(f"  {s}  {n}\n")
            fh.write("\n")
        fh.write("Every file in this folder is hashed in MANIFEST.txt.\n")

    mp = OUT / "MANIFEST.txt"
    with open(mp, "w", encoding="utf-8") as fh:
        fh.write(f"WILSON COUNSEL PDF PASS - MANIFEST - {RUN}\n{CAPTION}\n")
        fh.write("=" * 72 + "\n\n")
        for src, o, note, nn, ns in man:
            fh.write(f"{src}  {o.relative_to(OUT)}\n")
            fh.write(f"    note        : {note}\n")
            fh.write(f"    output sha  : {sha(o)}\n")
            fh.write(f"    native      : {nn}\n    native sha  : {ns}\n\n")
        fh.write(f"README_FOR_COUNSEL.txt\n    output sha  : {sha(rd)}\n\n")
        fh.write(f"outputs: {len(man)}\n")
        if missing:
            fh.write("\nNOT LOCATED:\n")
            for s, n in missing:
                fh.write(f"  {s}  {n}\n")

    with open(OUT / "CONVERSION_LOG.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(LOG) + "\n")

    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(OUT))

    print("\n" + "=" * 72 + "\nDONE\n" + "=" * 72)
    print(f"Folder      : {OUT}")
    print(f"Emails      : {OUT_E}")
    print(f"Images      : {OUT_I}")
    print(f"Zip to send : {ZIP}")
    print(f"Zip SHA-256 : {sha(ZIP)}")
    print(f"Zip bytes   : {ZIP.stat().st_size:,}")
    print(f"Outputs     : {len(man)}")
    if missing:
        print("\nNOT LOCATED:")
        for s, n in missing:
            print(f"  {s}  {n}")


if __name__ == "__main__":
    main()
