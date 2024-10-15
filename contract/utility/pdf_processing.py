# pd-enem/contract/utility/pdf_processing.py
import PyPDF2
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf):
    text = ""
    reader = PyPDF2.PdfReader(pdf)
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_image(pdf_path):
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

def extract_data_from_text(text):
    nome = "Não encontrado"
    cpf = "Não encontrado"
    nota_matematica = "Não encontrado"
    nota_redacao = "Não encontrado"
    return nome, cpf, nota_matematica, nota_redacao

def calculate_scores(nota_matematica, nota_redacao):
    try:
        nota_matematica_float = float(nota_matematica.replace(',', '.'))
        nota_redacao_float = float(nota_redacao.replace(',', '.'))
        total = nota_matematica_float + nota_redacao_float
        nota_geral = (nota_matematica_float * 80 + nota_redacao_float * 20) / 100
        return total, nota_geral
    except ValueError:
        return "Erro ao calcular a soma das notas.", "Erro ao calcular a nota geral."
