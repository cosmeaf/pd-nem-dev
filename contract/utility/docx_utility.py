import os
import uuid
import subprocess  # Importar subprocess
from docx import Document
from django.conf import settings

def manipular_docx(nome_aluno, nome_diretor, nome_escola, endereco_escola, data, media):
    # Caminho do template fixo do documento DOCX
    template_path = os.path.join(settings.BASE_DIR, 'contract', 'templates_documents', 'Carta.docx')

    # Verifique se o arquivo existe
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Arquivo {template_path} não encontrado.")

    # Carregar o template do documento
    doc = Document(template_path)

    # Substituir os placeholders no documento
    for p in doc.paragraphs:
        if '[Nome do Aluno]' in p.text:
            p.text = p.text.replace('[Nome do Aluno]', nome_aluno)
        if '[Nome do Diretor ou Diretora]' in p.text:
            p.text = p.text.replace('[Nome do Diretor ou Diretora]', nome_diretor)
        if '[Nome da Escola]' in p.text:
            p.text = p.text.replace('[Nome da Escola]', nome_escola)
        if '[Endereço Completo da Escola]' in p.text:  # Novo campo de endereço
            p.text = p.text.replace('[Endereço Completo da Escola]', endereco_escola)
        if '[Data]' in p.text:
            p.text = p.text.replace('[Data]', data)
        if '[Nota]' in p.text:
            p.text = p.text.replace('[Nota]', media)

    # Gerar um UUID para o nome do arquivo
    unique_filename = f'carta_gerada_{uuid.uuid4()}.docx'
    pdf_filename = unique_filename.replace('.docx', '.pdf')

    # Caminho para salvar o arquivo na pasta media/documents/
    docx_output_path = os.path.join(settings.MEDIA_ROOT, 'documents', unique_filename)
    pdf_output_path = os.path.join(settings.MEDIA_ROOT, 'documents', pdf_filename)

    # Salvar o documento manipulado como DOCX
    doc.save(docx_output_path)

    # Converter DOCX para PDF usando LibreOffice
    command = ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', os.path.dirname(pdf_output_path), docx_output_path]
    subprocess.run(command, check=True)

    return pdf_output_path
