import os
import json
import urllib.request
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Set output paths relative to current script
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CODE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

VERSES_URL = "https://raw.githubusercontent.com/praneshp1org/Bhagavad-Gita-JSON-data/main/verse.json"
TRANSLATIONS_URL = "https://raw.githubusercontent.com/praneshp1org/Bhagavad-Gita-JSON-data/main/translation.json"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Skip title page
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#7F8C8D"))
        
        # Draw running header
        self.drawString(54, 750, "Srimad Bhagavad Gita - Sanskrit Document RAG System")
        self.setStrokeColor(colors.HexColor("#BDC3C7"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Draw running footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "Confidential - Academic RAG System Ingestion")
        self.line(54, 52, 558, 52)
        
        self.restoreState()

def download_data():
    print("Downloading raw Sanskrit verses data...")
    try:
        req = urllib.request.Request(VERSES_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            verses_data = json.loads(r.read().decode('utf-8-sig'))
        print(f"Downloaded {len(verses_data)} verses.")
    except Exception as e:
        print(f"Error downloading verses: {e}")
        sys.exit(1)

    print("Downloading raw translations data...")
    try:
        req = urllib.request.Request(TRANSLATIONS_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            translations_data = json.loads(r.read().decode('utf-8-sig'))
        print(f"Downloaded {len(translations_data)} translations.")
    except Exception as e:
        print(f"Error downloading translations: {e}")
        sys.exit(1)

    return verses_data, translations_data

def process_and_merge(verses, translations):
    print("Merging verses and translations...")
    
    # Map verse_id -> translations list
    trans_map = {}
    for t in translations:
        v_id = t.get("verse_id")
        if v_id not in trans_map:
            trans_map[v_id] = []
        trans_map[v_id].append(t)
        
    merged = []
    
    # We sort verses by chapter_number and verse_number
    verses_sorted = sorted(verses, key=lambda x: (x.get("chapter_number", 0), x.get("verse_number", 0)))
    
    for v in verses_sorted:
        v_id = v.get("id") or v.get("verse_id")
        
        # Find translations for this verse
        v_trans = trans_map.get(v_id, [])
        
        # We prefer English translations by Swami Sivananda or Swami Gambhirananda
        eng_trans = ""
        hindi_trans = ""
        
        # Let's search for Swami Sivananda first, then any english
        for t in v_trans:
            if t.get("lang") == "english":
                author = t.get("authorName", "").lower()
                desc = t.get("description", "").strip()
                if "sivananda" in author:
                    eng_trans = desc
                    break
                elif not eng_trans:
                    eng_trans = desc
                    
        # Let's search for Hindi translations (e.g. Swami Adgadanand or similar)
        for t in v_trans:
            if t.get("lang") == "hindi":
                desc = t.get("description", "").strip()
                if not hindi_trans:
                    hindi_trans = desc
                    
        # Clean text lines (remove excessive whitespace)
        v_text = v.get("text", "").strip()
        v_text = "\n".join([line.strip() for line in v_text.split("\n") if line.strip()])
        
        v_meanings = v.get("word_meanings", "").strip()
        v_meanings = "\n".join([line.strip() for line in v_meanings.split("\n") if line.strip()])

        merged.append({
            "verse_id": v_id,
            "chapter_number": v.get("chapter_number"),
            "verse_number": v.get("verse_number"),
            "text": v_text,
            "transliteration": v.get("transliteration", "").strip(),
            "word_meanings": v_meanings,
            "english_translation": eng_trans,
            "hindi_translation": hindi_trans
        })
        
    # Write processed JSON
    output_json = os.path.join(DATA_DIR, "gita_processed.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"Processed dataset written to {output_json}")
    
    return merged

def generate_txt_corpus(merged_data):
    print("Generating TXT corpus...")
    corpus_path = os.path.join(DATA_DIR, "bhagavad_gita_corpus.txt")
    
    with open(corpus_path, "w", encoding="utf-8") as f:
        f.write("SRIMAD BHAGAVAD GITA - CORPUS FOR SANSKRIT RAG SYSTEM\n")
        f.write("=" * 60 + "\n\n")
        
        current_chap = 0
        for item in merged_data:
            c_num = item["chapter_number"]
            v_num = item["verse_number"]
            
            if c_num != current_chap:
                current_chap = c_num
                f.write(f"\nCHAPTER {current_chap}\n")
                f.write("-" * 40 + "\n\n")
                
            f.write(f"Chapter {c_num}, Verse {v_num}\n")
            f.write(f"Sanskrit Text:\n{item['text']}\n\n")
            f.write(f"Transliteration:\n{item['transliteration']}\n\n")
            if item['word_meanings']:
                f.write(f"Word Meanings:\n{item['word_meanings']}\n\n")
            if item['english_translation']:
                f.write(f"English Translation:\n{item['english_translation']}\n\n")
            if item['hindi_translation']:
                f.write(f"Hindi Translation:\n{item['hindi_translation']}\n\n")
            f.write("*" * 30 + "\n\n")
            
    print(f"TXT corpus written to {corpus_path}")

def generate_pdf_corpus(merged_data):
    print("Generating PDF corpus using ReportLab...")
    pdf_path = os.path.join(DATA_DIR, "bhagavad_gita_corpus.pdf")
    
    # Setup document
    # Top and bottom margins are 1 inch (72 points), side margins are 0.75 in (54 pt)
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    # Primary accent color: Deep Saffron (Hex #D35400)
    # Secondary: Charcoal (Hex #2C3E50)
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor("#D35400"),
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#2C3E50"),
        alignment=TA_CENTER
    )
    
    info_style = ParagraphStyle(
        'CoverInfo',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#7F8C8D"),
        alignment=TA_CENTER
    )
    
    chap_header_style = ParagraphStyle(
        'ChapHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#D35400"),
        spaceBefore=15,
        spaceAfter=15,
        alignment=TA_CENTER
    )
    
    verse_num_style = ParagraphStyle(
        'VerseNum',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#2C3E50"),
        spaceBefore=10,
        spaceAfter=5
    )
    
    sanskrit_style = ParagraphStyle(
        'SanskritText',
        parent=styles['Normal'],
        fontName='Helvetica',  # Standard Helvetica handles basic latin, but for Devanagari we rely on PDF viewer decoding/embedding or standard text
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#16A085"), # Teal for Sanskrit script
        leftIndent=15,
        spaceAfter=5
    )
    
    translit_style = ParagraphStyle(
        'TranslitText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2980B9"), # Blue for transliteration
        leftIndent=15,
        spaceAfter=5
    )
    
    meaning_style = ParagraphStyle(
        'MeaningText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#7F8C8D"),
        leftIndent=15,
        spaceAfter=5
    )
    
    trans_style = ParagraphStyle(
        'TranslationText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2C3E50"),
        leftIndent=15,
        spaceAfter=10
    )

    story = []
    
    # COVER PAGE
    story.append(Spacer(1, 100))
    story.append(Paragraph("Srimad Bhagavad Gita", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Sanskrit Document Corpus for RAG System Ingestion", subtitle_style))
    story.append(Spacer(1, 150))
    story.append(Paragraph("Fully processed dataset of all 18 Chapters and 700 Verses", info_style))
    story.append(Paragraph("Includes Devanagari text, Transliteration, Word Meanings & Translations", info_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Ingested on: July 2026", info_style))
    story.append(PageBreak())
    
    # CONTENT PAGES
    current_chap = 0
    
    for item in merged_data:
        c_num = item["chapter_number"]
        v_num = item["verse_number"]
        
        # Chapter header
        if c_num != current_chap:
            current_chap = c_num
            story.append(PageBreak())
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"CHAPTER {current_chap}", chap_header_style))
            story.append(Spacer(1, 10))
            
        # Group each verse details to avoid awkward page breaks within a verse
        verse_elements = []
        verse_elements.append(Paragraph(f"Chapter {c_num}, Verse {v_num}", verse_num_style))
        
        # Devanagari Sanskrit
        # Convert newline to <br/> for ReportLab Paragraph
        sans_html = item['text'].replace("\n", "<br/>")
        verse_elements.append(Paragraph(f"<b>Sanskrit:</b><br/>{sans_html}", sansanskrit_style_hack := ParagraphStyle('Sanskrit', parent=sanskrit_style)))
        
        # Transliteration
        translit_html = item['transliteration'].replace("\n", "<br/>")
        verse_elements.append(Paragraph(f"<b>Transliteration:</b><br/>{translit_html}", translit_style))
        
        # Word meanings
        if item['word_meanings']:
            meanings_html = item['word_meanings'].replace("\n", "<br/>")
            verse_elements.append(Paragraph(f"<b>Word Meanings:</b><br/>{meanings_html}", meaning_style))
            
        # English translation
        if item['english_translation']:
            verse_elements.append(Paragraph(f"<b>Translation (English):</b><br/>{item['english_translation']}", trans_style))
            
        # Add separator line
        verse_elements.append(Spacer(1, 5))
        
        story.append(KeepTogether(verse_elements))
        story.append(Spacer(1, 15))
        
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF corpus compiled at {pdf_path}")

if __name__ == "__main__":
    verses, translations = download_data()
    merged = process_and_merge(verses, translations)
    generate_txt_corpus(merged)
    generate_pdf_corpus(merged)
    print("\nIngestion completed successfully!")
