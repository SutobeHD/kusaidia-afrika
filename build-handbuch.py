#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the user-manual PDF for Rolf Schnee.

Run:   python build-handbuch.py
Out:   Kusaidia-Handbuch.pdf
"""

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, Flowable, NextPageTemplate,
)

# ============================================================
# Brand palette (matches the website's design tokens)
# ============================================================
TERRACOTTA    = HexColor("#b53c2a")
TERRACOTTA_DK = HexColor("#8a2a1b")
SAFFRON       = HexColor("#f8af52")
SAFFRON_DK    = HexColor("#d98e2c")
VANILLA       = HexColor("#fae3a6")
CREAM         = HexColor("#fbf7f1")
CREAM_WARM    = HexColor("#f4eadc")
INK           = HexColor("#1f1a16")
INK_SOFT      = HexColor("#4a3e34")
INK_MUTE      = HexColor("#7a6d62")
LINE          = HexColor("#e6dfd4")
CODE_BG       = HexColor("#f5efe6")

PAGE_W, PAGE_H = A4

# ============================================================
# Paragraph styles
# ============================================================
def make_styles():
    s = {}
    s["body"] = ParagraphStyle(
        "Body", fontName="Times-Roman", fontSize=10.5, leading=15,
        textColor=INK, alignment=TA_JUSTIFY, spaceAfter=8,
    )
    s["lead"] = ParagraphStyle(
        "Lead", parent=s["body"], fontName="Times-Italic", fontSize=12,
        leading=17, textColor=INK_SOFT, alignment=TA_LEFT, spaceAfter=14,
    )
    s["small"] = ParagraphStyle(
        "Small", parent=s["body"], fontSize=9, leading=13, textColor=INK_MUTE,
    )
    s["eyebrow"] = ParagraphStyle(
        "Eyebrow", fontName="Helvetica-Bold", fontSize=8, leading=11,
        textColor=TERRACOTTA, spaceAfter=4, alignment=TA_LEFT,
    )
    s["chapter"] = ParagraphStyle(
        "Chapter", fontName="Times-Bold", fontSize=26, leading=30,
        textColor=INK, alignment=TA_LEFT, spaceBefore=0, spaceAfter=8,
    )
    s["section"] = ParagraphStyle(
        "Section", fontName="Times-Bold", fontSize=17, leading=22,
        textColor=INK, alignment=TA_LEFT, spaceBefore=14, spaceAfter=6,
    )
    s["subsection"] = ParagraphStyle(
        "Subsection", fontName="Times-Bold", fontSize=13, leading=18,
        textColor=TERRACOTTA, alignment=TA_LEFT, spaceBefore=10, spaceAfter=4,
    )
    s["step"] = ParagraphStyle(
        "Step", parent=s["body"], leftIndent=14, spaceAfter=5,
    )
    s["bullet"] = ParagraphStyle(
        "Bullet", parent=s["body"], leftIndent=14, bulletIndent=2, spaceAfter=4,
    )
    s["code"] = ParagraphStyle(
        "Code", fontName="Courier", fontSize=9, leading=12.5,
        textColor=INK, alignment=TA_LEFT, leftIndent=0, rightIndent=0,
    )
    s["caption"] = ParagraphStyle(
        "Caption", fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
        textColor=INK_MUTE, alignment=TA_LEFT, spaceAfter=10,
    )
    s["cover_kicker"] = ParagraphStyle(
        "CoverKicker", fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=TERRACOTTA, alignment=TA_LEFT,
    )
    s["cover_title"] = ParagraphStyle(
        "CoverTitle", fontName="Times-Bold", fontSize=44, leading=48,
        textColor=INK, alignment=TA_LEFT, spaceAfter=12,
    )
    s["cover_subtitle"] = ParagraphStyle(
        "CoverSubtitle", fontName="Times-Italic", fontSize=18, leading=24,
        textColor=INK_SOFT, alignment=TA_LEFT,
    )
    s["cover_meta"] = ParagraphStyle(
        "CoverMeta", fontName="Helvetica", fontSize=10, leading=14,
        textColor=INK_MUTE, alignment=TA_LEFT,
    )
    s["toc_chapter"] = ParagraphStyle(
        "TocChapter", fontName="Helvetica-Bold", fontSize=10, leading=14,
        textColor=TERRACOTTA, alignment=TA_LEFT, spaceBefore=10, spaceAfter=4,
    )
    s["toc_item"] = ParagraphStyle(
        "TocItem", fontName="Times-Roman", fontSize=10.5, leading=15,
        textColor=INK, alignment=TA_LEFT, leftIndent=10,
    )
    s["table_header"] = ParagraphStyle(
        "TH", fontName="Helvetica-Bold", fontSize=9, leading=12,
        textColor=CREAM, alignment=TA_LEFT,
    )
    s["table_cell"] = ParagraphStyle(
        "TC", fontName="Times-Roman", fontSize=9.5, leading=13,
        textColor=INK, alignment=TA_LEFT,
    )
    s["table_code"] = ParagraphStyle(
        "TCcode", fontName="Courier", fontSize=8.5, leading=12,
        textColor=INK, alignment=TA_LEFT,
    )
    return s

ST = make_styles()

# ============================================================
# Custom flowables
# ============================================================
class HorizontalRule(Flowable):
    def __init__(self, width=None, thickness=0.5, color=LINE, space_before=4, space_after=8):
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.color = color
        self.space_before = space_before
        self.space_after = space_after

    def wrap(self, avail_w, avail_h):
        self._w = self.width or avail_w
        return (self._w, self.thickness + self.space_before + self.space_after)

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        y = self.space_after
        c.line(0, y, self._w, y)


class AccentMark(Flowable):
    """Small saffron square accent before a section heading."""
    def __init__(self, color=TERRACOTTA, size=8, space_after=6):
        super().__init__()
        self.color = color
        self.size = size
        self.space_after = space_after

    def wrap(self, avail_w, avail_h):
        return (self.size, self.size + self.space_after)

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.rect(0, self.space_after, self.size, self.size, fill=1, stroke=0)


def code_block(code_text):
    """Render a code block as a single-cell table with cream background."""
    p = Paragraph(code_text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"),
                  ST["code"])
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CODE_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBEFORE", (0, 0), (0, -1), 3, SAFFRON),
        ("BOX", (0, 0), (-1, -1), 0.25, LINE),
    ]))
    return t


def callout(text, kind="info"):
    """Tip / warning callout."""
    color = SAFFRON if kind == "info" else TERRACOTTA
    bg = CREAM_WARM if kind == "info" else HexColor("#f9e6e2")
    p = Paragraph(text, ST["body"])
    t = Table([[p]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBEFORE", (0, 0), (0, -1), 3, color),
    ]))
    return t


def step_list(items):
    """Numbered list with circle markers."""
    out = []
    for i, line in enumerate(items, 1):
        p = Paragraph(f'<font color="#b53c2a"><b>{i}.</b></font>&nbsp;&nbsp;{line}',
                      ST["step"])
        out.append(p)
    return out


def bullet_list(items):
    out = []
    for line in items:
        p = Paragraph(f'<font color="#d98e2c">•</font>&nbsp;&nbsp;{line}', ST["bullet"])
        out.append(p)
    return out


def chapter_head(num, title, kicker=None):
    """Chapter heading with a saffron rule above."""
    out = []
    out.append(Spacer(1, 4))
    if kicker:
        out.append(Paragraph(kicker.upper(), ST["eyebrow"]))
    out.append(Paragraph(f"<b>{num}</b>&nbsp;&nbsp;{title}", ST["chapter"]))
    out.append(HorizontalRule(thickness=1.5, color=TERRACOTTA,
                              space_before=2, space_after=14))
    return out


def section_head(title):
    return [Spacer(1, 8), Paragraph(title, ST["section"]),
            HorizontalRule(thickness=0.4, color=LINE, space_before=2, space_after=6)]


def sub_head(title):
    return [Paragraph(title, ST["subsection"])]


def p(text):
    return Paragraph(text, ST["body"])


# ============================================================
# Page templates
# ============================================================
HEADER_FOOTER_FONT = "Helvetica"

def draw_page_chrome(canv, doc):
    """Header strip + footer with page number + brand mark."""
    canv.saveState()

    # Header — thin terracotta rule
    canv.setStrokeColor(TERRACOTTA)
    canv.setLineWidth(0.6)
    canv.line(2.2 * cm, PAGE_H - 1.4 * cm, PAGE_W - 2.2 * cm, PAGE_H - 1.4 * cm)

    # Header — small brand mark on the left
    canv.setFont("Times-Roman", 9)
    canv.setFillColor(TERRACOTTA)
    canv.drawString(2.2 * cm, PAGE_H - 1.15 * cm, "Kusaidia Afrika")
    canv.setFillColor(INK_MUTE)
    canv.setFont(HEADER_FOOTER_FONT, 8)
    canv.drawString(2.2 * cm + 3.0 * cm, PAGE_H - 1.15 * cm,
                    "  ·  Handbuch für die Website")

    # Header — current chapter on the right
    chapter_label = getattr(canv, "_chapter_label", "")
    if chapter_label:
        canv.setFont(HEADER_FOOTER_FONT, 8)
        canv.setFillColor(INK_MUTE)
        canv.drawRightString(PAGE_W - 2.2 * cm, PAGE_H - 1.15 * cm, chapter_label)

    # Footer — page number
    canv.setFont(HEADER_FOOTER_FONT, 9)
    canv.setFillColor(INK_MUTE)
    canv.drawCentredString(PAGE_W / 2, 1.2 * cm, f"{doc.page}")

    canv.restoreState()


def draw_cover(canv, doc):
    """Cover page background."""
    canv.saveState()
    # Wide cream band, saffron edge
    canv.setFillColor(CREAM_WARM)
    canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    # Saffron block bottom-left
    canv.setFillColor(SAFFRON)
    canv.rect(0, 0, 5 * cm, 4 * cm, fill=1, stroke=0)
    # Terracotta block top-right
    canv.setFillColor(TERRACOTTA)
    canv.rect(PAGE_W - 6 * cm, PAGE_H - 4 * cm, 6 * cm, 4 * cm, fill=1, stroke=0)
    # Vanilla horizontal strip
    canv.setFillColor(VANILLA)
    canv.rect(0, PAGE_H * 0.42, PAGE_W, 0.6 * cm, fill=1, stroke=0)
    canv.restoreState()


# Page chapter labels (set per page via afterFlowable)
class HandbuchDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self._current_chapter = ""

    def afterFlowable(self, flowable):
        # Track current chapter for the running header
        if hasattr(flowable, "_chapter_for_header"):
            self._current_chapter = flowable._chapter_for_header

    def handle_pageBegin(self):
        self.canv._chapter_label = self._current_chapter
        super().handle_pageBegin()


class ChapterMarker(Flowable):
    """Invisible flowable that updates the running header chapter label."""
    def __init__(self, label):
        super().__init__()
        self._chapter_for_header = label

    def wrap(self, *_): return (0, 0)
    def draw(self): pass


# ============================================================
# Build the content
# ============================================================
def build_story():
    s = []

    # ---------- COVER ----------
    s.append(Spacer(1, 5 * cm))
    s.append(Paragraph("Handbuch", ST["cover_kicker"]))
    s.append(Spacer(1, 12))
    s.append(Paragraph("Deine Website,<br/>verständlich gemacht.", ST["cover_title"]))
    s.append(Spacer(1, 8))
    s.append(Paragraph("Wie sie funktioniert. Wie du sie selbst pflegst.",
                       ST["cover_subtitle"]))
    s.append(Spacer(1, 4 * cm))
    s.append(Paragraph("Für Rolf Schnee", ST["cover_meta"]))
    s.append(Paragraph("Kusaidia Afrika — Helfen in Afrika e.V.", ST["cover_meta"]))
    s.append(Paragraph("Mai 2026", ST["cover_meta"]))
    s.append(NextPageTemplate("content"))
    s.append(PageBreak())

    # ---------- VORWORT ----------
    s.append(ChapterMarker("Vorwort"))
    s += chapter_head("", "Vorwort", kicker="Bevor du anfängst")
    s.append(Paragraph(
        "Lieber Rolf,", ST["lead"]))
    s.append(p(
        "dieses Heft ist für dich gedacht. Es soll dir helfen, deine neue Website nicht "
        "nur zu benutzen, sondern auch zu <b>verstehen</b> — und kleine Änderungen "
        "selbst vorzunehmen."))
    s.append(p(
        "Du brauchst dafür keinerlei Vorkenntnisse. Wir fangen vorne an: Was ist eigentlich "
        "eine Website? Wie ist sie aufgebaut? Wo steht der Text, den ich auf der Startseite "
        "sehe? Wie ändere ich ein Datum oder ein Foto?"))
    s += sub_head("Was du am Ende kannst")
    s += bullet_list([
        "Texte auf der Website ändern.",
        "Eine neue Aktuelles-Meldung schreiben.",
        "Bilder austauschen oder neue hinzufügen.",
        "Eine ganz neue Seite anlegen.",
        "Erkennen, was du im Code siehst — auch wenn du nicht jedes Detail verstehst.",
        "Mit Git deinen Arbeitsstand sichern und wieder zurückrollen.",
    ])
    s.append(Spacer(1, 6))
    s.append(p(
        "Lass dir Zeit. Lies in der Reihenfolge, in der das Heft aufgebaut ist. Springe "
        "zurück, wo es nicht ganz hängenbleibt. Und ruf an, wenn etwas klemmt."))
    s.append(Spacer(1, 18))
    s.append(Paragraph("Herzlich,<br/>Thomas", ST["lead"]))
    s.append(PageBreak())

    # ---------- INHALT ----------
    s.append(ChapterMarker("Inhalt"))
    s += chapter_head("", "Inhalt", kicker="Was dich erwartet")
    toc_entries = [
        ("Teil 1", "Was ist eigentlich eine Website?", [
            "Eine Website ist nur eine Sammlung von Dateien",
            "Drei &bdquo;Sprachen&ldquo; arbeiten zusammen",
            "Was passiert beim Aufrufen?",
        ]),
        ("Teil 2", "Die Werkzeuge", [
            "Der Browser (kennst du schon)",
            "Der Editor — VS Code",
            "Die Ordnerstruktur deiner Website",
        ]),
        ("Teil 3", "HTML verstehen", [
            "Tags sind wie Klammern",
            "Die wichtigsten Tags",
            "Attribute — die Eigenschaften eines Tags",
            "Die Struktur einer ganzen Seite",
            "Walkthrough: deine Startseite",
        ]),
        ("Teil 4", "CSS auf einen Blick", [
            "Was CSS macht",
            "Wo deine Farben definiert sind",
            "Wann musst du CSS anfassen?",
        ]),
        ("Teil 5", "Häufige Aufgaben", [
            "A · Einen Text ändern",
            "B · Ein Bild austauschen",
            "C · Eine neue Aktuelles-Meldung",
            "D · Eine ganz neue Seite anlegen",
            "E · Einen Link einfügen",
            "F · Einen Spendenbetrag anpassen",
            "G · Ein Vorstandsmitglied ändern",
            "H · Ein Bild zur Galerie hinzufügen",
        ]),
        ("Teil 6", "Git — der Schutzschirm", [
            "Was ist Git?",
            "Die drei wichtigsten Befehle",
            "Wenn etwas kaputt geht",
        ]),
        ("Teil 7", "Wenn etwas nicht funktioniert", [
            "Häufige Fehler &amp; Lösungen",
            "Die Browser-Konsole",
        ]),
        ("Anhang", "Nachschlagen", [
            "A · Glossar",
            "B · Spickzettel der Tags",
            "C · Dateibaum deiner Website",
        ]),
    ]
    for part, title, items in toc_entries:
        s.append(Paragraph(f"{part}  ·  {title}", ST["toc_chapter"]))
        for it in items:
            s.append(Paragraph("— " + it, ST["toc_item"]))
    s.append(PageBreak())

    # ============================================================
    # TEIL 1 — Was ist eine Website?
    # ============================================================
    s.append(ChapterMarker("Teil 1 · Was ist eine Website?"))
    s += chapter_head("Teil 1", "Was ist eigentlich eine Website?",
                      kicker="Das Fundament — drei Seiten")
    s.append(Paragraph(
        "Bevor wir Code anschauen, klären wir das große Bild. Eine Website ist nicht "
        "magisch, sie ist nicht &bdquo;im Internet&ldquo; auf besondere Weise — sie besteht aus "
        "ganz normalen Dateien.", ST["lead"]))

    s += section_head("Kapitel 1 · Eine Website ist nur eine Sammlung von Dateien")
    s.append(p(
        "Auf einem Computer irgendwo auf der Welt — wir nennen ihn <b>Server</b> — liegen "
        "deine Dateien. Genau wie auf deinem eigenen PC, wo du auch Dokumente, Fotos und "
        "Tabellen hast. Nur dass dieser Server immer angeschaltet ist und immer im Internet "
        "erreichbar bleibt."))
    s.append(p(
        "Wenn jemand <font face=\"Courier\">kusaidia-afrika.de</font> in den Browser tippt, "
        "fragt der Browser diesen Server: &bdquo;Gib mir die Startseite!&ldquo; — und der Server "
        "schickt eine Datei zurück. Der Browser baut daraus die Seite zusammen, die du "
        "siehst."))
    s.append(p(
        "Deine ganze Website besteht aus rund 30 solchen Dateien. Sie liegen in einem "
        "Ordner auf deinem PC unter:"))
    s.append(code_block("C:\\Users\\rolf\\Documents\\GitHub\\Kusaidia\\"))
    s.append(Spacer(1, 6))
    s.append(p(
        "Wenn du die Website veröffentlichst (das macht dein Enkel oder ein Hosting-Dienst), "
        "werden genau diese Dateien auf den Server kopiert. Mehr passiert dabei nicht."))

    s += section_head("Kapitel 2 · Drei &bdquo;Sprachen&ldquo; arbeiten zusammen")
    s.append(p(
        "Jede Website spricht <b>drei Sprachen</b> gleichzeitig. Jede hat ihre Aufgabe:"))
    s.append(Spacer(1, 4))

    three_langs = [
        [Paragraph("<b>HTML</b>", ST["table_cell"]),
         Paragraph("<b>der Inhalt</b>", ST["table_cell"]),
         Paragraph("Überschriften, Absätze, Bilder, Links. Was auf der Seite <i>steht</i>.",
                   ST["table_cell"])],
        [Paragraph("<b>CSS</b>", ST["table_cell"]),
         Paragraph("<b>das Aussehen</b>", ST["table_cell"]),
         Paragraph("Farben, Schriften, Abstände, Größen. Wie es <i>aussieht</i>.",
                   ST["table_cell"])],
        [Paragraph("<b>JavaScript</b>", ST["table_cell"]),
         Paragraph("<b>das Verhalten</b>", ST["table_cell"]),
         Paragraph("Diashow, Menü auf-/zuklappen, Klick-Reaktionen. Was sich <i>bewegt</i>.",
                   ST["table_cell"])],
    ]
    tbl = Table(three_langs, colWidths=[3*cm, 4*cm, 9.4*cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, -1), CREAM_WARM),
        ("LINEABOVE", (0, 0), (-1, 0), 0.5, LINE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, LINE),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, LINE),
    ]))
    s.append(tbl)
    s.append(Spacer(1, 8))
    s.append(p(
        "<b>Eine Analogie:</b> Stell dir ein Haus vor."))
    s += bullet_list([
        "<b>HTML</b> sind die Mauern, Wände, Türen. Sie bilden die Struktur.",
        "<b>CSS</b> ist die Farbe der Wände, der Bodenbelag, die Tapete.",
        "<b>JavaScript</b> sind die Lichtschalter, die Türklingel, das, was reagiert wenn du es berührst.",
    ])
    s.append(p(
        "Du wirst hauptsächlich mit <b>HTML</b> in Kontakt kommen. CSS schaust du dir nur "
        "kurz an, JavaScript brauchst du gar nicht zu verstehen — es funktioniert von "
        "selbst."))

    s += section_head("Kapitel 3 · Was passiert beim Aufrufen?")
    s.append(p(
        "Wenn jemand deine Website besucht, läuft folgendes ab — und zwar in Sekunden­"
        "bruchteilen:"))
    s += step_list([
        "Browser fragt den Server: &bdquo;Gib mir die Datei <i>index.html</i>!&ldquo;",
        "Server schickt sie.",
        "Browser liest die Datei und merkt: &bdquo;Aha, ich brauche auch das "
        "Stylesheet <i>style.css</i> und ein paar Bilder.&ldquo;",
        "Browser holt sich auch diese Dateien.",
        "Browser baut alles zusammen und stellt die Seite dar.",
    ])
    s.append(Spacer(1, 6))
    s.append(callout(
        "<b>Wichtig:</b> Wenn du eine Datei änderst, kannst du sofort im Browser "
        "<font face='Courier'>F5</font> drücken, um die neue Version zu sehen. Drücke "
        "<font face='Courier'>Strg + F5</font>, falls die alte Version noch hängt — das "
        "lädt alles komplett neu."
    ))
    s.append(PageBreak())

    # ============================================================
    # TEIL 2 — Werkzeuge
    # ============================================================
    s.append(ChapterMarker("Teil 2 · Werkzeuge"))
    s += chapter_head("Teil 2", "Die Werkzeuge", kicker="Was du brauchst, um anzufangen")
    s.append(Paragraph(
        "Du brauchst genau drei Werkzeuge: einen Browser (hast du schon), einen Editor "
        "(installieren wir gleich), und den Datei-Explorer (gibt's bei Windows immer).",
        ST["lead"]))

    s += section_head("Kapitel 4 · Der Browser")
    s.append(p(
        "Du hast bestimmt schon einen Browser: Chrome, Firefox, Edge — alle funktionieren "
        "gleich gut. Damit schaust du dir an, wie deine Website aktuell aussieht."))
    s += sub_head("So öffnest du deine Website lokal:")
    s += step_list([
        "Datei-Explorer öffnen.",
        "Zum Kusaidia-Ordner gehen.",
        "Doppelklick auf <font face='Courier'>index.html</font>.",
        "Die Startseite öffnet sich im Browser.",
    ])

    s += section_head("Kapitel 5 · Der Editor — VS Code")
    s.append(p(
        "Du brauchst ein Programm, mit dem du die HTML-Dateien öffnen und bearbeiten kannst. "
        "Theoretisch geht das mit Word oder Notepad — aber das ist mühsam. Es gibt einen "
        "kostenlosen, professionellen Editor namens <b>Visual Studio Code</b> (kurz: VS Code)."))

    s += sub_head("Installation")
    s += step_list([
        "Im Browser <font face='Courier'>code.visualstudio.com</font> aufrufen.",
        "Auf den blauen Download-Knopf klicken (Windows).",
        "Die heruntergeladene Datei öffnen und installieren — Standard-Klicks reichen.",
        "VS Code starten.",
    ])

    s += sub_head("Den Kusaidia-Ordner öffnen")
    s += step_list([
        "In VS Code: Menü <b>Datei → Ordner öffnen</b>.",
        "Den Kusaidia-Ordner auswählen.",
        "Links siehst du nun den Datei-Baum.",
        "Klick auf eine Datei (z. B. <font face='Courier'>index.html</font>) öffnet sie zum Bearbeiten.",
    ])
    s.append(callout(
        "<b>Tipp:</b> VS Code zeigt dir HTML in <b>bunten Farben</b> — Tags blau, Attribute "
        "orange, Text grau. Das ist <i>Syntax-Highlighting</i> und hilft sehr beim Lesen. "
        "Du musst nichts dafür tun, es passiert automatisch."
    ))

    s += section_head("Kapitel 6 · Die Ordnerstruktur deiner Website")
    s.append(p(
        "Wenn du den Kusaidia-Ordner geöffnet hast, siehst du folgende Struktur:"))
    s.append(code_block(
"""Kusaidia/
├── index.html                ← Startseite
├── ueber-uns.html            ← Über uns
├── projekte.html             ← Übersicht Projekte
├── partner.html              ← Partner in Afrika
├── aktuelles.html            ← Neuigkeiten
├── unterstuetzen.html        ← Spenden & Mitgliedschaft
├── kontakt.html              ← Kontakt
├── impressum.html
├── datenschutz.html
├── bildergalerie.html        ← Galerie
├── ihre-spende-kommt-an.html ← Transparenz
│
├── projekte/                 ← Projekt-Detailseiten
│   ├── laborantenkolleg-bashanet.html
│   ├── clinical-medicine.html
│   ├── sanu-tec.html
│   ├── madunga-girls-school.html
│   └── student-support.html
│
├── en/                       ← Englische Version (gleiche Struktur)
│   ├── index.html
│   ├── about.html
│   ├── ...
│
├── css/
│   └── style.css             ← Aussehen (Farben, Schriften)
│
├── js/
│   └── main.js               ← Bewegung (Diashow, Menü)
│
└── assets/
    └── images/               ← Alle Fotos
        ├── hero-1.jpg
        ├── bischof-antony-lagwen.jpg
        └── ...
