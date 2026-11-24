#!/usr/bin/env python3
"""Generate synchronized English and Ukrainian CV PDFs from structured source text."""
import base64
import bz2
import html
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, KeepTogether, PageBreak, PageTemplate, Paragraph,
)

FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
pdfmetrics.registerFont(TTFont('CVRegular', str(FONT_DIR / 'DejaVuSansCondensed.ttf')))
pdfmetrics.registerFont(TTFont('CVBold', str(FONT_DIR / 'DejaVuSansCondensed-Bold.ttf')))
pdfmetrics.registerFont(TTFont('CVOblique', str(FONT_DIR / 'DejaVuSansCondensed-Oblique.ttf')))
NAVY = colors.HexColor('#102c48')
TEAL = colors.HexColor('#0d687a')
SLATE = colors.HexColor('#61717e')
RULE = colors.HexColor('#b5c5ce')
W, H = A4

ST = {
    'NameCV': ParagraphStyle('name', fontName='CVBold', fontSize=20, leading=24, textColor=NAVY, spaceAfter=5),
    'TagCV': ParagraphStyle('tag', fontName='CVBold', fontSize=9.8, leading=12.3, textColor=TEAL, spaceAfter=3),
    'ContactCV': ParagraphStyle('contact', fontName='CVRegular', fontSize=8.4, leading=10.4, textColor=SLATE, spaceAfter=3),
    'AvailabilityCV': ParagraphStyle('availability', fontName='CVBold', fontSize=9, leading=11.5, textColor=TEAL, spaceAfter=8),
    'SectionCV': ParagraphStyle('section', fontName='CVBold', fontSize=10.3, leading=12.3, textColor=TEAL, spaceBefore=7, spaceAfter=4),
    'PositionCV': ParagraphStyle('position', fontName='CVBold', fontSize=9.6, leading=12.2, textColor=NAVY, spaceBefore=5),
    'OrgCV': ParagraphStyle('org', fontName='CVRegular', fontSize=8.4, leading=10.4, textColor=SLATE, spaceAfter=3),
    'BulletCV': ParagraphStyle('bullet', fontName='CVRegular', fontSize=8.45, leading=11.6, textColor=NAVY, leftIndent=12, firstLineIndent=-8, spaceAfter=2),
    'BodyCV': ParagraphStyle('body', fontName='CVRegular', fontSize=8.6, leading=12, textColor=NAVY, spaceAfter=3),
    'NoteCV': ParagraphStyle('note', fontName='CVOblique', fontSize=7.8, leading=10.2, textColor=SLATE, spaceAfter=3),
}

def footer(canvas, doc, locale):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(.4)
    canvas.line(43, 27, W - 43, 27)
    canvas.setFillColor(SLATE)
    canvas.setFont('CVRegular', 7.4)
    name = 'SERHII NABOK' if locale == 'en' else 'СЕРГІЙ НАБОК'
    canvas.drawRightString(W - 45, 17, f'{name}  |  {doc.page}')
    canvas.restoreState()

def build(locale, rows, output):
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=45, rightMargin=45,
                          topMargin=37, bottomMargin=43, title='Serhii Nabok | CV', author='Serhii Nabok')
    frame = Frame(45, 42, W - 90, H - 77, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='default', frames=frame, onPage=lambda c, d: footer(c, d, locale))])
    content = []
    for style, string in rows:
        if not string.strip():
            content.append(PageBreak())
            continue
        s = html.escape(string).replace('•', '&#8226;')
        para = Paragraph(s, ST.get(style, ST['BodyCV']))
        if style == 'SectionCV':
            content.append(KeepTogether([para, HRFlowable(width='100%', thickness=.5, color=RULE, spaceAfter=2)]))
        else:
            content.append(para)
    doc.build(content)

if __name__ == '__main__':
    source = Path('.github/cv-source.json.bz2.b64')
    rows = json.loads(bz2.decompress(base64.b64decode(source.read_text().strip())))
    assert set(rows) == {'en', 'ua'}
    for locale, filename in [('en', 'cv.pdf'), ('ua', 'cv-ua.pdf')]:
        build(locale, rows[locale], Path(filename))
        assert Path(filename).stat().st_size > 20_000
        print(f'Generated {filename}: {Path(filename).stat().st_size:,} bytes')
