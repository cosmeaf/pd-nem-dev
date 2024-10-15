import os
import tempfile
import PyPDF2
import pytesseract
from django.shortcuts import render, redirect
from contract.forms import EnemPDFUploadForm
from contract.views.messages_view import render_message
from pdf2image import convert_from_path
import logging

logger = logging.getLogger('django')

def extract_text_from_pdf(pdf):
    """
    Extrai o texto de um PDF baseado em texto.
    """
    logger.info("Iniciando a extração de texto do PDF baseado em texto...")
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf)
        for page in reader.pages:
            text += page.extract_text()
        logger.info("Texto extraído com sucesso do PDF baseado em texto.")
    except Exception as e:
        logger.error(f"Erro ao extrair texto do PDF baseado em texto: {e}")
    return text

def extract_text_from_image(pdf_path):
    """
    Extrai o texto de um PDF baseado em imagem usando OCR.
    """
    logger.info("Iniciando a extração de texto do PDF baseado em imagem usando OCR...")
    text = ""
    try:
        pages = convert_from_path(pdf_path)
        for page in pages:
            text += pytesseract.image_to_string(page)
        logger.info("Texto extraído com sucesso do PDF baseado em imagem.")
    except Exception as e:
        logger.error(f"Erro ao extrair texto de imagem usando OCR: {e}")
    return text

def extract_data_from_text(text):
    """
    Lógica para extrair os dados necessários do texto.
    """
    logger.info("Iniciando a extração dos dados do texto...")
    nome = None
    cpf = None
    nota_matematica = None
    nota_redacao = None

    # Extração do nome e CPF
    if "Nome:" in text:
        nome = text.split("Nome:")[1].split("\n")[0].strip()
        logger.info(f"Nome extraído: {nome}")
    if "CPF:" in text:
        cpf = text.split("CPF:")[1].split("\n")[0].strip()
        logger.info(f"CPF extraído: {cpf}")

    # Extração das notas
    if "Matemática" in text or "Matematica" in text:
        try:
            if "Matemática e suas Tecnologias" in text:
                nota_matematica = text.split("Matemática e suas Tecnologias")[1].split("\n")[0].strip().split()[0]
            elif "Matematica e suas Tecnologias" in text:
                nota_matematica = text.split("Matematica e suas Tecnologias")[1].split("\n")[0].strip().split()[0]
            logger.info(f"Nota de Matemática extraída: {nota_matematica}")
        except IndexError:
            nota_matematica = None
    
    if "Redação" in text or "Redacao" in text:
        try:
            if "Redação" in text:
                nota_redacao = text.split("Redação")[1].split("\n")[0].strip().split()[0]
            elif "Redacao" in text:
                nota_redacao = text.split("Redacao")[1].split("\n")[0].strip().split()[0]
            logger.info(f"Nota de Redação extraída: {nota_redacao}")
        except IndexError:
            nota_redacao = None

    return nome, cpf, nota_matematica, nota_redacao

def calculate_scores(nota_matematica, nota_redacao):
    """
    Calcula a soma das notas e a nota geral ponderada (peso 80 para Matemática e peso 20 para Redação).
    """
    logger.info("Iniciando o cálculo das notas...")
    try:
        if nota_matematica is None or nota_redacao is None:
            raise ValueError("Notas de matemática ou redação estão ausentes.")

        # Converter as notas de string para float
        nota_matematica_float = float(nota_matematica.replace(',', '.'))
        nota_redacao_float = float(nota_redacao.replace(',', '.'))

        # Calcular a soma das notas
        total = nota_matematica_float + nota_redacao_float
        nota_geral = (nota_matematica_float * 80 + nota_redacao_float * 20) / 100

        logger.info(f"Soma das notas: {total}, Nota geral ponderada: {nota_geral}")
        return total, nota_geral
    except (ValueError, TypeError) as e:
        logger.error(f"Erro ao calcular as notas: {e}")
        return None, None

# Função auxiliar para normalizar CPFs (remover pontos e traços)
def normalize_cpf(cpf):
    if cpf:
        return cpf.replace('.', '').replace('-', '').strip()
    return None

