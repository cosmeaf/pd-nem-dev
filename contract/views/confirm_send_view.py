import requests
from django.shortcuts import redirect
from decouple import config  # Importa o config para carregar as variáveis de ambiente
from contract.views.messages_view import render_message
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
            id_value = request.session.get('user_id')
            nota_geral = request.session.get('nota_geral')
            apply_method = request.session.get('apply_method')

            # Verificar se os dados estão presentes
            if not id_value or not nota_geral or not apply_method:
                logger.error("Dados ausentes na sessão: id_value, nota_geral ou apply_method")
                return render_message(request, 'error')

            # URL do endpoint dinâmico usando a variável API_BASE_URL
            url_method = f'{API_BASE_URL}/form/{id_value}/applyMethod'

            # Headers da API
            headers = {
                'api-key': API_KEY
            }

            # Body da requisição (enviado em formato JSON)
            body = {
                "applyMethod": apply_method,
                "applyMethodGrade": nota_geral,
            }

            # Enviar os dados para a API com o método PATCH
            response_method = requests.patch(url_method, headers=headers, json=body)
            response_method.raise_for_status()  # Levanta uma exceção para status de erro

            # Limpar a sessão em caso de sucesso
            request.session.flush()

            # Redirecionar para a mensagem de sucesso
            return render_message(request, 'success')

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao enviar os dados: {e}")
            # Redirecionar para a mensagem de erro
            return render_message(request, 'error')

    # Se o método da requisição não for POST, redirecionar para a página de resultados
    return redirect('enem_result_view')
