import csv
import io
import json
from pathlib import Path


def extract_text_from_bytes(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()

    if ext in ('.txt', ''):
        try:
            return data.decode('utf-8')
        except Exception:
            return data.decode('latin-1', errors='ignore')

    if ext == '.json':
        try:
            obj = json.loads(data.decode('utf-8'))
            return json.dumps(obj, ensure_ascii=False)
        except Exception:
            try:
                return data.decode('utf-8', errors='ignore')
            except Exception:
                return ''

    if ext == '.csv':
        try:
            content = data.decode('utf-8')
        except Exception:
            content = data.decode('latin-1', errors='ignore')

        rows = csv.reader(io.StringIO(content))
        return '\n'.join(' '.join(row) for row in rows)

    if ext == '.docx':
        try:
            from docx import Document

            doc = Document(io.BytesIO(data))
            return '\n'.join(paragraph.text for paragraph in doc.paragraphs if paragraph.text)
        except Exception:
            return ''

    if ext == '.pdf':
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(io.BytesIO(data))
            pages = []
            for page in reader.pages:
                try:
                    pages.append(page.extract_text() or '')
                except Exception:
                    pages.append('')
            return '\n'.join(pages)
        except Exception:
            return ''

    try:
        return data.decode('utf-8', errors='ignore')
    except Exception:
        return ''
