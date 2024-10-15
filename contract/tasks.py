# contract/tasks.py
from celery import shared_task
from pdf2image import convert_from_path
from decouple import config
import pytesseract
import os
import logging
import requests

logger = logging.getLogger('django')

API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')


@shared_task(bind=True)
def process_enem_data(self, user_id, cpf, apply_method, file_path):
    """Task para processar o PDF via OCR e enviar os dados para a API."""

    try:
        # Converter o PDF em texto via OCR
        pages = convert_from_path(file_path)
        ocr_text = ''
        for page in pages:
            ocr_text += pytesseract.image_to_string(page)

        # Remover o arquivo do PDF após o processamento
        os.remove(file_path)

        # Extração dos dados
        nome, cpf_extraido, nota_matematica, nota_redacao = None, None, None, None
        for line in ocr_text.splitlines():
            if 'Nome:' in line:
                nome = line.split('Nome:')[-1].strip()
            if 'CPF:' in line:
                cpf_extraido = line.split('CPF:')[-1].strip().replace('.', '').replace('-', '')
            if 'Matemática e suas Tecnologias' in line:
                try:
                    nota_matematica = float(line.split()[-2].replace(',', '.'))
                except ValueError:
                    nota_matematica = None
            if 'Redação' in line:
                try:
                    nota_redacao = float(line.split()[-2].replace(',', '.'))
                except ValueError:
                    nota_redacao = None

        # Calcular a nota geral
        if nota_matematica is not None and nota_redacao is not None:
            nota_geral = (nota_matematica * 0.8) + (nota_redacao * 0.2)
        else:
            nota_geral = None

        # Chamar a task para enviar os dados
        send_enem_data.delay(user_id, nota_geral, apply_method)

    except Exception as e:
        logger.error(f"Erro ao processar o PDF ou extrair dados: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)



@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_enem_data(self, id_value, nota_geral, apply_method):
    """Task para enviar as notas via API com retentativa em caso de falha."""
    url_method = f'{API_BASE_URL}/form/{id_value}/applyMethod'
    headers = {'api-key': API_KEY}
    body = {
        "applyMethod": apply_method,
        "applyMethodGrade": nota_geral,
    }

    try:
        response_method = requests.patch(url_method, headers=headers, json=body)
        response_method.raise_for_status()  # Levanta uma exceção para status de erro
        logger.info(f"Dados enviados com sucesso para o usuário {id_value}")
        return {"status": "success", "data": response_method.json()}

    except requests.exceptions.RequestException as exc:
        logger.error(f"Erro ao enviar os dados para o usuário {id_value}: {exc}")
        raise self.retry(exc=exc)