"""))
    s.append(callout(
        "<b>Merke dir vor allem dies:</b> Wenn du Text änderst → es ist eine <b>.html</b>-"
        "Datei. Wenn du ein neues Bild reinlegst → in den Ordner <b>assets/images/</b>. "
        "Wenn du eine Farbe ändern willst → in <b>css/style.css</b>."
    ))
    s.append(PageBreak())

    # ============================================================
    # TEIL 3 — HTML
    # ============================================================
    s.append(ChapterMarker("Teil 3 · HTML verstehen"))
    s += chapter_head("Teil 3", "HTML verstehen", kicker="Die Sprache deiner Inhalte")
    s.append(Paragraph(
        "HTML ist eigentlich ganz einfach. Du musst dir nur ein Prinzip merken — und dann "
        "die wichtigsten zehn Tags. Das war's.", ST["lead"]))

    s += section_head("Kapitel 7 · Tags sind wie Klammern")
    s.append(p(
        "HTML besteht aus <b>Tags</b>. Ein Tag ist wie eine Klammer um einen Text, die "
        "dem Browser sagt, was darin steht — eine Überschrift, ein Absatz, ein Bild, ein "
        "Link."))
    s.append(p("Hier das einfachste Beispiel:"))
    s.append(code_block("<p>Hallo, das ist ein Absatz.</p>"))
    s.append(p("Was siehst du?"))
    s += bullet_list([
        "<font face='Courier'>&lt;p&gt;</font> ist die <b>öffnende Klammer</b> (p steht für &bdquo;paragraph&ldquo;, also Absatz).",
        "<font face='Courier'>&lt;/p&gt;</font> ist die <b>schließende Klammer</b> (mit Schrägstrich).",
        "Dazwischen steht der eigentliche Text.",
    ])
    s.append(p(
        "Im Browser wird daraus einfach: <i>Hallo, das ist ein Absatz.</i>"))
    s.append(callout(
        "Tags kommen <b>fast immer paarweise</b>: ein öffnender und ein schließender. "
        "Ausnahme: <font face='Courier'>&lt;img&gt;</font> für Bilder und ein paar andere — "
        "die brauchen keine schließende Klammer, weil sie keinen Inhalt umfassen, sondern "
        "<i>selbst</i> der Inhalt sind."
    ))

    s += section_head("Kapitel 8 · Die wichtigsten Tags")
    s.append(p("Diese zehn musst du kennen — den Rest wirst du im Vorbeigehen lernen:"))
    s.append(Spacer(1, 4))

    tags_data = [
        [Paragraph("<b>Tag</b>", ST["table_header"]),
         Paragraph("<b>Wofür</b>", ST["table_header"]),
         Paragraph("<b>Beispiel</b>", ST["table_header"])],

        [Paragraph("&lt;h1&gt; bis &lt;h6&gt;", ST["table_code"]),
         Paragraph("Überschriften (h1 = ganz groß, h6 = klein)", ST["table_cell"]),
         Paragraph("&lt;h1&gt;Über uns&lt;/h1&gt;", ST["table_code"])],

        [Paragraph("&lt;p&gt;", ST["table_code"]),
         Paragraph("Absatz", ST["table_cell"]),
         Paragraph("&lt;p&gt;Ein Absatz Text.&lt;/p&gt;", ST["table_code"])],

        [Paragraph("&lt;strong&gt;", ST["table_code"]),
         Paragraph("Fett gedruckter Text", ST["table_cell"]),
         Paragraph("&lt;strong&gt;wichtig&lt;/strong&gt;", ST["table_code"])],

        [Paragraph("&lt;em&gt;", ST["table_code"]),
         Paragraph("Kursiv (betont)", ST["table_cell"]),
         Paragraph("&lt;em&gt;betont&lt;/em&gt;", ST["table_code"])],

        [Paragraph("&lt;a&gt;", ST["table_code"]),
         Paragraph("Ein Link", ST["table_cell"]),
         Paragraph("&lt;a href=\"kontakt.html\"&gt;Kontakt&lt;/a&gt;", ST["table_code"])],

        [Paragraph("&lt;img&gt;", ST["table_code"]),
         Paragraph("Ein Bild (kein schließender Tag!)", ST["table_cell"]),
         Paragraph("&lt;img src=\"foto.jpg\" alt=\"...\" /&gt;", ST["table_code"])],

        [Paragraph("&lt;ul&gt; und &lt;li&gt;", ST["table_code"]),
         Paragraph("Aufzählung (ul = Liste, li = Eintrag)", ST["table_cell"]),
         Paragraph("&lt;ul&gt;&lt;li&gt;Eins&lt;/li&gt;&lt;li&gt;Zwei&lt;/li&gt;&lt;/ul&gt;",
                   ST["table_code"])],

        [Paragraph("&lt;br&gt;", ST["table_code"]),
         Paragraph("Zeilenumbruch", ST["table_cell"]),
         Paragraph("Erste Zeile&lt;br&gt;Zweite Zeile", ST["table_code"])],

        [Paragraph("&lt;div&gt;", ST["table_code"]),
         Paragraph("Allgemeiner Container (ein &bdquo;Kästchen&ldquo;)", ST["table_cell"]),
         Paragraph("&lt;div&gt;...Inhalt...&lt;/div&gt;", ST["table_code"])],

        [Paragraph("&lt;section&gt;", ST["table_code"]),
         Paragraph("Ein Abschnitt der Seite", ST["table_cell"]),
         Paragraph("&lt;section&gt;...&lt;/section&gt;", ST["table_code"])],
    ]
    tbl = Table(tags_data, colWidths=[4.5*cm, 6*cm, 6.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TERRACOTTA),
        ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, CREAM_WARM]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, LINE),
    ]))
    s.append(tbl)
    s.append(PageBreak())

    s += section_head("Kapitel 9 · Attribute — die Eigenschaften eines Tags")
    s.append(p(
        "Manche Tags brauchen zusätzliche Informationen. Diese stecken in <b>Attributen</b>, "
        "die im öffnenden Tag stehen."))
    s.append(p("Beispiel:"))
    s.append(code_block('<a href="kontakt.html">Schreiben Sie uns</a>'))
    s.append(Spacer(1, 4))
    s.append(p(
        "Hier ist <font face='Courier'>href=\"kontakt.html\"</font> ein Attribut. "
        "Es sagt dem Tag <font face='Courier'>&lt;a&gt;</font>: <i>"
        "&bdquo;Wenn jemand draufklickt, gehe zur Datei kontakt.html.&ldquo;</i>"))
    s += sub_head("Die wichtigsten Attribute")
    s += bullet_list([
        "<font face='Courier'><b>href=\"...\"</b></font> — wohin der Link führt "
        "(beim Tag &lt;a&gt;).",
        "<font face='Courier'><b>src=\"...\"</b></font> — wo das Bild liegt "
        "(beim Tag &lt;img&gt;).",
        "<font face='Courier'><b>alt=\"...\"</b></font> — eine Beschreibung des Bildes "
        "(wichtig für Sehbehinderte und Suchmaschinen).",
        "<font face='Courier'><b>class=\"...\"</b></font> — eine &bdquo;Schublade&ldquo; für das "
        "Aussehen. Das CSS nutzt sie, um zu bestimmen wie das Element gestaltet wird.",
        "<font face='Courier'><b>id=\"...\"</b></font> — ein einzigartiger Name. Brauchst "
        "du selten.",
    ])
    s.append(callout(
        "Attribute schreibt man immer in der Form <b>Name=\"Wert\"</b>. Der Wert steht "
        "in Anführungszeichen. Mehrere Attribute werden durch Leerzeichen getrennt."
    ))

    s += section_head("Kapitel 10 · Die Struktur einer ganzen Seite")
    s.append(p(
        "Jede deiner HTML-Dateien hat die gleiche Grundstruktur. Es lohnt sich, einmal "
        "zu wissen, was wo steht:"))
    s.append(code_block(
"""<!DOCTYPE html>
<html lang="de">
<head>
  <!-- Hier stehen Infos für den Browser. -->
  <!-- Diese Sachen sieht der Besucher NICHT direkt. -->
  <title>Seitentitel im Browser-Tab</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <!-- Alles was du auf der Seite SIEHST, steht hier drin. -->

  <header>Navigation oben</header>

  <main>
    Hauptinhalt — Überschriften, Absätze, Bilder, ...
  </main>

  <footer>Fußzeile mit Adresse, Links</footer>