def enem_upload_view(request):
    if request.method == 'POST':
        logger.info("Recebendo arquivo de upload do ENEM.")
        form = EnemPDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = request.FILES['pdf_file']

            # Criar um arquivo temporário para salvar o PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                temp_pdf.write(pdf.read())
                temp_pdf_path = temp_pdf.name
                logger.info(f"Arquivo PDF salvo temporariamente em: {temp_pdf_path}")

            try:
                # Identificar o tipo de PDF (baseado em texto ou imagem)
                try:
                    text = extract_text_from_pdf(pdf)
                    if text.strip():
                        logger.info("PDF baseado em texto identificado.")
                    else:
                        raise ValueError("PDF sem texto, tentando OCR.")
                except Exception as e:
                    logger.info(f"Tentando OCR: {str(e)}")
                    text = extract_text_from_image(temp_pdf_path)

                # Extrair os dados
                nome, cpf, nota_matematica, nota_redacao = extract_data_from_text(text)

                # Verificar se o CPF foi extraído corretamente
                if cpf is None:
                    logger.error("Não foi possível extrair o CPF do documento.")
                    return render_message(
                        request,
                        message_type='error',
                        title='Erro no CPF',
                        message='Não foi possível extrair o CPF do PDF. Verifique o arquivo e tente novamente.',
                        code=400
                    )

                # Normalizar o CPF extraído do PDF
                cpf_normalizado = normalize_cpf(cpf)
                # Recuperar e normalizar o CPF da sessão
                cpf_sessao = normalize_cpf(request.session.get('cpf'))

                # Debug: Imprimir CPFs para verificar
                logger.info(f"CPF da sessão (normalizado): {cpf_sessao}")
                logger.info(f"CPF do arquivo (normalizado): {cpf_normalizado}")

                # Comparar o CPF extraído com o CPF da sessão
                if cpf_normalizado != cpf_sessao:
                    logger.error("O CPF do documento não corresponde ao CPF fornecido.")
                    return render_message(
                        request,
                        message_type='error',
                        title='Ops! Erro ao enviar seus dados',
                        message='O CPF no arquivo não corresponde ao CPF fornecido. Verifique o arquivo e tente novamente.',
                        code=400
                    )

                # Calcular a soma das notas e a nota geral
                total_score, nota_geral = calculate_scores(nota_matematica, nota_redacao)

                # Verificar se a nota geral foi calculada
                if total_score is None or nota_geral is None:
                    logger.error("Erro ao calcular as notas.")
                    return render_message(
                        request,
                        message_type='error',
                        title='Ops! Erro em calcular notas',
                        message='Não foi possível calcular as notas. Verifique o arquivo e tente novamente.',
                        code=400
                    )

                # Armazenar os dados na sessão para a próxima etapa
                logger.info("Armazenando dados na sessão.")
                request.session['ocr_text'] = text
                request.session['nome'] = nome
                request.session['cpf_extraido'] = cpf_normalizado
                request.session['nota_matematica'] = nota_matematica
                request.session['nota_redacao'] = nota_redacao
                request.session['nota_geral'] = nota_geral

                # Redirecionar para a view de resultados
                return redirect('enem_result_view')

            except Exception as e:
                logger.error(f"Erro ao processar o PDF: {str(e)}")
                return render_message(
                    request,
                    message_type='error',
                    title='Ops! Erro em realizar processamento',
                    message='Erro ao processar o arquivo PDF. Verifique o arquivo e tente novamente.',
                    code=500
                )

            finally:
                # Remover o arquivo temporário
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                    logger.info(f"Arquivo temporário removido: {temp_pdf_path}")

        else:
            logger.error("Arquivo PDF inválido.")
            return render_message(
                request,
                message_type='error',
                title='Ops! Arquivo Inválido',
                message='Apenas arquivos no formato PDF são permitidos. Por favor, baixe o arquivo oficial do site do ENEM.',
                code=400
            )
    else:
        form = EnemPDFUploadForm()
        logger.info("Renderizando formulário de upload do ENEM.")
    
    return render(request, 'enem_upload.html', {'form': form})
