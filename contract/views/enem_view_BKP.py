import os
import tempfile
from django.shortcuts import render, redirect
from contract.forms import EnemPDFUploadForm
import PyPDF2
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf):
    """
    Extrai o texto de um PDF baseado em texto.
    """
    text = ""
    reader = PyPDF2.PdfReader(pdf)
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_image(pdf_path):
    """
    Extrai o texto de um PDF baseado em imagem usando OCR.
    """
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

def extract_data_from_text(text):
    """
    Lógica para extrair os dados necessários do texto.
    """
    nome = None
    cpf = None
    nota_matematica = None
    nota_redacao = None

    # Extração do nome e CPF
    if "Nome:" in text:
        nome = text.split("Nome:")[1].split("\n")[0].strip()
    if "CPF:" in text:
        cpf = text.split("CPF:")[1].split("\n")[0].strip()

    # Melhorando a busca por notas
    if "Matemática" in text or "Matematica" in text:
        try:
            if "Matemática e suas Tecnologias" in text:
                nota_matematica = text.split("Matemática e suas Tecnologias")[1].split("\n")[0].strip().split()[0]
            elif "Matematica e suas Tecnologias" in text:
                nota_matematica = text.split("Matematica e suas Tecnologias")[1].split("\n")[0].strip().split()[0]
        except IndexError:
            nota_matematica = None
    
    if "Redação" in text or "Redacao" in text:
        try:
            if "Redação" in text:
                nota_redacao = text.split("Redação")[1].split("\n")[0].strip().split()[0]
            elif "Redacao" in text:
                nota_redacao = text.split("Redacao")[1].split("\n")[0].strip().split()[0]
        except IndexError:
            nota_redacao = None

    return nome, cpf, nota_matematica, nota_redacao

def calculate_scores(nota_matematica, nota_redacao):
    """
    Calcula a soma das notas e a nota geral ponderada (peso 80 para Matemática e peso 20 para Redação).
    """
    try:
        # Verifica se as notas estão presentes
        if nota_matematica is None or nota_redacao is None:
            raise ValueError("Notas de matemática ou redação estão ausentes.")
        
        # Converter as notas de string para float
        nota_matematica_float = float(nota_matematica.replace(',', '.'))
        nota_redacao_float = float(nota_redacao.replace(',', '.'))

        # Calcular a soma das notas
        total = nota_matematica_float + nota_redacao_float

        # Calcular a nota geral ponderada
        nota_geral = (nota_matematica_float * 80 + nota_redacao_float * 20) / 100

        return total, nota_geral
    except (ValueError, TypeError) as e:
        return None, None  # Retorna None caso haja erro na conversão

# Função auxiliar para normalizar CPFs (remover pontos e traços)
def normalize_cpf(cpf):
    if cpf:
        return cpf.replace('.', '').replace('-', '').strip()
    return None

def enem_view(request):
    if request.method == 'POST':
        form = EnemPDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = request.FILES['pdf_file']

            # Criar um arquivo temporário para salvar o PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(pdf.read())
                temp_pdf_path = temp_pdf.name

            try:
                # Identificar o tipo de PDF (baseado em texto ou imagem)
                try:
                    text = extract_text_from_pdf(pdf)
                    if text.strip():
                        print("PDF baseado em texto identificado.")
                    else:
                        raise ValueError("PDF sem texto, tentando OCR.")
                except Exception as e:
                    print(f"Tentando OCR: {str(e)}")
                    text = extract_text_from_image(temp_pdf_path)

                # Extrair os dados
                nome, cpf, nota_matematica, nota_redacao = extract_data_from_text(text)

                # Verifica se o CPF foi extraído corretamente
                if cpf is None:
                    return render(request, 'confirm_error.html', {
                        'message': 'Não foi possível extrair o CPF do PDF. Verifique o arquivo e tente novamente.'
                    })

                # Normalizar o CPF extraído do PDF
                cpf_normalizado = normalize_cpf(cpf)
                # Recuperar e normalizar o CPF da sessão
                cpf_sessao = normalize_cpf(request.session.get('cpf'))

                # Debug: Imprimir CPFs para verificar
                print(f"CPF da sessão (normalizado): {cpf_sessao}")
                print(f"CPF do arquivo (normalizado): {cpf_normalizado}")

                # Comparar o CPF extraído com o CPF da sessão
                if cpf_normalizado != cpf_sessao:
                    return render(request, 'confirm_error.html', {
                        'message': 'O CPF no arquivo não corresponde ao CPF fornecido. Verifique o arquivo e tente novamente.'
                    })

                # Calcular a soma das notas e a nota geral
                total_score, nota_geral = calculate_scores(nota_matematica, nota_redacao)

                # Verifica se a nota geral foi calculada
                if total_score is None or nota_geral is None:
                    return render(request, 'confirm_error.html', {
                        'message': 'Não foi possível calcular as notas. Verifique o arquivo e tente novamente.'
                    })

                # Armazenar os dados na sessão para a próxima etapa
                request.session['ocr_text'] = text
                request.session['nome'] = nome
                request.session['cpf_extraido'] = cpf_normalizado
                request.session['nota_matematica'] = nota_matematica
                request.session['nota_redacao'] = nota_redacao
                request.session['nota_geral'] = nota_geral

                # Redirecionar para a view de resultados
                return redirect('enem_result_view')

            except Exception as e:
                print(f"Erro ao processar o PDF: {str(e)}")
                return render(request, 'enem_upload.html', {'form': form, 'error': str(e)})

            finally:
                # Remover o arquivo temporário
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

    else:
        form = EnemPDFUploadForm()

    return render(request, 'enem_upload.html', {'form': form})
