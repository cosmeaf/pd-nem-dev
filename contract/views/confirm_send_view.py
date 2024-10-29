import requests
from django.shortcuts import redirect, render
from decouple import config
from contract.views.messages_view import render_message
from contract.models import EnemData
import logging

# Configuração de logs
logger = logging.getLogger('django')

# Carregar URL base da API e chave de API do arquivo .env
API_BASE_URL = config('API_BASE_URL')
API_KEY = config('API_KEY')

# View para enviar os dados para a API usando PATCH
def confirm_send_view(request):
    if request.method == 'POST':
        try:
            # Obter os dados da sessão
            nome = request.session.get('nome')
            cpf = request.session.get('cpf_extraido')
            nota_matematica = request.session.get('nota_matematica')
            nota_redacao = request.session.get('nota_redacao')
            nota_geral = request.session.get('nota_geral')
            apply_method = request.session.get('apply_method')
            id_value = request.session.get('user_id')

            # Verificar se todos os dados estão presentes
            if not all([nome, cpf, nota_matematica, nota_redacao, nota_geral, apply_method, id_value]):
                logger.error("Dados ausentes na sessão.")
                return render_message(request, 'error', title='Erro', message='Dados incompletos.')

            # Verificar duplicidade de CPF antes de salvar
            if EnemData.objects.filter(cpf=cpf).exists():
                return render_message(request, 'error', title='CPF Duplicado', message='Dados já cadastrados no sistema.')

            # Salvar os dados na model EnemData
            enem_data = EnemData.objects.create(
                nome=nome,
                cpf=cpf,
                nota_matematica=nota_matematica,
                nota_redacao=nota_redacao,
                nota_geral=nota_geral
            )

            # URL do endpoint dinâmico usando a variável API_BASE_URL
            url_method = f'{API_BASE_URL}/form/{id_value}/applyMethod'
            headers = {'api-key': API_KEY}
            body = {
                "applyMethod": apply_method,
                "applyMethodGrade": nota_geral,
            }

            # Enviar os dados para a API com o método PATCH
            response_method = requests.patch(url_method, headers=headers, json=body)
            response_method.raise_for_status()

            # Limpar a sessão em caso de sucesso
            request.session.flush()

            # Redirecionar para a mensagem de sucesso
            return render_message(request, 'success', title='Sucesso', message='Dados enviados com sucesso.')

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar os dados: {e}")
            # Redirecionar para a mensagem de erro
            return render_message(request, 'error', title='Erro', message='Erro ao enviar dados para a API.')

    # Se o método da requisição não for POST, redirecionar para a página de resultados
    return redirect('enem_result_view')
