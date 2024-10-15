from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import os
from django.conf import settings
from io import BytesIO

def gerar_pdf(nome_aluno, nome_diretor, nome_escola, data, media_ensino_medio):
    # Caminho do PDF original
    pdf_template_path = os.path.join(settings.MEDIA_ROOT, 'templates_pdf', 'Manipulado_Carta.pdf')

    # Ler o PDF original
    reader = PdfReader(pdf_template_path)
    writer = PdfWriter()

    # Buffer para armazenar o PDF modificado
    buffer = BytesIO()

    for page in reader.pages:
        content = page.extract_text()

        # Substituir os placeholders pelos valores fornecidos
        content = content.replace("eduzin", nome_aluno)
        content = content.replace("Edu", nome_diretor)
        content = content.replace("Escola do edu", nome_escola)
        content = content.replace("2024-06-14", data)
        content = content.replace("1000", str(media_ensino_medio))

        # Adicionar conteúdo modificado ao writer
        writer.add_page(page)

    # Gerar caminho de saída para o PDF
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f'carta_gerada_{nome_aluno}.pdf')

    # Escrever o novo PDF no buffer
    writer.write(buffer)
    buffer.seek(0)

    # Salvar o novo PDF no caminho de saída
    with open(pdf_output_path, 'wb') as output_pdf:
        output_pdf.write(buffer.read())

    return pdf_output_path
