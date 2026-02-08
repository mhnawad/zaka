from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
import os


def _reshape_ar(text):
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def generate_pdf(filename, estate, explanation):
    styles = getSampleStyleSheet()

    # Try to register a common Arabic-capable TTF (DejaVu Sans as fallback if available)
    font_name = None
    possible_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', p))
                font_name = 'DejaVuSans'
                break
            except Exception:
                font_name = None

    if font_name:
        styles["Normal"].fontName = font_name

    doc = SimpleDocTemplate(filename)
    story = []

    story.append(Paragraph(_reshape_ar(f"قيمة التركة: {estate}"), styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    for line in explanation:
        story.append(Paragraph(_reshape_ar(line), styles["Normal"]))
        story.append(Paragraph("<br/>", styles["Normal"]))

    doc.build(story)
