from pathlib import Path

from fpdf import FPDF


PDF_PATH = Path(__file__).resolve().parent / 'test_files' / 'test_project.pdf'
FONT_PATH = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')


if not FONT_PATH.exists():
    raise SystemExit(f'Font not found: {FONT_PATH}')


pdf = FPDF()
pdf.add_page()
pdf.add_font('DejaVu', '', str(FONT_PATH), uni=True)
pdf.set_font('DejaVu', size=12)
pdf.cell(0, 10, 'Проект: Система CRM', ln=1)
pdf.cell(0, 10, 'Описание: Авторизация, задачи, экспорт CSV, веб-интерфейс.', ln=1)
pdf.cell(0, 10, 'Стек: FastAPI, Next.js, PostgreSQL', ln=1)
pdf.output(str(PDF_PATH))
print(f'updated {PDF_PATH}')
