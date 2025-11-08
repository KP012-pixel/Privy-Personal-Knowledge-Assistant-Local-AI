"""
Simple ingestion utilities:
- extract text from PDF (with OCR fallback)
- extract text from DOCX
- basic cleaning & chunking with list-preserving rules
Outputs a list of dicts: {id, source, page, chunk_id, text}
"""

from pypdf import PdfReader
from pdf2image import convert_from_path
from docx import Document
import pytesseract
import re
import uuid

# Chunking config (token-like by approximate words)
MIN_CHUNK_WORDS = 80
MAX_CHUNK_WORDS = 300

list_item_re = re.compile(r'^\s*([-•*]|\d+[\.\)])\s+', re.MULTILINE)

def _split_preserve_lists(text):
    """
    If text contains list markers, split into list items; otherwise leave as single block.
    """
    items = []
    parts = list_item_re.split(text)
    if len(parts) <= 1:
        return [text.strip()]
    # Reconstruct by scanning lines
    current = []
    for line in text.splitlines():
        if list_item_re.match(line):
            if current:
                items.append("\n".join(current).strip())
            current = [line.strip()]
        else:
            current.append(line)
    if current:
        items.append("\n".join(current).strip())
    # Filter out tiny empties
    items = [i for i in items if i and len(i.split()) > 3]
    return items or [text.strip()]

def _smart_chunk(text):
    """
    Chunk text into semantically-sized pieces while preserving detected list items.
    """
    text = text.strip()
    if not text:
        return []
    # If appears to be a list-like block, preserve items
    if list_item_re.search(text):
        items = _split_preserve_lists(text)
        chunks = []
        for it in items:
            words = it.split()
            if len(words) <= MAX_CHUNK_WORDS:
                chunks.append(it)
            else:
                # further slice long items by sentence
                sents = re.split(r'(?<=[.!?])\s+', it)
                cur = []
                for s in sents:
                    cur.extend(s.split())
                    if len(cur) >= MIN_CHUNK_WORDS:
                        chunks.append(" ".join(cur))
                        cur = []
                if cur:
                    chunks.append(" ".join(cur))
        return chunks
    # Regular text: chunk by approximate word count
    words = text.split()
    if len(words) <= MAX_CHUNK_WORDS:
        return [text]
    chunks = []
    cur = []
    for w in words:
        cur.append(w)
        if len(cur) >= MAX_CHUNK_WORDS:
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks

def extract_text_from_pdf(path):
    """
    Returns list of {'page': int, 'text': str}
    Uses PdfReader.extract_text() first; if empty for a page, falls back to OCR via pdf2image+pytesseract.
    """
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        txt = ""
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if not txt.strip():
            # Fallback to OCR for this page
            try:
                images = convert_from_path(path, first_page=i+1, last_page=i+1)
                if images:
                    txt = pytesseract.image_to_string(images[0])
            except Exception as e:
                txt = ""
        pages.append({'page': i+1, 'text': txt})
    return pages

def extract_text_from_docx(path):
    doc = Document(path)
    full = []
    for para in doc.paragraphs:
        full.append(para.text)
    return "\n".join(full)

def ingest_document(path, source_name=None):
    """
    High-level: ingest path (pdf/docx/txt) and return list of chunk dicts.
    """
    source = source_name or path
    chunks_out = []
    uid_base = uuid.uuid4().hex[:8]
    if path.lower().endswith(".pdf"):
        pages = extract_text_from_pdf(path)
        for p in pages:
            page_no = p['page']
            text = p['text'] or ""
            # cleaning: remove multiple newlines
            text = re.sub(r'\n{2,}', '\n', text).strip()
            for idx, c in enumerate(_smart_chunk(text)):
                chunk_id = f"{uid_base}-p{page_no}-c{idx}"
                chunks_out.append({
                    "id": chunk_id,
                    "source": source,
                    "page": page_no,
                    "chunk_id": chunk_id,
                    "text": c
                })
    elif path.lower().endswith(".docx"):
        text = extract_text_from_docx(path)
        text = re.sub(r'\n{2,}', '\n', text).strip()
        for idx, c in enumerate(_smart_chunk(text)):
            chunk_id = f"{uid_base}-d1-c{idx}"
            chunks_out.append({
                "id": chunk_id, "source": source, "page": 1, "chunk_id": chunk_id, "text": c
            })
    else:
        # plain text fallback
        with open(path, 'r', encoding='utf8') as f:
            text = f.read()
        text = re.sub(r'\n{2,}', '\n', text).strip()
        for idx, c in enumerate(_smart_chunk(text)):
            chunk_id = f"{uid_base}-t1-c{idx}"
            chunks_out.append({
                "id": chunk_id, "source": source, "page": 1, "chunk_id": chunk_id, "text": c
            })
    return chunks_out