</body>
</html>"""))
    s.append(Spacer(1, 6))
    s.append(p("Erklärung Stück für Stück:"))
    s += bullet_list([
        "<font face='Courier'>&lt;!DOCTYPE html&gt;</font> — sagt dem Browser: &bdquo;Das ist HTML.&ldquo;",
        "<font face='Courier'>&lt;html lang=\"de\"&gt;</font> — die Wurzel des Dokuments, Sprache ist Deutsch.",
        "<font face='Courier'>&lt;head&gt;</font> — Kopf der Datei. Hier stehen "
        "<b>unsichtbare</b> Infos wie Seitentitel, Beschreibung und Verweise auf Stylesheet.",
        "<font face='Courier'>&lt;body&gt;</font> — Körper. Hier steht alles, was der "
        "Besucher <b>sieht</b>.",
        "<font face='Courier'>&lt;!-- ... --&gt;</font> — ein Kommentar. Der Browser "
        "ignoriert ihn. Du kannst sowas zur eigenen Erinnerung schreiben.",
    ])
    s.append(PageBreak())

    s += section_head("Kapitel 11 · Walkthrough — deine Startseite")
    s.append(p(
        "Schauen wir mal kurz in <font face='Courier'>index.html</font> hinein. Du brauchst "
        "nicht alles zu verstehen — es geht nur ums Wiedererkennen."))
    s.append(p(
        "Wenn du die Datei in VS Code öffnest und ganz nach oben scrollst, siehst du:"))
    s.append(code_block(
"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Kusaidia Afrika – Helfen in Afrika e.V.</title>
  ...
</head>"""))
    s.append(p(
        "Das ist der <b>Kopf</b>. Der Titel im Browser-Tab kommt aus dem "
        "<font face='Courier'>&lt;title&gt;</font>-Tag."))
    s.append(p("Etwas tiefer beginnt der sichtbare Inhalt:"))
    s.append(code_block(
"""<body>
  <header class="site-header">
    <div class="site-header__inner">
      <a href="index.html" class="brand">
        <span class="brand__mark">Kusaidia Afrika</span>
        <span class="brand__tag">e.V. seit 2001</span>
      </a>
      ...
    </div>
  </header>"""))
    s.append(p(
        "Das ist der Header — die Leiste oben. &bdquo;Kusaidia Afrika&ldquo; und &bdquo;e.V. seit 2001&ldquo; "
        "siehst du am oberen Rand der Seite."))
    s.append(p("Noch weiter unten:"))
    s.append(code_block(
"""<section class="hero">
  ...
  <h1>Kusaidia.<br /><em>Suaheli für »Helfen«.</em></h1>
  <p class="hero__lead">
    Wir lindern die Not im Gesundheits- und Schulwesen ...
  </p>
  ...
</section>"""))
    s.append(p(
        "Das ist der Hero — also der große Eindruck oben mit Bild und Überschrift. Hier "
        "kannst du Schlagzeile und Lead-Text ändern, indem du den Text zwischen den "
        "Tags ersetzt."))
    s.append(callout(
        "<b>Faustregel:</b> Was zwischen den Tags steht, ist der Inhalt, den du gefahrlos "
        "ändern kannst. Was <i>im</i> Tag steht (z. B. <font face='Courier'>class=\"...\"</font>) "
        "ist für das Aussehen wichtig — lass das im Zweifel stehen."
    ))
    s.append(PageBreak())

    # ============================================================
    # TEIL 4 — CSS
    # ============================================================
    s.append(ChapterMarker("Teil 4 · CSS auf einen Blick"))
    s += chapter_head("Teil 4", "CSS auf einen Blick",
                      kicker="Du brauchst nur wenig zu wissen")
    s.append(Paragraph(
        "CSS bestimmt das Aussehen. Du kommst nur selten damit in Berührung — aber es ist "
        "gut zu wissen, wo deine Farben stehen, falls du sie mal ändern willst.",
        ST["lead"]))

    s += section_head("Kapitel 12 · Was CSS macht")
    s.append(p(
        "CSS heißt <i>Cascading Style Sheets</i>. Es bestimmt nicht, <b>was</b> auf der Seite "
        "ist (das macht HTML), sondern <b>wie</b> es aussieht."))
    s.append(p("Ein CSS-Schnipsel sieht so aus:"))
    s.append(code_block(
""".btn--primary {
  background: #b53c2a;
  color: white;
  padding: 10px 20px;
}"""))
    s.append(p("Übersetzt:"))
    s += bullet_list([
        "<b>.btn--primary</b> — &bdquo;alle Elemente mit der Klasse <i>btn--primary</i>&ldquo;.",
        "<b>background: #b53c2a;</b> — &bdquo;bekommen einen terracotta-roten Hintergrund&ldquo;.",
        "<b>color: white;</b> — &bdquo;und weißen Text&ldquo;.",
        "<b>padding: 10px 20px;</b> — &bdquo;und drumherum 10px oben/unten, 20px links/rechts Platz&ldquo;.",
    ])
    s.append(p(
        "Die Datei mit allen CSS-Regeln deiner Website heißt "
        "<font face='Courier'>css/style.css</font>. Sie hat etwa 900 Zeilen — das musst du "
        "alles nicht lesen!"))

    s += section_head("Kapitel 13 · Wo deine Farben definiert sind")
    s.append(p(
        "Ganz am Anfang von <font face='Courier'>css/style.css</font> stehen die "
        "<b>Markenfarben</b>. Sie heißen &bdquo;CSS-Variablen&ldquo; und werden im Rest der Datei wieder "
        "verwendet:"))
    s.append(code_block(
""":root {
  --terracotta:    #b53c2a;    /* Hauptfarbe rot-braun */
  --saffron:       #f8af52;    /* Sekundär orange */
  --vanilla:       #fae3a6;    /* Heller Akzent */
  --cream:         #fbf7f1;    /* Hintergrund warm-weiß */
  --ink:           #1f1a16;    /* Textfarbe dunkel */
}"""))
    s.append(p(
        "Möchtest du z. B. die Hauptfarbe leicht ändern? Du musst nur diese eine Zeile "
        "anfassen. <b>Alles andere zieht automatisch nach</b> — Buttons, Überschriften, "
        "Akzente. Das ist die Magie von CSS-Variablen."))
    s.append(callout(
        "<b>Achtung:</b> Eine Farbe wird als <b>#rrggbb</b> geschrieben — sechs Zeichen aus "
        "Ziffern (0–9) und Buchstaben (a–f). Du kannst auf <font face='Courier'>"
        "htmlcolorcodes.com</font> Farben suchen und den Code abschreiben."
    ))

    s += section_head("Kapitel 14 · Wann musst du CSS anfassen?")
    s.append(p(
        "<b>Selten.</b> Wenn du Text ergänzt, ein Foto austauschst oder eine "
        "Aktuelles-Meldung schreibst, kommst du nie mit CSS in Kontakt."))
    s.append(p("Du musst nur in <font face='Courier'>style.css</font> rein, wenn du:"))
    s += bullet_list([
        "Eine Farbe ändern willst (siehe Kapitel 13).",
        "Etwas verschieben/anders anordnen willst.",
        "Etwas nicht gut aussieht und du es justieren möchtest.",
    ])
    s.append(callout(
        "<b>Wenn du nicht weißt, was eine Zeile in style.css tut: lass sie stehen.</b> "
        "Du kannst nichts dauerhaft kaputtmachen, solange du Git benutzt (Teil 6). "
        "Das ist dein Sicherheitsnetz.", kind="info"
    ))
    s.append(PageBreak())

    # ============================================================
    # TEIL 5 — Häufige Aufgaben
    # ============================================================
    s.append(ChapterMarker("Teil 5 · Häufige Aufgaben"))
    s += chapter_head("Teil 5", "Häufige Aufgaben",
                      kicker="Hier wird's praktisch — Schritt für Schritt")
    s.append(Paragraph(
        "Acht typische Situationen, mit konkreten Klicks. Halte dich an die Reihenfolge — "
        "Schritt für Schritt. Speichere zwischendurch oft (Strg + S).",
        ST["lead"]))

    # Aufgabe A
    s += section_head("Aufgabe A · Einen Text ändern")
    s.append(Paragraph(
        "<b>Beispiel:</b> Die Telefonnummer hat sich geändert.", ST["body"]))
    s += step_list([
        "VS Code öffnen, dann den Kusaidia-Ordner (Datei → Ordner öffnen).",
        "Drücke <b>Strg + Shift + F</b> — das öffnet die Suche über alle Dateien.",
        "Tippe die alte Telefonnummer ein, z. B. <font face='Courier'>07142 32370</font>.",
        "VS Code zeigt alle Stellen, wo sie steht.",
        "Klicke das Pfeil-nach-unten-Symbol → es erscheint ein zweites Feld zum Ersetzen.",
        "Tippe die neue Nummer ein.",
        "Klick auf das Symbol &bdquo;Alle ersetzen&ldquo; (zwei Pfeile in Doppelkreis).",
        "Speichere alle Dateien: <b>Strg + K, dann S</b> (kurz hintereinander).",
        "Im Browser <font face='Courier'>index.html</font> öffnen, mit F5 neu laden.",
    ])
    s.append(callout(
        "<b>Strg+F</b> = in <i>dieser</i> Datei suchen. "
        "<b>Strg+Shift+F</b> = in <i>allen</i> Dateien suchen. "
        "Die zweite Form ist oft die mächtigere."
    ))

    # Aufgabe B
    s += section_head("Aufgabe B · Ein Bild austauschen")
    s.append(Paragraph(
        "<b>Beispiel:</b> Du hast ein aktuelleres Bild von Sr. Basilisa Panga.", ST["body"]))
    s += step_list([
        "Speichere das neue Bild auf deinem PC. Bedingungen:",
    ])
    s += bullet_list([
        "Format: <b>.jpg</b> (oder .png).",
        "Größe: max. ca. 2 MB (sonst lädt die Seite langsam).",
        "Name: <b>nur Kleinbuchstaben</b>, Bindestriche, keine Leerzeichen, keine Umlaute. "
        "Beispiel: <font face='Courier'>sr-basilisa-2025.jpg</font>.",
    ])
    s += step_list([
        "Lege das Bild in den Ordner <font face='Courier'>assets/images/</font>.",
        "Öffne VS Code. Drücke <b>Strg + Shift + F</b>.",
        "Suche nach dem alten Dateinamen: <font face='Courier'>sr-basilisa-panga.jpg</font>.",
        "Ersetze ihn durch deinen neuen Namen.",
        "Speichern, im Browser prüfen.",
    ])
    s.append(callout(
        "<b>Wenn das Bild nicht erscheint:</b> Schreibfehler im Namen? Liegt es wirklich "
        "in <font face='Courier'>assets/images/</font>? Schaue im Browser (F12 → Konsole) "
        "nach roten Fehlern.", kind="warn"
    ))
    s.append(PageBreak())

    # Aufgabe C
    s += section_head("Aufgabe C · Eine neue Aktuelles-Meldung")
    s.append(Paragraph(
        "<b>Beispiel:</b> Du willst über die Visitationsreise im Herbst 2026 berichten.",
        ST["body"]))
    s += step_list([
        "Öffne <font face='Courier'>aktuelles.html</font> in VS Code.",
        "Suche den Block <font face='Courier'>&lt;article&gt;</font> der "
        "Kunstauktion 2024.",
        "Markiere ihn komplett — vom öffnenden <font face='Courier'>&lt;article&gt;</font> "
        "bis zum schließenden <font face='Courier'>&lt;/article&gt;</font>.",
        "Strg + C (Kopieren), dann Pfeiltaste nach oben (Cursor an den Anfang des Blocks), "
        "dann Strg + V (Einfügen).",
        "Jetzt hast du die Meldung doppelt. In der oberen Kopie änderst du:",
    ])
    s += bullet_list([
        "Das Datum (z. B. <font face='Courier'>&bdquo;Oktober 2026 · Visitationsreise&ldquo;</font>).",
        "Die Überschrift zwischen <font face='Courier'>&lt;h2&gt;</font> und "
        "<font face='Courier'>&lt;/h2&gt;</font>.",
        "Den Text zwischen <font face='Courier'>&lt;p&gt;</font> und "
        "<font face='Courier'>&lt;/p&gt;</font>.",
        "Die ID hinter <font face='Courier'>id=\"...\"</font> (vergib einen passenden "
        "Namen, z. B. <font face='Courier'>visitation-2026</font>).",
    ])
    s += step_list([
        "Speichern (Strg + S). Browser → F5.",
        "Wenn du auch eine englische Version willst: dasselbe in <font face='Courier'>en/news.html</font>.",
    ])

    # Aufgabe D
    s += section_head("Aufgabe D · Eine ganz neue Seite anlegen")
    s.append(Paragraph(
        "<b>Beispiel:</b> Du willst einen Jahresbericht 2024 als eigene Seite.", ST["body"]))
    s += step_list([
        "Im Datei-Explorer den Kusaidia-Ordner öffnen.",
        "Suche eine einfache Vorlage — z. B. <font face='Courier'>impressum.html</font>.",
        "Rechtsklick → &bdquo;Kopieren&ldquo;.",
        "Rechtsklick im selben Ordner → &bdquo;Einfügen&ldquo;.",
        "Eine Datei <font face='Courier'>impressum - Kopie.html</font> entsteht. "
        "Umbenennen zu <b><font face='Courier'>jahresbericht-2024.html</font></b>.",
        "Öffnen in VS Code.",
        "Oben den <font face='Courier'>&lt;title&gt;</font> ändern.",
        "Die <font face='Courier'>&lt;h1&gt;</font>-Überschrift anpassen.",
        "Im <font face='Courier'>&lt;main&gt;</font>-Bereich deinen Inhalt schreiben.",
        "Speichern.",
        "<b>Wichtig — verlinken:</b> Damit Besucher die Seite finden, brauchst du einen "
        "Link von woanders. Z. B. in <font face='Courier'>aktuelles.html</font> einfügen: "
        "<font face='Courier'>&lt;a href=\"jahresbericht-2024.html\"&gt;Jahresbericht "
        "2024&lt;/a&gt;</font>.",
    ])
    s.append(callout(
        "<b>Dateinamen-Regel:</b> Nur Kleinbuchstaben, Bindestriche, keine Umlaute, kein "
        "Leerzeichen. Browser können sonst Probleme machen. "
        "Gut: <font face='Courier'>jahresbericht-2024.html</font> · "
        "Schlecht: <font face='Courier'>Jahresbericht 2024.html</font>"
    ))
    s.append(PageBreak())

    # Aufgabe E
    s += section_head("Aufgabe E · Einen Link einfügen")
    s.append(Paragraph("Die Grundformel ist immer:", ST["body"]))
    s.append(code_block('<a href="WOHIN">SICHTBARER TEXT</a>'))
    s.append(Spacer(1, 4))
    s.append(p("Drei Spielarten:"))
    s += bullet_list([
        "<b>Auf eine andere Seite deiner Website</b>:<br/>"
        "<font face='Courier'>&lt;a href=\"kontakt.html\"&gt;Kontakt&lt;/a&gt;</font>",
        "<b>Auf eine externe Seite</b>:<br/>"
        "<font face='Courier'>&lt;a href=\"https://www.tagesschau.de\"&gt;Tagesschau&lt;/a&gt;</font>",
        "<b>Auf eine E-Mail-Adresse</b>:<br/>"
        "<font face='Courier'>&lt;a href=\"mailto:info@beispiel.de\"&gt;Schreib uns&lt;/a&gt;</font>",
        "<b>Auf eine Telefonnummer</b>:<br/>"
        "<font face='Courier'>&lt;a href=\"tel:+4971423237\"&gt;07142 32370&lt;/a&gt;</font>",
    ])

    # Aufgabe F
    s += section_head("Aufgabe F · Einen Spendenbetrag anpassen")
    s.append(Paragraph(
        "<b>Beispiel:</b> Der Mitgliedsbeitrag soll von 40 € auf 45 € steigen.", ST["body"]))
    s += step_list([
        "<font face='Courier'>unterstuetzen.html</font> öffnen.",
        "Strg + F (Suchen in dieser Datei).",
        "Suche nach <font face='Courier'>Einzelmitgliedschaft</font>.",
        "Du landest in einer Kachel <font face='Courier'>&lt;div class=\"amount\"&gt;</font>. "
        "Darin steht <font face='Courier'>&lt;div class=\"amount__sum\"&gt;40&lt;/div&gt;</font>.",
        "Ändere die 40 zu 45.",
        "Strg + S. Browser → F5.",
        "Englische Version: dasselbe in <font face='Courier'>en/support.html</font>.",
    ])

    # Aufgabe G
    s += section_head("Aufgabe G · Ein Vorstandsmitglied ändern")
    s.append(Paragraph(
        "<b>Beispiel:</b> Es gibt einen neuen Vorstand &bdquo;Maria Müller, Schriftführerin&ldquo;.",
        ST["body"]))
    s += step_list([
        "<font face='Courier'>ueber-uns.html</font> öffnen.",
        "Suche einen bestehenden Vorstandsblock — etwa für Dr. Michael Lutz-Dettinger.",
        "Markiere den ganzen <font face='Courier'>&lt;div class=\"card\"&gt;...&lt;/div&gt;</font>-Block.",
        "Kopiere ihn und füge ihn darunter ein.",
        "Im neuen Block änderst du:",
    ])
    s += bullet_list([
        "Die Rolle nach <font face='Courier'>&lt;span class=\"card__kicker\"&gt;</font> "
        "(z. B. &bdquo;Schriftführung&ldquo;).",
        "Den Namen in <font face='Courier'>&lt;h3&gt;</font> (z. B. &bdquo;Maria Müller&ldquo;).",
        "Die Beschreibung in <font face='Courier'>&lt;p&gt;</font>.",
    ])
    s += step_list([
        "Speichern, im Browser prüfen.",
        "Wiederhole für <font face='Courier'>en/about.html</font>.",
    ])

    # Aufgabe H
    s += section_head("Aufgabe H · Ein Bild zur Galerie hinzufügen")
    s.append(Paragraph(
        "<b>Beispiel:</b> Du hast ein neues Foto aus Mbulu, das in die Galerie soll.",
        ST["body"]))
    s += step_list([
        "Bild nach <font face='Courier'>assets/images/</font> legen (kleinbuchstaben-name "
        "ohne Umlaute).",
        "<font face='Courier'>bildergalerie.html</font> öffnen.",
        "Suche die passende Sektion — etwa &bdquo;Schulen & Ausbildung&ldquo;.",
        "Innerhalb der Sektion: einen bestehenden Block <font face='Courier'>"
        "&lt;button class=\"gallery-tile\"&gt;...&lt;/button&gt;</font> kopieren und "
        "darunter einfügen.",
        "Im neuen Block den Bildpfad und die Beschriftung anpassen.",
        "Zähler oben anpassen: <font face='Courier'>&lt;span class=\"gallery-section__count\"&gt;</font> "
        "— die Zahl der Aufnahmen erhöhen.",
        "Speichern.",
        "Auch in <font face='Courier'>en/gallery.html</font> nachziehen.",
    ])
    s.append(PageBreak())

    # ============================================================
    # TEIL 6 — Git
    # ============================================================
    s.append(ChapterMarker("Teil 6 · Git — der Schutzschirm"))
    s += chapter_head("Teil 6", "Git — der Schutzschirm",
                      kicker="Dein wichtigstes Sicherheitsnetz")
    s.append(Paragraph(
        "Git ist eine kleine Software, die jeden Arbeitsstand für dich speichert. Du "
        "kannst jederzeit zu jedem alten Stand zurück. Das nimmt dir die Angst, etwas zu "
        "verändern.", ST["lead"]))

    s += section_head("Kapitel 15 · Was ist Git?")
    s.append(p(
        "Stell dir Git wie ein <b>Tagebuch</b> vor. Jedes Mal, wenn du etwas änderst, sagst "
        "du Git: &bdquo;Bitte speichere das, was ich gerade gemacht habe.&ldquo; Git macht eine Notiz "
        "und merkt sich alle Dateien in genau diesem Zustand."))
    s.append(p(
        "Diese Notizen heißen <b>Commits</b>. In deinem Tagebuch stehen aktuell schon ein "
        "paar Einträge:"))
    s.append(code_block(
"""6c10900  Fix gallery captions and use real Fr. Karama portrait
7a3b73a  Fix callout readability
07258fb  Add English version with DE/EN language switcher
d42ae24  Add photo gallery with lightbox
3c36678  Initial site rebuild from web archive content"""))
    s.append(Spacer(1, 4))
    s.append(p(
        "Die linke Spalte ist eine eindeutige ID (ein <i>Hash</i>), die rechte ist die "
        "Notiz dazu. Wenn etwas später nicht stimmt, kannst du an jeden Punkt zurück."))

    s += section_head("Kapitel 16 · Die drei wichtigsten Befehle")
    s.append(p("Du brauchst nur drei Befehle. Sie werden im <b>Terminal</b> eingegeben."))
    s += sub_head("So öffnest du das Terminal")
    s += bullet_list([
        "In VS Code: Menü <b>Terminal → Neues Terminal</b> (oder Strg + ö).",
        "Unten erscheint ein schwarzes Fenster mit Eingabeprompt.",
    ])

    s += sub_head("Befehl 1 — Was hat sich geändert?")
    s.append(code_block("git status"))
    s.append(p(
        "Zeigt dir alle Dateien, die du seit dem letzten Commit verändert hast. Eine "
        "geänderte Datei sieht rot aus, eine markierte grün."))

    s += sub_head("Befehl 2 — Alle Änderungen für den Commit markieren")
    s.append(code_block("git add ."))
    s.append(p(
        "Der Punkt am Ende bedeutet: &bdquo;alle Dateien&ldquo;. Damit teilst du Git mit: "
        "&bdquo;Ich will all das gleich speichern.&ldquo;"))

    s += sub_head("Befehl 3 — Den Commit mit einer Notiz machen")
    s.append(code_block('git commit -m "Neue Aktuelles-Meldung Oktober 2026"'))
    s.append(p(
        "Das <font face='Courier'>-m</font> heißt &bdquo;message&ldquo; (Nachricht). Schreibe eine "
        "kurze Beschreibung in Anführungszeichen — Stichworte reichen."))
    s.append(callout(
        "<b>Eselsbrücke:</b> status → add → commit. "
        "&bdquo;Schau, was ist? Alles dazu. Speichern.&ldquo;"
    ))

    s += section_head("Kapitel 17 · Wenn etwas kaputt geht")
    s += sub_head("Du hast noch nicht commit-et?")
    s.append(p("Dann kannst du alles auf den letzten gespeicherten Stand zurücksetzen:"))
    s.append(code_block("git checkout -- ."))
    s.append(callout(
        "<b>Achtung:</b> Das wirft ALLE Änderungen seit dem letzten Commit weg. Nur "
        "ausführen, wenn du sicher bist, dass die aktuelle Arbeit nicht wertvoll ist.",
        kind="warn"
    ))

    s += sub_head("Du hast schon commit-et, willst aber zurück?")
    s.append(p("Zeig dir erst die letzten Commits:"))
    s.append(code_block("git log --oneline"))
    s.append(p("Dann erzeuge einen Commit, der den letzten rückgängig macht:"))
    s.append(code_block("git revert HEAD"))
    s.append(p(
        "<font face='Courier'>HEAD</font> ist Git-Sprech für &bdquo;der letzte Commit&ldquo;. Du "
        "kannst auch eine spezifische ID nehmen, z. B. "
        "<font face='Courier'>git revert 6c10900</font>."))
    s.append(PageBreak())

    # ============================================================
    # TEIL 7 — Wenn was nicht funktioniert
    # ============================================================
    s.append(ChapterMarker("Teil 7 · Fehlerbehebung"))
    s += chapter_head("Teil 7", "Wenn etwas nicht funktioniert",
                      kicker="Was tun, wenn die Seite hakt?")
    s.append(Paragraph(
        "Atme tief durch. Du hast nichts kaputtgemacht — Git hat alles gesichert. Hier "
        "sind die häufigsten Fehler und ihre Lösungen.", ST["lead"]))

    problems = [
        ("Die Seite zeigt noch das alte Bild / den alten Text",
         "Der Browser merkt sich Inhalte (das nennt sich <i>Cache</i>). Drück "
         "<font face='Courier'>Strg + F5</font> — das lädt die Seite komplett neu."),
        ("Ich sehe meine Änderung nicht",
         "1) Hast du die Datei gespeichert? Strg + S.<br/>"
         "2) Hast du die richtige Datei geändert? Bist du im richtigen Ordner?<br/>"
         "3) Browser mit Strg + F5 neu laden."),
        ("Plötzlich sieht alles komisch aus",
         "Wahrscheinlich ein verloren gegangenes &lt; oder &gt;. Bitte den Enkel um Hilfe, "
         "ODER setze die Änderungen zurück: "
         "<font face='Courier'>git checkout -- &lt;dateiname.html&gt;</font>"),
        ("Ein Bild wird nicht angezeigt",
         "1) Tippfehler im Dateinamen? Groß/Klein beachten — die Website unterscheidet "
         "<font face='Courier'>Foto.jpg</font> von <font face='Courier'>foto.jpg</font>!<br/>"
         "2) Liegt das Bild wirklich in <font face='Courier'>assets/images/</font>?<br/>"
         "3) Hat das Bild eine ungewöhnliche Endung (.jpeg statt .jpg)?"),
        ("Ein Link führt ins Leere",
         "Schau im <font face='Courier'>href=\"...\"</font> nach. Pfad richtig "
         "geschrieben? Bei Links innerhalb von Ordnern: <font face='Courier'>"
         "projekte/sanu-tec.html</font>. Bei einer Datei zurück nach oben: "
         "<font face='Courier'>../index.html</font>."),
        ("Eine englische Seite findet nicht zurück nach Deutsch",
         "Das DE/EN-Umschalter-Link auf der englischen Seite zeigt nach "
         "<font face='Courier'>../&lt;deutsche-datei&gt;.html</font>. Prüfe ihn dort."),
    ]
    for title, sol in problems:
        s.append(Paragraph(f"<b>&bdquo;{title}&ldquo;</b>", ST["subsection"]))
        s.append(p(sol))
        s.append(Spacer(1, 4))

    s += section_head("Die Browser-Konsole — dein bester Freund")
    s.append(p(
        "Drücke <b>F12</b> im Browser. Es öffnet sich ein technisches Fenster. Klicke auf "
        "den Reiter <b>Konsole</b> (oder <i>Console</i>)."))
    s.append(p(
        "Hier siehst du rot markierte Fehlermeldungen. Auch wenn du sie nicht alle "
        "verstehst — sie helfen einem Helfer (deinem Enkel), den Fehler zu finden. Mach im "
        "Zweifel einen Screenshot."))
    s.append(callout(
        "<b>Allerletzte Rettung:</b> Im Terminal "
        "<font face='Courier'>git reset --hard HEAD</font> eingeben. "
        "Damit gehen <b>alle ungespeicherten Änderungen</b> verloren — und die Website "
        "ist wieder auf dem letzten Commit. Das funktioniert IMMER.",
        kind="warn"
    ))
    s.append(PageBreak())

    # ============================================================
    # ANHANG A — Glossar
    # ============================================================
    s.append(ChapterMarker("Anhang · Nachschlagen"))
    s += chapter_head("Anhang A", "Glossar", kicker="Was bedeutet das alles?")
    glossary = [
        ("Attribut", "Zusätzliche Information in einem Tag, in der Form "
                     "Name=\"Wert\". Beispiel: href=\"kontakt.html\"."),
        ("Browser", "Programm, mit dem du das Internet ansiehst — Chrome, Firefox, Edge."),
        ("Cache", "Zwischenspeicher des Browsers. Behält alte Inhalte, damit's schneller "
                  "geht. Manchmal nervt das. Lösung: Strg + F5."),
        ("Class / Klasse", "Ein &bdquo;Etikett&ldquo; an einem HTML-Element. Das CSS schaut auf "
                           "Klassen, um zu entscheiden wie etwas aussehen soll."),
        ("Commit", "Ein gespeicherter Stand in Git — wie eine Notiz im Tagebuch."),
        ("CSS", "<i>Cascading Style Sheets</i>. Sprache, die das Aussehen bestimmt."),
        ("Editor", "Programm zum Bearbeiten von Code-Dateien. Wir nutzen VS Code."),
        ("F5", "Browser-Taste: Seite neu laden."),
        ("Git", "Versionsverwaltung. Speichert deine Arbeit Schritt für Schritt."),
        ("Hash", "Die siebenstellige ID eines Commits — z. B. 6c10900."),
        ("HTML", "<i>HyperText Markup Language</i>. Sprache des Inhalts und der Struktur."),
        ("JavaScript", "Sprache des Verhaltens. Sorgt für Diashow, Menü auf/zu, "
                       "klickbare Sachen."),
        ("Lokal", "Auf deinem eigenen Computer (anders als &bdquo;online&ldquo;, auf dem Server)."),
        ("Repository (Repo)", "Der Ordner, der von Git verwaltet wird — bei uns also "
                              "der Kusaidia-Ordner."),
        ("Server", "Computer, der die Website im Internet bereitstellt."),
        ("Strg + F", "In der aktuellen Datei suchen."),
        ("Strg + Shift + F", "In ALLEN Dateien suchen."),
        ("Tag", "HTML-Element wie &lt;p&gt; oder &lt;h1&gt;."),
        ("Terminal", "Schwarzes Fenster für Befehle. In VS Code: Strg + ö."),
        ("URL", "Internetadresse, z. B. kusaidia-afrika.de."),
    ]
    gloss_rows = []
    for term, defn in glossary:
        gloss_rows.append([
            Paragraph(f"<b>{term}</b>", ST["table_cell"]),
            Paragraph(defn, ST["table_cell"]),
        ])
    tbl = Table(gloss_rows, colWidths=[4*cm, 13*cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, LINE),
    ]))
    s.append(tbl)
    s.append(PageBreak())

    # ============================================================
    # ANHANG B — Tag-Spickzettel
    # ============================================================
    s += chapter_head("Anhang B", "Spickzettel der häufigsten Tags",
                      kicker="Zum Ausdrucken & neben den Rechner legen")
    s.append(Paragraph(
        "Die wichtigsten HTML-Tags und Attribute auf einer Doppelseite — kompakt.",
        ST["lead"]))

    cheat_rows = [
        ["<b>Tag</b>", "<b>Was es macht</b>", "<b>Beispiel</b>"],
        ["&lt;h1&gt;", "Hauptüberschrift", "&lt;h1&gt;Titel&lt;/h1&gt;"],
        ["&lt;h2&gt;", "Abschnittsüberschrift", "&lt;h2&gt;Abschnitt&lt;/h2&gt;"],
        ["&lt;h3&gt;", "Unterüberschrift", "&lt;h3&gt;Detail&lt;/h3&gt;"],
        ["&lt;p&gt;", "Absatz", "&lt;p&gt;Text...&lt;/p&gt;"],
        ["&lt;strong&gt;", "fett", "&lt;strong&gt;wichtig&lt;/strong&gt;"],
        ["&lt;em&gt;", "kursiv", "&lt;em&gt;betont&lt;/em&gt;"],
        ["&lt;br&gt;", "Zeilenumbruch", "Zeile&lt;br&gt;Zeile"],
        ["&lt;hr&gt;", "horizontaler Strich", "&lt;hr&gt;"],
        ["&lt;a href=\"...\"&gt;", "Link", "&lt;a href=\"x.html\"&gt;Klick&lt;/a&gt;"],
        ["&lt;img src=\"...\"&gt;", "Bild", "&lt;img src=\"foto.jpg\" alt=\"...\"&gt;"],
        ["&lt;ul&gt;", "Liste (ungeordnet)", "&lt;ul&gt;&lt;li&gt;..&lt;/li&gt;&lt;/ul&gt;"],
        ["&lt;ol&gt;", "Liste (durchnummeriert)", "&lt;ol&gt;&lt;li&gt;..&lt;/li&gt;&lt;/ol&gt;"],
        ["&lt;li&gt;", "Listeneintrag", "&lt;li&gt;Punkt&lt;/li&gt;"],
        ["&lt;div&gt;", "Container", "&lt;div&gt;...&lt;/div&gt;"],
        ["&lt;section&gt;", "Abschnitt", "&lt;section&gt;...&lt;/section&gt;"],
    ]
    rows = [[Paragraph(c, ST["table_code"] if i > 0 and j != 1 else ST["table_cell"])
             for j, c in enumerate(row)] for i, row in enumerate(cheat_rows)]
    rows[0] = [Paragraph(c, ST["table_header"]) for c in cheat_rows[0]]
    tbl = Table(rows, colWidths=[4*cm, 6*cm, 7*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TERRACOTTA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, CREAM_WARM]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, LINE),
    ]))
    s.append(tbl)
    s.append(Spacer(1, 12))

    s += sub_head("Wichtige Attribute")
    attr_rows = [
        ["<b>Attribut</b>", "<b>Wofür</b>", "<b>Bei welchem Tag</b>"],
        ["href", "Ziel eines Links", "&lt;a&gt;"],
        ["src", "Pfad zum Bild", "&lt;img&gt;"],
        ["alt", "Beschreibung des Bildes", "&lt;img&gt;"],
        ["class", "CSS-Klasse (Aussehen)", "alle"],
        ["id", "Eindeutiger Name (für Anker)", "alle"],
        ["lang", "Sprache", "&lt;html&gt;"],
    ]
    rows = [[Paragraph(c, ST["table_code"] if i > 0 and j != 1 else ST["table_cell"])
             for j, c in enumerate(row)] for i, row in enumerate(attr_rows)]
    rows[0] = [Paragraph(c, ST["table_header"]) for c in attr_rows[0]]
    tbl = Table(rows, colWidths=[3.5*cm, 8.5*cm, 5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SAFFRON_DK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, CREAM_WARM]),
    ]))
    s.append(tbl)
    s.append(Spacer(1, 12))

    s += sub_head("Tastenkürzel")
    keys_rows = [
        ["<b>Tasten</b>", "<b>Was sie tun</b>"],
        ["Strg + S", "Datei speichern"],
        ["Strg + Z", "Letzte Änderung rückgängig"],
        ["Strg + F", "In dieser Datei suchen"],
        ["Strg + Shift + F", "In allen Dateien suchen"],
        ["Strg + C / V", "Kopieren / einfügen"],
        ["Strg + ö", "VS Code: Terminal öffnen"],
        ["F5", "Browser: neu laden"],
        ["Strg + F5", "Browser: ganz neu laden (Cache ignorieren)"],
        ["F12", "Browser: Entwicklerwerkzeuge öffnen"],
    ]
    rows = [[Paragraph(c, ST["table_cell"]) for c in row] for row in keys_rows]
    rows[0] = [Paragraph(c, ST["table_header"]) for c in keys_rows[0]]
    tbl = Table(rows, colWidths=[6*cm, 11*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, CREAM_WARM]),
    ]))
    s.append(tbl)
    s.append(PageBreak())

    # ============================================================
    # ANHANG C — Dateibaum
    # ============================================================
    s += chapter_head("Anhang C", "Dateibaum deiner Website",
                      kicker="Wo finde ich was?")
    s.append(Paragraph(
        "Ein Überblick: welche Datei wozu ist und wo welcher Inhalt steht.",
        ST["lead"]))

    file_rows = [
        ["<b>Datei</b>", "<b>Was drinsteht</b>"],
        ["index.html", "Startseite — Hero-Slideshow, Mission, Projekt-Karten, Stats."],
        ["ueber-uns.html", "Vereinsgeschichte (Margit Schnees Reise 1996), Vorstand."],
        ["projekte.html", "Übersicht aller Projekte; verlinkt auf Detailseiten."],
        ["projekte/laborantenkolleg-bashanet.html", "BNHCHS — Laboranten-Kolleg."],
        ["projekte/clinical-medicine.html", "Clinical-Medicine-Studiengang."],
        ["projekte/sanu-tec.html", "Sanu Tec Sekundarschule, Speisesaal."],
        ["projekte/madunga-girls-school.html", "Madunga Girls School — Einfriedung."],
        ["projekte/student-support.html", "Stipendienprogramm. Salome-Doriya-Anekdote."],
        ["partner.html", "Bischof Antony, Sr. Basilisa, Fr. Karama, Diözese Mbulu."],
        ["aktuelles.html", "Neuigkeiten — Kunstauktion 2024, Clinical Medicine."],
        ["unterstuetzen.html", "<b>Spendenkonto, IBAN, Mitgliedschaft, Beträge.</b>"],
        ["ihre-spende-kommt-an.html", "Transparenz — wie Spenden ankommen."],
        ["bildergalerie.html", "Galerie nach Themen (Land, Gesundheit, Schulen, ...)."],
        ["kontakt.html", "Kontaktformular, Anschrift, Rolfs Daten."],
        ["impressum.html", "Pflichtangaben (Anbieter, Registernummer)."],
        ["datenschutz.html", "DSGVO-Erklärung."],
        ["en/", "Englische Versionen — gleiche Inhalte, anderer Sprache."],
        ["css/style.css", "<b>Alle Stilangaben — Farben, Schriften, Layout.</b>"],
        ["js/main.js", "Diashow, Menü auf/zu, Lightbox in der Galerie."],
        ["assets/images/", "<b>Alle Fotos.</b> Hier kommen neue Bilder rein."],
    ]
    rows = [[Paragraph(c, ST["table_code"] if i > 0 and j == 0 else ST["table_cell"])
             for j, c in enumerate(row)] for i, row in enumerate(file_rows)]
    rows[0] = [Paragraph(c, ST["table_header"]) for c in file_rows[0]]
    tbl = Table(rows, colWidths=[8*cm, 9*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TERRACOTTA),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, CREAM_WARM]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, LINE),
    ]))
    s.append(tbl)

    s.append(Spacer(1, 18))
    s.append(HorizontalRule(thickness=1, color=TERRACOTTA))
    s.append(Spacer(1, 10))
    s.append(Paragraph(
        "<b>Und falls etwas hängenbleibt</b> — ruf an. Lieber einmal zu oft.",
        ST["lead"]))
    s.append(Spacer(1, 30))
    s.append(Paragraph("Viel Freude beim Schrauben.", ST["cover_subtitle"]))
    s.append(Spacer(1, 4))
    s.append(Paragraph("— Thomas", ST["cover_meta"]))

    return s


# ============================================================
# Build the document
# ============================================================
def build(out_path="Kusaidia-Handbuch.pdf"):
    doc = HandbuchDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2.4 * cm,
        rightMargin=2.4 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.0 * cm,
        title="Kusaidia Afrika - Handbuch fuer die Website",
        author="Thomas Beyer",
        subject="Anleitung zur Pflege der Kusaidia-Afrika-Website",
    )

    # Frame for content pages
    content_frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        showBoundary=0,
    )
    cover_frame = Frame(
        2.2 * cm, 1.5 * cm,
        PAGE_W - 4.4 * cm, PAGE_H - 3 * cm,
        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0,
        showBoundary=0,
    )

    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
        PageTemplate(id="content", frames=[content_frame], onPage=draw_page_chrome),
    ])

    story = build_story()
    doc.build(story)
    print(f"OK — wrote {out_path}")


if __name__ == "__main__":
    build()
